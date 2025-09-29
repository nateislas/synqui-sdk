# 🚨 Error Handling & Tracing

Comprehensive error tracking and debugging strategies to understand failure patterns, improve reliability, and maintain system health. Essential for production applications.

## 🎯 What is Error Handling Tracing?

Error handling tracing captures:
- **Exception details** - Type, message, stack trace, and context
- **Error patterns** - Frequency, distribution, and correlation with other events
- **Recovery actions** - Retry attempts, fallback mechanisms, circuit breaker states
- **Impact assessment** - User impact, system degradation, business consequences
- **Root cause analysis** - Error propagation, dependency failures, configuration issues

## 🚀 Basic Error Tracing

### Exception Capture and Context

```python
import vaquero
import logging

logger = logging.getLogger(__name__)

@vaquero.trace(agent_name="error_prone_operation")
def risky_database_operation(user_id: str) -> dict:
    """Database operation that might fail with comprehensive error tracing."""
    with vaquero.span("user_lookup") as span:
        span.set_attribute("user_id", user_id)
        span.set_attribute("operation_type", "user_retrieval")

        try:
            # Simulate database operation that might fail
            if user_id == "invalid":
                raise ConnectionError("Database connection failed")

            user_data = {"id": user_id, "name": "John Doe", "email": "john@example.com"}
            span.set_attribute("user_found", True)
            span.set_attribute("operation_successful", True)

            return user_data

        except ConnectionError as e:
            # Network/Database errors
            span.set_attribute("error_type", "connection_error")
            span.set_attribute("error_category", "infrastructure")
            span.set_attribute("operation_successful", False)

            # Log additional context
            logger.error(f"Database connection failed for user {user_id}", extra={
                "user_id": user_id,
                "error_type": type(e).__name__,
                "error_message": str(e)
            })

            raise

        except Exception as e:
            # Unexpected errors
            span.set_attribute("error_type", "unexpected_error")
            span.set_attribute("error_category", "application")
            span.set_attribute("operation_successful", False)

            # Don't log sensitive information in production
            logger.error(f"Unexpected error in user lookup", extra={
                "user_id": user_id,
                "error_type": type(e).__name__
            })

            raise
```

### Async Error Handling

```python
import vaquero
import asyncio

@vaquero.trace(agent_name="async_api_client")
class AsyncAPIClient:
    """Async API client with error tracing and retry logic."""

    def __init__(self, base_url: str, max_retries: int = 3):
        self.base_url = base_url
        self.max_retries = max_retries

    @vaquero.trace(agent_name="api_request")
    async def make_request(self, endpoint: str, method: str = "GET") -> dict:
        """Make API request with retry logic and error tracing."""
        for attempt in range(self.max_retries):
            with vaquero.span(f"attempt_{attempt + 1}") as attempt_span:
                attempt_span.set_attribute("attempt_number", attempt + 1)
                attempt_span.set_attribute("max_retries", self.max_retries)
                attempt_span.set_attribute("endpoint", endpoint)
                attempt_span.set_attribute("method", method)

                try:
                    # Simulate API call
                    if attempt < 2 and method == "POST":  # Fail first 2 attempts for POST
                        raise ConnectionError(f"Network error on attempt {attempt + 1}")

                    # Simulate successful response
                    response = {"status": "success", "data": {"id": 123}}
                    attempt_span.set_attribute("request_successful", True)
                    attempt_span.set_attribute("response_status", 200)

                    return response

                except ConnectionError as e:
                    attempt_span.set_attribute("request_successful", False)
                    attempt_span.set_attribute("error_type", "connection_error")

                    if attempt == self.max_retries - 1:
                        # Final attempt failed
                        attempt_span.set_attribute("final_attempt", True)
                        raise

                    # Wait before retry
                    wait_time = 2 ** attempt  # Exponential backoff
                    attempt_span.set_attribute("retry_wait_time", wait_time)

                    await asyncio.sleep(wait_time)

                except Exception as e:
                    attempt_span.set_attribute("request_successful", False)
                    attempt_span.set_attribute("error_type", "unexpected_error")
                    attempt_span.set_attribute("final_attempt", attempt == self.max_retries - 1)

                    raise
```

## 🎨 Advanced Error Patterns

### Circuit Breaker Pattern

