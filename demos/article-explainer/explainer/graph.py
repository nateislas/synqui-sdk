from explainer.prompts import (
    DEVELOPER_SYSTEM_PROMPT,
    SUMMARIZER_SYSTEM_PROMPT,
    EXPLAINER_SYSTEM_PROMPT,
    ANALOGY_CREATOR_SYSTEM_PROMPT,
    VULNERABILITY_EXPERT_SYSTEM_PROMPT,
)
from explainer.service.config import get_chat_model
from langgraph.prebuilt import create_react_agent
from langgraph.graph import StateGraph, END
from langchain_core.tools import StructuredTool
from typing import List, Dict, Any, TypedDict
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage

# Initialize Article Explainer graph
model = get_chat_model()

# Define state for the graph
class ArticleExplainerState(TypedDict):
    """State for the Article Explainer multi-agent system."""
    messages: List[BaseMessage]
    active_agent: str

# Create StructuredTool instances for handoff
def create_handoff_tool_function(target_agent: str):
    """Create a function that returns a handoff result for a specific agent."""
    def handoff_function():
        """Tool to hand control to another agent."""
        return {"handoff": target_agent}
    return handoff_function

transfer_to_developer = StructuredTool.from_function(
    func=create_handoff_tool_function("developer"),
    name="transfer_to_developer",
    description="Tool to hand control to the Developer for code examples and technical implementations."
)

transfer_to_summarizer = StructuredTool.from_function(
    func=create_handoff_tool_function("summarizer"),
    name="transfer_to_summarizer",
    description="Tool to hand control to the Summarizer for concise summaries, key points, and TL;DR responses."
)

transfer_to_explainer = StructuredTool.from_function(
    func=create_handoff_tool_function("explainer"),
    name="transfer_to_explainer",
    description="Tool to hand control to the Explainer for detailed step-by-step breakdowns and educational explanations."
)

transfer_to_analogy_creator = StructuredTool.from_function(
    func=create_handoff_tool_function("analogy_creator"),
    name="transfer_to_analogy_creator",
    description="Tool to hand control to the Analogy Creator for creating relatable analogies and metaphors for complex concepts."
)

transfer_to_vulnerability_expert = StructuredTool.from_function(
    func=create_handoff_tool_function("vulnerability_expert"),
    name="transfer_to_vulnerability_expert",
    description="Tool to hand control to the Vulnerability Expert for analyzing potential weaknesses in arguments and methodology."
)

# Create agents using create_react_agent
developer = create_react_agent(
    model,
    prompt=DEVELOPER_SYSTEM_PROMPT,
    tools=[
        transfer_to_summarizer,
        transfer_to_explainer,
        transfer_to_analogy_creator,
        transfer_to_vulnerability_expert,
    ],
    name="developer",
)

summarizer = create_react_agent(
    model,
    prompt=SUMMARIZER_SYSTEM_PROMPT,
    tools=[
        transfer_to_developer,
        transfer_to_explainer,
        transfer_to_analogy_creator,
        transfer_to_vulnerability_expert,
    ],
    name="summarizer",
)

explainer = create_react_agent(
    model,
    prompt=EXPLAINER_SYSTEM_PROMPT,
    tools=[
        transfer_to_developer,
        transfer_to_summarizer,
        transfer_to_analogy_creator,
        transfer_to_vulnerability_expert,
    ],
    name="explainer",
)

analogy_creator = create_react_agent(
    model,
    prompt=ANALOGY_CREATOR_SYSTEM_PROMPT,
    tools=[
        transfer_to_developer,
        transfer_to_summarizer,
        transfer_to_explainer,
        transfer_to_vulnerability_expert,
    ],
    name="analogy_creator",
)

vulnerability_expert = create_react_agent(
    model,
    prompt=VULNERABILITY_EXPERT_SYSTEM_PROMPT,
    tools=[
        transfer_to_developer,
        transfer_to_summarizer,
        transfer_to_explainer,
        transfer_to_analogy_creator,
    ],
    name="vulnerability_expert",
)

# Create node functions for each agent
def developer_node(state, config=None):
    """Execute the developer agent."""
    agent_input = {"messages": state["messages"]}
    result = developer.invoke(agent_input, config=config)
    return {
        "messages": result["messages"],
        "active_agent": "developer"
    }

def summarizer_node(state, config=None):
    """Execute the summarizer agent."""
    agent_input = {"messages": state["messages"]}
    result = summarizer.invoke(agent_input, config=config)
    return {
        "messages": result["messages"],
        "active_agent": "summarizer"
    }

def explainer_node(state, config=None):
    """Execute the explainer agent."""
    agent_input = {"messages": state["messages"]}
    result = explainer.invoke(agent_input, config=config)
    return {
        "messages": result["messages"],
        "active_agent": "explainer"
    }

def analogy_creator_node(state, config=None):
    """Execute the analogy creator agent."""
    agent_input = {"messages": state["messages"]}
    result = analogy_creator.invoke(agent_input, config=config)
    return {
        "messages": result["messages"],
        "active_agent": "analogy_creator"
    }

def vulnerability_expert_node(state, config=None):
    """Execute the vulnerability expert agent."""
    agent_input = {"messages": state["messages"]}
    result = vulnerability_expert.invoke(agent_input, config=config)
    return {
        "messages": result["messages"],
        "active_agent": "vulnerability_expert"
    }

def route_based_on_handoff(state):
    """Route to the next agent based on handoff tool calls."""
    messages = state["messages"]
    if not messages:
        return END

    # Check the last message for tool calls
    last_message = messages[-1]
    if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
        for tool_call in last_message.tool_calls:
            # Check if this is a handoff tool
            if tool_call['name'].startswith('transfer_to_'):
                target_agent = tool_call['name'].replace('transfer_to_', '')
                return target_agent

    # Check the last message content for handoff indicators
    if hasattr(last_message, 'content'):
        content = last_message.content.lower()
        handoff_indicators = {
            'developer': ['code', 'implementation', 'technical'],
            'summarizer': ['summary', 'tl;dr', 'key points'],
            'explainer': ['explain', 'step-by-step', 'breakdown'],
            'analogy_creator': ['analogy', 'metaphor', 'relatable'],
            'vulnerability_expert': ['weakness', 'critique', 'analysis']
        }

        for agent, keywords in handoff_indicators.items():
            if any(keyword in content for keyword in keywords):
                return agent

    # Default: end the conversation
    return END

# Create the StateGraph
workflow = StateGraph(ArticleExplainerState)

# Add nodes for each agent
workflow.add_node("developer", developer_node)
workflow.add_node("summarizer", summarizer_node)
workflow.add_node("explainer", explainer_node)
workflow.add_node("analogy_creator", analogy_creator_node)
workflow.add_node("vulnerability_expert", vulnerability_expert_node)

# Set the entry point to explainer (default agent)
workflow.set_entry_point("explainer")

# Add conditional edges from each agent back to routing
for agent_name in ["developer", "summarizer", "explainer", "analogy_creator", "vulnerability_expert"]:
    workflow.add_conditional_edges(
        agent_name,
        route_based_on_handoff,
        {
            "developer": "developer",
            "summarizer": "summarizer",
            "explainer": "explainer",
            "analogy_creator": "analogy_creator",
            "vulnerability_expert": "vulnerability_expert",
            END: END
        }
    )

# Compile the graph
app = workflow.compile()
