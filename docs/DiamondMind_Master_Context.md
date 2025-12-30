# **DiamondMind Master Context (v2.7)**

## **1. Engagement Protocol (AI Instructions)**

### **Code Sync Rule**

I (The AI) start this session with zero knowledge of your local file contents.

* **The "First Touch" Rule:** Before modifying a file for the first time in this session, I MUST ask you to paste its current content.
* **State Retention:** Once you provide the code, I will maintain its state in my context. I will only ask for it again if we have drifted significantly or you modified it externally.
* **No Assumptions:** I will never generate full file replacements without having seen the source code at least once in the current session.

### **The "Victory Lap" Reminder**

At the end of every JIRA Story or major bug fix, I must run the following prompt:

"Review the work we completed in this session. Compare it against the current Master Context Document. Update the document to include:

* New Architectural Decisions (Section 2)
* New Tribal Knowledge (Section 3)
* Changes to Paths/URLs/Envs (Section 4)
* Updates to API Contracts & Endpoints (Section 8)
* Changes to Data Flow Architecture (Section 9)
* Updates to Error Patterns - Mobile App & Backend (Section 10)
* Changes to Storage & Persistence (Section 11)
* Authentication & Security updates (Section 12)
* Updates to Performance & Constraints (Section 13)
* Changes to Testing Strategy (Section 14)
* Dependency Version updates (Section 15)
* Any new Important Notes

Always generate the whole document, never include statements like 'refer to previous version'.  Each time the file is generated it must be able to stand alone. 

Output the full, updated Markdown file."

## **2. Project Identity & Stack**

* **Name:** DiamondMind
* **Goal:** AI-driven Baseball Analytics (Mobile Video Analysis)
* **Repo Type:** Monorepo (Windows Environment)

### **Microservices Architecture**

We split the backend to prevent memory crashes on the Free Tier and to isolate heavy dependencies.

| Service     | Role           | Tech Stack                       | Location            |
| :---------- | :------------- | :------------------------------- | :------------------ |
| Mobile App  | Client         | React Native (Expo SDK 52)       | diamondmind-mobile/ |
| API Gateway | Orchestrator   | Python FastAPI (Native)          | backend/            |
| AI Worker   | Compute Engine | Python 3.12 + MediaPipe (Docker) | ai-service/         |

### **Directory Structure (Map)**

**📁 Required File:** project_map.txt

This context document references a separate file containing the complete project structure. If you don't have project_map.txt, please:

1. Generate it using the script in Section 7
2. Provide it to me so I can understand the current file organization
3. Keep it updated when major structural changes occur

**AI Agent Note:** If project_map.txt has not been provided in this session, ask the user to share it before making any file-related recommendations or modifications.

## **3. "Tribal Knowledge" (Critical Fixes)**

These are non-standard implementations required to make the system work. Do not refactor these without understanding the history.

### **A. Mobile Uploads (The "Legacy" Fix)**

**Problem:** Expo SDK 52 broke the standard FileSystem.uploadAsync for binary multipart.

**The Fix:** We use the legacy sub-package and integer constants.

**Code Pattern (Required):**

import * as FileSystem from 'expo-file-system/legacy'; // <--- MUST be legacy
// ...
uploadType: 1, // <--- MUST be Integer 1 (Multipart), NOT the Enum

### **B. Backend Memory (The "Streaming" Fix)**

**Problem:** Render Free Tier (512MB RAM) crashes if FastAPI reads a video into memory (await file.read()).

**The Fix:** We use a generator to stream the file chunk-by-chunk from Mobile → Backend → AI Service.

**Rule:** Never use file.read() for video files in backend/main.py.

### **C. The "Cold Start" Timeout**

**Problem:** Render services sleep after 15 minutes. The wake-up time (>60s) causes the Mobile App to throw `[Error: timeout]`.

**Protocol:** Before testing a new build, manually visit the Swagger docs of both services to wake them up.

### **D. The "Response Format" Fix (CRITICAL)**

**Problem:** The mobile app's SkeletonOverlay component accesses landmarks by numeric index (e.g., `landmarks[11]` for left shoulder, `landmarks[12]` for right shoulder). If the AI service returns landmarks as named objects (e.g., `{"LEFT_SHOULDER": {...}}`), the overlay will fail silently.

**The Fix:** The AI service MUST return landmarks as an **array** indexed 0-32, matching MediaPipe's landmark order.

**Code Pattern (Required in pose_engine.py):**

# ✅ CORRECT: Build landmarks as an array

landmarks_array = []
for landmark in results.pose_landmarks.landmark:
    landmarks_array.append({
        "x": landmark.x,
        "y": landmark.y,
        "z": landmark.z,
        "visibility": landmark.visibility
    })

