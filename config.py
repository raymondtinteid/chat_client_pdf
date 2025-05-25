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
    "text-embedding-3-large": {
        "azure_endpoint": os.getenv("EMBEDDING_ENDPOINT"),
        "api_key": os.getenv("EMBEDDING_KEY"),
        "api_model": os.getenv("EMBEDDING_MODEL"),
        "api_version": os.getenv("EMBEDDING_VERSION"),
        "client": AzureOpenAI,
    },
}
available_models = [k for k in model_config.keys() if model_config[k]["api_key"]]

prio_model_name = available_models[0]

vector_db_config = {
    "n_results": 2,
    "chunk_size": 1000,
    "chroma_db_path": "./chroma_db",
    "chroma_db_collection": "doc_collection",
}

pdf_size_token_limit = 400000