```python
import vaquero
import asyncio
from enum import Enum

class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

@vaquero.trace(agent_name="circuit_breaker")
class CircuitBreaker:
    """Circuit breaker implementation with comprehensive tracing."""

    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.state = CircuitState.CLOSED
        self.last_failure_time = None

    @vaquero.trace(agent_name="circuit_breaker_call")
    async def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker protection."""
        with vaquero.span("circuit_breaker_execution") as span:
            span.set_attribute("circuit_state", self.state.value)
            span.set_attribute("failure_count", self.failure_count)
            span.set_attribute("failure_threshold", self.failure_threshold)

            if self.state == CircuitState.OPEN:
                if self._should_attempt_reset():
                    self.state = CircuitState.HALF_OPEN
                    span.set_attribute("state_transition", "open_to_half_open")
                else:
                    span.set_attribute("circuit_open", True)
                    raise Exception("Circuit breaker is OPEN")

            try:
                result = await func(*args, **kwargs)
                self._on_success(span)
                return result

            except Exception as e:
                self._on_failure(span)
                span.set_attribute("error_type", type(e).__name__)
                span.set_attribute("error_message", str(e))
                raise

    def _should_attempt_reset(self) -> bool:
        """Check if we should attempt to reset the circuit breaker."""
        if self.last_failure_time is None:
            return True
        return (asyncio.get_event_loop().time() - self.last_failure_time) >= self.recovery_timeout

    def _on_success(self, span):
        """Handle successful call."""
        with vaquero.span("success_handling") as success_span:
            self.failure_count = 0
            old_state = self.state
            self.state = CircuitState.CLOSED

            success_span.set_attribute("old_state", old_state.value)
            success_span.set_attribute("new_state", self.state.value)
            success_span.set_attribute("state_transition", f"{old_state.value}_to_{self.state.value}")

    def _on_failure(self, span):
        """Handle failed call."""
        with vaquero.span("failure_handling") as failure_span:
            self.failure_count += 1
            self.last_failure_time = asyncio.get_event_loop().time()
            old_state = self.state

            if self.failure_count >= self.failure_threshold:
                self.state = CircuitState.OPEN
                failure_span.set_attribute("circuit_opened", True)

            failure_span.set_attribute("old_state", old_state.value)
            failure_span.set_attribute("new_state", self.state.value)
            failure_span.set_attribute("failure_count", self.failure_count)
```

### Error Aggregation and Analysis

```python
import vaquero
from collections import defaultdict, deque
from datetime import datetime, timedelta

@vaquero.trace(agent_name="error_aggregator")
class ErrorAggregator:
    """Aggregate and analyze error patterns."""

    def __init__(self, window_size: int = 1000, time_window: timedelta = timedelta(minutes=5)):
        self.window_size = window_size
        self.time_window = time_window
        self.error_counts = defaultdict(int)
        self.error_window = deque(maxlen=window_size)
        self.error_patterns = defaultdict(list)

    @vaquero.trace(agent_name="error_recording")
    def record_error(self, error: Exception, context: dict = None):
        """Record an error for pattern analysis."""
        with vaquero.span("error_aggregation") as span:
            span.set_attribute("error_type", type(error).__name__)
            span.set_attribute("error_message", str(error))
            span.set_attribute("context_provided", context is not None)

            # Add to error window
            error_record = {
                "error_type": type(error).__name__,
                "error_message": str(error),
                "timestamp": datetime.utcnow(),
                "context": context or {}
            }

            self.error_window.append(error_record)
            self.error_counts[type(error).__name__] += 1

            # Analyze patterns
            self._analyze_error_patterns(span)

            span.set_attribute("window_size", len(self.error_window))
            span.set_attribute("unique_error_types", len(self.error_counts))

    def _analyze_error_patterns(self, span):
        """Analyze error patterns for insights."""
        with vaquero.span("pattern_analysis") as pattern_span:
            # Group errors by type and time window
            time_cutoff = datetime.utcnow() - self.time_window

            recent_errors = [
                error for error in self.error_window
                if error["timestamp"] > time_cutoff
            ]

            pattern_span.set_attribute("recent_error_count", len(recent_errors))

            # Detect error spikes
            if len(recent_errors) > 50:  # Arbitrary threshold
                pattern_span.set_attribute("error_spike_detected", True)

                # Analyze error distribution
                error_types_recent = defaultdict(int)
                for error in recent_errors:
                    error_types_recent[error["error_type"]] += 1

                pattern_span.set_attribute("error_types_in_spike", len(error_types_recent))

                # Most common error in spike
                if error_types_recent:
                    most_common = max(error_types_recent.items(), key=lambda x: x[1])
                    pattern_span.set_attribute("most_common_error", most_common[0])
                    pattern_span.set_attribute("most_common_count", most_common[1])

    @vaquero.trace(agent_name="error_report_generation")
    def generate_error_report(self) -> dict:
        """Generate comprehensive error report."""
        with vaquero.span("report_compilation") as span:
            # Calculate error rates
            total_errors = len(self.error_window)
            time_cutoff = datetime.utcnow() - self.time_window
            recent_errors = [
                error for error in self.error_window
                if error["timestamp"] > time_cutoff
            ]

            report = {
                "summary": {
                    "total_errors": total_errors,
                    "recent_errors": len(recent_errors),
                    "error_rate_per_minute": len(recent_errors) / max((datetime.utcnow() - time_cutoff).total_seconds() / 60, 1),
                    "unique_error_types": len(self.error_counts)
                },
                "error_distribution": dict(self.error_counts),
                "patterns": self._identify_patterns()
            }

            span.set_attribute("report_period_minutes", self.time_window.total_seconds() / 60)
            span.set_attribute("report_coverage_percent", len(recent_errors) / max(total_errors, 1) * 100)

            return report

    def _identify_patterns(self) -> dict:
        """Identify error patterns and trends."""
        patterns = {}

        # Analyze error frequency trends
        if len(self.error_window) >= 10:
            recent_errors = list(self.error_window)[-10:]  # Last 10 errors
            error_types_recent = [error["error_type"] for error in recent_errors]

            # Check for repeated errors
            for error_type in set(error_types_recent):
                count = error_types_recent.count(error_type)
                if count >= 3:  # 3 or more of same error type
                    patterns[error_type] = {
                        "frequency": count,
                        "pattern": "repeated_errors",
                        "severity": "high" if count >= 5 else "medium"
                    }

        return patterns
```

