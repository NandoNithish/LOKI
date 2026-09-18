from __future__ import annotations

from agents.shared import AgentResult, NarrativeRequest
from core.simulation import Consequence
from tools.branch_manager import create_branch, clone_world_state
from tools.timeline import get_events_until
from tools.world_state import get_world_state
import uuid


class NarrativeAgent:

    def __init__(self, llm=None):
        self.llm = llm

    def diverge(
        self,
        request: NarrativeRequest,
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

        branch = create_branch(
            world_state=world_state,
            name=f"Alternate Timeline {request.sequence}",
            description=request.change,
        )

        new_state = clone_world_state(
            world_state,
            branch,
        )

        affected_events = get_events_until(
            world_state,
            request.sequence,
        )

        consequence = Consequence(
            id=str(uuid.uuid4()),
            branch_id=branch.id,
            title="Timeline Divergence",
            description=request.change,
            affected_events=[
                event.id
                for event in affected_events
            ],
            sequence=request.sequence,
            confidence=0.5,
        )

        new_state.events[consequence.id] = {
            "title": consequence.title,
            "description": consequence.description,
        }

        if self.llm is None:
            return AgentResult(
                success=True,
                output=(
                    f"Created alternate branch "
                    f"'{branch.name}'."
                ),
                metadata={
                    "branch_id": branch.id,
                    "world_state": new_state.model_dump(),
                    "consequence": consequence.model_dump(),
                },
            )

        prompt = self._build_prompt(
            request,
            world_state,
            affected_events,
        )

        response = self.llm.invoke(prompt)

        return AgentResult(
            success=True,
            output=str(response),
            metadata={
                "branch_id": branch.id,
                "consequence": consequence.model_dump(),
            },
        )

    def _build_prompt(
        self,
        request,
        world_state,
        affected_events,
    ) -> str:

        return f"""
Story: {request.story_id}
Timeline point: {request.sequence}

User's change:
{request.change}

Current world state:
{world_state.model_dump()}

Events up to the divergence:
{[event.model_dump() for event in affected_events]}

Simulate the downstream consequences.

Return:
- affected characters
- affected relationships
- changed events
- new events
- likely future consequences

Do not alter the canonical timeline.
Clearly distinguish generated consequences from canon.
"""