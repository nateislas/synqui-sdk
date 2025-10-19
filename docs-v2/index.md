# Vaquero Python SDK Documentation

<div align="center">
  <h2>🔬 AI-Native Observability Platform</h2>
  <p><strong>Built specifically for LLM applications, agent workflows, and AI system debugging</strong></p>
</div>

---

## What is Vaquero?

**Vaquero** is an open-source observability platform designed specifically for AI agents and LLM applications. Unlike traditional monitoring tools, Vaquero understands the unique complexity of AI systems and provides the insights you need to debug, optimize, and scale your AI workflows.

### Why Vaquero?

- **🤖 AI-First Design** - Built from the ground up for LLM applications and agent workflows
- **🔍 Zero-Configuration Tracing** - `@vaquero.trace()` decorator works instantly out of the box
- **⚡ Production Ready** - Enterprise-grade reliability with batching, retries, and error handling
- **💡 AI-Powered Insights** - Automatic analysis of trace patterns with actionable recommendations
- **🔧 Framework Agnostic** - Works with any AI framework (LangChain, LlamaIndex, custom agents, etc.)

## Architecture

```mermaid
graph TB
    A[🤖 AI Application<br/>LangChain, Custom Agents] --> B[🔍 Vaquero SDK<br/>@vaquero.trace()]
    B --> C[📦 Batch Processing<br/>Intelligent Batching]
    C --> D[🌐 API Ingestion<br/>Secure Transport]
    D --> E[📊 Dashboard<br/>Real-time Analytics]
    E --> F[💡 AI Insights<br/>Performance Optimization]

    style A fill:#e1f5fe
    style B fill:#f3e5f5
    style C fill:#e8f5e8
    style D fill:#fff3e0
    style E fill:#fce4ec
    style F fill:#f1f8e9
```

## Quick Start

Get started in 3 simple steps:

<div class="quick-start-grid">

### 1. Install & Configure
```python title="Installation"
pip install vaquero-sdk

import vaquero
vaquero.init(api_key="cf_your-project-key-here")
```

### 2. Add Tracing
```python title="Basic Tracing"
@vaquero.trace("my_agent")
def process_data(data):
    # Your AI logic here
    return result

# Works with LangChain too!
from vaquero.langchain import get_vaquero_handler

handler = get_vaquero_handler()
chain.invoke(input, config={"callbacks": [handler]})
```

### 3. Analyze Results
```python title="Dashboard Access"
# Traces automatically appear in your dashboard
# Access comprehensive insights and performance analytics
```

**[→ Start Here: Installation & Setup](./quick-start/setup.md)**

---

## Documentation Sections

| Section | Description | Primary Audience |
|---------|-------------|------------------|
| **[Quick Start](./quick-start/)** | Get up and running in minutes | **New users** |
| **[SDK Reference](./sdk-reference/)** | Complete API and configuration guide | **Developers** |
| **[Agent Frameworks](./agent-frameworks/)** | Framework-specific integration guides | **AI engineers** |
| **[Observability Platform](./observability-platform/)** | Dashboard and insights guide | **Everyone** |
| **[Advanced Usage](./advanced-usage/)** | Production deployment and optimization | **Platform teams** |

---

## Use Cases

### AI Agent Development
```python title="LangChain Integration"
from vaquero.langchain import get_vaquero_handler

handler = get_vaquero_handler(parent_context={"team": "research"})
llm_chain.invoke(input, config={"callbacks": [handler]})
```

### Data Processing Pipelines
```python title="Multi-Step Workflows"
@vaquero.trace("data_pipeline")
async def process_dataset(dataset):
    # Step 1: Schema analysis
    # Step 2: Data transformation
    # Step 3: Quality validation
    # All steps automatically traced and analyzed
```

### LLM Application Monitoring
```python title="Automatic Instrumentation"
vaquero.init(auto_instrument_llm=True)

# OpenAI, Anthropic, and other LLM calls
# automatically captured with tokens, cost, timing
response = client.chat.completions.create(...)
```

### Performance Optimization
```python title="AI-Powered Insights"
# Identify bottlenecks and optimization opportunities
# Dashboard shows slow operations, error patterns
# AI insights suggest specific improvements
```

---

## Key Features

| Feature | Description | Benefit |
|---------|-------------|---------|
| **Zero-Configuration Tracing** | `@vaquero.trace()` decorator works instantly | Start monitoring immediately |
| **LangChain Integration** | Built-in callback handlers for LCEL chains | Seamless agent observability |
| **AI-Powered Insights** | Automatic analysis of trace patterns | Proactive optimization suggestions |
| **Dashboard Analytics** | Visual trace exploration and performance monitoring | Self-service debugging |
| **Production Ready** | Circuit breakers, batching, error handling | Enterprise-grade reliability |
| **Framework Agnostic** | Works with any agent framework | Future-proof architecture |

---

## Getting Help

### Documentation
- **[Complete Guides](./sdk-reference/)** - Detailed setup and configuration
- **[Framework Examples](./agent-frameworks/)** - Framework-specific patterns
- **[Dashboard Guide](./observability-platform/)** - Analytics and insights

### Community
- **[Discord Community](https://discord.gg/vaquero)** - Get help and share experiences
- **[GitHub Issues](https://github.com/vaquero/vaquero-python/issues)** - Report bugs and request features

### Support
- **Email**: support@vaquero.app
- **Response Time**: < 24 hours for enterprise customers

---

## Next Steps

Ready to get started? Choose your path:

### New to Vaquero?
**[→ Start with Quick Start](./quick-start/setup.md)** - 5-minute setup guide

### Migrating from v1?
**[→ Migration Guide](./quick-start/migration.md)** - Upgrade your existing setup

### Building AI Agents?
**[→ LangChain Integration](./agent-frameworks/langchain-integration.md)** - Best practices for agent observability

### Need Analytics?
**[→ Dashboard Guide](./observability-platform/dashboard-overview.md)** - Master trace analysis and insights

---

<div align="center">
  <p><strong>Questions?</strong> Join our <a href="https://discord.gg/vaquero">Discord community</a> or email <a href="mailto:support@vaquero.app">support@vaquero.app</a></p>
</div>
