# DiamondMind JIRA Automation Guide

**Last Updated:** 2026-01-11  
**Script:** `backend/scripts/sync_jira.py`

---

## Overview

The JIRA sync script automates ticket creation, updates, and management for DiamondMind. It supports creating new stories, updating existing ones, changing ticket status, and exporting backlog data.

**Key Features:**
- Smart sync (auto-detect create vs update)
- Dry-run mode for safe previews
- Batch operations
- Status transitions
- Backlog export

---

## Setup

### Prerequisites

1. **JIRA Account** with API access
2. **API Token** from JIRA
3. **Environment Variables** configured

### Environment Configuration

Create `.env` file in `backend/` directory:

```env
JIRA_URL=https://your-domain.atlassian.net
JIRA_EMAIL=your-email@example.com
JIRA_API_TOKEN=your_api_token_here
PROJECT_KEY=DM
```

**Get API Token:**
1. Go to https://id.atlassian.com/manage-profile/security/api-tokens
2. Click "Create API token"
3. Copy token to `.env` file

### Verify Setup

```powershell
cd backend\scripts
python sync_jira.py --help
```

Should show command help without errors.

---

## Commands Reference

### 1. sync - Smart Sync (Recommended)

Automatically creates new stories or updates existing ones based on `key` field.

**Usage:**
```powershell
python sync_jira.py sync [file] [--dry-run]
```

**Examples:**
```powershell
# Sync default stories.json
python sync_jira.py sync

# Sync specific file
python sync_jira.py sync dm15_update.json

# Preview changes (no modifications)
python sync_jira.py sync stories.json --dry-run
```

**When to use:**
- Mixed batch of new and existing stories
- Unsure if stories exist in JIRA
- Want automatic detection

---

### 2. create - Create New Stories

Creates only stories without a `key` field. Skips stories that have keys.

**Usage:**
```powershell
python sync_jira.py create [file] [--dry-run]
```

**Examples:**
```powershell
# Create from default file
python sync_jira.py create

# Create from specific file
python sync_jira.py create new_features.json

# Preview what would be created
python sync_jira.py create new_features.json --dry-run
```

**When to use:**
- Creating multiple new stories
- Want explicit control (no updates)
- Batch story creation

---

### 3. update - Update Existing Stories

Updates only stories that have a `key` field. Skips stories without keys.

**Usage:**
```powershell
python sync_jira.py update [file] [--dry-run]
```

**Examples:**
```powershell
# Update from default file
python sync_jira.py update

# Update specific story
python sync_jira.py update dm15_complete.json

# Preview changes
python sync_jira.py update dm15_complete.json --dry-run
```

**When to use:**
- Updating story details
- Marking stories complete
- Changing priorities/labels

---

### 4. transition - Change Ticket Status

Moves a ticket to a different status (Done, In Progress, etc.).

**Usage:**
```powershell
python sync_jira.py transition <ticket_id> [status]
```

**Examples:**
```powershell
# Move to Done (default)
python sync_jira.py transition DM-15

# Move to In Progress
python sync_jira.py transition DM-16 "In Progress"

# Move to Testing
python sync_jira.py transition DM-17 Testing
```

**Available Statuses:**
- To Do
- In Progress
- Testing
- Done
- Idea

---

### 5. fetch - Export Stories by Status

Fetch and export stories by status for planning and review.

**Usage:**
```powershell
python sync_jira.py fetch <status1> [status2...] [-o output_file]
```

**Examples:**
```powershell
# Fetch and print to console
python sync_jira.py fetch "To Do" "In Progress"

# Export to JSON file
python sync_jira.py fetch "To Do" "In Progress" "Idea" -o backlog.json

# Fetch completed stories
python sync_jira.py fetch "Done" -o completed.json

# Fetch single status
python sync_jira.py fetch "Testing" -o testing.json
```

**Output includes:**
- Story key, summary, status, priority
- Description and labels
- Total count
- Export timestamp

---

## JSON File Format

### Structure Overview

```json
{
  "defaults": {
    "priority": {"name": "Medium"},
    "labels": ["Backend", "Feature"],
    "issuetype": {"name": "Story"}
  },
  "stories": [
    {
      "summary": "Story title",
      "priority": {"name": "High"},
      "labels": ["Mobile"],
      "details": { ... }
    }
  ]
}
```

### Field Reference

#### Top-Level Fields

| Field | Required | Type | Description |
|-------|----------|------|-------------|
| `defaults` | No | Object | Default values for all stories |
| `stories` | Yes | Array | List of story objects |

#### Story Fields

| Field | Required | Type | Description |
|-------|----------|------|-------------|
| `key` | Update only | String | JIRA ticket ID (e.g., "DM-15") |
| `summary` | Yes | String | Story title |
| `priority` | No | Object | `{"name": "High/Medium/Low"}` |
| `labels` | No | Array | Tags (e.g., `["Backend", "Mobile"]`) |
| `issuetype` | No | Object | `{"name": "Story/Bug/Task"}` |
| `details` | Recommended | Object | Structured story details |

