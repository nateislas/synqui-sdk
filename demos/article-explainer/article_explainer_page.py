import streamlit as st
import os
import tempfile
import logging
import sys
import signal
from typing import Optional
from streamlit_pdf_viewer import pdf_viewer
from dotenv import load_dotenv
from langchain_core.messages import AIMessage
import json as _json

from explainer.graph import app
from explainer.service.content_loader import ContentLoader
from langchain_core.messages import HumanMessage
from langchain_core.callbacks import UsageMetadataCallbackHandler
from langgraph_swarm import SwarmState

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

# Get logger and ensure it uses the root logger's handlers
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Add handlers to the specific logger to ensure it writes to app.log
if not logger.handlers:
    logger.addHandler(logging.FileHandler('app.log'))
    logger.addHandler(logging.StreamHandler())

# Load environment variables
load_dotenv()

# Initialize Synqui SDK with error handling
try:
    import synqui
    SYNQUI_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Synqui SDK not available: {e}")
    SYNQUI_AVAILABLE = False

# LangGraph handler import (new API)
try:
    from synqui.langgraph import SynquiLangGraphHandler
    SYNQUI_LANGGRAPH_AVAILABLE = True
except Exception:
    SYNQUI_LANGGRAPH_AVAILABLE = False


def _process_pdf_upload(uploaded_file) -> Optional[str]:
    """Process uploaded PDF and return document content"""
    if uploaded_file is None:
        return None

    temp_dir = tempfile.gettempdir()
    temp_file_path = os.path.join(temp_dir, f"uploaded_{uploaded_file.name}")

    with open(temp_file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    loader = ContentLoader()
    try:
        document_content = loader.get_text(temp_file_path, max_chunks=10)
        return document_content
    except Exception as e:
        st.error(f"Error processing PDF: {str(e)}")
        return None
    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)


def _shutdown_app():
    """Shutdown the Streamlit application"""
    st.warning("🛑 Shutting down the application...")
    
    # Clean up any active Synqui sessions
    if "synqui_chat_session" in st.session_state and st.session_state.synqui_chat_session:
        try:
            st.session_state.synqui_chat_session.end_session("user_shutdown")
            st.info("🔧 Synqui session ended gracefully")
        except Exception as e:
            st.warning(f"Warning: Could not end Synqui session: {e}")
    
    # Clear session state
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    
    st.stop()
    # Force exit the process (equivalent to Ctrl+C)
    os._exit(0)


