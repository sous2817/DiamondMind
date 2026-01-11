# DiamondMind Features

**Last Updated:** 2026-01-11

---

## Feature Overview

| Feature | Status | JIRA | Priority | Description |
|---------|--------|------|----------|-------------|
| **Core Functionality** |
| AI Skeleton Extraction | ✅ Live | DM-12 | High | MediaPipe pose landmark detection (33 points) |
| Video Upload & Processing | ✅ Live | DM-20, DM-21, DM-24 | Highest | Mobile video upload with async processing |
| Skeleton Overlay | ✅ Live | DM-13, DM-30 | Highest | Real-time skeleton visualization on video |
| Real-time Progress | ✅ Live | DM-26 | Medium | WebSocket-based processing updates |
| **User Management** |
| User Authentication | ✅ Live | DM-15, DM-55 | High | Supabase password-based auth |
| User Profiles | ✅ Live | DM-15 | High | Age group, handedness, height tracking |
| Swing History | ✅ Live | DM-55 | High | View all past swing analyses |
| **Swing Management** |
| Custom Swing Metadata | ✅ Live | DM-57 | Medium | Add titles and notes to swings |
| Swing Deletion | ✅ Live | DM-11, DM-57 | Medium | Delete unwanted swing records |
| Upload Cleanup | ✅ Live | DM-56 | Medium | Auto-cleanup of failed/aborted uploads |
| **Video Analysis** |
| Bat Trail Tracking | ✅ Live | DM-54 | High | Geometric bat position tracking |
| Frame-by-Frame Playback | ✅ Live | DM-59 | High | Manual frame stepping with arrow keys |
| Skeleton Toggle | ✅ Live | DM-52 | Medium | Show/hide skeleton overlay |
| Fullscreen Analysis | ✅ Live | DM-35 | High | Custom fullscreen with overlay |
| **Performance Optimizations** |
| Async Processing | ✅ Live | DM-50 | High | Background video analysis |
| Frame Skipping | ✅ Live | DM-28 | High | Process every Nth frame for speed |
| Skeleton Sync | ✅ Live | DM-49, DM-51 | High | Optimized overlay synchronization |
| High-Frequency Polling | ✅ Live | DM-37 | Highest | 60fps skeleton tracking |
| SVG Calibration | ✅ Live | DM-33 | Highest | Perfect overlay alignment |
| expo-video Migration | ✅ Live | DM-34 | Highest | Modern video engine |
| **UI/UX** |
| Modern Home Screen | ✅ Live | DM-42 | High | Professional UI with unified error handling |
| Safe Area Compliance | ✅ Live | DM-36 | High | Proper button positioning |
| Upload Cancellation | ✅ Live | DM-39 | Medium | Cancel in-progress uploads |
| Centralized Config | ✅ Live | DM-41 | High | Single source for API URLs |
| **Infrastructure** |
| Cloud Database | ✅ Live | DM-10 | High | PostgreSQL on Render |
| Dockerized AI Service | ✅ Live | DM-23 | High | Containerized MediaPipe service |
| Python 3.12 Compatibility | ✅ Live | DM-48 | High | Fixed dependency conflicts |
| Timestamp Display | ✅ Live | DM-8 | Medium | Show swing capture times |
| Age-Adaptive Prompting | ✅ Live | DM-16 | Medium | Tailored feedback by skill level |
| **Planned Features** |
| Video Compression | 📋 Planned | DM-58, DM-62 | High | Native video compression (post-Expo Go) |
| Video HTTP Serving | 📋 Planned | DM-61 | Medium | Serve videos via HTTP endpoint |
| Full Video Player in Detail | 📋 Planned | DM-60 | Medium | Add video player to SwingDetailScreen |
| YOLO Bat Detection | 📋 Planned | DM-53 | Low | ML-based bat tracking |
| Video Export | 📋 Planned | DM-40 | Lowest | Download video with overlay |
| **GenAI / RAG Features** |
| Vector Database Integration | 💡 Idea | DM-43 | High | Store swings for semantic search |
| RAG Pipeline | 💡 Idea | DM-44 | High | Natural language swing analysis |
| Semantic Search | 💡 Idea | DM-45 | Medium | Find similar swings |
| LLM Swing Comparisons | 💡 Idea | DM-46 | Medium | AI-generated comparison summaries |
| AI Coaching Chatbot | 💡 Idea | DM-47 | Medium | Interactive Q&A about swings |
| **Future Modes** |
| Pitching Analysis | 💡 Idea | DM-19 | Medium | Separate mode for pitching mechanics |
| **Platform Expansion** |
| React Web App | 💡 Idea | DM-31 | Medium | Desktop browser access |
| Native Mobile Wrapper | 💡 Idea | DM-18 | Medium | App Store/Play Store builds |
| Progressive Web App | 💡 Idea | DM-17 | Low | Installable web app |
| **Accessibility** |
| Text-to-Speech Feedback | 💡 Idea | DM-14 | Medium | Audio coaching feedback |

