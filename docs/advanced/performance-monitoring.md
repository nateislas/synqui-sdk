# 📊 Performance Monitoring

**Advanced performance monitoring and optimization strategies** for production applications. Monitor system performance, identify bottlenecks, and optimize resource usage.

## 🎯 What is Performance Monitoring?

Performance monitoring tracks:
- **System metrics** - CPU, memory, disk, network usage
- **Application performance** - Response times, throughput, error rates
- **Resource utilization** - Database connections, cache hit rates, API quotas
- **User experience** - Page load times, interaction delays, perceived performance
- **Business metrics** - Conversion rates, user engagement, operational costs

## 🚀 Basic Performance Monitoring

### Application Performance Metrics

```python
import vaquero
import psutil
import time

@vaquero.trace(agent_name="performance_collector")
class PerformanceCollector:
    """Collect comprehensive application performance metrics."""

    def __init__(self):
        self.metrics = []
        self.start_time = time.time()

    def collect_system_metrics(self) -> dict:
        """Collect system-level performance metrics."""
        with vaquero.span("system_metrics_collection") as span:
            metrics = {
                "timestamp": time.time(),
                "uptime_seconds": time.time() - self.start_time,
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_percent": psutil.disk_usage('/').percent,
                "network_io": dict(psutil.net_io_counters()._asdict()),
                "process_count": len(psutil.pids())
            }

            self.metrics.append(metrics)
            span.set_attribute("metrics_collected", True)
            span.set_attribute("sample_size", len(self.metrics))

            return metrics

    def collect_application_metrics(self) -> dict:
        """Collect application-specific performance metrics."""
        with vaquero.span("application_metrics_collection") as span:
            # Get SDK statistics
            sdk = vaquero.get_default_sdk()
            sdk_stats = sdk.get_stats()

            app_metrics = {
                "timestamp": time.time(),
                "sdk_traces_sent": sdk_stats.get("traces_sent", 0),
                "sdk_queue_size": sdk_stats.get("queue_size", 0),
                "sdk_memory_usage_mb": sdk_stats.get("memory_usage_mb", 0),
                "active_spans": len(sdk._active_spans) if hasattr(sdk, '_active_spans') else 0
            }

            span.set_attribute("application_metrics_collected", True)
            return app_metrics

    def get_performance_summary(self) -> dict:
        """Generate performance summary report."""
        with vaquero.span("performance_summary") as span:
            if not self.metrics:
                return {"error": "No metrics collected"}

            # Calculate averages
            avg_cpu = sum(m["cpu_percent"] for m in self.metrics) / len(self.metrics)
            avg_memory = sum(m["memory_percent"] for m in self.metrics) / len(self.metrics)

            # Find peaks
            max_cpu = max(m["cpu_percent"] for m in self.metrics)
            max_memory = max(m["memory_percent"] for m in self.metrics)

            summary = {
                "collection_period": time.time() - self.start_time,
                "samples_collected": len(self.metrics),
                "system_performance": {
                    "avg_cpu_percent": avg_cpu,
                    "avg_memory_percent": avg_memory,
                    "max_cpu_percent": max_cpu,
                    "max_memory_percent": max_memory,
                    "performance_grade": self._calculate_performance_grade(avg_cpu, avg_memory)
                },
                "recommendations": self._generate_performance_recommendations(avg_cpu, avg_memory)
            }

            span.set_attribute("summary_generated", True)
            span.set_attribute("performance_grade", summary["system_performance"]["performance_grade"])

            return summary

    def _calculate_performance_grade(self, cpu_percent: float, memory_percent: float) -> str:
        """Calculate overall performance grade."""
        avg_utilization = (cpu_percent + memory_percent) / 2

        if avg_utilization < 30:
            return "excellent"
        elif avg_utilization < 50:
            return "good"
        elif avg_utilization < 70:
            return "fair"
        else:
            return "poor"

    def _generate_performance_recommendations(self, cpu_percent: float, memory_percent: float) -> list:
        """Generate performance optimization recommendations."""
        recommendations = []

        if cpu_percent > 80:
            recommendations.append({
                "type": "cpu_optimization",
                "priority": "high",
                "message": "High CPU utilization detected",
                "suggestion": "Consider optimizing CPU-intensive operations or scaling horizontally"
            })

        if memory_percent > 85:
            recommendations.append({
                "type": "memory_optimization",
                "priority": "high",
                "message": "High memory utilization detected",
                "suggestion": "Review memory usage patterns and consider memory optimization"
            })

        return recommendations
```