# ❌ WRONG: Do NOT use named keys

landmarks_dict = {
    "NOSE": {...},
    "LEFT_SHOULDER": {...}  # This breaks the mobile overlay!
}

### **E. The "Single Source of Truth" Config (DM-41)**

**Problem:** URLs were hardcoded in multiple files across the mobile app, making updates error-prone and causing silent failures when URLs didn't match.

**The Fix:** All URLs are now centralized in a single configuration file: `diamondmind-mobile/src/config.js`

**Rule:** Never hardcode `diamondmind-backend-yalf.onrender.com` or any URL directly in mobile app files. Always import from `config.js`.

### **F. Expo Video Player "Race Condition" (New)**

**Problem:** Manually calling `player.replace()` or `player.play()` immediately after setting `videoUri` state causes a race condition crash: `[Error: Call to function 'VideoPlayer.play' has been rejected... (received class java.lang.Integer)]`.

**The Fix:** Rely entirely on the useVideoPlayer hook's internal logic.

**Code Pattern (Required):**

// ✅ CORRECT: Let the hook handle it
const player = useVideoPlayer(videoUri, (p) => {
    if(videoUri) p.play();
});
// ...
setVideoUri(newUri); // The hook detects this change automatically.

## **4. "Hardcoded" Wiring & Configuration**

### **Configuration Hierarchy**

URLs and environment variables follow a strict hierarchy to avoid mismatches:

| Level                          | Purpose                            | Location                         | Notes                                |
| :----------------------------- | :--------------------------------- | :------------------------------- | :----------------------------------- |
| **1. Mobile Config**     | Single source for mobile app       | diamondmind-mobile/src/config.js | ⚠️ UPDATE THIS FIRST               |
| **2. AI Service Config** | Backend URL for progress reporting | ai-service/pose_engine.py        | Has env var override via BACKEND_URL |
| **3. Render Dashboard**  | Service-to-service URLs            | Render.com Environment Variables | Set AI_SERVICE_URL here              |
| **4. Local Scripts**     | JIRA Automation                    | backend/.env                     | Used by sync_jira.py                 |

### **Current Live Values**

| Variable            | Current Value                                 | Used By                     | Location(s)                                  |
| :------------------ | :-------------------------------------------- | :-------------------------- | :------------------------------------------- |
| Config.API_BASE_URL | https://diamondmind-backend-yalf.onrender.com | Mobile → Backend HTTP      | diamondmind-mobile/src/config.js             |
| Config.WS_BASE_URL  | wss://diamondmind-backend-yalf.onrender.com   | Mobile → Backend WebSocket | diamondmind-mobile/src/config.js             |
| BACKEND_URL         | https://diamondmind-backend-yalf.onrender.com | AI → Backend progress      | ai-service/pose_engine.py (env var override) |
| AI_SERVICE_URL      | https://dm-ai-service.onrender.com            | Backend → AI               | Render Dashboard (Backend Environment)       |
| PORT                | 8001                                          | AI Service                  | ai-service/Dockerfile                        |

### **Configuration Update Checklist**

When changing backend URLs, update in this order:

1. **Mobile Config:** Update `LIVE_BACKEND_URL` in `diamondmind-mobile/src/config.js`
2. **AI Service:** Set `BACKEND_URL` environment variable in Render Dashboard (AI Service)
3. **Backend:** Verify `AI_SERVICE_URL` is correct in Render Dashboard (Backend Service)
4. **Optional:** Update `backend/render.yaml` if using Blueprints

## **5. Deployment / Rebuild Manual**

Follow these exact specifications if redeploying to Render.

### **Service 1: AI Worker (Deploy First)**

* **Type:** Web Service (Docker Runtime)
* **Root Directory:** ai-service
* **Environment Variables:** - PORT=8001 (Required)
  * BACKEND_URL=https://diamondmind-backend-yalf.onrender.com (Optional, falls back to hardcoded default)
* **Build Context:** Must include pose_landmarker_heavy.task and Dockerfile
* **System Dependencies:** Dockerfile installs libgl1 and libglib2.0-0 (Required for OpenCV/MediaPipe)

### **Service 2: API Gateway (Deploy Second)**

* **Type:** Web Service (Native Python 3 Runtime)
* **Root Directory:** backend
* **Build Command:** `pip install -r requirements.txt`
* **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
* **Environment Variables:** * PYTHON_VERSION = 3.11.0
  * AI_SERVICE_URL = https://dm-ai-service.onrender.com (Must match AI Worker URL)
