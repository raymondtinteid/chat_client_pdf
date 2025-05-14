#!/usr/bin/env python3
import os
from dataclasses import dataclass
from typing import Any, Dict, Optional, List
import json

from google import genai
from openai import AzureOpenAI, OpenAI

from dotenv import load_dotenv

load_dotenv()


@dataclass
class LLM:
    """
    Data class representing an LLM client with its type and client object.

    Attributes:
        type: The type of LLM client ("azure_openai", "gemini")
        client: The client object for the respective LLM service
    """

    type: Optional[str] = None
    client: Optional[Any] = None
    model: str = None
    available: List[str] = None


def get_ai_client() -> LLM:
    """
    Check available API keys and return the appropriate client.

    Returns:
        LLMClient object containing the client type and client object
    """
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    azure_api_key = os.getenv("AZURE_OPENAI_API_KEY")
    azure_api_version = os.getenv("AZURE_OPENAI_API_VERSION")
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    model = os.getenv("MODEL")
    available = json.loads(os.getenv("AVAILABLE_MODELS"))

    if azure_endpoint or azure_api_key:
        client = AzureOpenAI(
            azure_endpoint=azure_endpoint,
            api_version=azure_api_version,
            api_key=azure_api_key,
        )
        type = "azure_openai"
    else:
        client = genai.Client(api_key=gemini_api_key)
        type = "gemini"

    return LLM(type=type, client=client, model=model, available=available)


llm_client = get_ai_client()