### Custom Exception Handling

```python
import vaquero

@vaquero.trace(agent_name="custom_exception_handler")
class CustomExceptionHandler:
    """Custom exception handling with tracing."""

    def __init__(self):
        self.error_counts = defaultdict(int)
        self.error_contexts = {}

    @vaquero.trace(agent_name="exception_processing")
    def handle_exception(self, exception: Exception, context: dict = None) -> dict:
        """Process and categorize exceptions with rich tracing."""
        with vaquero.span("exception_analysis") as span:
            span.set_attribute("exception_type", type(exception).__name__)
            span.set_attribute("exception_message", str(exception))
            span.set_attribute("context_provided", context is not None)

            # Categorize exception
            category = self._categorize_exception(exception)
            span.set_attribute("exception_category", category)

            # Track error counts
            self.error_counts[category] += 1
            span.set_attribute("category_count", self.error_counts[category])

            # Store error context for analysis
            error_id = f"{type(exception).__name__}_{hash(str(exception))}"
            self.error_contexts[error_id] = {
                "exception": exception,
                "context": context,
                "category": category,
                "timestamp": datetime.utcnow()
            }

            # Generate response based on category
            response = self._generate_response(category, exception, context)

            span.set_attribute("response_generated", True)
            span.set_attribute("response_type", response.get("type", "unknown"))

            return response

    def _categorize_exception(self, exception: Exception) -> str:
        """Categorize exception for appropriate handling."""
        if isinstance(exception, ConnectionError):
            return "network_error"
        elif isinstance(exception, ValueError):
            return "validation_error"
        elif isinstance(exception, KeyError):
            return "data_error"
        elif isinstance(exception, TimeoutError):
            return "timeout_error"
        else:
            return "unexpected_error"

    def _generate_response(self, category: str, exception: Exception, context: dict) -> dict:
        """Generate appropriate response for exception category."""
        if category == "network_error":
            return {
                "type": "retry",
                "message": "Network error occurred. Please retry the operation.",
                "retry_after": 5,
                "max_retries": 3
            }
        elif category == "validation_error":
            return {
                "type": "user_error",
                "message": "Invalid input provided. Please check your data.",
                "validation_errors": self._extract_validation_errors(exception)
            }
        elif category == "timeout_error":
            return {
                "type": "system_overload",
                "message": "Service is currently experiencing high load. Please try again later.",
                "suggested_wait": 30
            }
        else:
            return {
                "type": "system_error",
                "message": "An unexpected error occurred. Please contact support.",
                "error_id": f"ERR_{int(time.time())}"
            }

    def _extract_validation_errors(self, exception: Exception) -> list:
        """Extract specific validation errors from exception."""
        # Implementation depends on your validation framework
        return [str(exception)]
```

## 📊 Error Monitoring and Alerting

### Error Rate Monitoring

