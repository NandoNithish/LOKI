from __future__ import annotations

import re

from core.world.events import Event, EventType


def extract_events(
    text: str,
    story_id: str,
) -> list[Event]:

    events: list[Event] = []

    paragraphs = [
        paragraph.strip()
        for paragraph in re.split(r"\n\s*\n", text)
        if paragraph.strip()
    ]

    for index, paragraph in enumerate(paragraphs):

        event_id = f"{story_id}_event_{index + 1}"

        title = paragraph.split(".")[0][:100]

        events.append(
            Event(
                id=event_id,
                story_id=story_id,
                title=title or f"Event {index + 1}",
                description=paragraph,
                sequence=index + 1,
                event_type=EventType.PLOT,
            )
        )

    return events