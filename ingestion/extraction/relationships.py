from __future__ import annotations

import re

from core.world.relationships import RelationshipState


def extract_relationships(
    text: str,
    character_ids: list[str],
) -> list[RelationshipState]:

    relationships: list[RelationshipState] = []

    # Basic initial relationship discovery.
    # Rich relationship extraction will be handled
    # by the Story Analyst Agent.

    lowered = text.lower()

    for index, first in enumerate(character_ids):
        for second in character_ids[index + 1:]:

            first_name = first.replace("_", " ")
            second_name = second.replace("_", " ")

            if (
                first_name.lower() in lowered
                and second_name.lower() in lowered
            ):
                relationship_id = (
                    f"{first}_{second}"
                )

                relationships.append(
                    RelationshipState(
                        id=relationship_id,
                        character_a=first,
                        character_b=second,
                        relationship_type="associated",
                        description=(
                            "Characters appear in "
                            "the same source material."
                        ),
                    )
                )

    return relationships