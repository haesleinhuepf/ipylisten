from __future__ import annotations

from typing import Union, List, Dict


def prompt_openai(message: Union[str, List[Dict[str, str]]], model: str = "gpt-5-mini") -> str:
    """Send a message to OpenAI and return only the text response."""
    try:
        # Lazy import so environments without OpenAI don't break until used
        from openai import OpenAI
    except Exception as import_error:  # pragma: no cover
        raise RuntimeError(
            "openai package is required to use LLM features. Install and set OPENAI_API_KEY."
        ) from import_error

    if isinstance(message, str):
        message = [{"role": "user", "content": message}]

    client = OpenAI()

    response = client.chat.completions.create(
        model=model,
        messages=message,
    )

    return response.choices[0].message.content or ""


essential_instructions = (
    "You are a writing assistant. Improve spelling, grammar, and punctuation. "
    "Do not change meaning. Return only the corrected text."
)


def correct_grammar(text: str, model: str = "gpt-5-mini") -> str:
    """Use an LLM to correct spelling and grammar of the provided text."""
    system = {"role": "system", "content": essential_instructions}
    user = {"role": "user", "content": text}
    return prompt_openai([system, user], model=model)
