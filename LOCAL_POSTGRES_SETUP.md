# Local Development with PostgreSQL

This guide explains how to run DiamondMind with a local PostgreSQL database instead of SQLite.

## Quick Start

### 1. Start Local Postgres

```powershell
# Start PostgreSQL container in background
docker-compose up -d

# Check if it's running
docker-compose ps
```

### 2. Update Environment

Copy `.env.example` to `.env` and make sure it uses the local DATABASE_URL:

```bash
DATABASE_URL=postgresql://diamond_user:dev_password_change_in_production@localhost:5432/diamondmind
SUPABASE_URL=https://zgwxrfetbplatwpimmec.supabase.co
SUPABASE_SERVICE_KEY=your_service_key_here
AI_SERVICE_URL=http://localhost:8001
```

### 3. Run Backend

```powershell
cd backend
uvicorn app.main:app --reload --port 8000
```

The backend will automatically:
- Connect to local Postgres
- Run migrations (create tables)
- Start accepting requests

## Database Management

### View Database

```powershell
# Connect to database via psql
docker exec -it diamondmind-db psql -U diamond_user -d diamondmind

# Common commands:
\dt              # List tables
\d users         # Describe users table
\d swings        # Describe swings table
SELECT * FROM users;
\q               # Quit
```

### Reset Database

```powershell
# Stop and remove container + volume
docker-compose down -v

# Start fresh
docker-compose up -d
```

### Stop Database

```powershell
# Stop (keeps data)
docker-compose stop

# Stop and remove (keeps data volume)
docker-compose down

# Stop and remove including data
docker-compose down -v
```

## Switching Between Local and Production

### Local Development
```bash
DATABASE_URL=postgresql://diamond_user:dev_password_change_in_production@localhost:5432/diamondmind
AI_SERVICE_URL=http://localhost:8001
```

### Production (Render)
```bash
DATABASE_URL=postgresql://diamondmind_user:PASSWORD@dpg-xxxxx-a/diamondmind  
AI_SERVICE_URL=https://dm-ai-service.onrender.com
```

## Benefits of Local Postgres

✅ **Free** - No Render DB charges  
✅ **Fast** - No network latency  
✅ **Offline** - Works without internet  
✅ **Safe** - Test without affecting production  
✅ **Easy Migration** - Same schema as production  

## Troubleshooting

### Port 5432 already in use
```powershell
# Check what's using port 5432
netstat -ano | findstr :5432

# Stop any existing Postgres service or change port in docker-compose.yml
```

### Connection refused
```powershell
# Make sure Docker is running
docker ps

# Check postgres logs
docker-compose logs postgres
```

### Tables not created
```powershell
# Frontend will auto-create tables on startup
# Or manually trigger: python -c "from app.database import Base, engine; Base.metadata.create_all(engine)"
```

### Reset everything
```powershell
docker-compose down -v
docker-compose up -d
# Restart backend - tables will be recreated
```

## Production Deployment

When deploying to Render, use the production `DATABASE_URL` from your Render Postgres instance. The same codebase works for both!
