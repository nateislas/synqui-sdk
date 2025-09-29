# 🎯 Custom Spans

**Advanced span creation and management** for complex tracing scenarios. Create custom spans for specific operations, build sophisticated tracing hierarchies, and implement custom observability patterns.

## 🎯 What are Custom Spans?

Custom spans allow you to:
- **Create spans manually** for operations that need special handling
- **Build complex hierarchies** beyond simple function tracing
- **Add rich metadata** to any operation, even without decorators
- **Implement custom observability** for unique business logic
- **Create reusable tracing patterns** for common operations

## 🚀 Basic Custom Span Usage

### Manual Span Creation

```python
import vaquero

# Create a custom span anywhere in your code
with vaquero.span("custom_operation") as span:
    span.set_attribute("operation_type", "data_processing")
    span.set_attribute("data_size", len(data))

    # Your custom logic here
    result = process_data(data)
    span.set_attribute("processing_successful", True)
    span.set_attribute("result_size", len(result))

    return result
```

### Async Custom Spans

```python
import vaquero
import asyncio

# Custom spans work with async code too
async def async_operation_with_custom_spans():
    with vaquero.span("async_workflow") as workflow_span:
        workflow_span.set_attribute("workflow_type", "async_processing")

        # Step 1: Async data fetch
        with vaquero.span("data_fetch") as fetch_span:
            fetch_span.set_attribute("fetch_method", "api_call")

            data = await fetch_external_data()
            fetch_span.set_attribute("data_fetched", True)
            fetch_span.set_attribute("data_size", len(data))

        # Step 2: Async processing
        with vaquero.span("data_processing") as process_span:
            process_span.set_attribute("processing_algorithm", "parallel")

            processed_results = await asyncio.gather(*[
                process_single_item(item) for item in data
            ])

            process_span.set_attribute("items_processed", len(processed_results))
            process_span.set_attribute("processing_successful", True)

        # Step 3: Async save
        with vaquero.span("data_save") as save_span:
            save_span.set_attribute("save_method", "batch_insert")

            await save_results_to_database(processed_results)
            save_span.set_attribute("save_successful", True)

        workflow_span.set_attribute("workflow_completed", True)
        return processed_results
```

## 🎨 Advanced Custom Span Patterns

### Context Manager Spans

```python
import vaquero
from contextlib import contextmanager

@contextmanager
def traced_operation(operation_name: str, **attributes):
    """Context manager for creating traced operations."""
    with vaquero.span(operation_name) as span:
        # Set initial attributes
        for key, value in attributes.items():
            span.set_attribute(key, value)

        try:
            yield span
        except Exception as e:
            span.set_attribute("operation_successful", False)
            span.set_attribute("error_type", type(e).__name__)
            span.set_attribute("error_message", str(e))
            raise
        else:
            span.set_attribute("operation_successful", True)

# Usage
def process_with_context_manager(data: dict) -> dict:
    with traced_operation(
        "data_processing",
        data_size=len(str(data)),
        processing_algorithm="enhanced"
    ) as span:
        # Processing logic
        result = enhanced_data_processing(data)

        span.set_attribute("result_size", len(str(result)))
        span.set_attribute("processing_time_ms", 150)

        return result
```

### Decorator-Based Custom Spans

```python
import vaquero
from functools import wraps

def traced_operation(operation_name: str, **default_attributes):
    """Decorator that creates custom spans with default attributes."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            span_attributes = default_attributes.copy()

            # Add function-specific attributes
            span_attributes.update({
                "function_name": func.__name__,
                "module_name": func.__module__,
                "is_method": len(args) > 0 and hasattr(args[0], func.__name__)
            })

            with vaquero.span(operation_name, **span_attributes) as span:
                try:
                    result = func(*args, **kwargs)
                    span.set_attribute("operation_successful", True)
                    return result
                except Exception as e:
                    span.set_attribute("operation_successful", False)
                    span.set_attribute("error_type", type(e).__name__)
                    raise

        return wrapper
    return decorator

# Usage
@traced_operation(
    "user_service",
    service_type="user_management",
    version="2.1"
)
def get_user_profile(user_id: str) -> dict:
    """Get user profile with custom tracing."""
    # Your logic here
    return {"user_id": user_id, "profile": "data"}
```

### Dynamic Span Creation

