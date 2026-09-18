from fastapi import APIRouter

from agents.narrative import NarrativeAgent
from agents.shared import NarrativeRequest

router = APIRouter(prefix="/branches", tags=["branches"])

agent = NarrativeAgent()


@router.post("/diverge")
def diverge(request: NarrativeRequest):
    return agent.diverge(request).model_dump()