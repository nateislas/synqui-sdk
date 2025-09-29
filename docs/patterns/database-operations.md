# 🗄️ Database Operation Tracing

Monitor database queries, transactions, and connection patterns to identify performance bottlenecks and optimize data access. Essential for applications with database-heavy workloads.

## 🎯 What is Database Operation Tracing?

Database operation tracing captures:
- **Query performance** - Execution time, rows returned, query complexity
- **Connection details** - Pool usage, connection errors, transaction states
- **Transaction tracking** - Begin, commit, rollback operations
- **Error patterns** - Connection failures, timeout issues, constraint violations
- **Resource usage** - Memory usage, lock contention, index utilization

## 🚀 Basic Database Tracing

### SQLAlchemy Integration

```python
import vaquero
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()
engine = create_engine("postgresql://user:pass@localhost/db")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Traced database operations
@vaquero.trace(agent_name="user_repository")
class UserRepository:
    """User repository with comprehensive database tracing."""

    def __init__(self):
        self.SessionLocal = SessionLocal

    @vaquero.trace(agent_name="user_lookup")
    def get_user_by_id(self, user_id: int) -> dict | None:
        """Get user by ID with query tracing."""
        with self.SessionLocal() as session:
            with vaquero.span("database_query") as span:
                span.set_attribute("query_type", "SELECT")
                span.set_attribute("table", "users")
                span.set_attribute("user_id", user_id)

                try:
                    user = session.query(User).filter(User.id == user_id).first()
                    span.set_attribute("user_found", user is not None)

                    if user:
                        span.set_attribute("query_result", "success")
                        return {
                            "id": user.id,
                            "name": user.name,
                            "email": user.email
                        }
                    else:
                        span.set_attribute("query_result", "not_found")
                        return None

                except Exception as e:
                    span.set_attribute("query_result", "error")
                    span.set_attribute("error_type", type(e).__name__)
                    raise

    @vaquero.trace(agent_name="user_creation")
    def create_user(self, name: str, email: str) -> int:
        """Create user with transaction tracing."""
        with vaquero.span("user_transaction") as span:
            span.set_attribute("operation", "INSERT")
            span.set_attribute("table", "users")

            with self.SessionLocal() as session:
                with vaquero.span("insert_operation") as insert_span:
                    try:
                        user = User(name=name, email=email)
                        session.add(user)
                        session.commit()

                        insert_span.set_attribute("user_created", True)
                        insert_span.set_attribute("created_user_id", user.id)
                        span.set_attribute("transaction_result", "committed")

                        return user.id

                    except Exception as e:
                        session.rollback()
                        insert_span.set_attribute("user_created", False)
                        span.set_attribute("transaction_result", "rolled_back")
                        span.set_attribute("error_type", type(e).__name__)
                        raise

# Usage
user_repo = UserRepository()
user = user_repo.get_user_by_id(123)
new_user_id = user_repo.create_user("John Doe", "john@example.com")
```

### Raw SQL Query Tracing

```python
import vaquero
import psycopg2

@vaquero.trace(agent_name="raw_sql_client")
class DatabaseClient:
    """Raw SQL client with comprehensive tracing."""

    def __init__(self, connection_string: str):
        self.connection_string = connection_string

    def execute_query(self, query: str, params: tuple = None) -> list:
        """Execute raw SQL query with tracing."""
        with vaquero.span("raw_sql_execution") as span:
            span.set_attribute("query_type", "SELECT" if query.strip().upper().startswith("SELECT") else "MODIFY")
            span.set_attribute("query_length", len(query))
            span.set_attribute("has_parameters", params is not None)

            with psycopg2.connect(self.connection_string) as conn:
                with conn.cursor() as cursor:
                    with vaquero.span("query_execution") as exec_span:
                        start_time = time.time()
                        cursor.execute(query, params or ())
                        results = cursor.fetchall()
                        execution_time = time.time() - start_time

                        exec_span.set_attribute("rows_returned", len(results))
                        exec_span.set_attribute("execution_time_ms", execution_time * 1000)
                        span.set_attribute("query_successful", True)

                        return results

    def execute_transaction(self, queries: list) -> bool:
        """Execute multiple queries in a transaction."""
        with vaquero.span("database_transaction") as span:
            span.set_attribute("query_count", len(queries))
            span.set_attribute("transaction_type", "multi_query")

            with psycopg2.connect(self.connection_string) as conn:
                with vaquero.span("transaction_setup") as setup_span:
                    try:
                        # Begin transaction
                        with vaquero.span("begin_transaction") as begin_span:
                            conn.autocommit = False

                        # Execute queries
                        for i, (query, params) in enumerate(queries):
                            with vaquero.span(f"query_{i+1}") as query_span:
                                query_span.set_attribute("query_index", i + 1)
                                query_span.set_attribute("query_type", "SELECT" if query.strip().upper().startswith("SELECT") else "MODIFY")

                                with conn.cursor() as cursor:
                                    cursor.execute(query, params or ())

                                query_span.set_attribute("query_successful", True)

                        # Commit transaction
                        with vaquero.span("commit_transaction") as commit_span:
                            conn.commit()
                            span.set_attribute("transaction_result", "committed")

                        return True

                    except Exception as e:
                        # Rollback on error
                        with vaquero.span("rollback_transaction") as rollback_span:
                            conn.rollback()
                            span.set_attribute("transaction_result", "rolled_back")
                            span.set_attribute("error_type", type(e).__name__)

                        raise
```

