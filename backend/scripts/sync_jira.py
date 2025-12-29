from jira import JIRA
import os
import json
import sys
from dotenv import load_dotenv

load_dotenv()

# --- CONFIGURATION ---
JIRA_URL = os.getenv("JIRA_URL")
JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_TOKEN = os.getenv("JIRA_API_TOKEN")
PROJECT_KEY = os.getenv("PROJECT_KEY")  # Now loaded from .env
STORIES_FILE = "c:\\dm\\backend\\scripts\\stories.json"

# Validate critical env vars
if not JIRA_URL or not JIRA_EMAIL or not JIRA_TOKEN or not PROJECT_KEY:
    print("❌ Error: Missing JIRA credentials or PROJECT_KEY in .env file")
    sys.exit(1)

def get_jira_client():
    return JIRA(server=JIRA_URL, basic_auth=(JIRA_EMAIL, JIRA_TOKEN))

def format_description(details):
    """
    Converts a structured dictionary into a JIRA-formatted string.
    """
    desc = ""

    # User Story Panel
    if "user_story" in details:
        desc += "{panel:title=User Story|bgColor=#EAE6FF}\n"
        desc += details["user_story"] + "\n"
        desc += "{panel}\n\n"

    # Context
    if "context" in details:
        desc += "h3. 🧠 Context & Goal\n"
        desc += details["context"] + "\n\n"

    # Acceptance Criteria
    if "acceptance_criteria" in details:
        desc += "h3. ✅ Acceptance Criteria (Definition of Done)\n"
        for item in details["acceptance_criteria"]:
            desc += f"* {item}\n"
        desc += "\n"

    # Technical Implementation
    if "technical_details" in details:
        desc += "h3. ⚙️ Technical Implementation Details\n"
        for item in details["technical_details"]:
            desc += f"* {item}\n"
        desc += "\n"

    # Edge Cases
    if "edge_cases" in details:
        desc += "h3. ⚠️ Edge Cases & Constraints\n"
        for item in details["edge_cases"]:
            desc += f"* {item}\n"
        desc += "\n"

    return desc

def create_backlog():
    # 1. Check if file exists
    if not os.path.exists(STORIES_FILE):
        print(f"❌ Error: Could not find {STORIES_FILE}")
        return

    # 2. Load data from JSON
    try:
        with open(STORIES_FILE, "r") as f:
            stories = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing JSON: {e}")
        return

    # Wrap single object in list if necessary
    if isinstance(stories, dict):
        stories = [stories]

    jira = get_jira_client()
    print(f"🚀 Connecting to JIRA Project: {PROJECT_KEY}...")
    print(f"📂 Found {len(stories)} stories in {STORIES_FILE}")

    # 3. Process Tickets
    for story_data in stories:
        # Prepare the fields dictionary
        fields = {
            "summary": story_data.get("summary"),
            "issuetype": story_data.get("issuetype", {"name": "Story"}),
            "labels": story_data.get("labels", []),
            "description": story_data.get("description", "")
        }

        # Format description if detailed structure is used
        if "details" in story_data:
            fields["description"] = format_description(story_data["details"])
            
        # Add priority if present
        if "priority" in story_data:
             fields["priority"] = story_data["priority"]

        # --- UPDATE vs CREATE LOGIC ---
        
        # 1. Check if a specific KEY is provided (e.g., "DM-12")
        if "key" in story_data:
            issue_key = story_data["key"]
            print(f"🔄 Updating existing ticket: {issue_key}...")
            try:
                issue = jira.issue(issue_key)
                issue.update(fields=fields)
                print(f"✅ Successfully updated {issue_key}")
            except Exception as e:
                print(f"❌ Failed to update {issue_key}: {e}")

        # 2. If no key, CREATE a new one
        else:
            fields["project"] = {"key": PROJECT_KEY}
            try:
                new_issue = jira.create_issue(fields=fields)
                print(f"✨ Created New Ticket: {new_issue.key}")
            except Exception as e:
                print(f"❌ Failed to create {fields['summary']}: {e}")

def transition_ticket(ticket_id, target_status="Done"):
    jira = get_jira_client()
    print(f"🕵️ Looking for {ticket_id}...")
    
    try:
        issue = jira.issue(ticket_id)
        transitions = jira.transitions(issue)
        target_id = None
        
        print(f"📋 Available Transitions for {ticket_id}:")
        for t in transitions:
            print(f"   - {t['name']} (ID: {t['id']})")
            if t['name'].lower() == target_status.lower():
                target_id = t['id']

        if target_id:
            jira.transition_issue(issue, target_id)
            print(f"✅ Success! {ticket_id} moved to '{target_status}'.")
        else:
            print(f"❌ Error: Could not find transition '{target_status}'.")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command.lower() == "create":
            create_backlog()
        else:
            ticket_id = command
            status = sys.argv[2] if len(sys.argv) > 2 else "Done"
            transition_ticket(ticket_id, status)
    else:
        print("⚠️  Usage:")
        print("   1. Create/Update Backlog:   python scripts/sync_jira.py create")
        print("   2. Move Ticket Status:      python scripts/sync_jira.py [TICKET_ID] [STATUS]")