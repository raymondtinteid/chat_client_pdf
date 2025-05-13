#!/usr/bin/env python3

import os
from typing import Dict, Tuple, List, BinaryIO, Any, Optional
from dotenv import load_dotenv
import ui  # Import our new UI module
from parser import extract_pdf_text_by_page
from llm import get_ai_client
from utilities import extract_token_usage
from chat import chat_wrapper, update_last_response, chat_response
from request import handle_openai_request, handle_gemini_request

load_dotenv()


if __name__ == "__main__":
    # Import gradio here to avoid circular imports
    import gradio as gr

    # Create the UI
    demo, service_info = ui.create_ui(chat_wrapper, update_last_response)

    # Update service info with the current AI service
    ai_service_type = get_ai_client()["type"]
    ui.update_service_info(service_info, ai_service_type)

    # Launch the application
    demo.launch(debug=True, show_error=True)
