# 🚀 Vaquero Python SDK Documentation

<div align="center">
  <h2>Comprehensive observability and tracing for AI agents and applications</h2>
  <p><strong>Zero-config tracing</strong> • <strong>LangChain integration</strong> • <strong>AI-powered insights</strong></p>
</div>

---

## 🎯 What is Vaquero?

Vaquero is an **observability platform** designed specifically for AI agents and applications. Unlike traditional monitoring tools, Vaquero understands the unique challenges of AI workflows:

- **Agent execution flows** with complex tool calling patterns
- **LLM interactions** with automatic token and cost tracking
- **Multi-step reasoning** processes that traditional tools miss
- **Performance bottlenecks** in AI pipelines

## 🚀 Quick Start

Get started in 3 simple steps:

<div class="quick-start-grid">

### 1️⃣ Install & Configure
```python
pip install vaquero-sdk

import vaquero
vaquero.init(api_key="your-project-key")
```

### 2️⃣ Add Tracing
```python
@vaquero.trace("my_agent")
def process_data(data):
    # Your AI logic here
    return result

# Works with LangChain too!
from vaquero.langchain import get_vaquero_handler

handler = get_vaquero_handler()
chain.invoke(input, config={"callbacks": [handler]})
```

### 3️⃣ Analyze Results
```python
# Traces automatically appear in your dashboard
# Access insights and performance data
```

</div>

**[→ Start Here: Installation & Setup](./quick-start/setup.md)**

---

## 📚 Documentation Sections

<div class="docs-sections">

| Section | Description | Primary Audience |
|---------|-------------|------------------|
| **[🚀 Quick Start](./quick-start/)** | Get up and running in minutes | **New users** |
| **[🔧 SDK Reference](./sdk-reference/)** | Complete API and configuration guide | **Developers** |
| **[🤖 Agent Frameworks](./agent-frameworks/)** | Framework-specific integration guides | **AI engineers** |
| **[📊 Observability Platform](./observability-platform/)** | Dashboard and insights guide | **Everyone** |
| **[🛠️ Advanced Usage](./advanced-usage/)** | Production deployment and optimization | **Platform teams** |

</div>

---

## 🎯 Use Cases

<div class="use-cases-grid">

### **🔧 AI Agent Development**
```python
# LangChain integration with automatic tracing
from vaquero.langchain import get_vaquero_handler

handler = get_vaquero_handler(parent_context={"team": "research"})
llm_chain.invoke(input, config={"callbacks": [handler]})
```

### **📊 Data Processing Pipelines**
```python
# Multi-step workflows with comprehensive observability
@vaquero.trace("data_pipeline")
async def process_dataset(dataset):
    # Step 1: Schema analysis
    # Step 2: Data transformation
    # Step 3: Quality validation
    # All steps automatically traced and analyzed
```

### **🔍 LLM Application Monitoring**
```python
# Automatic LLM call instrumentation
vaquero.init(auto_instrument_llm=True)

# OpenAI, Anthropic, and other LLM calls
# automatically captured with tokens, cost, timing
response = client.chat.completions.create(...)
```

### **⚡ Performance Optimization**
```python
# Identify bottlenecks and optimization opportunities
# Dashboard shows slow operations, error patterns
# AI insights suggest specific improvements
```

</div>

---

## 🎨 Key Features

<div class="features-grid">

| Feature | Description | Benefit |
|---------|-------------|---------|
| **🔍 Zero-Config Tracing** | `@vaquero.trace()` decorator works instantly | Start monitoring immediately |
| **🤖 LangChain Integration** | Built-in callback handlers for LCEL chains | Seamless agent observability |
| **📊 AI-Powered Insights** | Automatic analysis of trace patterns | Proactive optimization suggestions |
| **🎛️ Dashboard Analytics** | Visual trace exploration and performance monitoring | Self-service debugging |
| **⚡ Production Ready** | Circuit breakers, batching, error handling | Enterprise-grade reliability |
| **🔧 Framework Agnostic** | Works with any agent framework | Future-proof architecture |

</div>

---

## 🚦 Getting Help

<div class="help-grid">

### **📖 Documentation**
- **[Complete Guides](./sdk-reference/)** - Detailed setup and configuration
- **[Framework Examples](./agent-frameworks/)** - Framework-specific patterns
- **[Dashboard Guide](./observability-platform/)** - Analytics and insights

### **💬 Community**
- **[Discord Community](https://discord.gg/vaquero)** - Get help and share experiences
- **[GitHub Issues](https://github.com/vaquero/vaquero-python/issues)** - Report bugs and request features

### **📧 Support**
- **Email**: support@vaquero.app
- **Response Time**: < 24 hours for enterprise customers

</div>

---

## 🎯 Next Steps

Ready to get started? Choose your path:

<div class="next-steps">

### **🆕 New to Vaquero?**
**[→ Start with Quick Start](./quick-start/setup.md)** - 5-minute setup guide

### **🔄 Migrating from v1?**
**[→ Migration Guide](./quick-start/migration.md)** - Upgrade your existing setup

### **🤖 Building AI Agents?**
**[→ LangChain Integration](./agent-frameworks/langchain-integration.md)** - Best practices for agent observability

### **📊 Need Analytics?**
**[→ Dashboard Guide](./observability-platform/dashboard-overview.md)** - Master trace analysis and insights

</div>

---

<div align="center">
  <p><strong>Questions?</strong> Join our <a href="https://discord.gg/vaquero">Discord community</a> or email <a href="mailto:support@vaquero.app">support@vaquero.app</a></p>
</div>