def main():
    st.set_page_config(page_title="Article Explainer", page_icon="📚", layout="wide")

    # Initialize Synqui SDK
    if "synqui_initialized" not in st.session_state:
        if SYNQUI_AVAILABLE:
            try:
                synqui.init(
                    project_name=os.getenv('SYNQUI_PROJECT_NAME', "article-explainer"),
                    project_api_key=os.getenv('SYNQUI_PROJECT_API_KEY'),
                    endpoint=os.getenv('SYNQUI_ENDPOINT', 'http://localhost:8000'),
                    environment=os.getenv('SYNQUI_ENVIRONMENT', os.getenv('SYNQUI_MODE', 'development'))
                )
                st.session_state.synqui_initialized = True

                # Create fallback handler if not already created
                if "synqui_handler" not in st.session_state:
                    if SYNQUI_AVAILABLE and SYNQUI_LANGGRAPH_AVAILABLE:
                        st.session_state.synqui_handler = SynquiLangGraphHandler()
                    else:
                        st.session_state.synqui_handler = None
            except Exception as e:
                st.warning(f"Synqui initialization failed: {e}")
                st.session_state.synqui_initialized = False
        else:
            st.info("Synqui SDK not available - running without observability")
            st.session_state.synqui_initialized = False

    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "document_content" not in st.session_state:
        st.session_state.document_content = None
    if "agent_state" not in st.session_state:
        st.session_state.agent_state = None
    if "uploaded_pdf_bytes" not in st.session_state:
        st.session_state.uploaded_pdf_bytes = None

    with st.sidebar:
        st.header("📚 Article Explainer")
        
        # Stop button at the top of the sidebar
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("🛑 Stop App", type="secondary", help="Shutdown the application"):
                _shutdown_app()
        with col2:
            st.markdown("")  # Empty column for spacing
        
        st.divider()  # Visual separator
        
        uploaded_file = st.file_uploader(type="pdf", label="Document Uploader")

        if uploaded_file is not None:
            # Check if this is a new document (different from current)
            is_new_document = (st.session_state.get('current_document_name') != uploaded_file.name)

            if st.session_state.document_content is None or is_new_document:
                with st.spinner("Processing PDF..."):
                    st.session_state.uploaded_pdf_bytes = uploaded_file.read()

                    document_content = _process_pdf_upload(uploaded_file)
                    if document_content:
                        st.session_state.document_content = document_content
                        st.toast("PDF processed with success")

                        context_message = f"[Document content] : {document_content}"
                        st.session_state.agent_state = SwarmState(
                            messages=[{"role": "user", "content": context_message}],
                        )
                        
                        # Document processed successfully

                        if not st.session_state.messages:
                            st.session_state.messages = [
                                {
                                    "role": "assistant",
                                    "content": "Hello, what can I help you with?",
                                }
                            ]

                        # Create or update Synqui chat session
                        if st.session_state.synqui_initialized and SYNQUI_AVAILABLE:
                            try:
                                # Store document name for session timeout handling
                                st.session_state.current_document_name = uploaded_file.name

                                # End previous session if this is a new document
                                if (is_new_document and
                                    "synqui_chat_session" in st.session_state and
                                    st.session_state.synqui_chat_session):
                                    old_session = st.session_state.synqui_chat_session
                                    old_session.end_session("new_document")
                                    st.info(f"🕒 Previous session ended (new document uploaded)")

                                # Create a new chat session for this document
                                session_name = f"pdf_chat_{uploaded_file.name}"
                                synqui_session = synqui.start_chat_session(
                                    name=session_name,
                                    session_type="chat",
                                    timeout_minutes=30,
                                    metadata={
                                        "document_name": uploaded_file.name,
                                        "document_type": "pdf",
                                        "document_size": len(uploaded_file.getbuffer())
                                    }
                                )

                                # Update handler to use session-aware version (automatic session management)
                                if SYNQUI_LANGGRAPH_AVAILABLE:
                                    st.session_state.synqui_handler = SynquiLangGraphHandler(session=synqui_session)
                                else:
                                    st.session_state.synqui_handler = None
                                st.session_state.synqui_chat_session = synqui_session
                                
                                # Debug: Log session creation
                                st.info(f"🔧 Debug: Created session-aware handler for session {synqui_session.session_id}")

                                if is_new_document:
                                    st.info(f"🕒 New chat session created: {session_name} (30min timeout)")
                                else:
                                    st.info(f"🕒 Chat session created: {session_name} (30min timeout)")

                            except Exception as e:
                                st.warning(f"Synqui session creation failed: {e}")

    if st.session_state.document_content is not None:
        with st.expander("📖 View document", expanded=False):
            if st.session_state.uploaded_pdf_bytes:
                pdf_viewer(st.session_state.uploaded_pdf_bytes, height=600)

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if prompt := st.chat_input("Ask me anything about the document..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    try:
                        st.session_state.agent_state["messages"].append(
                            HumanMessage(content=prompt)
                        )

                        # Handle user message in session
                        if (st.session_state.synqui_initialized and
                            SYNQUI_AVAILABLE and
                            "synqui_handler" in st.session_state and
                            hasattr(st.session_state.synqui_handler, 'handle_user_message')):
                            st.session_state.synqui_handler.handle_user_message(prompt)

                        # Create Synqui configuration for LangGraph
                        if st.session_state.synqui_initialized and SYNQUI_AVAILABLE:
                            # Debug: Log handler and session info
                            handler = st.session_state.synqui_handler
                            session = st.session_state.get('synqui_chat_session')
                            if session:
                                st.info(f"🔧 Debug: Using session {session.session_id} with handler {type(handler).__name__}")
                            
                            # Set graph architecture on handler (extracts nodes/edges automatically)
                            handler.set_graph_architecture(
                                graph=app.get_graph(),
                                graph_name="ArticleExplainer"
                            )
                            
                            # Create Synqui configuration with usage handler and invoke LangGraph
                            usage_handler = UsageMetadataCallbackHandler()
                            config = {"callbacks": [handler, usage_handler], "configurable": {"synqui_handler": handler}}
                            
                            # Add detailed logging for agent execution
                            st.info(f"🚀 Starting LangGraph execution with {len(st.session_state.agent_state['messages'])} messages")
                            st.info(f"🔧 LangGraph app nodes: {list(app.get_graph().nodes.keys())}")
                            
                            # COMPREHENSIVE LOGGING FOR DEBUGGING
                            logger.info("=" * 80)
                            logger.info("🚀 LANGGRAPH EXECUTION START")
                            logger.info(f"🔧 Input state: {st.session_state.agent_state}")
                            logger.info(f"🔧 Config: {config}")
                            logger.info(f"🔧 Handler type: {type(handler)}")
                            logger.info(f"🔧 Handler session: {handler.session.session_id if handler.session else 'None'}")
                            logger.info(f"🔧 Available graph nodes: {list(app.get_graph().nodes.keys())}")
                            logger.info(f"🔧 Graph edges: {list(app.get_graph().edges)}")
                            
                            # Log the graph structure in detail
                            graph = app.get_graph()
                            logger.info("🔧 Graph structure details:")
                            for node_name, node_data in graph.nodes.items():
                                logger.info(f"  - Node: {node_name}, Type: {type(node_data)}")
                                if hasattr(node_data, 'func'):
                                    logger.info(f"    Function: {node_data.func.__name__ if hasattr(node_data.func, '__name__') else 'Unknown'}")
                            
                            response_state = app.invoke(st.session_state.agent_state, config=config)
                            
                            # Log the response
                            logger.info("✅ LANGGRAPH EXECUTION COMPLETED")
                            logger.info(f"🔧 Response state: {response_state}")
                            logger.info(f"🔧 Response messages count: {len(response_state['messages'])}")
                            if response_state['messages']:
                                for i, msg in enumerate(response_state['messages']):
                                    logger.info(f"🔧 Message {i}: {type(msg).__name__} - {str(msg.content)[:100]}...")
                            logger.info("=" * 80)
                            
                            st.info(f"✅ LangGraph execution completed. Response messages: {len(response_state['messages'])}")
                            if response_state['messages']:
                                last_message = response_state['messages'][-1]
                                st.info(f"📝 Last message type: {type(last_message).__name__}")
                                # Reduced logging to avoid cluttering the debug output
                                # if hasattr(last_message, 'content'):
                                #     st.info(f"📝 Last message content preview: {str(last_message.content)[:100]}...")
                        else:
                            st.info("⚠️ Running without Synqui observability")
                            
                            # Log even without Synqui
                            logger.info("=" * 80)
                            logger.info("🚀 LANGGRAPH EXECUTION START (NO SYNQUI)")
                            logger.info(f"🔧 Input state: {st.session_state.agent_state}")
                            logger.info(f"🔧 Available graph nodes: {list(app.get_graph().nodes.keys())}")
                            
                            response_state = app.invoke(st.session_state.agent_state)
                            
                            logger.info("✅ LANGGRAPH EXECUTION COMPLETED (NO SYNQUI)")
                            logger.info(f"🔧 Response state: {response_state}")
                            logger.info("=" * 80)

                        st.session_state.agent_state = response_state

                        # Choose the last non-empty AI message and normalize its content for display

                        def _to_display_text(_content):
                            if isinstance(_content, str):
                                return _content
                            if isinstance(_content, list):
                                parts = []
                                for p in _content:
                                    if isinstance(p, dict) and "text" in p:
                                        parts.append(p["text"])
                                    else:
                                        parts.append(str(p))
                                return "\n".join(parts)
                            if isinstance(_content, dict):
                                try:
                                    return "```json\n" + _json.dumps(_content, ensure_ascii=False, indent=2) + "\n```"
                                except Exception:
                                    return str(_content)
                            return str(_content)

                        def _last_nonempty_ai_text(_messages):
                            """Pick the most useful final assistant message.
                            Preference order:
                              1) Latest non-empty AIMessage from a non-developer agent (explainer, summarizer, analogy_creator, vulnerability_expert)
                              2) Latest non-empty AIMessage from any agent
                              3) Fallback to any AIMessage (may be empty)
                            Tool-call-only AI turns are skipped.
                            """
                            preferred_agents = {"explainer", "summarizer", "analogy_creator", "vulnerability_expert"}

                            # Pass 1: non-developer with substantial content
                            for m in reversed(_messages):
                                if isinstance(m, AIMessage):
                                    if getattr(m, "tool_calls", None):
                                        continue
                                    agent_name = getattr(m, "name", None)
                                    txt = _to_display_text(getattr(m, "content", ""))
                                    if agent_name in preferred_agents and txt and txt.strip():
                                        # Heuristic: avoid short clarifying questions
                                        if len(txt.strip()) >= 40:
                                            return txt

                            # Pass 2: any non-empty AIMessage, newest first
                            for m in reversed(_messages):
                                if isinstance(m, AIMessage):
                                    if getattr(m, "tool_calls", None):
                                        continue
                                    txt = _to_display_text(getattr(m, "content", ""))
                                    if txt and txt.strip():
                                        return txt

                            # Pass 3: fallback
                            for m in reversed(_messages):
                                if isinstance(m, AIMessage):
                                    return _to_display_text(getattr(m, "content", ""))
                            return "(no assistant content)"

                        _msgs = response_state["messages"]
                        _display_text = _last_nonempty_ai_text(_msgs)

                        st.markdown(_display_text)

                        st.session_state.messages.append(
                            {"role": "assistant", "content": _display_text}
                        )

                        # Log a short preview of the assistant response to app.log
                        try:
                            logger.info(f"📝 Last message content: {_display_text[:20]}")
                        except Exception:
                            pass

                    except Exception as e:
                        error_message = f"Sorry, I encountered an error: {str(e)}"
                        st.error(error_message)
                        st.session_state.messages.append(
                            {"role": "assistant", "content": error_message}
                        )

    else:

        with st.expander("ℹ️ How to use this app"):
            st.markdown("""
            1. **Upload a document**: Use the sidebar to upload your PDF document
            2. **Wait for processing**: The app will extract and process the content
            3. **Start chatting**: Ask questions about the document content
            4. **Get expert answers**: The agentic team will provide detailed explanations, analogies, summaries, or technical breakdowns
            """)


if __name__ == "__main__":
    main()
