#!/usr/bin/env python3


from chat import chat_wrapper
from ui import create_ui

# Create the UI
demo = create_ui(chat_wrapper)

# Launch the application
demo.launch(debug=True, show_error=True)