### Real-time Performance Tracking

```python
import vaquero
import asyncio

@vaquero.trace(agent_name="realtime_monitor")
class RealtimePerformanceMonitor:
    """Monitor performance in real-time with alerting."""

    def __init__(self, alert_thresholds: dict = None):
        self.alert_thresholds = alert_thresholds or {
            "cpu_percent": 80,
            "memory_percent": 85,
            "error_rate": 0.05
        }
        self.alerts_triggered = []

    async def start_monitoring(self, interval: int = 60):
        """Start continuous performance monitoring."""
        with vaquero.span("monitoring_startup") as span:
            span.set_attribute("monitoring_interval", interval)
            span.set_attribute("alert_thresholds", self.alert_thresholds)

            while True:
                try:
                    await self._collect_and_analyze()
                    await asyncio.sleep(interval)
                except Exception as e:
                    span.set_attribute("monitoring_error", str(e))
                    await asyncio.sleep(interval * 2)  # Longer delay on error

    async def _collect_and_analyze(self):
        """Collect metrics and trigger alerts if needed."""
        with vaquero.span("metrics_collection_and_analysis") as span:
            # Collect current metrics
            current_metrics = self._collect_current_metrics()
            span.set_attribute("metrics_collected", True)

            # Analyze for alerts
            alerts = self._check_alert_thresholds(current_metrics)
            if alerts:
                await self._trigger_alerts(alerts)
                span.set_attribute("alerts_triggered", len(alerts))

    def _collect_current_metrics(self) -> dict:
        """Collect current system and application metrics."""
        return {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent,
            "network_bytes_sent": psutil.net_io_counters().bytes_sent,
            "network_bytes_recv": psutil.net_io_counters().bytes_recv,
            "process_count": len(psutil.pids())
        }

    def _check_alert_thresholds(self, metrics: dict) -> list:
        """Check if any metrics exceed alert thresholds."""
        alerts = []

        for metric_name, threshold in self.alert_thresholds.items():
            current_value = metrics.get(metric_name)
            if current_value and current_value > threshold:
                alerts.append({
                    "metric": metric_name,
                    "current_value": current_value,
                    "threshold": threshold,
                    "severity": "high" if current_value > threshold * 1.2 else "medium",
                    "timestamp": time.time()
                })

        return alerts

    async def _trigger_alerts(self, alerts: list):
        """Trigger performance alerts."""
        for alert in alerts:
            with vaquero.span("alert_triggering") as span:
                span.set_attribute("alert_metric", alert["metric"])
                span.set_attribute("alert_value", alert["current_value"])
                span.set_attribute("alert_threshold", alert["threshold"])

                # Send alert (implementation depends on your alerting system)
                await self._send_alert(alert)

                self.alerts_triggered.append(alert)

    async def _send_alert(self, alert: dict):
        """Send performance alert."""
        # Implementation depends on your alerting infrastructure
        print(f"PERFORMANCE ALERT: {alert['metric']} = {alert['current_value']}% (threshold: {alert['threshold']}%)")
```

## 🎨 Advanced Performance Patterns

### Custom Performance Metrics

