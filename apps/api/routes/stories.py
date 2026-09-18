from fastapi import APIRouter

router = APIRouter(prefix="/stories", tags=["stories"])


@router.get("/")
def list_stories():
    return {"stories": []}