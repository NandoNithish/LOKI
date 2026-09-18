from fastapi import APIRouter

from agents import CharacterAgent
from agents.shared import CharacterRequest

router = APIRouter(prefix="/chat", tags=["chat"])

agent = CharacterAgent()


@router.post("/")
def chat(request: CharacterRequest):
    return agent.respond(request).model_dump()