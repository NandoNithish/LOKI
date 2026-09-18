from fastapi import APIRouter

router = APIRouter(prefix="/characters", tags=["characters"])


@router.get("/{character_id}")
def get_character(character_id: str):
    return {"character_id": character_id}