"""LangGraph-specific processor for hierarchical trace collection."""

import logging
from typing import Dict, List, Any, Optional
from .base_processor import FrameworkProcessor, HierarchicalTrace
from ..cost_calculator import calculate_cost

logger = logging.getLogger(__name__)

class LangGraphProcessor(FrameworkProcessor):
    """LangGraph processor that handles agent swarm workflows."""
    
    def __init__(self):
        self.agents = {}  # agent_name -> agent_data
        self.spans = []  # All spans for this trace
        self.agent_orchestrations = {}  # orchestration_id -> orchestration_data
    
    def add_span(self, span_data: Dict[str, Any]) -> None:
        """Add LangGraph span to processor."""
        self.spans.append(span_data)
        
        agent_name = span_data.get('agent_name', '')
        component_type = span_data.get('component_type', 'agent')
        logger.info(f"📥 Processing LangGraph span: {agent_name} (type: {component_type})")
        
        # Extract session information
        session_id = span_data.get('session_id')
        chat_session_id = span_data.get('chat_session_id')
        agent_orchestration_id = span_data.get('agent_orchestration_id')
        
        # Create or update agent orchestration
        if agent_orchestration_id and agent_orchestration_id not in self.agent_orchestrations:
            self.agent_orchestrations[agent_orchestration_id] = {
                'id': agent_orchestration_id,
                'session_id': session_id,
                'chat_session_id': chat_session_id,
                'agents': [],
                'start_time': span_data.get('start_time'),
                'end_time': span_data.get('end_time'),
                'status': span_data.get('status', 'completed')
            }
        
        # Determine the level based on component type
        if component_type == 'agent':
            level = 2  # Individual agents are level 2
        elif component_type in ['llm', 'tool', 'chain', 'prompt']:
            level = 3  # Internal components are level 3
        else:
            level = 2  # Default to level 2
        
        # Add agent to orchestration
        if agent_orchestration_id:
            agent_data = {
                'name': agent_name,
                'level': level,
                'framework': 'langgraph',
                'component_type': component_type,
                'parent_agent_id': None,
                'spans': [span_data],
                'session_id': session_id,
                'chat_session_id': chat_session_id,
                'agent_orchestration_id': agent_orchestration_id,
                'message_type': span_data.get('message_type', 'agent_response'),
                'message_sequence': span_data.get('message_sequence', 0)
            }
            
            self.agent_orchestrations[agent_orchestration_id]['agents'].append(agent_data)
            logger.debug(f"Added LangGraph {component_type} {agent_name} to orchestration {agent_orchestration_id}")
        else:
            # Standalone agent/component
            if agent_name not in self.agents:
                self.agents[agent_name] = {
                    'name': agent_name,
                    'level': level,
                    'framework': 'langgraph',
                    'component_type': component_type,
                    'parent_agent_id': None,
                    'spans': []
                }
            
            self.agents[agent_name]['spans'].append(span_data)
            logger.debug(f"Added standalone LangGraph {component_type} {agent_name}")
    
    def process_trace(self, trace_id: str) -> HierarchicalTrace:
        """Process all spans into hierarchical format."""
        agents = []
        dependencies = []
        
        # Extract session information from spans
        trace_session_id = None
        chat_session_id = None
        for span in self.spans:
            if span.get('session_id'):
                trace_session_id = span['session_id']
            if span.get('chat_session_id'):
                chat_session_id = span['chat_session_id']
                break
        
        # For session-aware traces, we need to use the original trace_id
        # but ensure all agents are grouped under the session
        if chat_session_id:
            logger.info(f"Processing session-aware trace {trace_id} for chat session {chat_session_id}")
        else:
            logger.info(f"Processing standalone trace {trace_id}")
        
        # If we have a session, create a proper hierarchical structure
        if chat_session_id:
            # Create session orchestration agent (level 1)
            session_orchestration = {
                'name': f"chat_session_{chat_session_id[:8]}",
                'level': 1,
                'framework': 'langgraph',
                'component_type': 'session_orchestration',
                'parent_agent_id': None,
                'session_id': trace_session_id,
                'chat_session_id': chat_session_id,
                'start_time': self._get_earliest_start_time(self.spans),
                'end_time': self._get_latest_end_time(self.spans),
                'status': 'completed',
                'agents': []
            }
            
            # Group agents by orchestration and level
            agent_groups = {}
            for agent_name, agent_data in self.agents.items():
                orchestration_id = agent_data.get('agent_orchestration_id', 'default')
                if orchestration_id not in agent_groups:
                    agent_groups[orchestration_id] = {'agents': [], 'components': []}
                
                if agent_data.get('level', 2) == 2:  # Agent level
                    agent_groups[orchestration_id]['agents'].append(agent_data)
                else:  # Component level
                    agent_groups[orchestration_id]['components'].append(agent_data)
            
            # Process each orchestration group
            for orchestration_id, group in agent_groups.items():
                # Create agent orchestration entry (level 2)
                orchestration_entry = {
                    'name': f"agent_orchestration_{orchestration_id[:8]}" if orchestration_id != 'default' else 'agent_orchestration',
                    'level': 2,
                    'framework': 'langgraph',
                    'component_type': 'agent_orchestration',
                    'parent_agent_id': session_orchestration['name'],
                    'session_id': trace_session_id,
                    'chat_session_id': chat_session_id,
                    'start_time': self._get_earliest_start_time([span for agent in group['agents'] for span in agent['spans']]),
                    'end_time': self._get_latest_end_time([span for agent in group['agents'] for span in agent['spans']]),
                    'status': 'completed',
                    'agents': []
                }
                
                # Add individual agents (level 3)
                for agent_data in group['agents']:
                    model_info = self._extract_model_info(agent_data['spans'])
                    total_tokens = sum(span.get('input_tokens', 0) + span.get('output_tokens', 0) for span in agent_data['spans'])
                    total_cost = sum(span.get('cost', 0) for span in agent_data['spans'])
                    
                    agent_entry = {
                        'name': agent_data['name'],
                        'level': 3,  # Individual agents are level 3
                        'framework': 'langgraph',
                        'component_type': 'agent',
                        'parent_agent_id': orchestration_entry['name'],
                        'session_id': trace_session_id,
                        'chat_session_id': chat_session_id,
                        'start_time': self._get_earliest_start_time(agent_data['spans']),
                        'end_time': self._get_latest_end_time(agent_data['spans']),
                        'duration': self._calculate_duration(agent_data['spans']),
                        'status': 'completed',
                        'total_tokens': total_tokens,
                        'total_cost': total_cost,
                        'model_info': model_info,
                        'agents': []
                    }
                    
                    # Add components (level 4) as sub-agents
                    for component_data in group['components']:
                        if component_data.get('parent_agent_id') == agent_data['name']:
                            component_entry = {
                                'name': component_data['name'],
                                'level': 4,  # Components are level 4
                                'framework': 'langgraph',
                                'component_type': component_data.get('component_type', 'component'),
                                'parent_agent_id': agent_entry['name'],
                                'session_id': trace_session_id,
                                'chat_session_id': chat_session_id,
                                'start_time': self._get_earliest_start_time(component_data['spans']),
                                'end_time': self._get_latest_end_time(component_data['spans']),
                                'duration': self._calculate_duration(component_data['spans']),
                                'status': 'completed',
                                'agents': []
                            }
                            agent_entry['agents'].append(component_entry)
                    
                    orchestration_entry['agents'].append(agent_entry)
                
                session_orchestration['agents'].append(orchestration_entry)
                agents.append(orchestration_entry)
            
            # Add the session orchestration as the main agent
            agents.insert(0, session_orchestration)
        else:
            # Fallback to standalone agents if no session
            for agent_name, agent_data in self.agents.items():
                # Extract model information from spans
                model_info = self._extract_model_info(agent_data['spans'])
                
                # Calculate metrics
                total_tokens = sum(span.get('input_tokens', 0) + span.get('output_tokens', 0) for span in agent_data['spans'])
                total_cost = sum(span.get('cost', 0) for span in agent_data['spans'])
                
                agent_entry = {
                    'name': agent_name,
                    'level': 1,
                    'framework': 'langgraph',
                    'component_type': 'agent',
                    'parent_agent_id': None,
                    'session_id': trace_session_id,
                    'start_time': self._get_earliest_start_time(agent_data['spans']),
                    'end_time': self._get_latest_end_time(agent_data['spans']),
                    'duration': self._calculate_duration(agent_data['spans']),
                    'status': 'completed',
                    'total_tokens': total_tokens,
                    'total_cost': total_cost,
                    'model_info': model_info,
                    'agents': []
                }
                agents.append(agent_entry)
        
        # Create hierarchical trace
        hierarchical_trace = HierarchicalTrace(
            trace_id=trace_id,  # Use the original trace_id, not session_trace_id
            name=f"LangGraph Session" if chat_session_id else f"LangGraph Workflow",
            agents=agents,
            dependencies=dependencies,
            metadata={
                'framework': 'langgraph',
                'session_id': trace_session_id,
                'chat_session_id': chat_session_id,
                'agent_count': len(agents),
                'orchestration_count': len(self.agent_orchestrations)
            }
        )
        
        logger.info(f"Processed LangGraph trace {trace_id} with {len(agents)} agents")
        return hierarchical_trace
    
    def _extract_model_info(self, spans: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract model information from spans."""
        model_info = {}
        
        for span in spans:
            if span.get('model_name'):
                model_info['model_name'] = span.get('model_name')
                model_info['model_provider'] = span.get('model_provider')
                model_info['model_parameters'] = span.get('model_parameters')
                break
        
        return model_info
    
    def _get_earliest_start_time(self, spans: List[Dict[str, Any]]) -> str:
        """Get earliest start time from spans."""
        start_times = [s.get('start_time') for s in spans if s.get('start_time')]
        return min(start_times) if start_times else None
    
    def _get_latest_end_time(self, spans: List[Dict[str, Any]]) -> str:
        """Get latest end time from spans."""
        end_times = [s.get('end_time') for s in spans if s.get('end_time')]
        return max(end_times) if end_times else None
    
    def _calculate_duration(self, spans: List[Dict[str, Any]]) -> int:
        """Calculate total duration from spans."""
        start_time = self._get_earliest_start_time(spans)
        end_time = self._get_latest_end_time(spans)
        if start_time and end_time:
            from datetime import datetime
            start = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            end = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
            return int((end - start).total_seconds() * 1000)
        return 0
    
    def detect_framework(self, span_data: Dict[str, Any]) -> bool:
        """Detect if this is a LangGraph span."""
        agent_name = span_data.get('agent_name', '')
        metadata = span_data.get('metadata', {})
        
        # Check for LangGraph indicators
        return (
            agent_name.startswith('langgraph:') or
            'langgraph' in str(metadata).lower() or
            span_data.get('framework') == 'langgraph' or
            span_data.get('chat_session_id') is not None  # LangGraph workflows have chat sessions
        )
