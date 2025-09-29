# 🔄 Workflow Orchestration

**Monitor complex multi-step processes and business workflows** with comprehensive tracing. Perfect for understanding process flows, identifying bottlenecks, and optimizing complex operations.

## 🎯 What is Workflow Orchestration?

Workflow orchestration tracing captures:
- **Process flow** - Step-by-step execution of complex workflows
- **Decision points** - Conditional logic and branching paths
- **Parallel execution** - Concurrent operations and dependencies
- **State transitions** - Changes in workflow state over time
- **Resource coordination** - How different components interact
- **Failure recovery** - Error handling and retry mechanisms

## 🚀 Basic Workflow Tracing

### Simple Sequential Workflow

```python
import vaquero
import asyncio

@vaquero.trace(agent_name="user_registration_workflow")
async def register_user_workflow(user_data: dict) -> dict:
    """Complete user registration workflow with comprehensive tracing."""
    workflow_id = f"reg_{int(time.time())}"

    with vaquero.span("user_registration_workflow") as workflow_span:
        workflow_span.set_attribute("workflow_id", workflow_id)
        workflow_span.set_attribute("workflow_type", "user_registration")
        workflow_span.set_attribute("user_email", user_data.get("email", "unknown"))

        # Step 1: Validate user data
        with vaquero.span("data_validation") as validate_span:
            validate_span.set_attribute("validation_type", "user_registration")

            try:
                validated_data = await validate_user_data(user_data)
                validate_span.set_attribute("validation_successful", True)
                validate_span.set_attribute("validated_fields", list(validated_data.keys()))
            except Exception as e:
                validate_span.set_attribute("validation_successful", False)
                validate_span.set_attribute("validation_error", str(e))
                raise

        # Step 2: Check for existing user
        with vaquero.span("duplicate_check") as check_span:
            check_span.set_attribute("check_type", "email_uniqueness")

            existing_user = await check_existing_user(validated_data["email"])
            if existing_user:
                check_span.set_attribute("user_exists", True)
                check_span.set_attribute("existing_user_id", existing_user["id"])
                raise ValueError("User already exists")
            else:
                check_span.set_attribute("user_exists", False)

        # Step 3: Create user in database
        with vaquero.span("user_creation") as create_span:
            create_span.set_attribute("creation_method", "database_insert")

            user_id = await create_user_in_database(validated_data)
            create_span.set_attribute("created_user_id", user_id)
            create_span.set_attribute("creation_successful", True)

        # Step 4: Send welcome email
        with vaquero.span("welcome_email") as email_span:
            email_span.set_attribute("email_template", "welcome_v1")
            email_span.set_attribute("recipient_email", validated_data["email"])

            email_sent = await send_welcome_email(user_id, validated_data["email"])
            email_span.set_attribute("email_delivered", email_sent)

        # Step 5: Update analytics
        with vaquero.span("analytics_update") as analytics_span:
            analytics_span.set_attribute("event_type", "user_registration")
            analytics_span.set_attribute("user_id", user_id)

            await update_user_analytics(user_id, "registration_completed")
            analytics_span.set_attribute("analytics_updated", True)

        # Workflow completion
        workflow_span.set_attribute("workflow_completed", True)
        workflow_span.set_attribute("final_user_id", user_id)

        return {
            "workflow_id": workflow_id,
            "user_id": user_id,
            "status": "completed",
            "steps_completed": 5
        }
```

### Parallel Workflow Execution

