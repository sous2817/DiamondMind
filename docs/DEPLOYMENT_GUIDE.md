# DiamondMind Deployment Guide

**Last Updated:** 2026-01-11  
**Platform:** Render.com

---

## Overview

DiamondMind consists of 3 services on Render:
1. **Backend (API Gateway)** - FastAPI
2. **AI Service (Worker)** - MediaPipe in Docker
3. **Database** - PostgreSQL

**Deployment Order:** Database → AI Service → Backend

---

## Prerequisites

- GitHub account with access to DiamondMind repository
- Render account (free tier sufficient)
- Supabase project (for authentication)

---

## Step 1: Database Setup

### Create PostgreSQL Database

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **New +** → **PostgreSQL**
3. Configure:
   - **Name:** `diamondmind-db`
   - **Database:** `diamondmind`
   - **User:** `diamondmind`
   - **Region:** Virginia (US East)
   - **Instance Type:** Free

4. Click **Create Database**
5. **Save the Internal Database URL** (starts with `postgresql://`)

### Run Migrations

**Option A: From local machine (recommended)**
```powershell
cd backend
$env:DATABASE_URL="postgresql://..." # Use Internal URL from Render
alembic upgrade head
```

**Option B: Manual SQL via Render Shell**
1. Go to database in Render Dashboard
2. Click **Shell** tab
3. Run migration SQL manually

---

## Step 2: AI Service Deployment

### Deploy Docker Service

1. In Render Dashboard, click **New +** → **Web Service**
2. Select **Build and deploy from a Git repository**
3. Choose **DiamondMind** repository
4. Configure:

| Setting | Value |
|---------|-------|
| **Name** | `diamondmind-ai-service` |
| **Region** | Virginia (US East) |
| **Branch** | `main` |
| **Root Directory** | `ai-service` |
| **Runtime** | Docker |
| **Instance Type** | Free |

### Environment Variables

Click **Advanced** → Add these variables:

| Key | Value |
|-----|-------|
| `PORT` | `8001` |
| `BACKEND_URL` | *(Leave empty for now, update after backend deployment)* |
| `FRAME_SKIP` | `2` |

### Deploy

1. Click **Create Web Service**
2. Wait 5-10 minutes for build
3. **Save the service URL** (e.g., `https://dm-ai-service.onrender.com`)

### Verify

```powershell
curl https://dm-ai-service.onrender.com/
# Should return 404 or basic response (service is alive)
```

---

## Step 3: Backend Deployment

### Deploy Python Service

1. In Render Dashboard, click **New +** → **Web Service**
2. Select **DiamondMind** repository
3. Configure:

| Setting | Value |
|---------|-------|
| **Name** | `diamondmind-backend` |
| **Region** | Virginia (US East) |
| **Branch** | `main` |
| **Root Directory** | `backend` |
| **Runtime** | Python 3 |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
| **Instance Type** | Free |

### Environment Variables

Click **Advanced** → Add these variables:

| Key | Value | Notes |
|-----|-------|-------|
| `PYTHON_VERSION` | `3.12.0` | Required |
| `DATABASE_URL` | *(Paste Internal URL from Step 1)* | Use Internal URL |
| `AI_SERVICE_URL` | *(Paste AI Service URL from Step 2)* | No trailing slash |
| `SUPABASE_URL` | `https://zgwxrfetbplatwpimmec.supabase.co` | From Supabase dashboard |
| `SUPABASE_SERVICE_KEY` | *(Get from Supabase dashboard)* | Keep secret! |

### Deploy

1. Click **Create Web Service**
2. Wait 3-5 minutes for build
3. **Save the backend URL** (e.g., `https://diamondmind-backend-yalf.onrender.com`)

### Verify

Open in browser:
```
https://diamondmind-backend-yalf.onrender.com/docs
```
Should show FastAPI Swagger UI.

---

## Step 4: Update AI Service

Now that backend is deployed, update AI service with backend URL:

1. Go to AI Service in Render Dashboard
2. Click **Environment**
3. Update `BACKEND_URL`:
   - **Value:** *(Paste backend URL from Step 3)*