```python
import vaquero

@vaquero.trace(agent_name="error_rate_monitor")
class ErrorRateMonitor:
    """Monitor error rates and trigger alerts."""

    def __init__(self, alert_threshold: float = 0.05):  # 5% error rate
        self.alert_threshold = alert_threshold
        self.error_window = deque(maxlen=1000)
        self.success_window = deque(maxlen=1000)

    @vaquero.trace(agent_name="error_rate_tracking")
    def record_operation(self, success: bool, operation_type: str = "unknown"):
        """Record operation success/failure for rate calculation."""
        with vaquero.span("rate_calculation") as span:
            span.set_attribute("operation_success", success)
            span.set_attribute("operation_type", operation_type)

            if success:
                self.success_window.append(True)
            else:
                self.error_window.append(False)

            # Calculate current error rate
            total_operations = len(self.error_window) + len(self.success_window)
            error_rate = len(self.error_window) / max(total_operations, 1)

            span.set_attribute("total_operations", total_operations)
            span.set_attribute("error_rate", error_rate)
            span.set_attribute("error_count", len(self.error_window))

            # Check if alert threshold exceeded
            if error_rate > self.alert_threshold and total_operations > 10:
                span.set_attribute("alert_triggered", True)
                span.set_attribute("alert_threshold", self.alert_threshold)

                # Trigger alert
                self._trigger_alert(error_rate, operation_type)

    def _trigger_alert(self, error_rate: float, operation_type: str):
        """Trigger error rate alert."""
        with vaquero.span("alert_triggering") as span:
            span.set_attribute("alert_type", "error_rate")
            span.set_attribute("current_rate", error_rate)
            span.set_attribute("threshold", self.alert_threshold)
            span.set_attribute("operation_type", operation_type)

            # Send alert (implementation depends on your alerting system)
            alert_data = {
                "type": "error_rate_exceeded",
                "error_rate": error_rate,
                "threshold": self.alert_threshold,
                "operation_type": operation_type,
                "timestamp": datetime.utcnow()
            }

            # Send to alerting system
            self._send_alert(alert_data)

    def _send_alert(self, alert_data: dict):
        """Send alert to monitoring system."""
        # Implementation depends on your alerting infrastructure
        print(f"ALERT: {alert_data}")
```

### Error Correlation Analysis

```python
import vaquero

@vaquero.trace(agent_name="error_correlator")
class ErrorCorrelator:
    """Correlate errors with system events and user actions."""

    def __init__(self):
        self.error_events = deque(maxlen=1000)
        self.system_events = deque(maxlen=1000)

    @vaquero.trace(agent_name="error_event_recording")
    def record_error_event(self, error: Exception, user_id: str = None, request_id: str = None):
        """Record error event with context."""
        with vaquero.span("error_event_storage") as span:
            span.set_attribute("error_type", type(error).__name__)
            span.set_attribute("user_id", user_id)
            span.set_attribute("request_id", request_id)

            event = {
                "timestamp": datetime.utcnow(),
                "error_type": type(error).__name__,
                "error_message": str(error),
                "user_id": user_id,
                "request_id": request_id,
                "event_type": "error"
            }

            self.error_events.append(event)
            span.set_attribute("event_stored", True)

    @vaquero.trace(agent_name="system_event_recording")
    def record_system_event(self, event_type: str, details: dict):
        """Record system events for correlation analysis."""
        with vaquero.span("system_event_storage") as span:
            span.set_attribute("system_event_type", event_type)
            span.set_attribute("event_details_count", len(details))

            event = {
                "timestamp": datetime.utcnow(),
                "event_type": event_type,
                "details": details,
                "event_type": "system"
            }

            self.system_events.append(event)
            span.set_attribute("event_stored", True)

    @vaquero.trace(agent_name="correlation_analysis")
    def analyze_correlations(self, time_window: timedelta = timedelta(minutes=5)) -> dict:
        """Analyze correlations between errors and system events."""
        with vaquero.span("correlation_computation") as span:
            cutoff_time = datetime.utcnow() - time_window

            # Filter recent events
            recent_errors = [
                event for event in self.error_events
                if event["timestamp"] > cutoff_time
            ]

            recent_system_events = [
                event for event in self.system_events
                if event["timestamp"] > cutoff_time
            ]

            span.set_attribute("recent_errors", len(recent_errors))
            span.set_attribute("recent_system_events", len(recent_system_events))

            # Find correlations
            correlations = self._find_temporal_correlations(recent_errors, recent_system_events)

            analysis = {
                "time_window_minutes": time_window.total_seconds() / 60,
                "error_count": len(recent_errors),
                "system_event_count": len(recent_system_events),
                "correlations": correlations
            }

            span.set_attribute("correlations_found", len(correlations))
            span.set_attribute("analysis_complete", True)

            return analysis

    def _find_temporal_correlations(self, errors: list, system_events: list) -> list:
        """Find temporal correlations between errors and system events."""
        correlations = []

        for error in errors:
            error_time = error["timestamp"]

            # Look for system events within 1 minute of error
            for system_event in system_events:
                time_diff = abs((error_time - system_event["timestamp"]).total_seconds())

                if time_diff <= 60:  # Within 1 minute
                    correlations.append({
                        "error_type": error["error_type"],
                        "system_event_type": system_event["event_type"],
                        "time_difference_seconds": time_diff,
                        "correlation_strength": "strong" if time_diff <= 10 else "weak"
                    })

        return correlations
```