```python
import vaquero
import asyncio

@vaquero.trace(agent_name="parallel_processing_workflow")
async def process_user_batch(users: list) -> dict:
    """Process multiple users in parallel with workflow tracing."""
    workflow_id = f"batch_{int(time.time())}"

    with vaquero.span("batch_processing_workflow") as workflow_span:
        workflow_span.set_attribute("workflow_id", workflow_id)
        workflow_span.set_attribute("workflow_type", "batch_processing")
        workflow_span.set_attribute("batch_size", len(users))

        # Step 1: Validate all users
        with vaquero.span("batch_validation") as validation_span:
            validation_span.set_attribute("validation_strategy", "parallel")

            validation_tasks = [
                validate_single_user(user_data) for user_data in users
            ]

            try:
                validation_results = await asyncio.gather(*validation_tasks, return_exceptions=True)
                validation_span.set_attribute("validation_completed", len(validation_results))

                # Check for validation failures
                failed_validations = [
                    i for i, result in enumerate(validation_results)
                    if isinstance(result, Exception)
                ]

                if failed_validations:
                    validation_span.set_attribute("validation_failures", len(failed_validations))
                    raise ValueError(f"Validation failed for {len(failed_validations)} users")

            except Exception as e:
                validation_span.set_attribute("validation_successful", False)
                raise

        # Step 2: Process users in parallel batches
        with vaquero.span("parallel_processing") as processing_span:
            processing_span.set_attribute("processing_strategy", "parallel_batches")

            batch_size = 10
            user_batches = [users[i:i + batch_size] for i in range(0, len(users), batch_size)]

            batch_tasks = []
            for batch_num, batch in enumerate(user_batches):
                batch_task = process_user_batch_chunk(batch, batch_num)
                batch_tasks.append(batch_task)

            # Execute batches in parallel
            batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)

            # Analyze batch results
            successful_batches = len([r for r in batch_results if not isinstance(r, Exception)])
            processing_span.set_attribute("successful_batches", successful_batches)
            processing_span.set_attribute("total_batches", len(batch_results))

        # Step 3: Aggregate results
        with vaquero.span("result_aggregation") as aggregation_span:
            aggregation_span.set_attribute("aggregation_strategy", "consolidate_results")

            total_processed = sum(
                len(result.get("processed_users", []))
                for result in batch_results
                if not isinstance(result, Exception)
            )

            aggregation_span.set_attribute("total_users_processed", total_processed)
            aggregation_span.set_attribute("processing_successful", True)

        # Workflow completion
        workflow_span.set_attribute("workflow_completed", True)
        workflow_span.set_attribute("total_users_processed", total_processed)

        return {
            "workflow_id": workflow_id,
            "total_users": len(users),
            "processed_users": total_processed,
            "batch_results": len(batch_results),
            "status": "completed"
        }

async def process_user_batch_chunk(users: list, batch_num: int) -> dict:
    """Process a chunk of users with individual tracing."""
    with vaquero.span(f"batch_chunk_{batch_num}") as span:
        span.set_attribute("batch_number", batch_num)
        span.set_attribute("chunk_size", len(users))

        processed_users = []

        for user in users:
            with vaquero.span(f"process_user_{user['id']}") as user_span:
                user_span.set_attribute("user_id", user["id"])
                user_span.set_attribute("user_email", user["email"])

                # Process individual user
                processed_user = await process_single_user(user)
                processed_users.append(processed_user)

                user_span.set_attribute("processing_successful", True)

        span.set_attribute("users_processed", len(processed_users))
        return {"processed_users": processed_users, "batch_number": batch_num}
```

## 🎨 Advanced Workflow Patterns

### State Machine Workflows

