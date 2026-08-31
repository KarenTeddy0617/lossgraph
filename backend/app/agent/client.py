from typing import Optional, Type

from google import genai
from pydantic import BaseModel

from app.config import settings


def get_gemini_client():
    """
    Create and return the Gemini client.
    """

    if not settings.GEMINI_API_KEY:
        raise RuntimeError(
            "GEMINI_API_KEY is not configured."
        )

    return genai.Client(
        api_key=settings.GEMINI_API_KEY
    )


def generate_agent_response(
    system_instruction: str,
    prompt: str,
    response_schema: Optional[Type[BaseModel]] = None,
) -> str:
    """
    Generate a Gemini response.

    When response_schema is supplied, Gemini is instructed
    to return structured JSON matching that schema.
    """

    client = get_gemini_client()

    config = {
        "system_instruction": system_instruction,
        "temperature": 0.1,
    }

    if response_schema is not None:
        config["response_mime_type"] = "application/json"
        config["response_schema"] = response_schema

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=config,
    )

    if not response.text:
        raise RuntimeError(
            "Gemini returned an empty response."
        )

    return response.text