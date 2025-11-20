# Code Examples

## LangChain Integration

### Basic LLM Usage
```python
import vaquero
import os
from vaquero.langchain import get_vaquero_handler
from langchain_openai import ChatOpenAI

# Initialize Vaquero
vaquero.init(
    project_name="langchain-demo",
    project_api_key=os.getenv("VAQUERO_PROJECT_API_KEY")
)

# Create handler with context
handler = get_vaquero_handler(
    parent_context={"pipeline": "demo"}
)

# Use with LLM
llm = ChatOpenAI(callbacks=[handler])
llm.invoke("Hello")
```

### LangChain Agents
```python
from langchain.agents import initialize_agent

# Create handler
handler = get_vaquero_handler(
    parent_context={"agent_type": "data_processing"}
)

# Initialize agent with handler
agent = initialize_agent(
    tools, llm, agent="zero-shot-react-description", callbacks=[handler]
)
agent.run("task")
```

### LangChain Chains
```python
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

# Create handler
handler = get_vaquero_handler()

# Use with chain
chain = LLMChain(llm=llm, prompt=prompt, callbacks=[handler])
chain.run("input")
```

## LangGraph Integration

### Basic Workflow
```python
import vaquero
import os
from vaquero.langgraph import VaqueroLangGraphHandler

# 1. Initialize Vaquero
vaquero.init(
    project_name="my-agent",
    project_api_key=os.getenv("VAQUERO_PROJECT_API_KEY")
)

# 2. Start a session
session = vaquero.start_chat_session(
    name="chat-session-1",
    session_type="chat",
    timeout_minutes=30,
    metadata={"user_id": "123"}
)

# 3. Create the handler
handler = VaqueroLangGraphHandler(session=session)

# 4. Register graph architecture (recommended)
handler.set_graph_architecture(
    graph=app.get_graph(),
    graph_name="MyAgent"
)

# 5. Invoke with handler
config = {
    "callbacks": [handler],
    "configurable": {"vaquero_handler": handler}
}
app.invoke(inputs, config=config)
```

### Complete Example (from Article Explainer)
```python
import vaquero
import os
from vaquero.langgraph import VaqueroLangGraphHandler
from langchain_core.callbacks import UsageMetadataCallbackHandler

# Initialize
vaquero.init(
    project_name=os.getenv('VAQUERO_PROJECT_NAME', "article-explainer"),
    project_api_key=os.getenv('VAQUERO_PROJECT_API_KEY'),
    environment=os.getenv('VAQUERO_ENVIRONMENT', 'development')
)

# Start session for document processing
session = vaquero.start_chat_session(
    name=f"pdf_chat_{document_name}",
    session_type="chat",
    timeout_minutes=30,
    metadata={
        "document_name": document_name,
        "document_type": "pdf"
    }
)

# Create handler with session
handler = VaqueroLangGraphHandler(session=session)

# Register graph architecture
handler.set_graph_architecture(
    graph=app.get_graph(),
    graph_name="ArticleExplainer"
)

# Invoke with multiple callbacks
usage_handler = UsageMetadataCallbackHandler()
config = {
    "callbacks": [handler, usage_handler],
    "configurable": {"vaquero_handler": handler}
}
response_state = app.invoke(agent_state, config=config)
```

## Data Processing Pipeline Example

### Using LangChain Agents with Vaquero
```python
import vaquero
import os
from vaquero.langchain import get_vaquero_handler

# Initialize
vaquero.init(
    project_name="Simple Workflow",
    project_api_key=os.getenv("VAQUERO_PROJECT_API_KEY", ""),
    environment=os.getenv("VAQUERO_ENVIRONMENT", "development")
)

# Create handler for pipeline
handler = get_vaquero_handler(
    parent_context={"pipeline": "data_processing"}
)

# Use with agents
callbacks = [handler]
agents = create_pipeline_agents(callbacks=callbacks)

# Agents automatically trace their execution
result = agents["data_processor"].invoke({"input": "Process this data..."})
```

