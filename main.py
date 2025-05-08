#!/usr/bin/env python3

import gradio as gr
import PyPDF2
import os
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from openai import AzureOpenAI


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
        # Azure authentication setup
        token_provider = get_bearer_token_provider(
            DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default"
        )

        client = AzureOpenAI(
            azure_endpoint=os.getenv("APP_OPENAI_API_BASE"),
            api_version=os.getenv("APP_OPENAI_API_VERSION", "2025-01-01-preview"),
            azure_ad_token_provider=token_provider,
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

        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"Error processing request: {str(e)}"


with gr.Blocks() as demo:
    gr.ChatInterface(
        chat_response,
        additional_inputs=[
            gr.File(
                label="Upload PDF(s) (Optional)",
                file_types=[".pdf"],
                file_count="multiple",  # Correct parameter name
            )
        ],
        title="Multi-PDF Chat Assistant",
        description="Upload PDFs (optional) and ask questions. Supports multiple documents!",
        examples=[
            ["Summarize the main points"],
            ["Compare the documents"],
            ["What's the key conclusion?"],
        ],
    )

if __name__ == "__main__":
    demo.launch()