## 🎨 Advanced Database Patterns

### Connection Pool Monitoring

```python
import vaquero

@vaquero.trace(agent_name="connection_pool_monitor")
class ConnectionPoolMonitor:
    """Monitor database connection pool performance."""

    def __init__(self, pool):
        self.pool = pool
        self.metrics = {
            "connections_created": 0,
            "connections_checked_out": 0,
            "connections_checked_in": 0,
            "pool_exhaustion_events": 0
        }

    @vaquero.trace(agent_name="pool_operation")
    def get_connection(self):
        """Get connection from pool with monitoring."""
        with vaquero.span("connection_acquisition") as span:
            span.set_attribute("pool_size", self.pool.size())
            span.set_attribute("pool_checked_out", self.pool.checkedout())

            try:
                conn = self.pool.getconn()
                self.metrics["connections_checked_out"] += 1

                span.set_attribute("acquisition_successful", True)
                span.set_attribute("pool_utilization", self.pool.checkedout() / self.pool.size())

                return conn

            except Exception as e:
                self.metrics["pool_exhaustion_events"] += 1
                span.set_attribute("acquisition_successful", False)
                span.set_attribute("error_type", "pool_exhausted")
                raise

    @vaquero.trace(agent_name="connection_return")
    def return_connection(self, conn):
        """Return connection to pool with monitoring."""
        with vaquero.span("connection_return") as span:
            span.set_attribute("connection_state", "returning")

            try:
                self.pool.putconn(conn)
                self.metrics["connections_checked_in"] += 1
                span.set_attribute("return_successful", True)

            except Exception as e:
                span.set_attribute("return_successful", False)
                span.set_attribute("error_type", type(e).__name__)
                raise

    @vaquero.trace(agent_name="pool_metrics")
    def get_pool_metrics(self) -> dict:
        """Get comprehensive pool performance metrics."""
        with vaquero.span("metrics_collection") as span:
            current_metrics = {
                "pool_size": self.pool.size(),
                "checked_out_connections": self.pool.checkedout(),
                "available_connections": self.pool.size() - self.pool.checkedout(),
                "total_operations": sum(self.metrics.values()),
                **self.metrics
            }

            span.set_attribute("pool_utilization_percent", (self.pool.checkedout() / self.pool.size()) * 100)
            span.set_attribute("pool_efficiency", self.metrics["connections_checked_in"] / max(self.metrics["connections_checked_out"], 1))

            return current_metrics
```

### Query Performance Analysis

