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
PROJECT_KEY = "DM" 
STORIES_FILE = "scripts/stories.json"  # Point to your new file

if not JIRA_URL or not JIRA_EMAIL or not JIRA_TOKEN:
    print("❌ Error: Missing JIRA credentials in .env file")
    sys.exit(1)

def get_jira_client():
    return JIRA(server=JIRA_URL, basic_auth=(JIRA_EMAIL, JIRA_TOKEN))

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

    jira = get_jira_client()
    print(f"🚀 Connecting to JIRA Project: {PROJECT_KEY}...")
    print(f"📂 Found {len(stories)} stories in {STORIES_FILE}")
    
    # 3. Create Tickets
    for story in stories:
        story["project"] = PROJECT_KEY
        try:
            new_issue = jira.create_issue(fields=story)
            print(f"✅ Created: {new_issue.key} - {story['summary']}")
        except Exception as e:
            print(f"❌ Failed to create {story['summary']}: {e}")

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
        print("   1. Create Backlog:   python scripts/sync_jira.py create")
        print("   2. Update Ticket:    python scripts/sync_jira.py [TICKET_ID] [STATUS]")