```python
import vaquero
from enum import Enum

class WorkflowState(Enum):
    PENDING = "pending"
    VALIDATING = "validating"
    PROCESSING = "processing"
    COMPLETING = "completing"
    COMPLETED = "completed"
    FAILED = "failed"

@vaquero.trace(agent_name="state_machine_workflow")
class StateMachineWorkflow:
    """Workflow with explicit state management and transitions."""

    def __init__(self, workflow_id: str, initial_data: dict):
        self.workflow_id = workflow_id
        self.data = initial_data
        self.current_state = WorkflowState.PENDING
        self.state_history = []

    async def execute(self) -> dict:
        """Execute workflow with state transitions."""
        with vaquero.span("state_machine_execution") as workflow_span:
            workflow_span.set_attribute("workflow_id", self.workflow_id)
            workflow_span.set_attribute("initial_state", self.current_state.value)

            try:
                # State: PENDING → VALIDATING
                await self._transition_to_state(WorkflowState.VALIDATING)

                # State: VALIDATING → PROCESSING
                await self._transition_to_state(WorkflowState.PROCESSING)

                # State: PROCESSING → COMPLETING
                await self._transition_to_state(WorkflowState.COMPLETING)

                # State: COMPLETING → COMPLETED
                await self._transition_to_state(WorkflowState.COMPLETED)

                workflow_span.set_attribute("final_state", self.current_state.value)
                workflow_span.set_attribute("workflow_successful", True)

                return {
                    "workflow_id": self.workflow_id,
                    "final_state": self.current_state.value,
                    "state_transitions": len(self.state_history),
                    "status": "completed"
                }

            except Exception as e:
                # State: Any → FAILED
                await self._transition_to_state(WorkflowState.FAILED)
                workflow_span.set_attribute("workflow_successful", False)
                workflow_span.set_attribute("failure_state", self.current_state.value)
                raise

    async def _transition_to_state(self, new_state: WorkflowState):
        """Transition workflow to new state with tracing."""
        old_state = self.current_state

        with vaquero.span(f"state_transition_{old_state.value}_to_{new_state.value}") as span:
            span.set_attribute("from_state", old_state.value)
            span.set_attribute("to_state", new_state.value)
            span.set_attribute("workflow_id", self.workflow_id)

            # Execute state-specific logic
            await self._execute_state_logic(old_state, new_state)

            # Update state
            self.current_state = new_state

            # Record transition
            transition_record = {
                "from_state": old_state.value,
                "to_state": new_state.value,
                "timestamp": time.time(),
                "workflow_id": self.workflow_id
            }
            self.state_history.append(transition_record)

            span.set_attribute("transition_successful", True)

    async def _execute_state_logic(self, from_state: WorkflowState, to_state: WorkflowState):
        """Execute logic specific to state transition."""
        if to_state == WorkflowState.VALIDATING:
            await self._validate_workflow_data()
        elif to_state == WorkflowState.PROCESSING:
            await self._process_workflow_data()
        elif to_state == WorkflowState.COMPLETING:
            await self._complete_workflow()
        elif to_state == WorkflowState.COMPLETED:
            await self._finalize_workflow()
        elif to_state == WorkflowState.FAILED:
            await self._handle_workflow_failure()

    async def _validate_workflow_data(self):
        """Validate workflow input data."""
        with vaquero.span("data_validation") as span:
            # Validation logic
            if not self.data.get("required_field"):
                raise ValueError("Missing required field")

            span.set_attribute("validation_successful", True)

    async def _process_workflow_data(self):
        """Process workflow data."""
        with vaquero.span("data_processing") as span:
            # Processing logic
            result = await process_complex_data(self.data)
            span.set_attribute("processing_successful", True)

    async def _complete_workflow(self):
        """Complete workflow operations."""
        with vaquero.span("workflow_completion") as span:
            # Completion logic
            await save_workflow_results(self.workflow_id, self.data)
            span.set_attribute("completion_successful", True)

    async def _finalize_workflow(self):
        """Finalize workflow."""
        with vaquero.span("workflow_finalization") as span:
            # Finalization logic
            await notify_workflow_completion(self.workflow_id)
            span.set_attribute("finalization_successful", True)

    async def _handle_workflow_failure(self):
        """Handle workflow failure."""
        with vaquero.span("workflow_failure_handling") as span:
            # Failure handling logic
            await log_workflow_failure(self.workflow_id, self.data)
            span.set_attribute("failure_handled", True)
```

### Event-Driven Workflows

