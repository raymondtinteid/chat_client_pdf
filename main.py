#!/usr/bin/env python3

import os
from typing import Dict, Tuple, List, BinaryIO, Any, Optional
from dotenv import load_dotenv
import ui  # Import our new UI module
from parser import extract_pdf_text_by_page
from llm import get_ai_client

load_dotenv()


def extract_token_usage(response: Any, client_type: str) -> Dict[str, int]:
    """
    Extract token usage information from the API response.

    Args:
        response: The API response object
        client_type: The type of AI client used

    Returns:
        Dictionary containing token usage information
    """
    token_usage = {
        "prompt_tokens": 0,
        "completion_tokens": 0,
        "total_tokens": 0,
    }

    try:
        if client_type in ["azure_openai", "openai"]:
            token_usage = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            }
        elif client_type == "gemini":
            token_usage = {
                "prompt_tokens": getattr(response, "prompt_tokens", 0),
                "completion_tokens": response.usage_metadata.candidates_token_count,
                "total_tokens": response.usage_metadata.total_token_count,
            }
    except Exception:
        # If token extraction fails, return zeros
        pass

    return token_usage


def chat_response(
    message: str, history: List[Tuple[str, str]], files: List[BinaryIO]
) -> Tuple[str, Dict[str, int]]:
    """
    Generate response using either PDF context or general knowledge via OpenAI or Gemini.

    Args:
        message: The user's message
        history: Conversation history
        files: List of uploaded PDF files

    Returns:
        Tuple containing the response text and token usage information
    """
    try:
        # Check which API key is available and create the appropriate client
        client_info = get_ai_client()
        client_type = client_info["type"]
        client = client_info["client"]

        if client_type == "none":
            return "No AI service is available. Please set up API keys.", {
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0,
            }

        # Add PDF context if available
        context = None
        if files and len(files) > 0:
            pdf_text = extract_pdf_text_by_page(files)[:6000]
            context = f"Use these documents to answer questions:\n{pdf_text}"

        # Handle different client types
        if client_type in ["azure_openai", "openai"]:
            return handle_openai_request(client, client_type, message, history, context)
        elif client_type == "gemini":
            return handle_gemini_request(client, message, history, context)
        else:
            return "Unsupported AI service type.", {
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0,
            }

    except Exception as e:
        return f"Error processing request: {str(e)}", {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
        }


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

    # Count tokens first
    token_count = client.models.count_tokens(model="gemini-2.0-flash", contents=prompt)
    prompt_tokens = token_count.total_tokens

    # Get response from Gemini
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt,
    )

    # Store prompt tokens for later use in token extraction
    response.prompt_tokens = prompt_tokens

    # Extract token usage
    token_usage = extract_token_usage(response, "gemini")

    return response.text.strip(), token_usage


def chat_wrapper(message, history, files):
    """Wrapper function to handle chat interactions"""
    # Convert tuple history to list of ChatMessage objects if needed
    messages_history = []
    for h in history:
        if isinstance(h, tuple):
            messages_history.append(gr.ChatMessage(role="user", content=h))
            messages_history.append(gr.ChatMessage(role="assistant", content=h[1]))
        else:
            messages_history.append(h)

    response_text, token_usage = chat_response(message, history, files)

    # Create token usage information
    token_info_text = f"**Token Usage:** Prompt: {token_usage['prompt_tokens']} | Completion: {token_usage['completion_tokens']} | Total: {token_usage['total_tokens']}"

    # Add messages to history
    messages_history.append(gr.ChatMessage(role="user", content=message))
    messages_history.append(
        gr.ChatMessage(
            role="assistant",
            content=response_text,
            metadata={"title": f"Token Usage: {token_usage['total_tokens']} total"},
        )
    )

    return "", messages_history, response_text, token_info_text


def update_last_response(history):
    """Update the last response textbox with the most recent assistant message"""
    if history and len(history) > 0:
        if isinstance(history[-1], tuple):
            last_msg = history[-1][1]
        else:
            last_msg = history[-1].content if history[-1].role == "assistant" else ""
        return last_msg
    return ""


if __name__ == "__main__":
    # Import gradio here to avoid circular imports
    import gradio as gr

    # Create the UI
    demo, service_info = ui.create_ui(chat_wrapper, update_last_response)

    # Update service info with the current AI service
    ai_service_type = get_ai_client()["type"]
    ui.update_service_info(service_info, ai_service_type)

    # Launch the application
    demo.launch()
