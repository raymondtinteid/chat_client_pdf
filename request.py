import os
from typing import Dict, Tuple, List, Any, Optional
from utilities import extract_token_usage
from dataclasses import dataclass
from llm import LLM
from config import model_config


@dataclass
class Response:
    content: str
    token_usage: dict


def handle_openai_request(
    llm_client: LLM,
    message: str,
    history: List[Tuple[str, str]],
    model: str,
    context: Optional[str] = None,
    last_n: Optional[int] = None,
) -> Tuple[str, Dict[str, int]]:
    """
    Handle requests for Azure OpenAI clients.

    Args:
        llm_client: The Azure OpenAI client
        message: The user's message
        history: Conversation history
        context: Optional context from PDF files

    Returns:
        Tuple containing the response text and token usage information
    """
    messages = []

    # Add context if available
    if context:
        messages += [{"role": "user", "content": context}]

    def _msg_role(x):
        if x["role"] == "user":
            m = f"User: {x['content']}\n"
        elif x["role"] == "assistant":
            m = f"Assistant: {x['content']}\n\n"
        return m

    messages += [{"role": item["role"], "content": item["content"]} for item in history]

    # Add current message
    messages += [{"role": "user", "content": message}]

    response = llm_client.client.chat.completions.create(
        model=model_config[model]["model"],
        messages=messages,
    )

    # Extract token usage
    token_usage = extract_token_usage(response, "azure_openai")

    content = response.choices[0].message.content.strip()
    return Response(content, token_usage)


def handle_gemini_request(
    llm_client: LLM,
    message: str,
    history: List[dict],
    model: str,
    context: Optional[str] = None,
    last_n: Optional[int] = None,
) -> Tuple[str, Dict[str, int]]:
    """
    Handle requests for Gemini client.

    Args:
        client: The Gemini client
        message: The user's message
        history: Conversation history
        last_n: Last n messages to include
        context: Optional context from PDF files

    Returns:
        Tuple containing the response text and token usage information
    """
    prompt = ""

    # Add context if available
    if context:
        prompt += context + "\n\n"

    def _msg_role(x):
        if x["role"] == "user":
            m = f"User: {x['content']}\n"
        elif x["role"] == "assistant":
            m = f"Assistant: {x['content']}\n\n"
        return m

    if not last_n:
        last_n = len(history)

    prompt += "".join(map(_msg_role, history[-last_n:]))

    # Add current message
    prompt += f"User: {message}\nAssistant:"

    # Get response from Gemini
    response = llm_client.client.models.generate_content(
        model=model_config[model]["model"],
        contents=prompt,
    )

    # Extract token usage
    token_usage = extract_token_usage(response, "gemini")

    content = response.text.strip()
    return Response(content, token_usage)
