# 📚 API Reference

Complete reference for all Vaquero SDK functions, classes, and configuration options.

## 🚀 Core Functions

### `vaquero.init()`

Initialize the Vaquero SDK.

```python
def init(
    api_key: str | None = None,
    project_id: str | None = None,
    endpoint: str | None = None,
    mode: str | None = None,
    config: SDKConfig | None = None,
    **kwargs
) -> None
```

**Parameters:**
- `api_key` (str): Your Vaquero API key
- `project_id` (str, optional): Project ID for general API keys
- `endpoint` (str, optional): Custom API endpoint
- `mode` (str, optional): Operating mode ("development" or "production")
- `config` (SDKConfig, optional): Complete configuration object
- `**kwargs`: Additional configuration options

**Examples:**
```python
# Simple initialization
vaquero.init(api_key="cf_your-key-here")

# With project ID
vaquero.init(
    api_key="cf_general-key-here",
    project_id="your-project-id"
)

# With environment variables
import os
os.environ["VAQUERO_API_KEY"] = "cf_your-key-here"
vaquero.init()  # Uses environment variable

# Advanced configuration
from vaquero import SDKConfig
config = SDKConfig(
    api_key="your-key",
    batch_size=50,
    debug=True
)
vaquero.init(config=config)
```

### `vaquero.trace()`

Decorator for tracing function execution.

```python
def trace(
    agent_name: str,
    tags: dict[str, str] | None = None,
    capture_inputs: bool | None = None,
    capture_outputs: bool | None = None,
    capture_errors: bool | None = None
) -> Callable
```

**Parameters:**
- `agent_name` (str): Name for this traced operation
- `tags` (dict, optional): Key-value pairs for categorization
- `capture_inputs` (bool, optional): Override global input capture setting
- `capture_outputs` (bool, optional): Override global output capture setting
- `capture_errors` (bool, optional): Override global error capture setting

**Examples:**
```python
@vaquero.trace("data_processor")
def process_data(data: dict) -> dict:
    return {"result": data}

@vaquero.trace(
    "ml_model",
    tags={"model": "v2", "team": "research"}
)
def run_inference(features: list) -> float:
    return 0.85

@vaquero.trace(
    "api_client",
    capture_inputs=False,  # Don't capture sensitive data
    capture_outputs=True   # But do capture responses
)
async def call_external_api(data: dict) -> dict:
    return {"status": "success"}
```

### `vaquero.span()`

Context manager for manual span creation.

```python
def span(
    name: str,
    attributes: dict[str, Any] | None = None,
    tags: dict[str, str] | None = None
) -> SpanContext
```

**Parameters:**
- `name` (str): Name for this span
- `attributes` (dict, optional): Key-value pairs to set immediately
- `tags` (dict, optional): Tags for categorization

**Examples:**
```python
# Sync usage
with vaquero.span("database_query") as span:
    span.set_attribute("table", "users")
    span.set_attribute("query_type", "select")
    result = db.execute_query("SELECT * FROM users")

# Async usage
async with vaquero.span("api_call") as span:
    span.set_attribute("endpoint", "/api/users")
    span.set_attribute("method", "POST")
    response = await api_client.post("/api/users", data)

# Nested spans
with vaquero.span("user_registration") as parent_span:
    parent_span.set_attribute("user_id", "123")

    with vaquero.span("validate_email") as child_span:
        child_span.set_attribute("email", "user@example.com")
        is_valid = validate_email("user@example.com")

    with vaquero.span("create_user") as child_span:
        child_span.set_attribute("source", "api")
        user = create_user({"email": "user@example.com"})
```

## 🏗️ Classes

### `SDKConfig`

Configuration class for the Vaquero SDK.

```python
@dataclass
class SDKConfig:
    api_key: str
    project_id: str | None = None
    endpoint: str = "https://api.vaquero.app"
    mode: str = "development"
    batch_size: int = 100
    flush_interval: float = 5.0
    max_retries: int = 3
    capture_inputs: bool = True
    capture_outputs: bool = True
    capture_errors: bool = True
    capture_tokens: bool = True
    capture_system_prompts: bool = True
    auto_instrument_llm: bool = True
    auto_instrument_http: bool = False
    auto_instrument_db: bool = False
    debug: bool = False
    enabled: bool = True
    log_level: str = "INFO"
```

