from jira import JIRA
import os
from dotenv import load_dotenv

load_dotenv()

# CONFIGURATION
JIRA_URL = "https://diamondmind.atlassian.net/"
JIRA_EMAIL = "sous2817@gmail.com"
JIRA_TOKEN = os.getenv("JIRA_API_TOKEN") # Add this to your .env file

def create_tickets():
    print("🚀 Connecting to JIRA...")
    jira = JIRA(server=JIRA_URL, basic_auth=(JIRA_EMAIL, JIRA_TOKEN))
    
    project_key = "DM"
    
    stories = [
            {
                "summary": "Feature: Display Timestamps in History",
                "description": "As a user, I want to see WHEN I took the swing (e.g., 'Dec 23, 10:30 AM') so I can differentiate sessions.",
                "issuetype": {"name": "Story"},
            }
        ]
    
    for story in stories:
        story["project"] = project_key
        new_issue = jira.create_issue(fields=story)
        print(f"✅ Created Ticket: {new_issue.key}")

if __name__ == "__main__":
    create_tickets()