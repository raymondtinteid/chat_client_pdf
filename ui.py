#!/usr/bin/env python3

import gradio as gr


def create_ui(chat_wrapper_func, update_last_response_func):
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
        service_info = gr.Markdown()

        # Token usage display
        token_info = gr.Markdown("**Token Usage:** No messages yet")

        last_response = gr.Textbox(visible=False)

        with gr.Row():
            msg = gr.Textbox(
                show_label=False,
                placeholder="Enter text and press enter",
                container=False,
            )
            submit_btn = gr.Button("Submit")

        copy_btn = gr.Button("Copy Last Response")

        msg.submit(
            chat_wrapper_func,
            [msg, chatbot, file_input],
            [msg, chatbot, last_response, token_info],
        ).then(update_last_response_func, chatbot, last_response)

        submit_btn.click(
            chat_wrapper_func,
            [msg, chatbot, file_input],
            [msg, chatbot, last_response, token_info],
        ).then(update_last_response_func, chatbot, last_response)

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

    return demo, service_info


def update_service_info(service_info, ai_service_type):
    """Update the service info display with the current AI service type"""
    service_info.value = f"**Using AI Service:** {ai_service_type}"
