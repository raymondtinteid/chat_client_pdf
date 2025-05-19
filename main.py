#!/usr/bin/env python3

import os
from pdfparser import extract_pdf_text_by_page
from typing import Any, BinaryIO, Dict, List, Optional, Tuple

import gradio as gr

from chat import chat_response, chat_wrapper
from llm import get_ai_client
from ui import create_ui
from utilities import extract_token_usage


# Create the UI
demo, service_info = create_ui(chat_wrapper)

# Launch the application
demo.launch(debug=True, show_error=True)
