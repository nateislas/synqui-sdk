"""
LangGraph integration for Vaquero SDK.

This module provides specialized integration for LangGraph applications,
handling the unique timing and execution flow of LangGraph agent swarms.
"""

import logging
from typing import Any, Dict, Optional, List
from datetime import datetime
import uuid
import asyncio
from contextlib import asynccontextmanager

from .langchain import VaqueroCallbackHandler
from .trace_collector_unified import UnifiedTraceCollector
from .chat_session import ChatSession

logger = logging.getLogger(__name__)


class VaqueroLangGraphHandler(VaqueroCallbackHandler):
    """
    Specialized Vaquero handler for LangGraph applications.
    
    This handler addresses the timing issues specific to LangGraph's
    agent swarm architecture by ensuring proper trace finalization
    and sending before SDK shutdown.
    
    Key Features:
    - Captures individual node executions (agents) within LangGraph workflows
    - Handles LangGraph-specific callbacks for comprehensive tracing
    - Maintains proper hierarchical structure (Session → Message/Orchestration → Agents → Components)
    - Supports chat session management for conversational applications
    """
    
    def __init__(self, session: Optional[ChatSession] = None, **kwargs):
        """Initialize the LangGraph handler with optional chat session.

        Args:
            session: Optional ChatSession for chat-based applications
            **kwargs: Additional arguments passed to parent class
        """
        super().__init__(**kwargs)
        self.session = session
        self._active_traces: Dict[str, Dict[str, Any]] = {}
        self._active_nodes: Dict[str, Dict[str, Any]] = {}  # Track individual node executions
        self._trace_finalization_pending = False
        self._message_sequence = 0  # Track message sequence for chat sessions
        self._current_orchestration_id = None  # Track current agent orchestration
        self._session_trace_id = None  # Single trace ID for the entire session

    def handle_user_message(self, message_content: str, message_id: Optional[str] = None) -> None:
        """Handle a user message in a chat session.

        Args:
            message_content: The user's message content
            message_id: Optional message ID (generated if not provided)
        """
        if not self.session:
            logger.debug("No session available for user message")
            return

        # Initialize session trace ID if not set
        if self._session_trace_id is None:
            self._session_trace_id = str(uuid.uuid4())
            logger.debug(f"Initialized session trace ID: {self._session_trace_id}")

        # Generate message ID if not provided
        if not message_id:
            message_id = str(uuid.uuid4())

        # Increment message sequence for next response
        self._message_sequence += 1

        # Update session activity and metrics
        self.session.update_activity()
        self.session.add_message(tokens=0, cost=0.0)  # Tokens/cost will be calculated from agents

        # Create user message span (not a complete trace)
        user_span_data = {
            'trace_id': self._session_trace_id,  # Use session trace ID
            'agent_name': 'user_message',
            'function_name': 'user_input',
            'start_time': datetime.utcnow().isoformat(),
            'end_time': datetime.utcnow().isoformat(),
            'status': 'completed',
            'duration': 0,
            'inputs': {'content': message_content},
            'outputs': {'content': message_content},
            'session_id': self.session.session_id,
            'session_type': self.session.session_type,
            'chat_session_id': self.session.session_id,
            'message_type': 'user_message',
            'message_content': message_content,
            'message_sequence': self._message_sequence,
            'user_message_id': message_id,
            'framework': 'langgraph'
        }

        # Send user message span
        if self.sdk and hasattr(self.sdk, '_trace_collector') and self.sdk._trace_collector:
            self.sdk._trace_collector.process_span(user_span_data)
            logger.debug(f"Sent user message span for session trace: {self._session_trace_id}")
        else:
            logger.warning("No trace collector available for user message")

    def on_chain_start(
        self,
        serialized: Dict[str, Any],
        inputs: Dict[str, Any],
        *,
        run_id: str,
        parent_run_id: Optional[str] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> None:
        """Handle chain start for LangGraph."""
        try:
            super().on_chain_start(
                serialized, inputs, run_id=run_id, parent_run_id=parent_run_id,
                tags=tags, metadata=metadata, **kwargs
            )
            
            # Track active traces for LangGraph
            if run_id not in self._active_traces:
                self._active_traces[run_id] = {
                    'start_time': datetime.utcnow(),
                    'parent_run_id': parent_run_id,
                    'chain_type': serialized.get('name', 'unknown') if serialized else 'unknown',
                    'inputs': inputs
                }
        except Exception as e:
            logger.warning(f"Error in LangGraph chain start callback: {e}")
            # Still track the trace even if parent callback fails
            if run_id not in self._active_traces:
                self._active_traces[run_id] = {
                    'start_time': datetime.utcnow(),
                    'parent_run_id': parent_run_id,
                    'chain_type': 'unknown',
                    'inputs': inputs
                }
    
    def on_chain_end(
        self,
        outputs: Dict[str, Any],
        *,
        run_id: str,
        parent_run_id: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Handle chain end for LangGraph."""
        try:
            super().on_chain_end(outputs, run_id=run_id, parent_run_id=parent_run_id, **kwargs)
        except Exception as e:
            logger.warning(f"Error in LangGraph chain end callback: {e}")
        
        # Update trace info
        if run_id in self._active_traces:
            self._active_traces[run_id]['end_time'] = datetime.utcnow()
            self._active_traces[run_id]['outputs'] = outputs
    
    def on_chain_error(
        self,
        error: Exception,
        *,
        run_id: str,
        parent_run_id: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Handle chain error for LangGraph."""
        try:
            super().on_chain_error(error, run_id=run_id, parent_run_id=parent_run_id, **kwargs)
        except Exception as e:
            logger.warning(f"Error in LangGraph chain error callback: {e}")
        
        # Mark trace as errored
        if run_id in self._active_traces:
            self._active_traces[run_id]['error'] = str(error)
            self._active_traces[run_id]['end_time'] = datetime.utcnow()

    def on_agent_start(
        self,
        serialized: Dict[str, Any],
        inputs: Dict[str, Any],
        *,
        run_id: str,
        parent_run_id: Optional[str] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> None:
        """Handle agent start for LangGraph nodes."""
        try:
            super().on_agent_start(
                serialized, inputs, run_id=run_id, parent_run_id=parent_run_id,
                tags=tags, metadata=metadata, **kwargs
            )
            
            # Extract agent name from serialized data
            agent_name = serialized.get('name', 'unknown_agent') if serialized else 'unknown_agent'
            
            # Track individual node execution
            self._active_nodes[run_id] = {
                'start_time': datetime.utcnow(),
                'parent_run_id': parent_run_id,
                'agent_name': agent_name,
                'inputs': inputs,
                'metadata': metadata or {}
            }
            
            logger.debug(f"Started LangGraph node: {agent_name} (run_id: {run_id})")
            
        except Exception as e:
            logger.warning(f"Error in LangGraph agent start callback: {e}")

    def on_agent_end(
        self,
        outputs: Dict[str, Any],
        *,
        run_id: str,
        parent_run_id: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Handle agent end for LangGraph nodes."""
        try:
            super().on_agent_end(outputs, run_id=run_id, parent_run_id=parent_run_id, **kwargs)
        except Exception as e:
            logger.warning(f"Error in LangGraph agent end callback: {e}")
        
        # Update node info and send trace
        if run_id in self._active_nodes:
            node_info = self._active_nodes[run_id]
            node_info['end_time'] = datetime.utcnow()
            node_info['outputs'] = outputs
            
            # Calculate duration
            duration = (node_info['end_time'] - node_info['start_time']).total_seconds()
            
            # Create agent orchestration ID if this is the first agent in a new orchestration
            if not self._current_orchestration_id:
                self._current_orchestration_id = str(uuid.uuid4())
            
            # Send individual agent span
            self._send_agent_span(node_info, duration)
            
            # Clean up
            del self._active_nodes[run_id]
            
            logger.debug(f"Completed LangGraph node: {node_info['agent_name']} (run_id: {run_id})")

    def on_agent_error(
        self,
        error: Exception,
        *,
        run_id: str,
        parent_run_id: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Handle agent error for LangGraph nodes."""
        try:
            super().on_agent_error(error, run_id=run_id, parent_run_id=parent_run_id, **kwargs)
        except Exception as e:
            logger.warning(f"Error in LangGraph agent error callback: {e}")
        
        # Mark node as errored
        if run_id in self._active_nodes:
            self._active_nodes[run_id]['error'] = str(error)
            self._active_nodes[run_id]['end_time'] = datetime.utcnow()
            
            # Send error span
            node_info = self._active_nodes[run_id]
            duration = (node_info['end_time'] - node_info['start_time']).total_seconds()
            self._send_agent_span(node_info, duration, is_error=True)
            
            # Clean up
            del self._active_nodes[run_id]

    def _send_agent_span(self, node_info: Dict[str, Any], duration: float, is_error: bool = False) -> None:
        """Send individual agent span to the unified trace collector."""
        try:
            if self.sdk and hasattr(self.sdk, '_trace_collector') and self.sdk._trace_collector:
                # Initialize session trace ID if not set
                if self._session_trace_id is None:
                    self._session_trace_id = str(uuid.uuid4())
                    logger.debug(f"Initialized session trace ID in agent span: {self._session_trace_id}")

                # Create agent span data (not a complete trace)
                agent_span_data = {
                    'trace_id': self._session_trace_id,  # Use session trace ID
                    'agent_name': node_info['agent_name'],
                    'function_name': node_info['agent_name'],
                    'start_time': node_info['start_time'].isoformat(),
                    'end_time': node_info['end_time'].isoformat(),
                    'status': 'failed' if is_error else 'completed',
                    'duration': duration,
                    'inputs': node_info['inputs'],
                    'outputs': node_info.get('outputs', {}),
                    'error': node_info.get('error'),
                    'framework': 'langgraph',
                    'component_type': 'agent'
                }

                # Add session information if available
                if self.session:
                    agent_span_data.update({
                        'session_id': self.session.session_id,
                        'session_type': self.session.session_type,
                        'chat_session_id': self.session.session_id,
                        'message_type': 'agent_response',
                        'message_sequence': self._message_sequence,
                        'agent_orchestration_id': self._current_orchestration_id,
                        'session_metadata': self.session.to_dict()
                    })

                # Send span to trace collector (will be collected for hierarchical processing)
                self.sdk._trace_collector.process_span(agent_span_data)
                logger.debug(f"Sent LangGraph agent span: {node_info['agent_name']} for session trace: {self._session_trace_id}")

        except Exception as e:
            logger.error(f"Failed to send LangGraph agent span: {e}")

    def finalize_langgraph_traces(self):
        """Finalize LangGraph session by triggering hierarchical trace processing."""
        logger.debug("Finalizing LangGraph session traces...")

        # If we have a session trace ID, finalize the hierarchical trace
        if self._session_trace_id and self.sdk and hasattr(self.sdk, '_trace_collector') and self.sdk._trace_collector:
            try:
                logger.debug(f"Finalizing hierarchical trace for session: {self._session_trace_id}")
                self.sdk._trace_collector.finalize_trace(self._session_trace_id)
                logger.debug(f"Successfully finalized hierarchical trace: {self._session_trace_id}")
            except Exception as e:
                logger.error(f"Failed to finalize hierarchical trace {self._session_trace_id}: {e}")
        else:
            logger.debug("No session trace ID available for hierarchical finalization")

        # Clear active traces and reset state
        self._active_traces.clear()
        self._active_nodes.clear()
        self._trace_finalization_pending = False
        self._current_orchestration_id = None

        # Note: We don't reset _session_trace_id here as it should persist for the session
        # It will be reset when a new session is created

        logger.debug("LangGraph session traces finalized")
    


@asynccontextmanager
async def langgraph_trace_context(handler: VaqueroLangGraphHandler):
    """
    Context manager for LangGraph tracing that ensures proper cleanup.
    
    This context manager ensures that traces are finalized and sent
    before the context exits, addressing the timing issues with
    LangGraph's execution flow.
    """
    try:
        yield handler
    finally:
        # Ensure traces are finalized before context exit
        handler.finalize_langgraph_traces()
        
        # Give a moment for traces to be sent
        await asyncio.sleep(0.1)


def get_vaquero_langgraph_handler(**kwargs) -> VaqueroLangGraphHandler:
    """
    Get a Vaquero handler specifically configured for LangGraph.
    
    Args:
        **kwargs: Additional arguments for the handler
        
    Returns:
        VaqueroLangGraphHandler: Configured handler for LangGraph
    """
    return VaqueroLangGraphHandler(**kwargs)


def create_langgraph_config(handler: VaqueroLangGraphHandler) -> Dict[str, Any]:
    """
    Create a configuration dict for LangGraph with the Vaquero handler.
    
    Args:
        handler: VaqueroLangGraphHandler instance
        
    Returns:
        Dict containing the configuration for LangGraph
    """
    return {
        'callbacks': [handler],
        'configurable': {
            'vaquero_handler': handler
        }
    }