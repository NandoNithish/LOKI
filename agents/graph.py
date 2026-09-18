from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from agents.character import CharacterAgent
from agents.consistency import ConsistencyAgent
from agents.narrative import NarrativeAgent
from agents.router import RouterAgent
from agents.shared import AgentState, CharacterRequest, NarrativeRequest


router_agent = RouterAgent()
character_agent = CharacterAgent()
narrative_agent = NarrativeAgent()
consistency_agent = ConsistencyAgent()


def route_request(state: AgentState):
    decision = router_agent.route(
        state.user_input
    )

    return {
        "intent": decision.intent.value,
        "metadata": {
            **state.metadata,
            "target_agent": decision.target_agent,
            "routing_reason": decision.reason,
        },
    }


def character_node(state: AgentState):
    if not state.character_id:
        return {
            "agent_output": "No character was selected."
        }

    request = CharacterRequest(
        character_id=state.character_id,
        story_id=state.story_id,
        branch_id=state.branch_id,
        sequence=state.current_sequence,
        message=state.user_input,
    )

    result = character_agent.respond(request)

    return {
        "agent_output": result.output,
        "metadata": {
            **state.metadata,
            "character_result": result.metadata,
        },
    }


def narrative_node(state: AgentState):
    request = NarrativeRequest(
        story_id=state.story_id,
        branch_id=state.branch_id,
        sequence=state.current_sequence,
        change=state.user_input,
    )

    result = narrative_agent.diverge(request)

    return {
        "agent_output": result.output,
        "metadata": {
            **state.metadata,
            "narrative_result": result.metadata,
        },
    }


def consistency_node(state: AgentState):
    """
    Consistency validation will receive the generated branch
    world state once the persistence layer is connected.
    """

    return {
        "metadata": {
            **state.metadata,
            "consistency_checked": False,
            "consistency_reason": (
                "World-state persistence not connected yet."
            ),
        }
    }


def choose_agent(state: AgentState):
    if state.intent in {
        "chat",
        "perspective",
        "interview",
    }:
        return "character"

    if state.intent in {
        "divergence",
        "expansion",
        "missing_scene",
        "crossover",
    }:
        return "narrative"

    return "character"


def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node(
        "router",
        route_request,
    )

    graph.add_node(
        "character",
        character_node,
    )

    graph.add_node(
        "narrative",
        narrative_node,
    )

    graph.add_node(
        "consistency",
        consistency_node,
    )

    graph.add_edge(
        START,
        "router",
    )

    graph.add_conditional_edges(
        "router",
        choose_agent,
        {
            "character": "character",
            "narrative": "narrative",
        },
    )

    graph.add_edge(
        "character",
        END,
    )

    graph.add_edge(
        "narrative",
        "consistency",
    )

    graph.add_edge(
        "consistency",
        END,
    )

    return graph.compile()


reworld_graph = build_graph()