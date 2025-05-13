#!/usr/bin/env python3
from openai import AzureOpenAI, OpenAI
from google import genai
from typing import Dict, Any, Optional
import os
from dataclasses import dataclass


@dataclass
class LLMClient:
    """
    Data class representing an LLM client with its type and client object.
    
    Attributes:
        type: The type of LLM client ("azure_openai", "openai", "gemini", or "none")
        client: The client object for the respective LLM service
    """
    type: str
    client: Optional[Any] = None


def get_ai_client() -> LLMClient:
    """
    Check available API keys and return the appropriate client.

    Returns:
        LLMClient object containing the client type and client object
    """
    # Check for Azure OpenAI
    azure_endpoint = os.getenv("APP_OPENAI_API_BASE")
    azure_api_key = os.getenv("AZURE_OPENAI_API_KEY")

    if azure_endpoint and azure_api_key:
        client = AzureOpenAI(
            azure_endpoint=azure_endpoint,
            api_version=os.getenv("APP_OPENAI_API_VERSION", "2025-01-01-preview"),
            api_key=azure_api_key,
        )
        return LLMClient(type="azure_openai", client=client)

    # Check for OpenAI
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if openai_api_key:
        client = OpenAI(api_key=openai_api_key)
        return LLMClient(type="openai", client=client)

    # Check for Gemini
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if gemini_api_key:
        client = genai.Client(api_key=gemini_api_key)
        return LLMClient(type="gemini", client=client)

    # No API keys available
    return LLMClient(type="none", client=None)


llm_client = get_ai_client()