```python
import vaquero

class DynamicSpanManager:
    """Create and manage spans dynamically based on runtime conditions."""

    def __init__(self):
        self.active_spans = {}

    def start_operation_span(self, operation_id: str, operation_type: str, **attributes):
        """Start a new operation span."""
        span_name = f"operation_{operation_type}_{operation_id}"

        span = vaquero.span(span_name)
        span.set_attribute("operation_id", operation_id)
        span.set_attribute("operation_type", operation_type)

        for key, value in attributes.items():
            span.set_attribute(key, value)

        self.active_spans[operation_id] = span
        return span

    def update_operation_span(self, operation_id: str, **attributes):
        """Update an active operation span."""
        if operation_id in self.active_spans:
            span = self.active_spans[operation_id]
            for key, value in attributes.items():
                span.set_attribute(key, value)

    def complete_operation_span(self, operation_id: str, success: bool = True, **final_attributes):
        """Complete an operation span."""
        if operation_id in self.active_spans:
            span = self.active_spans[operation_id]

            # Add final attributes
            span.set_attribute("operation_completed", True)
            span.set_attribute("operation_successful", success)

            for key, value in final_attributes.items():
                span.set_attribute(key, value)

            # Remove from active spans
            del self.active_spans[operation_id]

# Usage
span_manager = DynamicSpanManager()

def long_running_operation(operation_id: str, data: dict):
    # Start operation
    span_manager.start_operation_span(
        operation_id,
        "data_processing",
        data_size=len(str(data)),
        priority="high"
    )

    try:
        # Long-running processing
        for i in range(10):
            span_manager.update_operation_span(
                operation_id,
                current_step=i+1,
                progress_percent=((i+1) / 10) * 100
            )

            # Simulate work
            time.sleep(0.1)

        # Complete successfully
        span_manager.complete_operation_span(
            operation_id,
            success=True,
            final_result="completed",
            total_steps=10
        )

        return {"status": "success"}

    except Exception as e:
        # Complete with failure
        span_manager.complete_operation_span(
            operation_id,
            success=False,
            error_type=type(e).__name__,
            error_message=str(e)
        )
        raise
```

## 📊 Custom Span Analytics

### Span Performance Analysis

```python
import vaquero

@vaquero.trace(agent_name="span_analytics")
class SpanAnalytics:
    """Analyze custom span performance and patterns."""

    def __init__(self):
        self.span_metrics = []
        self.span_hierarchy = {}

    def record_span_completion(self, span_name: str, duration: float, attributes: dict):
        """Record span completion for analysis."""
        with vaquero.span("span_analysis_recording") as span:
            span.set_attribute("analyzed_span", span_name)
            span.set_attribute("span_duration_ms", duration * 1000)

            metric = {
                "span_name": span_name,
                "duration": duration,
                "attributes": attributes,
                "timestamp": time.time()
            }

            self.span_metrics.append(metric)

            # Build hierarchy analysis
            if span_name not in self.span_hierarchy:
                self.span_hierarchy[span_name] = {
                    "total_duration": 0,
                    "call_count": 0,
                    "avg_duration": 0
                }

            hierarchy = self.span_hierarchy[span_name]
            hierarchy["total_duration"] += duration
            hierarchy["call_count"] += 1
            hierarchy["avg_duration"] = hierarchy["total_duration"] / hierarchy["call_count"]

            span.set_attribute("hierarchy_updated", True)

    def analyze_span_patterns(self) -> dict:
        """Analyze span patterns and identify optimization opportunities."""
        with vaquero.span("span_pattern_analysis") as span:
            if not self.span_metrics:
                return {"error": "No span metrics available"}

            # Group by span name
            spans_by_name = {}
            for metric in self.span_metrics:
                span_name = metric["span_name"]
                if span_name not in spans_by_name:
                    spans_by_name[span_name] = []
                spans_by_name[span_name].append(metric)

            analysis = {
                "total_spans": len(self.span_metrics),
                "unique_span_types": len(spans_by_name),
                "span_performance": {},
                "optimization_suggestions": []
            }

            for span_name, metrics in spans_by_name.items():
                durations = [m["duration"] for m in metrics]
                avg_duration = sum(durations) / len(durations)
                max_duration = max(durations)

                performance = {
                    "call_count": len(metrics),
                    "avg_duration": avg_duration,
                    "max_duration": max_duration,
                    "total_duration": sum(durations),
                    "performance_category": self._categorize_performance(avg_duration)
                }

                analysis["span_performance"][span_name] = performance

                # Generate optimization suggestions
                if avg_duration > 1.0:  # More than 1 second average
                    analysis["optimization_suggestions"].append({
                        "span_name": span_name,
                        "issue": "High average duration",
                        "current_avg_ms": avg_duration * 1000,
                        "suggestion": f"Consider optimizing {span_name} operation"
                    })

            span.set_attribute("analysis_complete", True)
            span.set_attribute("suggestions_generated", len(analysis["optimization_suggestions"]))

            return analysis

    def _categorize_performance(self, avg_duration: float) -> str:
        """Categorize span performance."""
        if avg_duration < 0.1:  # Less than 100ms
            return "excellent"
        elif avg_duration < 0.5:  # Less than 500ms
            return "good"
        elif avg_duration < 2.0:  # Less than 2 seconds
            return "fair"
        else:
            return "poor"
```

