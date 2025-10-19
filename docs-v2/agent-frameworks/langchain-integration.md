# LangChain Integration

Seamlessly integrate Vaquero observability into your LangChain applications. This is the primary use case for Vaquero - providing comprehensive tracing for AI agent workflows.

## Quick Start

### 1. Install Dependencies
```bash
pip install vaquero-sdk langchain langchain-openai
```

### 2. Initialize Vaquero
```python title="SDK Initialization"
import vaquero

# Initialize with your API key
vaquero.init(api_key="cf_your-project-key-here")
```

### 3. Add Callback Handler
```python title="Handler Setup"
from vaquero.langchain import get_vaquero_handler

# Get the callback handler
handler = get_vaquero_handler(parent_context={"team": "ai_research"})

# Use with any LangChain chain
chain.invoke(
    {"input": "Your query here"},
    config={"callbacks": [handler]}
)
```

That's it! Your LangChain operations are now automatically traced.

## Integration Patterns

### LCEL Chain Tracing
```python title="Text Processing Chain"
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from vaquero.langchain import get_vaquero_handler

# Initialize Vaquero
vaquero.init(api_key="your-key")

# Create callback handler
handler = get_vaquero_handler(parent_context={"workflow": "text_processing"})

# Build your chain
llm = ChatOpenAI(model="gpt-4", temperature=0)
prompt = ChatPromptTemplate.from_template("Summarize: {text}")
parser = StrOutputParser()

chain = prompt | llm | parser

# Execute with tracing
result = chain.invoke(
    {"text": "Your long text here..."},
    config={"callbacks": [handler]}
)

# Traces will show:
# - Prompt template rendering
# - LLM call with tokens, cost, timing
# - Output parsing
# - Total chain execution time
```

### Agent Tracing
```python title="Research Agent"
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate
from vaquero.langchain import get_vaquero_handler

# Initialize Vaquero
vaquero.init(api_key="your-key")

# Create callback handler
handler = get_vaquero_handler(parent_context={"agent_type": "research_assistant"})

# Build agent (example)
llm = ChatOpenAI(model="gpt-4", temperature=0)
tools = [your_tools]  # Your custom tools
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful research assistant."),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}")
])

agent = create_tool_calling_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools)

# Execute with comprehensive tracing
result = agent_executor.invoke(
    {"input": "Research the latest AI trends"},
    config={"callbacks": [handler]}
)

# Traces will capture:
# - Agent reasoning steps
# - Tool calls and responses
# - LLM interactions
# - Error handling and retries
# - Final response generation
```

### RAG Application Tracing
```python title="RAG System"
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_community.vectorstores import FAISS
from vaquero.langchain import get_vaquero_handler

# Initialize Vaquero
vaquero.init(api_key="your-key")

# Create callback handler
handler = get_vaquero_handler(parent_context={"application": "rag_system"})

# Build RAG chain
embeddings = OpenAIEmbeddings()
vectorstore = FAISS.from_texts(["Your documents here"], embeddings)
retriever = vectorstore.as_retriever()

llm = ChatOpenAI(model="gpt-4", temperature=0)
prompt = ChatPromptTemplate.from_template(
    "Context: {context}\nQuestion: {question}\nAnswer:"
)

rag_chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

# Execute with full observability
result = rag_chain.invoke(
    "What are the key findings?",
    config={"callbacks": [handler]}
)

# Traces will show:
# - Document retrieval process
# - Embedding generation and similarity search
# - Prompt construction
# - LLM generation with tokens and cost
# - Response parsing and formatting
```

## Advanced Configuration

### Custom Parent Context
```python title="Structured Context"
# Add structured context for better organization
handler = get_vaquero_handler(parent_context={
    "team": "ml_engineering",
    "project": "customer_support_bot",
    "version": "2.1.0",
    "environment": "production"
})
```

### Multiple Callback Handlers
```python title="Multiple Handlers"
# Use multiple handlers for different purposes
from vaquero.langchain import get_vaquero_handler

# Primary observability handler
primary_handler = get_vaquero_handler(parent_context={"team": "engineering"})

# Secondary handler for specific metrics
secondary_handler = get_vaquero_handler(
    parent_context={"component": "llm_chain"},
    config={"capture_inputs": True, "capture_outputs": True}
)

# Use both handlers
chain.invoke(
    {"input": "Your query"},
    config={"callbacks": [primary_handler, secondary_handler]}
)
```

### Conditional Tracing
```python title="Environment-Based Tracing"
# Enable tracing only for certain conditions
import os
from vaquero.langchain import get_vaquero_handler

# Only trace in development or for specific users
should_trace = (
    os.getenv("ENVIRONMENT") == "development" or
    "admin" in user_context.get("role", "")
)

if should_trace:
    handler = get_vaquero_handler()
    chain.invoke(input, config={"callbacks": [handler]})
else:
    chain.invoke(input)  # No tracing overhead
```

## What Gets Traced

### LLM Operations
- **Model**: Which model was called (gpt-4, gpt-3.5-turbo, etc.)
- **Tokens**: Input, output, and total token counts
- **Cost**: Estimated cost based on token usage
- **Duration**: Time spent in LLM call
- **Temperature**: Model parameters used
- **Messages**: System, user, and assistant messages (configurable)

### Chain Operations
- **Chain Structure**: Which components are connected
- **Execution Flow**: Step-by-step execution path
- **Input/Output**: Data flowing between components
- **Timing**: Duration of each step
- **Errors**: Any failures in the chain

