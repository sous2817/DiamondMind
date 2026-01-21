# DiamondMind Technical Reference

**Version:** 3.0  
**Last Updated:** 2026-01-11

---

## Quick Links

- **Quick Start:** `AI_CONTEXT.md`
- **Developer Onboarding:** `DEVELOPER_ONBOARDING.md`
- **Deployment:** `DEPLOYMENT_GUIDE.md`
- **Features:** `FEATURES.md`
- **Roadmap:** `PRODUCT_ROADMAP.md`

---

## 1. Architecture Overview

### System Design

DiamondMind uses a 3-tier microservices architecture to isolate expensive AI processing from the API layer.

```
Mobile App (Expo)
    ↓ HTTPS
API Gateway (FastAPI)
    ↓ Internal HTTP
AI Worker (Docker + MediaPipe)
    ↓ Callback
API Gateway
    ↓ WebSocket
Mobile App
```

**Why this architecture:**
- **Memory isolation:** AI service (MediaPipe) needs 512MB+ RAM
- **Independent scaling:** Can upgrade AI service without touching API
- **Async processing:** Mobile doesn't wait for 30-60s AI processing
- **Free tier optimization:** Separate services = separate RAM limits

### Technology Choices

| Component | Technology | Why |
|-----------|------------|-----|
| Mobile | Expo SDK 52 | Cross-platform, fast iteration |
| API Gateway | FastAPI | Async support, auto-docs, Python ecosystem |
| AI Worker | MediaPipe | Best-in-class pose detection, free |
| Database | PostgreSQL | Relational data, JSONB support |
| Auth | Supabase | Managed auth, JWT tokens, free tier |
| Deployment | Render | Free tier, Docker support, easy setup |

### Mobile App Architecture (Post-Refactor)

**Component Structure:**
```
diamondmind-mobile/
  src/
    styles/
      theme.js              ← Centralized theme (colors, spacing)
    components/
      MainApp.js            ← Upload/analysis screen (600 lines)
      MainApp.styles.js     ← MainApp styles (separate for clarity)
      SkeletonOverlay.js
      BatTrailOverlay.js
    screens/
      LoginScreen.js
      ProfileScreen.js
      SwingDetailScreen.js
  App.js                    ← Navigation setup only (300 lines)
```

**Design Decisions (DM-64, DM-65):**
1. **Centralized Theme** (`src/styles/theme.js`):
   - Single source of truth for colors, spacing, typography
   - Prevents color inconsistencies
   - Easy to switch themes or rebrand

2. **Component Extraction** (`MainApp.js`):
   - Separated 600-line upload/analysis component from App.js
   - App.js now focuses solely on navigation setup
   - Improves maintainability and testability
   - Styles co-located with component for clarity

**Why This Matters:**
- **Before:** App.js was 917 lines (navigation + logic + styles)
- **After:** App.js is 300 lines (navigation only), MainApp.js is 600 lines (feature logic)
- **Benefit:** Easier to test, maintain, and onboard new developers

---

### C. YOLO Bat Detection Training Pipeline

**Challenge:** HSV color-based detection was brittle. Needed learning-based approach.

**Dataset Evolution:**
- **v1:** 603 Roboflow images → 44.4% mAP, 58.8% precision
- **v2:** +122 real-world images (Label Studio) → 38.0% mAP, 64.6% precision, 3.5ms inference
- **v3:** 5,596 images (complete dataset) → **70-85% mAP** ✅ **Production-ready**
- **Analysis:** Larger dataset dramatically improved accuracy. v3 ready for integration.

**Training (GPU Required):**
```powershell
# GPU setup (Windows)
pip uninstall torch torchvision -y
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121

# Train (10 min on GTX 1660)
python scripts/training/train.py --epochs 50 --batch 16 --device 0
```
- **Critical:** Reduce workers to 2 (Windows resource limits)
- **Result:** 5-6x faster than CPU

**Annotation Workflow (Label Studio):**
1. Split data BEFORE annotating: `scripts/annotation/split_dataset.py`
2. Pre-annotate: `scripts/annotation/pre_annotate.py --images path`
3. Import JSON into Label Studio (local file storage)
4. Review/correct (3x faster: 10 sec vs 30 sec per image)
5. Export to YOLO format

**Project Structure (Reorganized 2026-01-12):**
```
scripts/
  ├── training/     # train.py, quick_test.py
  ├── inference/    # predict.py, export.py
  ├── annotation/   # pre_annotate.py, split_dataset.py, validate_dataset.py
  └── utils/        # convert_*.py
models/
  ├── v1_baseline_603imgs/
  ├── v2_realworld_725imgs/
  └── v3_final_5596imgs/  ← **Latest production model (70-85% mAP)**
```

