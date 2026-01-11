# DiamondMind System Restoration Manual

This guide provides complete step-by-step instructions for deploying the DiamondMind stack from scratch, whether you're setting it up for the first time or rebuilding after a failure.

---

## Prerequisites

Before starting, ensure you have the following installed and configured:

### Required Software

- [ ] **Git** - [Download](https://git-scm.com/downloads)
- [ ] **Node.js** (v18 or higher) - [Download](https://nodejs.org/)
- [ ] **Docker Desktop** (for local AI service testing) - [Download](https://www.docker.com/products/docker-desktop/)
- [ ] **Python 3.11+** (for local backend testing) - [Download](https://www.python.org/downloads/)

### Required Accounts

- [ ] **GitHub Account** - Access to the DiamondMind repository
- [ ] **Render Account** - [Sign up](https://render.com/) (Free tier is sufficient)

### Verify Installations

```powershell
# Verify all tools are installed correctly
git --version          # Should show: git version 2.x.x
node --version         # Should show: v18.x.x or higher
npm --version          # Should show: 9.x.x or higher
docker --version       # Should show: Docker version 24.x.x
python --version       # Should show: Python 3.11.x or higher
```

---

## Phase 0: Initial Repository Setup

### Step 1: Clone the Repository

```powershell
# Navigate to your preferred directory
cd C:\

# Clone the DiamondMind repository
git clone https://github.com/sous2817/DiamondMind.git DM

# Navigate into the project
cd DM
```

### Step 2: Verify Project Structure

Your project should have this structure:

```
DM/
├── ai-service/
│   ├── Dockerfile
│   ├── main.py
│   ├── requirements.txt
│   └── pose_landmarker_heavy.task
├── backend/
│   ├── app/
│   │   └── main.py
│   └── requirements.txt
└── diamondmind-mobile/
    ├── src/
    │   └── services/
    │       └── UploadService.js
    ├── App.js
    └── package.json
```

### Step 3: Obtain Required Model File

The AI service requires the MediaPipe pose detection model file.

**Option A: If file is in repository**
- Verify `ai-service/pose_landmarker_heavy.task` exists
- File size should be approximately 100MB+

**Option B: If file is missing**
1. Download from [MediaPipe Models](https://developers.google.com/mediapipe/solutions/vision/pose_landmarker/index#models)
2. Save as `ai-service/pose_landmarker_heavy.task`

### Step 4: Connect GitHub to Render

1. Log in to your [Render Dashboard](https://dashboard.render.com/)
2. Click your profile icon → **Account Settings**
3. Navigate to **GitHub** section
4. Click **Connect GitHub Account**
5. Authorize Render to access your repositories
6. Select the DiamondMind repository

---

## Phase 1: AI Service Deployment (Worker)

The AI service processes video analysis and must be deployed first.

### Step 1: Verify Dockerfile

Navigate to `ai-service/Dockerfile` and verify it contains:

```dockerfile
# ai-service/Dockerfile
FROM python:3.12-slim
WORKDIR /app

# Install System Dependencies
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Install Python Dependencies
COPY requirements.txt .
COPY pose_landmarker_heavy.task . 
RUN pip install --no-cache-dir -r requirements.txt

# Start Application
COPY . .
EXPOSE 8001
CMD ["python", "main.py"]
```

**If file is missing or incorrect:** Create/update the file with the content above.

### Step 2: Deploy to Render

1. In your [Render Dashboard](https://dashboard.render.com/), click **New +** → **Web Service**
2. Select **Build and deploy from a Git repository**
3. Find and select your **DiamondMind** repository
4. Configure the service:

| Setting | Value |
|---------|-------|
| **Name** | `diamondmind-ai-service` |
| **Region** | Virginia (US East) |
| **Branch** | `main` (or your default branch) |
| **Root Directory** | `ai-service` |
| **Runtime** | Docker |
| **Instance Type** | Free |

5. Add Environment Variable:
   - Click **Advanced** → **Add Environment Variable**
   - **Key:** `PORT`
   - **Value:** `8001`

6. Click **Create Web Service**

### Step 3: Wait for Deployment

- Initial build takes 5-10 minutes
- Watch the logs for any errors
- Look for: `"Uvicorn running on..."` or similar success message

### Step 4: Save the URL

Once deployed, you'll see a URL like:
```
https://diamondmind-ai-service-xxxx.onrender.com
```

**CRITICAL:** Copy this URL - you'll need it for Phase 2.

### Step 5: Verify Deployment

Test the AI service is responding:

```powershell
curl https://diamondmind-ai-service-xxxx.onrender.com/
```

**Expected Result:** 404 or basic response (this is normal - it means the service is awake)

---

## Phase 2: Backend Service Deployment (API Gateway)

The backend communicates with the mobile app and forwards requests to the AI service.

### Step 1: Verify Requirements File

Navigate to `backend/requirements.txt` and verify it includes:

```
fastapi
uvicorn
sqlalchemy
requests
httpx==0.27.0
opencv-python-headless
```

**If missing:** Add the missing dependencies to the file.

### Step 2: Deploy to Render

1. In your [Render Dashboard](https://dashboard.render.com/), click **New +** → **Web Service**
2. Select **Build and deploy from a Git repository**
3. Find and select your **DiamondMind** repository
4. Configure the service:

| Setting | Value |
|---------|-------|
| **Name** | `diamondmind-backend` |
| **Region** | Virginia (US East) |
| **Branch** | `main` (or your default branch) |
| **Root Directory** | `backend` |
| **Runtime** | Python 3 |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
| **Instance Type** | Free |

5. Add Environment Variables:
   - Click **Advanced** → **Add Environment Variable**
   - **Variable 1:**
     - **Key:** `PYTHON_VERSION`
     - **Value:** `3.11.0`
   - **Variable 2:**
     - **Key:** `AI_SERVICE_URL`
     - **Value:** `[PASTE_AI_SERVICE_URL_FROM_PHASE_1]` (no trailing slash)

6. Click **Create Web Service**

### Step 3: Wait for Deployment

- Build takes 3-5 minutes
- Watch logs for: `"Application startup complete"`
- If you see errors about missing modules, check `requirements.txt`

### Step 4: Save the URL

Once deployed, you'll see a URL like:
```
https://diamondmind-backend-yalf.onrender.com
```

**CRITICAL:** Copy this URL - you'll need it for Phase 3.

### Step 5: Verify Deployment

Test the backend is responding:

```powershell
# This should open Swagger documentation in your browser
start https://diamondmind-backend-yalf.onrender.com/docs
```

**Expected Result:** Interactive API documentation loads successfully.

---

## Phase 3: Mobile App Setup (React Native)

The mobile application runs on your device or emulator.

### Step 1: Install Dependencies

```powershell
# Navigate to mobile directory
cd diamondmind-mobile

# Install all npm packages
npm install
```

**Expected Output:** No errors. Dependencies installed successfully.

### Step 2: Update Backend URL

**For First-Time Setup OR After Backend Redeployment:**

1. Open `diamondmind-mobile/src/services/UploadService.js`
2. Update the `API_URL` constant:

```javascript
import * as FileSystem from 'expo-file-system/legacy'; 

// 🚨 UPDATE THIS URL TO YOUR BACKEND FROM PHASE 2
const API_URL = "https://diamondmind-backend-yalf.onrender.com"; 

const UploadService = {
    // ... your upload logic
}
export default UploadService;
```

3. Save the file

### Step 3: Start the Development Server

```powershell
# Clear cache and start Expo
npx expo start --clear
```

**Expected Output:**
- QR code appears in terminal
- Development server starts
- Metro bundler running

### Step 4: Run on Device

**Option A: Physical Device (Recommended)**
1. Install **Expo Go** app from App Store (iOS) or Play Store (Android)
2. Scan the QR code with your camera (iOS) or Expo Go app (Android)
3. App should load on your device

**Option B: Android Emulator**
1. Press `a` in the terminal
2. App launches in Android Studio emulator

**Option C: iOS Simulator (Mac only)**
1. Press `i` in the terminal
2. App launches in iOS Simulator

---

## Phase 4: Verification & Testing

### Step 1: Wake the Services

Render Free Tier services sleep after 15 minutes of inactivity. Before testing:

```powershell
# Wake the backend
start https://diamondmind-backend-yalf.onrender.com/docs

# Wake the AI service
curl https://diamondmind-ai-service-xxxx.onrender.com/
```

Wait 10-15 seconds for services to fully wake up.

### Step 2: End-to-End Test

1. **Open the mobile app** on your device
2. **Select a test video** (ideally 5-10 seconds, under 50MB)
3. **Upload the video**
4. **Expected behavior:**
   - Upload progress indicator appears
   - Processing takes 10-30 seconds
   - Skeleton overlay appears on video
   - No error messages

### Step 3: Verify Success

**Signs of Successful Deployment:**
- ✅ Mobile app connects without "Network Error"
- ✅ Video uploads without timeout
- ✅ AI analysis completes and returns data
- ✅ Skeleton overlay renders on video

**Check Render Logs:**
1. Go to Render Dashboard
2. Click on each service
3. View **Logs** tab
4. Look for successful request logs (no 500 errors)

---

## Troubleshooting Guide

### Common Issues & Solutions

| Symptom | Root Cause | Solution |
|---------|-----------|----------|
| `[AxiosError: Network Error]` on device | Mobile app cannot reach backend | 1. Verify `API_URL` in `UploadService.js`<br>2. Ensure phone and computer on same WiFi (if local)<br>3. Check backend is deployed and awake |
| `[Error: timeout]` on device | Services are in sleep mode | Visit backend `/docs` and AI service `/` endpoints to wake them. Wait 15 seconds and retry. |
| `ModuleNotFoundError: cv2` in backend logs | OpenCV dependency missing | Add `opencv-python-headless` to `backend/requirements.txt` and redeploy |
| `Connection Refused` in backend logs | Backend cannot connect to AI service | Verify `AI_SERVICE_URL` environment variable in Render backend settings matches AI service URL exactly |
| Build fails on Render | Missing dependencies or incorrect path | 1. Check Root Directory is correct<br>2. Verify all files exist in repository<br>3. Check Render logs for specific error |
| `pose_landmarker_heavy.task not found` | Model file missing from AI service | Ensure file is in `ai-service/` directory and committed to repository |
| Mobile app won't start | Dependencies not installed | Run `npm install` in `diamondmind-mobile/` directory |

### Getting Help

If issues persist:
1. Check Render logs for both services
2. Review the Master Context Document for "Tribal Knowledge"
3. Verify all environment variables are set correctly
4. Ensure services are awake before testing

---

## Clean Slate: Starting Over

If you need to completely reset and redeploy:

### Delete Render Services

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click on each service (AI Service, Backend)
3. Click **Settings** → Scroll to bottom
4. Click **Delete Service** → Confirm

### Reset Local Environment

```powershell
# Pull latest code
cd C:\DM
git pull origin main

# Clean mobile dependencies
cd diamondmind-mobile
Remove-Item -Recurse -Force node_modules
Remove-Item -Recurse -Force .expo
npm install

# Return to root and restart from Phase 1
cd ..
```

### Redeploy

Follow this guide from **Phase 1** again with fresh services.

---

## Local Development Setup (Optional)

For testing changes locally before deploying:

### Run Backend Locally

```powershell
cd backend
$env:AI_SERVICE_URL="https://diamondmind-ai-service-xxxx.onrender.com"
uvicorn app.main:app --reload --port 8000
```

### Run AI Service Locally

```powershell
cd ai-service
docker build -t dm-ai .
docker run -p 8001:8001 dm-ai
```

### Update Mobile App for Local Testing

In `UploadService.js`, change:
- **Android Emulator:** `http://10.0.2.2:8000`
- **Physical Device:** `http://[YOUR_PC_IP]:8000` (find IP with `ipconfig`)

---

## Important Notes

- Always deploy the AI service (Phase 1) before the backend (Phase 2)
- Services must be awake before testing - visit their URLs to wake them
- Keep the URLs in `UploadService.js` updated whenever you redeploy
- Environment variables are case-sensitive
- Free tier services have resource limits (512MB RAM for backend)
- Cold starts can take 60+ seconds on first request after sleep

---

## Next Steps

After successful deployment:
1. Review the **Master Context Document** for development guidelines
2. Check "Tribal Knowledge" section for critical implementation details
3. Set up local development environment for faster iteration
4. Consider upgrading Render services to paid tier for production use