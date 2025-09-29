# 🌐 API Endpoint Tracing

Monitor your API endpoints to understand request patterns, performance characteristics, and error rates. Perfect for REST APIs, GraphQL endpoints, and microservices.

## 🎯 What is API Endpoint Tracing?

API endpoint tracing captures:
- **Request/response details** - Method, URL, status codes, response times
- **Request metadata** - Headers, query parameters, request body size
- **Response metrics** - Response size, content type, error details
- **Client information** - User agents, IP addresses, authentication status
- **Performance data** - Database queries, external API calls, processing time

## 🚀 Basic API Endpoint Tracing

### FastAPI Integration

```python
from fastapi import FastAPI, Depends, HTTPException
import vaquero

app = FastAPI()

# Middleware for automatic request tracing
@app.middleware("http")
async def vaquero_middleware(request, call_next):
    with vaquero.span("http_request") as span:
        span.set_attribute("method", request.method)
        span.set_attribute("url", str(request.url))
        span.set_attribute("user_agent", request.headers.get("user-agent", ""))

        response = await call_next(request)

        span.set_attribute("status_code", response.status_code)
        span.set_attribute("response_size", len(await response.body()))

        return response

# Traced endpoint
@app.get("/users/{user_id}")
@vaquero.trace(agent_name="user_service")
async def get_user(user_id: int):
    """Get user by ID with automatic tracing."""
    with vaquero.span("database_lookup") as span:
        span.set_attribute("user_id", user_id)
        span.set_attribute("query_type", "SELECT")

        # Simulate database call
        user = await database.get_user(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        span.set_attribute("user_found", True)

    return user
```

### Flask Integration

```python
from flask import Flask, request, g
import vaquero

app = Flask(__name__)

@app.before_request
def before_request():
    g.start_time = time.time()

@app.after_request
def after_request(response):
    if hasattr(g, 'start_time'):
        duration = time.time() - g.start_time

        with vaquero.span("flask_request") as span:
            span.set_attribute("method", request.method)
            span.set_attribute("path", request.path)
            span.set_attribute("status_code", response.status_code)
            span.set_attribute("duration_ms", duration * 1000)
            span.set_attribute("user_agent", request.headers.get("User-Agent", ""))

    return response

@app.route("/api/users/<int:user_id>")
@vaquero.trace(agent_name="user_api")
def get_user(user_id):
    """Get user endpoint with tracing."""
    with vaquero.span("user_lookup") as span:
        span.set_attribute("user_id", user_id)

        user = database.get_user(user_id)
        if not user:
            span.set_attribute("user_found", False)
            return {"error": "User not found"}, 404

        span.set_attribute("user_found", True)
        return user
```

### Django Integration

```python
# middleware.py
from django.utils.deprecation import MiddlewareMixin
import vaquero
import time

class VaqueroMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request._vaquero_start_time = time.time()

    def process_response(self, request, response):
        if hasattr(request, '_vaquero_start_time'):
            duration = time.time() - request._vaquero_start_time

            with vaquero.span("django_request") as span:
                span.set_attribute("method", request.method)
                span.set_attribute("path", request.path)
                span.set_attribute("status_code", response.status_code)
                span.set_attribute("duration_ms", duration * 1000)

        return response

# views.py
from django.http import JsonResponse
import vaquero

@vaquero.trace(agent_name="user_view")
def get_user(request, user_id):
    """Get user view with tracing."""
    with vaquero.span("user_query") as span:
        span.set_attribute("user_id", user_id)
        span.set_attribute("request_method", request.method)

        try:
            user = User.objects.get(id=user_id)
            span.set_attribute("user_found", True)

            return JsonResponse({
                "id": user.id,
                "name": user.name,
                "email": user.email
            })

        except User.DoesNotExist:
            span.set_attribute("user_found", False)
            return JsonResponse({"error": "User not found"}, status=404)
```

## 🎨 Advanced API Patterns

### Request/Response Tracing

Monitor the complete request lifecycle:

