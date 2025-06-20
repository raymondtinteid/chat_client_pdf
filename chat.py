from typing import List, Tuple, Any, Dict, BinaryIO, Optional
import gradio as gr
import os
from pdfparser import Document, create_context
from ui import llm_client
from request import handle_openai_request, handle_gemini_request, Response
from config import prio_model_name


def chat_response(
    message: str,
    history: List[dict] = [],
    files: List[str] = [],
    model: str = prio_model_name,
) -> Response:
    """
    Generate response using either PDF context or general knowledge via OpenAI or Gemini.

    Args:
        message: The user's message
        history: Conversation history
        files: List of uploaded PDF files

    Returns:
        Tuple containing the response text and token usage information
    """
    context = create_context(files)

    request_dispatcher = {
        "gpt-4o": handle_openai_request,
        "o1-preview": handle_openai_request,
        "gemini": handle_gemini_request,
    }
    return request_dispatcher[llm_client.model](
        llm_client, message, history, model, context
    )


def chat_wrapper(message: str, history: List[dict], files: List[str], model: str):
    """Wrapper function to handle chat interactions"""

    response = chat_response(message, history, files, model)
    p_tokens = response.token_usage["prompt_tokens"]
    c_tokens = response.token_usage["completion_tokens"]
    t_tokens = response.token_usage["total_tokens"]

    # Create token usage information
    token_info = f"**Token Usage:** Prompt: {p_tokens} | Completion: {c_tokens} | Total: {t_tokens}"
    last_response = response.content

    # Add messages to history
    history += [
        gr.ChatMessage(role="user", content=message),
        gr.ChatMessage(
            role="assistant",
            content=last_response,
        ),
    ]

    # Clear message box
    msg = ""

    # Return new states of objects
    return msg, history, last_response, token_info, model


def add_to_history(message: str, history: List[dict]):
    return history + [{"role": "user", "content": message}]
