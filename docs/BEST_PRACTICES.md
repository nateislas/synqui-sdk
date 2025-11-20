# Best Practices

## ✅ Do

- **Use project names** - `vaquero.init(project_api_key="key", project_name="my-app")`
- **Register graph architecture** - `handler.set_graph_architecture()` for LangGraph workflows
- **Start chat sessions** - Use `start_chat_session()` for conversational agents
- **Add meaningful context** - Pass `parent_context` to handlers for better trace organization
- **Handle errors gracefully** - SDK captures exceptions automatically

## ❌ Avoid

- **Sensitive data** - Don't log passwords, keys, or PII in attributes
- **Forgetting to pass handlers** - Always include handlers in callback lists
- **Blocking operations in async code** - Use proper async patterns

