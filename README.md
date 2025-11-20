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

> **Note:** The package is installed as `vaquero-sdk`, but imported in Python as `import vaquero`.

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

## 📚 Documentation

- **[📖 Code Examples](docs/EXAMPLES.md)** - LangChain and LangGraph integration examples
- **[🎨 Advanced Usage](docs/ADVANCED.md)** - Session management, graph architecture, and custom configuration
- **[🔧 Configuration Reference](docs/CONFIGURATION.md)** - Complete parameter and environment variable reference
- **[🚨 Best Practices](docs/BEST_PRACTICES.md)** - Recommended patterns and common pitfalls
- **[💡 Examples Directory](examples/)** - Real-world examples and integration patterns
- **[🎯 Demo: Article Explainer](demos/article-explainer/)** - Full-featured demo application using LangGraph and Vaquero
- **[🌐 Web Documentation](https://www.vaquero.app/docs)** - Complete API reference and guides

---

## 🔧 Installation

### From PyPI (Recommended)
```bash
pip install vaquero-sdk
```

### From Source
```bash
git clone https://github.com/nateislas/vaquero-sdk.git
cd vaquero-sdk
pip install -e .
```

### With All Dependencies
```bash
pip install vaquero-sdk[all]
```

---

## 📝 Contributing

Join our community! See [Contributing Guide](CONTRIBUTING.md)

---

<div align="center">
  <p><strong>Need help?</strong> Join our <a href="https://discord.gg/vaquero">Discord community</a> or email <a href="mailto:support@vaquero.app">support@vaquero.app</a></p>
</div>