```python
import vaquero
import sqlparse

@vaquero.trace(agent_name="query_analyzer")
class QueryAnalyzer:
    """Analyze query performance and patterns."""

    def __init__(self):
        self.query_stats = {}

    @vaquero.trace(agent_name="query_analysis")
    def analyze_query(self, query: str, execution_time: float) -> dict:
        """Analyze a query for performance insights."""
        with vaquero.span("query_parsing") as span:
            span.set_attribute("query_length", len(query))
            span.set_attribute("execution_time_ms", execution_time * 1000)

            # Parse query structure
            parsed = sqlparse.parse(query)[0]
            span.set_attribute("query_complexity", len(parsed.tokens))

            # Identify query type
            query_type = self._identify_query_type(query)
            span.set_attribute("detected_query_type", query_type)

            # Track statistics
            if query_type not in self.query_stats:
                self.query_stats[query_type] = {
                    "count": 0,
                    "total_time": 0,
                    "avg_time": 0,
                    "slow_queries": 0
                }

            stats = self.query_stats[query_type]
            stats["count"] += 1
            stats["total_time"] += execution_time

            if execution_time > 1.0:  # Slow query threshold
                stats["slow_queries"] += 1

            stats["avg_time"] = stats["total_time"] / stats["count"]

            return {
                "query_type": query_type,
                "complexity_score": len(parsed.tokens),
                "performance_category": "slow" if execution_time > 1.0 else "fast",
                "statistics": stats
            }

    def _identify_query_type(self, query: str) -> str:
        """Identify the type of SQL query."""
        query_upper = query.strip().upper()

        if query_upper.startswith("SELECT"):
            return "SELECT"
        elif query_upper.startswith("INSERT"):
            return "INSERT"
        elif query_upper.startswith("UPDATE"):
            return "UPDATE"
        elif query_upper.startswith("DELETE"):
            return "DELETE"
        else:
            return "UNKNOWN"

    @vaquero.trace(agent_name="performance_report")
    def generate_performance_report(self) -> dict:
        """Generate comprehensive performance report."""
        with vaquero.span("report_generation") as span:
            total_queries = sum(stats["count"] for stats in self.query_stats.values())
            total_time = sum(stats["total_time"] for stats in self.query_stats.values())

            report = {
                "summary": {
                    "total_queries": total_queries,
                    "total_execution_time": total_time,
                    "average_query_time": total_time / max(total_queries, 1)
                },
                "query_types": self.query_stats,
                "recommendations": self._generate_recommendations()
            }

            span.set_attribute("report_query_types", len(self.query_stats))
            span.set_attribute("report_total_queries", total_queries)

            return report

    def _generate_recommendations(self) -> list:
        """Generate optimization recommendations."""
        recommendations = []

        for query_type, stats in self.query_stats.items():
            if stats["slow_queries"] > stats["count"] * 0.1:  # More than 10% slow
                recommendations.append({
                    "type": "performance",
                    "query_type": query_type,
                    "issue": f"High percentage of slow {query_type} queries",
                    "suggestion": f"Review {query_type} queries for optimization opportunities"
                })

        return recommendations
```

### ORM Query Optimization

```python
import vaquero

@vaquero.trace(agent_name="orm_optimizer")
class ORMQueryOptimizer:
    """Optimize ORM queries with tracing."""

    def __init__(self, session):
        self.session = session

    @vaquero.trace(agent_name="n_plus_one_detector")
    def detect_n_plus_one(self, query_func):
        """Detect N+1 query patterns."""
        with vaquero.span("n_plus_one_detection") as span:
            # Monkey patch to count queries
            original_execute = self.session.execute

            query_count = 0
            def counting_execute(*args, **kwargs):
                nonlocal query_count
                query_count += 1
                return original_execute(*args, **kwargs)

            self.session.execute = counting_execute

            try:
                # Execute the potentially problematic query
                result = query_func()

                span.set_attribute("query_count", query_count)
                span.set_attribute("result_count", len(result) if hasattr(result, '__len__') else 1)

                # Detect N+1 pattern
                if query_count > 10:  # Arbitrary threshold
                    span.set_attribute("n_plus_one_detected", True)
                    span.set_attribute("optimization_needed", True)
                else:
                    span.set_attribute("n_plus_one_detected", False)

                return result

            finally:
                # Restore original execute method
                self.session.execute = original_execute

    @vaquero.trace(agent_name="batch_query_optimizer")
    def optimize_batch_query(self, user_ids: list) -> list:
        """Optimize batch queries to avoid N+1 problems."""
        with vaquero.span("batch_optimization") as span:
            span.set_attribute("user_count", len(user_ids))
            span.set_attribute("optimization_strategy", "batch_query")

            # Instead of N+1 queries, use a single batch query
            with vaquero.span("batch_user_lookup") as batch_span:
                batch_span.set_attribute("query_type", "batch_select")
                batch_span.set_attribute("batch_size", len(user_ids))

                # Single query for all users
                users = self.session.query(User).filter(User.id.in_(user_ids)).all()

                batch_span.set_attribute("users_found", len(users))
                span.set_attribute("optimization_successful", len(users) > 0)

                return users
```

## 📊 Database Performance Monitoring

### Query Performance Metrics

