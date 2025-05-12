#!/usr/bin/env python3

import os
from openai import AzureOpenAI, OpenAI
from google import genai
from dotenv import load_dotenv
import ui  # Import our new UI module
from parser import extract_pdf_text

load_dotenv()


def get_ai_client():
    """Check available API keys and return the appropriate client"""
    # Check for Azure OpenAI
    azure_endpoint = os.getenv("APP_OPENAI_API_BASE")
    azure_api_key = os.getenv("AZURE_OPENAI_API_KEY")

    if azure_endpoint and azure_api_key:
        client = AzureOpenAI(
            azure_endpoint=azure_endpoint,
            api_version=os.getenv("APP_OPENAI_API_VERSION", "2025-01-01-preview"),
            api_key=azure_api_key,
        )
        return {"type": "azure_openai", "client": client}

    # Check for OpenAI
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if openai_api_key:
        client = OpenAI(api_key=openai_api_key)
        return {"type": "openai", "client": client}

    # Check for Gemini
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if gemini_api_key:
        client = genai.Client(api_key=gemini_api_key)
        return {"type": "gemini", "client": client}

    # No API keys available
    return {"type": "none", "client": None}


def chat_response(message, history, files):
    """Generate response using either PDF context or general knowledge via OpenAI or Gemini"""
    try:
        # Prepare messages list
        messages = []

        # Add PDF context if available
        if files and len(files) > 0:
            pdf_text = extract_pdf_text(files)[:6000]
            context = f"Use these documents to answer questions:\n{pdf_text}"
        else:
            context = None

        # Check which API key is available and create the appropriate client
        client = get_ai_client()

        if client["type"] == "azure_openai":
            # Azure OpenAI implementation
            # [Code remains the same as in the original script]
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

            # Get response from Azure OpenAI
            response = client["client"].chat.completions.create(
                model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
                messages=messages,
            )

            # Extract token usage
            token_usage = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            }

            return response.choices.message.content.strip(), token_usage

        elif client["type"] == "openai":
            # OpenAI implementation
            # [Code remains the same as in the original script]
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

            # Get response from OpenAI
            response = client["client"].chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0.7,
            )

            # Extract token usage
            token_usage = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            }

            return response.choices.message.content.strip(), token_usage

        elif client["type"] == "gemini":
            # Gemini implementation
            # [Code remains the same as in the original script]
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
            token_count = client["client"].models.count_tokens(
                model="gemini-2.0-flash", contents=prompt
            )
            prompt_tokens = token_count.total_tokens

            # Get response from Gemini
            response = client["client"].models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt,
            )

            # Extract token usage from response
            completion_tokens = response.usage_metadata.candidates_token_count
            total_tokens = response.usage_metadata.total_token_count

            token_usage = {
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": total_tokens,
            }

            return response.text.strip(), token_usage

        else:
            return "No AI service is available. Please set up API keys.", {
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
    # Convert tuple history to list of ChatMessage objects if needed
    messages_history = []
    for h in history:
        if isinstance(h, tuple):
            messages_history.append(gr.ChatMessage(role="user", content=h[0]))
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
            metadata={"title": f"🔢 Token Usage: {token_usage['total_tokens']} total"},
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

    # Install required packages if not already installed
    try:
        import google.generativeai
    except ImportError:
        print("Installing google-generativeai package...")
        os.system("pip install google-generativeai")

    # Create the UI
    demo, service_info = ui.create_ui(chat_wrapper, update_last_response)

    # Update service info with the current AI service
    ai_service_type = get_ai_client()["type"]
    ui.update_service_info(service_info, ai_service_type)

    # Launch the application
    demo.launch()
