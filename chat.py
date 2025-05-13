from typing import List, Tuple, Any, Dict, BinaryIO, Optional
import os
from parser import extract_pdf_text_by_page
from llm import get_ai_client
from utilities import extract_token_usage


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
            from main import handle_openai_request
            return handle_openai_request(client, client_type, message, history, context)
        elif client_type == "gemini":
            from main import handle_gemini_request
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


def chat_wrapper(message, history, files):
    """Wrapper function to handle chat interactions"""
    import gradio as gr

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
    breakpoint()
    if history and len(history) > 0:
        if isinstance(history[-1], tuple):
            last_msg = history[-1][1]
        else:
            last_msg = (
                history[-1]["content"] if history[-1]["role"] == "assistant" else ""
            )
        return last_msg
    return ""
