from core.simulation import Branch
from core.world import WorldState
from copy import deepcopy
import uuid

_branches: dict[str, Branch] = {}


def create_branch(
    world_state: WorldState,
    name: str,
    description: str = "",
    divergence_event_id: str | None = None,
) -> Branch:

    branch = Branch(
        id=str(uuid.uuid4()),
        story_id=world_state.story_id,
        name=name,
        description=description,
        parent_branch_id=world_state.branch_id,
        divergence_event_id=divergence_event_id,
        divergence_sequence=world_state.current_point.sequence,
    )

    _branches[branch.id] = branch

    return branch


def get_branch(branch_id: str) -> Branch | None:
    return _branches.get(branch_id)


def clone_world_state(
    world_state: WorldState,
    branch: Branch,
) -> WorldState:
    cloned = deepcopy(world_state)
    cloned.branch_id = branch.id
    return cloned