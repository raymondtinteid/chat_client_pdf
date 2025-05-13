import os
from typing import Dict, Tuple, List, Any, Optional
from utilities import extract_token_usage

def handle_openai_request(
    client: Any,
    client_type: str,
    message: str,
    history: List[Tuple[str, str]],
    context: Optional[str],
) -> Tuple[str, Dict[str, int]]:
    """
    Handle requests for OpenAI and Azure OpenAI clients.

    Args:
        client: The OpenAI client
        client_type: The type of client ("openai" or "azure_openai")
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

    # Get response from OpenAI or Azure OpenAI
    if client_type == "azure_openai":
        response = client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
            messages=messages,
        )
    else:  # OpenAI
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.7,
        )

    # Extract token usage
    token_usage = extract_token_usage(response, client_type)

    return response.choices.message.content.strip(), token_usage


def handle_gemini_request(
    client: Any, message: str, history: List[Tuple[str, str]], context: Optional[str]
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

    # Add conversation history
    for human, assistant in history:
        prompt += f"User: {human}\nAssistant: {assistant}\n\n"

    # Add current message
    prompt += f"User: {message}\nAssistant:"

    # Get response from Gemini
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt,
    )

    # Extract token usage
    token_usage = extract_token_usage(response, "gemini")

    return response.text.strip(), token_usage
