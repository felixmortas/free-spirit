import os

from langchain.agents import create_agent
from langchain_mistralai import ChatMistralAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import InMemorySaver

from system_prompt import get_system_prompt
from tools import get_tools
from middleware.model_fallback import fallback

def create_email_agent(model_name: str, debug: bool):
    if model_name.startswith("gemini"):
        model = ChatGoogleGenerativeAI(model=model_name, api_key=os.getenv('GOOGLE_API_KEY')) # gemini-3-flash-preview gemini-2.5-pro gemini-2.5-flash gemini-2.5-flash-lite gemini-2.5-flash-lite-preview-09-2025 gemini-2.5-flash-native-audio-preview-12-2025 gemini-2.5-flash-preview-tts gemini-2.0-flash gemini-2.0-flash-lite

    elif model_name.startswith("mistral"):
        model = ChatMistralAI(model=model_name, api_key=os.getenv('MISTRAL_API_KEY'))

    else:
        raise ValueError(f"Modèle non supporté : {model_name}. Utilisez un modèle 'gemini-*' ou 'mistral-*'.")
    
    system_prompt_path = os.path.join("prompts", "system_prompt.md")
    checkpointer = InMemorySaver()

    return create_agent(
        model=model, 
        tools=get_tools(), 
        system_prompt=get_system_prompt(system_prompt_path),
        checkpointer=checkpointer,
        # state_schema=State, 
        # context_schema=Context, 
        middleware=[fallback],
        debug=debug
    )