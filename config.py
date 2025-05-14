#!/usr/bin/env python3
from openai import AzureOpenAI
from google import genai

import os
from dotenv import load_dotenv

load_dotenv()

model_config = {
    # sorted by priority
    "gemini": {
        "api_key": os.getenv("GEMINI_API_KEY"),
        "model": os.getenv("GEMINI_MODEL"),
        "client": genai.Client,
    },
    "gpt-4o": {
        "azure_endpoint": os.getenv("GPT4O_ENDPOINT"),
        "api_key": os.getenv("GPT4O_KEY"),
        "api_version": os.getenv("GPT4O_VERSION"),
        "model": os.getenv("GPT4O_MODEL"),
        "client": AzureOpenAI,
    },
    "o1-preview": {
        "azure_endpoint": os.getenv("O1_ENDPOINT"),
        "api_key": os.getenv("O1_KEY"),
        "api_version": os.getenv("O1_VERSION"),
        "model": os.getenv("O1_MODEL"),
        "client": AzureOpenAI,
    },
}
available_models = [k for k in model_config.keys() if model_config[k]["api_key"]]

prio_model_name = available_models[0]