### Custom Span Hierarchies

```python
import vaquero

class CustomSpanHierarchy:
    """Build and manage custom span hierarchies."""

    def __init__(self):
        self.span_tree = {}

    def create_hierarchical_span(self, parent_name: str, child_name: str, **attributes):
        """Create a hierarchical span relationship."""
        with vaquero.span(parent_name) as parent_span:
            parent_span.set_attribute("span_type", "parent")
            parent_span.set_attribute("child_span", child_name)

            for key, value in attributes.items():
                parent_span.set_attribute(key, value)

            # Create child span
            with vaquero.span(child_name) as child_span:
                child_span.set_attribute("span_type", "child")
                child_span.set_attribute("parent_span", parent_name)
                child_span.set_attribute("hierarchy_level", 2)

                # Child logic here
                result = self._execute_child_logic(child_name, attributes)

                child_span.set_attribute("child_successful", True)
                return result

    def _execute_child_logic(self, span_name: str, attributes: dict):
        """Execute logic specific to child span."""
        if "database" in span_name.lower():
            return self._execute_database_operation(attributes)
        elif "api" in span_name.lower():
            return self._execute_api_operation(attributes)
        else:
            return self._execute_generic_operation(attributes)

    def _execute_database_operation(self, attributes: dict):
        """Execute database operation with tracing."""
        with vaquero.span("db_query_execution") as span:
            span.set_attribute("query_type", attributes.get("query_type", "unknown"))

            # Database logic
            result = execute_database_query(attributes)
            span.set_attribute("query_successful", True)

            return result

    def _execute_api_operation(self, attributes: dict):
        """Execute API operation with tracing."""
        with vaquero.span("api_call_execution") as span:
            span.set_attribute("api_endpoint", attributes.get("endpoint", "unknown"))

            # API logic
            result = make_api_call(attributes)
            span.set_attribute("api_successful", True)

            return result

    def _execute_generic_operation(self, attributes: dict):
        """Execute generic operation with tracing."""
        with vaquero.span("generic_operation") as span:
            span.set_attribute("operation_type", "generic")

            # Generic logic
            result = perform_generic_operation(attributes)
            span.set_attribute("operation_successful", True)

            return result

# Usage
hierarchy_manager = CustomSpanHierarchy()

def complex_business_operation(user_id: str, operation_type: str):
    """Complex operation with hierarchical span structure."""
    return hierarchy_manager.create_hierarchical_span(
        "business_operation",
        f"{operation_type}_execution",
        user_id=user_id,
        operation_type=operation_type,
        complexity="high"
    )
```

## 🎯 Best Practices

### 1. **Span Naming Conventions**
```python
# ✅ Good - Clear, descriptive names
with vaquero.span("user_profile_lookup") as span:
with vaquero.span("payment_processing") as span:
with vaquero.span("email_notification") as span:

# ❌ Avoid - Generic, unclear names
with vaquero.span("operation") as span:
with vaquero.span("process") as span:
with vaquero.span("task") as span:
```

### 2. **Attribute Consistency**
```python
# ✅ Good - Consistent attribute naming
span.set_attribute("user_id", user_id)
span.set_attribute("operation_type", "user_lookup")
span.set_attribute("success", True)
span.set_attribute("duration_ms", 150)

# ❌ Avoid - Inconsistent naming
span.set_attribute("userID", user_id)      # camelCase
span.set_attribute("operation", "lookup")   # Different name
span.set_attribute("result", "success")     # Different name
span.set_attribute("time_taken", 150)      # Different units
```

