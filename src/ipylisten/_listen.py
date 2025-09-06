from __future__ import annotations

from typing import Optional

from ._mic import listen_to_microphone
from ._llm import correct_grammar
from ._jupyter import set_current_cell_text
from ._config import get_prefix


def listen(
    microphone_index: Optional[int] = None,
    timeout: Optional[float] = 10,
    model: str = "gpt-5-mini",
) -> Optional[str]:
    """Listen via the microphone, grammar-correct via LLM, and insert into cell.

    Returns the corrected text (or None if no text captured).
    """
    raw_text = listen_to_microphone(microphone_index=microphone_index, timeout=timeout)
    if not raw_text:
        return None

    corrected = correct_grammar(raw_text, model=model).strip()
    if not corrected:
        corrected = raw_text

    # Get prefix and prepend it to the corrected text
    prefix = get_prefix()
    if prefix:
        final_text = f"{prefix}{corrected}"
    else:
        final_text = corrected

    # Insert into the current Jupyter cell; if not in IPython, just print it
    inserted = set_current_cell_text(final_text, replace=True)
    if not inserted:
        print("Failed to insert into cell, printing to console instead")
        print(final_text)

    return final_text