**Usage:**
```python
from vaquero import SDKConfig

config = SDKConfig(
    api_key="your-key",
    mode="production",
    batch_size=200,
    capture_inputs=False,  # Privacy protection
    debug=False
)

vaquero.init(config=config)
```

### `VaqueroSDK`

Main SDK class (advanced usage).

```python
class VaqueroSDK:
    def __init__(self, config: SDKConfig)

    def trace(self, agent_name: str, **kwargs) -> Callable
    def span(self, name: str, **kwargs) -> SpanContext
    def flush(self) -> None
    def shutdown(self) -> None
    def get_stats(self) -> dict
    def is_enabled(self) -> bool
```

**Advanced Usage:**
```python
from vaquero import VaqueroSDK, SDKConfig

# Create custom SDK instance
config = SDKConfig(api_key="your-key", mode="production")
sdk = VaqueroSDK(config)

# Use custom instance
@sdk.trace("custom_agent")
def my_function():
    return "Hello"

# Manual control
sdk.flush()  # Force send traces
stats = sdk.get_stats()  # Get metrics
```

## 🔧 Utility Functions

### `vaquero.get_default_sdk()`

Get the global SDK instance.

```python
def get_default_sdk() -> VaqueroSDK
```

**Example:**
```python
import vaquero

vaquero.init(api_key="your-key")
sdk = vaquero.get_default_sdk()

# Check status
stats = sdk.get_stats()
print(f"Traces sent: {stats.get('traces_sent', 0)}")

# Manual control
vaquero.flush()  # Send pending traces
```

### `vaquero.flush()`

Force send all pending traces.

```python
def flush() -> None
```

**Example:**
```python
import vaquero

vaquero.init(api_key="your-key")

@vaquero.trace("my_function")
def my_function():
    return "Hello"

# Force immediate sending (useful for testing)
vaquero.flush()
```

### `vaquero.shutdown()`

Clean shutdown of the SDK.

```python
def shutdown() -> None
```

**Example:**
```python
import vaquero

vaquero.init(api_key="your-key")

# ... your code ...

# Clean shutdown before exit
vaquero.shutdown()
```

## 🌐 HTTP Client Integration

### Automatic HTTP Request Tracing

Enable automatic tracing of HTTP requests:

```python
import vaquero

# Enable HTTP auto-instrumentation
vaquero.init(
    api_key="your-key",
    auto_instrument_http=True
)

# All HTTP requests are now automatically traced
import requests

response = requests.get("https://api.example.com/users")
# This request is automatically traced with:
# - URL, method, status code
# - Request/response headers (sanitized)
# - Response time
# - Error handling
```

## 🗄️ Database Integration

### Automatic Database Query Tracing

Enable automatic tracing of database operations:

```python
import vaquero

# Enable database auto-instrumentation
vaquero.init(
    api_key="your-key",
    auto_instrument_db=True
)

# Database operations are automatically traced
import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

# This query is automatically traced
cursor.execute("SELECT * FROM users WHERE active = ?", (True,))
results = cursor.fetchall()
```

## 🔄 Error Handling

### Exception Propagation

The SDK never swallows exceptions:

```python
import vaquero

@vaquero.trace("risky_operation")
def risky_function():
    if some_condition:
        raise ValueError("Something went wrong")
    return "success"

try:
    result = risky_function()
except ValueError as e:
    # Exception propagates normally
    # But is also captured in the trace
    print(f"Error: {e}")
    # The trace will show:
    # - Exception type and message
    # - Stack trace
    # - Function arguments
    # - Local variables at time of error
```

### Custom Error Handling

```python
@vaquero.trace("api_call")
def call_external_service():
    try:
        response = requests.get("https://api.example.com/data")
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        # Log additional context
        with vaquero.span("error_context") as span:
            span.set_attribute("error_type", type(e).__name__)
            span.set_attribute("url", "https://api.example.com/data")
            span.set_attribute("status_code", getattr(e.response, 'status_code', None))

        raise
```

## 📊 Performance Monitoring

### SDK Statistics

```python
import vaquero

vaquero.init(api_key="your-key")

# Get comprehensive SDK statistics
stats = vaquero.get_default_sdk().get_stats()

print(f"Enabled: {stats.get('enabled', False)}")
print(f"Traces sent: {stats.get('traces_sent', 0)}")
print(f"Queue size: {stats.get('queue_size', 0)}")
print(f"Memory usage: {stats.get('memory_usage_mb', 0)} MB")
print(f"Errors: {stats.get('errors', 0)}")
print(f"Last flush: {stats.get('last_flush_time', 'Never')}")
```

