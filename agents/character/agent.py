from __future__ import annotations
from config.settings import settings
from langchain_google_genai import ChatGoogleGenerativeAI
from agents.shared import AgentResult, CharacterRequest
from tools.character_memory import get_character_knowledge
from tools.story_search import search_story
from tools.world_state import get_world_state


class CharacterAgent:

    def __init__(self, llm=None):
        self.llm = llm or ChatGoogleGenerativeAI(
        model=settings.llm_model,
        google_api_key=settings.gemini_api_key,
        temperature=0.7,
    )

    def respond(
        self,
        request: CharacterRequest,
    ) -> AgentResult:

        world_state = get_world_state(
            request.story_id,
            request.branch_id,
        )

        if world_state is None:
            return AgentResult(
                success=False,
                errors=["World state not found."],
            )

        character = world_state.get_character(
            request.character_id
        )

        if character is None:
            return AgentResult(
                success=False,
                errors=["Character not found."],
            )

        knowledge = get_character_knowledge(
            world_state,
            request.character_id,
            request.sequence,
        )

        retrieved = search_story(
            request.message,
            limit=5,
        )

        context = {
            "character": character.model_dump(),
            "knowledge": [
                fact.model_dump()
                for fact in knowledge
            ],
            "source_evidence": [
                result.text
                for result in retrieved
            ],
            "sequence": request.sequence,
            "user_message": request.message,
        }

        response = self.llm.invoke(
            self._build_prompt(context)
        )

        return AgentResult(
            success=True,
            output=response.content,
            metadata={
                "character_id": character.id,
                "sequence": request.sequence,
            },
        )

    def _build_prompt(self, context: dict) -> str:
        return f"""
Character: {context["character"]}

Known facts:
{context["knowledge"]}

Source evidence:
{context["source_evidence"]}

Timeline sequence:
{context["sequence"]}

User:
{context["user_message"]}

Respond strictly as the character.

Rules:
- Stay consistent with the character's personality.
- Use only knowledge available to the character at this timeline point.
- Do not reveal information learned after this timeline point.
- Do not invent canon facts when the source evidence does not support them.
"""

    def _fallback_response(self, name: str) -> str:
        return (
            f"{name} is ready to respond, but the LLM "
            "provider has not been connected yet."
        )