# DiamondMind Restoration Guide

**Last Updated:** 2026-01-11  
**Purpose:** Rebuild DiamondMind from scratch

---

## When to Use This Guide

- Setting up DiamondMind for the first time
- Recovering from catastrophic failure
- Migrating to new infrastructure
- Creating a fresh deployment

---

## Prerequisites

### Required Software
- Git
- Node.js 18+
- Python 3.12+
- Docker Desktop (optional, for local AI service)

### Required Accounts
- GitHub (repository access)
- Render (deployment platform)
- Supabase (authentication)

### Verify Installations

```powershell
git --version      # Should show 2.x.x
node --version     # Should show v18.x.x+
python --version   # Should show 3.12.x
```

---

## Restoration Steps

### 1. Clone Repository (2 min)

```powershell
git clone https://github.com/sous2817/DiamondMind.git
cd DiamondMind
```

**Verify structure:**
```
DiamondMind/
├── ai-service/
├── backend/
├── diamondmind-mobile/
└── docs/
```

### 2. Deploy Services (30 min)

Follow `DEPLOYMENT_GUIDE.md` in this order:
1. Database setup
2. AI Service deployment
3. Backend deployment
4. Mobile app configuration

**Quick checklist:**
- [ ] Database created and migrated
- [ ] AI Service deployed with correct env vars
- [ ] Backend deployed with all env vars
- [ ] Mobile app config updated

### 3. Verify Deployment (5 min)

**Test each service:**

```powershell
# Database
# (Test via backend connection)

# AI Service
curl https://dm-ai-service.onrender.com/

# Backend
start https://diamondmind-backend-yalf.onrender.com/docs

# Mobile
cd diamondmind-mobile
npx expo start --clear
```

### 4. End-to-End Test (5 min)

1. Open mobile app on device
2. Sign up new user
3. Upload test video (5-10 seconds)
4. Verify skeleton overlay appears
5. Check swing appears in history

---

## Recovery Scenarios

### Scenario 1: Database Lost

**Symptoms:**
- Backend can't connect to database
- All user data gone

**Recovery:**
1. Create new PostgreSQL database on Render
2. Update `DATABASE_URL` in backend env vars
3. Run migrations:
   ```powershell
   cd backend
   $env:DATABASE_URL="postgresql://..."
   alembic upgrade head
   ```
4. Restart backend service

**Data Loss:** All users and swings lost (no backup)

---

### Scenario 2: Backend Service Corrupted

**Symptoms:**
- Backend won't start
- 500 errors on all endpoints

**Recovery:**
1. Check Render logs for errors
2. Try rollback to previous deployment
3. If rollback fails, delete and recreate service:
   - Delete backend service in Render
   - Redeploy following `DEPLOYMENT_GUIDE.md` Step 3
   - Update mobile app config

**Data Loss:** None (database preserved)

---

### Scenario 3: AI Service Corrupted

**Symptoms:**
- Video processing fails
- Backend can't reach AI service

**Recovery:**
1. Check Render logs
2. Verify `pose_landmarker_heavy.task` file in repository
3. Try rollback
4. If rollback fails, delete and recreate:
   - Delete AI service in Render
   - Redeploy following `DEPLOYMENT_GUIDE.md` Step 2
   - Update `BACKEND_URL` in AI service env vars

**Data Loss:** None

---

### Scenario 4: Complete Infrastructure Loss

**Symptoms:**
- All Render services deleted
- Starting from zero

**Recovery:**
1. Follow full deployment guide from beginning
2. Estimated time: 45 minutes
3. All data lost (no backups)

**Prevention:**
- Export database regularly
- Keep environment variables documented
- Maintain service URLs in secure location

---

### Scenario 5: Repository Corrupted

**Symptoms:**
- Git repository inaccessible
- Code lost

**Recovery:**
1. Restore from GitHub (if pushed)
2. If not pushed, restore from local backup
3. If no backup, rebuild from documentation

**Prevention:**
- Push to GitHub regularly
- Keep local backups
- Document critical code patterns

---

## Data Backup Strategy

### Database Backup

**Manual Export:**
1. Go to database in Render Dashboard
2. Click **Shell** tab
3. Run:
   ```sql
   -- Export users
   COPY users TO '/tmp/users.csv' CSV HEADER;
   
   -- Export swings
   COPY swings TO '/tmp/swings.csv' CSV HEADER;
   ```
4. Download files

**Automated (Recommended):**
- Upgrade to Render Starter tier ($7/month)
- Enables automatic backups

### Code Backup

**GitHub:**
```powershell
git push origin main
```

**Local:**
```powershell
# Create backup
git bundle create diamondmind-backup.bundle --all

# Restore from backup
git clone diamondmind-backup.bundle DiamondMind
```

---

## Environment Variables Backup

Keep a secure copy of all environment variables:

**Backend:**
```env
PYTHON_VERSION=3.12.0
DATABASE_URL=postgresql://...
AI_SERVICE_URL=https://...
SUPABASE_URL=https://...
SUPABASE_SERVICE_KEY=...
```

**AI Service:**
```env
PORT=8001
BACKEND_URL=https://...
FRAME_SKIP=2
```

**Mobile:**
```javascript
// config.js
API_BASE_URL: 'https://...'
SUPABASE_URL: 'https://...'
SUPABASE_ANON_KEY: '...'
```

---

## Verification Checklist

After restoration, verify:

### Services
- [ ] Database accessible
- [ ] AI Service responds to health check
- [ ] Backend Swagger UI loads
- [ ] All environment variables set

### Functionality
- [ ] User signup works
- [ ] User login works
- [ ] Video upload works
- [ ] Skeleton overlay appears
- [ ] Swing history loads
- [ ] Profile updates work

### Performance
- [ ] Processing time < 45s
- [ ] No timeout errors
- [ ] Services wake from sleep

---

## Troubleshooting

### Issue: Services won't deploy

**Check:**
- GitHub connected to Render
- Repository accessible
- All required files present
- Dockerfile valid (AI service)

### Issue: Database migration fails

**Solutions:**
- Run migrations manually via SQL
- Check database connection string
- Verify alembic version compatibility

### Issue: Mobile app can't connect

**Solutions:**
- Verify `config.js` has correct URLs
- Check services are awake
- Test backend `/docs` endpoint

---

## Prevention Best Practices

### Regular Maintenance
- [ ] Push code to GitHub daily
- [ ] Export database weekly
- [ ] Document environment changes
- [ ] Test restoration process quarterly

### Monitoring
- [ ] Check Render logs weekly
- [ ] Monitor free tier limits
- [ ] Track error rates
- [ ] Review user feedback

### Documentation
- [ ] Keep `DEPLOYMENT_GUIDE.md` updated
- [ ] Document all env var changes
- [ ] Update this guide with new scenarios
- [ ] Maintain service URL list

---

## Recovery Time Estimates

| Scenario | Time | Data Loss |
|----------|------|-----------|
| Database only | 15 min | All data |
| Backend only | 15 min | None |
| AI Service only | 15 min | None |
| Complete rebuild | 45 min | All data |
| With backups | 60 min | Minimal |

---

## Related Documentation

- **Deployment:** `DEPLOYMENT_GUIDE.md`
- **Developer Setup:** `DEVELOPER_ONBOARDING.md`
- **Features:** `FEATURES.md`
- **Technical:** `CONTEXT_DOC.md`
