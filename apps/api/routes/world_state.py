from fastapi import APIRouter

from tools.world_state import get_world_state

router = APIRouter(
    prefix="/world-state",
    tags=["world-state"],
)


@router.get("/{story_id}/{branch_id}")
def world_state(
    story_id: str,
    branch_id: str,
):
    state = get_world_state(
        story_id,
        branch_id,
    )

    if state is None:
        return {"found": False}

    return state.model_dump()