```python
import vaquero
import statistics

@vaquero.trace(agent_name="query_performance_tracker")
class QueryPerformanceTracker:
    """Track and analyze query performance metrics."""

    def __init__(self):
        self.query_times = []
        self.slow_queries = []

    @vaquero.trace(agent_name="performance_recording")
    def record_query_performance(self, query: str, execution_time: float, rows_returned: int):
        """Record query performance for analysis."""
        with vaquero.span("performance_tracking") as span:
            span.set_attribute("query_hash", hash(query) % 10000)
            span.set_attribute("execution_time_ms", execution_time * 1000)
            span.set_attribute("rows_returned", rows_returned)

            self.query_times.append(execution_time)

            if execution_time > 0.5:  # Slow query threshold
                self.slow_queries.append({
                    "query": query[:100] + "..." if len(query) > 100 else query,
                    "execution_time": execution_time,
                    "rows_returned": rows_returned
                })
                span.set_attribute("slow_query_detected", True)

    @vaquero.trace(agent_name="performance_analysis")
    def analyze_performance(self) -> dict:
        """Analyze query performance patterns."""
        with vaquero.span("statistical_analysis") as span:
            if not self.query_times:
                return {"error": "No queries recorded"}

            analysis = {
                "total_queries": len(self.query_times),
                "average_execution_time": statistics.mean(self.query_times),
                "median_execution_time": statistics.median(self.query_times),
                "p95_execution_time": statistics.quantiles(self.query_times, n=20)[18],
                "slow_query_count": len(self.slow_queries),
                "slow_query_percentage": len(self.slow_queries) / len(self.query_times) * 100
            }

            span.set_attribute("analysis_complete", True)
            span.set_attribute("slow_query_rate", analysis["slow_query_percentage"])

            return analysis

    @vaquero.trace(agent_name="optimization_suggestions")
    def suggest_optimizations(self) -> list:
        """Suggest query optimizations based on performance data."""
        with vaquero.span("optimization_analysis") as span:
            suggestions = []

            if self.slow_queries:
                # Analyze slow queries for patterns
                slow_query_types = {}
                for slow_query in self.slow_queries:
                    query_type = slow_query["query"].split()[0].upper()
                    if query_type not in slow_query_types:
                        slow_query_types[query_type] = []
                    slow_query_types[query_type].append(slow_query)

                for query_type, queries in slow_query_types.items():
                    if len(queries) > 5:  # Many slow queries of this type
                        suggestions.append({
                            "type": "query_optimization",
                            "query_type": query_type,
                            "issue": f"Multiple slow {query_type} queries detected",
                            "suggestion": f"Consider optimizing {query_type} queries or adding appropriate indexes",
                            "affected_queries": len(queries)
                        })

            span.set_attribute("suggestions_generated", len(suggestions))
            return suggestions
```

## 🛠️ Database Integration Patterns

### Redis Operations Tracing

```python
import vaquero
import redis

@vaquero.trace(agent_name="redis_client")
class TracedRedisClient:
    """Redis client with comprehensive tracing."""

    def __init__(self, host: str = 'localhost', port: int = 6379):
        self.redis_client = redis.Redis(host=host, port=port, decode_responses=True)

    @vaquero.trace(agent_name="redis_operation")
    def get(self, key: str) -> str | None:
        """Get value from Redis with tracing."""
        with vaquero.span("redis_get") as span:
            span.set_attribute("operation", "GET")
            span.set_attribute("key", key)

            try:
                value = self.redis_client.get(key)
                span.set_attribute("value_found", value is not None)
                span.set_attribute("operation_successful", True)

                return value

            except Exception as e:
                span.set_attribute("operation_successful", False)
                span.set_attribute("error_type", type(e).__name__)
                raise

    @vaquero.trace(agent_name="redis_cache_operation")
    def cache_user_data(self, user_id: str, user_data: dict, ttl: int = 3600) -> bool:
        """Cache user data in Redis with tracing."""
        with vaquero.span("redis_cache") as span:
            span.set_attribute("operation", "SET")
            span.set_attribute("key", f"user:{user_id}")
            span.set_attribute("ttl_seconds", ttl)
            span.set_attribute("data_size", len(str(user_data)))

            try:
                cached = self.redis_client.setex(
                    f"user:{user_id}",
                    ttl,
                    json.dumps(user_data)
                )

                span.set_attribute("cache_successful", cached)
                span.set_attribute("operation_successful", True)

                return True

            except Exception as e:
                span.set_attribute("cache_successful", False)
                span.set_attribute("operation_successful", False)
                span.set_attribute("error_type", type(e).__name__)
                raise

    @vaquero.trace(agent_name="redis_batch_operation")
    def batch_operations(self, operations: list) -> dict:
        """Execute multiple Redis operations in a pipeline."""
        with vaquero.span("redis_pipeline") as span:
            span.set_attribute("operation_count", len(operations))
            span.set_attribute("operation_type", "pipeline")

            try:
                with self.redis_client.pipeline() as pipe:
                    with vaquero.span("pipeline_setup") as setup_span:
                        # Queue operations
                        for i, (operation, *args) in enumerate(operations):
                            with vaquero.span(f"queue_operation_{i}") as op_span:
                                op_span.set_attribute("operation_index", i)
                                op_span.set_attribute("operation_type", operation)

                                if operation == "set":
                                    pipe.set(args[0], args[1])
                                elif operation == "get":
                                    pipe.get(args[0])
                                # Add more operations as needed

                        setup_span.set_attribute("operations_queued", len(operations))

                    # Execute pipeline
                    with vaquero.span("pipeline_execution") as exec_span:
                        results = pipe.execute()
                        exec_span.set_attribute("results_count", len(results))
                        exec_span.set_attribute("execution_successful", True)

                span.set_attribute("pipeline_successful", True)
                return {"results": results, "count": len(results)}

            except Exception as e:
                span.set_attribute("pipeline_successful", False)
                span.set_attribute("error_type", type(e).__name__)
                raise
```

