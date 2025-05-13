from typing import Dict, Any


def extract_token_usage(response: Any, client_type: str) -> Dict[str, int]:
    """
    Extract token usage information from the API response.

    Args:
        response: The API response object
        client_type: The type of AI client used

    Returns:
        Dictionary containing token usage information
    """
    token_usage = {
        "prompt_tokens": 0,
        "completion_tokens": 0,
        "total_tokens": 0,
    }

    try:
        if client_type in ["azure_openai", "openai"]:
            token_usage = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            }
        elif client_type == "gemini":
            token_usage = {
                "prompt_tokens": response.usage_metadata.prompt_token_count,
                "completion_tokens": response.usage_metadata.candidates_token_count,
                "total_tokens": response.usage_metadata.total_token_count,
            }
    except Exception:
        # If token extraction fails, return zeros
        pass

    return token_usage
