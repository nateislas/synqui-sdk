# ⚙️ Configuration Reference

Complete guide to configuring the Vaquero SDK for your specific needs and environment.

## 🚀 Quick Configuration

### Environment Variables (Recommended)
```bash
# Required
export VAQUERO_API_KEY="cf_your-project-scoped-key-here"

# Optional - sensible defaults provided
export VAQUERO_ENDPOINT="https://api.vaquero.app"
export VAQUERO_MODE="development"  # or "production"
export VAQUERO_BATCH_SIZE="100"
export VAQUERO_FLUSH_INTERVAL="5.0"
export VAQUERO_MAX_RETRIES="3"
```

### Programmatic Configuration
```python
import vaquero
from vaquero import SDKConfig

# Simple configuration
vaquero.init(api_key="your-api-key")

# Advanced configuration
config = SDKConfig(
    api_key="your-api-key",
    project_id="your-project-id",  # Optional for project-scoped keys
    endpoint="https://api.vaquero.app",
    mode="production",
    batch_size=100,
    flush_interval=5.0,
    max_retries=3,
    capture_inputs=True,
    capture_outputs=True,
    capture_errors=True,
    capture_tokens=True,
    auto_instrument_llm=True,
    environment="production",
    debug=False
)

vaquero.init(config=config)
```

## 📋 Configuration Options

### Core Settings

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `api_key` | `str` | **Required** | Your Vaquero API key |
| `project_id` | `str` | `None` | Project ID (required for general API keys) |
| `endpoint` | `str` | `"https://api.vaquero.app"` | Vaquero API endpoint |
| `mode` | `str` | `"development"` | Operating mode (`"development"` or `"production"`) |

### Performance Settings

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `batch_size` | `int` | `100` | Number of traces per batch |
| `flush_interval` | `float` | `5.0` | Seconds between batch flushes |
| `max_retries` | `int` | `3` | Maximum retry attempts for failed requests |
| `timeout` | `float` | `30.0` | Request timeout in seconds |

### Data Capture Settings

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `capture_inputs` | `bool` | `True` | Capture function arguments |
| `capture_outputs` | `bool` | `True` | Capture return values |
| `capture_errors` | `bool` | `True` | Capture exceptions and stack traces |
| `capture_tokens` | `bool` | `True` | Track LLM token usage and costs |
| `capture_system_prompts` | `bool` | `True` | Include LLM system prompts in traces |

### Auto-Instrumentation Settings

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `auto_instrument_llm` | `bool` | `True` | Automatically trace LLM calls |
| `auto_instrument_http` | `bool` | `False` | Automatically trace HTTP requests |
| `auto_instrument_db` | `bool` | `False` | Automatically trace database operations |

### Debug & Monitoring

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `debug` | `bool` | `False` | Enable debug logging |
| `enabled` | `bool` | `True` | Enable/disable SDK |
| `log_level` | `str` | `"INFO"` | Logging level |

## 🌍 Environment-Based Configuration

### Development Environment
```python
# Development configuration - optimized for debugging
dev_config = SDKConfig(
    api_key="dev-api-key",
    project_id="dev-project",
    mode="development",
    batch_size=10,           # Smaller batches for faster feedback
    flush_interval=2.0,      # Faster flushing for real-time monitoring
    capture_inputs=True,     # Full debugging info
    capture_outputs=True,
    capture_errors=True,
    debug=True,              # Verbose logging
    auto_instrument_llm=True # Immediate feedback on LLM calls
)
```

### Production Environment
```python
# Production configuration - optimized for performance and privacy
prod_config = SDKConfig(
    api_key="prod-api-key",
    project_id="prod-project",
    mode="production",
    batch_size=100,          # Larger batches for efficiency
    flush_interval=10.0,     # Less frequent flushing
    capture_inputs=False,    # Privacy protection
    capture_outputs=False,   # Privacy protection
    capture_errors=True,     # Keep error tracking
    capture_tokens=True,     # Track costs
    debug=False,             # Clean logs
    auto_instrument_llm=False, # Explicit control in production
    environment="production"
)
```

## 🔧 Advanced Configuration Patterns

