# 🎯 Your First Trace

Now that you have Vaquero installed and configured, let's add tracing to your code. This is where the magic happens!

## 📝 Basic Function Tracing

### Simple Decorator Pattern
```python
import vaquero

# Initialize SDK (if not already done)
vaquero.init(api_key="your-api-key")

@vaquero.trace("data_processor")
def process_user_data(user_id: str, data: dict) -> dict:
    """Process user data with automatic tracing."""
    # Your business logic here
    result = {
        "user_id": user_id,
        "processed": True,
        "items_count": len(data.get("items", [])),
        "timestamp": "2024-01-01T00:00:00Z"
    }
    return result

# Call your function - it's automatically traced!
result = process_user_data("user123", {"items": ["item1", "item2"]})
```

### Async Function Support
```python
import asyncio
import vaquero

@vaquero.trace("api_client")
async def fetch_user_profile(user_id: str) -> dict:
    """Fetch user profile from external API."""
    # Simulate API call
    await asyncio.sleep(0.1)

    return {
        "user_id": user_id,
        "name": "John Doe",
        "email": "john@example.com",
        "preferences": {"theme": "dark", "notifications": True}
    }

# Works seamlessly with async/await
async def main():
    profile = await fetch_user_profile("user123")
    return profile

result = asyncio.run(main())
```

## 🔍 Manual Span Creation

For more detailed tracing of complex operations:

```python
import vaquero

@vaquero.trace("complex_workflow")
async def process_order(order_data: dict) -> dict:
    """Process an order with multiple steps."""

    # Step 1: Validate order
    async with vaquero.span("validate_order") as span:
        span.set_attribute("order_id", order_data["id"])
        span.set_attribute("user_id", order_data["user_id"])

        # Validation logic
        if not order_data.get("items"):
            raise ValueError("Order must contain items")

    # Step 2: Process payment
    async with vaquero.span("process_payment") as span:
        span.set_attribute("amount", order_data["total"])
        span.set_attribute("currency", order_data["currency"])

        # Payment processing logic
        payment_result = {"status": "success", "transaction_id": "txn_123"}

    # Step 3: Update inventory
    async with vaquero.span("update_inventory") as span:
        span.set_attribute("item_count", len(order_data["items"]))

        # Inventory update logic
        inventory_result = {"updated": True, "items_affected": 3}

    return {
        "order_id": order_data["id"],
        "status": "completed",
        "steps": ["validated", "paid", "inventory_updated"]
    }
```

## 🏷️ Adding Context and Metadata

Make your traces more informative:

```python
@vaquero.trace(
    agent_name="user_registration",
    tags={
        "team": "user_growth",
        "feature": "registration_flow",
        "version": "2.0"
    }
)
def register_user(email: str, name: str) -> dict:
    """Register a new user with detailed context."""

    with vaquero.span("validate_email") as span:
        span.set_attribute("email_domain", email.split("@")[1])
        span.set_attribute("email_length", len(email))

        # Email validation logic
        if "@" not in email:
            raise ValueError("Invalid email format")

    return {
        "user_id": "user_123",
        "email": email,
        "name": name,
        "registration_date": "2024-01-01T00:00:00Z"
    }
```

## 🛠️ Error Handling

Errors are automatically captured with full context:

```python
@vaquero.trace("risky_operation")
def risky_data_processing(data: dict) -> dict:
    """Process data that might fail."""

    try:
        # This might fail
        if data.get("should_fail"):
            raise ValueError("Simulated processing error")

        return {"status": "success", "processed": True}

    except Exception as e:
        # Error automatically captured with:
        # - Stack trace
        # - Function arguments
        # - Local variables
        # - Timing information
        raise
```

## 📊 Batch Processing

Trace batch operations efficiently:

