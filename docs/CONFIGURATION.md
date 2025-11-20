# Configuration Reference

## Initialization Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `project_api_key` | `str` | **Yes** | - | Your Vaquero API key (starts with `cf_`) |
| `project_name` | `str` | No | `None` | Project name (recommended, auto-resolves project ID) |
| `project_id` | `str` | No | `None` | Project ID (used if project_name not provided) |
| `endpoint` | `str` | No | `"https://api.vaquero.app"` | Vaquero API endpoint |
| `environment` | `str` | No | `"development"` | Environment: `"development"`, `"staging"`, or `"production"` |

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `VAQUERO_PROJECT_API_KEY` | Your project API key | `cf_...` |
| `VAQUERO_PROJECT_NAME` | Name of your project | `my-project` |
| `VAQUERO_PROJECT_ID` | Project ID (optional) | `uuid-here` |
| `VAQUERO_ENVIRONMENT` | Environment name | `development`, `staging`, or `production` |

## Environment-Specific Settings

The SDK automatically adjusts batch sizes and flush intervals based on environment:

```python
# Development (faster feedback)
vaquero.init(
    project_api_key="key",
    project_name="my-app",
    environment="development"
)
# → batch_size=10, flush_interval=2.0s

# Staging (balanced)
vaquero.init(
    project_api_key="key",
    project_name="my-app",
    environment="staging"
)
# → batch_size=50, flush_interval=3.0s

# Production (optimized for throughput)
vaquero.init(
    project_api_key="key",
    project_name="my-app",
    environment="production"
)
# → batch_size=100, flush_interval=5.0s
```

