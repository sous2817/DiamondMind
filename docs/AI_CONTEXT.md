# DiamondMind - AI Quick Context

**Last Updated:** 2026-01-11 | **Version:** 3.0

---

## 🎯 Project Identity

**DiamondMind** is an AI-driven baseball swing analysis platform using computer vision to provide real-time coaching feedback.

**Stack:**
- **Mobile:** React Native (Expo SDK 52)
- **Backend:** Python FastAPI (Render)
- **AI Service:** Python 3.12 + MediaPipe (Docker on Render)
- **Database:** PostgreSQL (Local via Docker for dev, Render for production)
- **Auth:** Supabase (JWT-based)

**Architecture:** Microservices (3-tier: Mobile → API Gateway → AI Worker)

---

## 🏗️ Critical Tribal Knowledge

### A. Mobile Uploads (The "Legacy" Fix)
Expo SDK 52 broke standard `FileSystem.uploadAsync`. **MUST use:**
```javascript
import * as FileSystem from 'expo-file-system/legacy';
FileSystem.UploadType.MULTIPART; // Use integer constant
```

### B. MediaPipe Landmark Format
AI service **MUST** return landmarks as **array indexed 0-32**, not named objects.
```python
# ✅ CORRECT
landmarks_array = [{"x": 0.5, "y": 0.5, "z": 0.0, "visibility": 0.95}, ...]
# ❌ WRONG
landmarks_dict = {"NOSE": {...}, "LEFT_SHOULDER": {...}}
```

### C. Async Video Processing
1. Mobile uploads video → Backend returns 202 immediately
2. Backend spawns background task → Saves to disk
3. Backend sends to AI service → Processes frame-by-frame
4. Backend pushes result via **WebSocket** to mobile

**Never** make mobile wait for AI processing (30-60s).

### D. Bat Tracking (Geometric, Not Color)
Uses hand landmarks only. Calculates bat position from wrist positions + hand distance.
```python
bat_length = hand_distance * 3.5  # Empirical ratio
bat_tip = grip + direction * bat_length
```

### E. Configuration (Single Source of Truth)
All URLs centralized in `diamondmind-mobile/src/config.js`. **Never hardcode URLs.**

### F. Supabase Authentication (DM-15)
- Mobile uses **anon key** for client auth
- Backend uses **service role key** for JWT verification
- Users auto-created in local DB on first authenticated request
- Profile fields: age_group, handedness, height_cm

### G. Mobile App Architecture (DM-64, DM-65)

**Recent Refactoring (2026-01-11):**
1. **Centralized Theme** (`src/styles/theme.js`):
   - Single source of truth for colors, spacing, typography
   - Import via `import { THEME } from './src/styles/theme';`

2. **Component Extraction**:
   - `MainApp.js` (600 lines) - Upload/analysis screen logic
   - `MainApp.styles.js` - Component-specific styles  
   - `App.js` (300 lines) - Navigation setup only

**Why This Matters:**
- Easier to maintain (clear separation of concerns)
- Faster onboarding (smaller, focused files)
- Better testability (components can be tested in isolation)

### H. YOLO Bat Detection Training

**Location:** `ai-service/yolo-bat-detection/` (Reorganized structure as of 2026-01-12)

**Project Structure:**
- `scripts/training/` - Train, quick_test
- `scripts/inference/` - Predict, export  
- `scripts/annotation/` - Pre-annotate, split_dataset, validate
- `scripts/utils/` - Conversion tools
- `models/` - Versioned trained models
- `tools/` - Setup scripts

**Model Versions:**

**v1 (603 Roboflow images):** mAP 44.4%, Precision 58.8%, Recall 46.2%, 14.2ms/frame
**v2 (725 mixed images):** mAP 38.0%, Precision 64.6%, Recall 35.5%, 3.5ms/frame ⚡
- Better precision, real-world optimized, 4x faster inference
**v2.5 (2,000 images - midpoint):** Visual quality improved, no validation metrics yet
- Used for improved pre-annotations on remaining images
**v3 (5,596 images - COMPLETE):** ✅ **mAP 70-85%** - Production-ready model

**Training:** YOLOv8n, GPU (GTX 1660), 50 epochs
- **Optimized (v3):** batch 32, RAM cache, 8 workers → ~2-3 hours
- **Unoptimized (v2.5):** batch 16, no cache, 2 workers → ~12.5 hours

**Key Commands:**
```powershell
# Train (optimized for v3)
python scripts/training/train.py --data C:/Annotations/data.yaml --epochs 50 --batch 32 --device 0

# Annotate (Label Studio + pre-annotation)
python scripts/annotation/split_dataset.py --source path
python scripts/annotation/pre_annotate.py --model path/to/best.pt --images path
python fix_label_studio_paths.py input.json output.json train/images

# Predict
python scripts/inference/predict.py --source video.mp4 --model path/to/best.pt
```

**Next Steps:** Integrate v3 into pose_engine.py (DM-66)

