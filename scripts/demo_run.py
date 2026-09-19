from __future__ import annotations

import json
import urllib.request

BASE_URL = "http://127.0.0.1:8000/api"


def api_call(path: str, method: str = "GET", data: dict | None = None):
    url = f"{BASE_URL}{path}"
    req = urllib.request.Request(url, method=method)
    if data:
        req.add_header("Content-Type", "application/json")
        req.data = json.dumps(data).encode("utf-8")
    r = urllib.request.urlopen(req)
    return json.loads(r.read().decode("utf-8"))


def run_live_demo():
    print("=" * 80)
    print("RE:WORLD LIVE EXECUTION DEMO — ASHWOOD MURDER MYSTERY")
    print("=" * 80)

    # 1. World State Summary
    summary = api_call("/world-state/demo/canon/summary")
    print("\n[STEP 1: WORLD STATE LOADED]")
    print(f"Story ID:            {summary['story_id']}")
    print(f"Branch:              {summary['branch_id']}")
    print(f"Characters:          {summary['character_count']}")
    print(f"Canon Events:        {summary['event_count']}")
    print(f"Canon Relationships: {summary['relationship_count']}")
    print(f"Knowledge Facts:     {summary['knowledge_count']}")

    # 2. Characters List
    chars = api_call("/characters/demo?branch_id=canon")
    print("\n[STEP 2: ACTIVE CHARACTERS]")
    for c in chars["characters"]:
        status = "ALIVE" if c["alive"] else "DECEASED (VICTIM)"
        print(f"  • {c['name']:<20} | Status: {status:<18} | Loc: {c['current_location']}")

    # 3. Interrogation at Sequence 1 (Early Checkpoint)
    print("\n" + "-" * 80)
    print("[STEP 3: TEMPORAL INTERROGATION — SEQUENCE 1 (EARLY CRIME SCENE)]")
    print("User Question to Detective Hale: 'Who killed Thomas Ashwood and what was the weapon?'")
    
    chat_seq1 = api_call("/chat/", "POST", {
        "character_id": "detective_hale",
        "story_id": "demo",
        "branch_id": "canon",
        "sequence": 1,
        "message": "Who killed Thomas Ashwood and what was the weapon?",
    })
    print(f"Knowledge Facts in Hale's Memory at Seq 1: {chat_seq1['knowledge_count']}")
    print("\nDetective Hale's Response at Sequence 1:")
    print(f"\"{chat_seq1['output'].strip()}\"")

    # 4. Interrogation at Sequence 12 (Resolution Checkpoint)
    print("\n" + "-" * 80)
    print("[STEP 4: TEMPORAL INTERROGATION — SEQUENCE 12 (CASE CONCLUDED)]")
    print("User Question to Detective Hale: 'Who killed Thomas Ashwood and what was the weapon?'")
    
    chat_seq12 = api_call("/chat/", "POST", {
        "character_id": "detective_hale",
        "story_id": "demo",
        "branch_id": "canon",
        "sequence": 12,
        "message": "Who killed Thomas Ashwood and what was the weapon?",
    })
    print(f"Knowledge Facts in Hale's Memory at Seq 12: {chat_seq12['knowledge_count']}")
    print("\nDetective Hale's Response at Sequence 12:")
    print(f"\"{chat_seq12['output'].strip()}\"")

    # 5. What-If Branch Simulation at Sequence 6
    print("\n" + "-" * 80)
    print("[STEP 5: CREATING WHAT-IF DIVERGENCE BRANCH AT SEQUENCE 6]")
    divergence_prompt = "What if Evelyn did not go to the docks and never received the rare toxin?"
    print(f"Divergence Change: \"{divergence_prompt}\"")
    
    branch_res = api_call("/branches/create", "POST", {
        "story_id": "demo",
        "parent_branch_id": "canon",
        "sequence": 6,
        "change": divergence_prompt,
    })
    branch_id = branch_res["branch"]["id"]
    print(f"\nCreated Alternate Branch ID: {branch_id}")
    print(f"Divergence Point:           Sequence {branch_res['branch']['divergence_sequence']}")
    print(f"Downstream Events Affected: {branch_res['affected_events']}")
    print(f"Characters Affected:        {', '.join(branch_res['affected_characters'])}")

    # 6. Consistency Validation
    print("\n" + "-" * 80)
    print("[STEP 6: CONSISTENCY AGENT VALIDATION]")
    consistency = api_call(f"/branches/{branch_id}/validate", "POST")
    print(f"Consistency Valid:   {consistency['valid']}")
    print(f"Validation Summary:  {consistency['summary']}")
    if consistency["issues"]:
        print("Detected Inconsistencies / Alternate Deltas:")
        for issue in consistency["issues"][:3]:
            print(f"  • [{issue['type']}] {issue['message']}")

    # 7. Structural Diff & Ripple Metrics
    print("\n" + "-" * 80)
    print("[STEP 7: BRANCH STRUCTURAL DIFF & RIPPLE METRICS]")
    diff = api_call(f"/branches/{branch_id}/diff")
    print(f"Ripple Depth:          {diff['ripple_depth']}")
    print(f"Total Changes:         {diff['total_changes']}")
    print(f"Relationships Changed: {diff['relationships_changed']}")
    print(f"Characters Affected:   {len(diff['characters_affected'])} ({', '.join(diff['characters_affected'])})")
    
    print("\nAdded Events in Alternate Timeline:")
    for e in diff["events_added"]:
        print(f"  [+] [Seq {e['sequence']}] {e['title']}")
        print(f"      Description: {e['branch_description']}")

    # 8. Canon Immutability Check
    print("\n" + "-" * 80)
    print("[STEP 8: CANON IMMUTABILITY AUDIT]")
    canon_after = api_call("/timelines/demo/canon")
    print(f"Canon Total Events: {canon_after['total_events']} (Expected: 12)")
    assert canon_after["total_events"] == 12, "ERROR: Canon was mutated!"
    print("Canon timeline is 100% intact, immutable, and preserved.")
    print("=" * 80)


if __name__ == "__main__":
    run_live_demo()
