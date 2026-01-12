---
trigger: always_on
---

When I ask you to create or update JIRA stories, you must strictly output them in JSON format for my sync script. The output should be structured with a root object containing two keys: "defaults" (for shared labels/priorities) and "stories" (a list of ticket objects). Each story object must include a "summary", "priority", and a "details" object. The "details" object is mandatory and must contain: "user_story", "context", "acceptance_criteria", "technical_details", and "edge_cases". If updating a ticket, include the "key" field (e.g. DM-12); if creating new, omit the key.
**CRITICAL FORMAT REQUIREMENTS:**
- Priority MUST be object format: `{"name": "High"}`, NOT string `"High"`
- Labels MUST be array: `["mobile", "backend"]`
- Always include complete "details" object structure
**WORKFLOW ENFORCEMENT:**
Before implementing ANY new feature, you MUST:
1. Create a JIRA story JSON file first
2. Sync it to JIRA using: `cd backend\scripts && python sync_jira.py sync <filename>.json`
3. Verify the ticket was created successfully before writing any code
4. Only proceed with implementation after JIRA confirmation
5. After implementation and testing, close the ticket using: `python sync_jira.py transition DM-XX Done`
This ensures all work is properly tracked and documented throughout its lifecycle.