```python
import vaquero
import asyncio
from dataclasses import dataclass
from typing import Dict, List, Any

@dataclass
class WorkflowEvent:
    """Event in a workflow execution."""
    event_type: str
    payload: Dict[str, Any]
    timestamp: float
    source: str

@vaquero.trace(agent_name="event_driven_workflow")
class EventDrivenWorkflow:
    """Workflow driven by events with comprehensive tracing."""

    def __init__(self, workflow_id: str):
        self.workflow_id = workflow_id
        self.events_processed = []
        self.current_state = "initialized"

    async def start_workflow(self):
        """Start the event-driven workflow."""
        with vaquero.span("workflow_initialization") as span:
            span.set_attribute("workflow_id", self.workflow_id)
            span.set_attribute("workflow_type", "event_driven")

            # Initialize workflow state
            self.current_state = "running"
            span.set_attribute("initialization_successful", True)

            # Start event processing loop
            await self._process_events()

    async def _process_events(self):
        """Process workflow events."""
        while self.current_state == "running":
            with vaquero.span("event_processing_loop") as span:
                span.set_attribute("current_state", self.current_state)

                # Get next event (simplified)
                event = await self._get_next_event()

                if event:
                    await self._handle_event(event)
                    self.events_processed.append(event)
                    span.set_attribute("event_processed", True)
                else:
                    # No more events, workflow complete
                    self.current_state = "completed"
                    span.set_attribute("workflow_completed", True)
                    break

    async def _handle_event(self, event: WorkflowEvent):
        """Handle a specific workflow event."""
        with vaquero.span(f"event_handler_{event.event_type}") as span:
            span.set_attribute("event_type", event.event_type)
            span.set_attribute("event_source", event.source)
            span.set_attribute("event_timestamp", event.timestamp)

            # Route to appropriate handler
            if event.event_type == "user_action":
                await self._handle_user_action(event)
            elif event.event_type == "system_event":
                await self._handle_system_event(event)
            elif event.event_type == "external_trigger":
                await self._handle_external_trigger(event)
            else:
                span.set_attribute("event_handled", False)
                span.set_attribute("unknown_event_type", event.event_type)

    async def _handle_user_action(self, event: WorkflowEvent):
        """Handle user action events."""
        with vaquero.span("user_action_processing") as span:
            user_id = event.payload.get("user_id")
            action_type = event.payload.get("action_type")

            span.set_attribute("user_id", user_id)
            span.set_attribute("action_type", action_type)

            # Process user action
            result = await process_user_action(user_id, action_type)
            span.set_attribute("action_processed", True)

            # Generate follow-up events
            await self._generate_follow_up_events("user_action_completed", {
                "user_id": user_id,
                "original_action": action_type,
                "result": result
            })

    async def _handle_system_event(self, event: WorkflowEvent):
        """Handle system-generated events."""
        with vaquero.span("system_event_processing") as span:
            event_details = event.payload

            span.set_attribute("system_event_details", str(event_details))

            # Process system event
            await handle_system_event(event_details)
            span.set_attribute("system_event_handled", True)

    async def _handle_external_trigger(self, event: WorkflowEvent):
        """Handle external trigger events."""
        with vaquero.span("external_trigger_processing") as span:
            trigger_data = event.payload

            span.set_attribute("trigger_source", trigger_data.get("source"))

            # Process external trigger
            await process_external_trigger(trigger_data)
            span.set_attribute("trigger_processed", True)

    async def _generate_follow_up_events(self, event_type: str, payload: dict):
        """Generate follow-up events for workflow continuation."""
        with vaquero.span("follow_up_event_generation") as span:
            span.set_attribute("generated_event_type", event_type)

            follow_up_event = WorkflowEvent(
                event_type=event_type,
                payload=payload,
                timestamp=time.time(),
                source="workflow_engine"
            )

            # Queue follow-up event for processing
            await self._queue_event(follow_up_event)
            span.set_attribute("follow_up_event_queued", True)

    async def _get_next_event(self) -> WorkflowEvent | None:
        """Get next event from queue (simplified implementation)."""
        # In real implementation, this would poll an event queue
        # For demo purposes, simulate event generation
        await asyncio.sleep(0.1)  # Simulate polling delay

        # Generate a sample event
        if len(self.events_processed) < 3:  # Process 3 events for demo
            return WorkflowEvent(
                event_type="user_action",
                payload={"user_id": "user123", "action_type": "login"},
                timestamp=time.time(),
                source="user_interface"
            )

        return None

    async def _queue_event(self, event: WorkflowEvent):
        """Queue event for processing (simplified)."""
        # In real implementation, this would add to event queue
        pass
```

## 📊 Workflow Performance Monitoring

### Workflow Analytics

```python
import vaquero

@vaquero.trace(agent_name="workflow_analytics")
class WorkflowAnalytics:
    """Analyze workflow performance and patterns."""

    def __init__(self):
        self.workflow_metrics = []
        self.step_durations = {}
        self.failure_patterns = {}

    def record_workflow_completion(self, workflow_id: str, workflow_type: str,
                                 duration: float, success: bool, steps_completed: int):
        """Record workflow completion for analysis."""
        with vaquero.span("workflow_completion_recording") as span:
            span.set_attribute("workflow_id", workflow_id)
            span.set_attribute("workflow_type", workflow_type)
            span.set_attribute("duration_seconds", duration)
            span.set_attribute("success", success)
            span.set_attribute("steps_completed", steps_completed)

            metric = {
                "workflow_id": workflow_id,
                "workflow_type": workflow_type,
                "duration": duration,
                "success": success,
                "steps_completed": steps_completed,
                "timestamp": time.time()
            }

            self.workflow_metrics.append(metric)

            # Track success rates by type
            if workflow_type not in self.step_durations:
                self.step_durations[workflow_type] = []

            if success:
                self.step_durations[workflow_type].append(duration)

            span.set_attribute("metric_recorded", True)

    def analyze_workflow_performance(self) -> dict:
        """Analyze workflow performance patterns."""
        with vaquero.span("workflow_performance_analysis") as span:
            if not self.workflow_metrics:
                return {"error": "No workflow metrics available"}

            # Group by workflow type
            workflows_by_type = {}
            for metric in self.workflow_metrics:
                workflow_type = metric["workflow_type"]
                if workflow_type not in workflows_by_type:
                    workflows_by_type[workflow_type] = []
                workflows_by_type[workflow_type].append(metric)

            analysis = {
                "total_workflows": len(self.workflow_metrics),
                "workflow_types": {},
                "performance_insights": []
            }

            for workflow_type, workflows in workflows_by_type.items():
                successful_workflows = [w for w in workflows if w["success"]]
                avg_duration = sum(w["duration"] for w in successful_workflows) / len(successful_workflows) if successful_workflows else 0

                type_analysis = {
                    "count": len(workflows),
                    "successful": len(successful_workflows),
                    "success_rate": len(successful_workflows) / len(workflows) if workflows else 0,
                    "avg_duration": avg_duration,
                    "total_steps_completed": sum(w["steps_completed"] for w in workflows)
                }

                analysis["workflow_types"][workflow_type] = type_analysis

                # Generate insights
                if type_analysis["success_rate"] < 0.8:  # Less than 80% success rate
                    analysis["performance_insights"].append({
                        "type": "low_success_rate",
                        "workflow_type": workflow_type,
                        "current_rate": type_analysis["success_rate"],
                        "recommendation": f"Review {workflow_type} workflow for reliability issues"
                    })

                if avg_duration > 30:  # More than 30 seconds
                    analysis["performance_insights"].append({
                        "type": "slow_workflow",
                        "workflow_type": workflow_type,
                        "avg_duration": avg_duration,
                        "recommendation": f"Optimize {workflow_type} workflow for better performance"
                    })

            span.set_attribute("analysis_complete", True)
            span.set_attribute("insights_generated", len(analysis["performance_insights"]))

            return analysis
```