### Multi-Environment Setup
```python
import os
from vaquero import SDKConfig

def get_config_for_environment():
    """Get configuration based on current environment."""

    env = os.getenv("ENVIRONMENT", "development")

    if env == "production":
        return SDKConfig(
            api_key=os.getenv("VAQUERO_PROD_API_KEY"),
            project_id=os.getenv("VAQUERO_PROD_PROJECT_ID"),
            mode="production",
            batch_size=200,
            flush_interval=15.0,
            capture_inputs=False,
            capture_outputs=False,
            debug=False
        )
    elif env == "staging":
        return SDKConfig(
            api_key=os.getenv("VAQUERO_STAGING_API_KEY"),
            project_id=os.getenv("VAQUERO_STAGING_PROJECT_ID"),
            mode="production",
            batch_size=50,
            flush_interval=5.0,
            capture_inputs=True,
            capture_outputs=True,
            debug=True
        )
    else:  # development
        return SDKConfig(
            api_key=os.getenv("VAQUERO_DEV_API_KEY"),
            project_id=os.getenv("VAQUERO_DEV_PROJECT_ID"),
            mode="development",
            batch_size=10,
            flush_interval=2.0,
            capture_inputs=True,
            capture_outputs=True,
            debug=True
        )

# Use the configuration
config = get_config_for_environment()
vaquero.init(config=config)
```

### Custom Configuration Class
```python
from vaquero import SDKConfig
from dataclasses import dataclass
from typing import Optional

@dataclass
class AppConfig:
    """Application-specific configuration."""

    # Vaquero settings
    vaquero_api_key: str
    vaquero_project_id: Optional[str] = None
    vaquero_mode: str = "development"

    # Application settings
    database_url: str
    redis_url: str
    log_level: str = "INFO"

    def to_vaquero_config(self) -> SDKConfig:
        """Convert to Vaquero SDK configuration."""

        # Determine batch size based on environment
        batch_size = 10 if self.vaquero_mode == "development" else 100

        return SDKConfig(
            api_key=self.vaquero_api_key,
            project_id=self.vaquero_project_id,
            mode=self.vaquero_mode,
            batch_size=batch_size,
            flush_interval=5.0,
            capture_inputs=self.vaquero_mode == "development",
            capture_outputs=self.vaquero_mode == "development",
            capture_errors=True,
            debug=self.vaquero_mode == "development",
            auto_instrument_llm=True
        )

# Usage
app_config = AppConfig(
    vaquero_api_key="your-api-key",
    vaquero_project_id="your-project-id",
    vaquero_mode="production",
    database_url="postgresql://...",
    redis_url="redis://...",
    log_level="WARNING"
)

vaquero.init(config=app_config.to_vaquero_config())
```

## 🔒 Security Considerations

### API Key Management
```python
# ✅ Good: Environment variables
import os
vaquero.init(api_key=os.getenv("VAQUERO_API_KEY"))

# ❌ Bad: Hardcoded keys
vaquero.init(api_key="cf_hardcoded_key_123")  # Security risk!

# ✅ Good: Key rotation
import vaquero

# Check if key needs rotation
sdk = vaquero.get_default_sdk()
if sdk.should_rotate_key():
    new_key = get_new_api_key()
    vaquero.init(api_key=new_key)
```

### Privacy Protection
```python
# Production configuration with privacy protection
config = SDKConfig(
    api_key="prod-api-key",
    mode="production",

    # Privacy-first settings
    capture_inputs=False,     # Don't capture function arguments
    capture_outputs=False,    # Don't capture return values
    capture_system_prompts=False,  # Don't capture LLM prompts

    # But keep essential tracking
    capture_errors=True,      # Track errors for debugging
    capture_tokens=True,      # Track costs for billing
    capture_performance=True  # Track timing for optimization
)
```

## 📊 Monitoring Configuration

### SDK Health Monitoring
```python
import vaquero

# Initialize SDK
vaquero.init(api_key="your-api-key")

# Monitor SDK health
sdk = vaquero.get_default_sdk()
stats = sdk.get_stats()

print(f"SDK Status: {'Active' if stats.get('enabled') else 'Disabled'}")
print(f"Traces Sent: {stats.get('traces_sent', 0)}")
print(f"Queue Size: {stats.get('queue_size', 0)}")
print(f"Memory Usage: {stats.get('memory_usage_mb', 0)} MB")
print(f"Error Count: {stats.get('errors', 0)}")

# Health check endpoint for monitoring systems
@app.get("/health/vaquero")
def vaquero_health():
    sdk = vaquero.get_default_sdk()
    stats = sdk.get_stats()

    return {
        "status": "healthy" if stats.get("enabled") and stats.get("errors", 0) < 10 else "unhealthy",
        "stats": stats,
        "timestamp": time.time()
    }
```

