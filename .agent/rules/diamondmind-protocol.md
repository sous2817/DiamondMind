---
trigger: always_on
---

1. **First Inspection Rule**: Before modifying a file for the first time in a session, use `view_file` to see its current state
2. **No Assumptions**: Never generate full file replacements without seeing the source code  
3. **Log Preservation**: Preserve existing logging unless it contradicts new logic
4. **PowerShell Environment**: Use PowerShell syntax (backslashes for paths), not bash
5. **Quick Context**: For new sessions, read `docs/AI_CONTEXT.md` first
6. **Victory Lap**: After completing JIRA stories, update `docs/CONTEXT_DOC.md` with new architectural decisions, tribal knowledge, and API changes
7. **JIRA ticket creation**:  Before any new feature implementation, verify if a JIRA story should be created.  If it should 