```python
import vaquero

@vaquero.trace(agent_name="business_metrics_collector")
class BusinessMetricsCollector:
    """Collect business-specific performance metrics."""

    def __init__(self):
        self.user_actions = []
        self.conversion_events = []
        self.performance_baselines = {}

    def record_user_action(self, action_type: str, user_id: str, duration: float, success: bool):
        """Record user action for performance analysis."""
        with vaquero.span("user_action_recording") as span:
            span.set_attribute("action_type", action_type)
            span.set_attribute("user_id", user_id)
            span.set_attribute("duration_ms", duration * 1000)
            span.set_attribute("success", success)

            action_record = {
                "action_type": action_type,
                "user_id": user_id,
                "duration": duration,
                "success": success,
                "timestamp": time.time()
            }

            self.user_actions.append(action_record)

            # Update baseline if needed
            if action_type not in self.performance_baselines:
                self.performance_baselines[action_type] = {
                    "avg_duration": duration,
                    "sample_count": 1
                }
            else:
                baseline = self.performance_baselines[action_type]
                baseline["avg_duration"] = (
                    baseline["avg_duration"] * baseline["sample_count"] + duration
                ) / (baseline["sample_count"] + 1)
                baseline["sample_count"] += 1

    def record_conversion_event(self, event_type: str, user_id: str, value: float = None):
        """Record conversion events for business metrics."""
        with vaquero.span("conversion_tracking") as span:
            span.set_attribute("event_type", event_type)
            span.set_attribute("user_id", user_id)
            span.set_attribute("event_value", value)

            conversion_record = {
                "event_type": event_type,
                "user_id": user_id,
                "value": value,
                "timestamp": time.time()
            }

            self.conversion_events.append(conversion_record)

    def generate_business_report(self) -> dict:
        """Generate business performance report."""
        with vaquero.span("business_report_generation") as span:
            # Calculate user action metrics
            if self.user_actions:
                total_actions = len(self.user_actions)
                successful_actions = len([a for a in self.user_actions if a["success"]])
                avg_action_time = sum(a["duration"] for a in self.user_actions) / total_actions

                action_metrics = {
                    "total_actions": total_actions,
                    "successful_actions": successful_actions,
                    "success_rate": successful_actions / total_actions,
                    "average_duration": avg_action_time
                }
            else:
                action_metrics = {"error": "No user actions recorded"}

            # Calculate conversion metrics
            if self.conversion_events:
                total_conversions = len(self.conversion_events)
                conversion_by_type = {}
                for event in self.conversion_events:
                    event_type = event["event_type"]
                    if event_type not in conversion_by_type:
                        conversion_by_type[event_type] = 0
                    conversion_by_type[event_type] += 1

                conversion_metrics = {
                    "total_conversions": total_conversions,
                    "conversion_by_type": conversion_by_type
                }
            else:
                conversion_metrics = {"error": "No conversions recorded"}

            report = {
                "user_actions": action_metrics,
                "conversions": conversion_metrics,
                "performance_baselines": self.performance_baselines
            }

            span.set_attribute("report_generated", True)
            span.set_attribute("report_sections", len(report))

            return report
```

### Database Performance Monitoring

```python
import vaquero

@vaquero.trace(agent_name="database_performance_monitor")
class DatabasePerformanceMonitor:
    """Monitor database query performance and optimization opportunities."""

    def __init__(self):
        self.query_metrics = []
        self.slow_queries = []

    def record_query_performance(self, query: str, execution_time: float, rows_returned: int, query_type: str = "SELECT"):
        """Record query performance for analysis."""
        with vaquero.span("query_performance_recording") as span:
            span.set_attribute("query_hash", hash(query) % 10000)
            span.set_attribute("execution_time_ms", execution_time * 1000)
            span.set_attribute("rows_returned", rows_returned)
            span.set_attribute("query_type", query_type)

            query_metric = {
                "query": query,
                "execution_time": execution_time,
                "rows_returned": rows_returned,
                "query_type": query_type,
                "timestamp": time.time()
            }

            self.query_metrics.append(query_metric)

            # Track slow queries
            if execution_time > 0.5:  # 500ms threshold
                self.slow_queries.append(query_metric)
                span.set_attribute("slow_query_detected", True)

    def analyze_query_patterns(self) -> dict:
        """Analyze query patterns and identify optimization opportunities."""
        with vaquero.span("query_pattern_analysis") as span:
            if not self.query_metrics:
                return {"error": "No query metrics available"}

            # Group queries by type
            queries_by_type = {}
            for metric in self.query_metrics:
                query_type = metric["query_type"]
                if query_type not in queries_by_type:
                    queries_by_type[query_type] = []
                queries_by_type[query_type].append(metric)

            analysis = {
                "total_queries": len(self.query_metrics),
                "query_types": {},
                "optimization_opportunities": []
            }

            for query_type, queries in queries_by_type.items():
                type_analysis = {
                    "count": len(queries),
                    "avg_execution_time": sum(q["execution_time"] for q in queries) / len(queries),
                    "total_rows_returned": sum(q["rows_returned"] for q in queries),
                    "slow_queries": len([q for q in queries if q["execution_time"] > 0.5])
                }

                analysis["query_types"][query_type] = type_analysis

                # Identify optimization opportunities
                if type_analysis["slow_queries"] > len(queries) * 0.1:  # More than 10% slow
                    analysis["optimization_opportunities"].append({
                        "type": "slow_queries",
                        "query_type": query_type,
                        "issue": f"High percentage of slow {query_type} queries",
                        "recommendation": f"Review {query_type} queries for optimization opportunities"
                    })

            span.set_attribute("analysis_complete", True)
            span.set_attribute("optimization_opportunities_found", len(analysis["optimization_opportunities"]))

            return analysis
```

