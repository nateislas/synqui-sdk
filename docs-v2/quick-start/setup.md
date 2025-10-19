# 🚀 Installation & Setup

Get up and running with Vaquero in under 5 minutes.

## 📦 Installation

### Option 1: PyPI (Recommended)
```bash
pip install vaquero-sdk
```

### Option 2: From Source
```bash
git clone https://github.com/vaquero/vaquero-python.git
cd vaquero-python
pip install -e .
```

### Option 3: With All Dependencies
```bash
pip install vaquero-sdk[all]  # Includes optional integrations
```

## ⚙️ Configuration

### Step 1: Get Your API Key

1. **Sign up** at [https://app.vaquero.com](https://app.vaquero.com)
2. **Create a project** (or join an existing one)
3. **Copy your project-scoped API key** (starts with `cf_`)

### Step 2: Initialize the SDK

#### Option A: Project-Scoped Key (Recommended)
```python
import vaquero

# Simple initialization (recommended)
vaquero.init(api_key="cf_your-project-scoped-key-here")

# Or set environment variable
import os
os.environ["VAQUERO_API_KEY"] = "cf_your-project-scoped-key-here"
vaquero.init()  # Uses environment variable
```

#### Option B: General API Key + Project ID
```python
import vaquero

vaquero.init(
    api_key="your-general-api-key-here",
    project_id="your-project-id-here"
)
```

### Step 3: Verify Installation

```python
import vaquero

# Check if SDK is ready
if vaquero.get_default_sdk().config.enabled:
    print("✅ Vaquero SDK is ready!")
else:
    print("❌ SDK configuration issue")
```

## 🌍 Environment Variables

Configure via environment variables for easy deployment:

```bash
# Required
export VAQUERO_API_KEY="cf_your-project-scoped-key-here"

# Optional
export VAQUERO_ENDPOINT="https://api.vaquero.app"
export VAQUERO_MODE="development"  # or "production"
export VAQUERO_BATCH_SIZE="100"
export VAQUERO_FLUSH_INTERVAL="5.0"
```

## 🔧 Configuration Options

### Basic Configuration
```python
from vaquero import SDKConfig

config = SDKConfig(
    api_key="your-api-key",
    project_id="your-project-id",  # Optional for project-scoped keys
    endpoint="https://api.vaquero.app",
    mode="development"  # or "production"
)

vaquero.init(config=config)
```

### Advanced Configuration
```python
config = SDKConfig(
    api_key="your-api-key",
    project_id="your-project-id",
    batch_size=100,           # Traces per batch
    flush_interval=5.0,       # Seconds between flushes
    max_retries=3,           # Network retry attempts
    capture_inputs=True,     # Include function arguments
    capture_outputs=True,    # Include return values
    capture_errors=True,     # Include exceptions
    capture_tokens=True,     # Track LLM token usage
    environment="production",
    debug=False,             # Disable in production
    auto_instrument_llm=True # Auto-trace LLM calls
)

vaquero.init(config=config)
```

## 🚨 Common Issues

### "SDK not initialized" Error
```python
# Make sure to call init() before using the SDK
import vaquero
vaquero.init(api_key="your-key")  # ← Don't forget this!

@vaquero.trace("my_function")
def my_function():
    return "Hello, World!"
```

### Environment Variables Not Working
```bash
# Make sure to export, not just set
export VAQUERO_API_KEY="your-key"  # ✅ Correct
VAQUERO_API_KEY="your-key"         # ❌ Wrong

# Restart your Python process after setting env vars
```

### API Key Issues
```python
# Check your API key format
# Project-scoped: cf_PfnOhuv9UPLYpU_9o1gr6s1q27JNv7lbFspUR_aoFAM
# General: cf_l5-XPrTnnqk4H42pbchNrdcR5KvGUrpMH3tG6bgw6GE

# Verify key is valid
import vaquero
vaquero.init(api_key="your-key")
```

## ✅ Verification

### Test Your Setup
```python
import vaquero

# Initialize SDK
vaquero.init(api_key="your-api-key")

# Create a test trace
@vaquero.trace("test_function")
def test_function():
    return "Hello, Vaquero!"

# Call the function
result = test_function()
print(f"Result: {result}")

# Check SDK status
sdk = vaquero.get_default_sdk()
stats = sdk.get_stats()
print(f"Traces sent: {stats.get('traces_sent', 0)}")
```

### Check Dashboard
1. Go to [https://app.vaquero.com](https://app.vaquero.com)
2. Look for your test trace in the trace explorer
3. Verify the trace details and metadata

## 🎯 Next Steps

Now that you have Vaquero set up:

1. **[→ Add your first trace](./first-trace.md)** - Start instrumenting your code
2. **[→ Access the dashboard](./dashboard-access.md)** - Explore your trace data
3. **[→ Integrate with LangChain](../agent-frameworks/langchain-integration.md)** - For AI agent workflows

## 🆘 Need Help?

- **Documentation**: [Complete SDK Reference](../sdk-reference/)
- **Community**: [Discord](https://discord.gg/vaquero)
- **Support**: support@vaquero.app

---

**[← Back to Overview](../index.md)** | **[→ Next: First Trace](./first-trace.md)**