```python
import vaquero
from fastapi import FastAPI, Request, Response

app = FastAPI()

@app.middleware("http")
async def comprehensive_middleware(request: Request, call_next):
    request_id = str(uuid.uuid4())

    with vaquero.span("api_request") as span:
        span.set_attribute("request_id", request_id)
        span.set_attribute("method", request.method)
        span.set_attribute("url", str(request.url))
        span.set_attribute("client_ip", request.client.host)

        # Capture request details
        with vaquero.span("request_details") as req_span:
            req_span.set_attribute("content_type", request.headers.get("content-type"))
            req_span.set_attribute("user_agent", request.headers.get("user-agent"))
            req_span.set_attribute("accept_language", request.headers.get("accept-language"))

            # Capture request body (be careful with size)
            if request.method in ["POST", "PUT", "PATCH"]:
                body = await request.body()
                req_span.set_attribute("request_size", len(body))

        start_time = time.time()
        response = await call_next(request)
        duration = time.time() - start_time

        # Capture response details
        with vaquero.span("response_details") as resp_span:
            resp_span.set_attribute("status_code", response.status_code)
            resp_span.set_attribute("response_time_ms", duration * 1000)

            # Don't capture response body for large responses
            if response.headers.get("content-length"):
                content_length = int(response.headers.get("content-length", 0))
                if content_length < 10000:  # Only for small responses
                    resp_span.set_attribute("response_size", content_length)

        span.set_attribute("total_duration_ms", duration * 1000)

        return response
```

### Authentication and Authorization Tracing

```python
import vaquero

@vaquero.trace(agent_name="auth_service")
async def authenticate_user(credentials: dict) -> dict:
    """Authenticate user with comprehensive tracing."""
    with vaquero.span("credential_validation") as span:
        span.set_attribute("auth_method", credentials.get("method", "unknown"))

        if not credentials.get("username") or not credentials.get("password"):
            span.set_attribute("validation_result", "failed")
            raise ValueError("Missing credentials")

        span.set_attribute("validation_result", "passed")

    with vaquero.span("user_lookup") as span:
        span.set_attribute("lookup_source", "database")

        user = await database.get_user_by_username(credentials["username"])
        if not user:
            span.set_attribute("user_found", False)
            raise ValueError("User not found")

        span.set_attribute("user_found", True)

    with vaquero.span("password_verification") as span:
        span.set_attribute("hash_algorithm", "bcrypt")

        is_valid = verify_password(credentials["password"], user.hashed_password)
        span.set_attribute("password_valid", is_valid)

        if not is_valid:
            raise ValueError("Invalid password")

    with vaquero.span("token_generation") as span:
        span.set_attribute("token_type", "jwt")

        token = generate_jwt_token(user)
        span.set_attribute("token_generated", True)

    return {
        "user_id": user.id,
        "token": token,
        "expires_at": time.time() + 3600
    }
```

### API Rate Limiting and Throttling

```python
import vaquero

@vaquero.trace(agent_name="rate_limiter")
async def check_rate_limit(user_id: str, endpoint: str) -> bool:
    """Check rate limits with tracing."""
    with vaquero.span("rate_limit_check") as span:
        span.set_attribute("user_id", user_id)
        span.set_attribute("endpoint", endpoint)

        # Check different rate limit windows
        with vaquero.span("minute_limit") as minute_span:
            minute_count = await redis.incr(f"rate_limit:{user_id}:{endpoint}:minute")
            minute_span.set_attribute("count", minute_count)
            minute_span.set_attribute("limit", 60)

            if minute_count == 1:
                await redis.expire(f"rate_limit:{user_id}:{endpoint}:minute", 60)

        with vaquero.span("hour_limit") as hour_span:
            hour_count = await redis.incr(f"rate_limit:{user_id}:{endpoint}:hour")
            hour_span.set_attribute("count", hour_count)
            hour_span.set_attribute("limit", 1000)

            if hour_count == 1:
                await redis.expire(f"rate_limit:{user_id}:{endpoint}:hour", 3600)

        # Determine if rate limited
        is_limited = minute_count > 60 or hour_count > 1000
        span.set_attribute("rate_limited", is_limited)

        return not is_limited
```

## 📊 API Metrics and Analytics

### Response Time Monitoring