### Performance Tuning
```python
# Monitor and adjust performance based on usage patterns
def tune_vaquero_performance():
    """Dynamically tune SDK performance based on current usage."""

    sdk = vaquero.get_default_sdk()
    stats = sdk.get_stats()

    # Adjust batch size based on queue depth
    queue_size = stats.get('queue_size', 0)
    if queue_size > 500:
        # Increase batch size to reduce memory usage
        vaquero.init(api_key="your-key", batch_size=200)
    elif queue_size < 10:
        # Decrease batch size for faster feedback
        vaquero.init(api_key="your-key", batch_size=50)

    # Adjust flush interval based on error rate
    error_rate = stats.get('errors', 0) / max(stats.get('traces_sent', 1), 1)
    if error_rate > 0.1:
        # Increase flush interval to reduce server load
        vaquero.init(api_key="your-key", flush_interval=15.0)
```

## 🚨 Troubleshooting Configuration Issues

### Common Configuration Problems

#### 1. "SDK not initialized" Error
```python
# ✅ Correct
import vaquero
vaquero.init(api_key="your-key")  # Initialize first

@vaquero.trace("my_function")
def my_function():
    return "Hello"

# ❌ Incorrect
@vaquero.trace("my_function")  # Error: SDK not initialized
def my_function():
    return "Hello"

import vaquero
vaquero.init(api_key="your-key")  # Too late!
```

#### 2. Environment Variables Not Working
```bash
# ✅ Correct
export VAQUERO_API_KEY="your-key"
python your_script.py

# ❌ Incorrect
VAQUERO_API_KEY="your-key" python your_script.py  # Not exported

# ✅ Correct (alternative)
VAQUERO_API_KEY="your-key" python -c "import os; print(os.environ.get('VAQUERO_API_KEY'))"
```

#### 3. API Key Format Issues
```python
# ✅ Correct - Project-scoped key
vaquero.init(api_key="cf_PfnOhuv9UPLYpU_9o1gr6s1q27JNv7lbFspUR_aoFAM")

# ✅ Correct - General API key + project ID
vaquero.init(
    api_key="cf_l5-XPrTnnqk4H42pbchNrdcR5KvGUrpMH3tG6bgw6GE",
    project_id="your-project-id"
)

# ❌ Incorrect - Wrong format
vaquero.init(api_key="sk-1234567890abcdef")  # Wrong prefix
vaquero.init(api_key="your-key")  # Too generic
```

## ✅ Verification

### Test Your Configuration
```python
import vaquero

# Initialize with your configuration
vaquero.init(api_key="your-api-key", mode="development")

# Test basic functionality
@vaquero.trace("test_function")
def test_function():
    return {"status": "success", "timestamp": time.time()}

result = test_function()

# Verify SDK is working
sdk = vaquero.get_default_sdk()
stats = sdk.get_stats()

assert stats.get("enabled") == True
assert stats.get("traces_sent", 0) > 0

print("✅ Configuration verified successfully!")
```

### Debug Configuration Issues
```python
import vaquero
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# Initialize SDK
vaquero.init(api_key="your-api-key", debug=True)

# Check detailed status
sdk = vaquero.get_default_sdk()
config = sdk.config

print(f"API Key configured: {'*' * (len(config.api_key) - 8) + config.api_key[-4:] if config.api_key else 'None'}")
print(f"Endpoint: {config.endpoint}")
print(f"Mode: {config.mode}")
print(f"Batch size: {config.batch_size}")
print(f"Debug enabled: {config.debug}")
```

## 🎯 Next Steps

- **[→ API Reference](./api-reference.md)** - Complete API documentation
- **[→ Integration Guides](./integrations.md)** - Framework-specific setup
- **[→ Production Deployment](../advanced-usage/production-deployment.md)** - Production best practices

## 🆘 Need Help?

- **Examples**: [Configuration Examples](../examples/)
- **Community**: [Discord](https://discord.gg/vaquero)
- **Support**: support@vaquero.app

---

**[← Back to SDK Reference](../index.md#sdk-reference)** | **[→ Next: API Reference](./api-reference.md)**
