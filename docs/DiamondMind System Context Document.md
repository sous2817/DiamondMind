# DiamondMind Master Context (v2.3)

## 1. Engagement Protocol (AI Instructions)

### Code Sync Rule

I (The AI) start this session with zero knowledge of your local file contents.

- **The "First Touch" Rule:** Before modifying a file for the first time in this session, I MUST ask you to paste its current content.
- **State Retention:** Once you provide the code, I will maintain its state in my context. I will only ask for it again if we have drifted significantly or you modified it externally.
- **No Assumptions:** I will never generate full file replacements without having seen the source code at least once in the current session.

### The "Victory Lap" Reminder

At the end of every JIRA Story or major bug fix, I must run the following prompt:

> "Review the work we completed in this session. Compare it against the current Master Context Document. Update the document to include:
> - New Architectural Decisions (Section 2)
> - New Tribal Knowledge (Section 3)
> - Changes to Paths/URLs/Envs (Section 4)
> - Updates to API Contracts & Endpoints (Section 8)
> - Changes to Data Flow Architecture (Section 9)
> - Updates to Error Patterns - Mobile App & Backend (Section 10)
> - Changes to Storage & Persistence (Section 11)
> - Authentication & Security updates (Section 12)
> - Updates to Performance & Constraints (Section 13)
> - Changes to Testing Strategy (Section 14)
> - Dependency Version updates (Section 15)
> - Any new Important Notes
> 
> Output the full, updated Markdown file."

---

## 2. Project Identity & Stack

- **Name:** DiamondMind
- **Goal:** AI-driven Baseball Analytics (Mobile Video Analysis)
- **Repo Type:** Monorepo (Windows Environment)

### Microservices Architecture

We split the backend to prevent memory crashes on the Free Tier and to isolate heavy dependencies.

| Service | Role | Tech Stack | Location |
|---------|------|------------|----------|
| Mobile App | Client | React Native (Expo SDK 52) | `diamondmind-mobile/` |
| API Gateway | Orchestrator | Python FastAPI (Native) | `backend/` |
| AI Worker | Compute Engine | Python 3.12 + MediaPipe (Docker) | `ai-service/` |

### Directory Structure (Map)

**📁 Required File:** `project_map.txt`

This context document references a separate file containing the complete project structure. If you don't have `project_map.txt`, please:

1. Generate it using the script in Section 7
2. Provide it to me so I can understand the current file organization
3. Keep it updated when major structural changes occur

**AI Agent Note:** If `project_map.txt` has not been provided in this session, ask the user to share it before making any file-related recommendations or modifications.

---

## 3. "Tribal Knowledge" (Critical Fixes)

These are non-standard implementations required to make the system work. Do not refactor these without understanding the history.

### A. Mobile Uploads (The "Legacy" Fix)

**Problem:** Expo SDK 52 broke the standard `FileSystem.uploadAsync` for binary multipart.

**The Fix:** We use the legacy sub-package and integer constants.

**Code Pattern (Required):**

```javascript
import * as FileSystem from 'expo-file-system/legacy'; // <--- MUST be legacy
// ...
uploadType: 1, // <--- MUST be Integer 1 (Multipart), NOT the Enum
```

### B. Backend Memory (The "Streaming" Fix)

**Problem:** Render Free Tier (512MB RAM) crashes if FastAPI reads a video into memory (`await file.read()`).

**The Fix:** We use a generator to stream the file chunk-by-chunk from Mobile → Backend → AI Service.

**Rule:** Never use `file.read()` for video files in `backend/main.py`.

### C. The "Cold Start" Timeout

**Problem:** Render services sleep after 15 minutes. The wake-up time (>60s) causes the Mobile App to throw `[Error: timeout]`.

**Protocol:** Before testing a new build, manually visit the Swagger docs of both services to wake them up.

---

## 4. "Hardcoded" Wiring & Configuration

If these variables do not match, the system fails silently.

| Variable | Current Live Value | Location |
|----------|-------------------|----------|
| `API_URL` | `https://diamondmind-backend-yalf.onrender.com` | `diamondmind-mobile/src/services/UploadService.js` |
| `AI_SERVICE_URL` | `https://dm-ai-service.onrender.com` | Render Dashboard → Backend Environment |
| `PORT` | `8001` (Exposed) | `ai-service/Dockerfile` |

---

## 5. Deployment / Rebuild Manual

Follow these exact specifications if redeploying to Render.

### Service 1: AI Worker (Deploy First)

- **Type:** Web Service (Docker Runtime)
- **Root Directory:** `ai-service`
- **Environment Variables:** `PORT=8001`
- **Build Context:** Must include `pose_landmarker_heavy.task` and `Dockerfile`
- **System Dependencies:** Dockerfile installs `libgl1` and `libglib2.0-0` (Required for OpenCV/MediaPipe)

### Service 2: API Gateway (Deploy Second)

- **Type:** Web Service (Native Python 3 Runtime)
- **Root Directory:** `backend`
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- **Environment Variables:**
  - `PYTHON_VERSION = 3.11.0`
  - `AI_SERVICE_URL = [URL of Service 1]`
