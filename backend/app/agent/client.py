from google import genai

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
) -> str:

    client = get_gemini_client()

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config={
            "system_instruction": system_instruction,
            "temperature": 0.2,
        },
    )

    return response.text