## 🎯 Best Practices

### 1. **Rich Error Context**
```python
# ✅ Good - Comprehensive error context
except Exception as e:
    with vaquero.span("error_handling") as span:
        span.set_attribute("error_type", type(e).__name__)
        span.set_attribute("error_location", "user_lookup")
        span.set_attribute("user_id", user_id)
        span.set_attribute("request_id", request_id)
        span.set_attribute("retry_count", attempt_number)
        span.set_attribute("error_severity", self._assess_severity(e))

# ❌ Avoid - Minimal error context
except Exception as e:
    span.set_attribute("error", "failed")
```

### 2. **Error Categorization**
```python
# ✅ Good - Proper error categorization
def _categorize_error(self, error: Exception) -> str:
    if isinstance(error, (ConnectionError, TimeoutError)):
        return "infrastructure"
    elif isinstance(error, (ValueError, TypeError)):
        return "validation"
    elif isinstance(error, KeyError):
        return "data"
    else:
        return "application"

# ❌ Avoid - No categorization
except Exception as e:
    span.set_attribute("error", str(e))
```

### 3. **Recovery Strategy Tracking**
```python
# ✅ Good - Track recovery attempts
with vaquero.span("recovery_attempt") as span:
    span.set_attribute("recovery_strategy", "retry_with_backoff")
    span.set_attribute("attempt_number", attempt)
    span.set_attribute("backoff_seconds", wait_time)

    try:
        result = await retry_operation()
        span.set_attribute("recovery_successful", True)
    except Exception as e:
        span.set_attribute("recovery_successful", False)
        span.set_attribute("final_failure", attempt == max_attempts)
```

## 🚨 Common Error Scenarios

### Database Connection Failures
```python
@vaquero.trace(agent_name="db_connection_handler")
def handle_db_connection_error(error: Exception, retry_count: int = 0):
    with vaquero.span("db_error_handling") as span:
        span.set_attribute("error_type", "database_connection")
        span.set_attribute("retry_count", retry_count)

        if isinstance(error, ConnectionError):
            span.set_attribute("connection_strategy", "retry")
            span.set_attribute("backoff_strategy", "exponential")

            # Implement connection retry logic
            wait_time = min(2 ** retry_count, 30)  # Max 30 seconds
            time.sleep(wait_time)

            span.set_attribute("retry_wait_time", wait_time)
```

### API Rate Limiting
```python
@vaquero.trace(agent_name="rate_limit_handler")
def handle_rate_limit_error(error: Exception, endpoint: str):
    with vaquero.span("rate_limit_handling") as span:
        span.set_attribute("error_type", "rate_limited")
        span.set_attribute("endpoint", endpoint)
        span.set_attribute("handling_strategy", "backoff_and_retry")

        # Extract retry-after from error response
        retry_after = getattr(error, 'retry_after', 60)
        span.set_attribute("retry_after_seconds", retry_after)

        time.sleep(retry_after)
```

### Authentication Failures
```python
@vaquero.trace(agent_name="auth_error_handler")
def handle_authentication_error(error: Exception, user_context: dict):
    with vaquero.span("auth_error_handling") as span:
        span.set_attribute("error_type", "authentication_failed")
        span.set_attribute("user_id", user_context.get("user_id"))
        span.set_attribute("auth_method", user_context.get("auth_method"))

        if "token" in str(error).lower():
            span.set_attribute("error_subtype", "token_error")
            # Implement token refresh logic
        elif "credentials" in str(error).lower():
            span.set_attribute("error_subtype", "credential_error")
            # Implement re-authentication logic
```

## 🎉 You're Ready!

Error handling and tracing gives you complete visibility into your application's failure patterns, recovery mechanisms, and system reliability. Combined with function, API, and database tracing, you get comprehensive observability across your entire application stack.

Next, explore **[Advanced Features](../advanced/)** for power user capabilities like auto-instrumentation and workflow orchestration.
