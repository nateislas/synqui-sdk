# 🤠 Vaquero Python SDK

<div align="center">
  <h3>System intelligence for multi-agent AI</h3>
  <p><strong>Architecture extraction</strong> • <strong>Agent coordination</strong> • <strong>Performance insights</strong></p>

  [![PyPI version](https://badge.fury.io/py/vaquero-sdk.svg)](https://badge.fury.io/py/vaquero-sdk)
  [![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
  [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
</div>

---

## ⚡ Quick Start

### 1. Install
```bash
pip install vaquero-sdk
```

### 2. Get Your API Key
1. Go to the [Vaquero Dashboard](https://www.vaquero.app)
2. Create a new project (or select an existing one)
3. Navigate to the project's **Settings** page
4. Click **Create Project API Key** (keys start with `cf_`)

### 3. Initialize Vaquero
```python
import vaquero
import os

vaquero.init(
    project_name="my-project",
    project_api_key=os.getenv("VAQUERO_PROJECT_API_KEY"),
    environment=os.getenv("VAQUERO_ENVIRONMENT", "development")
)
```

### 4. Integrate with LangChain
```python
from vaquero.langchain import get_vaquero_handler
from langchain_openai import ChatOpenAI

# Create handler
handler = get_vaquero_handler(
    parent_context={"pipeline": "demo"}
)

# Use with LLM
llm = ChatOpenAI(callbacks=[handler])
llm.invoke("Hello, world!")

# Done! ✨ View your traces at https://www.vaquero.app
```

---

## 🎯 Key Features

| Feature | Description |
|---------|-------------|
| 🧠 **Automatic Failure Analysis** | AI-powered root cause analysis—know what broke and how to fix it instantly |
| 📊 **Architecture Performance Tracking** | Track architecture evolution with real data. Compare versions and know which configurations work before shipping |
| 🔧 **Development & Production Modes** | Debug fast in development. Monitor reliably in production. One platform for both |
| 🤖 **MCP Integration** | Your agents fix themselves. Connect via MCP to query insights, identify issues, and implement fixes automatically |
| 📈 **Performance Monitoring** | Track success rates, latency, and costs over time. Get alerted when patterns start degrading |
| 🏗️ **System Architecture Visualization** | Automatically extract and visualize agent relationships and coordination patterns |

---

## 📚 Resources

- **[💡 Examples](examples/)** - Real-world examples and integration patterns
- **[🎯 Demo: Article Explainer](demos/article-explainer/)** - Full-featured demo application using LangGraph and Vaquero
- **[📖 Documentation](https://www.vaquero.app/docs)** - Complete API reference and guides

---

## 🔧 Installation Options

### 🛠️ From PyPI (Recommended)
```bash
pip install vaquero-sdk
```

> **Note:** The package is installed as `vaquero-sdk`, but imported in Python as `import vaquero`.

### 🔨 From Source
```bash
git clone https://github.com/nateislas/vaquero-sdk.git
cd vaquero-sdk
pip install -e .
```

### 📦 With All Dependencies
```bash
pip install vaquero-sdk[all]
```

---

## 💻 Code Examples

### LangChain Integration

**Basic LLM Usage**
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

**LangChain Agents**
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

**LangChain Chains**
```python
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

# Create handler
handler = get_vaquero_handler()

# Use with chain
chain = LLMChain(llm=llm, prompt=prompt, callbacks=[handler])
chain.run("input")
```

### LangGraph Integration

**Basic Workflow**
```python
import vaquero
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

**Complete Example (from Article Explainer)**
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

### Data Processing Pipeline Example

**Using LangChain Agents with Vaquero**
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

---

## 🎨 Advanced Usage

### Session Management

**Creating and Managing Sessions**
```python
# Start a new chat session
session = vaquero.start_chat_session(
    name="user-123-session",
    session_type="chat",
    timeout_minutes=30,
    max_duration_minutes=240,
    metadata={"user_id": "123", "environment": "production"}
)

# Session automatically groups related traces
# Use the same session for multiple invocations
handler = VaqueroLangGraphHandler(session=session)
```

**Session Lifecycle**
```python
# Sessions automatically timeout after inactivity
# Manually end a session if needed
if session:
    session.end_session("user_logout")
```

### Graph Architecture Registration

**Capture Your Agent Structure**
```python
# Register graph architecture for visualization
handler.set_graph_architecture(
    graph=app.get_graph(),
    graph_name="CustomerSupportAgent"
)

# This enables:
# - Automatic node/edge extraction
# - Architecture visualization in dashboard
# - Version tracking of graph changes
```

### Custom Configuration

**Advanced Setup**
```python
import vaquero
import os

vaquero.init(
    project_name="my-project",
    project_api_key=os.getenv("VAQUERO_PROJECT_API_KEY"),
    environment=os.getenv("VAQUERO_ENVIRONMENT", "development")
)
```

### Environment Variables

**Configuration via Environment**
```bash
VAQUERO_PROJECT_API_KEY=cf_your-api-key
VAQUERO_PROJECT_NAME=my-project
VAQUERO_ENVIRONMENT=development
```

```python
import vaquero
import os

vaquero.init(
    project_name=os.getenv("VAQUERO_PROJECT_NAME"),
    project_api_key=os.getenv("VAQUERO_PROJECT_API_KEY"),
    environment=os.getenv("VAQUERO_ENVIRONMENT", "development")
)
```

### Production Configuration
```python
import vaquero
import os

vaquero.init(
    project_name="production-app",
    project_api_key=os.getenv("VAQUERO_PROJECT_API_KEY"),
    environment="production"
)
```

In production, traces are batched and sent asynchronously to avoid blocking your application.

---

## 🔧 Configuration Reference

### Initialization Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `project_api_key` | `str` | **Yes** | - | Your Vaquero API key (starts with `cf_`) |
| `project_name` | `str` | No | `None` | Project name (recommended, auto-resolves project ID) |
| `project_id` | `str` | No | `None` | Project ID (used if project_name not provided) |
| `endpoint` | `str` | No | `"https://api.vaquero.app"` | Vaquero API endpoint |
| `environment` | `str` | No | `"development"` | Environment: `"development"`, `"staging"`, or `"production"` |

### Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `VAQUERO_PROJECT_API_KEY` | Your project API key | `cf_...` |
| `VAQUERO_PROJECT_NAME` | Name of your project | `my-project` |
| `VAQUERO_PROJECT_ID` | Project ID (optional) | `uuid-here` |
| `VAQUERO_ENVIRONMENT` | Environment name | `development`, `staging`, or `production` |

### Environment-Specific Settings

The SDK automatically adjusts batch sizes and flush intervals based on environment:

```python
# Development (faster feedback)
vaquero.init(
    project_api_key="key",
    project_name="my-app",
    environment="development"
)
# → batch_size=10, flush_interval=2.0s

# Staging (balanced)
vaquero.init(
    project_api_key="key",
    project_name="my-app",
    environment="staging"
)
# → batch_size=50, flush_interval=3.0s

# Production (optimized for throughput)
vaquero.init(
    project_api_key="key",
    project_name="my-app",
    environment="production"
)
# → batch_size=100, flush_interval=5.0s
```

---

## 🚨 Best Practices

### ✅ Do
- **Use project names** - `vaquero.init(project_api_key="key", project_name="my-app")`
- **Register graph architecture** - `handler.set_graph_architecture()` for LangGraph workflows
- **Start chat sessions** - Use `start_chat_session()` for conversational agents
- **Add meaningful context** - Pass `parent_context` to handlers for better trace organization
- **Handle errors gracefully** - SDK captures exceptions automatically

### ❌ Avoid
- **Sensitive data** - Don't log passwords, keys, or PII in attributes
- **Forgetting to pass handlers** - Always include handlers in callback lists
- **Blocking operations in async code** - Use proper async patterns

---

## 📝 Contributing

Join our community! See [Contributing Guide](CONTRIBUTING.md)

---

<div align="center">
  <p><strong>Need help?</strong> Join our <a href="https://discord.gg/vaquero">Discord community</a> or email <a href="mailto:support@vaquero.app">support@vaquero.app</a></p>
</div>
