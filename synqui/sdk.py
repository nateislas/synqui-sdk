"""Main Synqui SDK implementation."""

import asyncio
import functools
import signal
import time
import atexit
from contextlib import asynccontextmanager, contextmanager
from queue import Queue, Empty
from typing import Any, Callable, Dict, Optional, Union, Generator
from datetime import datetime

from .config import SDKConfig
from .models import TraceData, SpanStatus
from .context import span_context, create_child_span
from .serialization import safe_serialize
from .trace_collector_unified import UnifiedTraceCollector
from .token_counter import count_function_tokens, extract_tokens_from_llm_response
from .auto_instrumentation import AutoInstrumentationEngine
from .analytics import initialize_analytics, get_analytics
from .chat_session import ChatSession, create_chat_session


class SynquiSDK:
    """Main SDK class for Synqui instrumentation.

    This class provides the core functionality for tracing function calls
    and sending trace data to the Synqui platform.

    Example:
        config = SDKConfig(api_key="your-key", project_id="your-project")
        sdk = SynquiSDK(config)

        @sdk.trace("my_agent")
        def my_function():
            return "result"
    """

    def __init__(self, config: SDKConfig):
        """Initialize the SDK with configuration.

        Args:
            config: SDK configuration instance
        """
        self.config = config
        self._event_queue: Queue = Queue()
        self._trace_collector: Optional[UnifiedTraceCollector] = None
        self._auto_instrumentation: Optional[AutoInstrumentationEngine] = None
        self._first_trace_tracked = False

        # Log initialization
        print("🤠 Synqui: Initializing SDK...")

        # Initialize analytics (framework detection, SDK version reporting)
        self._analytics = initialize_analytics(
            api_key=config.api_key,
            project_id=config.project_id,
            enabled=True,
        )

        # Start trace collector and auto-instrumentation
        self._start_trace_collector()
        self._start_auto_instrumentation()

        # Register automatic shutdown to ensure traces are flushed on program exit
        atexit.register(self.shutdown)
        
        # Register signal handler for graceful shutdown on Ctrl+C
        # Only register signal handlers if we're in the main thread
        try:
            def signal_handler(signum, frame):
                self.shutdown()
                exit(0)
            
            signal.signal(signal.SIGINT, signal_handler)
            signal.signal(signal.SIGTERM, signal_handler)
        except ValueError:
            # Signal handlers can only be registered from the main thread
            # This is expected in some environments like Streamlit, Jupyter, etc.
            pass

    def _start_trace_collector(self):
        """Start the unified trace collector."""
        if self._trace_collector is None:
            self._trace_collector = UnifiedTraceCollector(self)
    
    def _start_auto_instrumentation(self):
        """Start automatic LLM instrumentation."""
        if self._auto_instrumentation is None:
            self._auto_instrumentation = AutoInstrumentationEngine(self)
            self._auto_instrumentation.instrument_all()
    
    def _stop_auto_instrumentation(self):
        """Stop automatic LLM instrumentation."""
        if self._auto_instrumentation:
            self._auto_instrumentation.restore_original_methods()
            self._auto_instrumentation = None

    def trace(self, agent_name: str, **kwargs) -> Callable:
        """Decorator for tracing function calls.

        This decorator can be used on both synchronous and asynchronous functions.
        It automatically captures timing, inputs, outputs, and errors.

        Args:
            agent_name: Name of the agent/component being traced
            **kwargs: Additional options (tags, metadata, etc.)

        Returns:
            Decorated function

        Example:
            @sdk.trace("data_processor")
            def process_data(data):
                \"\"\"
                Process data with expected performance of 1-5 seconds.
                \"\"\"
                return {"processed": data}

            @sdk.trace("api_client")
            async def fetch_data(url):
                async with httpx.AsyncClient() as client:
                    response = await client.get(url)
                    return response.json()
        """
        def decorator(func: Callable) -> Callable:
            # Capture code context (always enabled)
            code_context = self._capture_code_context(func)

            if asyncio.iscoroutinefunction(func):
                return self._async_trace_decorator(func, agent_name, code_context, **kwargs)
            else:
                return self._sync_trace_decorator(func, agent_name, code_context, **kwargs)

        return decorator

    def _capture_code_context(self, func: Callable) -> Dict[str, Any]:
        """Capture code context for analysis."""
        try:
            import inspect

            source_code = inspect.getsource(func)
            docstring = func.__doc__
            signature = str(inspect.signature(func))

            module = inspect.getmodule(func)
            module_name = module.__name__ if module else None
            file_path = module.__file__ if module else None

            code_context = {
                'source_code': source_code,
                'docstring': docstring,
                'function_signature': signature,
                'module_name': module_name,
                'file_path': file_path,
                'function_name': func.__name__
            }

            return code_context
        except Exception:
            return {}

    def _sync_trace_decorator(self, func: Callable, agent_name: str, code_context: Dict[str, Any], **kwargs) -> Callable:
        """Synchronous trace decorator implementation."""

        @functools.wraps(func)
        def wrapper(*args, **func_kwargs):
            # Create trace data
            trace_data = create_child_span(
                agent_name=agent_name,
                function_name=func.__name__,
                tags=kwargs.get("tags", {}),
                metadata=kwargs.get("metadata", {})
            )

            # Set the name field for workflow traces to match agent_name
            # This ensures the batch processor can identify workflow spans
            trace_data.name = agent_name

            # Add code context to metadata
            if code_context:

                source_code = code_context.get('source_code', '')
                docstring = code_context.get('docstring', '')


                trace_data.metadata.update({
                    'source_code': source_code,
                    'docstring': docstring,
                    'function_signature': code_context.get('function_signature', ''),
                    'module_name': code_context.get('module_name', ''),
                    'file_path': code_context.get('file_path', ''),
                    'function_name': code_context.get('function_name', '')
                })

            # Set prompt fields if provided
            self._set_prompt_fields(trace_data, kwargs)

            # Add global tags from config
            trace_data.tags.update(self.config.tags)

            with span_context(trace_data):
                try:
                    # Capture inputs (always enabled)
                    trace_data.inputs = self._capture_inputs(args, func_kwargs)

                    # Execute function
                    result = func(*args, **func_kwargs)

                    # Capture outputs (always enabled)
                    trace_data.outputs = self._capture_outputs(result)

                    # Count tokens (always enabled)
                    self._count_tokens(trace_data, args, func_kwargs, result)

                    # Mark as completed
                    trace_data.finish(SpanStatus.COMPLETED)

                    return result

                except Exception as e:
                    # Capture error (always enabled)
                    trace_data.set_error(e)
                    raise

                finally:
                    # Ensure parent reference is persisted
                    if trace_data.parent_span_id:
                        trace_data.inputs = trace_data.inputs or {}
                        trace_data.inputs.setdefault("parent_span_id", trace_data.parent_span_id)
                        trace_data.metadata.setdefault("parent_span_id", trace_data.parent_span_id)

                    # Send trace data
                    self._send_trace(trace_data)

        return wrapper

    def _async_trace_decorator(self, func: Callable, agent_name: str, code_context: Dict[str, Any], **kwargs) -> Callable:
        """Asynchronous trace decorator implementation."""

        @functools.wraps(func)
        async def wrapper(*args, **func_kwargs):
            # Create trace data
            trace_data = create_child_span(
                agent_name=agent_name,
                function_name=func.__name__,
                tags=kwargs.get("tags", {}),
                metadata=kwargs.get("metadata", {})
            )

            # Set the name field for workflow traces to match agent_name
            # This ensures the batch processor can identify workflow spans
            trace_data.name = agent_name

            # Add code context to metadata
            if code_context:

                source_code = code_context.get('source_code', '')
                docstring = code_context.get('docstring', '')


                trace_data.metadata.update({
                    'source_code': source_code,
                    'docstring': docstring,
                    'function_signature': code_context.get('function_signature', ''),
                    'module_name': code_context.get('module_name', ''),
                    'file_path': code_context.get('file_path', ''),
                    'function_name': code_context.get('function_name', '')
                })

            # Set prompt fields if provided
            self._set_prompt_fields(trace_data, kwargs)

            # Add global tags from config
            trace_data.tags.update(self.config.tags)

            with span_context(trace_data):
                try:
                    # Capture inputs (always enabled)
                    trace_data.inputs = self._capture_inputs(args, func_kwargs)

                    # Execute function
                    result = await func(*args, **func_kwargs)

                    # Capture outputs (always enabled)
                    trace_data.outputs = self._capture_outputs(result)

                    # Count tokens (always enabled)
                    self._count_tokens(trace_data, args, func_kwargs, result)

                    # Mark as completed
                    trace_data.finish(SpanStatus.COMPLETED)

                    return result

                except Exception as e:
                    # Capture error (always enabled)
                    trace_data.set_error(e)
                    raise

                finally:
                    # Ensure parent reference is persisted
                    if trace_data.parent_span_id:
                        trace_data.inputs = trace_data.inputs or {}
                        trace_data.inputs.setdefault("parent_span_id", trace_data.parent_span_id)
                        trace_data.metadata.setdefault("parent_span_id", trace_data.parent_span_id)

                    # Send trace data
                    self._send_trace(trace_data)

        return wrapper

    def span(self, operation_name: str, **kwargs):
        """Context manager for manual span creation.

        This is used as a context manager for code blocks that need manual span control.
        For function decoration, use @synqui.trace() instead.

        Args:
            operation_name: Name of the operation/agent
            **kwargs: Additional options (tags, metadata, etc.)

        Returns:
            Context manager yielding TraceData instance

        Examples:
            # As context manager (for code blocks)
            with sdk.span("custom_operation") as span:
                span.set_attribute("batch_size", 100)
                # Your code here
        """

        return self._span_context_manager(operation_name, **kwargs)
    
    @contextmanager
    def _span_context_manager(self, operation_name: str, **kwargs) -> Generator[TraceData, None, None]:
        """Internal context manager implementation for span."""
        # Create trace data
        trace_data = create_child_span(
            agent_name=operation_name,
            function_name=operation_name,
            tags=kwargs.get("tags", {}),
            metadata=kwargs.get("metadata", {})
        )

        # Set the name field for workflow spans to match agent_name
        # This ensures the batch processor can identify workflow spans
        trace_data.name = operation_name

        # Add global tags from config
        trace_data.tags.update(self.config.tags)

        with span_context(trace_data):
            try:
                yield trace_data
            except Exception as e:
                # Capture error (always enabled)
                trace_data.set_error(e)
                raise
            finally:
                # Finish span if not already finished
                if trace_data.status == SpanStatus.RUNNING:
                    trace_data.finish(SpanStatus.COMPLETED)

                # Send trace data
                self._send_trace(trace_data)
    
    def _sync_span_decorator(self, func: Callable, operation_name: str, code_context: Dict[str, Any], **kwargs) -> Callable:
        """Synchronous span decorator implementation."""
        @functools.wraps(func)
        def wrapper(*args, **func_kwargs):
            # Create trace data as a child span
            trace_data = create_child_span(
                agent_name=operation_name,
                function_name=func.__name__,
                tags=kwargs.get("tags", {}),
                metadata=kwargs.get("metadata", {})
            )
            
            # Set the name field to match agent_name
            trace_data.name = operation_name
            
            # Add code context to metadata
            if code_context:
                trace_data.metadata.update({
                    'source_code': code_context.get('source_code', ''),
                    'docstring': code_context.get('docstring', ''),
                    'function_signature': code_context.get('function_signature', ''),
                    'module_name': code_context.get('module_name', ''),
                    'file_path': code_context.get('file_path', ''),
                    'function_name': code_context.get('function_name', '')
                })
            
            # Add global tags from config
            trace_data.tags.update(self.config.tags)
            
            with span_context(trace_data):
                try:
                    # Capture inputs (always enabled)
                    trace_data.inputs = self._capture_inputs(args, func_kwargs)
                    
                    # Execute function
                    result = func(*args, **func_kwargs)
                    
                    # Capture outputs (always enabled)
                    trace_data.outputs = self._capture_outputs(result)
                    
                    # Mark as completed
                    trace_data.finish(SpanStatus.COMPLETED)
                    
                    return result
                
                except Exception as e:
                    # Capture error (always enabled)
                    trace_data.set_error(e)
                    
                    raise
                
                finally:
                    # Send trace data
                    self._send_trace(trace_data)
        
        return wrapper
    
    def _async_span_decorator(self, func: Callable, operation_name: str, code_context: Dict[str, Any], **kwargs) -> Callable:
        """Asynchronous span decorator implementation."""
        @functools.wraps(func)
        async def wrapper(*args, **func_kwargs):
            # Create trace data as a child span
            trace_data = create_child_span(
                agent_name=operation_name,
                function_name=func.__name__,
                tags=kwargs.get("tags", {}),
                metadata=kwargs.get("metadata", {})
            )
            
            # Set the name field to match agent_name
            trace_data.name = operation_name
            
            # Add code context to metadata
            if code_context:
                trace_data.metadata.update({
                    'source_code': code_context.get('source_code', ''),
                    'docstring': code_context.get('docstring', ''),
                    'function_signature': code_context.get('function_signature', ''),
                    'module_name': code_context.get('module_name', ''),
                    'file_path': code_context.get('file_path', ''),
                    'function_name': code_context.get('function_name', '')
                })
            
            # Add global tags from config
            trace_data.tags.update(self.config.tags)
            
            with span_context(trace_data):
                try:
                    # Capture inputs (always enabled)
                    trace_data.inputs = self._capture_inputs(args, func_kwargs)
                    
                    # Execute function
                    result = await func(*args, **func_kwargs)
                    
                    # Capture outputs (always enabled)
                    trace_data.outputs = self._capture_outputs(result)
                    
                    # Mark as completed
                    trace_data.finish(SpanStatus.COMPLETED)
                    
                    return result
                
                except Exception as e:
                    # Capture error (always enabled)
                    trace_data.set_error(e)
                    
                    raise
                
                finally:
                    # Send trace data
                    self._send_trace(trace_data)
        
        return wrapper

    def _capture_inputs(self, args: tuple, kwargs: dict) -> Dict[str, Any]:
        """Safely capture function inputs.

        Args:
            args: Function positional arguments
            kwargs: Function keyword arguments

        Returns:
            Dictionary containing serialized inputs
        """
        try:
            return {
                "args": [safe_serialize(arg) for arg in args],
                "kwargs": {k: safe_serialize(v) for k, v in kwargs.items()}
            }
        except Exception as e:
            return {"error": "Failed to capture inputs"}

    def _capture_outputs(self, result: Any) -> Dict[str, Any]:
        """Safely capture function outputs.

        Args:
            result: Function return value

        Returns:
            Dictionary containing serialized outputs
        """
        try:
            return {"result": safe_serialize(result)}
        except Exception as e:
            return {"error": "Failed to capture outputs"}

    def _count_tokens(self, trace_data: TraceData, args: tuple, kwargs: dict, result: Any) -> None:
        """Count tokens for function inputs and outputs.

        Args:
            trace_data: Trace data to update with token counts
            args: Function arguments
            kwargs: Function keyword arguments
            result: Function result
        """
        try:
            # Try to extract tokens from LLM response first
            if hasattr(result, 'usage') or isinstance(result, dict) and 'usage' in result:
                token_count = extract_tokens_from_llm_response(result)
                if token_count.total_tokens > 0:
                    trace_data.input_tokens = token_count.input_tokens
                    trace_data.output_tokens = token_count.output_tokens
                    trace_data.total_tokens = token_count.total_tokens
                    trace_data.model_name = token_count.model
                    trace_data.model_provider = token_count.provider
                    return
            
            # Fallback to counting tokens from inputs and outputs
            token_count = count_function_tokens(args, result)
            trace_data.input_tokens = token_count.input_tokens
            trace_data.output_tokens = token_count.output_tokens
            trace_data.total_tokens = token_count.total_tokens
            
        except Exception as e:
            # Set default values
            trace_data.input_tokens = 0
            trace_data.output_tokens = 0
            trace_data.total_tokens = 0

    def _send_trace(self, trace_data: TraceData):
        """Send trace data to the trace collector.

        Args:
            trace_data: TraceData instance to send
        """
        # Track first trace for analytics
        if not self._first_trace_tracked and self._analytics:
            self._analytics.track_first_trace(trace_data.trace_id)
            self._first_trace_tracked = True

        try:
            # Add environment information
            trace_data.metadata["environment"] = self.config.environment
            trace_data.metadata["sdk_version"] = "0.1.0"

            # Metadata is already set in trace_data

            # Convert TraceData to dictionary for trace collector
            span_data = trace_data.to_dict()
            
            # Process the span with the trace collector
            self._trace_collector.process_span(span_data)
            
            # NOTE: We do NOT automatically end traces here.
            # Traces are ended explicitly by:
            # 1. The span context manager (for @synqui.trace decorators)
            # 2. The LangChain callback handler (when the workflow completes)
            # 3. Manual calls to synqui.end_trace() by the user

        except Exception:
            pass

    def _set_prompt_fields(self, trace_data: TraceData, kwargs: Dict[str, Any]) -> None:
        """Populate explicit prompt fields on the trace if provided.

        Supported kwargs:
            - system_prompt: str
            - prompt_name: str
            - prompt_version: str
            - prompt_parameters: dict
        """
        try:
            system_prompt = kwargs.get("system_prompt")
            if isinstance(system_prompt, str):
                trace_data.system_prompt = system_prompt
                # Compute a stable hash for dedup/version hint
                import hashlib
                trace_data.prompt_hash = hashlib.sha256(system_prompt.encode("utf-8")).hexdigest()

            prompt_name = kwargs.get("prompt_name")
            if isinstance(prompt_name, str):
                trace_data.prompt_name = prompt_name

            prompt_version = kwargs.get("prompt_version")
            if isinstance(prompt_version, str):
                trace_data.prompt_version = prompt_version

            prompt_parameters = kwargs.get("prompt_parameters")
            if isinstance(prompt_parameters, dict):
                trace_data.prompt_parameters = prompt_parameters
        except Exception:
            pass

    def flush(self, timeout: Optional[float] = None):
        """Manually flush pending traces.

        Args:
            timeout: Maximum time to wait for flush to complete
        """
        if self._trace_collector:
            # TraceCollectorV2 handles flushing automatically
            pass

    def shutdown(self, timeout: Optional[float] = None):
        """Shutdown the SDK and flush remaining traces.

        Args:
            timeout: Maximum time to wait for shutdown to complete
        """
        # Stop auto-instrumentation
        self._stop_auto_instrumentation()
        
        # Shutdown all LangGraph handlers first (they need to finalize traces)
        try:
            from .langgraph import shutdown_all_langgraph_handlers
            shutdown_all_langgraph_handlers()
        except ImportError:
            pass
        except Exception:
            pass
        
        # Shutdown trace collector
        if self._trace_collector:
            self._trace_collector.shutdown()
            self._trace_collector = None
            

    def is_enabled(self) -> bool:
        """Check if the SDK is enabled.

        Returns:
            Always returns True (SDK is always enabled when initialized)
        """
        return True

    def get_queue_size(self) -> int:
        """Get the current size of the event queue.

        Returns:
            Number of events in the queue
        """
        return self._event_queue.qsize()

    def start_chat_session(
        self,
        name: Optional[str] = None,
        session_type: str = "chat",
        timeout_minutes: int = 30,
        max_duration_minutes: int = 240,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ChatSession:
        """Start a new chat session for conversational AI applications.

        Args:
            name: Human-readable name for the session
            session_type: Type of session ('chat', 'pipeline', 'workflow')
            timeout_minutes: Minutes of inactivity before session timeout
            max_duration_minutes: Maximum session duration in minutes
            metadata: Additional session metadata

        Returns:
            The created ChatSession instance

        Example:
            # Initialize SDK first
            sdk = SynquiSDK(config)

            # Create a chat session for conversational AI
            session = sdk.start_chat_session(
                name="pdf_chat_assistant",
                session_type="chat",
                timeout_minutes=30
            )

            # Use the session with LangGraph handler
            handler = SynquiLangGraphHandler(session=session)
        """
        return create_chat_session(
            name=name,
            session_type=session_type,
            timeout_minutes=timeout_minutes,
            max_duration_minutes=max_duration_minutes,
            metadata=metadata
        )


# Global SDK instance
_sdk_instance: Optional[SynquiSDK] = None


def get_current_sdk() -> Optional[SynquiSDK]:
    """Get the current global SDK instance.
    
    Returns:
        Current SDK instance or None if not initialized
    """
    return _sdk_instance


def initialize(config: SDKConfig) -> SynquiSDK:
    """Initialize the global SDK instance.

    Args:
        config: SDK configuration

    Returns:
        Initialized SDK instance
    """
    global _sdk_instance
    _sdk_instance = SynquiSDK(config)
    return _sdk_instance


def get_global_instance() -> SynquiSDK:
    """Get the global SDK instance.

    Returns:
        Global SDK instance

    Raises:
        RuntimeError: If no global instance has been created
    """
    if _sdk_instance is None:
        raise RuntimeError(
            "No global SDK instance available. "
            "Call synqui.init() or SynquiSDK.initialize() first."
        )
    return _sdk_instance