#### Details Object

| Field | Type | Description |
|-------|------|-------------|
| `user_story` | String | "As a [user], I want [goal]..." |
| `context` | String | Background and motivation |
| `acceptance_criteria` | Array | List of completion criteria |
| `technical_details` | Array | Implementation notes |
| `edge_cases` | Array | Edge cases and constraints |

---

## JSON Examples

### Example 1: Create New Story

```json
{
  "defaults": {
    "priority": {"name": "Medium"},
    "labels": ["Backend"]
  },
  "stories": [
    {
      "summary": "Add video compression endpoint",
      "priority": {"name": "High"},
      "labels": ["Backend", "Performance"],
      "details": {
        "user_story": "As a user, I want videos compressed before upload so that uploads are faster.",
        "context": "Large videos (50-100MB) cause slow uploads and memory issues on free tier.",
        "acceptance_criteria": [
          "Videos compressed to 720p",
          "File size reduced by 70%",
          "Processing time < 10s"
        ],
        "technical_details": [
          "Use FFmpeg for compression",
          "Target bitrate: 2.5 Mbps",
          "Maintain aspect ratio"
        ],
        "edge_cases": [
          "Videos already < 10MB - skip compression",
          "Compression fails - fallback to original",
          "Very short videos (< 1s) - handle gracefully"
        ]
      }
    }
  ]
}
```

### Example 2: Update Existing Story

```json
{
  "stories": [
    {
      "key": "DM-15",
      "summary": "User Profile System (COMPLETE)",
      "priority": {"name": "High"},
      "labels": ["Backend", "Mobile", "Complete"],
      "details": {
        "user_story": "As a user, I want to create a profile so that I can save my swing history.",
        "context": "Supabase authentication integrated. Users can sign up, log in, and manage profiles.",
        "acceptance_criteria": [
          "✅ User signup with email/password",
          "✅ User login with session persistence",
          "✅ Profile fields: age_group, handedness, height",
          "✅ Authenticated API endpoints",
          "✅ JWT token verification"
        ],
        "technical_details": [
          "✅ Supabase client integrated",
          "✅ Auth middleware for JWT verification",
          "✅ User auto-creation on first login",
          "✅ Profile endpoints (GET, PATCH)",
          "✅ Authenticated swings endpoint"
        ],
        "edge_cases": [
          "✅ Enum case mismatch fixed",
          "✅ Existing users must re-register",
          "✅ Email confirmation disabled for MVP"
        ]
      }
    }
  ]
}
```

### Example 3: Batch Create Multiple Stories

```json
{
  "defaults": {
    "priority": {"name": "Medium"},
    "labels": ["GenAI", "RAG"]
  },
  "stories": [
    {
      "summary": "Integrate Vector Database",
      "priority": {"name": "High"},
      "details": {
        "user_story": "As a developer, I want to store swing data in a vector database for semantic search.",
        "context": "Foundation for RAG and similarity search features.",
        "acceptance_criteria": [
          "Pinecone or Weaviate integrated",
          "Swing embeddings stored",
          "Metadata indexed"
        ]
      }
    },
    {
      "summary": "Implement RAG Pipeline",
      "priority": {"name": "High"},
      "details": {
        "user_story": "As a user, I want natural language coaching feedback.",
        "context": "Transform raw pose data into actionable coaching advice.",
        "acceptance_criteria": [
          "LLM integrated (OpenAI/Anthropic)",
          "Coaching knowledge base created",
          "Feedback quality > 4.5/5"
        ]
      }
    }
  ]
}
```

---

## Common Workflows

### Workflow 1: Update Single Story (Mark Complete)

**Scenario:** DM-15 is complete, update JIRA to reflect completion.

**Steps:**
1. Create `dm15_complete.json`:
```json
{
  "stories": [
    {
      "key": "DM-15",
      "summary": "User Profile System (COMPLETE)",
      "priority": {"name": "High"},
      "labels": ["Backend", "Mobile", "Complete"],
      "details": {
        "acceptance_criteria": [
          "✅ User signup",
          "✅ User login",
          "✅ Profile management"
        ]
      }
    }
  ]
}
```

2. Preview changes:
```powershell
python sync_jira.py update dm15_complete.json --dry-run
```

3. Apply update:
```powershell
python sync_jira.py update dm15_complete.json
```

4. Transition to Done:
```powershell
python sync_jira.py transition DM-15 Done
```

---

### Workflow 2: Create Feature Batch

**Scenario:** Planning Phase 2 GenAI features, create 5 new stories.

**Steps:**
1. Create `genai_features.json` with 5 stories (no `key` fields)