4. Click **Save Changes** (auto-deploys)

---

## Step 5: Mobile App Configuration

### Update Config File

Edit `diamondmind-mobile/src/config.js`:

```javascript
export default {
  // Backend URL (from Step 3)
  API_BASE_URL: 'https://diamondmind-backend-yalf.onrender.com',
  
  // Supabase config
  SUPABASE_URL: 'https://zgwxrfetbplatwpimmec.supabase.co',
  SUPABASE_ANON_KEY: 'sb_publishable_vjX51zfiL7Z_...',
};
```

### Test Mobile App

```powershell
cd diamondmind-mobile
npx expo start --clear
```

---

## Verification Checklist

- [ ] Database accessible via Internal URL
- [ ] AI Service responds to health check
- [ ] Backend Swagger UI loads
- [ ] Mobile app connects without errors
- [ ] Video upload works end-to-end
- [ ] Skeleton overlay appears

---

## Common Deployment Tasks

### Add Environment Variable

1. Go to service in Render Dashboard
2. Click **Environment**
3. Click **Add Environment Variable**
4. Enter Key and Value
5. Click **Save Changes** (auto-deploys)

### Manual Deploy

1. Go to service dashboard
2. Click **Manual Deploy** → **Deploy latest commit**
3. Monitor logs

### Rollback Deployment

1. Go to **Events** tab
2. Find previous successful deployment
3. Click **Rollback to this deploy**

### View Logs

1. Go to service dashboard
2. Click **Logs** tab
3. Use search/filter

---

## Environment Variables Reference

### Backend

| Variable | Required | Purpose |
|----------|----------|---------|
| `PYTHON_VERSION` | Yes | Python runtime version |
| `DATABASE_URL` | Yes | PostgreSQL connection |
| `AI_SERVICE_URL` | Yes | AI service endpoint |
| `SUPABASE_URL` | Yes | Supabase project URL |
| `SUPABASE_SERVICE_KEY` | Yes | Supabase service role key |

### AI Service

| Variable | Required | Purpose |
|----------|----------|---------|
| `PORT` | Yes | Service port (8001) |
| `BACKEND_URL` | Yes | Backend callback URL |
| `FRAME_SKIP` | No | Frame processing rate (default: 2) |

---

## Troubleshooting

### Service Won't Start

**Check:**
- All required environment variables set
- Logs for specific error messages
- Database connection string is correct

### Slow Processing

**Solutions:**
- Increase `FRAME_SKIP` to 3 (faster, less detailed)
- Verify free tier limits not exceeded
- Check if service is cold starting

### Database Connection Errors

**Solutions:**
- Use **Internal** database URL (not External)
- Verify database is running
- Run migrations if needed

### Mobile App Can't Connect

**Solutions:**
- Verify `API_BASE_URL` in `config.js`
- Check backend is deployed and awake
- Visit `/docs` endpoint to wake service

---

## Free Tier Limitations

### Constraints
- **AI Service:** 512MB RAM, shared CPU
- **Backend:** 512MB RAM, shared CPU
- **Database:** 1GB storage, 30-day expiration
- **Sleep:** Services sleep after 15 min inactivity

### Optimizations
- Frame skipping reduces CPU usage
- Video compression reduces memory usage
- Keep videos under 50MB

### Cold Starts
- First request after sleep: 30-60s
- Wake services by visiting their URLs
- Subsequent requests are fast

---

## Production Recommendations

### Upgrade Path

**For production use, consider:**
1. **Starter tier** ($7/month per service)
   - No sleep
   - More resources
   - Better performance

2. **Database upgrade** ($7/month)
   - No expiration
   - More storage
   - Better performance

### Security

- Rotate `SUPABASE_SERVICE_KEY` regularly
- Use environment-specific Supabase projects
- Enable HTTPS only
- Monitor logs for suspicious activity

---

## Related Documentation

- **Developer Setup:** `DEVELOPER_ONBOARDING.md`
- **Restoration:** `RESTORATION_GUIDE.md`
- **Features:** `FEATURES.md`
- **Context:** `CONTEXT_DOC.md`
