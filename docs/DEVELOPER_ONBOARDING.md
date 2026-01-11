# DiamondMind Developer Onboarding

**Goal:** Get a new developer productive in 1 hour

---

## Prerequisites

### Required Software
- **Node.js** 18+ and npm
- **Python** 3.11+ (3.12 recommended)
- **Git**
- **Docker** (for AI service local development)
- **Code Editor** (VS Code recommended)

### Required Accounts
- **GitHub** - Access to DiamondMind repository
- **Render** - Backend and AI service deployment (optional for local dev)
- **Supabase** - Authentication service (get credentials from team)

### Recommended Tools
- **Expo Go** app on iOS/Android device for mobile testing
- **PostgreSQL client** (pgAdmin, DBeaver, or VS Code extension)
- **Postman** or **Thunder Client** for API testing

---

## Quick Start (30 minutes)

### Step 1: Clone Repository (2 min)

```powershell
git clone https://github.com/sous2817/DiamondMind.git
cd DiamondMind
```

### Step 2: Mobile App Setup (10 min)

```powershell
cd diamondmind-mobile
npm install
npx expo start
```

**What happens:**
- Installs React Native dependencies (~5 min)
- Starts Expo dev server
- Shows QR code for mobile testing

**Test it:**
1. Open Expo Go app on your phone
2. Scan QR code
3. App should load (may take 30s first time)

### Step 3: Backend Setup (10 min)

```powershell
cd ..\backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**Create `.env` file:**
```env
AI_SERVICE_URL=https://dm-ai-service.onrender.com
DATABASE_URL=sqlite:///./test.db
SUPABASE_URL=https://zgwxrfetbplatwpimmec.supabase.co
SUPABASE_SERVICE_KEY=<ask team for key>
```

**Start backend:**
```powershell
uvicorn app.main:app --reload
```

**Test it:**
- Open http://localhost:8000/docs
- Should see FastAPI Swagger UI

### Step 4: AI Service (Optional - 8 min)

**For local AI development only. Skip if using production AI service.**

```powershell
cd ..\ai-service
docker build -t dm-ai .
docker run -p 8001:8001 -e BACKEND_URL=http://host.docker.internal:8000 dm-ai
```

**Test it:**
- Open http://localhost:8001
- Should see `{"status": "healthy"}`

---

## Project Structure

```
DiamondMind/
├── diamondmind-mobile/     # React Native (Expo) mobile app
│   ├── src/
│   │   ├── config.js       # API URLs and Supabase config
│   │   ├── services/       # API clients (Auth, Upload, Swing)
│   │   ├── screens/        # UI screens
│   │   └── context/        # React context (UserContext)
│   └── app.json            # Expo configuration
│
├── backend/                # FastAPI backend (API Gateway)
│   ├── app/
│   │   ├── main.py         # Routes and endpoints
│   │   ├── models.py       # SQLAlchemy models
│   │   ├── database.py     # Database connection
│   │   ├── supabase_client.py    # Supabase integration
│   │   └── auth_middleware.py    # JWT authentication
│   ├── alembic/            # Database migrations
│   └── requirements.txt    # Python dependencies
│
├── ai-service/             # MediaPipe AI worker (Docker)
│   ├── pose_engine.py      # Core pose detection logic
│   ├── main.py             # FastAPI service
│   ├── Dockerfile          # Container definition
│   └── pose_landmarker_heavy.task  # MediaPipe model
│
└── docs/                   # Documentation
    ├── AI_CONTEXT.md       # Quick context for AI
    ├── FEATURES.md         # Feature documentation
    ├── DEPLOYMENT_GUIDE.md # Deployment instructions
    └── CONTEXT_DOC.md      # Technical reference
```

---

## Making Your First Change

### Scenario: Add a new API endpoint

**Goal:** Add a simple health check endpoint to the backend.

**Steps:**

1. **Open `backend/app/main.py`**

2. **Add new endpoint:**
```python
@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}
```

3. **Test it:**
```powershell
# Backend should auto-reload
curl http://localhost:8000/api/health
```

4. **Commit:**
```powershell
git add backend/app/main.py
git commit -m "feat: Add health check endpoint"
```

### Scenario: Update mobile UI

**Goal:** Change the app title on the home screen.

**Steps:**

1. **Open `diamondmind-mobile/src/screens/RecordScreen.js`**

2. **Find the title Text component and update it**

3. **Save file** - Expo will hot reload automatically

4. **See changes** on your phone immediately

---

## Common Development Tasks

### Run Database Migration

```powershell
cd backend
alembic upgrade head
```

### Create New Migration

```powershell
cd backend
alembic revision -m "add new column"
# Edit the generated file in alembic/versions/
alembic upgrade head
```

### Test API Endpoints

**Using Swagger UI:**
- http://localhost:8000/docs
- Click endpoint → "Try it out" → Execute

**Using curl:**
```powershell
# Upload video
curl -X POST http://localhost:8000/api/videos/upload `
  -F "file=@test.mp4" `
  -F "job_id=test123"

# Get profile (requires auth)
curl http://localhost:8000/api/profile `
  -H "Authorization: Bearer <jwt_token>"
