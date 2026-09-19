"""Interactive CLI for Re:World - Test any scenario, chat with characters, and branch timelines."""
from __future__ import annotations

import json
import urllib.error
import urllib.request

BASE_URL = "http://127.0.0.1:8000/api"


def api_call(path: str, method: str = "GET", data: dict | None = None):
    url = f"{BASE_URL}{path}"
    req = urllib.request.Request(url, method=method)
    if data:
        req.add_header("Content-Type", "application/json")
        req.data = json.dumps(data).encode("utf-8")
    try:
        r = urllib.request.urlopen(req)
        return json.loads(r.read().decode("utf-8"))
    except urllib.error.URLError as e:
        print(f"\n[Error] Unable to reach backend at {BASE_URL}.")
        print("Please make sure the backend is running:")
        print("  .venv\\Scripts\\python -m uvicorn apps.api.main:app --host 127.0.0.1 --port 8000\n")
        raise e


def print_banner():
    print("=" * 75)
    print("      RE:WORLD — LIVE INTERACTIVE NARRATIVE CONSOLE")
    print("=" * 75)


def list_and_select_character(story_id: str, branch_id: str):
    res = api_call(f"/characters/{story_id}?branch_id={branch_id}")
    chars = res.get("characters", [])
    print("\nAvailable Characters:")
    for i, c in enumerate(chars, 1):
        status = "ALIVE" if c.get("alive", True) else "DECEASED"
        print(f"  [{i}] {c['name']} ({c['id']}) - {status} @ {c.get('current_location', 'Unknown')}")
    
    while True:
        choice = input("\nSelect character [1-6] or enter character_id (or 'back'): ").strip()
        if choice.lower() == "back":
            return None
        if choice.isdigit() and 1 <= int(choice) <= len(chars):
            return chars[int(choice) - 1]["id"]
        for c in chars:
            if c["id"] == choice:
                return c["id"]
        print("Invalid choice, try again.")


def chat_loop(story_id: str, branch_id: str):
    char_id = list_and_select_character(story_id, branch_id)
    if not char_id:
        return

    # Get character details
    char_info = api_call(f"/characters/{story_id}/{char_id}?branch_id={branch_id}")
    
    # Get timeline events to let user select sequence
    timeline = api_call(f"/timelines/{story_id}/{branch_id}")
    max_seq = timeline.get("max_sequence", 12)
    
    print(f"\n--- Interrogating {char_info['name']} ---")
    print(f"Role / Description: {char_info.get('description', '')}")
    print(f"Timeline range: Sequence 1 to {max_seq}")
    
    seq_input = input(f"Select Timeline Sequence position [1-{max_seq}] (default {max_seq}): ").strip()
    seq = int(seq_input) if seq_input.isdigit() else max_seq

    # Show facts known at this sequence
    knowledge = api_call(f"/characters/{story_id}/{char_id}/knowledge?sequence={seq}&branch_id={branch_id}")
    print(f"\n[Temporal Knowledge]: {char_info['name']} has {knowledge.get('total', 0)} facts in memory at Sequence {seq}.")
    
    print("\nType your questions below. (Commands: 'seq <num>' to change timeline, 'facts' to list facts, 'exit' to return)\n")
    
    while True:
        msg = input(f"[{char_info['name']} @ Seq {seq}] You: ").strip()
        if not msg:
            continue
        if msg.lower() in ("exit", "quit", "back"):
            break
        if msg.lower().startswith("seq "):
            try:
                new_seq = int(msg.split()[1])
                seq = new_seq
                knowledge = api_call(f"/characters/{story_id}/{char_id}/knowledge?sequence={seq}&branch_id={branch_id}")
                print(f"[Updated] Timeline shifted to Sequence {seq}. Facts in memory: {knowledge.get('total', 0)}")
                continue
            except Exception:
                print("Usage: seq <number>")
                continue
        if msg.lower() == "facts":
            knowledge = api_call(f"/characters/{story_id}/{char_id}/knowledge?sequence={seq}&branch_id={branch_id}")
            print(f"\nFacts known by {char_info['name']} up to Sequence {seq}:")
            for f in knowledge.get("facts", []):
                print(f"  • {f['statement']}")
            print()
            continue

        # Send chat request
        res = api_call("/chat/", "POST", {
            "character_id": char_id,
            "story_id": story_id,
            "branch_id": branch_id,
            "sequence": seq,
            "message": msg,
        })

        if res.get("success"):
            print(f"\n{char_info['name']}:")
            print(f"{res.get('output', '').strip()}\n")
            print(f"[Knowledge Used: {res.get('knowledge_count', 0)} facts]\n")
        else:
            print(f"Error: {res.get('errors')}")


