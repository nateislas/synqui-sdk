# 🚀 Vaquero SDK Documentation

**Comprehensive observability for multi-agent AI systems.** See your agent architecture evolve in real-time, debug failures faster, and keep your AI workflows running smoothly.

## 🎯 Quick Start (5 minutes)

Get up and running with Vaquero in just 3 simple steps:

<div class="quick-start-steps">

### 1️⃣ Install
```bash
pip install vaquero-sdk
```

### 2️⃣ Configure
```python
import vaquero

vaquero.configure(
    api_key="your-api-key",
    project_id="your-project-id"
)
```

### 3️⃣ Trace
```python
@vaquero.trace("my_agent")
def my_function(data):
    # Your code here
    return processed_data
```

</div>

**That's it!** Your functions are now automatically traced and monitored.

## 📚 Documentation Sections

<div class="nav-cards">

### 🚀 [Quick Start](./quick-start.md)
Get started in 5 minutes with installation, configuration, and your first trace.

### 📖 [Common Patterns](./patterns/)
Essential patterns for function tracing, API endpoints, database operations, and error handling.

### 🔧 [Advanced Features](./advanced/)
Power user features including auto-instrumentation, custom spans, and performance monitoring.

### 📚 [API Reference](./reference/)
Complete reference for configuration, tracing, spans, and utilities.

### 🛠️ [Integrations](./integrations/)
Framework-specific guides for FastAPI, Django, Flask, and Celery.

### ❓ [Troubleshooting](./troubleshooting.md)
Common issues, performance tips, and debugging guides.

</div>

## 🌟 Key Features

<div class="feature-grid">

### ⚡ **Zero-Config Setup**
Get started with just an API key. Everything else works out of the box.

### 🔍 **Automatic LLM Instrumentation**
Automatically trace OpenAI, Anthropic, and other LLM calls with prompts, tokens, and performance metrics.

### 📊 **Real-time Monitoring**
See your agent interactions, architecture evolution, and performance metrics in real-time.

### 🛠️ **Framework Integration**
Built-in support for FastAPI, Django, Flask, Celery, and more.

### 🔒 **Enterprise Security**
Project-scoped API keys, encrypted data in transit and at rest, and comprehensive audit trails.

</div>

## 💡 Use Cases

<div class="use-cases">

### 🤖 **AI Agent Development**
Monitor agent interactions, debug complex workflows, and optimize performance.

### 🔧 **API Development**
Trace API endpoints, monitor response times, and identify bottlenecks.

### 🗄️ **Database Operations**
Monitor query performance, track data flow, and optimize database usage.

### ⚙️ **Background Jobs**
Monitor Celery tasks, Redis operations, and distributed processing.

</div>

## 🚀 Next Steps

Ready to get started? Jump to the **[Quick Start guide](./quick-start.md)** or explore **[common patterns](./patterns/)** for practical examples.

Need help? Check out the **[troubleshooting guide](./troubleshooting.md)** or **[contact support](mailto:support@vaquero.com)**.

---

<div class="footer-note">
📖 **Need more details?** Browse the full documentation above or use the search to find specific topics.
</div>
