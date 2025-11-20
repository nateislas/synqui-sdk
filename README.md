# 🚀 Vaquero Python SDK

<div align="center">
  <h3>Comprehensive observability and tracing for AI agents and applications</h3>
  <p><strong>Zero-config tracing</strong> • <strong>Auto-instrumentation</strong> • <strong>Production-ready</strong></p>

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

### 2. Configure
```python
import vaquero

vaquero.init(api_key="your-api-key")
```

### 3. Trace
```python
@vaquero.trace("my_agent")
def process_data(data):
    return {"result": data}

# Done! ✨
```

---

## 🎯 Key Features

| Feature | Description |
|---------|-------------|
| 🔍 **Automatic Tracing** | One decorator instruments your entire function with comprehensive observability |
| 🤖 **LLM Auto-Instrumentation** | Automatically captures OpenAI, Anthropic, and other LLM calls with zero code changes |
| ⚡ **Async-First** | Full support for async/await patterns with intelligent batching |
| 📊 **Performance Monitoring** | Built-in profiling, memory tracking, and performance insights |
| 🛡️ **Production Ready** | Circuit breakers, retry logic, and enterprise-grade reliability |
| 🎛️ **Zero Configuration** | Environment variables and sensible defaults get you started instantly |

---

## 📚 Resources

- **[💡 Examples](examples/)** - Real-world examples and integration patterns
- **[🎯 Demo: Article Explainer](demos/article-explainer/)** - Full-featured demo application using LangGraph and Vaquero

---

## 🔧 Installation Options

### 🛠️ From PyPI (Recommended)
```bash
pip install vaquero-sdk
```

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

### Basic Function Tracing
```python
import vaquero

# Configure once
vaquero.init(api_key="your-key")

@vaquero.trace("data_processor")
def process_data(data):
    """Process some data."""
    result = {"processed": len(data), "items": data}
    return result

# Your function is now automatically traced!
result = process_data(["item1", "item2", "item3"])
```

### Async Support
```python
@vaquero.trace("api_client")
async def fetch_data(url):
    """Async data fetching."""
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.json()

# Works seamlessly with async/await
result = await fetch_data("https://api.example.com/data")
```

### Manual Span Creation
```python
async with vaquero.span("complex_operation") as span:
    span.set_attribute("operation_type", "batch_processing")
    span.set_attribute("batch_size", len(data))

    # Your complex logic here
    result = await process_batch(data)

    span.set_attribute("result_count", len(result))
```

### Auto-Instrumentation (Zero Code Changes!)
```python
# Enable LLM auto-instrumentation
vaquero.init(api_key="your-key", auto_instrument_llm=True)

# Now any LLM calls are automatically traced!
import openai

client = openai.OpenAI(api_key="your-key")
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Hello!"}]
)
# System prompts, tokens, timing all captured automatically! ✨
```

---

## 🎨 Advanced Usage

### Manual Span Creation

**Sync & Async Support**
```python
# Same API works for both sync and async!
with vaquero.span("custom_operation") as span:
    span.set_attribute("user_id", "12345")
    result = expensive_computation()
    span.set_attribute("result_size", len(result))

async with vaquero.span("async_operation") as span:
    span.set_attribute("operation_type", "ml_inference")
    result = await ml_model.predict(data)
    span.set_attribute("confidence", result.confidence)
```

### Nested Tracing

**Parent-Child Relationships**
```python
@vaquero.trace("main_processor")
def main_process(data):
    # Parent span automatically created
    preprocessed = preprocess_data(data)

    # Child span with context
    with vaquero.span("validation") as span:
        span.set_attribute("data_size", len(preprocessed))
        validate_data(preprocessed)

    return postprocess_data(preprocessed)
```

### Custom Configuration

**Advanced Setup**
```python
from vaquero import SDKConfig

config = SDKConfig(
    api_key="your-api-key",
    project_id="your-project-id",  # Optional - auto-provisioned
    batch_size=100,        # Optimize for your workload
    flush_interval=5.0,    # Balance latency vs efficiency
    max_retries=3,         # Handle transient failures
    capture_inputs=True,   # Privacy vs debugging
    tags={"team": "ml", "env": "prod"}  # Global metadata
)

vaquero.init(config=config)
```

### Environment Variables

**Configuration via Environment**
```bash
VAQUERO_API_KEY=your-key
VAQUERO_PROJECT_ID=your-project
VAQUERO_ENDPOINT=https://api.vaquero.com
VAQUERO_BATCH_SIZE=50
VAQUERO_AUTO_INSTRUMENT_LLM=true
```

```python
import vaquero
vaquero.init()  # Loads from env vars
```

### Error Handling & Resilience

**Automatic Error Capture**
```python
@vaquero.trace("risky_operation")
def risky_operation(data):
    if not data:
        raise ValueError("Data cannot be empty")
    return process(data)

try:
    result = risky_operation([])
except ValueError as e:
    # Error automatically captured with full context
    print(f"Operation failed: {e}")
    # Stack trace, function args, timing all preserved
```

### Performance Monitoring

**Built-in Observability**
```python
# Check SDK health
stats = vaquero.get_default_sdk().get_stats()
print(f"Traces: {stats['traces_sent']}")
print(f"Memory: {stats['memory_usage_mb']} MB")

# Manual control
vaquero.flush()  # Force send pending traces

# Get current context
from vaquero import get_current_span
span = get_current_span()
span.set_attribute("custom_metric", value)
```

---

## 🔧 Configuration Reference

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `api_key` | string | Required | Your Vaquero API key |
| `project_id` | string | Optional | Your project identifier (auto-provisioned) |
| `batch_size` | int | 100 | Traces per batch |
| `flush_interval` | float | 5.0 | Seconds between flushes |
| `auto_instrument_llm` | bool | true | Auto-capture LLM calls |
| `capture_system_prompts` | bool | true | Capture LLM system prompts |
| `capture_code` | bool | true | Capture source code for analysis |
| `mode` | string | "development" | Operating mode ("development" or "production") |

---

## 🚨 Best Practices

### ✅ Do
- **Use descriptive agent names** - `@vaquero.trace("user_authentication_validator")`
- **Add meaningful attributes** - `span.set_attribute("user_id", user_id)`
- **Handle errors gracefully** - SDK captures exceptions automatically
- **Use async context managers** - `async with vaquero.span("operation"):`

### ❌ Avoid
- **Generic names** - `@vaquero.trace("validator")` (too vague)
- **Sensitive data** - Don't log passwords, keys, or PII
- **Blocking operations** - Use async patterns for I/O
- **Manual timing** - SDK handles timing automatically

---

## 🛠️ Development

### 🏗️ Setup
```bash
git clone https://github.com/nateislas/vaquero-sdk.git
cd vaquero-sdk
pip install -e ".[dev]"
```

### 🧪 Testing
```bash
make test          # Run all tests
make test-cov      # With coverage
make lint          # Code quality
```

### 📝 Contributing
Join our community! Contributions are welcome. Please open an issue or submit a pull request.

---


---

<div align="center">
  <p><strong>Need help?</strong> Join our <a href="https://discord.gg/vaquero">Discord community</a> or email <a href="mailto:support@vaquero.app">support@vaquero.app</a></p>
</div>
