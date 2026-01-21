from jira import JIRA
import os
import json
import sys
from dotenv import load_dotenv
import argparse

# Load environment variables
load_dotenv()

# --- CONFIGURATION ---
JIRA_URL = os.getenv("JIRA_URL")
JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_TOKEN = os.getenv("JIRA_API_TOKEN")
PROJECT_KEY = os.getenv("PROJECT_KEY")

# ✅ FIX: Use relative path (works on any machine)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_STORIES_FILE = os.path.join(BASE_DIR, "stories.json")

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

def validate_story_structure(story_data, index):
    """
    Validates that a story has required fields.
    Returns (is_valid, error_message)
    """
    if not story_data.get("summary"):
        return False, f"Story #{index}: Missing required field 'summary'"
    
    # If updating, must have key
    if story_data.get("_action") == "update" and not story_data.get("key"):
        return False, f"Story #{index}: Update requires 'key' field"
    
    return True, None

def load_stories_file(file_path):
    """
    Loads and validates JSON file.
    Returns (stories, defaults) or (None, None) on error.
    """
    if not os.path.exists(file_path):
        print(f"❌ Error: Could not find {file_path}")
        return None, None

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing JSON: {e}")
        return None, None

    # Handle new structure vs legacy list
    if isinstance(data, list):
        stories = data
        defaults = {}
    else:
        stories = data.get("stories", [])
        defaults = data.get("defaults", {})
    
    return stories, defaults

def build_issue_fields(story_data, defaults):
    """
    Builds JIRA issue fields from story data and defaults.
    """
    summary = story_data.get("summary")
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
    
    return fields

