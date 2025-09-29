# 📋 Function Tracing

The most common and fundamental pattern in Vaquero - tracing individual functions and methods to understand their behavior, performance, and interactions.

## 🎯 What is Function Tracing?

Function tracing automatically captures:
- **Execution time** - How long the function takes to run
- **Input parameters** - What data was passed to the function
- **Return values** - What the function returned
- **Exceptions** - Any errors that occurred during execution
- **Custom attributes** - Additional context you add

## 🚀 Basic Function Tracing

### Simple Synchronous Function

```python
import vaquero

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

# Usage
result = process_user_data("user123", {"key": "value"})
```

### Async Function Tracing

```python
import vaquero
import asyncio

@vaquero.trace(agent_name="api_client")
async def fetch_user_profile(user_id: str) -> dict:
    """Fetch user profile from external API."""
    # Simulate API call
    await asyncio.sleep(0.1)

    return {
        "user_id": user_id,
        "name": "John Doe",
        "email": "john@example.com"
    }

# Usage
profile = await fetch_user_profile("user123")
```

## 🎨 Advanced Function Tracing

### Custom Attributes and Tags

Add context to your traces for better analysis:

```python
import vaquero

@vaquero.trace(
    agent_name="ml_predictor",
    tags={
        "model_version": "v2.1",
        "environment": "production",
        "team": "ml"
    }
)
def predict_sentiment(text: str) -> dict:
    """Predict sentiment with rich metadata."""
    # Add custom attributes during execution
    with vaquero.span("text_analysis") as span:
        span.set_attribute("text_length", len(text))
        span.set_attribute("language", "en")

        # Your ML logic here
        confidence = 0.85
        sentiment = "positive" if confidence > 0.5 else "negative"

        span.set_attribute("confidence_score", confidence)
        span.set_attribute("predicted_sentiment", sentiment)

    return {
        "sentiment": sentiment,
        "confidence": confidence,
        "model": "v2.1"
    }
```

### Error Handling and Tracing

Errors are automatically captured, but you can add context:

```python
import vaquero

@vaquero.trace(agent_name="risky_operation")
def risky_operation(data: dict) -> dict:
    """Operation that might fail - demonstrates error tracing."""
    try:
        if not data.get("required_field"):
            raise ValueError("Missing required field")

        # Your risky logic here
        result = process_data(data)
        return result

    except Exception as e:
        # Error context is automatically captured
        # You can add additional context if needed
        with vaquero.span("error_context") as span:
            span.set_attribute("error_type", type(e).__name__)
            span.set_attribute("data_validation_failed", True)

        raise
```

## 🏗️ Pattern: Nested Function Calls

Trace the entire call stack of complex operations:

```python
import vaquero

@vaquero.trace(agent_name="user_registration")
def register_user(user_data: dict) -> dict:
    """Complete user registration workflow."""
    # This creates the parent span

    # Step 1: Validate data
    with vaquero.span("data_validation") as span:
        span.set_attribute("validation_type", "user_registration")

        validated_data = validate_user_data(user_data)
        span.set_attribute("validation_passed", True)

    # Step 2: Check for existing user
    with vaquero.span("duplicate_check") as span:
        span.set_attribute("check_type", "email_uniqueness")

        existing_user = check_existing_user(validated_data["email"])
        if existing_user:
            raise ValueError("User already exists")

        span.set_attribute("user_exists", False)

    # Step 3: Create user
    with vaquero.span("user_creation") as span:
        span.set_attribute("creation_method", "database_insert")

        user_id = create_user_in_database(validated_data)
        span.set_attribute("created_user_id", user_id)

    # Step 4: Send welcome email
    with vaquero.span("welcome_email") as span:
        span.set_attribute("email_template", "welcome_v1")

        email_sent = send_welcome_email(user_id, validated_data["email"])
        span.set_attribute("email_delivered", email_sent)

    return {"user_id": user_id, "status": "registered"}

@vaquero.trace(agent_name="data_validator")
def validate_user_data(data: dict) -> dict:
    """Validate user registration data."""
    # This creates a child span under user_registration
    return {"email": data["email"], "name": data["name"]}

@vaquero.trace(agent_name="user_checker")
def check_existing_user(email: str) -> dict | None:
    """Check if user already exists."""
    # This creates another child span
    return None  # User doesn't exist
```

## 📊 Pattern: Performance Monitoring

Monitor function performance and identify bottlenecks:

