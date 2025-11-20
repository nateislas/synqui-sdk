# Advanced Usage

## Session Management

### Creating and Managing Sessions
```python
# Start a new chat session
session = vaquero.start_chat_session(
    name="user-123-session",
    session_type="chat",
    timeout_minutes=30,
    max_duration_minutes=240,
    metadata={"user_id": "123", "environment": "production"}
)

# Session automatically groups related traces
# Use the same session for multiple invocations
handler = VaqueroLangGraphHandler(session=session)
```

### Session Lifecycle
```python
# Sessions automatically timeout after inactivity
# Manually end a session if needed
if session:
    session.end_session("user_logout")
```

## Graph Architecture Registration

### Capture Your Agent Structure
```python
# Register graph architecture for visualization
handler.set_graph_architecture(
    graph=app.get_graph(),
    graph_name="CustomerSupportAgent"
)

# This enables:
# - Automatic node/edge extraction
# - Architecture visualization in dashboard
# - Version tracking of graph changes
```

## Custom Configuration

### Advanced Setup
```python
import vaquero
import os

vaquero.init(
    project_name="my-project",
    project_api_key=os.getenv("VAQUERO_PROJECT_API_KEY"),
    environment=os.getenv("VAQUERO_ENVIRONMENT", "development")
)
```

### Environment Variables

**Configuration via Environment**
```bash
VAQUERO_PROJECT_API_KEY=cf_your-api-key
VAQUERO_PROJECT_NAME=my-project
VAQUERO_ENVIRONMENT=development
```

```python
import vaquero
import os

vaquero.init(
    project_name=os.getenv("VAQUERO_PROJECT_NAME"),
    project_api_key=os.getenv("VAQUERO_PROJECT_API_KEY"),
    environment=os.getenv("VAQUERO_ENVIRONMENT", "development")
)
```

### Production Configuration
```python
import vaquero
import os

vaquero.init(
    project_name="production-app",
    project_api_key=os.getenv("VAQUERO_PROJECT_API_KEY"),
    environment="production"
)
```

In production, traces are batched and sent asynchronously to avoid blocking your application.