def check_if_exists(jira, summary):
    """
    ✅ IDEMPOTENCY CHECK: Returns existing issue if found, else None.
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

def create_story(jira, story_data, defaults, dry_run=False):
    """
    Creates a new JIRA story.
    Returns (success, issue_key_or_error)
    """
    summary = story_data.get("summary")
    
    # Check if already exists
    existing_issue = check_if_exists(jira, summary)
    if existing_issue:
        return False, f"Story already exists as {existing_issue.key}"
    
    fields = build_issue_fields(story_data, defaults)
    
    if dry_run:
        print(f"   [DRY RUN] Would create: {summary}")
        return True, "DRY-RUN"
    
    try:
        new_issue = jira.create_issue(fields=fields)
        return True, new_issue.key
    except Exception as e:
        return False, str(e)

def update_story(jira, story_data, defaults, dry_run=False):
    """
    Updates an existing JIRA story by key.
    Returns (success, message)
    """
    issue_key = story_data.get("key")
    summary = story_data.get("summary")
    
    if not issue_key:
        return False, "Missing 'key' field for update"
    
    fields = build_issue_fields(story_data, defaults)
    # Remove project key from update (can't change project)
    fields.pop("project", None)
    
    if dry_run:
        print(f"   [DRY RUN] Would update {issue_key}: {summary}")
        return True, "DRY-RUN"
    
    try:
        issue = jira.issue(issue_key)
        issue.update(fields=fields)
        return True, f"Updated {issue_key}"
    except Exception as e:
        return False, str(e)

def sync_stories(file_path=None, dry_run=False):
    """
    Smart sync: Creates new stories or updates existing ones based on 'key' field.
    """
    file_path = file_path or DEFAULT_STORIES_FILE
    stories, defaults = load_stories_file(file_path)
    
    if stories is None:
        return
    
    jira = get_jira_client()
    print(f"🚀 Connecting to JIRA Project: {PROJECT_KEY}...")
    print(f"📂 Found {len(stories)} stories to process.")
    if dry_run:
        print("🔍 DRY RUN MODE - No changes will be made\n")
    
    created_count = 0
    updated_count = 0
    skipped_count = 0
    error_count = 0
    
    for idx, story_data in enumerate(stories, 1):
        # Validate story structure
        is_valid, error_msg = validate_story_structure(story_data, idx)
        if not is_valid:
            print(f"❌ {error_msg}")
            error_count += 1
            continue
        
        summary = story_data.get("summary")
        
        # Determine action: update if has key, create otherwise
        if "key" in story_data:
            # Update existing
            success, message = update_story(jira, story_data, defaults, dry_run)
            if success:
                print(f"✅ {message}")
                updated_count += 1
            else:
                print(f"❌ Failed to update '{summary}': {message}")
                error_count += 1
        else:
            # Create new
            success, result = create_story(jira, story_data, defaults, dry_run)
            if success:
                print(f"✨ Created: {summary} ({result})")
                created_count += 1
            else:
                print(f"⚠️  Skipped '{summary}': {result}")
                skipped_count += 1
    
    # Summary
    print(f"\n📊 Summary:")
    print(f"   ✨ Created: {created_count}")
    print(f"   ✅ Updated: {updated_count}")
    print(f"   ⚠️  Skipped: {skipped_count}")
    print(f"   ❌ Errors: {error_count}")

def create_stories_only(file_path=None, dry_run=False):
    """
    Creates only new stories (skips stories with 'key' field).
    """
    file_path = file_path or DEFAULT_STORIES_FILE
    stories, defaults = load_stories_file(file_path)
    
    if stories is None:
        return
    
    jira = get_jira_client()
    print(f"🚀 Connecting to JIRA Project: {PROJECT_KEY}...")
    print(f"📂 Found {len(stories)} stories to process (CREATE mode).")
    if dry_run:
        print("🔍 DRY RUN MODE - No changes will be made\n")
    
    created_count = 0
    skipped_count = 0
    
    for idx, story_data in enumerate(stories, 1):
        # Skip stories with keys (those are for updates)
        if "key" in story_data:
            print(f"⏭️  Skipping '{story_data.get('summary')}' (has key, use 'update' command)")
            skipped_count += 1
            continue
        
        is_valid, error_msg = validate_story_structure(story_data, idx)
        if not is_valid:
            print(f"❌ {error_msg}")
            skipped_count += 1
            continue
        
        success, result = create_story(jira, story_data, defaults, dry_run)
        if success:
            print(f"✨ Created: {story_data.get('summary')} ({result})")
            created_count += 1
        else:
            print(f"⚠️  Skipped '{story_data.get('summary')}': {result}")
            skipped_count += 1
    
    print(f"\n📊 Summary: Created {created_count}, Skipped {skipped_count}")

def update_stories_only(file_path=None, dry_run=False):
    """
    Updates only existing stories (requires 'key' field).
    """
    file_path = file_path or DEFAULT_STORIES_FILE
    stories, defaults = load_stories_file(file_path)
    
    if stories is None:
        return
    
    jira = get_jira_client()
    print(f"🚀 Connecting to JIRA Project: {PROJECT_KEY}...")
    print(f"📂 Found {len(stories)} stories to process (UPDATE mode).")
    if dry_run:
        print("🔍 DRY RUN MODE - No changes will be made\n")
    
    updated_count = 0
    skipped_count = 0
    
    for idx, story_data in enumerate(stories, 1):
        # Skip stories without keys
        if "key" not in story_data:
            print(f"⏭️  Skipping '{story_data.get('summary')}' (no key, use 'create' command)")
            skipped_count += 1
            continue
        
        is_valid, error_msg = validate_story_structure(story_data, idx)
        if not is_valid:
            print(f"❌ {error_msg}")
            skipped_count += 1
            continue
        
        success, message = update_story(jira, story_data, defaults, dry_run)
        if success:
            print(f"✅ {message}")
            updated_count += 1
        else:
            print(f"❌ Failed: {message}")
            skipped_count += 1
    
    print(f"\n📊 Summary: Updated {updated_count}, Skipped {skipped_count}")

def transition_ticket(ticket_id, target_status="Done"):
    """
    Transitions a ticket to a different status.
    """
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

def fetch_stories(statuses, output_file=None):
    """
    Fetch JIRA stories by status and optionally export to JSON.
    """
    from datetime import datetime
    
    jira = get_jira_client()
    
    # Build JQL query
    status_list = "', '".join(statuses)
    jql = f"project = {PROJECT_KEY} AND status IN ('{status_list}') ORDER BY created DESC"
    
    print(f"🔍 Fetching stories with status: {', '.join(statuses)}")
    print(f"📝 JQL: {jql}\n")
    
    try:
        issues = jira.search_issues(jql, maxResults=100)
        
        if not issues:
            print(f"❌ No stories found")
            return
        
        print(f"✅ Found {len(issues)} stories\n")
        
        # Convert to structured format
        stories = []
        for issue in issues:
            story = {
                "key": issue.key,
                "summary": issue.fields.summary,
                "status": issue.fields.status.name,
                "priority": issue.fields.priority.name if issue.fields.priority else "Medium",
            }
            
            # Add description if available
            if hasattr(issue.fields, 'description') and issue.fields.description:
                story["description"] = issue.fields.description
            
            # Add labels if available
            if hasattr(issue.fields, 'labels') and issue.fields.labels:
                story["labels"] = issue.fields.labels
            
            stories.append(story)
            
            # Print summary
            print(f"📌 {issue.key}: {issue.fields.summary}")
            print(f"   Status: {issue.fields.status.name} | Priority: {story['priority']}")
            print()
        
        # Export to JSON if output file specified or use default
        if output_file or len(stories) > 0:
            timestamp = datetime.now().strftime("%Y%m%d")
            
            # Generate default filename with timestamp if not provided
            if not output_file:
                status_slug = "_".join([s.lower().replace(" ", "_") for s in statuses[:2]])  # Use first 2 statuses
                output_file = f"jira_export_{status_slug}_{timestamp}.json"
            else:
                # Add timestamp to custom filename (before .json extension)
                base_name = output_file.replace('.json', '')
                output_file = f"{base_name}_{timestamp}.json"
            
            # Ensure output goes to docs folder (project root/docs)
            # BASE_DIR is backend/scripts, so go up 2 levels to project root
            project_root = os.path.dirname(os.path.dirname(BASE_DIR))
            docs_dir = os.path.join(project_root, "docs")
            
            # Create docs dir if it doesn't exist
            os.makedirs(docs_dir, exist_ok=True)
            
            # Use only basename if full path provided
            if not output_file.startswith(docs_dir):
                output_file = os.path.join(docs_dir, os.path.basename(output_file))
            
            with open(output_file, 'w') as f:
                json.dump({"stories": stories, "total": len(stories), "exported_at": str(datetime.now())}, f, indent=2)
            print(f"\n💾 Exported {len(stories)} stories to {output_file}")
        
        return stories
        
    except Exception as e:
        print(f"❌ Error fetching stories: {e}")

def main():
    parser = argparse.ArgumentParser(
        description="JIRA Story Sync Tool - Create, update, or transition JIRA stories",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Smart sync (create new, update existing)
  python sync_jira.py sync stories.json
  
  # Create only new stories
  python sync_jira.py create stories.json
  
  # Update only existing stories
  python sync_jira.py update dm10_update.json
  
  # Dry run (preview changes)
  python sync_jira.py update dm10_update.json --dry-run
  
  # Transition ticket status
  python sync_jira.py transition DM-10 Done
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Sync command
    sync_parser = subparsers.add_parser("sync", help="Smart sync: create new or update existing stories")
    sync_parser.add_argument("file", nargs="?", default=DEFAULT_STORIES_FILE, help="JSON file path")
    sync_parser.add_argument("--dry-run", action="store_true", help="Preview changes without applying")
    
    # Create command
    create_parser = subparsers.add_parser("create", help="Create only new stories")
    create_parser.add_argument("file", nargs="?", default=DEFAULT_STORIES_FILE, help="JSON file path")
    create_parser.add_argument("--dry-run", action="store_true", help="Preview changes without applying")
    
    # Update command
    update_parser = subparsers.add_parser("update", help="Update only existing stories (requires 'key' field)")
    update_parser.add_argument("file", nargs="?", default=DEFAULT_STORIES_FILE, help="JSON file path")
    update_parser.add_argument("--dry-run", action="store_true", help="Preview changes without applying")
    
    # Transition command
    transition_parser = subparsers.add_parser("transition", help="Change ticket status")
    transition_parser.add_argument("ticket_id", help="JIRA ticket ID (e.g., DM-10)")
    transition_parser.add_argument("status", nargs="?", default="Done", help="Target status (default: Done)")
    
    # Fetch command
    fetch_parser = subparsers.add_parser("fetch", help="Fetch stories by status")
    fetch_parser.add_argument("statuses", nargs="+", help="Status names (e.g., 'To Do' 'In Progress' 'Idea')")
    fetch_parser.add_argument("-o", "--output", help="Output JSON file path")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Execute command
    if args.command == "sync":
        sync_stories(args.file, args.dry_run)
    elif args.command == "create":
        create_stories_only(args.file, args.dry_run)
    elif args.command == "update":
        update_stories_only(args.file, args.dry_run)
    elif args.command == "transition":
        transition_ticket(args.ticket_id, args.status)
    elif args.command == "fetch":
        fetch_stories(args.statuses, args.output)

if __name__ == "__main__":
    main()