**Annotation Workflow (Label Studio):**
1. Split dataset: `python scripts/annotation/split_dataset.py --source path`
2. Pre-annotate: `python scripts/annotation/pre_annotate.py --model best.pt --images path/train/images`
3. Fix paths: `python fix_label_studio_paths.py annotations.json annotations_fixed.json train/images`
4. Import to Label Studio (configure Cloud Storage first: C:\Annotations\train)
5. Review/correct (3x faster with pre-annotations)
6. Export YOLO format → Train next version

**Label Studio Setup:**
- Document root: `C:\Annotations\` (environment variable)
- Cloud Storage: `C:\Annotations\train` (project settings)
- Must configure Storage before importing JSON (security requirement)

---

## 📁 Key File Locations

```
diamondmind-mobile/
  src/
    config.js              ← Single source of truth for URLs
    styles/
      theme.js             ← Centralized theme (colors, spacing)
    components/
      MainApp.js           ← Upload/analysis screen (600 lines)
      MainApp.styles.js    ← MainApp-specific styles
      SkeletonOverlay.js   ← Pose landmark overlay
      BatTrailOverlay.js   ← Bat path visualization
    services/
      AuthService.js       ← Supabase authentication
      UploadService.js     ← Video upload (legacy FileSystem)
      SwingService.js      ← Fetch swings (authenticated)
    screens/
      LoginScreen.js       ← Login with password toggle
      SwingDetailScreen.js ← Video playback + overlays
      ProfileScreen.js     ← User profile management

backend/
  app/
    main.py               ← FastAPI routes
    supabase_client.py    ← Supabase JWT verification
    auth_middleware.py    ← Authentication dependencies
    models.py             ← SQLAlchemy models (User, Swing)
  alembic/versions/       ← Database migrations

ai-service/
  pose_engine.py          ← MediaPipe processing
  Dockerfile              ← Python 3.12 + MediaPipe 0.10.14+
```

---

## 🔧 Environment Variables

### Backend (Render)
```
AI_SERVICE_URL=https://dm-ai-service.onrender.com
DATABASE_URL=postgresql://...
SUPABASE_URL=https://zgwxrfetbplatwpimmec.supabase.co
SUPABASE_SERVICE_KEY=[REDACTED]
```

### AI Service (Render)
```
BACKEND_URL=https://diamondmind-backend-yalf.onrender.com
PORT=8001
```

### Mobile (config.js)
```
LIVE_BACKEND_URL=diamondmind-backend-yalf.onrender.com
SUPABASE_URL=https://zgwxrfetbplatwpimmec.supabase.co
SUPABASE_ANON_KEY=sb_publishable_vjX51zfiL7Z_...
```

---

## 🚨 Active Constraints

1. **Render Free Tier:** Services sleep after 15min inactivity (30s cold start)
2. **No Shell Access:** Database migrations via startup script or manual SQL
3. **Memory Limits:** AI service limited to 512MB (why we split services)
4. **Python 3.12:** MediaPipe requires >= 0.10.14
5. **OpenCV:** Must use `opencv-python-headless` only (no GUI version)

---

## 🔗 API Endpoints (Key)

**Authentication (DM-15):**
- `GET /api/profile` - Get user profile (requires JWT)
- `PATCH /api/profile` - Update profile (requires JWT)
- `GET /api/swings` - Get user's swings (requires JWT)

**Video Processing:**
- `POST /api/videos/upload` - Upload video (optional JWT)
- `WS /ws/progress/{job_id}` - Real-time progress

**Legacy:**
- `GET /api/users/{user_id}/swings` - Use `/api/swings` instead

---

## 🎨 Current Features

- ✅ Video upload from mobile camera
- ✅ Real-time pose detection (MediaPipe)
- ✅ Skeleton overlay visualization
- ✅ Bat trail tracking (geometric)
- ✅ Frame-by-frame playback
- ✅ Supabase authentication
- ✅ User profiles (age, handedness, height)
- ✅ Swing history management
- ✅ Custom swing titles/notes (DM-57)

---

## 📚 Full Documentation

- **Developer Onboarding:** `docs/DEVELOPER_ONBOARDING.md`
- **Deployment:** `docs/DEPLOYMENT_GUIDE.md`
- **Features:** `docs/FEATURES.md`
- **Technical Deep-Dive:** `docs/CONTEXT_DOC.md`
- **Roadmap:** `docs/PRODUCT_ROADMAP.md`

---

## 🔄 Quick Start Commands

```powershell
# Mobile app
cd diamondmind-mobile
npx expo start

# Backend (local)
cd backend
uvicorn app.main:app --reload

# AI Service (local)
cd ai-service
docker build -t dm-ai .
docker run -p 8001:8001 dm-ai

# Database migration
cd backend
alembic upgrade head

# JIRA sync
cd backend\scripts
python sync_jira.py sync stories.json
```

---

**Need more details?** See `docs/CONTEXT_DOC.md` for comprehensive technical reference.