```python
@vaquero.trace("batch_processor")
def process_user_batch(users: list[dict]) -> list[dict]:
    """Process a batch of users."""

    results = []

    for i, user in enumerate(users):
        # Create individual spans for each item
        with vaquero.span(f"process_user_{i}") as span:
            span.set_attribute("user_id", user["id"])
            span.set_attribute("batch_index", i)
            span.set_attribute("total_users", len(users))

            # Process individual user
            result = {
                "user_id": user["id"],
                "processed": True,
                "processing_time": 0.1
            }
            results.append(result)

    return results

# Process a batch
users = [
    {"id": "user1", "name": "Alice"},
    {"id": "user2", "name": "Bob"},
    {"id": "user3", "name": "Charlie"}
]

results = process_user_batch(users)
```

## 🔧 Custom Attributes

Add domain-specific information to your traces:

```python
@vaquero.trace("ml_model")
def run_ml_inference(features: list[float], model_version: str) -> dict:
    """Run ML model inference with detailed tracking."""

    with vaquero.span("model_inference") as span:
        # Model-specific attributes
        span.set_attribute("model_version", model_version)
        span.set_attribute("feature_count", len(features))
        span.set_attribute("model_type", "neural_network")

        # Performance attributes
        span.set_attribute("batch_size", 1)
        span.set_attribute("inference_time_ms", 150)

        # Business attributes
        span.set_attribute("use_case", "fraud_detection")
        span.set_attribute("confidence_threshold", 0.8)

        # Simulate inference
        prediction = 0.85
        confidence = 0.92

        return {
            "prediction": prediction,
            "confidence": confidence,
            "model_version": model_version
        }
```

## ✅ Verification

### Check Your Traces
```python
import vaquero

# Initialize SDK
vaquero.init(api_key="your-api-key")

# Run a traced function
@vaquero.trace("demo_function")
def demo_function():
    return "Hello, Vaquero!"

result = demo_function()

# Check SDK stats
sdk = vaquero.get_default_sdk()
stats = sdk.get_stats()
print(f"Traces sent: {stats.get('traces_sent', 0)}")
print(f"Queue size: {stats.get('queue_size', 0)}")
```

### View in Dashboard
1. Go to [https://www.vaquero.app](https://www.vaquero.app)
2. Navigate to **Trace Explorer**
3. Look for your `demo_function` trace
4. Click to see details, timing, and metadata

## 🎯 Best Practices

### ✅ Do
- **Use descriptive agent names**: `@vaquero.trace("user_registration_validator")`
- **Add meaningful attributes**: `span.set_attribute("user_id", user_id)`
- **Handle errors gracefully**: SDK captures exceptions automatically
- **Use async context managers**: `async with vaquero.span("operation"):`

### ❌ Avoid
- **Generic names**: `@vaquero.trace("validator")` (too vague)
- **Sensitive data**: Don't log passwords, keys, or PII
- **Blocking operations**: Use async patterns for I/O
- **Manual timing**: SDK handles timing automatically

## 🚨 Troubleshooting

### Traces Not Appearing
```python
# Check if SDK is enabled
sdk = vaquero.get_default_sdk()
if not sdk.config.enabled:
    print("SDK is disabled - check configuration")

# Manually flush pending traces
vaquero.flush()

# Check network connectivity
import requests
try:
    response = requests.get("https://api.vaquero.app/health", timeout=5)
    print("API endpoint is reachable")
except:
    print("Network connectivity issue")
```

### Performance Issues
```python
# Monitor SDK performance
stats = vaquero.get_default_sdk().get_stats()
print(f"Memory usage: {stats.get('memory_usage_mb', 0)} MB")

# Adjust batch size if needed
vaquero.init(api_key="your-key", batch_size=50)  # Smaller batches
```

## 🎯 Next Steps

Now that you can trace your functions:

1. **[→ Access the dashboard](./dashboard-access.md)** - Explore your trace data
2. **[→ Integrate with LangChain](../agent-frameworks/langchain-integration.md)** - For AI agent workflows
3. **[→ Add performance monitoring](../sdk-reference/configuration.md)** - Optimize your application

## 🆘 Need Help?

- **Examples**: [Complete Examples](../examples/)
- **Community**: [Discord](https://discord.gg/vaquero)
- **Support**: support@vaquero.app

---

**[← Previous: Setup](./setup.md)** | **[→ Next: Dashboard Access](./dashboard-access.md)**