2. Preview:
```powershell
python sync_jira.py create genai_features.json --dry-run
```

3. Create all:
```powershell
python sync_jira.py create genai_features.json
```

4. Verify in JIRA dashboard

---

### Workflow 3: Sprint Planning

**Scenario:** Plan next sprint, export backlog and prioritize.

**Steps:**
1. Export current backlog:
```powershell
python sync_jira.py fetch "To Do" "Idea" -o backlog_20260111.json
```

2. Review exported JSON, identify priorities

3. Create sprint stories file with updated priorities

4. Sync changes:
```powershell
python sync_jira.py sync sprint_stories.json
```

---

### Workflow 4: Retrospective

**Scenario:** Sprint complete, document what was accomplished.

**Steps:**
1. Export completed stories:
```powershell
python sync_jira.py fetch "Done" -o sprint_complete.json
```

2. Review accomplishments

3. Update stories with lessons learned:
```json
{
  "stories": [
    {
      "key": "DM-15",
      "details": {
        "edge_cases": [
          "Learned: Enum case mismatch causes DB errors",
          "Learned: Supabase JWT verification requires service key"
        ]
      }
    }
  ]
}
```

4. Sync updates:
```powershell
python sync_jira.py update retrospective.json
```

---

## Best Practices

### File Organization

```
backend/scripts/
├── sync_jira.py           # Main script
├── stories.json           # Default file
├── dm15_complete.json     # Single story updates
├── genai_features.json    # Feature batches
└── backlog_20260111.json  # Exported backlogs
```

### Naming Conventions

- **Updates:** `dm{number}_{action}.json` (e.g., `dm15_complete.json`)
- **Batches:** `{feature}_{type}.json` (e.g., `genai_features.json`)
- **Exports:** `{type}_{date}.json` (e.g., `backlog_20260111.json`)

### Safety Tips

1. **Always dry-run first:**
   ```powershell
   python sync_jira.py sync stories.json --dry-run
   ```

2. **Use specific commands for clarity:**
   - `create` when you know stories are new
   - `update` when you know stories exist
   - `sync` when unsure

3. **Keep backups:**
   - Export before major changes
   - Version control JSON files

4. **Validate JSON:**
   - Use JSON validator before running
   - Check for required fields

---

## Troubleshooting

### Issue: "Missing required field 'summary'"

**Cause:** Story object missing `summary` field

**Solution:**
```json
{
  "stories": [
    {
      "summary": "Add story title here",  // ← Required!
      "details": { ... }
    }
  ]
}
```

### Issue: "Update requires 'key' field"

**Cause:** Using `update` command without `key` in story

**Solution:**
- Add `"key": "DM-XX"` to story object
- Or use `create` command instead

### Issue: "Story already exists"

**Cause:** Trying to create story with duplicate summary

**Solution:**
- Use `update` command with existing key
- Or change summary to be unique

### Issue: "Invalid authentication credentials"

**Cause:** Missing or incorrect JIRA credentials in `.env`

**Solution:**
1. Verify `.env` file exists in `backend/`
2. Check `JIRA_URL`, `JIRA_EMAIL`, `JIRA_API_TOKEN`
3. Regenerate API token if needed

---

## Advanced Usage

### Custom Issue Types

```json
{
  "stories": [
    {
      "summary": "Fix skeleton jitter bug",
      "issuetype": {"name": "Bug"},
      "priority": {"name": "Highest"}
    }
  ]
}
```

### Multiple Labels

```json
{
  "defaults": {
    "labels": ["Backend", "Mobile"]
  },
  "stories": [
    {
      "summary": "Cross-platform feature",
      "labels": ["Backend", "Mobile", "AI"]  // Merges with defaults
    }
  ]
}
```

### Minimal Story (Quick Create)

```json
{
  "stories": [
    {
      "summary": "Quick task to track"
    }
  ]
}
```

---

## Script Output Examples

### Successful Sync

```
🚀 Connecting to JIRA Project: DM...
📂 Found 3 stories to process.

✨ Created: Add video compression (DM-62)
✅ Updated DM-15
⚠️  Skipped 'Duplicate story': Story already exists as DM-10

📊 Summary:
   ✨ Created: 1
   ✅ Updated: 1
   ⚠️  Skipped: 1
   ❌ Errors: 0
```

### Dry Run

```
🔍 DRY RUN MODE - No changes will be made

   [DRY RUN] Would create: Add video compression
   [DRY RUN] Would update DM-15: User Profile System

📊 Summary: Created 1, Updated 1, Skipped 0
```

---

## Related Documentation

- **Features:** `FEATURES.md` - See what stories implement
- **Roadmap:** `PRODUCT_ROADMAP.md` - Sprint planning
- **Context:** `CONTEXT_DOC.md` - Technical details for stories
