# 🚀 Quick Start Guide

Get up and running with Vaquero in just 5 minutes!

## 🎯 Overview

This guide will get you from zero to your first traced function in under 5 minutes. We'll cover:

- Installation
- Basic configuration
- Your first trace
- Next steps

## 1️⃣ Installation (30 seconds)

Install Vaquero using pip:

```bash
pip install vaquero-sdk
```

That's it! No complex dependencies or setup required.

## 2️⃣ Configuration (1 minute)

### Option A: Project-Scoped API Key (Recommended)

For applications that work with a single project, use a project-scoped API key:

```python
import vaquero
import os

# Set environment variables
os.environ["VAQUERO_API_KEY"] = "cf_your-project-scoped-key-here"
os.environ["VAQUERO_ENDPOINT"] = "https://api.vaquero.app"

# Initialize SDK with development mode (reads from environment variables)
vaquero.init(api_key="cf_your-project-scoped-key-here")
```

### Option B: General API Key + Project ID

For applications that need access to multiple projects:

```python
import vaquero

# Initialize SDK with production mode
vaquero.init(
    api_key="your-general-api-key-here",
    project_id="your-project-id-here",
    mode="production"  # Use production mode for optimized settings
)
```

### Advanced Configuration

For production applications, you might want to customize:

```python
from vaquero import SDKConfig

config = SDKConfig(
    api_key="your-api-key",
    project_id="your-project-id",
    endpoint="https://api.vaquero.com",
    batch_size=100,           # Batch size for efficient transmission
    flush_interval=5.0,       # Flush interval in seconds
    max_retries=3,            # Retry failed requests
    capture_inputs=False,     # Disable for production privacy
    capture_outputs=False,    # Disable for production privacy
    capture_errors=True,      # Keep error capture enabled
    environment="production",
    debug=False
)

vaquero.init(config=config)
```

## 3️⃣ Your First Trace (1 minute)

Now let's trace your first function:

```python
import vaquero

# Initialize SDK (if not done already)
vaquero.init(api_key="your-api-key", project_id="your-project-id")

# Trace a function
@vaquero.trace(agent_name="data_processor")
def process_user_data(user_id: str, data: dict) -> dict:
    """Process user data with automatic tracing."""
    # Your business logic here
    result = {
        "user_id": user_id,
        "processed_at": "2024-01-01T00:00:00Z",
        "data_size": len(str(data)),
        "status": "processed"
    }
    return result

# Use the function - it's automatically traced!
result = process_user_data("user123", {"key": "value"})
print(f"Processed: {result}")
```

**That's it!** Your function calls are now being automatically traced and sent to Vaquero.

## 4️⃣ Manual Span Creation (30 seconds)

For more detailed tracing, you can create manual spans:

```python
import vaquero

@vaquero.trace(agent_name="complex_workflow")
def complex_operation(data: dict) -> dict:
    """Complex operation with manual span control."""
    # Parent span (automatically created by @vaquero.trace)

    # Manual child span
    with vaquero.span("database_operation") as span:
        span.set_attribute("operation", "user_lookup")
        span.set_attribute("table", "users")

        # Your database logic here
        user = database.get_user(data["user_id"])
        span.set_attribute("user_found", user is not None)

    # Another child span
    with vaquero.span("api_call") as span:
        span.set_attribute("endpoint", "/external-api")
        span.set_attribute("method", "POST")

        # Your API logic here
        response = api_client.post("/external-api", data)
        span.set_attribute("status_code", response.status_code)

    return {"status": "completed"}
```

## 🚀 What's Next?

Now that you have basic tracing working, explore these areas:

### 📖 **[Common Patterns](../patterns/)**
Learn essential patterns for different use cases:
- Function tracing
- API endpoint monitoring
- Database operation tracing
- Error handling

### 🔧 **[Advanced Features](../advanced/)**
Dive deeper into power user features:
- Automatic LLM instrumentation
- Custom performance monitoring
- Workflow orchestration
- Circuit breaker patterns

### 🛠️ **[Integrations](../integrations/)**
Framework-specific guides for:
- FastAPI
- Django
- Flask
- Celery

### 📚 **[API Reference](../reference/)**
Complete reference for all configuration options and APIs.

## 🔧 Troubleshooting

### Common Issues

**"SDK not initialized" error**
```python
# Make sure to call init() before using the SDK
import vaquero
vaquero.init(api_key="your-key", project_id="your-project-id")
```

**Traces not appearing**
```python
# Check if SDK is enabled
if vaquero.get_default_sdk().config.enabled:
    print("SDK is active")
else:
    print("SDK is disabled")
```

**Performance issues**
```python
# Use development mode for lower latency, production for efficiency
config = SDKConfig(batch_size=10, flush_interval=1.0, mode="development")
vaquero.init(config=config)
```

## 💡 Pro Tips

1. **Use descriptive agent names** - they'll appear in your dashboard
2. **Add meaningful attributes** - they help with debugging and analysis
3. **Handle sensitive data carefully** - don't log passwords or API keys
4. **Use context managers for resources** - database connections, API clients, etc.

## 🎉 You're All Set!

You now have Vaquero set up and running. Your functions are being traced automatically, and you can see the results in your Vaquero dashboard.

Ready to explore more? Check out the **[Common Patterns](../patterns/)** section for practical examples!
