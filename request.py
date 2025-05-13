import os
from typing import Dict, Tuple, List, Any, Optional
from utilities import extract_token_usage
from dataclasses import dataclass
from llm import LLM


@dataclass
class Response:
    content: str
    token_usage: dict


def handle_openai_request(
    llm: LLM,
    message: str,
    history: List[Tuple[str, str]],
    context: Optional[str],
) -> Tuple[str, Dict[str, int]]:
    """
    Handle requests for OpenAI and Azure OpenAI clients.

    Args:
        llm_client: The OpenAI client
        message: The user's message
        history: Conversation history
        context: Optional context from PDF files

    Returns:
        Tuple containing the response text and token usage information
    """
    messages = []

    # Add context if available
    if context:
        messages.append({"role": "system", "content": context})

    # Add conversation history
    for human, assistant in history:
        messages.extend(
            [
                {"role": "user", "content": human},
                {"role": "assistant", "content": assistant},
            ]
        )

    # Add current message
    messages.append({"role": "user", "content": message})

    response = llm.client.chat.completions.create(
        model=llm.model,
        messages=messages,
    )

    # Extract token usage
    token_usage = extract_token_usage(response, "azure_openai")

    content = response.choices.message.content.strip()
    return Response(conten, token_usage)


def handle_gemini_request(
    llm: LLM,
    message: str,
    history: List[dict],
    context: Optional[str],
) -> Tuple[str, Dict[str, int]]:
    """
    Handle requests for Gemini client.

    Args:
        client: The Gemini client
        message: The user's message
        history: Conversation history
        context: Optional context from PDF files

    Returns:
        Tuple containing the response text and token usage information
    """
    # Format prompt for Gemini
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

    prompt += "".join(map(_msg_role, history))

    # Add current message
    prompt += f"User: {message}\nAssistant:"

    # Get response from Gemini
    response = llm.client.models.generate_content(
        model=llm.model,
        contents=prompt,
    )

    # Extract token usage
    token_usage = extract_token_usage(response, "gemini")

    content = response.text.strip()
    return Response(content, token_usage)
