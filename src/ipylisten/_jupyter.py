from __future__ import annotations

from typing import Optional


def set_current_cell_text(code: str, replace: bool = True) -> bool:
    """Insert code into the current Jupyter cell.

    Returns True if insertion succeeded, else False (e.g., not in IPython).
    """
    try:
        from IPython import get_ipython
    except Exception:
        return False

    ip = get_ipython()
    if ip is None:
        return False

    ip.set_next_input(code, replace=replace)
    return True
