from core.world import (
    CharacterState,
    Event,
    StoryPoint,
    WorldState,
)
from tools.world_state import save_world_state


def seed_demo():
    story_id = "demo"
    branch_id = "canon"

    eren = CharacterState(
        id="eren",
        name="Eren",
        personality=["determined", "impulsive"],
        goals=["freedom"],
    )

    mikasa = CharacterState(
        id="mikasa",
        name="Mikasa",
        personality=["loyal", "protective"],
        goals=["protect Eren"],
    )

    event = Event(
        id="demo_event_1",
        story_id=story_id,
        title="Demo Event",
        description="A demonstration story event.",
        sequence=1,
        participants=["eren", "mikasa"],
    )

    state = WorldState(
        story_id=story_id,
        branch_id=branch_id,
        current_point=StoryPoint(
            sequence=1,
            label="Demo Timeline",
        ),
        characters={
            "eren": eren,
            "mikasa": mikasa,
        },
        events={
            event.id: event,
        },
    )

    save_world_state(state)

    print("Demo world seeded.")


if __name__ == "__main__":
    seed_demo()