---

## Status Legend

- ✅ **Live** - Deployed to production, fully functional
- 🚧 **In Progress** - Currently being developed
- 📋 **Planned** - In backlog, design complete
- 💡 **Idea** - Concept stage, not yet scoped
- ❌ **Deprecated** - No longer supported

---

## Detailed Feature Documentation

### Core Functionality

#### AI Skeleton Extraction (DM-12) ✅
**What it does:** Extracts 33 body landmarks from each video frame using Google MediaPipe Pose Landmarker (Heavy model).

**How it works:**
- Frame-by-frame processing in AI service
- Landmarks returned as array (indices 0-32)
- Includes x, y, z coordinates + visibility score
- Handles occlusion and low-confidence frames

**API:** `POST /analyze/pose` (AI Service)

**Limitations:**
- Requires clear view of full body
- Performance degrades with poor lighting
- Occlusion can cause landmark loss

---

#### Video Upload & Processing (DM-20, DM-21, DM-24) ✅
**What it does:** Users upload swing videos from mobile device for AI analysis.

**How it works:**
1. Mobile uploads video → Backend returns 202 immediately
2. Backend spawns background task → Saves to disk
3. Backend sends to AI service → Processes frame-by-frame
4. Backend pushes result via WebSocket to mobile

**API:**
- `POST /api/videos/upload` - Upload video file
- `WS /ws/progress/{job_id}` - Real-time progress

**Limitations:**
- Max video size limited by Render free tier memory
- Supported formats: MP4, MOV
- Processing time: 30-60 seconds

---

#### Skeleton Overlay (DM-13, DM-30) ✅
**What it does:** Visualizes detected pose landmarks as connected skeleton on video playback.

**How it works:**
- Canvas-based rendering in React Native
- Connects landmarks based on MediaPipe pose connections
- Synchronized with video frame position
- Color-coded: Blue for body, red for current frame

**Limitations:**
- Overlay only visible when landmarks detected
- Performance may vary on older devices

---

### User Management

#### User Authentication (DM-15, DM-55) ✅
**What it does:** Secure user authentication using Supabase with email and password.

**How it works:**
- Supabase Auth integration
- JWT token-based API authentication
- Auto-refresh tokens
- Users synced to local database on first login

**API:**
- Supabase handles signup/login
- `GET /api/profile` - Get user profile
- `PATCH /api/profile` - Update profile

**Limitations:**
- Email confirmation disabled for MVP
- Existing users from old system must re-register

---

#### User Profiles (DM-15) ✅
**What it does:** Store user demographic data for personalized coaching.

**Fields:**
- Age group: 10u, 12u, 14u, 16u, 18u, college, adult
- Handedness: left, right, switch
- Height: centimeters

**API:** `PATCH /api/profile?age_group=adult&handedness=right&height_cm=180`

**Limitations:**
- Profile editing UI minimal (endpoint exists)
- No validation on height range in mobile app

---

### Swing Management

#### Custom Swing Metadata (DM-57) ✅
**What it does:** Add custom titles and notes to swing records.

**How to use:**
1. Open swing in SwingDetailScreen
2. Tap edit icon
3. Add/update title and notes
4. Save changes

**API:** `PATCH /api/swings/{swing_id}?title=...&notes=...`

**Limitations:**
- No character limit validation
- No rich text formatting

---

#### Swing Deletion (DM-11, DM-57) ✅
**What it does:** Permanently delete swing records.

**API:** `DELETE /api/swings/{swing_id}`

**Limitations:**
- No undo functionality
- Video file not deleted from storage (cleanup pending)

---

#### Upload Cleanup (DM-56) ✅
**What it does:** Automatically clean up database records for aborted/failed uploads.

**How it works:**
- Swing status tracking: pending, processing, completed, failed
- Background cleanup of old pending/failed swings
- Only completed swings shown in history

**Limitations:**
- Cleanup runs periodically (not immediate)
- Video files may remain on disk

---

### Video Analysis

#### Bat Trail Tracking (DM-54) ✅
**What it does:** Tracks bat position throughout swing using geometric calculation.