- **Dependencies:** `requirements.txt` MUST include `opencv-python-headless` (to avoid libGL crashes) and `httpx`

---

## 6. Local Development Workflow (Onboarding)

How to run the stack on your local Windows machine.

### Option A: Hybrid (Recommended)

Run the Mobile App locally while pointing to cloud services.

1. Start the mobile app:
   ```powershell
   cd diamondmind-mobile
   npx expo start
   ```

2. Point it to Cloud Backend by setting `API_URL` to your Render URL

**Important:** If using a physical device, your phone must be on the same WiFi network as your PC (if running backend locally), or use the Cloud URL.

**Pros:** No need to run heavy Docker containers locally. Best for UI work.

### Option B: Full Local (Debugging)

Run all services locally for complete debugging control.

1. **AI Service:** Run via Docker Desktop
   ```powershell
   cd ai-service
   docker build -t dm-ai .
   docker run -p 8001:8001 dm-ai
   ```

2. **Backend:** Run via Uvicorn
   ```powershell
   cd backend
   $env:AI_SERVICE_URL="http://localhost:8001"
   uvicorn app.main:app --reload --port 8000
   ```

3. **Mobile App:** Update `API_URL` based on your environment:
   - **Android Emulator:** `http://10.0.2.2:8000`
   - **Physical Device:** `http://[YOUR_PC_LAN_IP]:8000`
   
   ```powershell
   cd diamondmind-mobile
   npx expo start
   ```

---

## 7. Project Structure Mapping

### The Script (`Generate-Map.ps1`)

You can copy/paste this entire block directly into your PowerShell terminal:

```powershell
function Show-ContextMap {
    param (
        [string]$Path = ".",
        [int]$MaxDepth = 4
    )

    # 🚫 Folders to Ignore
    $ExcludeList = @(
        "node_modules", 
        "venv", 
        ".git", 
        ".vscode", 
        "__pycache__", 
        "dist", 
        "build", 
        ".expo", 
        ".gradle",
        ".idea"
    )

    # Helper function for recursion
    function Print-Tree {
        param (
            [string]$CurrentPath,
            [string]$Indent,
            [int]$CurrentDepth
        )

        if ($CurrentDepth -ge $MaxDepth) { return }

        # Get items, filtering out the exclude list
        $items = Get-ChildItem -Path $CurrentPath | Where-Object { 
            $ExcludeList -notcontains $_.Name 
        }

        $count = $items.Count
        $i = 0

        foreach ($item in $items) {
            $i++
            $isLast = ($i -eq $count)
            $prefix = if ($isLast) { "└── " } else { "├── " }
            $childIndent = if ($isLast) { "    " } else { "│   " }

            # Print the item
            if ($item.PSIsContainer) {
                # Add a slash for directories to make it clear
                Write-Output "$Indent$prefix$($item.Name)/"
                
                # Recurse
                Print-Tree -CurrentPath $item.FullName -Indent ($Indent + $childIndent) -CurrentDepth ($CurrentDepth + 1)
            } else {
                Write-Output "$Indent$prefix$($item.Name)"
            }
        }
    }

    Write-Output "."
    Print-Tree -CurrentPath (Resolve-Path $Path) -Indent "" -CurrentDepth 0
}

# Ensure the output directory exists
$outputDir = "C:\dm\docs"
if (-not (Test-Path $outputDir)) {
    New-Item -ItemType Directory -Path $outputDir -Force | Out-Null
}

# Run it and save to a text file
$outputPath = Join-Path $outputDir "project_map.txt"
Show-ContextMap > $outputPath
Write-Host "✅ Done! Map saved to '$outputPath'" -ForegroundColor Green
```

### How to Use

1. Copy the code block above
2. Paste it into your PowerShell terminal (right-click to paste)
3. Press Enter
4. Open the newly created file: `C:\dm\docs\project_map.txt`

---

## 8. API Contracts & Endpoints

### Backend (API Gateway)

| Endpoint | Method | Purpose | Request Format | Response Format |
|----------|--------|---------|----------------|-----------------|
| `/upload` | POST | Upload video for analysis | Multipart form-data (video file) | JSON with pose landmarks |
| `/docs` | GET | FastAPI Swagger documentation | N/A | Interactive API docs |

### AI Service (Worker)

| Endpoint | Method | Purpose | Request Format | Response Format |
|----------|--------|---------|----------------|-----------------|
| `/process` | POST | Process video and extract pose data | Raw video stream | JSON pose landmarks |
| `/` | GET | Health check endpoint | N/A | 404 (standard "awake" signal) |

### Example Response

**Analysis Response:**
```json
{
  // JSON Skeleton Data with MediaPipe pose landmarks
}
```

---

## 9. Data Flow Architecture

### Complete Pipeline

```
[Mobile App] 
    ↓ (Multipart Upload via Legacy FileSystem)
[Backend - FastAPI]
    ↓ (Streaming chunks via httpx generator)
[AI Service - MediaPipe]
    ↓ (Frame-by-frame pose analysis)
[AI Service - Response]
    ↓ (JSON with pose landmarks)
[Backend - Relay]
    ↓ (Forward response)
[Mobile App - Render]
```