## 🎯 Best Practices

### 1. **Query Attribution**
```python
# ✅ Good - Rich query context
with vaquero.span("user_query") as span:
    span.set_attribute("query_type", "SELECT")
    span.set_attribute("table", "users")
    span.set_attribute("filter_columns", ["id", "email"])
    span.set_attribute("expected_rows", "single")

# ❌ Avoid - Minimal context
with vaquero.span("db_op") as span:
    span.set_attribute("op", "select")
```

### 2. **Transaction Tracking**
```python
# ✅ Good - Complete transaction lifecycle
with vaquero.span("user_transaction") as span:
    span.set_attribute("transaction_type", "user_update")
    span.set_attribute("affected_tables", ["users", "user_preferences"])

    with vaquero.span("begin_transaction") as begin_span:
        # Begin transaction logic

    try:
        # Transaction operations
        with vaquero.span("commit_transaction") as commit_span:
            # Commit logic
    except Exception as e:
        with vaquero.span("rollback_transaction") as rollback_span:
            # Rollback logic
```

### 3. **Connection Pool Monitoring**
```python
# ✅ Good - Pool health monitoring
with vaquero.span("connection_acquisition") as span:
    span.set_attribute("pool_size", pool.size())
    span.set_attribute("pool_utilization", pool.checkedout() / pool.size())
    span.set_attribute("pool_wait_time", wait_time)

# ❌ Avoid - Missing pool context
with vaquero.span("db_connection") as span:
    span.set_attribute("connected", True)
```

## 🚨 Common Issues

### "Connection pool exhaustion"
```python
# Monitor pool usage
@vaquero.trace(agent_name="pool_monitor")
def check_pool_health():
    with vaquero.span("pool_health_check") as span:
        utilization = pool.checkedout() / pool.size()
        span.set_attribute("pool_utilization", utilization)

        if utilization > 0.9:
            span.set_attribute("pool_stressed", True)
            # Trigger pool expansion or optimization
```

### "Slow query detection"
```python
# Automatic slow query detection
@vaquero.trace(agent_name="slow_query_detector")
def detect_slow_queries(execution_time: float, threshold: float = 1.0):
    with vaquero.span("slow_query_check") as span:
        span.set_attribute("execution_time_ms", execution_time * 1000)
        span.set_attribute("threshold_ms", threshold * 1000)

        if execution_time > threshold:
            span.set_attribute("slow_query_detected", True)
            # Trigger optimization or alert
```

### "Transaction deadlock monitoring"
```python
# Detect and handle deadlocks
@vaquero.trace(agent_name="deadlock_detector")
def handle_deadlock(error: Exception):
    with vaquero.span("deadlock_handling") as span:
        if "deadlock" in str(error).lower():
            span.set_attribute("deadlock_detected", True)
            span.set_attribute("recovery_strategy", "retry_with_backoff")

            # Implement retry logic with exponential backoff
```

## 🎉 You're Ready!

Database operation tracing gives you deep insights into your data layer performance, query patterns, and potential bottlenecks. Combined with function and API tracing, you get complete observability of your application's data flow.

Next, explore **[Error Handling Patterns](./error-handling.md)** for comprehensive error tracking and debugging strategies.
