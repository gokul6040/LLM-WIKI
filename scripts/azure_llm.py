from __future__ import annotations

import os
from typing import Optional

from dotenv import load_dotenv
from openai import AzureOpenAI


def _required_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def get_client() -> AzureOpenAI:
    load_dotenv()
    endpoint = _required_env("AZURE_OPENAI_ENDPOINT")
    api_key = _required_env("AZURE_OPENAI_API_KEY")
    api_version = _required_env("AZURE_OPENAI_API_VERSION")
    return AzureOpenAI(azure_endpoint=endpoint, api_key=api_key, api_version=api_version)


def ask_azure_llm(system_prompt: str, user_prompt: str, temperature: float = 0.1) -> str:
    client = get_client()
    deployment = _required_env("AZURE_OPENAI_DEPLOYMENT")
    response = client.chat.completions.create(
        model=deployment,
        temperature=temperature,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )
    message = response.choices[0].message.content
    return message.strip() if isinstance(message, str) else ""


def env_is_configured() -> bool:
    load_dotenv()
    keys = [
        "AZURE_OPENAI_ENDPOINT",
        "AZURE_OPENAI_API_KEY",
        "AZURE_OPENAI_DEPLOYMENT",
        "AZURE_OPENAI_API_VERSION",
    ]
    return all(os.getenv(k, "").strip() for k in keys)
