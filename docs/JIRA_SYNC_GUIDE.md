# JIRA Sync Script - Usage Guide

## Overview

Enhanced JIRA sync script with separate commands for creating, updating, and syncing stories.

## Commands

### 1. **sync** - Smart Sync (Recommended)
Automatically creates new stories or updates existing ones based on presence of `key` field.

```powershell
# Sync default stories.json
python scripts/sync_jira.py sync

# Sync specific file
python scripts/sync_jira.py sync scripts/dm10_update.json

# Dry run (preview changes)
python scripts/sync_jira.py sync scripts/stories.json --dry-run
```

### 2. **create** - Create New Stories Only
Creates only stories without a `key` field. Skips stories that have a `key`.

```powershell
# Create from default file
python scripts/sync_jira.py create

# Create from specific file
python scripts/sync_jira.py create scripts/new_stories.json

# Dry run
python scripts/sync_jira.py create scripts/new_stories.json --dry-run
```

### 3. **update** - Update Existing Stories Only
Updates only stories that have a `key` field. Skips stories without a `key`.

```powershell
# Update from default file
python scripts/sync_jira.py update

# Update specific story
python scripts/sync_jira.py update scripts/dm10_update.json

# Dry run (preview changes)
python scripts/sync_jira.py update scripts/dm10_update.json --dry-run
```

### 4. **transition** - Change Ticket Status
Moves a ticket to a different status (e.g., Done, In Progress).

```powershell
# Move to Done
python scripts/sync_jira.py transition DM-10 Done

# Move to In Progress
python scripts/sync_jira.py transition DM-10 "In Progress"
```

## JSON File Format

### Creating New Stories (no `key` field)
```json
{
  "defaults": {
    "priority": {"name": "Medium"},
    "labels": ["Backend", "Feature"]
  },
  "stories": [
    {
      "summary": "New Feature Story",
      "details": {
        "user_story": "As a user...",
        "context": "Background info...",
        "acceptance_criteria": ["Criterion 1", "Criterion 2"],
        "technical_details": ["Detail 1", "Detail 2"],
        "edge_cases": ["Edge case 1"]
      }
    }
  ]
}
```

### Updating Existing Stories (with `key` field)
```json
{
  "stories": [
    {
      "key": "DM-10",
      "summary": "Updated Summary",
      "priority": {"name": "High"},
      "details": {
        "user_story": "Updated story...",
        "acceptance_criteria": ["✅ Done", "✅ Complete"]
      }
    }
  ]
}
```

## Features

✅ **Separate Commands** - Explicit create/update/sync operations
✅ **File Path Arguments** - Use any JSON file, not just stories.json
✅ **Dry Run Mode** - Preview changes before applying with `--dry-run`
✅ **Validation** - Checks for required fields before API calls
✅ **Better Error Messages** - Clear feedback on what failed and why
✅ **Summary Stats** - Shows count of created/updated/skipped/errors

## Common Workflows

### Workflow 1: Update Single Story
```powershell
# 1. Create update file (e.g., dm10_update.json) with "key" field
# 2. Preview changes
python scripts/sync_jira.py update scripts/dm10_update.json --dry-run

# 3. Apply changes
python scripts/sync_jira.py update scripts/dm10_update.json
```

### Workflow 2: Create Multiple New Stories
```powershell
# 1. Create stories.json with multiple stories (no "key" fields)
# 2. Preview
python scripts/sync_jira.py create --dry-run

# 3. Create all
python scripts/sync_jira.py create
```

### Workflow 3: Mixed Create and Update
```powershell
# 1. Create stories.json with mix of stories (some with "key", some without)
# 2. Use sync command (smart mode)
python scripts/sync_jira.py sync scripts/stories.json
```

## Tips

- **Always use `--dry-run` first** to preview changes
- **Use `sync` for mixed operations** (creates new, updates existing)
- **Use `create` or `update` for explicit control** over what happens
- **Keep separate files** for different batches of updates (e.g., `dm10_update.json`, `new_features.json`)
