"""Comprehensive demo world for Re:World hackathon demo.

Uses the same schemas and services as uploaded stories.
The demo is based on a fictional detective story with rich
characters, events, relationships, and knowledge facts.
"""
from __future__ import annotations

from core.world import (
    CharacterState,
    Event,
    EventType,
    KnowledgeFact,
    Provenance,
    RelationshipState,
    StoryPoint,
    WorldState,
)
from tools.world_state import get_world_state, save_world_state
from tools.story_search import add_story_document


def seed_demo() -> None:
    # Skip if already seeded
    if get_world_state("demo", "canon") is not None:
        return

    story_id = "demo"
    branch_id = "canon"

    # ── Characters ──────────────────────────────────────────
    characters = {
        "detective_hale": CharacterState(
            id="detective_hale",
            name="Detective Hale",
            description="A sharp-minded detective with a troubled past. Leads the Ashwood murder investigation.",
            personality=["analytical", "determined", "guarded", "empathetic"],
            goals=["solve the Ashwood murder", "uncover the truth", "protect the innocent"],
            current_location="Ashwood Manor",
            aliases=["Hale", "The Detective"],
        ),
        "evelyn_cross": CharacterState(
            id="evelyn_cross",
            name="Evelyn Cross",
            description="The victim's ambitious daughter. Stands to inherit the Ashwood fortune. Hides a secret alliance.",
            personality=["calculating", "charming", "secretive", "ambitious"],
            goals=["secure the inheritance", "protect her secret", "maintain appearances"],
            current_location="Ashwood Manor",
            aliases=["Evelyn", "Eve"],
        ),
        "marcus_grey": CharacterState(
            id="marcus_grey",
            name="Marcus Grey",
            description="The family lawyer and longtime confidant of the victim. Knows more than he reveals.",
            personality=["cautious", "loyal", "evasive", "intelligent"],
            goals=["protect the family legacy", "conceal certain truths", "ensure the will is honored"],
            current_location="Grey & Associates Office",
            aliases=["Marcus", "Mr. Grey"],
        ),
        "dr_lin": CharacterState(
            id="dr_lin",
            name="Dr. Sarah Lin",
            description="The forensic pathologist. Discovers crucial evidence about the cause of death.",
            personality=["meticulous", "objective", "compassionate", "brave"],
            goals=["determine true cause of death", "present evidence truthfully"],
            current_location="City Morgue",
            aliases=["Dr. Lin", "Sarah"],
        ),
        "thomas_ashwood": CharacterState(
            id="thomas_ashwood",
            name="Thomas Ashwood",
            description="The murder victim. Patriarch of the Ashwood family. Found dead in his study.",
            personality=["authoritative", "paranoid", "cunning", "controlling"],
            goals=["protect the family secret", "maintain power"],
            current_location="Ashwood Manor",
            alive=False,
        ),
        "inspector_voss": CharacterState(
            id="inspector_voss",
            name="Inspector Voss",
            description="Hale's superior. Pressured by political interests to close the case quickly.",
            personality=["pragmatic", "politically aware", "impatient", "experienced"],
            goals=["close the case quickly", "satisfy political pressure", "maintain department reputation"],
            current_location="Police Headquarters",
            aliases=["Voss", "The Inspector"],
        ),
    }

    # ── Events (12 events for rich timeline) ────────────────
    events = {
        "evt_01": Event(
            id="evt_01", story_id=story_id,
            title="Thomas Ashwood Found Dead",
            description="Thomas Ashwood, patriarch of the Ashwood family, is found dead in his study at Ashwood Manor. The door was locked from the inside. A glass of whiskey sits half-finished on his desk.",
            sequence=1, event_type=EventType.PLOT,
            participants=["thomas_ashwood", "detective_hale"],
        ),
        "evt_02": Event(
            id="evt_02", story_id=story_id,
            title="Detective Hale Takes the Case",
            description="Detective Hale arrives at Ashwood Manor and examines the crime scene. He notes the locked door, the undisturbed windows, and a faint chemical smell near the whiskey glass.",
            sequence=2, event_type=EventType.PLOT,
            participants=["detective_hale"],
        ),
        "evt_03": Event(
            id="evt_03", story_id=story_id,
            title="Evelyn Cross Questioned",
            description="Evelyn Cross, Thomas's daughter, is questioned by Hale. She claims she was at a charity gala the entire evening. She appears composed but avoids eye contact when discussing her father's will.",
            sequence=3, event_type=EventType.CHARACTER,
            participants=["detective_hale", "evelyn_cross"],
        ),
        "evt_04": Event(
            id="evt_04", story_id=story_id,
            title="The Hidden Will Discovered",
            description="Marcus Grey reveals that Thomas had recently changed his will, cutting Evelyn's share significantly and leaving the majority to a mysterious trust. Grey seems nervous about this revelation.",
            sequence=4, event_type=EventType.PLOT,
            participants=["marcus_grey", "detective_hale"],
        ),
        "evt_05": Event(
            id="evt_05", story_id=story_id,
            title="Forensic Analysis Begins",
            description="Dr. Lin begins the autopsy. Initial findings suggest natural causes — a heart attack. But something about the tissue samples bothers her.",
            sequence=5, event_type=EventType.PLOT,
            participants=["dr_lin"],
        ),
        "evt_06": Event(
            id="evt_06", story_id=story_id,
            title="Secret Meeting at the Docks",
            description="Detective Hale discovers that Evelyn met with an unknown figure at the city docks two days before her father's death. Security footage is grainy but shows an exchange of documents.",
            sequence=6, event_type=EventType.PLOT,
            participants=["evelyn_cross", "detective_hale"],
        ),
        "evt_07": Event(
            id="evt_07", story_id=story_id,
            title="Poison Detected",
            description="Dr. Lin discovers traces of a rare toxin in Thomas's blood — one that mimics heart attack symptoms. The death was murder, not natural causes. She immediately calls Detective Hale.",
            sequence=7, event_type=EventType.PLOT,
            participants=["dr_lin", "detective_hale"],
        ),
        "evt_08": Event(
            id="evt_08", story_id=story_id,
            title="Inspector Voss Pressures Hale",
            description="Inspector Voss orders Hale to wrap up the investigation quickly. Powerful people connected to the Ashwood family are applying pressure. Voss hints that Hale's career is at stake.",
            sequence=8, event_type=EventType.CHARACTER,
            participants=["inspector_voss", "detective_hale"],
        ),
        "evt_09": Event(
            id="evt_09", story_id=story_id,
            title="Grey's Office Broken Into",
            description="Marcus Grey's office is broken into overnight. Files related to the Ashwood trust are stolen. Grey claims he has no idea who did it, but Hale notices Grey doesn't seem surprised.",
            sequence=9, event_type=EventType.PLOT,
            participants=["marcus_grey", "detective_hale"],
        ),
        "evt_10": Event(
            id="evt_10", story_id=story_id,
            title="Evelyn's Alibi Collapses",
            description="A witness from the charity gala confirms that Evelyn left the event early — at 9:15 PM, two hours before she claimed. The window of opportunity for the murder opens wide.",
            sequence=10, event_type=EventType.PLOT,
            participants=["evelyn_cross", "detective_hale"],
        ),
        "evt_11": Event(
            id="evt_11", story_id=story_id,
            title="The Ashwood Family Secret",
            description="Hale uncovers that the mysterious trust was established to protect an illegitimate heir — Thomas's secret second child. Evelyn knew about this sibling and feared losing everything.",
            sequence=11, event_type=EventType.PLOT,
            participants=["detective_hale", "marcus_grey", "evelyn_cross"],
        ),
        "evt_12": Event(
            id="evt_12", story_id=story_id,
            title="Confrontation and Confession",
            description="Hale confronts Evelyn with all the evidence. She breaks down and confesses — she obtained the poison through the contact at the docks and administered it in her father's whiskey. Marcus Grey knew about the changed will but chose silence.",
            sequence=12, event_type=EventType.PLOT,
            participants=["detective_hale", "evelyn_cross", "marcus_grey"],
        ),
    }

    # ── Relationships ───────────────────────────────────────
    relationships = {
        "rel_hale_evelyn": RelationshipState(
            id="rel_hale_evelyn",
            character_a="detective_hale", character_b="evelyn_cross",
            relationship_type="investigator-suspect",
            strength=-0.3,
            description="Hale suspects Evelyn but she is elusive and charming.",
            valid_from_sequence=3,
        ),
        "rel_hale_grey": RelationshipState(
            id="rel_hale_grey",
            character_a="detective_hale", character_b="marcus_grey",
            relationship_type="investigator-witness",
            strength=0.1,
            description="Grey cooperates but withholds information.",
            valid_from_sequence=4,
        ),
        "rel_evelyn_thomas": RelationshipState(
            id="rel_evelyn_thomas",
            character_a="evelyn_cross", character_b="thomas_ashwood",
            relationship_type="daughter-father",
            strength=-0.5,
            description="Evelyn resented her father's controlling nature and feared losing her inheritance.",
            valid_from_sequence=1,
        ),
        "rel_grey_thomas": RelationshipState(
            id="rel_grey_thomas",
            character_a="marcus_grey", character_b="thomas_ashwood",
            relationship_type="lawyer-client",
            strength=0.6,
            description="Grey was Thomas's trusted lawyer for 20 years.",
            valid_from_sequence=1,
        ),
        "rel_evelyn_grey": RelationshipState(
            id="rel_evelyn_grey",
            character_a="evelyn_cross", character_b="marcus_grey",
            relationship_type="uneasy alliance",
            strength=-0.2,
            description="Evelyn and Grey share knowledge they'd rather keep hidden.",
            valid_from_sequence=4,
        ),
        "rel_hale_voss": RelationshipState(
            id="rel_hale_voss",
            character_a="detective_hale", character_b="inspector_voss",
            relationship_type="subordinate-superior",
            strength=0.2,
            description="Voss respects Hale but pressures him politically.",
            valid_from_sequence=8,
        ),
        "rel_hale_lin": RelationshipState(
            id="rel_hale_lin",
            character_a="detective_hale", character_b="dr_lin",
            relationship_type="colleagues",
            strength=0.7,
            description="Hale trusts Dr. Lin's forensic expertise completely.",
            valid_from_sequence=5,
        ),
    }

    # ── Knowledge Facts (timeline-bounded) ──────────────────
    knowledge: dict[str, KnowledgeFact] = {}

    # Facts known by Detective Hale at various points
    hale_facts = [
        ("kf_h1", "detective_hale", "Thomas Ashwood was found dead in a locked room", 1, None),
        ("kf_h2", "detective_hale", "A half-finished glass of whiskey was on Thomas's desk", 2, None),
        ("kf_h3", "detective_hale", "There was a faint chemical smell near the whiskey glass", 2, None),
        ("kf_h4", "detective_hale", "Evelyn claims she was at a charity gala all evening", 3, 10),
        ("kf_h5", "detective_hale", "Thomas recently changed his will, reducing Evelyn's share", 4, None),
        ("kf_h6", "detective_hale", "Most of the estate goes to a mysterious trust", 4, None),
        ("kf_h7", "detective_hale", "Evelyn met someone at the city docks two days before the murder", 6, None),
        ("kf_h8", "detective_hale", "Thomas was poisoned with a rare toxin that mimics heart attacks", 7, None),
        ("kf_h9", "detective_hale", "Inspector Voss is under political pressure to close the case", 8, None),
        ("kf_h10", "detective_hale", "Marcus Grey's office was broken into and Ashwood trust files were stolen", 9, None),
        ("kf_h11", "detective_hale", "Evelyn left the gala at 9:15 PM, not midnight as she claimed", 10, None),
        ("kf_h12", "detective_hale", "The trust protects Thomas's secret illegitimate child", 11, None),
        ("kf_h13", "detective_hale", "Evelyn confessed to poisoning her father", 12, None),
    ]

    # Facts known by Evelyn
    evelyn_facts = [
        ("kf_e1", "evelyn_cross", "Father was controlling and threatened to disinherit me", 1, None),
        ("kf_e2", "evelyn_cross", "I attended the charity gala on the night father died", 1, None),
        ("kf_e3", "evelyn_cross", "I know about father's plan to change his will", 1, None),
        ("kf_e4", "evelyn_cross", "I met a contact at the docks to obtain something", 1, None),
        ("kf_e5", "evelyn_cross", "I left the gala early, but told the detective I stayed all night", 1, 10),
        ("kf_e6", "evelyn_cross", "Father had a secret second child — an illegitimate heir", 1, None),
    ]

    # Facts known by Marcus Grey
    grey_facts = [
        ("kf_g1", "marcus_grey", "I was Thomas Ashwood's lawyer for 20 years", 1, None),
        ("kf_g2", "marcus_grey", "Thomas recently asked me to rewrite his will", 1, None),
        ("kf_g3", "marcus_grey", "The new will creates a trust for a mysterious beneficiary", 1, None),
        ("kf_g4", "marcus_grey", "I suspect Evelyn may be involved but I have no proof", 4, None),
        ("kf_g5", "marcus_grey", "Someone broke into my office and stole the trust documents", 9, None),
    ]

    # Facts known by Dr. Lin
    lin_facts = [
        ("kf_l1", "dr_lin", "Initial autopsy suggested natural causes — heart attack", 5, 7),
        ("kf_l2", "dr_lin", "I found traces of a rare toxin in the blood samples", 7, None),
        ("kf_l3", "dr_lin", "The toxin is designed to mimic heart attack symptoms", 7, None),
        ("kf_l4", "dr_lin", "This toxin is not commercially available — it had to be custom-made", 7, None),
    ]

    for fact_id, char_id, statement, from_seq, until_seq in (
        hale_facts + evelyn_facts + grey_facts + lin_facts
    ):
        knowledge[fact_id] = KnowledgeFact(
            id=fact_id,
            character_id=char_id,
            statement=statement,
            valid_from_sequence=from_seq,
            valid_until_sequence=until_seq,
            provenance=Provenance.CANON,
            confidence=1.0,
        )

    # ── World State ─────────────────────────────────────────
    world = WorldState(
        story_id=story_id,
        branch_id=branch_id,
        current_point=StoryPoint(sequence=12, label="Confrontation and Confession"),
        characters=characters,
        events=events,
        relationships=relationships,
        knowledge=knowledge,
        locations={
            "ashwood_manor": "Ashwood Manor — the victim's estate",
            "police_hq": "Police Headquarters",
            "city_morgue": "City Morgue — forensic lab",
            "grey_office": "Grey & Associates Office",
            "city_docks": "City Docks — the secret meeting place",
        },
    )

    save_world_state(world)

    # ── Index story text for retrieval ──────────────────────
    story_chunks = [
        "Thomas Ashwood, patriarch of the Ashwood family, was found dead in his study. The door was locked from the inside. A glass of whiskey sat half-finished on his desk.",
        "Detective Hale arrived at Ashwood Manor. He examined the crime scene carefully, noting the locked door, undisturbed windows, and a faint chemical smell near the whiskey glass.",
        "Evelyn Cross, Thomas's daughter, was questioned. She claimed she attended a charity gala the entire evening. She appeared composed but avoided eye contact about the will.",
        "Marcus Grey, the family lawyer, revealed Thomas had recently changed his will. Evelyn's share was cut significantly. The majority went to a mysterious trust. Grey seemed nervous.",
        "Dr. Lin began the autopsy. Initial findings suggested natural causes — a heart attack. But something about the tissue samples troubled her deeply.",
        "Detective Hale discovered that Evelyn met with an unknown figure at the city docks two days before her father's death. Security footage showed an exchange of documents.",
        "Dr. Lin discovered traces of a rare toxin in Thomas's blood — one that mimics heart attack symptoms perfectly. The death was murder, not natural causes.",
        "Inspector Voss ordered Hale to close the case quickly. Political pressure from powerful people connected to the Ashwood family. Voss hinted Hale's career was at stake.",
        "Marcus Grey's office was broken into overnight. Files related to the Ashwood trust were stolen. Grey claimed ignorance but didn't seem surprised by the break-in.",
        "A witness confirmed that Evelyn left the charity gala at 9:15 PM — two hours before she claimed. Her alibi had collapsed entirely.",
        "Hale uncovered that the mysterious trust protected Thomas's secret illegitimate child. Evelyn knew about this sibling and feared losing everything she'd been promised.",
        "Hale confronted Evelyn with all the evidence. She broke down and confessed to obtaining the poison through her dock contact and administering it in her father's whiskey.",
    ]

    for i, chunk in enumerate(story_chunks):
        add_story_document(
            source_id=f"demo_chunk_{i + 1}",
            text=chunk,
            metadata={
                "story_id": story_id,
                "chunk_index": i,
                "sequence": i + 1,
            },
        )

    print(f"Demo world seeded: {len(characters)} characters, {len(events)} events, "
          f"{len(relationships)} relationships, {len(knowledge)} knowledge facts.")


if __name__ == "__main__":
    seed_demo()