from __future__ import annotations

import logging
from config.settings import settings
from agents.shared import AgentResult, CharacterRequest
from agents.character.prompts import SYSTEM_PROMPT
from tools.character_memory import get_character_knowledge
from tools.story_search import search_story
from tools.world_state import get_world_state

logger = logging.getLogger("reworld")


class CharacterAgent:

    def __init__(self, llm=None):
        if llm is not None:
            self.llm = llm
        else:
            try:
                from config.llm import get_llm
                self.llm = get_llm()
            except Exception as e:
                logger.warning(f"LLM not available for CharacterAgent: {e}")
                self.llm = None

    def respond(self, request: CharacterRequest) -> AgentResult:

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
                    "character_id": character.id,
                    "sequence": request.sequence,
                },
            )

        try:
            response = self.llm.invoke([
                ("system", SYSTEM_PROMPT),
                ("human", self._build_prompt(context)),
            ])

            output_text = response.content
            if isinstance(output_text, list):
                output_text = "".join(
                    part.get("text", "") if isinstance(part, dict) else str(part)
                    for part in output_text
                )
            elif not isinstance(output_text, str):
                output_text = str(output_text)

            return AgentResult(
                success=True,
                output=output_text,
                metadata={
                    "character_id": character.id,
                    "sequence": request.sequence,
                    "knowledge_count": len(knowledge),
                    "context": context,
                },
            )
        except Exception as e:
            logger.error(f"Character LLM error: {e}")
            return AgentResult(
                success=True,
                output=f"[{character.name}]: (Stirs thoughtfully) Based on what I know at this moment, {request.message} is something I must consider carefully.",
                metadata={
                    "character_id": character.id,
                    "sequence": request.sequence,
                    "knowledge_count": len(knowledge),
                    "context": context,
                    "error": str(e),
                },
            )

    def _build_prompt(self, context: dict) -> str:
        return f"""Character:
{context["character"]}

Known facts (strictly bounded to timeline position sequence <= {context["sequence"]}):
{context["knowledge"]}

Source evidence:
{context["source_evidence"]}

Timeline sequence:
{context["sequence"]}

User:
{context["user_message"]}

Respond strictly in character. Do not mention events or facts beyond sequence {context["sequence"]}.
"""

    def _fallback_response(self, name: str) -> str:
        return (
            f"{name} is ready to respond, but the LLM "
            "provider has not been connected yet."
        )