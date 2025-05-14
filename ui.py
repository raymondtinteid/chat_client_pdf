import gradio as gr
import json
import os
from config import available_models
from llm import llm_client

from proposals import proposals


def build_chatbot_column():
    with gr.Column(scale=4):
        chatbot = gr.Chatbot(type="messages", show_copy_button=True)
    return chatbot


def build_file_input_column():
    with gr.Column(scale=1):
        file_input = gr.File(
            label="Upload PDF(s)",
            file_types=[".pdf"],
            file_count="multiple",
        )
    return file_input


def build_service_info():
    service_info = gr.Markdown()
    # Update service info with the current AI service
    service_info.value = f"**Using AI Service:** {llm_client.model}"
    return service_info


def build_token_info():
    return gr.Markdown("**Token Usage:** No messages yet")


def build_model_version_info():
    return gr.Markdown(f"**Model:** {llm_client.model}")


def build_last_response():
    return gr.Textbox(visible=False)


def build_message_row():
    with gr.Row():
        msg = gr.Textbox(
            show_label=False,
            placeholder="Enter text and press enter",
            container=False,
        )
        submit_btn = gr.Button("Submit")
    return msg, submit_btn


def build_examples(msg):
    examples = [[item] for item in proposals.values()]  # value inserted into textbox
    example_labels = [item for item in proposals.keys()]  # short button labels

    return gr.Examples(
        examples=examples, inputs=msg, label="Examples", example_labels=example_labels
    )


def build_model_dropdown():
    # Default to current model if available, else first in list
    return gr.Dropdown(
        choices=available_models,
        value=llm_client.model,
        label="Choose LLM Model",
        interactive=True,
    )


def update_model_info(model_name: str):
    """
    Update the model in llm_client and return updated info text.

    Args:
        model_name: The new model name selected from dropdown

    Returns:
        Updated model info text
    """
    llm_client.update_model(model_name)
    return f"**Model:** {model_name}"


def create_ui(chat_wrapper):
    with gr.Blocks() as demo:
        with gr.Row():
            chatbot = build_chatbot_column()
            file_input = build_file_input_column()
        with gr.Row():
            model_dropdown = build_model_dropdown()
        service_info = build_service_info()
        model_info = build_model_version_info()
        token_info = build_token_info()
        last_response = build_last_response()
        msg, submit_btn = build_message_row()
        examples = build_examples(msg)

        # Update model_info when dropdown changes
        model_dropdown.change(
            update_model_info, inputs=[model_dropdown], outputs=[model_info]
        )

        # Pass the selected model to chat_wrapper as an additional input
        msg.submit(
            chat_wrapper,
            [msg, chatbot, file_input, model_dropdown],
            [msg, chatbot, last_response, token_info, model_info],
        )

        submit_btn.click(
            chat_wrapper,
            [msg, chatbot, file_input, model_dropdown],
            [msg, chatbot, last_response, token_info, model_info],
        )

    return demo, service_info