```python
import vaquero
import time

@vaquero.trace(agent_name="performance_monitor")
def monitored_function(data: list) -> dict:
    """Function with detailed performance monitoring."""
    start_time = time.time()

    # Track different phases of execution
    with vaquero.span("initialization") as span:
        span.set_attribute("data_size", len(data))
        # Initialization logic
        time.sleep(0.01)

    with vaquero.span("processing") as span:
        span.set_attribute("algorithm", "batch_processing")

        # Main processing logic
        processed_count = 0
        for item in data:
            # Process each item
            processed_count += 1

        span.set_attribute("items_processed", processed_count)

    with vaquero.span("finalization") as span:
        # Finalization logic
        result = {"count": processed_count, "status": "complete"}
        span.set_attribute("result_size", len(str(result)))

    total_time = time.time() - start_time

    # Add overall performance metrics
    with vaquero.span("performance_summary") as span:
        span.set_attribute("total_execution_time", total_time)
        span.set_attribute("items_per_second", len(data) / total_time)

    return result
```

## 🛠️ Pattern: Context Managers

Use context managers for resource management:

```python
import vaquero

@vaquero.trace(agent_name="resource_manager")
def managed_operation(file_path: str, data: dict) -> bool:
    """Operation that manages external resources."""
    with vaquero.span("file_operation") as span:
        span.set_attribute("operation", "write")
        span.set_attribute("file_path", file_path)

        # Resource management with tracing
        with open(file_path, 'w') as file:
            with vaquero.span("data_serialization") as serialize_span:
                serialize_span.set_attribute("data_type", type(data).__name__)

                json_data = json.dumps(data)
                serialize_span.set_attribute("serialized_size", len(json_data))

            with vaquero.span("file_write") as write_span:
                write_span.set_attribute("bytes_written", len(json_data))

                file.write(json_data)
                write_span.set_attribute("write_successful", True)

        span.set_attribute("operation_successful", True)

    return True
```

## 📈 When to Use Function Tracing

### ✅ Good Use Cases
- **API endpoints** - Monitor request/response patterns
- **Business logic functions** - Track data transformations
- **External service calls** - Monitor third-party API usage
- **Database operations** - Track query performance
- **Complex algorithms** - Monitor computational tasks

### ❌ Avoid These Cases
- **Very frequent operations** - May impact performance
- **Very simple getters/setters** - Usually not worth tracing
- **Internal utility functions** - Unless they have performance impact
- **One-liner functions** - Minimal value add

## 🎯 Best Practices

### 1. **Descriptive Agent Names**
```python
# ✅ Good
@vaquero.trace(agent_name="user_authentication_validator")
def validate_credentials(username, password):

# ❌ Avoid
@vaquero.trace(agent_name="validator")
def validate_credentials(username, password):
```

### 2. **Meaningful Attributes**
```python
# ✅ Good
with vaquero.span("database_query") as span:
    span.set_attribute("query_type", "SELECT")
    span.set_attribute("table", "users")
    span.set_attribute("row_count", len(results))

# ❌ Avoid
with vaquero.span("db_op") as span:
    span.set_attribute("x", "SELECT")
```

### 3. **Handle Sensitive Data**
```python
# ✅ Good
with vaquero.span("user_operation") as span:
    span.set_attribute("user_id", user_id)  # Safe to log
    span.set_attribute("operation_type", "update")

# ❌ Avoid
with vaquero.span("user_operation") as span:
    span.set_attribute("password", password)  # Never log passwords!
```

## 🚨 Common Issues

### "Traces not appearing in dashboard"
```python
# Check if SDK is properly configured
import vaquero

if not vaquero.get_default_sdk().config.enabled:
    print("SDK is disabled")

# Manually flush pending traces
vaquero.flush()
```

### "Performance impact too high"
```python
# Reduce batch size for lower latency
from vaquero import SDKConfig

config = SDKConfig(batch_size=10, flush_interval=1.0)
vaquero.configure_from_config(config)
```

### "Too much data being captured"
```python
# Disable input/output capture for performance
config = SDKConfig(
    capture_inputs=False,
    capture_outputs=False,
    capture_errors=True  # Keep error tracking
)
vaquero.configure_from_config(config)
```

## 🎉 You're Ready!

Function tracing is the foundation of observability. With these patterns, you can monitor your application's behavior, identify performance bottlenecks, and debug issues effectively.

Next, explore **[API Endpoint Tracing](./api-endpoints.md)** or **[Database Operation Tracing](./database-operations.md)** for more specific patterns.