**Key Lessons:**
1. **Validation data must match production use** - Roboflow test set gave inflated metrics
2. **Precision > Recall for UX** - Fewer false alarms better than catching every bat
3. **Pre-annotation saves 5.5 hours per 1000 images**
4. **Windows quirks:** DataLoader workers=2 max, file locks during training
5. **Dataset size matters:** 600 imgs → 40% mAP, 5,596 imgs → 70-85% mAP

**Next:** Integrate v3 model into pose_engine.py (DM-66)

---

## 2. Tribal Knowledge

**Critical implementation details that aren't obvious from the code.**

### A. Expo FileSystem Breaking Change (SDK 52)

**Problem:** Standard `FileSystem.uploadAsync` broken in SDK 52.

**Solution:** Use legacy import:
```javascript
import * as FileSystem from 'expo-file-system/legacy';
```

**Why:** Expo moved to new architecture, old API deprecated but still works via `/legacy` path.

**Impact:** All video uploads must use this import or they'll fail silently.

---

### B. MediaPipe Landmark Format (CRITICAL)

**Problem:** MediaPipe can return landmarks as named objects OR arrays. Mobile expects arrays.

**Solution:** AI service MUST return array indexed 0-32:
```python
# ✅ CORRECT
landmarks = [
    {"x": 0.5, "y": 0.5, "z": 0.0, "visibility": 0.95},  # Index 0: NOSE
    {"x": 0.48, "y": 0.52, "z": 0.01, "visibility": 0.93},  # Index 1: LEFT_EYE_INNER
    # ... indices 2-32
]

# ❌ WRONG - Mobile can't parse this
landmarks = {
    "NOSE": {"x": 0.5, "y": 0.5, "z": 0.0},
    "LEFT_EYE_INNER": {...}
}
```

**Why:** Mobile overlay code uses `landmarks[15]` for wrist, etc. Named objects break this.

**Impact:** Wrong format = skeleton won't render.

---

### C. Async Video Processing Pattern

**Why async:**
- AI processing takes 30-60 seconds
- Render free tier has 100s HTTP timeout
- Mobile can't wait that long

**Flow:**
1. Mobile uploads video → Backend returns 202 immediately with `job_id`
2. Backend spawns `BackgroundTask` → Saves video to disk
3. Backend sends to AI service → Processes frame-by-frame
4. AI service sends progress updates → Backend forwards via WebSocket
5. AI service sends final result → Backend pushes to mobile via WebSocket

**Critical:** Never make mobile wait for AI processing in HTTP response.

---

### D. Bat Tracking (Geometric, Not Color)

**Why geometric:**
- Color-based (HSV) fails with wood bats, varying lighting
- Hand landmarks are reliable (MediaPipe strength)

**Algorithm:**
```python
# Get wrist positions (landmarks 15, 16)
left_wrist = landmarks[15]
right_wrist = landmarks[16]

# Calculate hand distance
hand_distance = distance(left_wrist, right_wrist)

# Empirical ratio (tested on 100+ swings)
bat_length = hand_distance * 3.5

# Direction vector from hand positions
direction = normalize(right_wrist - left_wrist)

# Bat tip position
bat_tip = grip_position + (direction * bat_length)
```

**Why 3.5 ratio:** Empirically derived from real swing data. Works for most bat sizes.

**Limitations:**
- Requires both hands visible
- Fails if hands too close (< 20px)
- Assumes standard bat length

---

### E. Configuration Single Source of Truth

**Problem:** URLs hardcoded in multiple files caused deployment bugs.

**Solution:** All URLs in `diamondmind-mobile/src/config.js`:
```javascript
export default {
  API_BASE_URL: 'https://diamondmind-backend-yalf.onrender.com',
  SUPABASE_URL: 'https://zgwxrfetbplatwpimmec.supabase.co',
  SUPABASE_ANON_KEY: 'sb_publishable_...',
};
```

**Rule:** NEVER hardcode URLs anywhere else. Import from `config.js`.

---

### F. Supabase Authentication Flow

**Why Supabase:**
- Managed auth (no password storage)
- JWT tokens (stateless)
- Free tier sufficient
- Email/password + social login support

**Flow:**
1. Mobile: User signs up → Supabase creates user, returns JWT
2. Mobile: Store JWT in AsyncStorage
3. Mobile: Include JWT in `Authorization: Bearer {token}` header
4. Backend: Verify JWT with Supabase service key
5. Backend: Look up user in local DB by `supabase_id`
6. Backend: If not found, create user automatically
7. Backend: Return user data

