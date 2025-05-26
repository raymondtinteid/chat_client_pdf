import gradio as gr
from config import available_models
from llm import llm_client

from proposals import proposals


def build_chatbot_column():
    with gr.Column(scale=4):
        chatbot = gr.Chatbot(
            type="messages",
            show_copy_button=True,
            height=600,  # Extended height
            autoscroll=True,  # Automatic scrolling to bottom
        )
    return chatbot


def build_side_column(msg):
    with gr.Column(scale=1):
        file_input = gr.File(
            label="Upload PDF(s)",
            file_types=[".pdf", ".txt"],
            file_count="multiple",
        )
        model_dropdown = gr.Dropdown(
            choices=available_models,
            value=llm_client.model,
            label="Choose LLM Model",
            interactive=True,
        )
        token_info = gr.Markdown("**Token Usage:** No messages yet")
        examples = build_examples(msg)
    return file_input, model_dropdown, token_info, examples


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
            max_lines=3,  # Allow multi-line input but keep it compact
        )
    return msg


def build_examples(msg):
    examples = [[item] for item in proposals.values()]  # value inserted into textbox
    example_labels = [item for item in proposals.keys()]  # short button labels

    return gr.Examples(
        examples=examples, inputs=msg, label="Examples", example_labels=example_labels
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
    with gr.Blocks(theme=gr.themes.Base()) as demo:
        model_info = build_model_version_info()
        last_response = build_last_response()
        msg = build_message_row()

        with gr.Row():
            chatbot = build_chatbot_column()
            file_input, model_dropdown, token_info, examples = build_side_column(msg)

        # Update model_info when dropdown changes
        model_dropdown.change(
            update_model_info, inputs=[model_dropdown], outputs=[model_info]
        )

        # Submit on enter key press only
        msg.submit(
            chat_wrapper,
            [msg, chatbot, file_input, model_dropdown],
            [msg, chatbot, last_response, token_info, model_info],
        )

    return demo
