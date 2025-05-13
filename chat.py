from typing import List, Tuple, Any, Dict, BinaryIO, Optional
import gradio as gr
import os
from parser import extract_pdf_text_by_page
from llm import get_ai_client, llm_client
from request import handle_openai_request, handle_gemini_request, Response


def chat_response(message: str, history: List[dict], files: List[str]) -> Response:
    """
    Generate response using either PDF context or general knowledge via OpenAI or Gemini.

    Args:
        message: The user's message
        history: Conversation history
        files: List of uploaded PDF files

    Returns:
        Tuple containing the response text and token usage information
    """
    # Add PDF context if available
    context = None
    if files and len(files) > 0:
        pdf_text = extract_pdf_text_by_page(files)[:6000]
        context = f"Use these documents to answer questions:\n{pdf_text}"

    request_dispatcher = {
        "azure_openai": handle_openai_request,
        "gemini": handle_gemini_request,
    }
    return request_dispatcher[llm_client.type](llm_client, message, history, context)


def chat_wrapper(message: str, history: List[dict], files: List[str]):
    """Wrapper function to handle chat interactions"""

    response = chat_response(message, history, files)
    p_tokens = response.token_usage["prompt_tokens"]
    c_tokens = response.token_usage["completion_tokens"]
    t_tokens = response.token_usage["total_tokens"]

    # Create token usage information
    token_info = f"**Token Usage:** Prompt: {p_tokens} | Completion: {c_tokens} | Total: {t_tokens}"
    last_response = response.content

    # Add messages to history
    chatbot = history + [
        gr.ChatMessage(role="user", content=message),
        gr.ChatMessage(
            role="assistant",
            content=last_response,
            metadata={"title": f"Token Usage: {t_tokens} total"},
        ),
    ]

    # Clear message box
    msg = ""

    # Return new states of objects
    return msg, chatbot, last_response, token_info
