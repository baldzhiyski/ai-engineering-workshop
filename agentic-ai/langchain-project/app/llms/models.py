from langchain_openai import ChatOpenAI
from ..core.config import settings

def get_general_model(temperature: float = 0.0):
    return ChatOpenAI(
        model=settings.openai_chat_model,
        temperature=temperature,
        api_key=settings.openai_api_key,
    )


def get_reasoning_model(temperature: float = 0.0):
    return ChatOpenAI(
        model=settings.openai_chat_model,
        temperature=temperature,
        api_key=settings.openai_api_key,
    )