### Performance Tuning

```python
# Monitor and adjust based on performance
def optimize_vaquero_settings():
    sdk = vaquero.get_default_sdk()
    stats = sdk.get_stats()

    # Adjust batch size based on queue depth
    if stats.get('queue_size', 0) > 1000:
        # Large queue - increase batch size
        vaquero.init(api_key="your-key", batch_size=200)
    elif stats.get('queue_size', 0) < 10:
        # Small queue - decrease batch size for responsiveness
        vaquero.init(api_key="your-key", batch_size=50)

    # Adjust flush interval based on error rate
    error_rate = stats.get('errors', 0) / max(stats.get('traces_sent', 1), 1)
    if error_rate > 0.05:  # 5% error rate
        vaquero.init(api_key="your-key", flush_interval=15.0)
```

## 🔍 Debugging

### Debug Mode

```python
import vaquero
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# Initialize with debug enabled
vaquero.init(api_key="your-key", debug=True)

# Now you'll see detailed SDK logs:
# DEBUG:vaquero:Initializing SDK with config...
# DEBUG:vaquero:Batch processor started
# DEBUG:vaquero:Trace sent successfully
```

### Trace Inspection

```python
# Inspect traces before they're sent
@vaquero.trace("debug_function")
def debug_function():
    # Access current span for debugging
    from vaquero import get_current_span

    current_span = get_current_span()
    if current_span:
        print(f"Current span: {current_span.name}")
        print(f"Trace ID: {current_span.trace_id}")

    return "debug result"
```

## 🎯 Best Practices

### Performance Optimization
```python
# ✅ Good: Appropriate batch sizes
vaquero.init(batch_size=100)  # Balanced for most use cases

# ✅ Good: Environment-specific configuration
if os.getenv("ENVIRONMENT") == "production":
    vaquero.init(batch_size=200, flush_interval=10.0)
else:
    vaquero.init(batch_size=10, flush_interval=2.0, debug=True)
```

### Error Handling
```python
# ✅ Good: Comprehensive error capture
@vaquero.trace("robust_function")
def robust_function():
    try:
        risky_operation()
    except Exception as e:
        # Additional error context
        with vaquero.span("error_recovery") as span:
            span.set_attribute("recovery_attempted", True)
            span.set_attribute("error_type", type(e).__name__)
        raise
```

### Resource Management
```python
# ✅ Good: Proper cleanup
import vaquero

vaquero.init(api_key="your-key")

try:
    # Your application code
    pass
finally:
    # Clean shutdown
    vaquero.shutdown()
```

## 🚨 Common Issues

### "SDK not initialized" Error
```python
# ❌ Wrong
@vaquero.trace("my_function")
def my_function():
    return "Hello"

import vaquero  # Too late!
vaquero.init(api_key="your-key")

# ✅ Correct
import vaquero
vaquero.init(api_key="your-key")  # Initialize first

@vaquero.trace("my_function")
def my_function():
    return "Hello"
```

### Performance Issues
```python
# ❌ Bad: Too frequent flushing
vaquero.init(flush_interval=0.1)  # Creates too much overhead

# ✅ Good: Balanced settings
vaquero.init(flush_interval=5.0)  # Good balance of latency vs efficiency
```

## ✅ Verification

### Test SDK Functionality
```python
import vaquero

def test_sdk():
    # Initialize
    vaquero.init(api_key="your-test-key")

    # Test tracing
    @vaquero.trace("test_agent")
    def test_function():
        return {"status": "success"}

    # Call function
    result = test_function()

    # Verify SDK is working
    sdk = vaquero.get_default_sdk()
    stats = sdk.get_stats()

    assert stats.get("enabled") == True
    assert stats.get("traces_sent", 0) > 0

    print("✅ SDK verification passed!")

if __name__ == "__main__":
    test_sdk()
```

## 🎯 Next Steps

- **[← Configuration Guide](./configuration.md)** - Complete setup guide
- **[→ Integration Guides](./integrations.md)** - Framework-specific setup
- **[→ Examples](../examples/)** - Practical usage patterns

## 🆘 Need Help?

- **Examples**: [Complete Examples](../examples/)
- **Community**: [Discord](https://discord.gg/vaquero)
- **Support**: support@vaquero.app

---

**[← Back to SDK Reference](../index.md#sdk-reference)** | **[→ Next: Integration Guides](./integrations.md)**
