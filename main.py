#!/usr/bin/env python3

import gradio as gr
import PyPDF2
import os
from openai import AzureOpenAI  # Removed Azure Identity imports

def extract_pdf_text(files):
    """Extract text from multiple PDF files"""
    full_text = ""
    for file in files:
        with open(file.name, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            text = "\n".join([page.extract_text() for page in reader.pages])
            full_text += f"\n\n[Document: {os.path.basename(file.name)}]\n{text}"
    return full_text.strip()

def chat_response(message, history, files):
    """Generate response using either PDF context or general knowledge"""
    try:
        # API Key authentication setup
        client = AzureOpenAI(
            azure_endpoint=os.getenv("APP_OPENAI_API_BASE"),
            api_version=os.getenv("APP_OPENAI_API_VERSION", "2025-01-01-preview"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),  # Changed to API key
        )

        # Prepare messages list
        messages = []

        # Add PDF context if available
        if files and len(files) > 0:
            pdf_text = extract_pdf_text(files)[
                :6000
            ]  # Increased token limit for multiple files
            messages.append(
                {
                    "role": "system",
                    "content": f"Use these documents to answer questions:\n{pdf_text}",
                }
            )

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
        response = client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
            messages=messages,
            temperature=0.7,
        )

        return response.choices.message.content.strip()

    except Exception as e:
        return f"Error processing request: {str(e)}"

with gr.Blocks() as demo:
    chatbot = gr.Chatbot()
    copy_btn = gr.Button("Copy last response to clipboard")
    file_input = gr.File(
        label="Upload PDF(s) (Optional)",
        file_types=[".pdf"],
        file_count="multiple",
    )

    state = gr.State([])

    def chat_wrapper(message, history, files):
        response = chat_response(message, history, files)
        # Save the response in state for copy button
        state.value = response
        return response

    chat_interface = gr.ChatInterface(
        chat_wrapper,
        additional_inputs=[file_input],
        chatbot=chatbot,
        title="Multi-PDF Chat Assistant",
        description="Upload PDFs (optional) and ask questions. Supports multiple documents!",
        examples=[
            ["Summarize the main points"],
            ["Compare the documents"],
            ["What's the key conclusion?"],
        ],
    )

    def copy_to_clipboard_fn(response):
        # This function is only for triggering JS, actual clipboard copy is handled in JS below
        return gr.update()

    copy_btn.click(
        None,
        inputs=None,
        outputs=None,
        _js="""
        () => {
            // Find the last assistant message in the chat
            const chatEls = document.querySelectorAll('[data-testid="chatbot"] [data-testid="message"]');
            if (chatEls.length === 0) return;
            // Find the last assistant message (even index: user, odd index: assistant)
            let lastAssistant = null;
            for (let i = chatEls.length - 1; i >= 0; i--) {
                if (chatEls[i].classList.contains("assistant")) {
                    lastAssistant = chatEls[i];
                    break;
                }
            }
            if (!lastAssistant) return;
            // Get the text content
            const text = lastAssistant.innerText;
            if (!text) return;
            // Copy to clipboard
            navigator.clipboard.writeText(text);
        }
        """
    )

if __name__ == "__main__":
    demo.launch()