## 📈 Performance Optimization Strategies

### Memory Usage Optimization

```python
import vaquero
import gc

@vaquero.trace(agent_name="memory_optimizer")
class MemoryOptimizer:
    """Monitor and optimize memory usage patterns."""

    def __init__(self):
        self.memory_snapshots = []

    def take_memory_snapshot(self) -> dict:
        """Take a snapshot of current memory usage."""
        with vaquero.span("memory_snapshot") as span:
            snapshot = {
                "timestamp": time.time(),
                "memory_percent": psutil.virtual_memory().percent,
                "memory_used_mb": psutil.virtual_memory().used / 1024 / 1024,
                "memory_available_mb": psutil.virtual_memory().available / 1024 / 1024,
                "process_memory_mb": self._get_process_memory()
            }

            self.memory_snapshots.append(snapshot)

            # Check for memory leaks
            if len(self.memory_snapshots) > 10:
                memory_trend = self._analyze_memory_trend()
                if memory_trend["increasing"]:
                    span.set_attribute("memory_leak_detected", True)
                    self._trigger_memory_optimization()

            span.set_attribute("snapshot_taken", True)
            return snapshot

    def _get_process_memory(self) -> float:
        """Get memory usage for current process."""
        process = psutil.Process()
        return process.memory_info().rss / 1024 / 1024  # MB

    def _analyze_memory_trend(self) -> dict:
        """Analyze memory usage trends."""
        if len(self.memory_snapshots) < 5:
            return {"error": "Insufficient data for trend analysis"}

        recent_snapshots = self.memory_snapshots[-5:]
        memory_values = [s["memory_used_mb"] for s in recent_snapshots]

        # Simple linear trend detection
        first_value = memory_values[0]
        last_value = memory_values[-1]
        trend = last_value - first_value

        return {
            "trend_mb": trend,
            "increasing": trend > 0,
            "significant_change": abs(trend) > 50  # 50MB threshold
        }

    def _trigger_memory_optimization(self):
        """Trigger memory optimization procedures."""
        with vaquero.span("memory_optimization") as span:
            # Force garbage collection
            gc.collect()

            # Clear any caches if they exist
            if hasattr(self, '_clear_caches'):
                self._clear_caches()

            span.set_attribute("optimization_triggered", True)
            span.set_attribute("gc_collected", True)
```

### Response Time Optimization

```python
import vaquero

@vaquero.trace(agent_name="response_time_optimizer")
class ResponseTimeOptimizer:
    """Monitor and optimize response times."""

    def __init__(self):
        self.response_times = []
        self.response_time_targets = {
            "api_endpoints": 0.5,      # 500ms target
            "database_queries": 0.1,    # 100ms target
            "external_apis": 2.0       # 2 second target
        }

    def record_response_time(self, operation_type: str, duration: float, endpoint: str = None):
        """Record response time for analysis."""
        with vaquero.span("response_time_recording") as span:
            span.set_attribute("operation_type", operation_type)
            span.set_attribute("duration_ms", duration * 1000)
            span.set_attribute("endpoint", endpoint)

            self.response_times.append({
                "operation_type": operation_type,
                "duration": duration,
                "endpoint": endpoint,
                "timestamp": time.time()
            })

            # Check against targets
            target = self.response_time_targets.get(operation_type)
            if target and duration > target:
                span.set_attribute("target_exceeded", True)
                span.set_attribute("target_ms", target * 1000)
                span.set_attribute("exceedance_ms", (duration - target) * 1000)

    def optimize_response_times(self) -> dict:
        """Generate response time optimization recommendations."""
        with vaquero.span("response_time_optimization") as span:
            if not self.response_times:
                return {"error": "No response times recorded"}

            # Group by operation type
            operations_by_type = {}
            for record in self.response_times:
                op_type = record["operation_type"]
                if op_type not in operations_by_type:
                    operations_by_type[op_type] = []
                operations_by_type[op_type].append(record)

            recommendations = {}

            for op_type, records in operations_by_type.items():
                durations = [r["duration"] for r in records]
                avg_duration = sum(durations) / len(durations)
                max_duration = max(durations)

                target = self.response_time_targets.get(op_type, 1.0)

                if avg_duration > target:
                    recommendations[op_type] = {
                        "current_avg_ms": avg_duration * 1000,
                        "target_ms": target * 1000,
                        "improvement_needed_ms": (avg_duration - target) * 1000,
                        "max_duration_ms": max_duration * 1000,
                        "optimization_priority": "high" if avg_duration > target * 2 else "medium"
                    }

            span.set_attribute("recommendations_generated", len(recommendations))
            return recommendations
```