* **Dependencies:** requirements.txt MUST include opencv-python-headless (to avoid libGL crashes) and httpx

## **6. Local Development Workflow (Onboarding)**

How to run the stack on your local Windows machine.

### **Option A: Hybrid (Recommended)**

Run the Mobile App locally while pointing to cloud services.

1. **Mobile Config:** Verify config.js points to your cloud backend (default)
2. Start the mobile app:
   `cd diamondmind-mobile`
   `npx expo start`

**Important:** If using a physical device, your phone must be on the same WiFi network as your PC (if running backend locally), or use the Cloud URL.

**Pros:** No need to run heavy Docker containers locally. Best for UI work.

### **Option B: Full Local (Debugging)**

Run all services locally for complete debugging control.

1. **AI Service:** Run via Docker Desktop
   `cd ai-service`
   `docker build -t dm-ai .`
   `docker run -p 8001:8001 -e BACKEND_URL=http://host.docker.internal:8000 dm-ai`
2. **Backend:** Run via Uvicorn
   `cd backend`
   `$env:AI_SERVICE_URL="http://localhost:8001"`
   `uvicorn app.main:app --reload --port 8000`
3. **Mobile App:** Update config.js for local development:
   `// For local testing`
   `const LOCAL_IP = "192.168.1.100"; // Your PC's LAN IP`
   `const LIVE_BACKEND_URL = "localhost:8000"; // or LOCAL_IP + ":8000"`

   Choose based on your environment:

   * **Android Emulator:** Use 10.0.2.2:8000
   * **Physical Device:** Use your PC's LAN IP (e.g., 192.168.1.100:8000)
   * **iOS Simulator:** Use localhost:8000

`cd diamondmind-mobile`
`npx expo start`

## **7. Project Structure Mapping**

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

### **How to Use**

1. Copy the code block above
2. Paste it into your PowerShell terminal (right-click to paste)
3. Press Enter
4. Open the newly created file: C:\dm\docs\project_map.txt

## **8. API Contracts & Endpoints**

### **Backend (API Gateway)**

| Endpoint                    | Method    | Purpose                          | Request Format                                        | Response Format           |
| :-------------------------- | :-------- | :------------------------------- | :---------------------------------------------------- | :------------------------ |
| /api/videos/upload          | POST      | Upload video for analysis        | Multipart form-data (video file) + job_id query param | JSON with pose landmarks  |
| /ws/progress/{job_id}       | WebSocket | Real-time progress updates       | WebSocket connection                                  | JSON: {"progress": 0-100} |
| /api/jobs/{job_id}/progress | POST      | Receive progress from AI service | JSON: {"progress": int}                               | JSON: {"status": "ok"}    |
| /docs                       | GET       | FastAPI Swagger documentation    | N/A                                                   | Interactive API docs      |

### **AI Service (Worker)**

| Endpoint      | Method | Purpose                             | Request Format                                        | Response Format                 |
| :------------ | :----- | :---------------------------------- | :---------------------------------------------------- | :------------------------------ |
| /analyze/pose | POST   | Process video and extract pose data | Multipart form-data (video file) + job_id query param | JSON pose landmarks (see below) |
| /             | GET    | Health check endpoint               | N/A                                                   | JSON: {"status": "healthy"}     |

### **Example Response (AI Service → Backend → Mobile)**

**Analysis Response Structure:**

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

**Critical Notes:**

* landmarks MUST be an array, not an object with named keys
* Array indices 0-32 follow MediaPipe's landmark ordering
* timestamp is in milliseconds
* If no person detected in a frame, landmarks will be null
* Mobile app uses `frames_with_person` to warn users about detection issues

## **9. Data Flow Architecture**

### **Complete Pipeline**

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

### **Step-by-Step Process**

1. **Mobile Upload:** User selects video → UploadService.js uploads via FileSystem.uploadAsync (legacy) with a unique job_id
2. **WebSocket Connection:** Mobile app opens WebSocket connection to /ws/progress/{job_id} using Config.WS_BASE_URL
3. **Backend Receives:** Streams video chunks to AI service using httpx generator without loading to memory
4. **AI Processing:** MediaPipe extracts pose landmarks from each frame
5. **Progress Updates:** AI service POSTs progress to backend every 10 frames using BACKEND_URL
6. **Progress Broadcast:** Backend broadcasts progress via WebSocket to mobile app
7. **AI Response:** Returns JSON with landmark coordinates as an array
8. **Backend Relay:** Forwards JSON response back to mobile app
9. **Mobile Rendering:** Overlays skeleton on video using pose data, syncing with video playback

### **Data Formats**

**Video Input:**

* **Tested Size:** Up to ~50MB
* **Larger files:** May hit timeout limits

