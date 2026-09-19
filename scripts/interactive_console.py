"""Interactive CLI for Re:World - Ingest your own stories, test any scenario, and interrogate characters in real time."""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
import uuid

BASE_URL = "http://127.0.0.1:8000/api"


def api_call(path: str, method: str = "GET", data: dict | None = None, content_type: str = "application/json"):
    url = f"{BASE_URL}{path}"
    req = urllib.request.Request(url, method=method)
    if data and content_type == "application/json":
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


def upload_file_api(file_path: str, title: str):
    """Upload TXT, PDF, or DOCX via multipart/form-data."""
    boundary = f"----WebKitFormBoundary{uuid.uuid4().hex}"
    filename = os.path.basename(file_path)
    
    with open(file_path, "rb") as f:
        file_bytes = f.read()

    body = bytearray()
    # Add title field
    body.extend(f"--{boundary}\r\n".encode("utf-8"))
    body.extend(b'Content-Disposition: form-data; name="title"\r\n\r\n')
    body.extend(title.encode("utf-8"))
    body.extend(b"\r\n")

    # Add file field
    body.extend(f"--{boundary}\r\n".encode("utf-8"))
    body.extend(f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'.encode("utf-8"))
    body.extend(b"Content-Type: application/octet-stream\r\n\r\n")
    body.extend(file_bytes)
    body.extend(b"\r\n")
    body.extend(f"--{boundary}--\r\n".encode("utf-8"))

    url = f"{BASE_URL}/stories/upload"
    req = urllib.request.Request(url, data=bytes(body), method="POST")
    req.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")
    
    r = urllib.request.urlopen(req)
    return json.loads(r.read().decode("utf-8"))


def print_banner():
    print("=" * 80)
    print("      RE:WORLD — CUSTOM STORY INGESTION & INTERACTION CONSOLE")
    print("=" * 80)


def ingest_custom_story():
    print("\n--- INGEST YOUR OWN STORY MATERIAL ---")
    print("1. Provide a local file path (.txt, .pdf, .docx)")
    print("2. Paste raw text directly")
    print("3. Back")
    
    choice = input("\nChoose input method [1-3]: ").strip()
    
    if choice == "1":
        file_path = input("\nEnter file path (e.g. C:/path/to/story.txt or my_story.pdf): ").strip().strip('"').strip("'")
        if not os.path.exists(file_path):
            print(f"[Error] File not found: {file_path}")
            return None
        
        default_title = os.path.splitext(os.path.basename(file_path))[0].replace("_", " ").title()
        title = input(f"Enter Story Title (default: '{default_title}'): ").strip() or default_title
        
        print("\nIngesting and extracting narrative entities (characters, timeline, facts)...")
        res = upload_file_api(file_path, title)
        print(f"\n[Success] World Created: '{res['title']}' (ID: {res['story_id']})")
        print(f"Extracted: {res['characters']} characters, {res['events']} events, {res['relationships']} relationships, {res['timeline_points']} timeline points.")
        return res["story_id"]

    elif choice == "2":
        title = input("\nEnter Story Title: ").strip() or "Custom Narrative"
        print("Enter/paste your story text below (Type 'EOF' or press Enter twice on a new line when finished):")
        lines = []
        while True:
            try:
                line = input()
                if line.strip() == "EOF":
                    break
                lines.append(line)
                if len(lines) >= 2 and lines[-1] == "" and lines[-2] == "":
                    break
            except EOFError:
                break
        
        raw_text = "\n".join(lines).strip()
        if not raw_text:
            print("[Error] No text entered.")
            return None
        
        print("\nAnalyzing story and extracting narrative graph...")
        res = api_call("/stories/", "POST", {
            "title": title,
            "raw_text": raw_text,
            "description": f"Custom narrative: {title}",
        })
        print(f"\n[Success] World Created: '{res['title']}' (ID: {res['story_id']})")
        print(f"Extracted: {res['characters']} characters, {res['events']} events, {res['relationships']} relationships, {res['timeline_points']} timeline points.")
        return res["story_id"]

    return None


def list_and_select_character(story_id: str, branch_id: str):
    res = api_call(f"/characters/{story_id}?branch_id={branch_id}")
    chars = res.get("characters", [])
    if not chars:
        print("\nNo characters found in this world yet.")
        return None

    print("\nAvailable Characters:")
    for i, c in enumerate(chars, 1):
        status = "ALIVE" if c.get("alive", True) else "DECEASED"
        loc = c.get('current_location') or 'Present'
        print(f"  [{i}] {c['name']:<22} (ID: {c['id']:<18}) - {status:<8} @ {loc}")
    
    while True:
        choice = input(f"\nSelect character [1-{len(chars)}] or enter character_id (or 'back'): ").strip()
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

    char_info = api_call(f"/characters/{story_id}/{char_id}?branch_id={branch_id}")
    timeline = api_call(f"/timelines/{story_id}/{branch_id}")
    max_seq = timeline.get("max_sequence", 1)
    if max_seq == 0:
        max_seq = len(timeline.get("events", [])) or 1
    
    print(f"\n" + "=" * 60)
    print(f"   LIVE INTERROGATION: {char_info['name'].upper()}")
    print("=" * 60)
    print(f"Description: {char_info.get('description', 'Key participant')}")
    print(f"Timeline range: Sequence 0 to {max_seq}")
    
    seq_input = input(f"Select Timeline Sequence position [0-{max_seq}] (default {max_seq}): ").strip()
    seq = int(seq_input) if seq_input.isdigit() else max_seq

    knowledge = api_call(f"/characters/{story_id}/{char_id}/knowledge?sequence={seq}&branch_id={branch_id}")
    print(f"\n[Temporal Memory Gate]: {char_info['name']} has {knowledge.get('total', 0)} facts in memory at Sequence {seq}.")
    print("\nAsk ANY on-the-spot question! The character will answer strictly in character using timeline-bounded knowledge.")
    print("Commands: 'seq <num>' to change timeline position, 'facts' to list facts, 'exit' to return.\n")
    
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
                print(f"[Timeline Shifted] Position: Sequence {seq} | Facts in Memory: {knowledge.get('total', 0)}")
                continue
            except Exception:
                print("Usage: seq <number>")
                continue
        if msg.lower() == "facts":
            knowledge = api_call(f"/characters/{story_id}/{char_id}/knowledge?sequence={seq}&branch_id={branch_id}")
            print(f"\nFacts known by {char_info['name']} at Sequence {seq}:")
            facts = knowledge.get("facts", [])
            if not facts:
                print("  (No facts learned prior to this sequence)")
            for f in facts:
                print(f"  • {f['statement']}")
            print()
            continue

        # Chat with the character
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
            print(f"[Facts in Active Context: {res.get('knowledge_count', 0)}]\n")
        else:
            print(f"Error: {res.get('errors')}")


def branch_loop(story_id: str, current_branch: str):
    timeline = api_call(f"/timelines/{story_id}/{current_branch}")
    events = timeline.get("events", [])
    
    print("\n--- Create What-If Timeline Divergence ---")
    if not events:
        print("No events in current timeline.")
        return current_branch

    for e in events:
        print(f"  [Seq {e['sequence']:>2}] {e['title']}")
        
    seq_input = input("\nEnter divergence sequence point: ").strip()
    if not seq_input.isdigit():
        print("Invalid sequence.")
        return current_branch
    
    divergence_seq = int(seq_input)
    prompt = input("Enter your 'What If' scenario prompt: ").strip()
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
    
    print("\nRunning consistency validation...")
    consist = api_call(f"/branches/{branch_id}/validate", "POST")
    print(f"Consistency: {'VALID' if consist.get('valid') else 'CONTRADICTIONS DETECTED'}")
    print(f"Summary: {consist.get('summary')}")
    
    diff = api_call(f"/branches/{branch_id}/diff")
    print(f"\nRipple Depth: {diff.get('ripple_depth')} | Total Structural Changes: {diff.get('total_changes')}")
    
    switch = input("\nSwitch active session to this new branch? (y/N): ").strip().lower()
    if switch == "y":
        return branch_id
    return current_branch


def select_world():
    stories_res = api_call("/stories/")
    stories = stories_res.get("stories", [])
    print("\nAvailable Story Worlds:")
    for i, s in enumerate(stories, 1):
        print(f"  [{i}] {s['title']} (ID: {s['id']}) — {s.get('description', '')}")
    
    choice = input(f"\nSelect story [1-{len(stories)}] (or enter story ID): ").strip()
    if choice.isdigit() and 1 <= int(choice) <= len(stories):
        return stories[int(choice) - 1]["id"]
    for s in stories:
        if s["id"] == choice:
            return s["id"]
    return stories[0]["id"] if stories else "demo"


def main():
    print_banner()
    
    try:
        api_call("/health")
    except Exception:
        return
    
    story_id = "demo"
    current_branch = "canon"
    
    while True:
        print("\n" + "-" * 80)
        print(f"ACTIVE WORLD: [{story_id.upper()}] | CURRENT BRANCH: [{current_branch.upper()}]")
        print("-" * 80)
        print("1. INGEST YOUR OWN STORY (File .txt/.pdf/.docx or Raw Text)")
        print("2. Ask On-the-Spot Questions to Characters (Live Interrogation)")
        print("3. Create 'What-If' Scenario / Branch Timeline")
        print("4. View Timeline Events & Canon/Generated Status")
        print("5. Switch to a Different Story World or Branch")
        print("6. Exit")
        
        choice = input("\nChoose option [1-6]: ").strip()
        
        if choice == "1":
            new_story_id = ingest_custom_story()
            if new_story_id:
                story_id = new_story_id
                current_branch = "canon"
                # Automatically prompt to start interrogating
                ask_now = input("\nWould you like to interrogate characters in this newly created world now? (Y/n): ").strip().lower()
                if ask_now != "n":
                    chat_loop(story_id, current_branch)
        elif choice == "2":
            chat_loop(story_id, current_branch)
        elif choice == "3":
            current_branch = branch_loop(story_id, current_branch)
        elif choice == "4":
            timeline = api_call(f"/timelines/{story_id}/{current_branch}")
            print(f"\nTimeline for [{story_id}] on branch [{current_branch}]:")
            events = timeline.get("events", [])
            if not events:
                print("  (No events recorded)")
            for e in events:
                canon_tag = "[CANON]" if e.get("canonical") else "[GENERATED]"
                print(f"  Seq {e['sequence']:>2} | {canon_tag:<11} | {e['title']}")
                print(f"         {e['description']}")
        elif choice == "5":
            print("\n1. Select different Story World")
            print("2. Switch Branch in current Story World")
            sub = input("Choose [1-2]: ").strip()
            if sub == "1":
                story_id = select_world()
                current_branch = "canon"
            elif sub == "2":
                branches = api_call(f"/branches/?story_id={story_id}")
                print("\nAvailable Branches:")
                print("  • canon (Original Timeline)")
                for b in branches.get("branches", []):
                    print(f"  • {b['id']} ({b['name']})")
                target = input("\nEnter branch ID to switch to (or 'canon'): ").strip()
                if target:
                    current_branch = target
        elif choice == "6":
            print("\nExiting Re:World. Goodbye!")
            break


if __name__ == "__main__":
    main()
