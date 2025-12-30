from jira import JIRA
import os
import json
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- CONFIGURATION ---
JIRA_URL = os.getenv("JIRA_URL")
JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_TOKEN = os.getenv("JIRA_API_TOKEN")
PROJECT_KEY = os.getenv("PROJECT_KEY")

# ✅ FIX: Use relative path (works on any machine)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STORIES_FILE = os.path.join(BASE_DIR, "stories.json")

# Validate critical env vars
if not all([JIRA_URL, JIRA_EMAIL, JIRA_TOKEN, PROJECT_KEY]):
    print("❌ Error: Missing JIRA credentials or PROJECT_KEY in .env file")
    sys.exit(1)

def get_jira_client():
    return JIRA(server=JIRA_URL, basic_auth=(JIRA_EMAIL, JIRA_TOKEN))

def format_description(details):
    """
    Converts a structured dictionary into a JIRA-formatted string.
    """
    desc = ""

    if "user_story" in details:
        desc += "{panel:title=User Story|bgColor=#EAE6FF}\n" + details["user_story"] + "\n{panel}\n\n"

    if "context" in details:
        desc += "h3. 🧠 Context & Goal\n" + details["context"] + "\n\n"

    if "acceptance_criteria" in details:
        desc += "h3. ✅ Acceptance Criteria (Definition of Done)\n"
        for item in details["acceptance_criteria"]:
            desc += f"* {item}\n"
        desc += "\n"

    if "technical_details" in details:
        desc += "h3. ⚙️ Technical Implementation Details\n"
        for item in details["technical_details"]:
            desc += f"* {item}\n"
        desc += "\n"

    if "edge_cases" in details:
        desc += "h3. ⚠️ Edge Cases & Constraints\n"
        for item in details["edge_cases"]:
            desc += f"* {item}\n"
        desc += "\n"

    return desc

def check_if_exists(jira, summary):
    """
    ✅ IDEMPOTENCY CHECK: Returns existing issue key if found, else None.
    """
    # Escape quotes for JQL
    safe_summary = summary.replace('"', '\\"')
    jql = f'project = "{PROJECT_KEY}" AND summary ~ "{safe_summary}"'
    
    results = jira.search_issues(jql)
    
    # Double-check exact string match to avoid fuzzy false positives
    for issue in results:
        if issue.fields.summary == summary:
            return issue
    return None

def create_backlog():
    if not os.path.exists(STORIES_FILE):
        print(f"❌ Error: Could not find {STORIES_FILE}")
        return

    try:
        with open(STORIES_FILE, "r") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing JSON: {e}")
        return

    # Handle new structure vs legacy list
    if isinstance(data, list):
        stories = data
        defaults = {}
    else:
        stories = data.get("stories", [])
        defaults = data.get("defaults", {})

    jira = get_jira_client()
    print(f"🚀 Connecting to JIRA Project: {PROJECT_KEY}...")
    print(f"📂 Found {len(stories)} stories to process.")

    for story_data in stories:
        # Merge defaults with specific story data
        summary = story_data.get("summary")
        if not summary:
            print("❌ Skipping invalid story: Missing 'summary'")
            continue

        issuetype = story_data.get("issuetype", defaults.get("issuetype", {"name": "Story"}))
        priority = story_data.get("priority", defaults.get("priority", {"name": "Medium"}))
        
        # Merge labels (unique values)
        default_labels = defaults.get("labels", [])
        story_labels = story_data.get("labels", [])
        combined_labels = list(set(default_labels + story_labels))

        fields = {
            "project": {"key": PROJECT_KEY},
            "summary": summary,
            "issuetype": issuetype,
            "priority": priority,
            "labels": combined_labels,
            "description": story_data.get("description", "")
        }

        if "details" in story_data:
            fields["description"] = format_description(story_data["details"])

        # --- EXECUTION ---
        
        # 1. Update existing by Key
        if "key" in story_data:
            issue_key = story_data["key"]
            print(f"🔄 Updating explicitly defined ticket: {issue_key}...")
            try:
                jira.issue(issue_key).update(fields=fields)
                print(f"✅ Updated {issue_key}")
            except Exception as e:
                print(f"❌ Failed update {issue_key}: {e}")
        
        # 2. Idempotency Check (Prevent Duplicates)
        else:
            existing_issue = check_if_exists(jira, summary)
            if existing_issue:
                print(f"⚠️  Skipping: '{summary}' already exists as {existing_issue.key}")
            else:
                # 3. Create New
                try:
                    new_issue = jira.create_issue(fields=fields)
                    print(f"✨ Created New Ticket: {new_issue.key}")
                except Exception as e:
                    print(f"❌ Failed to create '{summary}': {e}")

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