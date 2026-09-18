from __future__ import annotations

import re

from core.world.characters import CharacterState


def extract_characters(text: str) -> list[CharacterState]:
    """
    Lightweight character extraction.

    This is intentionally deterministic for now.
    The Story Analyst Agent will later perform richer
    LLM-based extraction.
    """

    characters: dict[str, CharacterState] = {}

    # Detect simple dialogue-style names:
    # NAME: dialogue
    pattern = re.compile(
        r"(?m)^([A-Z][A-Za-z0-9 _'-]{1,40}):"
    )

    for match in pattern.finditer(text):
        name = match.group(1).strip()

        key = name.lower()

        if key not in characters:
            character_id = (
                re.sub(r"[^a-z0-9]+", "_", key)
                .strip("_")
            )

            characters[key] = CharacterState(
                id=character_id,
                name=name,
            )

    return list(characters.values())