## 🎯 Best Practices

### 1. **Set Realistic Performance Targets**
```python
# ✅ Good - Realistic targets based on use case
targets = {
    "user_registration": 2.0,     # 2 seconds for complex flow
    "api_lookup": 0.2,           # 200ms for simple lookups
    "background_processing": 30.0 # 30 seconds for batch jobs
}

# ❌ Avoid - Unrealistic targets
targets = {
    "user_registration": 0.1,     # 100ms - too aggressive
    "api_lookup": 0.001,         # 1ms - impossible
}
```

### 2. **Monitor Resource Utilization**
```python
# ✅ Good - Comprehensive resource monitoring
@vaquero.trace(agent_name="resource_monitor")
def monitor_resources():
    with vaquero.span("resource_check") as span:
        cpu_usage = psutil.cpu_percent()
        memory_usage = psutil.virtual_memory().percent
        disk_usage = psutil.disk_usage('/').percent

        span.set_attribute("cpu_usage", cpu_usage)
        span.set_attribute("memory_usage", memory_usage)
        span.set_attribute("disk_usage", disk_usage)

        # Alert on high utilization
        if cpu_usage > 80 or memory_usage > 85:
            span.set_attribute("high_utilization_detected", True)
```

### 3. **Track Business Impact**
```python
# ✅ Good - Business-focused metrics
@vaquero.trace(agent_name="business_impact_tracker")
def track_business_impact(error_rate: float, response_time: float):
    with vaquero.span("business_impact_assessment") as span:
        span.set_attribute("error_rate", error_rate)
        span.set_attribute("avg_response_time", response_time)

        # Calculate business impact
        if error_rate > 0.05:  # 5% error rate
            impact = "high"
        elif response_time > 2.0:  # 2 second response time
            impact = "medium"
        else:
            impact = "low"

        span.set_attribute("business_impact", impact)
```

## 🚨 Common Issues

### "Performance monitoring overhead"
```python
# Monitor the monitoring overhead
@vaquero.trace(agent_name="monitoring_overhead_check")
def check_monitoring_overhead():
    start = time.time()
    # Your monitoring code here
    monitoring_time = time.time() - start

    if monitoring_time > 0.1:  # 100ms threshold
        print(f"Monitoring overhead too high: {monitoring_time*1000:.2f}ms")
```

### "False positive alerts"
```python
# Implement alert cooldown periods
last_alert_time = 0
alert_cooldown = 300  # 5 minutes

if should_alert and (time.time() - last_alert_time) > alert_cooldown:
    trigger_alert()
    last_alert_time = time.time()
```

### "Missing performance context"
```python
# Include operational context in metrics
@vaquero.trace(agent_name="contextual_performance")
def record_with_context(operation_type: str, duration: float):
    with vaquero.span("performance_with_context") as span:
        span.set_attribute("operation_type", operation_type)
        span.set_attribute("duration_ms", duration * 1000)
        span.set_attribute("environment", os.getenv("ENVIRONMENT", "unknown"))
        span.set_attribute("server_load", get_current_load())
        span.set_attribute("database_connections", get_active_connections())
```

## 🎉 You're Ready!

Performance monitoring gives you deep insights into your application's performance characteristics, resource utilization, and optimization opportunities. Combined with auto-instrumentation, you get complete visibility into both application behavior and system performance.

Next, explore **[Workflow Orchestration](./workflow-orchestration.md)** for monitoring complex multi-step processes or **[Custom Spans](./custom-spans.md)** for advanced tracing techniques.
