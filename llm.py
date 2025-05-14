#!/usr/bin/env python3
import os
from dataclasses import dataclass
from typing import Any, Dict, Optional, List
import json

from google import genai
from openai import AzureOpenAI, OpenAI

from dotenv import load_dotenv

load_dotenv()

model_config = {
    "gemini-2.0-flash": {
        "KEY": os.getenv("GEMINI_API_KEY"),
        "MODEL": "gemini-2.0-flash",
    },
    "gpt-4o": {
        "ENDPOINT": os.getenv("GPT4O_ENDPOINT"),
        "KEY": os.getenv("GPT4O_KEY"),
        "VERSION": os.getenv("GPT4O_VERSION"),
        "MODEL": os.getenv("GPT4O_MODEL"),
    },
    "o1-preview": {
        "ENDPOINT": os.getenv("O1_ENDPOINT"),
        "KEY": os.getenv("O1_KEY"),
        "VERSION": os.getenv("O1_VERSION"),
        "MODEL": os.getenv("O1_MODEL"),
    },
}


@dataclass
class LLM:
    """
    Data class representing an LLM client with its type and client object.

    Attributes:
        type: The type of LLM client ("azure_openai", "gemini")
        client: The client object for the respective LLM service
        model: The current model being used
        available: List of available models
    """

    type: Optional[str] = None
    client: Optional[Any] = None
    model: str = None
    available: List[str] = None

    def update_model(self, new_model: str) -> str:
        """
        Update the model attribute and client with a new value.

        Args:
            new_model: The new model to use

        Returns:
            The updated model name
        """

        if new_model not in model_config:
            raise ValueError(f"Model {new_model} not found in model_config.")

        config = model_config[new_model]
        if new_model in ["gpt-4o", "o1-preview"]:
            from openai import AzureOpenAI

            self.client = AzureOpenAI(
                azure_endpoint=config["ENDPOINT"],
                api_key=config["KEY"],
                api_version=config["VERSION"],
            )
            self.type = "azure_openai"
        elif new_model == "gemini-2.0-flash":
            from google import genai

            self.client = genai.Client(api_key=config["KEY"])
            self.type = "gemini"
        else:
            raise ValueError(f"Unsupported model: {new_model}")

        self.model = config["MODEL"]
        return self.model


def get_ai_client() -> LLM:
    """
    Check available API keys and return the appropriate client.

    Returns:
        LLMClient object containing the client type and client object
    """

    if os.getenv("GPT4O_KEY"):
        client = AzureOpenAI(
            azure_endpoint=os.getenv("GPT4O_ENDPOINT"),
            api_version=os.getenv("GPT4O_VERSION"),
            api_key=os.getenv("GPT4O_KEY"),
        )
        type = "azure_openai"
        model = os.getenv("GPT4O_MODEL")
    elif os.getenv("O1_KEY"):
        client = AzureOpenAI(
            azure_endpoint=os.getenv("O1_ENDPOINT"),
            api_version=os.getenv("O1_VERSION"),
            api_key=os.getenv("O1_KEY"),
        )
        type = "azure_openai"
        model = os.getenv("O1_MODEL")
    else:
        client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        type = "gemini"
        model = os.getenv("GEMINI_MODEL")

    return LLM(
        type=type,
        client=client,
        model=model,
        available=json.loads(os.getenv("AVAILABLE_MODELS")),
    )


llm_client = get_ai_client()
