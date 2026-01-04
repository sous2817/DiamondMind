# DiamondMind Master Context

**Version 2.11** | AI-Driven Baseball Analytics Platform

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

| Service               | Role           | Tech Stack                       | Location                |
| --------------------- | -------------- | -------------------------------- | ----------------------- |
| **Mobile App**  | Client         | React Native (Expo SDK 52)       | `diamondmind-mobile/` |
| **API Gateway** | Orchestrator   | Python FastAPI (Native)          | `backend/`            |
| **AI Worker**   | Compute Engine | Python 3.12 + MediaPipe (Docker) | `ai-service/`         |

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

### E. The "Single Source of Truth" Config

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

### H. Overlay Synchronization (The "O(1)" Fix)

**Problem:** "Jittery" overlay animations caused by using `Array.find()` (O(N)) inside the high-frequency synchronize loop.

**The Fix:** Use `Math.floor(currentTime * fps)` (O(1)) for instant index calculation.

**✅ Required Code Pattern:**
```javascript
// App.js
const frameIndex = Math.floor(payload.currentTime * result.fps);
const frame = result.frames[frameIndex];
```

---

### I. Async Upload & Processing (The "Idle Timeout" Fix)

**Problem:** Load balancers (Render/AWS) kill idle connections after ~100s. Our AI analysis takes ~105s, dealing a "Timeout Error" to the mobile app even if the backend succeeds.

**The Fix:** Decouple the HTTP response from the AI processing.
1. Mobile Uploads video.
2. Backend responds **202 Accepted** immediately.
3. Backend processes video in a **BackgroundTask**.
4. Backend pushes the final result to Mobile via **WebSocket**.

**✅ Required Code Pattern:**
```javascript
// App.js
ws.onmessage = (e) => {
    if (data.result) { setResult(data.result); } // Success via WS
}
// Do not trust the HTTP response to have the result.
```

---

### J. Response Size Optimization (The "OOM" Fix)

**Problem:** The AI Service returned full-precision floats (16+ digits) for every landmark. This created a massive JSON payload (10MB+) that caused `OutOfMemoryError` on Android during parsing.

**The Fix:** Round all coordinates to **4 decimal places** in the AI Service.

**✅ Required Code Pattern:**
```python
# ai-service/pose_engine.py
"x": round(landmark.x, 4),
"y": round(landmark.y, 4),
# ...
```

---

## 4. Configuration & Wiring

### 🔧 Configuration Hierarchy

URLs and environment variables follow a strict hierarchy to avoid mismatches:

| Level                          | Purpose                            | Location                             | Notes                                    |
| ------------------------------ | ---------------------------------- | ------------------------------------ | ---------------------------------------- |
| **1. Mobile Config**     | Single source for mobile app       | `diamondmind-mobile/src/config.js` | ⚠️**UPDATE THIS FIRST**          |
| **2. AI Service Config** | Backend URL for progress reporting | `ai-service/pose_engine.py`        | Has env var override via `BACKEND_URL` |
| **3. Render Dashboard**  | Service-to-service URLs            | Render.com Environment Variables     | Set `AI_SERVICE_URL` here              |
| **4. Local Scripts**     | JIRA Automation                    | `backend/.env`                     | Used by `sync_jira.py`                 |

---

### 🌐 Current Live Values

| Variable                | Current Value                                     | Used By                     | Location(s)                             |
| ----------------------- | ------------------------------------------------- | --------------------------- | --------------------------------------- |
| `Config.API_BASE_URL` | `https://diamondmind-backend-yalf.onrender.com` | Mobile → Backend HTTP      | `diamondmind-mobile/src/config.js`    |
| `Config.WS_BASE_URL`  | `wss://diamondmind-backend-yalf.onrender.com`   | Mobile → Backend WebSocket | `diamondmind-mobile/src/config.js`    |
| `BACKEND_URL`         | `https://diamondmind-backend-yalf.onrender.com` | AI → Backend progress      | `ai-service/pose_engine.py` (env var) |
| `AI_SERVICE_URL`      | `https://dm-ai-service.onrender.com`            | Backend → AI               | Render Dashboard (Backend)              |
| `PORT`                | `8001`                                          | AI Service                  | `ai-service/Dockerfile`               |

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

| Endpoint                        | Method    | Purpose                          | Request Format                                           | Response Format              |
| ------------------------------- | --------- | -------------------------------- | -------------------------------------------------------- | ---------------------------- |
| `/api/videos/upload`          | POST      | Upload video for analysis        | Multipart form-data (video file) +`job_id` query param | JSON `{"status": "processing"}` |
| `/ws/progress/{job_id}`       | WebSocket | Real-time progress & results     | WebSocket connection                                     | JSON events                  |
| `/api/jobs/{job_id}/progress` | POST      | Receive progress from AI service | JSON:`{"progress": int}`                               | JSON:`{"status": "ok"}`    |
| `/docs`                       | GET       | FastAPI Swagger documentation    | N/A                                                      | Interactive API docs         |