### Step-by-Step Process

1. **Mobile Upload:** User selects video → `UploadService.js` uploads via `FileSystem.uploadAsync` (legacy)
2. **Backend Receives:** Streams video chunks to AI service using httpx generator without loading to memory
3. **AI Processing:** MediaPipe extracts pose landmarks from each frame
4. **AI Response:** Returns JSON with landmark coordinates
5. **Backend Relay:** Forwards JSON response back to mobile app
6. **Mobile Rendering:** Overlays skeleton on video using pose data

### Data Formats

**Video Input:**
- **Tested Size:** Up to ~50MB
- **Larger files:** May hit timeout limits

**Pose Data:** JSON skeleton data flows back: AI → Backend → Mobile

---

## 10. Error Handling & Patterns

### Mobile App Error Patterns

| Error Type | Cause | User Message | Action |
|-----------|-------|--------------|--------|
| `AxiosError: Network Error` | Cannot reach backend | "Unable to connect to server" | Check `API_URL` in `UploadService.js` |
| `Error: timeout` | Service cold start (>60s) | "Server is waking up, please try again" | Visit `/docs` endpoint to wake services |
| `TypeError: undefined is not an object (evaluating 'FileSystem.UploadType')` | Using Enum instead of Integer | N/A | Must use `uploadType: 1` (integer) |

### Backend Error Patterns

| Error Type | Cause | Solution |
|-----------|-------|----------|
| `ModuleNotFoundError: cv2` | Missing OpenCV | Add `opencv-python-headless` to `backend/requirements.txt` |
| `Connection Refused` | Cannot reach AI service | Verify `AI_SERVICE_URL` in Render Backend settings |

### Retry Strategy

- **Mobile Client Timeout:** 60 seconds
- **Cold Start Protocol:** Manually visit `/docs` on Backend and `/` on AI Service before testing

---

## 11. Storage & Persistence

### Video Storage

- **Mobile:** Local temp files during upload
- **Backend:** Ephemeral - streams only, never saved to disk (memory constraints)
- **AI Service:** Ephemeral - processed in memory

### Analysis Results

- **Current:** Ephemeral (returned in JSON response only)
- **Future Plan:** Save JSON results to database (TBD)

### File Cleanup

All video data is ephemeral and not persisted on server infrastructure.

---

## 12. Authentication & Security

### Service-to-Service Communication

- **Backend → AI Service:** Open (Internal Render Network)
- **Mobile → Backend:** Currently Open (Dev Mode)
- **Future:** Plan to implement Auth0 or Firebase authentication

### CORS Configuration

Configured in `backend/app/main.py`

---

## 13. Performance & Constraints

### Processing Times

- **Cold Start Time:** ~60 seconds (Render Free Tier)
- **Client Timeout:** 60 seconds

### Resource Limits

| Service | RAM Limit | Notes |
|---------|-----------|-------|
| Backend | 512MB (Hard Limit) | Render Free Tier |
| AI Worker | [Render allocation] | Docker container |
| Mobile | Device-dependent | Local processing |

### Video Constraints

- **Tested Size:** Up to ~50MB
- **Larger Files:** May hit timeout limits
- **Supported Formats:** [To be documented - MP4, MOV, etc.]

---

## 14. Testing Strategy

### Service Health Checks

**Backend:**
```powershell
# Test backend is awake
curl https://diamondmind-backend-yalf.onrender.com/docs
# Expected: Swagger UI loads
```

**AI Service:**
```powershell
# Test AI service is awake
curl https://dm-ai-service.onrender.com/
# Expected: 404 (standard "awake" signal)
```

### End-to-End Testing

1. **Preparation:** Wake both services by visiting their health check endpoints
2. **Test:** Upload `test_video.mp4` via Mobile App
3. **Validation:** Verify "Skeleton" overlay appears on video

---

## 15. Dependency Versions (Locked)

### Mobile App (`diamondmind-mobile/package.json`)

```json
{
  "expo": "~52.0.0",
  "expo-file-system": "~18.0.0"  // Must support /legacy
}
```

### Backend (`backend/requirements.txt`)

```
httpx==0.27.0                    // Verified stable for streaming
opencv-python-headless==4.10.x   // Avoids libGL crash on native
fastapi
uvicorn
sqlalchemy
requests
```

### AI Service (`ai-service/requirements.txt`)

```
mediapipe
opencv-python
```

### System Dependencies

- **Python Version (Backend):** 3.11.0
- **Python Version (AI Service):** 3.12
- **Docker:** Required for local AI service development

---

## Important Notes

- Always deploy the AI Worker (Service 1) before the API Gateway (Service 2)
- Wake services by visiting their health check endpoints before testing
- Never refactor "tribal knowledge" fixes without consultation
- Keep configuration variables synchronized across all deployments
- Run the "Victory Lap" prompt at the end of each JIRA Story or major bug fix
- Physical devices must be on the same WiFi network as your PC for local development