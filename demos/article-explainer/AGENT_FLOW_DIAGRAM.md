# Article Explainer: Agent Flow Diagram

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER INTERFACE                            │
│                    (Streamlit Web App)                          │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                    DOCUMENT PROCESSING                          │
│  PDF Upload → ContentLoader → Text Extraction → Chunking       │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                    LANGGRAPH SWARM                             │
│                    (Default: Explainer)                        │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                      AGENT SWARM                                │
│                                                                 │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐        │
│  │  EXPLAINER  │◄──►│  DEVELOPER  │◄──►│ SUMMARIZER  │        │
│  │  (Default)  │    │             │    │             │        │
│  └─────────────┘    └─────────────┘    └─────────────┘        │
│         ▲                   ▲                   ▲             │
│         │                   │                   │             │
│         ▼                   ▼                   ▼             │
│  ┌─────────────┐    ┌─────────────┐                          │
│  │   ANALOGY   │◄──►│VULNERABILITY│                          │
│  │   CREATOR   │    │   EXPERT    │                          │
│  └─────────────┘    └─────────────┘                          │
└─────────────────────────────────────────────────────────────────┘
```

## Agent Specialization Matrix

```
┌─────────────────┬──────────────┬──────────────┬──────────────┬──────────────┐
│     AGENT       │   PRIMARY    │   OUTPUT     │   HANDOFF    │   USE CASE   │
│                 │   EXPERTISE  │    STYLE     │  CAPABILITY  │              │
├─────────────────┼──────────────┼──────────────┼──────────────┼──────────────┤
│   EXPLAINER     │ Educational  │ Structured   │ All Agents   │ "Explain how │
│   (Default)     │ Explanations │ Step-by-step │              │  this works" │
├─────────────────┼──────────────┼──────────────┼──────────────┼──────────────┤
│   DEVELOPER     │ Code Examples│ Technical    │ All Agents   │ "Show me the │
│                 │ & Technical  │ Implementation│              │  code for X" │
├─────────────────┼──────────────┼──────────────┼──────────────┼──────────────┤
│   SUMMARIZER    │ Key Points   │ Concise      │ All Agents   │ "Give me a   │
│                 │ & TL;DR      │ Bullet Points│              │  summary"    │
├─────────────────┼──────────────┼──────────────┼──────────────┼──────────────┤
│ ANALOGY CREATOR │ Metaphors    │ Relatable    │ All Agents   │ "Explain like│
│                 │ & Analogies  │ Comparisons  │              │  I'm 5"      │
├─────────────────┼──────────────┼──────────────┼──────────────┼──────────────┤
│VULNERABILITY    │ Critical     │ Balanced     │ All Agents   │ "What are the│
│EXPERT           │ Analysis     │ Critique     │              │  weaknesses"│
└─────────────────┴──────────────┴──────────────┴──────────────┴──────────────┘
```

## Document Processing Pipeline

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   PDF FILE  │───►│ContentLoader│───►│Text Splitter│───►│   Chunks    │
│   Upload    │    │             │    │ (1000 chars)│    │ (Max 10)    │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
                                                              │
                                                              ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Response  │◄───│   Agent     │◄───│   Swarm     │◄───│   Context   │
│  Generation │    │ Processing  │    │ Coordination│    │ Injection   │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

## Agent Handoff Decision Tree

```
                    USER QUERY
                         │
                         ▼
                ┌─────────────────┐
                │   EXPLAINER     │
                │   (Default)     │
                └─────────┬───────┘
                          │
                    ┌─────▼─────┐
                    │ Can I     │
                    │ handle    │
                    │ this?     │
                    └─────┬─────┘
                          │
                    ┌─────▼─────┐
                    │    YES    │    NO
                    │           │
                    ▼           ▼
            ┌─────────────┐ ┌─────────────┐
            │  RESPOND    │ │  HANDOFF    │
            │  DIRECTLY   │ │  TO OTHER   │
            └─────────────┘ │   AGENT     │
                            └─────────────┘
                                     │
                            ┌────────▼────────┐
                            │                 │
                            ▼                 ▼
                    ┌─────────────┐   ┌─────────────┐
                    │  DEVELOPER  │   │ SUMMARIZER  │
                    │             │   │             │
                    └─────────────┘   └─────────────┘
                            │                 │
                            ▼                 ▼
                    ┌─────────────┐   ┌─────────────┐
                    │   ANALOGY   │   │VULNERABILITY│
                    │   CREATOR   │   │   EXPERT    │
                    └─────────────┘   └─────────────┘
```

## Conversation Flow Example

```
User: "Explain how machine learning works in this paper"

┌─────────────────────────────────────────────────────────────────┐
│ 1. EXPLAINER receives query                                     │
│ 2. Analyzes: "This needs educational explanation"              │
│ 3. Provides step-by-step breakdown                             │
│ 4. Decides: "User might want code examples"                    │
│ 5. Handoff to DEVELOPER                                        │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│ 1. DEVELOPER receives context + query                          │
│ 2. Analyzes: "User wants practical implementation"             │
│ 3. Provides code examples                                      │
│ 4. Decides: "User might want a summary"                       │
│ 5. Handoff to SUMMARIZER                                       │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│ 1. SUMMARIZER receives full context                            │
│ 2. Analyzes: "User wants key takeaways"                       │
│ 3. Provides concise summary                                   │
│ 4. Completes response                                          │
└─────────────────────────────────────────────────────────────────┘
```

## Vaquero Tracing Opportunities

### High-Value Trace Scenarios

1. **Multi-Agent Handoffs**
   - Agent decision-making process
   - Handoff tool invocations
   - Context preservation across agents

2. **Document Processing**
   - PDF upload and processing
   - Text extraction and chunking
   - Context injection into agent state

3. **Collaborative Responses**
   - Multiple agents contributing to single response
   - Agent coordination and communication
   - Final response assembly

4. **Error Handling**
   - Agent failure recovery
   - Exception handling across agents
   - Graceful degradation

5. **User Interaction Patterns**
   - Query routing and agent selection
   - Follow-up question handling
   - Session state management

This architecture provides rich opportunities for testing Vaquero's ability to trace complex multi-agent workflows, document processing pipelines, and real-world user interactions.