**Pose Data:** JSON skeleton data flows back: AI → Backend → Mobile

* **Structure:** Array of frames, each containing timestamp and landmarks array
* **Landmarks:** 33-element array (indices 0-32) with x, y, z, visibility per landmark

## **10. Error Handling & Patterns**

### **Mobile App Error Patterns**

| Error Type                                   | Cause                         | User Message                            | Action                                                                    |
| :------------------------------------------- | :---------------------------- | :-------------------------------------- | :------------------------------------------------------------------------ |
| AxiosError: Network Error                    | Cannot reach backend          | "Unable to connect to server"           | Check Config.API_BASE_URL in config.js                                    |
| Error: timeout                               | Service cold start (>60s)     | "Server is waking up, please try again" | Visit /docs endpoint to wake services                                     |
| Call to function 'VideoPlayer.play' rejected | Race condition in Expo Video  | N/A                                     | Use useVideoPlayer hook, do not call p.play() manually after setVideoUri. |
| Black Bar at bottom (LogBox)                 | console.error usage in dev    | N/A                                     | Use console.log for handled errors to avoid blocking UI.                  |
| TypeError: undefined is not an object        | Using Enum instead of Integer | N/A                                     | Must use uploadType: 1 (integer)                                          |
| WebSocket connection failure                 | Wrong WebSocket URL           | Progress bar stuck at 0%                | Verify Config.WS_BASE_URL matches backend URL                             |

### **Backend Error Patterns**

| Error Type               | Cause                   | Solution                                               |
| :----------------------- | :---------------------- | :----------------------------------------------------- |
| ModuleNotFoundError: cv2 | Missing OpenCV          | Add opencv-python-headless to backend/requirements.txt |
| Connection Refused       | Cannot reach AI service | Verify AI_SERVICE_URL in Render Backend settings       |
| WebSocket disconnects    | Long processing time    | Normal - WebSocket closes after upload completes       |

### **AI Service Error Patterns**

| Error Type               | Cause                               | Solution                                                         |
| :----------------------- | :---------------------------------- | :--------------------------------------------------------------- |
| No person detected       | Poor video quality, lighting issues | Log warning with detection stats, continue processing            |
| Progress reporting fails | Backend unreachable or wrong URL    | Silent failure - processing continues. Check BACKEND_URL env var |

### **Retry Strategy**

