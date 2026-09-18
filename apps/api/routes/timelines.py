from fastapi import APIRouter

router = APIRouter(prefix="/timelines", tags=["timelines"])


@router.get("/{story_id}/{branch_id}")
def get_timeline(story_id: str, branch_id: str):
    return {
        "story_id": story_id,
        "branch_id": branch_id,
        "events": [],
    }