```

### View Backend Logs

```powershell
cd backend
uvicorn app.main:app --reload --log-level debug
```

### Clear Mobile Cache

```powershell
cd diamondmind-mobile
npx expo start --clear
```

---

## Testing & Verification

### Backend Tests

```powershell
cd backend
pytest
```

### Mobile App Testing

**On Device:**
1. Use Expo Go app (development)
2. Scan QR code from `npx expo start`

**On Simulator:**
```powershell
# iOS (Mac only)
npx expo start --ios

# Android
npx expo start --android
```

### End-to-End Test

1. **Start all services:**
   - Backend: `uvicorn app.main:app --reload`
   - Mobile: `npx expo start`

2. **Test flow:**
   - Sign up new user in mobile app
   - Upload a swing video
   - Verify skeleton overlay appears
   - Check database for swing record

---

## Common Issues & Solutions

### Issue: "Module not found" in mobile app

**Solution:**
```powershell
cd diamondmind-mobile
rm -rf node_modules
npm install
npx expo start --clear
```

### Issue: Backend can't connect to database

**Solution:**
- Check `.env` file exists in `backend/`
- Verify `DATABASE_URL` is set
- For local dev, use SQLite: `DATABASE_URL=sqlite:///./test.db`

### Issue: Supabase authentication fails

**Solution:**
- Verify `SUPABASE_URL` and `SUPABASE_SERVICE_KEY` in backend `.env`
- Verify `SUPABASE_URL` and `SUPABASE_ANON_KEY` in mobile `src/config.js`
- Check Supabase dashboard for user confirmation status

### Issue: AI service timeout

**Solution:**
- Use production AI service URL (default in config)
- For local AI service, ensure Docker is running
- Check AI service logs: `docker logs <container_id>`

### Issue: Video upload fails

**Solution:**
- Check video file size (< 50MB recommended)
- Verify backend can reach AI service
- Check backend logs for error details

---

## Development Workflow

### Daily Workflow

1. **Pull latest changes:**
```powershell
git pull origin main
```

2. **Start services:**
```powershell
# Terminal 1: Backend
cd backend
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload

# Terminal 2: Mobile
cd diamondmind-mobile
npx expo start
```

3. **Make changes, test, commit**

4. **Push to GitHub:**
```powershell
git push origin feature/your-feature-name
```

### Before Committing

- [ ] Code follows existing style
- [ ] No console.log() or print() left in code
- [ ] Tested locally
- [ ] Updated documentation if needed
- [ ] Commit message follows format: `type: description`
  - Types: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`

---

## Key Files to Know

### Configuration Files

| File | Purpose |
|------|---------|
| `diamondmind-mobile/src/config.js` | API URLs, Supabase config |
| `backend/.env` | Backend environment variables |
| `backend/app/main.py` | API routes and endpoints |
| `ai-service/Dockerfile` | AI service container definition |

### Important Code

| File | Purpose |
|------|---------|
| `backend/app/auth_middleware.py` | JWT authentication |
| `backend/app/models.py` | Database schema |
| `diamondmind-mobile/src/services/AuthService.js` | Supabase authentication |
| `diamondmind-mobile/src/services/UploadService.js` | Video upload |
| `ai-service/pose_engine.py` | MediaPipe pose detection |

---

## Where to Find Help

### Documentation
- **Quick Start:** `docs/AI_CONTEXT.md`
- **Features:** `docs/FEATURES.md`
- **Deployment:** `docs/DEPLOYMENT_GUIDE.md`
- **Technical Details:** `docs/CONTEXT_DOC.md`

### Code Examples
- **API Endpoints:** http://localhost:8000/docs (Swagger UI)
- **Existing Features:** See `docs/FEATURES.md`

### Team Resources
- **JIRA:** Track tickets and features
- **GitHub Issues:** Bug reports and feature requests
- **Slack/Discord:** Ask questions (if applicable)

---

## Next Steps

After completing this onboarding:

1. **Read `docs/FEATURES.md`** - Understand what the system does
2. **Pick a JIRA ticket** - Start with "Good First Issue" label
3. **Read `docs/CONTEXT_DOC.md`** - Deep dive into architecture
4. **Join team standup** - Meet the team

**Estimated time to first PR:** 1-2 days

---

## Troubleshooting Checklist

If something isn't working:

- [ ] All services running? (backend, mobile, AI service if local)
- [ ] Environment variables set correctly?
- [ ] Dependencies installed? (`npm install`, `pip install -r requirements.txt`)
- [ ] Database migrated? (`alembic upgrade head`)
- [ ] Correct Node/Python versions?
- [ ] Firewall blocking ports? (8000, 8001, 19000-19006)
- [ ] Check logs for error messages

Still stuck? Check `docs/CONTEXT_DOC.md` Section 3: Tribal Knowledge for known issues.
