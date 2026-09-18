from __future__ import annotations

from agents.shared import AgentResult, CharacterRequest
from tools.character_memory import get_character_knowledge
from tools.story_search import search_story
from tools.world_state import get_world_state


class CharacterAgent:

    def __init__(self, llm=None):
        self.llm = llm

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

        if self.llm is None:
            return AgentResult(
                success=True,
                output=self._fallback_response(character.name),
                metadata={
                    "context": context,
                },
            )

        response = self.llm.invoke(
            self._build_prompt(context)
        )

        return AgentResult(
            success=True,
            output=str(response),
            metadata={
                "character_id": character.id,
                "sequence": request.sequence,
            },
        )

    def _build_prompt(self, context: dict) -> str:
        return f"""
Character: {context["character"]}
Known facts: {context["knowledge"]}
Source evidence: {context["source_evidence"]}
Timeline sequence: {context["sequence"]}

User: {context["user_message"]}

Respond strictly as the character.
Do not reveal information learned after this timeline point.
"""

    def _fallback_response(self, name: str) -> str:
        return (
            f"{name} is ready to respond, but the LLM "
            "provider has not been connected yet."
        )