```python
import vaquero
import statistics

class APIMetrics:
    """Collect and analyze API performance metrics."""

    def __init__(self):
        self.response_times = []

    @vaquero.trace(agent_name="metrics_collector")
    async def record_response_time(self, endpoint: str, method: str, duration: float):
        """Record response time for analysis."""
        with vaquero.span("metrics_recording") as span:
            span.set_attribute("endpoint", endpoint)
            span.set_attribute("method", method)
            span.set_attribute("duration_ms", duration * 1000)

            self.response_times.append(duration)

            # Calculate statistics every 100 requests
            if len(self.response_times) % 100 == 0:
                await self.calculate_statistics()

    @vaquero.trace(agent_name="statistics_calculator")
    async def calculate_statistics(self):
        """Calculate response time statistics."""
        if not self.response_times:
            return

        with vaquero.span("statistical_analysis") as span:
            mean_time = statistics.mean(self.response_times)
            median_time = statistics.median(self.response_times)
            p95_time = statistics.quantiles(self.response_times, n=20)[18]  # 95th percentile

            span.set_attribute("mean_response_time", mean_time)
            span.set_attribute("median_response_time", median_time)
            span.set_attribute("p95_response_time", p95_time)
            span.set_attribute("sample_size", len(self.response_times))

            # Log slow requests
            slow_requests = [t for t in self.response_times if t > 1.0]  # > 1 second
            if slow_requests:
                span.set_attribute("slow_request_count", len(slow_requests))
                span.set_attribute("slow_request_percentage", len(slow_requests) / len(self.response_times) * 100)

# Global metrics collector
api_metrics = APIMetrics()
```

### Error Rate Monitoring

```python
import vaquero

@vaquero.trace(agent_name="error_tracker")
async def track_api_errors(error: Exception, endpoint: str, user_id: str = None):
    """Track API errors for monitoring."""
    with vaquero.span("error_tracking") as span:
        span.set_attribute("error_type", type(error).__name__)
        span.set_attribute("error_message", str(error))
        span.set_attribute("endpoint", endpoint)

        if user_id:
            span.set_attribute("user_id", user_id)

        # Categorize errors
        if isinstance(error, ConnectionError):
            span.set_attribute("error_category", "network")
        elif isinstance(error, ValueError):
            span.set_attribute("error_category", "validation")
        elif isinstance(error, HTTPException):
            span.set_attribute("error_category", "client_error")
        else:
            span.set_attribute("error_category", "server_error")

        # Send to error tracking service
        await error_service.report_error(error, span)
```

## 🛠️ Framework-Specific Patterns

### GraphQL Endpoint Tracing

```python
import vaquero
from strawberry.fastapi import GraphQLRouter

@vaquero.trace(agent_name="graphql_resolver")
async def resolve_user(root, info, user_id: int):
    """GraphQL resolver with tracing."""
    with vaquero.span("user_resolution") as span:
        span.set_attribute("user_id", user_id)
        span.set_attribute("resolver", "resolve_user")
        span.set_attribute("query_complexity", info.field_asts[0].selection_set.selections)

        # Resolve user data
        user = await database.get_user(user_id)
        span.set_attribute("resolution_successful", user is not None)

        return user

# Create GraphQL schema with tracing
@strawberry.type
class Query:
    user: User = strawberry.field(resolver=resolve_user)

schema = strawberry.Schema(query=Query)
graphql_app = GraphQLRouter(schema)
```

### WebSocket Endpoint Tracing

```python
import vaquero
import asyncio
from fastapi import WebSocket

@vaquero.trace(agent_name="websocket_handler")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket connection with tracing."""
    await websocket.accept()

    with vaquero.span("websocket_connection") as span:
        span.set_attribute("connection_type", "websocket")
        span.set_attribute("protocol", "ws")

        try:
            while True:
                with vaquero.span("message_processing") as msg_span:
                    data = await websocket.receive_text()
                    msg_span.set_attribute("message_size", len(data))

                    # Process message
                    response = await process_websocket_message(data)
                    msg_span.set_attribute("processing_successful", True)

                    await websocket.send_text(response)

        except WebSocketDisconnect:
            span.set_attribute("disconnection_reason", "client_disconnect")
        except Exception as e:
            span.set_attribute("error_type", type(e).__name__)
            span.set_attribute("connection_failed", True)
            raise
```

