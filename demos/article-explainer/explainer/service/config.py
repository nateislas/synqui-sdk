from dotenv import load_dotenv
import os
from langchain_ollama import ChatOllama
from langchain_google_genai import ChatGoogleGenerativeAI


def get_chat_model(model_name: str = "gemini-2.5-flash-lite"):
    """Returns a LangChain chat model initialized with the API key from the environment."""
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")

    if not api_key:
        # This is the solution for the local setup, in case you want to host your model locally.
        return ChatOllama(
            model="qwen3:8b",
            base_url="http://localhost:11434"
        )

    return ChatGoogleGenerativeAI(
        model=model_name,
        temperature=0.2,
        google_api_key=api_key
    )


def get_vaquero_config():
    """Returns Vaquero configuration from environment variables."""
    load_dotenv()
    return {
        "project_name": os.getenv("VAQUERO_PROJECT_NAME", "article-explainer"),
        "project_api_key": os.getenv("VAQUERO_PROJECT_API_KEY"),
        "endpoint": os.getenv("VAQUERO_ENDPOINT", "http://localhost:8000"),
        "environment": os.getenv("VAQUERO_ENVIRONMENT", os.getenv("VAQUERO_MODE", "development"))
    }