**Critical:** Backend uses **service role key** (secret), mobile uses **anon key** (public).

---

## 3. Data Flow Architecture

### Video Upload & Analysis

```
1. Mobile selects video
   ↓
2. Mobile uploads to /api/videos/upload
   ↓
3. Backend returns 202 + job_id immediately
   ↓
4. Mobile connects WebSocket /ws/progress/{job_id}
   ↓
5. Backend spawns BackgroundTask:
   - Saves video to /tmp/
   - Sends to AI service
   ↓
6. AI service processes:
   - Extracts frames
   - Runs MediaPipe on each frame
   - Sends progress updates to backend
   ↓
7. Backend forwards progress via WebSocket
   ↓
8. AI service sends final result to backend
   ↓
9. Backend saves to database:
   - Creates Swing record
   - Creates AnalysisResult record
   ↓
10. Backend pushes result via WebSocket
   ↓
11. Mobile receives result, displays skeleton overlay
```

**Key Points:**
- HTTP for upload (fast)
- WebSocket for progress (real-time)
- Background task for AI (async)
- Database for persistence

---

### Authentication & User Sync

```
1. Mobile: User signs up/logs in with Supabase
   ↓
2. Supabase: Returns JWT token
   ↓
3. Mobile: Stores JWT in AsyncStorage
   ↓
4. Mobile: Makes API request with JWT header
   ↓
5. Backend: auth_middleware.get_current_user()
   - Verifies JWT with Supabase
   - Extracts supabase_id from token
   ↓
6. Backend: Query local DB for user by supabase_id
   ↓
7. If user exists: Return user
   If not: Create user automatically
   ↓
8. Backend: User available in endpoint via Depends(get_current_user)
```

**Why auto-create users:**
- Supabase is source of truth for auth
- Local DB is source of truth for app data
- Sync happens automatically on first API call

---

## 4. API Contracts

### Authentication Endpoints

