from typing import List, Tuple, Any


def chat_wrapper(message, history, files):
    """Wrapper function to handle chat interactions"""
    import gradio as gr
    from main import chat_response

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
