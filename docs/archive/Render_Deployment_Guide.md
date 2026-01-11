# Render Deployment Guide
**DiamondMind - Environment Configuration & Deployment**

---

## Overview

This guide covers deploying and configuring DiamondMind services on Render.com, including environment variables, deployment procedures, and troubleshooting.

---

## Services Architecture

DiamondMind consists of three services on Render:

1. **Backend (API Gateway)** - FastAPI service
   - URL: `https://diamondmind-backend-yalf.onrender.com`
   - Language: Python
   - Database: PostgreSQL (external)

2. **AI Service** - MediaPipe pose detection
   - URL: Internal (called by backend)
   - Language: Python
   - Free tier: 512MB RAM, shared CPU

3. **Database** - PostgreSQL
   - Hosted on Render
   - Connection via `DATABASE_URL`

---

## Environment Variables

### Backend Service

| Variable | Value | Purpose |
|----------|-------|---------|
| `DATABASE_URL` | `postgresql://...` | PostgreSQL connection string |
| `JWT_SECRET_KEY` | `<secret>` | JWT token signing |
| `AI_SERVICE_URL` | `<ai-service-url>` | AI service endpoint |

### AI Service

| Variable | Value | Purpose | Added In |
|----------|-------|---------|----------|
| `BACKEND_URL` | `https://diamondmind-backend-yalf.onrender.com` | Backend callback URL | Initial |
| `BAT_HSV_LOWER` | `0,0,0` | Bat detection HSV lower bound | DM-33 |
| `BAT_HSV_UPPER` | `180,255,50` | Bat detection HSV upper bound | DM-33 |
| `FRAME_SKIP` | `2` | Frame skipping rate (1=none, 2=50%, 3=67%) | **DM-28** |

---

## Deployment Procedures

### Adding Environment Variables

1. **Navigate to Service:**
   - Go to https://dashboard.render.com
   - Select the service (Backend or AI Service)

2. **Add Variable:**
   - Click **"Environment"** in left sidebar
   - Click **"Add Environment Variable"**
   - Enter **Key** and **Value**
   - Click **"Save Changes"**

3. **Auto-Deploy:**
   - Service will automatically redeploy
   - Monitor in **"Logs"** tab

### Manual Deployment

**When to use:** After pushing code changes

1. Go to service dashboard
2. Click **"Manual Deploy"** → **"Deploy latest commit"**
3. Monitor deployment logs
4. Verify service health after deployment

### Rollback

**If deployment fails:**

1. Go to **"Events"** tab
2. Find previous successful deployment
3. Click **"Rollback to this deploy"**
4. Confirm rollback

---

## DM-28 Deployment (Frame Skipping)

### Step-by-Step

1. **Access AI Service:**
   - Dashboard → DiamondMind AI Service

2. **Add Environment Variable:**
   ```
   Key:   FRAME_SKIP
   Value: 2
   ```

3. **Save and Deploy:**
   - Click "Save Changes"
   - Wait for auto-deploy (~2-3 minutes)

4. **Verify Deployment:**
   - Check **"Logs"** tab for startup messages
   - Look for: `✅ Complete. Processed X frames.`

5. **Test:**
   - Upload a test video via mobile app
   - Check logs for: `...Read 100/900 frames, Processed 50`
   - Verify processing time is 30-45s (down from 60-90s)

### Troubleshooting

**Issue:** Service won't start after adding FRAME_SKIP

**Solution:**
- Check logs for errors
- Verify `FRAME_SKIP` is a number (not text)
- Try setting `FRAME_SKIP=1` to disable skipping

**Issue:** Processing is too slow

**Solution:**
- Increase skip rate: `FRAME_SKIP=3` (67% reduction)
- Monitor quality - may be too choppy

**Issue:** Skeleton rendering is choppy

**Solution:**
- Reduce skip rate: `FRAME_SKIP=1` (no skipping)
- Balance speed vs quality

---

## Monitoring & Logs

### Viewing Logs

1. Go to service dashboard
2. Click **"Logs"** tab
3. Use search/filter to find specific messages

### Key Log Messages