### Agent Operations
- **Reasoning Steps**: Agent's thought process
- **Tool Selection**: Which tools are chosen and why
- **Tool Execution**: Tool calls and responses
- **Final Response**: Agent's final answer
- **Iterations**: Multiple reasoning cycles

## 🎯 Best Practices

### ✅ Do
```python
# ✅ Good: Descriptive parent context
handler = get_vaquero_handler(parent_context={
    "team": "customer_success",
    "feature": "support_chatbot",
    "model": "gpt-4"
})

# ✅ Good: Use appropriate callback placement
# For entire application
app_handler = get_vaquero_handler(parent_context={"app": "support_system"})

# For specific workflows
workflow_handler = get_vaquero_handler(parent_context={"workflow": "user_query"})
```

### ❌ Avoid
```python
# ❌ Bad: Generic context
handler = get_vaquero_handler()  # No context for organization

# ❌ Bad: Too much detail in context
handler = get_vaquero_handler(parent_context={
    "user_id": "123",  # Too specific for general tracing
    "session_id": "abc",  # Use tags instead
    "request_id": "xyz"   # Use span attributes
})
```

### Performance Optimization
```python
# ✅ Good: Balanced configuration
handler = get_vaquero_handler(
    parent_context={"team": "engineering"},
    config={
        "capture_inputs": True,    # For debugging
        "capture_outputs": True,   # For verification
        "capture_tokens": True,    # For cost tracking
        "batch_size": 50          # Smaller batches for responsiveness
    }
)

# ✅ Good: Environment-specific settings
if os.getenv("ENVIRONMENT") == "production":
    handler = get_vaquero_handler(
        parent_context={"env": "prod"},
        config={"capture_inputs": False}  # Privacy protection
    )
```

## 🔍 Debugging LangChain Issues

### Enable Debug Logging
```python
import logging
import vaquero

# Enable detailed logging
logging.basicConfig(level=logging.DEBUG)

# Initialize with debug enabled
vaquero.init(api_key="your-key", debug=True)

# Now you'll see:
# - Chain execution details
# - Tool call information
# - LLM interaction logs
# - Error context
```

### Inspect Chain Execution
```python
# Add custom logging to understand execution
@vaquero.trace("debug_chain")
def debug_langchain_execution():
    from vaquero.langchain import get_vaquero_handler

    handler = get_vaquero_handler()

    # Execute chain with tracing
    result = chain.invoke(
        {"input": "Test query"},
        config={"callbacks": [handler]}
    )

    # Check what was captured
    sdk = vaquero.get_default_sdk()
    stats = sdk.get_stats()
    print(f"Traces captured: {stats.get('traces_sent', 0)}")

    return result
```

## 📈 Monitoring LangChain Performance

### Performance Metrics
```python
# Monitor LangChain performance patterns
@vaquero.trace("performance_monitor")
def analyze_langchain_performance():
    sdk = vaquero.get_default_sdk()
    stats = sdk.get_stats()

    # Analyze performance metrics
    if stats.get("traces_sent", 0) > 100:
        avg_duration = calculate_average_duration(stats)
        error_rate = calculate_error_rate(stats)

        print(f"Average chain duration: {avg_duration}ms")
        print(f"Error rate: {error_rate}%")

        # Adjust configuration if needed
        if error_rate > 0.05:  # 5% error rate
            print("High error rate detected - consider retry logic")
```

### Cost Tracking
```python
# Track LLM costs across LangChain usage
@vaquero.trace("cost_tracker")
def track_llm_costs():
    # Costs are automatically captured in traces
    # View in dashboard under "Cost Analytics"

    # Or access programmatically
    traces = get_recent_traces()
    total_cost = sum(trace.get("cost", 0) for trace in traces)

    print(f"Total LLM cost this month: ${total_cost:.2f}")
```

## 🚨 Common Issues

### "Handler not initialized" Error
```python
# ✅ Correct
import vaquero
vaquero.init(api_key="your-key")  # Initialize first

handler = get_vaquero_handler()

# ❌ Wrong
handler = get_vaquero_handler()  # Error: SDK not initialized
import vaquero
vaquero.init(api_key="your-key")
```

### Missing LLM Traces
```python
# ✅ Correct - Enable auto-instrumentation
vaquero.init(api_key="your-key", auto_instrument_llm=True)

# ✅ Correct - Manual tracing for non-auto instrumented models
from vaquero.langchain import get_vaquero_handler

handler = get_vaquero_handler()
llm = ChatOpenAI(model="gpt-4", callbacks=[handler])  # Pass handler to LLM
```

### Performance Overhead
```python
# ✅ Good: Optimize for production
handler = get_vaquero_handler(
    config={
        "batch_size": 100,        # Larger batches
        "capture_inputs": False,  # Reduce data volume
        "capture_outputs": False  # Reduce data volume
    }
)

# ✅ Good: Conditional tracing for production
if os.getenv("ENVIRONMENT") == "development":
    handler = get_vaquero_handler()
else:
    handler = None  # No tracing overhead
```

## 🎯 Next Steps

Now that you have LangChain integration working:

1. **[→ Dashboard Analysis](../observability-platform/dashboard-overview.md)** - Explore your trace data
2. **[→ Custom Agents](./custom-agents.md)** - Build agents with Vaquero observability
3. **[→ Performance Optimization](../advanced-usage/performance-optimization.md)** - Optimize your AI workflows

## 🆘 Need Help?

- **Examples**: [LangChain Examples](../examples/langchain-examples/)
- **Community**: [Discord](https://discord.gg/vaquero)
- **Support**: support@vaquero.app

---

**[← Back to Agent Frameworks](../index.md#agent-frameworks)** | **[→ Next: Framework Comparison](./framework-comparison.md)**