#### GET /api/profile
**Auth:** Required (JWT)  
**Returns:** Current user profile
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "user123",
  "age_group": "adult",
  "handedness": "right",
  "height_cm": 180
}
```

#### PATCH /api/profile
**Auth:** Required (JWT)  
**Params:** `age_group`, `handedness`, `height_cm` (all optional)  
**Returns:** Updated profile

---

### Swing Endpoints

#### POST /api/videos/upload
**Auth:** Optional (JWT)  
**Body:** Multipart form-data with `file` and `job_id`  
**Returns:**
```json
{
  "status": "processing",
  "job_id": "abc123"
}
```

#### GET /api/swings
**Auth:** Required (JWT)  
**Returns:** Array of user's swings
```json
[
  {
    "id": 1,
    "filename": "video.mp4",
    "title": "Practice swing",
    "notes": "Working on follow-through",
    "video_url": "/uploads/video.mp4",
    "status": "completed",
    "created_at": "2026-01-11T10:00:00",
    "has_analysis": true
  }
]
```

#### GET /api/swings/{swing_id}/analysis
**Auth:** None  
**Returns:** Full analysis with landmarks
```json
{
  "swing_id": 1,
  "skeletal_data": [
    {
      "frame_index": 0,
      "timestamp_ms": 0,
      "landmarks": [
        {"x": 0.5, "y": 0.5, "z": 0.0, "visibility": 0.95},
        // ... 32 more landmarks
      ]
    }
  ],
  "bat_trail": [...],
  "total_frames": 900,
  "fps": 30
}
```

---

## 5. Database Schema

### Users Table
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    supabase_id VARCHAR(255) UNIQUE,  -- UUID from Supabase
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    age_group VARCHAR(20),  -- Enum: 10u, 12u, 14u, 16u, 18u, college, adult
    handedness VARCHAR(10),  -- Enum: left, right, switch
    height_cm INTEGER,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### Swings Table
```sql
CREATE TABLE swings (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    filename VARCHAR(255) NOT NULL,
    title VARCHAR(255),
    notes TEXT,
    video_url VARCHAR(500),
    status VARCHAR(50) DEFAULT 'completed',  -- Enum: pending, processing, completed, failed
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Analysis Results Table
```sql
CREATE TABLE analysis_results (
    id SERIAL PRIMARY KEY,
    swing_id INTEGER REFERENCES swings(id) ON DELETE CASCADE,
    skeletal_data JSONB,  -- Array of frame data
    bat_trail JSONB,      -- Array of bat positions
    total_frames INTEGER,
    frames_with_person INTEGER,
    fps FLOAT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

**Key Design Decisions:**
- `supabase_id` for auth sync
- `JSONB` for flexible landmark storage
- `ON DELETE CASCADE` for data integrity
- Separate `analysis_results` table for large data

---

## 6. Performance & Constraints

### Render Free Tier Limits

| Service | RAM | CPU | Storage | Sleep |
|---------|-----|-----|---------|-------|
| Backend | 512MB | Shared | Ephemeral | 15 min |
| AI Service | 512MB | Shared | Ephemeral | 15 min |
| Database | N/A | N/A | 1GB | Never |

**Optimizations:**
- Frame skipping (process every 2nd frame) = 50% faster
- Video compression (target 720p) = 70% smaller files
- Async processing = no HTTP timeouts
- Connection pooling = handles cold starts

**Cold Start Behavior:**
- First request after 15min sleep: 30-60s
- Subsequent requests: < 1s
- Wake services by visiting URLs before testing

---

### Memory Management

**Problem:** MediaPipe + OpenCV + video file can exceed 512MB RAM.

**Solutions:**
1. **Frame skipping:** Process every 2nd frame (configurable via `FRAME_SKIP` env var)
2. **Video compression:** Mobile compresses before upload (pending native implementation)
3. **Streaming:** Don't load entire video into memory
4. **Cleanup:** Delete temp files immediately after processing

**Monitoring:**
- Watch Render logs for OOM (Out of Memory) errors
- If crashes occur, increase `FRAME_SKIP` to 3

---

## 7. Error Patterns

### Common Errors & Solutions

#### "Internal Server Error" on /api/profile

**Cause:** User not synced to local database

**Solution:** Check `auth_middleware.py` user creation logic. Verify `supabase_id` is set.

---

#### "Failed to fetch swings"

**Cause:** Using old endpoint `/api/users/{user_id}/swings` or missing JWT

**Solution:** Use `/api/swings` with `Authorization: Bearer {token}` header

---

#### Skeleton overlay doesn't appear

**Cause 1:** Landmarks in wrong format (named objects instead of array)  
**Solution:** Check AI service returns array indexed 0-32

**Cause 2:** Video aspect ratio mismatch  
**Solution:** Check SVG coordinate calibration in `SkeletonOverlay.js`

---

#### Video upload timeout

**Cause:** Using synchronous upload (waiting for AI processing)  
**Solution:** Verify async pattern (202 response + WebSocket)

---

## 8. Testing Strategy

### Local Testing

**Backend:**
```powershell
cd backend
pytest
```

**Mobile:**
- Use Expo Go on physical device
- Test on both iOS and Android
- Clear cache between tests: `npx expo start --clear`

**AI Service:**
```powershell
cd ai-service
docker build -t dm-ai .
docker run -p 8001:8001 dm-ai
# Test: curl http://localhost:8001/
```

---

### Integration Testing

**End-to-end flow:**
1. Sign up new user
2. Upload test video (5-10 seconds)
3. Verify WebSocket progress updates
4. Verify skeleton overlay appears
5. Verify swing appears in history
6. Delete swing

**Test videos:** Keep 3-5 test videos in `docs/test-videos/` for consistent testing.

---

## 9. Dependency Versions

### Critical Version Constraints

**Python:**
- **3.12** required for MediaPipe 0.10.14+
- **3.11** minimum for backend

**MediaPipe:**
- **0.10.14+** required for Python 3.12
- Earlier versions incompatible

**OpenCV:**
- **opencv-python-headless** ONLY
- Never use `opencv-python` (GUI version conflicts)

**Expo:**
- **SDK 52** current
- FileSystem requires `/legacy` import

**Node.js:**
- **18+** required for Expo
- **20** recommended

---

## 10. Security Considerations

### Secrets Management

**Never commit:**
- `SUPABASE_SERVICE_KEY`
- `JIRA_API_TOKEN`
- `DATABASE_URL` (production)

**Storage:**
- Backend: Render environment variables
- Mobile: `config.js` (anon key is public, safe to commit)
- Local: `.env` file (gitignored)

### Authentication

**JWT Verification:**
- Backend verifies every JWT with Supabase
- Tokens expire (managed by Supabase)
- No session storage on backend (stateless)

**User Data:**
- Users can only access their own swings
- Authenticated endpoints use `Depends(get_current_user)`
- No user_id in URLs (prevents enumeration)

---

## Related Documentation

- **Quick Start:** `AI_CONTEXT.md`
- **Setup:** `DEVELOPER_ONBOARDING.md`
- **Deploy:** `DEPLOYMENT_GUIDE.md`
- **Restore:** `RESTORATION_GUIDE.md`
- **Features:** `FEATURES.md`
- **Roadmap:** `PRODUCT_ROADMAP.md`
- **JIRA:** `JIRA_AUTOMATION.md`