**How it works:**
- Geometric approach (no color detection)
- Calculates from wrist landmarks (15, 16)
- Bat length = hand distance × 3.5 (empirical ratio)
- Direction vector from hand positions

**Limitations:**
- Requires both hands visible
- Accuracy depends on hand landmark quality
- Minimum hand distance: 20 pixels

---

#### Frame-by-Frame Playback (DM-59) ✅
**What it does:** Step through swing video one frame at a time using arrow keys.

**How to use:**
1. Open swing in SwingDetailScreen
2. Use left/right arrow keys to step frames
3. Skeleton overlay updates with each frame

**Limitations:**
- Requires video to be loaded
- Frame precision depends on video FPS

---

### Performance Optimizations

#### Async Processing (DM-50) ✅
**What it does:** Processes videos in background without blocking mobile app.

**How it works:**
- FastAPI background tasks
- Immediate 202 response after upload
- Processing happens asynchronously
- Results delivered via WebSocket

**Limitations:**
- No retry mechanism if processing fails
- Job status not persisted (lost on server restart)

---

#### Frame Skipping (DM-28) ✅
**What it does:** Process every Nth frame for 2x faster analysis.

**How it works:**
- Processes every 2nd frame (30fps instead of 60fps)
- Maintains accuracy while reducing compute time
- Timestamp correctly mapped to actual video time

**Limitations:**
- May miss very fast movements
- Not configurable per-video

---

### Infrastructure

#### Cloud Database (DM-10) ✅
**What it does:** PostgreSQL database for persistent storage.

**Schema:**
- `users` - User accounts and profiles
- `swings` - Swing metadata and video URLs
- `analysis_results` - Pose landmarks and metrics

**Features:**
- Foreign key relationships with cascading deletes
- JSONB columns for efficient JSON storage
- Connection pooling for performance

**Limitations:**
- Render free tier: 1GB storage, 30-day expiration
- Recommend Starter tier ($7/month) for production

---

#### Dockerized AI Service (DM-23) ✅
**What it does:** Containerized AI service with all system dependencies.

**Why Docker:**
- MediaPipe requires system libraries (libGL, libglib)
- Standard Python environments lack these dependencies
- Docker bundles everything for reliable deployment

**Configuration:**
- Base: `python:3.12-slim`
- System deps: `libgl1-mesa-glx`, `libglib2.0-0`
- Port: 8001

---

## Planned Features

### Video Compression (DM-58, DM-62) 📋
**Goal:** Compress videos to 720p @ 2.5 Mbps before upload.

**Benefits:**
- Reduce file sizes from 50-100MB to 10-20MB
- Prevent AI service crashes (512MB RAM limit)
- Faster uploads and processing

**Status:** Infrastructure exists, needs native implementation (post-Expo Go)

---

### Video HTTP Serving (DM-61) 📋
**Goal:** Serve videos via HTTP URLs for mobile streaming.

**Current State:** Videos stored as local file paths

**Proposed Solution:**
- Option 1: FastAPI static files (MVP)
- Option 2: Cloud storage (S3/Supabase Storage) for production

---

### Full Video Player in Detail (DM-60) 📋
**Goal:** Add video playback to SwingDetailScreen.

**Features:**
- Video player with skeleton overlay
- Bat trail visualization
- Frame-by-frame scrubbing
- Fullscreen mode

**Status:** Endpoint exists, UI pending

---

## GenAI / RAG Features 💡

These features are in the ideation phase and represent the future vision for AI-powered coaching.

### Vector Database Integration (DM-43)
Store swing data in vector database (Pinecone/Weaviate) for semantic search.

### RAG Pipeline (DM-44)
Generate natural language coaching feedback using retrieval-augmented generation.

### Semantic Search (DM-45)
Find similar swings ("Pro Comps") based on biomechanics.

### LLM Swing Comparisons (DM-46)
AI-generated explanations of why swings are similar.

### AI Coaching Chatbot (DM-47)
Interactive Q&A about swing analysis.

---

## Platform Expansion 💡

### React Web App (DM-31)
Desktop browser access for deeper analysis.

### Native Mobile Wrapper (DM-18)
App Store and Play Store builds using EAS.

### Progressive Web App (DM-17)
Installable web app for offline access.

---

## For More Information

- **Roadmap:** See `docs/PRODUCT_ROADMAP.md` for priorities
- **Technical Details:** See `docs/CONTEXT_DOC.md` for implementation
- **Deployment:** See `docs/DEPLOYMENT_GUIDE.md` for setup