### 3. **Error Context in Custom Spans**
```python
# ✅ Good - Comprehensive error context
try:
    with vaquero.span("risky_operation") as span:
        span.set_attribute("operation_type", "data_processing")
        span.set_attribute("input_size", len(data))

        result = process_risky_data(data)
        span.set_attribute("operation_successful", True)

except Exception as e:
    span.set_attribute("operation_successful", False)
    span.set_attribute("error_type", type(e).__name__)
    span.set_attribute("error_location", "data_processing")
    span.set_attribute("error_severity", "high")
    raise
```

## 🚨 Common Issues

### "Custom spans not appearing"
```python
# Check if spans are properly created and closed
@vaquero.trace(agent_name="span_debugger")
def debug_span_creation():
    with vaquero.span("test_span") as span:
        span.set_attribute("test_attribute", "test_value")
        # Make sure to return or use the span context

        # Span will be automatically closed when exiting the 'with' block
        return span.get_attribute("test_attribute")
```

### "Performance overhead from custom spans"
```python
# Use span sampling for high-frequency operations
@vaquero.trace(agent_name="sampled_operation")
def high_frequency_operation():
    import random

    # Only create spans for 10% of operations
    if random.random() < 0.1:
        with vaquero.span("sampled_operation") as span:
            span.set_attribute("sampled", True)
            # Your logic here
    else:
        # Your logic without tracing
        pass
```

### "Complex span hierarchies"
```python
# Build clear span hierarchies
def complex_workflow():
    with vaquero.span("workflow_root") as root_span:
        root_span.set_attribute("workflow_type", "complex")

        # Level 1 spans
        with vaquero.span("phase_1") as phase1_span:
            phase1_span.set_attribute("phase", 1)

            # Level 2 spans
            with vaquero.span("step_1_1") as step_span:
                step_span.set_attribute("step", "1.1")
                # Your logic here

            with vaquero.span("step_1_2") as step_span:
                step_span.set_attribute("step", "1.2")
                # Your logic here

        # Level 1 spans
        with vaquero.span("phase_2") as phase2_span:
            phase2_span.set_attribute("phase", 2)
            # More logic here
```

## 📚 Custom Span Libraries

### Reusable Span Patterns

```python
import vaquero

class SpanPatterns:
    """Reusable span creation patterns."""

    @staticmethod
    def database_operation_span(operation_name: str, table: str, query_type: str = "SELECT"):
        """Create a database operation span."""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                with vaquero.span(operation_name) as span:
                    span.set_attribute("operation_type", "database")
                    span.set_attribute("table", table)
                    span.set_attribute("query_type", query_type)

                    try:
                        result = func(*args, **kwargs)
                        span.set_attribute("operation_successful", True)
                        return result
                    except Exception as e:
                        span.set_attribute("operation_successful", False)
                        span.set_attribute("error_type", type(e).__name__)
                        raise
            return wrapper
        return decorator

    @staticmethod
    def api_operation_span(operation_name: str, endpoint: str, method: str = "GET"):
        """Create an API operation span."""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                with vaquero.span(operation_name) as span:
                    span.set_attribute("operation_type", "api")
                    span.set_attribute("endpoint", endpoint)
                    span.set_attribute("method", method)

                    try:
                        result = func(*args, **kwargs)
                        span.set_attribute("operation_successful", True)
                        return result
                    except Exception as e:
                        span.set_attribute("operation_successful", False)
                        span.set_attribute("error_type", type(e).__name__)
                        raise
            return wrapper
        return decorator

# Usage
@SpanPatterns.database_operation_span("user_lookup", "users", "SELECT")
def get_user_from_db(user_id: str):
    # Database logic
    return {"id": user_id, "name": "John"}

@SpanPatterns.api_operation_span("external_api_call", "/api/data", "POST")
def call_external_api(data: dict):
    # API logic
    return {"status": "success"}
```

## 🎉 You're Ready!

Custom spans give you complete control over your tracing implementation, allowing you to build sophisticated observability patterns that fit your specific use cases. Combined with auto-instrumentation and other advanced features, you can achieve comprehensive visibility across your entire application.

Next, explore **[Framework Integrations](../integrations/)** for framework-specific tracing patterns or **[Troubleshooting](../troubleshooting.md)** for debugging and optimization guides.