## 🎯 Best Practices

### 1. **Clear Workflow Boundaries**
```python
# ✅ Good - Clear workflow scope
@vaquero.trace(agent_name="user_registration_workflow")
async def register_user_workflow(user_data: dict):

# ❌ Avoid - Unclear scope
@vaquero.trace(agent_name="user_process")
async def handle_user_stuff(user_data: dict):
```

### 2. **State Transition Clarity**
```python
# ✅ Good - Explicit state transitions
await self._transition_to_state(WorkflowState.VALIDATING)
await self._transition_to_state(WorkflowState.PROCESSING)

# ❌ Avoid - Implicit state changes
# Just mutate self.state without clear transitions
```

### 3. **Error Context Preservation**
```python
# ✅ Good - Preserve error context through workflow
try:
    await self._execute_state_logic(old_state, new_state)
except Exception as e:
    with vaquero.span("state_transition_error") as span:
        span.set_attribute("failed_transition", f"{old_state.value}_to_{new_state.value}")
        span.set_attribute("error_context", "state_transition")
        raise
```

## 🚨 Common Issues

### "Workflow state confusion"
```python
# Track state transitions explicitly
@vaquero.trace(agent_name="state_tracker")
def track_state_changes():
    with vaquero.span("state_change") as span:
        old_state = self.current_state
        # State change logic
        self.current_state = new_state

        span.set_attribute("state_change", f"{old_state}_to_{new_state}")
        span.set_attribute("change_reason", "user_action")
```

### "Parallel execution tracking"
```python
# Track parallel operations clearly
@vaquero.trace(agent_name="parallel_executor")
async def execute_parallel_tasks(tasks: list):
    with vaquero.span("parallel_execution") as span:
        span.set_attribute("total_tasks", len(tasks))
        span.set_attribute("execution_strategy", "parallel")

        # Execute tasks in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Track results
        successful = len([r for r in results if not isinstance(r, Exception)])
        span.set_attribute("successful_tasks", successful)
        span.set_attribute("failed_tasks", len(tasks) - successful)
```

### "Workflow timeout handling"
```python
# Implement timeout handling
@vaquero.trace(agent_name="workflow_timeout_handler")
async def execute_with_timeout(workflow_func, timeout_seconds: int = 300):
    with vaquero.span("timeout_protected_execution") as span:
        span.set_attribute("timeout_seconds", timeout_seconds)

        try:
            result = await asyncio.wait_for(workflow_func(), timeout=timeout_seconds)
            span.set_attribute("execution_successful", True)
            return result
        except asyncio.TimeoutError:
            span.set_attribute("execution_successful", False)
            span.set_attribute("timeout_occurred", True)
            raise
```

## 🎉 You're Ready!

Workflow orchestration tracing gives you complete visibility into complex multi-step processes, state transitions, and parallel execution patterns. Combined with other tracing techniques, you get comprehensive observability across your entire application ecosystem.

Next, explore **[Custom Spans](./custom-spans.md)** for advanced tracing techniques or **[Performance Monitoring](./performance-monitoring.md)** for system-level observability.
