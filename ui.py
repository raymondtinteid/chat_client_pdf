#!/usr/bin/env python3

import gradio as gr
import os

def create_ui(chat_wrapper, get_ai_client):
    """Create and return the Gradio UI components"""
    with gr.Blocks() as demo:
        with gr.Row():
            with gr.Column(scale=4):
                chatbot = gr.Chatbot(type="messages", show_copy_button=True)

            with gr.Column(scale=1):
                file_input = gr.File(
                    label="Upload PDF(s) (Optional)",
                    file_types=[".pdf"],
                    file_count="multiple",
                )

        # Display which AI service is being used
        ai_service = get_ai_client()["type"]
        service_info = gr.Markdown(f"**Using AI Service:** {ai_service}")

        # Token usage display
        token_info = gr.Markdown("**Token Usage:** No messages yet")

        last_response = gr.Textbox(visible=False)

        def update_last_response(history):
            if history and len(history) > 0:
                if isinstance(history[-1], tuple):
                    last_msg = history[-1][1]
                else:
                    last_msg = (
                        history[-1].content if history[-1].role == "assistant" else ""
                    )
                return last_msg
            return ""

        with gr.Row():
            msg = gr.Textbox(
                show_label=False, placeholder="Enter text and press enter", container=False
            )
            submit_btn = gr.Button("Submit")

        copy_btn = gr.Button("Copy Last Response")

        msg.submit(
            chat_wrapper,
            [msg, chatbot, file_input],
            [msg, chatbot, last_response, token_info],
        ).then(update_last_response, chatbot, last_response)

        submit_btn.click(
            chat_wrapper,
            [msg, chatbot, file_input],
            [msg, chatbot, last_response, token_info],
        ).then(update_last_response, chatbot, last_response)

        # Set up the copy button functionality
        copy_btn.click(
            lambda x: x,
            last_response,
            None,
            js="(text) => { navigator.clipboard.writeText(text); }",
        )

        gr.Examples(
            examples=[
                ["Summarize the main points"],
                ["Compare the documents"],
                ["What's the key conclusion?"],
            ],
            inputs=msg,
        )
        
    return demo, chatbot, last_response, token_info

def launch_ui(demo):
    """Launch the Gradio UI"""
    # Install required packages if not already installed
    try:
        import google.generativeai
    except ImportError:
        print("Installing google-generativeai package...")
        os.system("pip install google-generativeai")

    demo.launch()
