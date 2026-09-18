from __future__ import annotations

import re

from core.world.timeline import StoryPoint


def extract_timeline(
    text: str,
) -> list[StoryPoint]:

    points: list[StoryPoint] = []

    # Detect common chapter / episode markers.
    pattern = re.compile(
        r"(?im)^(chapter|episode|part)\s+([^\n]+)"
    )

    matches = list(pattern.finditer(text))

    for index, match in enumerate(matches):

        kind = match.group(1).capitalize()
        label = match.group(2).strip()

        points.append(
            StoryPoint(
                sequence=index + 1,
                label=f"{kind} {label}",
                chapter=label if kind == "Chapter" else None,
                episode=label if kind == "Episode" else None,
            )
        )

    if not points:
        points.append(
            StoryPoint(
                sequence=0,
                label="Beginning",
                description="Beginning of the source.",
            )
        )

    return points