---
trigger: always_on
---

When I ask you to create or update JIRA stories, you must strictly output them in JSON format for my sync script. The output should be structured with a root object containing two keys: "defaults" (for shared labels/priorities) and "stories" (a list of ticket objects). Each story object must include a "summary", "priority", and a "details" object. The "details" object is mandatory and must contain: "user_story", "context", "acceptance_criteria", "technical_details", and "edge_cases". If updating a ticket, include the "key" field (e.g. DM-12); if creating new, omit the key.