* **Mobile Client Timeout:** 60 seconds
* **Cold Start Protocol:** Manually visit /docs on Backend and / on AI Service before testing
* **Progress Updates:** Fire-and-forget (failures don't block processing)

## **11. Storage & Persistence**

### **Video Storage**

* **Mobile:** Local temp files during upload
* **Backend:** Ephemeral - streams only, never saved to disk (memory constraints)
* **AI Service:** Ephemeral - saved to /tmp/dm_uploads during processing, deleted after completion

### **Analysis Results**

* **Current:** Ephemeral (returned in JSON response only)
* **Future Plan:** Save JSON results to database (TBD)

### **File Cleanup**

All video data is ephemeral. AI service deletes temp files after processing in finally block.

## **12. Authentication & Security**

### **Service-to-Service Communication**

* **Backend → AI Service:** Open (Internal Render Network)
* **AI Service → Backend:** Open for progress updates
* **Mobile → Backend:** Currently Open (Dev Mode)
* **Future:** Plan to implement Auth0 or Firebase authentication

### **CORS Configuration**

Configured in both backend/app/main.py and ai-service/main.py with allow_origins=["*"] (dev mode)

## **13. Performance & Constraints**

### **Processing Times**

* **Cold Start Time:** ~60 seconds (Render Free Tier)
* **Client Timeout:** 60 seconds
* **Progress Update Interval:** Every 10 frames

### **Resource Limits**

| Service   | RAM Limit           | Notes            |
| :-------- | :------------------ | :--------------- |
| Backend   | 512MB (Hard Limit)  | Render Free Tier |
| AI Worker | [Render allocation] | Docker container |
| Mobile    | Device-dependent    | Local processing |

### **Video Constraints**

* **Tested Size:** Up to ~50MB
* **Larger Files:** May hit timeout limits
* **Supported Formats:** MP4, MOV, AVI (validated by backend)

### **AI Model Settings**

* **Model Complexity:** 1 (Standard) - Balance between speed and accuracy
* **Detection Confidence:** 0.5 minimum
* **Frame Processing:** Sequential (not parallelized to avoid memory issues)

## **14. Testing Strategy**

### **Service Health Checks**

**Backend:**

# Test backend is awake

curl https://diamondmind-backend-yalf.onrender.com/docs

# Expected: Swagger UI loads

**AI Service:**

# Test AI service is awake

curl https://dm-ai-service.onrender.com/

# Expected: JSON response with status "healthy"

### **End-to-End Testing**

1. **Preparation:** Wake both services by visiting their health check endpoints
2. **Test:** Upload test_video.mp4 via Mobile App
3. **Monitor Console:** Watch for WebSocket connection, progress updates, and response structure
4. **Validation:** Verify "Skeleton" overlay appears on video with green lines and red dots

## **15. Dependency Versions (Locked)**

### **Mobile App (diamondmind-mobile/package.json)**

{
  "expo": "~52.0.0",
  "expo-file-system": "~18.0.0",  // Must support /legacy
  "expo-video": "latest",
  "react-native-svg": "latest",
  "expo-sharing": "latest",
  "react-native-view-shot": "latest"
}

### **Backend (backend/requirements.txt)**

httpx==0.27.0                    // Verified stable for streaming
opencv-python-headless==4.10.x   // Avoids libGL crash on native
fastapi
uvicorn
sqlalchemy
requests
websockets                       // For WebSocket support
jira                             // For Automation scripts
python-dotenv                    // For Automation scripts

### **AI Service (ai-service/requirements.txt)**

mediapipe
opencv-python
requests                         // For progress reporting

### **System Dependencies**

* **Python Version (Backend):** 3.11.0
* **Python Version (AI Service):** 3.12
* **Docker:** Required for local AI service development

## **16. Additional Files to Check for Hardcoded URLs**

When updating URLs or deploying to new environments, check these additional locations:

### **Potentially Affected Files**

| File/Location          | What to Check                    | Notes                              |
| :--------------------- | :------------------------------- | :--------------------------------- |
| backend/render.yaml    | Environment variable definitions | If using Blueprints for IaC        |
| backend/.env           | Local development URLs           | Not committed to git               |
| ai-service/.env        | Local BACKEND_URL override       | Not committed to git               |
| docker-compose.yml     | Service URLs for local testing   | If you create one                  |
| Integration test files | Any test scripts with URLs       | Check /backend/tests/ if exists    |
| GitHub Actions / CI    | Workflow files may have URLs     | Check .github/workflows/ if exists |

### **Environment Variables Checklist**

When setting up a new environment or troubleshooting:

**Mobile App:**

* ✅ `diamondmind-mobile/src/config.js` - Update `LIVE_BACKEND_URL`

**AI Service (Render Dashboard):**

* ✅ `PORT` = 8001
* ✅ `BACKEND_URL` = https://diamondmind-backend-yalf.onrender.com (optional override)

**Backend (Render Dashboard):**

* ✅ `PYTHON_VERSION` = 3.11.0
* ✅ `AI_SERVICE_URL` = https://dm-ai-service.onrender.com

**JIRA Automation (Local .env):**

* ✅ `JIRA_URL` = https://[your-domain].atlassian.net
* ✅ `JIRA_EMAIL` = [email]
* ✅ `JIRA_API_TOKEN` = [token]
* ✅ `PROJECT_KEY` = [key]

## **17. JIRA Automation & Sync**

We use a local Python script to manage JIRA stories, ensuring that the development context is always synchronized with the project management tool.

### **Scripts**

* **Location:** `backend/scripts/`
* **Files:** `sync_jira.py`, `stories.json`

### **Workflow**

1. **Define Stories:** Edit `stories.json` with the JSON format.
2. **Create/Update:** Run the script to push changes to JIRA.
   `python backend/scripts/sync_jira.py create`
3. **Transition:** Move tickets (optional).
   `python backend/scripts/sync_jira.py [TICKET-ID] Done`

### **Dependencies**

Requires `jira` and `python-dotenv` packages.

## **Important Notes**

* Always deploy the AI Worker (Service 1) before the API Gateway (Service 2)
* Wake services by visiting their health check endpoints before testing
* Never refactor "tribal knowledge" fixes without consultation
* Keep configuration variables synchronized across all deployments
* Run the "Victory Lap" prompt at the end of each JIRA Story or major bug fix
* Physical devices must be on the same WiFi network as your PC for local development
* **CRITICAL:** AI service must return landmarks as an array (indices 0-32), not as named objects
* **CRITICAL:** All mobile app URLs must be managed through config.js - never hardcode URLs directly
* **CRITICAL:** Use useVideoPlayer hook correctly; avoid manual play calls that race with state updates
* WebSocket URL must exactly match the backend URL (common source of progress bar issues)
* Monitor console logs during development to verify data flow and catch issues early
* When updating URLs, always update config.js FIRST, then verify backend environment variables match
