from __future__ import annotations

from pathlib import Path


def load_prompt(prompt_dir: str | Path, prompt_name: str) -> str:
    base = Path(prompt_dir)
    path = base / prompt_name
    if not path.exists():
        raise FileNotFoundError(f"Prompt not found: {path}")
    return path.read_text(encoding="utf-8")