def branch_loop(story_id: str, current_branch: str):
    timeline = api_call(f"/timelines/{story_id}/{current_branch}")
    events = timeline.get("events", [])
    
    print("\n--- Create What-If Timeline Divergence ---")
    print("Timeline Events:")
    for e in events:
        print(f"  [Seq {e['sequence']:>2}] {e['title']}")
        
    seq_input = input("\nEnter divergence sequence point: ").strip()
    if not seq_input.isdigit():
        print("Invalid sequence.")
        return current_branch
    
    divergence_seq = int(seq_input)
    prompt = input("Enter your 'What If' divergence prompt: ").strip()
    if not prompt:
        print("Empty prompt.")
        return current_branch
    
    print("\nSimulating divergence with narrative engine...")
    res = api_call("/branches/create", "POST", {
        "story_id": story_id,
        "parent_branch_id": current_branch,
        "sequence": divergence_seq,
        "change": prompt,
    })
    
    branch_id = res["branch"]["id"]
    print(f"\n[Created Branch]: {branch_id}")
    print(f"Affected Events: {res.get('affected_events')}")
    print(f"Affected Characters: {', '.join(res.get('affected_characters', []))}")
    
    # Check consistency
    print("\nRunning consistency validation...")
    consist = api_call(f"/branches/{branch_id}/validate", "POST")
    print(f"Consistency Status: {'VALID' if consist.get('valid') else 'CONTRADICTIONS DETECTED'}")
    print(f"Summary: {consist.get('summary')}")
    
    # Check diff
    diff = api_call(f"/branches/{branch_id}/diff")
    print(f"\nRipple Depth: {diff.get('ripple_depth')} | Total Structural Changes: {diff.get('total_changes')}")
    
    switch = input("\nSwitch active session to this new branch? (y/N): ").strip().lower()
    if switch == "y":
        return branch_id
    return current_branch


def main():
    print_banner()
    
    story_id = "demo"
    current_branch = "canon"
    
    # Ensure backend is accessible
    try:
        api_call("/health")
    except Exception:
        return
    
    while True:
        print("\n" + "-" * 75)
        print(f"ACTIVE WORLD: {story_id.upper()} | CURRENT BRANCH: {current_branch.upper()}")
        print("-" * 75)
        print("1. Interrogate Character (Live Question & Answer with Temporal Memory)")
        print("2. Create 'What-If' Scenario / Branch Timeline")
        print("3. View Timeline & Events")
        print("4. Switch Branch (Canon / Alternate)")
        print("5. Exit")
        
        choice = input("\nChoose option [1-5]: ").strip()
        
        if choice == "1":
            chat_loop(story_id, current_branch)
        elif choice == "2":
            current_branch = branch_loop(story_id, current_branch)
        elif choice == "3":
            timeline = api_call(f"/timelines/{story_id}/{current_branch}")
            print(f"\nTimeline for branch [{current_branch}]:")
            for e in timeline.get("events", []):
                canon_tag = "[CANON]" if e.get("canonical") else "[GENERATED]"
                print(f"  Seq {e['sequence']:>2} | {canon_tag:<11} | {e['title']}")
                print(f"         {e['description']}")
        elif choice == "4":
            branches = api_call(f"/branches/?story_id={story_id}")
            print("\nAvailable Branches:")
            print("  • canon (Original Timeline)")
            for b in branches.get("branches", []):
                print(f"  • {b['id']} ({b['name']})")
            target = input("\nEnter branch ID to switch to (or 'canon'): ").strip()
            if target:
                current_branch = target
        elif choice == "5":
            print("\nExiting Re:World console. Goodbye!")
            break


if __name__ == "__main__":
    main()
