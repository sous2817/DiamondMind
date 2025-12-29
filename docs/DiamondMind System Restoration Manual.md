# DiamondMind System Restoration Manual

This guide provides step-by-step instructions for rebuilding your complete DiamondMind stack from scratch.

---

## Phase 1: AI Service (Worker)

The AI service processes video data and must be deployed first.

### 1.1 File Verification

Verify that `ai-service/Dockerfile` exists with the following configuration:

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

### 1.2 Render Deployment

1. Navigate to your Render dashboard and click **New +** → **Web Service**
2. Connect your DiamondMind repository
3. Configure the following settings:
   - **Name:** `diamondmind-ai-service`
   - **Runtime:** Docker
   - **Region:** Oregon (US West)
   - **Root Directory:** `ai-service`
   - **Dockerfile Path:** `Dockerfile`
4. Add environment variable:
   - `PORT = 8001`
5. Click **Create Web Service** and wait for deployment
6. Save the deployment URL (e.g., `https://diamondmind-ai-service.onrender.com`)

---

## Phase 2: Backend Service (API Gateway)

The backend service communicates with the mobile app and forwards requests to the AI service.

### 2.1 File Verification

Ensure `backend/requirements.txt` includes these critical dependencies:

```
fastapi
uvicorn
sqlalchemy
requests
httpx==0.27.0
opencv-python-headless
```

### 2.2 Render Deployment

1. Navigate to your Render dashboard and click **New +** → **Web Service**
2. Connect your DiamondMind repository
3. Configure the following settings:
   - **Name:** `diamondmind-backend`
   - **Runtime:** Python 3
   - **Region:** Oregon (US West)
   - **Root Directory:** `backend`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Add environment variables:
   - `PYTHON_VERSION = 3.11.0`
   - `AI_SERVICE_URL = [URL from Phase 1]` (no trailing slash)
5. Click **Create Web Service** and wait for deployment
6. Save the deployment URL (e.g., `https://diamondmind-backend-yalf.onrender.com`)

---

## Phase 3: Mobile App (React Native)

The mobile application runs on your device or emulator.

### 3.1 Configure API Endpoint

Update the backend URL in `diamondmind-mobile/src/services/UploadService.js`:

```javascript
import * as FileSystem from 'expo-file-system/legacy'; 

// Update this URL whenever you redeploy the backend
const API_URL = "https://diamondmind-backend-yalf.onrender.com"; 

const UploadService = {
    // ... your upload logic
}

export default UploadService;
```

### 3.2 Run Locally

1. Navigate to the mobile directory:
   ```powershell
   cd diamondmind-mobile
   ```

2. Start the Expo development server:
   ```powershell
   npx expo start --clear
   ```

3. Scan the QR code with your device to test the application

---

## Troubleshooting Guide

| Symptom | Root Cause | Solution |
|---------|-----------|----------|
| `[AxiosError: Network Error]` on device | Mobile app cannot reach backend | Verify `API_URL` in `diamondmind-mobile/src/services/UploadService.js` |
| `[Error: timeout]` on device | Services are in sleep mode | Visit the backend URL `/docs` endpoint in your browser to wake the service |
| `ModuleNotFoundError: cv2` in backend logs | OpenCV dependency missing | Add `opencv-python-headless` to `backend/requirements.txt` |
| `Connection Refused` in backend logs | Backend cannot connect to AI service | Verify `AI_SERVICE_URL` environment variable in Render backend settings |

---

## Important Notes

- Always deploy the AI service (Phase 1) before the backend service (Phase 2)
- Update the mobile app's `API_URL` whenever you redeploy the backend
- Render services may sleep after periods of inactivity; visit the URL to wake them
- Keep environment variables synchronized across deployments