---

### 🤖 AI Service (Worker)

| Endpoint          | Method | Purpose                             | Request Format                                           | Response Format                |
| ----------------- | ------ | ----------------------------------- | -------------------------------------------------------- | ------------------------------ |
| `/analyze/pose` | POST   | Process video and extract pose data | Multipart form-data (video file) +`job_id` query param | JSON pose landmarks            |
| `/`             | GET    | Health check endpoint               | N/A                                                      | JSON:`{"status": "healthy"}` |

---

### 📦 Example Response Structure

**Analysis Response (AI Service → Backend → WS → Mobile):**

```json
{
  "frames": [
    {
      "timestamp": 0,
      "landmarks": [
        {"x": 0.5, "y": 0.5, "z": 0.0, "visibility": 0.95},
        // ... 33 landmarks total (indices 0-32)
      ]
    }
  ],
  "total_frames": 120,
  "frames_with_person": 115,
  "fps": 30.0,
  "download_url": "/api/videos/download/analyzed_job123.mp4"
}
```

---

## 9. Data Flow Architecture

### 🔄 Async Pipeline (Updated for v2.11)

```
[Mobile App]
    ↓ (Multipart Upload)
[Backend - FastAPI]
    → (202 Accepted - Immediate Response)
    ↓ (Spawns Background Task)
[AI Service - MediaPipe]
    ↓ (Frame-by-frame pose analysis)
    ↓ (Progress updates every 10 frames via HTTP POST)
[Backend - WebSocket]
    ↓ (Real-time progress broadcast)
    ↓ (Final Result JSON Push)
[Mobile App]
    ↓ (Receives `data.result` event)
    ↓ (Renders Overlay)
```

---

### 📝 Step-by-Step Process

1. **Mobile Upload:** User selects video → `UploadService.js` uploads via `FileSystem.uploadAsync` with `job_id`.
2. **Immediate Ack:** Backend saves file to temp, spawns background task, and returns `{"status": "processing"}`.
3. **Wait State:** Mobile app sees "processing" and keeps the WebSocket open (spinner active).
4. **AI Processing:** Background task sends video to AI. AI processes it.
5. **Completion:** AI returns JSON to Backend.
6. **Result Push:** Backend pushes `{"result": {...}}` to Mobile via WebSocket.
7. **Mobile Rendering:** App receives result, closes socket, and displays analysis.

---

## 10. Error Handling

### 📱 Mobile App Error Patterns

| Error Type                                       | Cause                             | User Message                         | Action                                                         |
| ------------------------------------------------ | --------------------------------- | ------------------------------------ | -------------------------------------------------------------- |
| `AxiosError: Network Error`                    | Cannot reach backend              | "Unable to connect to server"        | Check `Config.API_BASE_URL` in `config.js`                 |
| `Error: timeout`                               | Processing > 10m or Service sleep | "Server is waking up..." or "Timout" | Visit `/docs` endpoint to wake services. Retry.              |
| `Call to function 'VideoPlayer.play' rejected` | Race condition in Expo Video      | N/A                                  | Use `useVideoPlayer` hook, do not call `p.play()` manually |
| `OutOfMemoryError`                             | JSON response too large           | App Crash                            | AI Service must round floats to 4 decimals.                    |

---

## 11. Storage & Persistence

### 📹 Video Storage

- **Mobile:** Local temp files during upload
- **Backend:** Ephemeral temp files (`/tmp`) during upload/relay
- **AI Service:** Ephemeral - saved to `/tmp/dm_uploads` during processing
- **Cleanup:** Backend automatically deletes temp files in `finally` block of background task.

---

## 12. Authentication & Security

### 🔐 Service-to-Service Communication

- **Backend → AI Service:** Open (Internal Render Network)
- **AI Service → Backend:** Open for progress updates
- **Mobile → Backend:** Currently Open (Dev Mode)
- **Future:** Plan to implement Auth0 or Firebase authentication

---

## 13. Performance & Constraints

### ⏱️ Processing Times

- **Cold Start Time:** ~60 seconds (Render Free Tier)
- **Client Timeout:** 600 seconds (10 minutes)
- **Idle Timeout:** ~100 seconds (Solved via Async/WebSocket architecture)

---

## 17. JIRA Automation

**Script:** `backend/scripts/sync_jira.py`
**Config:** `backend/scripts/stories.json`

### Supported Commands:

- `sync_jira.py create` - Creates new tickets from JSON
- `sync_jira.py update` - Updates existing tickets

### Recent Tickets:
- **DM-49:** Optimize Skeleton Overlay Synchronization (Closed)
- **DM-50:** Async Backend Refactor (In Progress)