## 📈 Performance Optimization

### Database Query Optimization

```python
import vaquero

@vaquero.trace(agent_name="query_optimizer")
async def optimized_user_query(user_ids: list[int]) -> list[dict]:
    """Optimized user query with performance monitoring."""
    with vaquero.span("query_optimization") as span:
        span.set_attribute("query_type", "batch_lookup")
        span.set_attribute("user_count", len(user_ids))

        # Use batch query instead of N+1 queries
        with vaquero.span("batch_query_execution") as query_span:
            query_span.set_attribute("query_method", "batch_select")

            # Single query for all users
            users = await database.batch_get_users(user_ids)
            query_span.set_attribute("users_found", len(users))

        # Process results
        with vaquero.span("result_processing") as process_span:
            process_span.set_attribute("processing_algorithm", "parallel")

            processed_users = []
            for user in users:
                # Process each user (could be parallelized)
                processed_user = await enrich_user_data(user)
                processed_users.append(processed_user)

            process_span.set_attribute("processed_count", len(processed_users))

        return processed_users
```

## 🎯 Best Practices

### 1. **Consistent Naming**
```python
# ✅ Good - Clear and consistent
@vaquero.trace(agent_name="user_api")
async def get_user(user_id: int):

@vaquero.trace(agent_name="user_api")
async def create_user(user_data: dict):

@vaquero.trace(agent_name="user_api")
async def update_user(user_id: int, data: dict):

# ❌ Avoid - Inconsistent naming
@vaquero.trace(agent_name="get_user")
async def get_user(user_id: int):

@vaquero.trace(agent_name="user_creation")
async def create_user(user_data: dict):
```

### 2. **Request Context**
```python
# ✅ Good - Include request context
with vaquero.span("api_request") as span:
    span.set_attribute("request_id", request_id)
    span.set_attribute("user_id", current_user.id)
    span.set_attribute("session_id", session.id)

# ❌ Avoid - Missing context
with vaquero.span("api_request") as span:
    span.set_attribute("status", "success")
```

### 3. **Error Context**
```python
# ✅ Good - Rich error context
except Exception as e:
    with vaquero.span("error_context") as span:
        span.set_attribute("error_type", type(e).__name__)
        span.set_attribute("error_location", "user_lookup")
        span.set_attribute("user_id", user_id)
        span.set_attribute("retry_count", attempt_number)

# ❌ Avoid - Minimal error context
except Exception as e:
    span.set_attribute("error", "failed")
```

## 🚨 Common Issues

### "Middleware not capturing all requests"
```python
# Make sure middleware is added to ALL routes
app.add_middleware(VaqueroMiddleware)

# Check if specific routes need special handling
@app.middleware("http")
async def vaquero_middleware(request, call_next):
    # Handle all request types
    if request.method in ["GET", "POST", "PUT", "DELETE", "PATCH"]:
        # Apply tracing
        pass
    return await call_next(request)
```

### "Performance overhead too high"
```python
# Use sampling for high-traffic endpoints
@app.middleware("http")
async def sampled_middleware(request, call_next):
    if random.random() < 0.1:  # Sample 10% of requests
        with vaquero.span("sampled_request") as span:
            return await call_next(request)
    else:
        return await call_next(request)
```

### "Missing request/response data"
```python
# Capture request body carefully
@app.middleware("http")
async def body_capture_middleware(request, call_next):
    if request.method in ["POST", "PUT", "PATCH"]:
        body = await request.body()
        if len(body) < 10000:  # Only capture small requests
            with vaquero.span("request_body") as span:
                span.set_attribute("body_size", len(body))
```

## 🎉 You're Ready!

API endpoint tracing gives you complete visibility into your API's behavior, performance, and error patterns. Combined with function tracing, you get a complete picture of your application's request processing pipeline.

Next, explore **[Database Operation Tracing](./database-operations.md)** or **[Error Handling Patterns](./error-handling.md)** for more specific use cases.