**AI Service Processing:**
```
🎬 Starting processing: /tmp/video.mp4 (Job: abc123)
   ...Read 100/900 frames, Processed 50 (3333ms)
   ...Read 200/900 frames, Processed 100 (6667ms)
✅ Complete. Processed 900 frames.
```

**Backend API:**
```
📡 WebSocket connecting to job: abc123
📤 Starting upload for Job ID: abc123, User ID: 2
✅ Analysis complete for job abc123
```

### Performance Metrics

**Before DM-28:**
- Processing time: 60-90s for 30s video
- Frames processed: 900 (30fps)
- CPU usage: High

**After DM-28 (FRAME_SKIP=2):**
- Processing time: 30-45s ✅
- Frames processed: 450 (15fps)
- CPU usage: Reduced

---

## Database Migrations

### Running Migrations (Alembic)

**From local machine:**

```bash
cd backend
set DATABASE_URL=postgresql://...  # Windows
alembic upgrade head
```

**Verify migration:**
```bash
alembic current
alembic history
```

### Manual SQL (If Alembic Fails)

1. Connect to database via Render dashboard
2. Go to **"Shell"** tab
3. Run SQL commands directly

**Example (DM-56/DM-57):**
```sql
-- Add swing metadata columns
ALTER TABLE swings ADD COLUMN title VARCHAR(255);
ALTER TABLE swings ADD COLUMN notes TEXT;
ALTER TABLE swings ADD COLUMN status VARCHAR(50) DEFAULT 'completed';
```

---

## Free Tier Limitations

### AI Service (512MB RAM)

**Constraints:**
- Limited CPU (shared)
- 512MB RAM
- Spins down after 15 minutes of inactivity

**Optimizations:**
- DM-29: Video compression (reduces memory usage)
- DM-28: Frame skipping (reduces CPU usage)
- Keep videos under 50MB

**Cold Start:**
- First request after spin-down takes 30-60s
- Subsequent requests are fast

---

## Configuration Best Practices

### Environment Variables

✅ **DO:**
- Use environment variables for all config
- Document variables in this guide
- Test changes in staging first (if available)

❌ **DON'T:**
- Hardcode URLs or secrets in code
- Change multiple variables at once
- Deploy without testing locally first

### Deployment

✅ **DO:**
- Monitor logs after deployment
- Test critical flows (upload, analysis)
- Keep this guide updated

❌ **DON'T:**
- Deploy during peak usage
- Skip testing
- Forget to update JIRA status

---

## Quick Reference

### Common Tasks

| Task | Steps |
|------|-------|
| Add env var | Environment → Add → Save |
| Deploy code | Manual Deploy → Deploy latest |
| View logs | Logs tab → Filter/Search |
| Rollback | Events → Previous deploy → Rollback |
| Check DB | Shell tab → Run SQL |

### Environment Variable Quick Copy

**AI Service:**
```
BACKEND_URL=https://diamondmind-backend-yalf.onrender.com
BAT_HSV_LOWER=0,0,0
BAT_HSV_UPPER=180,255,50
FRAME_SKIP=2
```

---

## Support & Troubleshooting

### Common Issues

**Service won't start:**
- Check logs for errors
- Verify all required env vars are set
- Check database connection

**Slow processing:**
- Increase FRAME_SKIP (2 → 3)
- Check free tier limits
- Monitor CPU usage

**Database errors:**
- Verify DATABASE_URL is correct
- Check database is running
- Run migrations if needed

### Getting Help

1. Check logs first
2. Review this guide
3. Check JIRA for related tickets
4. Test locally to isolate issue

---

## Changelog

| Date | Change | Ticket |
|------|--------|--------|
| 2026-01-08 | Added FRAME_SKIP environment variable | DM-28 |
| 2026-01-07 | Added swing metadata columns | DM-56/DM-57 |
| 2025-12-XX | Initial deployment | - |

---

## Related Documentation

- [Product Roadmap](file:///c:/dm/docs/Product_Roadmap.md)
- [JIRA Sync Guide](file:///c:/dm/docs/JIRA_SYNC_GUIDE.md)
- [DiamondMind Context Doc](file:///c:/dm/docs/DiamondMind%20Context%20Doc.md)
