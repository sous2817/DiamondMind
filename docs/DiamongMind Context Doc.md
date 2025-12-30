# DiamondMind Master Context
**Version 2.8** | AI-Driven Baseball Analytics Platform

---

## 📋 Table of Contents

1. [Engagement Protocol](#1-engagement-protocol)
2. [Project Identity & Stack](#2-project-identity--stack)
3. [Tribal Knowledge](#3-tribal-knowledge)
4. [Configuration & Wiring](#4-configuration--wiring)
5. [Deployment Manual](#5-deployment-manual)
6. [Local Development](#6-local-development)
7. [Project Structure Mapping](#7-project-structure-mapping)
8. [API Contracts](#8-api-contracts)
9. [Data Flow Architecture](#9-data-flow-architecture)
10. [Error Handling](#10-error-handling)
11. [Storage & Persistence](#11-storage--persistence)
12. [Authentication & Security](#12-authentication--security)
13. [Performance & Constraints](#13-performance--constraints)
14. [Testing Strategy](#14-testing-strategy)
15. [Dependency Versions](#15-dependency-versions)
16. [Additional Configuration Files](#16-additional-configuration-files)
17. [JIRA Automation](#17-jira-automation)

---

## 1. Engagement Protocol
### AI Instructions for Development Sessions

### 🔄 Code Sync Rule

> **I (The AI) start this session with zero knowledge of your local file contents.**

#### The "First Touch" Rule
Before modifying a file for the first time in this session, I **MUST** ask you to paste its current content.

#### State Retention
Once you provide the code, I will maintain its state in my context. I will only ask for it again if:
- We have drifted significantly
- You modified it externally

#### Core Principles
- ❌ **No Assumptions**: Never generate full file replacements without seeing the source code
- 📝 **Log Preservation**: Preserve existing logging statements unless they contradict new logic
- 🗺️ **Project Map Required**: If `project_map.txt` hasn't been provided, ask for it before making file-related changes

---

### 🏆 The "Victory Lap" Reminder

At the end of every JIRA Story or major bug fix, run this prompt:

> "Review the work we completed in this session. Compare it against the current Master Context Document. Update the document to include:
>
> - New Architectural Decisions (Section 2)
> - New Tribal Knowledge (Section 3)
> - Changes to Paths/URLs/Envs (Section 4)
> - Updates to API Contracts & Endpoints (Section 8)
> - Changes to Data Flow Architecture (Section 9)
> - Updates to Error Patterns (Section 10)
> - Changes to Storage & Persistence (Section 11)
> - Authentication & Security updates (Section 12)
> - Updates to Performance & Constraints (Section 13)
> - Changes to Testing Strategy (Section 14)
> - Dependency Version updates (Section 15)
> - Any new Important Notes
>
> Always generate the whole document, never include statements like 'refer to previous version'. Each time the file is generated it must be able to stand alone.
>
> Output the full, updated Markdown file."

---

## 2. Project Identity & Stack

**Name:** DiamondMind  
**Goal:** AI-driven Baseball Analytics (Mobile Video Analysis)  
**Repo Type:** Monorepo (Windows Environment)  
**Architecture:** Microservices

### 🏗️ System Architecture

We split the backend to prevent memory crashes on the Free Tier and to isolate heavy dependencies.

| Service | Role | Tech Stack | Location |
|---------|------|------------|----------|
| **Mobile App** | Client | React Native (Expo SDK 52) | `diamondmind-mobile/` |
| **API Gateway** | Orchestrator | Python FastAPI (Native) | `backend/` |
| **AI Worker** | Compute Engine | Python 3.12 + MediaPipe (Docker) | `ai-service/` |

### 📁 Directory Structure

**Required File:** `project_map.txt`

This context document references a separate file containing the complete project structure. If you don't have it:
1. Generate it using the script in [Section 7](#7-project-structure-mapping)
2. Provide it to the AI for proper file organization understanding
3. Keep it updated when major structural changes occur

---

## 3. Tribal Knowledge
### ⚠️ Critical Fixes (Do Not Refactor Without Understanding History)

These are non-standard implementations required to make the system work.

---

### A. Mobile Uploads (The "Legacy" Fix)

**Problem:** Expo SDK 52 broke the standard `FileSystem.uploadAsync` for binary multipart.

**The Fix:** Use the legacy sub-package and integer constants.

**✅ Required Code Pattern:**
```javascript
import * as FileSystem from 'expo-file-system/legacy'; // <--- MUST be legacy
// ...
uploadType: 1, // <--- MUST be Integer 1 (Multipart), NOT the Enum
```

---

### B. Backend Memory (The "Streaming" Fix)

**Problem:** Render Free Tier (512MB RAM) crashes if FastAPI reads a video into memory (`await file.read()`).

**The Fix:** Use a generator to stream the file chunk-by-chunk from Mobile → Backend → AI Service.

**Rule:** Never use `file.read()` for video files in `backend/main.py`.

---

### C. The "Cold Start" Timeout

**Problem:** Render services sleep after 15 minutes. The wake-up time (>60s) causes the Mobile App to throw `[Error: timeout]`.

**Protocol:** Before testing a new build, manually visit the Swagger docs of both services to wake them up.

---

### D. The "Response Format" Fix (CRITICAL) 🚨

**Problem:** The mobile app's `SkeletonOverlay` component accesses landmarks by numeric index (e.g., `landmarks[11]` for left shoulder). If the AI service returns landmarks as named objects (e.g., `{"LEFT_SHOULDER": {...}}`), the overlay will fail silently.

**The Fix:** The AI service **MUST** return landmarks as an array indexed 0-32, matching MediaPipe's landmark order.

**✅ CORRECT Pattern:**
```python
# Build landmarks as an array
landmarks_array = []
for landmark in results.pose_landmarks.landmark:
    landmarks_array.append({
        "x": landmark.x,
        "y": landmark.y,
        "z": landmark.z,
        "visibility": landmark.visibility
    })
```

**❌ WRONG Pattern:**
```python
# Do NOT use named keys
landmarks_dict = {
    "NOSE": {...},
    "LEFT_SHOULDER": {...}  # This breaks the mobile overlay!
}
```

---

### E. The "Single Source of Truth" Config (DM-41)

**Problem:** URLs were hardcoded in multiple files across the mobile app, making updates error-prone and causing silent failures.

**The Fix:** All URLs are centralized in `diamondmind-mobile/src/config.js`

**Rule:** Never hardcode `diamondmind-backend-yalf.onrender.com` or any URL directly in mobile app files. Always import from `config.js`.

---

### F. Expo Video Player "Race Condition"

**Problem:** Manually calling `player.replace()` or `player.play()` immediately after setting `videoUri` state causes a race condition crash.

**The Fix:** Rely entirely on the `useVideoPlayer` hook's internal logic.

**✅ Required Code Pattern:**
```javascript
// Let the hook handle it
const player = useVideoPlayer(videoUri, (p) => {
    if(videoUri) p.play();
});
// ...
setVideoUri(newUri); // The hook detects this change automatically
```

---

### G. AI Service Dependencies (Python 3.12 & OpenCV)

**Problems:**
- `mediapipe < 0.10.13` fails to install on Python 3.12
- Installing both `opencv-python` and `opencv-python-headless` causes namespace collisions
- `pip` running as root in Docker throws warnings

**The Fix:**
- **MediaPipe:** Must be `>=0.10.14`
- **OpenCV:** Must strictly be `opencv-python-headless` (remove the full version)
- **Docker:** Add `ENV PIP_ROOT_USER_ACTION=ignore` to suppress warnings

---

## 4. Configuration & Wiring

### 🔧 Configuration Hierarchy

URLs and environment variables follow a strict hierarchy to avoid mismatches:

| Level | Purpose | Location | Notes |
|-------|---------|----------|-------|
| **1. Mobile Config** | Single source for mobile app | `diamondmind-mobile/src/config.js` | ⚠️ **UPDATE THIS FIRST** |
| **2. AI Service Config** | Backend URL for progress reporting | `ai-service/pose_engine.py` | Has env var override via `BACKEND_URL` |
| **3. Render Dashboard** | Service-to-service URLs | Render.com Environment Variables | Set `AI_SERVICE_URL` here |
| **4. Local Scripts** | JIRA Automation | `backend/.env` | Used by `sync_jira.py` |

---

### 🌐 Current Live Values

| Variable | Current Value | Used By | Location(s) |
|----------|---------------|---------|-------------|
| `Config.API_BASE_URL` | `https://diamondmind-backend-yalf.onrender.com` | Mobile → Backend HTTP | `diamondmind-mobile/src/config.js` |
| `Config.WS_BASE_URL` | `wss://diamondmind-backend-yalf.onrender.com` | Mobile → Backend WebSocket | `diamondmind-mobile/src/config.js` |
| `BACKEND_URL` | `https://diamondmind-backend-yalf.onrender.com` | AI → Backend progress | `ai-service/pose_engine.py` (env var) |
| `AI_SERVICE_URL` | `https://dm-ai-service.onrender.com` | Backend → AI | Render Dashboard (Backend) |
| `PORT` | `8001` | AI Service | `ai-service/Dockerfile` |

---

### ✅ Configuration Update Checklist

When changing backend URLs, update in this order:

1. **Mobile Config:** Update `LIVE_BACKEND_URL` in `diamondmind-mobile/src/config.js`
2. **AI Service:** Set `BACKEND_URL` environment variable in Render Dashboard (AI Service)
3. **Backend:** Verify `AI_SERVICE_URL` is correct in Render Dashboard (Backend Service)
4. **Optional:** Update `backend/render.yaml` if using Blueprints

---

## 5. Deployment Manual

Follow these exact specifications if redeploying to Render.

### 🤖 Service 1: AI Worker (Deploy First)

**Type:** Web Service (Docker Runtime)  
**Root Directory:** `ai-service`

**Environment Variables:**
- `PORT=8001` (Required)
- `BACKEND_URL=https://diamondmind-backend-yalf.onrender.com`

**Build Context:** Must include `pose_landmarker_heavy.task` and `Dockerfile`

**System Dependencies:** Dockerfile installs `libgl1` and `libglib2.0-0`

**Dockerfile Note:** Includes `ENV PIP_ROOT_USER_ACTION=ignore` to silence pip root warnings

---

### 🌐 Service 2: API Gateway (Deploy Second)

**Type:** Web Service (Native Python 3 Runtime)  
**Root Directory:** `backend`

**Build Command:** `pip install -r requirements.txt`  
**Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

**Environment Variables:**
- `PYTHON_VERSION = 3.11.0` (or 3.12 if upgraded)
- `AI_SERVICE_URL = https://dm-ai-service.onrender.com`

**Dependencies:** `requirements.txt` MUST include:
- `opencv-python-headless` (to avoid libGL crashes)
- `httpx`

---

## 6. Local Development

### Option A: Hybrid (Recommended) 🌟

Run the Mobile App locally while pointing to cloud services.

1. **Mobile Config:** Verify `config.js` points to your cloud backend (default)
2. **Start the mobile app:**
   ```bash
   cd diamondmind-mobile
   npx expo start
   ```

**Important:** If using a physical device, your phone must be on the same WiFi network as your PC (if running backend locally), or use the Cloud URL.

**Pros:** No need to run heavy Docker containers locally. Best for UI work.

---

### Option B: Full Local (Debugging) 🔬

Run all services locally for complete debugging control.

#### AI Service (Docker Desktop)
```bash
cd ai-service
docker build -t dm-ai .
docker run -p 8001:8001 -e BACKEND_URL=http://host.docker.internal:8000 dm-ai
```

#### Backend (Uvicorn)
```bash
cd backend
$env:AI_SERVICE_URL="http://localhost:8000"
uvicorn app.main:app --reload --port 8000
```

#### Mobile App (Update config.js)
```javascript
// For local testing
const LOCAL_IP = "192.168.1.100"; // Your PC's LAN IP
const LIVE_BACKEND_URL = "localhost:8000"; // or LOCAL_IP + ":8000"
```

**Choose based on your environment:**
- **Android Emulator:** Use `10.0.2.2:8000`
- **Physical Device:** Use your PC's LAN IP (e.g., `192.168.1.100:8000`)
- **iOS Simulator:** Use `localhost:8000`

```bash
cd diamondmind-mobile
npx expo start
```

---

## 7. Project Structure Mapping

### 📊 PowerShell Script

Copy/paste this entire block directly into your PowerShell terminal:

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

## 8. API Contracts

### 🔌 Backend (API Gateway)

| Endpoint | Method | Purpose | Request Format | Response Format |
|----------|--------|---------|----------------|-----------------|
| `/api/videos/upload` | POST | Upload video for analysis | Multipart form-data (video file) + `job_id` query param | JSON with pose landmarks |
| `/ws/progress/{job_id}` | WebSocket | Real-time progress updates | WebSocket connection | JSON: `{"progress": 0-100}` |
| `/api/jobs/{job_id}/progress` | POST | Receive progress from AI service | JSON: `{"progress": int}` | JSON: `{"status": "ok"}` |
| `/docs` | GET | FastAPI Swagger documentation | N/A | Interactive API docs |

---

### 🤖 AI Service (Worker)

| Endpoint | Method | Purpose | Request Format | Response Format |
|----------|--------|---------|----------------|-----------------|
| `/analyze/pose` | POST | Process video and extract pose data | Multipart form-data (video file) + `job_id` query param | JSON pose landmarks |
| `/` | GET | Health check endpoint | N/A | JSON: `{"status": "healthy"}` |

---

### 📦 Example Response Structure

**Analysis Response (AI Service → Backend → Mobile):**

```json
{
  "frames": [
    {
      "timestamp": 0,
      "landmarks": [
        {"x": 0.5, "y": 0.5, "z": 0.0, "visibility": 0.95},
        {"x": 0.48, "y": 0.45, "z": -0.1, "visibility": 0.92},
        // ... 33 landmarks total (indices 0-32)
        // Index 0 = NOSE
        // Index 11 = LEFT_SHOULDER
        // Index 12 = RIGHT_SHOULDER
        // etc. (follows MediaPipe Pose landmark order)
      ]
    }
  ],
  "total_frames": 120,
  "frames_with_person": 115,
  "fps": 30.0
}
```

**Critical Notes:**
- ✅ `landmarks` MUST be an array, not an object with named keys
- ✅ Array indices 0-32 follow MediaPipe's landmark ordering
- ✅ `timestamp` is in milliseconds
- ✅ If no person detected in a frame, `landmarks` will be `null`
- ✅ Mobile app uses `frames_with_person` to warn users about detection issues

---

## 9. Data Flow Architecture

### 🔄 Complete Pipeline

```
[Mobile App]
    ↓ (Multipart Upload via Legacy FileSystem)
[Backend - FastAPI]
    ↓ (Streaming chunks via httpx generator)
[AI Service - MediaPipe]
    ↓ (Frame-by-frame pose analysis)
    ↓ (Progress updates every 10 frames via HTTP POST)
[Backend - WebSocket]
    ↓ (Real-time progress broadcast)
[Mobile App - Progress Bar]

[AI Service - Response]
    ↓ (JSON with pose landmarks array)
[Backend - Relay]
    ↓ (Forward response)
[Mobile App - Render Skeleton]
```

---

### 📝 Step-by-Step Process

1. **Mobile Upload:** User selects video → `UploadService.js` uploads via `FileSystem.uploadAsync` (legacy) with a unique `job_id`

2. **WebSocket Connection:** Mobile app opens WebSocket connection to `/ws/progress/{job_id}` using `Config.WS_BASE_URL`

3. **Backend Receives:** Streams video chunks to AI service using `httpx` generator without loading to memory

4. **AI Processing:** MediaPipe extracts pose landmarks from each frame

5. **Progress Updates:** AI service POSTs progress to backend every 10 frames using `BACKEND_URL`

6. **Progress Broadcast:** Backend broadcasts progress via WebSocket to mobile app

7. **AI Response:** Returns JSON with landmark coordinates as an array

8. **Backend Relay:** Forwards JSON response back to mobile app

9. **Mobile Rendering:** Overlays skeleton on video using pose data, syncing with video playback

---

### 📊 Data Formats

**Video Input:**
- **Tested Size:** Up to ~50MB
- **Larger files:** May hit timeout limits

**Pose Data:**
- **Format:** JSON skeleton data flows back: AI → Backend → Mobile
- **Structure:** Array of frames, each containing `timestamp` and `landmarks` array
- **Landmarks:** 33-element array (indices 0-32) with `x`, `y`, `z`, `visibility` per landmark

---

## 10. Error Handling

### 📱 Mobile App Error Patterns

| Error Type | Cause | User Message | Action |
|------------|-------|--------------|--------|
| `AxiosError: Network Error` | Cannot reach backend | "Unable to connect to server" | Check `Config.API_BASE_URL` in `config.js` |
| `Error: timeout` | Service cold start (>60s) | "Server is waking up, please try again" | Visit `/docs` endpoint to wake services |
| `Call to function 'VideoPlayer.play' rejected` | Race condition in Expo Video | N/A | Use `useVideoPlayer` hook, do not call `p.play()` manually |
| Black Bar at bottom (LogBox) | `console.error` usage in dev | N/A | Use `console.log` for handled errors |
| `TypeError: undefined is not an object` | Using Enum instead of Integer | N/A | Must use `uploadType: 1` (integer) |
| WebSocket connection failure | Wrong WebSocket URL | Progress bar stuck at 0% | Verify `Config.WS_BASE_URL` matches backend |

---

### 🖥️ Backend Error Patterns

| Error Type | Cause | Solution |
|------------|-------|----------|
| `ModuleNotFoundError: cv2` | Missing OpenCV | Add `opencv-python-headless` to `requirements.txt` |
| Connection Refused | Cannot reach AI service | Verify `AI_SERVICE_URL` in Render Backend settings |
| WebSocket disconnects | Long processing time | Normal - WebSocket closes after upload completes |

---

### 🤖 AI Service Error Patterns

| Error Type | Cause | Solution |
|------------|-------|----------|
| No person detected | Poor video quality, lighting issues | Log warning with detection stats, continue processing |
| Progress reporting fails | Backend unreachable or wrong URL | Silent failure - processing continues. Check `BACKEND_URL` env var |
| pip permission denied | Running as root in Docker | Add `ENV PIP_ROOT_USER_ACTION=ignore` to Dockerfile |

---

### 🔄 Retry Strategy

- **Mobile Client Timeout:** 60 seconds
- **Cold Start Protocol:** Manually visit `/docs` on Backend and `/` on AI Service before testing
- **Progress Updates:** Fire-and-forget (failures don't block processing)

---

## 11. Storage & Persistence

### 📹 Video Storage

- **Mobile:** Local temp files during upload
- **Backend:** Ephemeral - streams only, never saved to disk (memory constraints)
- **AI Service:** Ephemeral - saved to `/tmp/dm_uploads` during processing, deleted after completion

### 📊 Analysis Results

- **Current:** Ephemeral (returned in JSON response only)
- **Future Plan:** Save JSON results to database (TBD)

### 🗑️ File Cleanup

All video data is ephemeral. AI service deletes temp files after processing in `finally` block.

---

## 12. Authentication & Security

### 🔐 Service-to-Service Communication

- **Backend → AI Service:** Open (Internal Render Network)
- **AI Service → Backend:** Open for progress updates
- **Mobile → Backend:** Currently Open (Dev Mode)
- **Future:** Plan to implement Auth0 or Firebase authentication

### 🌐 CORS Configuration

Configured in both `backend/app/main.py` and `ai-service/main.py` with `allow_origins=["*"]` (dev mode)

---

## 13. Performance & Constraints

### ⏱️ Processing Times

- **Cold Start Time:** ~60 seconds (Render Free Tier)
- **Client Timeout:** 60 seconds
- **Progress Update Interval:** Every 10 frames

### 💾 Resource Limits

| Service | RAM Limit | Notes |
|---------|-----------|-------|
| Backend | 512MB (Hard Limit) | Render Free Tier |
| AI Worker | [Render allocation] | Docker container |
| Mobile | Device-dependent | Local processing |

### 🎥 Video Constraints

- **Tested Size:** Up to ~50MB
- **Larger Files:** May hit timeout limits
- **Supported Formats:** MP4, MOV, AVI (validated by backend)

### 🤖 AI Model Settings

- **Model Complexity:** 1 (Standard) - Balance between speed and accuracy
- **Detection Confidence:** 0.5 minimum
- **Frame Processing:** Sequential (not parallelized to avoid memory issues)

---

## 14. Testing Strategy

### 🏥 Service Health Checks

**Backend:**
```bash
# Test backend is awake
curl https://diamondmind-backend-yalf.onrender.com/docs
# Expected: Swagger UI loads
```

**AI Service:**
```bash
# Test AI service is awake
curl https://dm-ai-service.onrender.com/
# Expected: JSON response with status "healthy"
```

---

### 🧪 End-to-End Testing

1. **Preparation:** Wake both services by visiting their health check endpoints
2. **Test:** Upload `test_video.mp4` via Mobile App
3. **Monitor Console:** Watch for WebSocket connection, progress updates, and response structure
4. **Validation:** Verify "Skeleton" overlay appears on video with green lines and red dots

---

### 📋 Console Log Checkpoints

**Expected logs during successful upload:**
```
📤 Starting upload for Job ID: [id]
📡 WebSocket connecting to job: [id]
✅ WebSocket connected
📊 Progress update: 10%
📊 Progress update: 20%
...
📊 Progress update: 100%
✅ Analysis complete: { totalFrames: X, framesWithPerson: Y }
```

---

## 15. Dependency Versions

### 📱 Mobile App (`diamondmind-mobile/package.json`)

```json
{
  "expo": "~52.0.0",
  "expo-file-system": "~18.0.0",  // Must support /legacy
  "expo-video": "latest",
  "react-native-svg": "latest",
  "expo-sharing": "latest",
  "react-native-view-shot": "latest"
}
```

---

### 🖥️ Backend (`backend/requirements.txt`)

```
httpx==0.27.0                    # Verified stable for streaming
opencv-python-headless==4.10.x   # Avoids libGL crash on native
fastapi
uvicorn
sqlalchemy
requests
websockets                       # For WebSocket support
jira                             # For Automation scripts
python-dotenv                    # For Automation scripts
```

---

### 🤖 AI Service (`ai-service/requirements.txt`)

```
mediapipe==0.10.14               # Required for Python 3.12 compatibility
opencv-python-headless           # REQUIRED: Use headless to avoid conflict
requests                         # For progress reporting
numpy
matplotlib
```

---

### 🐍 System Dependencies

- **Python Version (Backend):** 3.11.0
- **Python Version (AI Service):** 3.12 (Requires `mediapipe >= 0.10.14`)
- **Docker:** Required for local AI service development

---

## 16. Additional Configuration Files

### 📂 Potentially Affected Files

When updating URLs or deploying to new environments, check these locations:

| File/Location | What to Check | Notes |
|---------------|---------------|-------|
| `backend/render.yaml` | Environment variable definitions | If using Blueprints for IaC |
| `backend/.env` | Local development URLs | Not committed to git |
| `ai-service/.env` | Local `BACKEND_URL` override | Not committed to git |
| `docker-compose.yml` | Service URLs for local testing | If you create one |
| Integration test files | Any test scripts with URLs | Check `/backend/tests/` if exists |
| GitHub Actions / CI | Workflow files may have URLs | Check `.github/workflows/` if exists |

---

### ✅ Environment Variables Checklist

**Mobile App:**
- ✅ `diamondmind-mobile/src/config.js` - Update `LIVE_BACKEND_URL`

**AI Service (Render Dashboard):**
- ✅ `PORT = 8001`
- ✅ `BACKEND_URL = https://diamondmind-backend-yalf.onrender.com` (optional override)

**Backend (Render Dashboard):**
- ✅ `PYTHON_VERSION = 3.11.0`
- ✅ `AI_SERVICE_URL = https://dm-ai-service.onrender.com`

**JIRA Automation (Local .env):**
- ✅ `JIRA_URL = https://[your-domain].atlassian.net`
- ✅ `JIRA_EMAIL = [email]`
- ✅ `JIRA_API_TOKEN = [token]`
- ✅ `PROJECT_KEY = [key]`

---

## 17. JIRA Automation

### 📝 Scripts

**Location:** `backend/scripts/`  
**Files:** `sync_jira.py`, `stories.json`

---

### 🔄 Workflow

**1. Define Stories:** Edit `stories.json` with the JSON format

**2. Create/Update:** Run the script to push changes to JIRA
```bash
python backend/scripts/sync_jira.py create
```

**3. Transition:** Move tickets (optional)
```bash
python backend/scripts/sync_jira.py [TICKET-ID] Done
```

---

### 📦 Dependencies

Requires `jira` and `python-dotenv` packages.

---

## 🎯 Important Reminders

- ✅ Always deploy the **AI Worker** (Service 1) **before** the API Gateway (Service 2)
- ✅ Wake services by visiting their health check endpoints before testing
- ✅ Never refactor "tribal knowledge" fixes without consultation
- ✅ Keep configuration variables synchronized across all deployments
- ✅ Run the "Victory Lap" prompt at the end of each JIRA Story or major bug fix
- ✅ Physical devices must be on the same WiFi network as your PC for local development
- 🚨 **CRITICAL:** AI service must return landmarks as an **array** (indices 0-32), not as named objects
- 🚨 **CRITICAL:** All mobile app URLs must be managed through `config.js` - never hardcode URLs directly
- 🚨 **CRITICAL:** Use `useVideoPlayer` hook correctly; avoid manual play calls that race with state updates
- 🚨 **CRITICAL:** AI Service requires `opencv-python-headless` and `mediapipe>=0.10.14` for Python 3.12 compatibility
- ⚠️ WebSocket URL must exactly match the backend URL (common source of progress bar issues)
- 📊 Monitor console logs during development to verify data flow and catch issues early
- 🔄 When updating URLs, always update `config.js` **FIRST**, then verify backend environment variables match

---

**End of Document** | Last Updated: v2.8