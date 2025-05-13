import gradio as gr

from llm import llm_client


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
    service_info.value = f"**Using AI Service:** {llm_client.type}"
    return service_info


def build_token_info():
    return gr.Markdown("**Token Usage:** No messages yet")


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
    return gr.Examples(
        examples=[["Create sales proposal"]],
        inputs=msg,
    )


def create_ui(chat_wrapper):
    with gr.Blocks() as demo:
        with gr.Row():
            chatbot = build_chatbot_column()
            file_input = build_file_input_column()
        service_info = build_service_info()
        token_info = build_token_info()
        last_response = build_last_response()
        msg, submit_btn = build_message_row()
        examples = build_examples(msg)

        msg.submit(
            chat_wrapper,
            [msg, chatbot, file_input],
            [msg, chatbot, last_response, token_info],
        )

        submit_btn.click(
            chat_wrapper,
            [msg, chatbot, file_input],
            [msg, chatbot, last_response, token_info],
        )

        copy_btn.click(
            lambda x: x,
            last_response,
            None,
            js="(text) => { navigator.clipboard.writeText(text); }",
        )

    return demo, service_info
