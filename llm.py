#!/usr/bin/env python3
from dataclasses import dataclass
from typing import Any, Dict, Optional, List, Union
import json

from google import genai
from openai import AzureOpenAI

from config import model_config, available_models, prio_model_name


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

    client: Optional[Any] = None
    model: str = None

    def update_model(self, new_model: str) -> str:
        """
        Update the model attribute and client with a new value.

        Args:
            new_model: The new model to use

        Returns:
            The updated model name
        """

        if new_model not in available_models:
            raise ValueError(f"Model {new_model} not found in model_config.")

        self.client = create_client(new_model)
        self.model = model_config[new_model]["model"]
        return model_config[new_model]["model"]


def create_client(model: str) -> Union[AzureOpenAI, genai.Client]:

    exclude = ["model", "client"]
    client_cls = model_config[model]["client"]

    return client_cls(
        **{k: v for k, v in model_config[model].items() if k not in exclude}
    )


def get_ai_client() -> LLM:
    """
    Check available API keys and return the appropriate client.

    Returns:
        LLMClient object containing the client type and client object
    """

    model = prio_model_name
    client = create_client(model)

    return LLM(
        client=client,
        model=model,
    )


llm_client = get_ai_client()
