"""Unified trace collector that routes to framework-specific processors."""

import logging
import uuid
import json
from typing import Dict, Any, Optional, TYPE_CHECKING
from datetime import datetime
from .processors import LangChainProcessor
from .processors.langgraph_processor import LangGraphProcessor

if TYPE_CHECKING:
    from .sdk import VaqueroSDK

logger = logging.getLogger(__name__)

def json_serializable(obj):
    """Convert objects to JSON-serializable format."""
    if isinstance(obj, uuid.UUID):
        return str(obj)
    elif isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, dict):
        return {k: json_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [json_serializable(item) for item in obj]
    return obj

class UnifiedTraceCollector:
    """Unified trace collector that routes spans to framework-specific processors."""
    
    def __init__(self, sdk: 'VaqueroSDK'):
        self.sdk = sdk
        self.config = sdk.config
        self.processors = {
            'langchain': LangChainProcessor(),
            'langgraph': LangGraphProcessor(),
            # Add other processors as needed
        }
        self.trace_processors = {}  # trace_id -> processor
        self._traces = {}  # For compatibility with shutdown method
        self._cached_user_id = None  # Cache user ID to avoid repeated whoami calls
        self._cached_project_id = None  # Cache project ID to avoid repeated whoami calls
    
    def process_span(self, span_data: Dict[str, Any]) -> None:
        """Process span with appropriate framework processor."""
        trace_id = span_data.get('trace_id')
        if not trace_id:
            logger.warning("Span has no trace_id, skipping")
            return
        
        logger.debug(f"Processing span with trace_id: {trace_id}, agent_name: {span_data.get('agent_name', 'unknown')}, component_type: {span_data.get('component_type', 'unknown')}")
        
        # Get or create processor for this trace
        if trace_id not in self.trace_processors:
            framework = self._detect_framework(span_data)
            self.trace_processors[trace_id] = self.processors[framework]
            logger.debug(f"Created {framework} processor for trace {trace_id}")
        
        # Add span to appropriate processor
        processor = self.trace_processors[trace_id]
        processor.add_span(span_data)
        logger.debug(f"Added span to processor for trace {trace_id}")
    
    def _detect_framework(self, span_data: Dict[str, Any]) -> str:
        """Detect framework from span data."""
        # Check LangGraph first since it has more specific detection
        if self.processors['langgraph'].detect_framework(span_data):
            return 'langgraph'
        
        # Then check LangChain
        if self.processors['langchain'].detect_framework(span_data):
            return 'langchain'
        
        # Default to langchain for backward compatibility
        return 'langchain'
    
    def finalize_trace(self, trace_id: str) -> None:
        """Finalize trace and send to database."""
        print(f"🔍 TRACE COLLECTOR: Finalizing trace {trace_id}")
        
        if trace_id not in self.trace_processors:
            print(f"🔍 TRACE COLLECTOR: No processor found for trace {trace_id}")
            logger.warning(f"No processor found for trace {trace_id}")
            return
        
        try:
            processor = self.trace_processors[trace_id]
            print(f"🔍 TRACE COLLECTOR: Processing trace with {type(processor).__name__}")
            hierarchical_trace = processor.process_trace(trace_id)
            
            print(f"🔍 TRACE COLLECTOR: Sending hierarchical trace to database")
            # Send to database
            self._send_to_database(hierarchical_trace)
            
            # Count agents vs components for better logging
            agent_count = sum(1 for agent in hierarchical_trace.agents if agent.get('level') == 1)
            component_count = sum(1 for agent in hierarchical_trace.agents if agent.get('level') == 2)
            total_count = len(hierarchical_trace.agents)
            
            if agent_count > 0 and component_count > 0:
                logger.info(f"Finalized trace {trace_id} with {total_count} entities ({agent_count} agents, {component_count} components)")
            else:
                logger.info(f"Finalized trace {trace_id} with {total_count} entities")
            
        except Exception as e:
            logger.error(f"Failed to finalize trace {trace_id}: {e}")
        finally:
            # Clean up
            if trace_id in self.trace_processors:
                del self.trace_processors[trace_id]
    
    def end_trace(self, trace_id: str, end_data: Dict[str, Any]) -> None:
        """End a trace and finalize it."""
        try:
            if trace_id in self.trace_processors:
                processor = self.trace_processors[trace_id]
                hierarchical_trace = processor.process_trace(trace_id)
                
                # Send to database
                self._send_to_database(hierarchical_trace)
                
                # Count agents vs components for better logging
                agent_count = sum(1 for agent in hierarchical_trace.agents if agent.get('level') == 1)
                component_count = sum(1 for agent in hierarchical_trace.agents if agent.get('level') == 2)
                total_count = len(hierarchical_trace.agents)
                
                if agent_count > 0 and component_count > 0:
                    logger.info(f"Finalized trace {trace_id} with {total_count} entities ({agent_count} agents, {component_count} components)")
                else:
                    logger.info(f"Finalized trace {trace_id} with {total_count} entities")
                
                # Clean up
                del self.trace_processors[trace_id]
            else:
                logger.warning(f"No processor found for trace {trace_id}")
                
        except Exception as e:
            logger.error(f"Failed to end trace {trace_id}: {e}")
    
    def _send_to_database(self, hierarchical_trace) -> None:
        """Send hierarchical trace to database."""
        try:
            trace_id = hierarchical_trace.trace_id
            # Calculate trace timing from agents
            start_times = []
            end_times = []
            for agent in hierarchical_trace.agents:
                if agent.get('start_time'):
                    # Convert string to datetime if needed
                    start_time = agent['start_time']
                    if isinstance(start_time, str):
                        from datetime import datetime
                        start_time = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                    start_times.append(start_time)
                if agent.get('end_time'):
                    # Convert string to datetime if needed
                    end_time = agent['end_time']
                    if isinstance(end_time, str):
                        from datetime import datetime
                        end_time = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
                    end_times.append(end_time)
            
            # Use earliest start and latest end times
            trace_start_time = min(start_times) if start_times else None
            trace_end_time = max(end_times) if end_times else None
            trace_duration_ms = 0
            if trace_start_time and trace_end_time:
                trace_duration_ms = int((trace_end_time - trace_start_time).total_seconds() * 1000)
            
            # Create trace data
            # Extract session_id from agents if available
            trace_session_id = None
            for agent in hierarchical_trace.agents:
                agent_session_id = None

                # Check agent metadata for session_id
                if agent.get('metadata') and isinstance(agent.get('metadata'), dict):
                    agent_session_id = agent['metadata'].get('session_id')

                # Check tags for session_id
                if not agent_session_id and agent.get('tags') and isinstance(agent.get('tags'), dict):
                    agent_session_id = agent['tags'].get('session_id')

                if agent_session_id:
                    trace_session_id = agent_session_id
                    break

            # Extract environment from metadata
            trace_environment = None
            if hierarchical_trace.metadata:
                trace_environment = hierarchical_trace.metadata.get('environment') or hierarchical_trace.metadata.get('mode')
            
            # Ensure we have valid datetime values for the API
            from datetime import datetime
            current_time = datetime.utcnow()
            
            # Format datetimes with explicit UTC timezone indicator
            def format_datetime(dt):
                if dt:
                    return dt.isoformat() + "Z" if not dt.isoformat().endswith('Z') else dt.isoformat()
                return current_time.isoformat() + "Z"
            
            # Extract session metadata from first agent that has it
            session_metadata = None
            for agent in hierarchical_trace.agents:
                if agent.get('session_metadata'):
                    session_metadata = agent['session_metadata']
                    break

            # Extract session fields
            session_type = None
            session_timeout_minutes = None
            message_count = 0
            if session_metadata:
                session_type = session_metadata.get('session_type')
                session_timeout_minutes = session_metadata.get('timeout_minutes')
                message_count = session_metadata.get('message_count', 0)

            # Extract chat_session_id from metadata
            chat_session_id = hierarchical_trace.metadata.get('chat_session_id') if hierarchical_trace.metadata else None
            
            trace_data = {
                "trace_id": hierarchical_trace.trace_id,
                "name": hierarchical_trace.name,
                "status": "completed",
                "start_time": format_datetime(trace_start_time),
                "end_time": format_datetime(trace_end_time),
                "duration_ms": trace_duration_ms,
                "session_id": trace_session_id,
                "session_type": session_type,
                "session_start_time": session_metadata.get('start_time') if session_metadata else None,
                "session_end_time": session_metadata.get('end_time') if session_metadata else None,
                "session_timeout_minutes": session_timeout_minutes,
                "message_count": message_count,
                "chat_session_id": chat_session_id,
                "environment": trace_environment,
                "tags": {},
                "metadata": hierarchical_trace.metadata or {}
            }
            
            # Create agents data
            agents_data = []
            for agent in hierarchical_trace.agents:
                # Use model information that was already extracted by the processor
                llm_model_name = agent.get('llm_model_name')
                llm_model_provider = agent.get('llm_model_provider')
                llm_model_parameters = agent.get('llm_model_parameters')
                system_prompt = agent.get('system_prompt')

                # Format agent start_time and end_time properly
                agent_start_time = agent.get('start_time')
                agent_end_time = agent.get('end_time')
                
                if agent_start_time and isinstance(agent_start_time, str):
                    from datetime import datetime
                    try:
                        agent_start_time = datetime.fromisoformat(agent_start_time.replace('Z', '+00:00')).isoformat() + "Z"
                    except (ValueError, AttributeError):
                        agent_start_time = None
                
                if agent_end_time and isinstance(agent_end_time, str):
                    from datetime import datetime
                    try:
                        agent_end_time = datetime.fromisoformat(agent_end_time.replace('Z', '+00:00')).isoformat() + "Z"
                    except (ValueError, AttributeError):
                        agent_end_time = None
                
                # Extract session fields from agent metadata
                agent_session_id = None
                message_type = None
                message_content = None
                message_sequence = None
                user_message_id = None
                agent_orchestration_id = None

                # Check agent metadata for session fields
                agent_metadata = agent.get('metadata', {}) or agent.get('tags', {})
                if isinstance(agent_metadata, dict):
                    agent_session_id = agent_metadata.get('session_id') or agent_metadata.get('chat_session_id')
                    message_type = agent_metadata.get('message_type')
                    message_content = agent_metadata.get('message_content')
                    message_sequence = agent_metadata.get('message_sequence')
                    user_message_id = agent_metadata.get('user_message_id')
                    agent_orchestration_id = agent_metadata.get('agent_orchestration_id')

                # Also check direct agent fields
                if not agent_session_id:
                    agent_session_id = agent.get('session_id') or agent.get('chat_session_id')
                if not message_type:
                    message_type = agent.get('message_type')
                if not message_content:
                    message_content = agent.get('message_content')
                if not message_sequence:
                    message_sequence = agent.get('message_sequence')
                if not user_message_id:
                    user_message_id = agent.get('user_message_id')
                if not agent_orchestration_id:
                    agent_orchestration_id = agent.get('agent_orchestration_id')

                agent_data = {
                    "trace_id": hierarchical_trace.trace_id,
                    "agent_id": agent.get('agent_id', str(uuid.uuid4())),
                    "name": agent.get('name', ''),
                    "type": agent.get('component_type', 'agent'),
                    "description": agent.get('description', ''),
                    "tags": agent.get('tags', {}),
                    "start_time": agent_start_time,
                    "end_time": agent_end_time,
                    "duration_ms": int(agent.get('duration_ms') or 0),
                    "input_tokens": agent.get('input_tokens') or 0,
                    "output_tokens": agent.get('output_tokens') or 0,
                    "total_tokens": agent.get('total_tokens') or 0,
                    "cost": agent.get('cost') or 0.0,
                    "status": agent.get('status', 'completed'),
                    "input_data": agent.get('input_data', {}),
                    "output_data": agent.get('output_data', {}),
                    # LLM-specific fields
                    "llm_model_name": llm_model_name,
                    "llm_model_provider": llm_model_provider,
                    "llm_model_parameters": llm_model_parameters,
                    "system_prompt": system_prompt,
                    # Hierarchical fields
                    "parent_agent_id": agent.get('parent_agent_id'),
                    "level": agent.get('level', 1),
                    "framework": agent.get('framework'),
                    "component_type": agent.get('component_type'),
                    "framework_metadata": agent.get('framework_metadata', {}),
                    # Chat session fields
                    "message_type": message_type,
                    "message_content": message_content,
                    "message_sequence": message_sequence,
                    "user_message_id": user_message_id,
                    "agent_orchestration_id": agent_orchestration_id,
                    "chat_session_id": agent_session_id
                }
                agents_data.append(agent_data)
            
            # Send as batch to API
            batch_data = {
                "traces": [trace_data],
                "agents": agents_data
            }
            
            self._send_batch_to_api(batch_data)
            
            logger.info(f"Sent hierarchical trace to database: {hierarchical_trace.trace_id}")
            logger.info(f"  Logical agents: {len([a for a in hierarchical_trace.agents if a.get('level') == 1])}")
            logger.info(f"  Internal components: {len([a for a in hierarchical_trace.agents if a.get('level') == 2])}")
            # Log component types
            component_types = {}
            for agent in hierarchical_trace.agents:
                if agent.get('level') == 2:
                    comp_type = agent.get('component_type', 'unknown')
                    component_types[comp_type] = component_types.get(comp_type, 0) + 1
            logger.info(f"  Component breakdown: {component_types}")
            
        except Exception as e:
            logger.error(f"Failed to send hierarchical trace to database: {e}", exc_info=True)
    
    def _send_agent_to_api(self, agent_data: dict) -> None:
        """Send individual agent to API."""
        try:
            import requests
            
            # Send to the traces API endpoint
            url = f"{self.sdk.config.endpoint}/api/v1/traces"
            headers = {
                "Authorization": f"Bearer {self.sdk.config.api_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(url, json=agent_data, headers=headers, timeout=30)
            
            if response.status_code not in [200, 201]:
                logger.warning(f"Failed to send agent to API: {response.status_code} - {response.text}")
            else:
                logger.debug(f"Successfully sent agent {agent_data.get('name')} to API")
                
        except Exception as e:
            logger.error(f"Failed to send agent to API: {e}")
    
    def _send_batch_to_api(self, batch_data: dict) -> None:
        """Send batch trace data to API."""
        try:
            import requests
            
            # Make batch_data JSON-serializable (convert UUIDs, datetimes, etc.)
            serializable_data = json_serializable(batch_data)
            
            # Get user ID and project ID from whoami endpoint
            user_id = self._get_user_id()
            project_id = self._cached_project_id
            
            # Log the project routing information
            logger.info(f"🔍 SDK: Sending batch to API with project_id: {project_id}")
            logger.info(f"🔍 SDK: Batch contains {len(serializable_data.get('traces', []))} traces")
            if serializable_data.get('traces'):
                for i, trace in enumerate(serializable_data.get('traces', [])):
                    logger.info(f"🔍 SDK: Trace {i}: {trace.get('name', 'unnamed')} (ID: {trace.get('trace_id', 'unknown')})")
            
            # Send to the batch traces API endpoint
            url = f"{self.sdk.config.endpoint}/api/v1/traces/batch"
            headers = {
                "Authorization": f"Bearer {self.sdk.config.api_key}",
                "Content-Type": "application/json"
            }
            
            # Add user ID and project ID headers if available
            if user_id:
                headers["X-User-ID"] = user_id
                logger.info(f"🔍 SDK: Added X-User-ID header: {user_id}")
            
            if project_id:
                headers["X-Project-ID"] = project_id
                logger.info(f"🔍 SDK: Added X-Project-ID header: {project_id}")
            else:
                logger.warning(f"🔍 SDK: No project_id available - traces may be sent to wrong project!")
            
            logger.info(f"🔍 SDK: Sending request to {url} with headers: {list(headers.keys())}")
            
            response = requests.post(url, json=serializable_data, headers=headers, timeout=30)
            
            if response.status_code not in [200, 201, 202]:
                logger.warning(f"Failed to send batch to API: {response.status_code} - {response.text}")
            else:
                logger.info(f"🔍 SDK: Successfully sent batch to API (status: {response.status_code})")
                
        except Exception as e:
            logger.error(f"Failed to send batch to API: {e}")
    
    def _get_user_id(self) -> Optional[str]:
        """Get user ID and project ID from whoami endpoint (cached)."""
        # Return cached user ID if available
        if self._cached_user_id is not None:
            return self._cached_user_id
            
        try:
            import requests
            
            # Call whoami endpoint to get user ID and project ID
            whoami_url = f"{self.sdk.config.endpoint}/api/v1/auth/whoami"
            whoami_headers = {
                "Authorization": f"Bearer {self.sdk.config.api_key}",
                "Content-Type": "application/json"
            }
            
            logger.info(f"🔍 SDK: Calling whoami endpoint: {whoami_url}")
            response = requests.get(whoami_url, headers=whoami_headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                user_id = data.get("user_id")
                # Use configured project_id instead of whoami project_id
                project_id = self.sdk.config.project_id
                
                # Log the whoami response for debugging
                logger.info(f"🔍 SDK: Whoami response - user_id: {user_id}, whoami_project_id: {data.get('project_id')}")
                logger.info(f"🔍 SDK: Using configured project_id: {project_id}")
                logger.info(f"🔍 SDK: Full whoami response: {data}")
                
                # Cache both user_id and project_id
                self._cached_user_id = user_id
                self._cached_project_id = project_id
                
                return user_id
            else:
                logger.warning(f"Failed to get user ID from whoami: {response.status_code}")
                return None
                
        except Exception as e:
            logger.warning(f"Failed to get user ID: {e}")
            return None
    
    def shutdown(self):
        """Shutdown the unified trace collector and finalize all pending traces."""
        logger.info("Unified trace collector shutdown - finalizing all pending traces")
        
        # Finalize all pending traces before shutdown
        pending_traces = list(self.trace_processors.keys())
        logger.info(f"Finalizing {len(pending_traces)} pending traces before shutdown")
        
        for trace_id in pending_traces:
            try:
                logger.info(f"Finalizing trace {trace_id} during shutdown")
                self.finalize_trace(trace_id)
            except Exception as e:
                logger.error(f"Failed to finalize trace {trace_id} during shutdown: {e}")
        
        logger.info("Unified trace collector shutdown complete")
