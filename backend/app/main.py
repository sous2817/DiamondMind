import httpx
import os
from fastapi import FastAPI, UploadFile, File, HTTPException, WebSocket, WebSocketDisconnect, Depends
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("backend")

app = FastAPI(title="DiamondMind Main Backend")

import shutil
from fastapi import BackgroundTasks

# Database imports
from app.database import engine, Base, get_db
from app.models import User, Swing, AnalysisResult, SwingStatus
from app.cleanup import cleanup_orphaned_swings

# Scheduler for cleanup jobs
from apscheduler.schedulers.asyncio import AsyncIOScheduler

class ConnectionManager:
    def __init__(self):
        self.active_connections: dict = {}

    async def connect(self, job_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[job_id] = websocket

    def disconnect(self, job_id: str):
        if job_id in self.active_connections:
            del self.active_connections[job_id]

    async def send_progress(self, job_id: str, progress: int):
        if job_id in self.active_connections:
            await self.active_connections[job_id].send_json({"progress": progress})

    async def send_result(self, job_id: str, result: dict):
        if job_id in self.active_connections:
            await self.active_connections[job_id].send_json({"result": result})

    async def send_error(self, job_id: str, message: str):
        if job_id in self.active_connections:
            # Strip HTML error pages and replace with friendly messages
            if message.strip().startswith("<!DOCTYPE") or message.strip().startswith("<html"):
                # Extract status code if present
                if "504" in message:
                    clean_msg = "AI service timeout - please try again"
                elif "503" in message:
                    clean_msg = "AI service unavailable - service may be starting up"
                elif "502" in message:
                    clean_msg = "AI service connection error"
                else:
                    clean_msg = "AI service error - please retry"
            else:
                # For non-HTML errors, keep first 150 chars
                clean_msg = message[:150] if len(message) > 150 else message
            
            await self.active_connections[job_id].send_json({"error": clean_msg})

manager = ConnectionManager()
scheduler = AsyncIOScheduler()

# Database startup event
@app.on_event("startup")
async def startup():
    """Create database tables on startup (for local dev with SQLite)"""
    logger.info("🚀 Starting up DiamondMind Backend...")
    
    # Run Alembic migrations automatically (for production)
    try:
        from alembic.config import Config
        from alembic import command
        import os
        
        # Only run migrations if DATABASE_URL is set (production)
        if os.getenv("DATABASE_URL"):
            logger.info("📊 Running database migrations...")
            alembic_cfg = Config("alembic.ini")
            command.upgrade(alembic_cfg, "head")
            logger.info("✅ Database migrations complete")
        else:
            # Local development - just create tables
            Base.metadata.create_all(bind=engine)
            logger.info("✅ Database tables created/verified (local SQLite)")
    except Exception as e:
        logger.error(f"⚠️ Migration failed: {str(e)}")
        # Fall back to creating tables directly
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables created/verified (fallback)")
    
    # Start cleanup job (runs every hour)
    scheduler.add_job(cleanup_orphaned_swings, 'interval', hours=1, id='cleanup_swings')
    scheduler.start()
    logger.info("🧹 Cleanup job scheduled (runs every hour)")

@app.post("/api/jobs/{job_id}/progress")
async def receive_progress(job_id: str, data: dict):
    await manager.send_progress(job_id, data["progress"])
    return {"status": "ok"}

@app.websocket("/ws/progress/{job_id}")
async def websocket_endpoint(websocket: WebSocket, job_id: str):
    await manager.connect(job_id, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(job_id)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

AI_SERVICE_URL = os.environ.get("AI_SERVICE_URL", "http://localhost:8001")

# ========== DIAGNOSTIC ENDPOINT ==========

@app.get("/api/debug/db-status")
async def debug_db_status(db: Session = Depends(get_db)):
    """Check database state and migration status"""
    try:
        from sqlalchemy import inspect, text
        
        inspector = inspect(db.bind)
        swings_columns = inspector.get_columns('swings')
        column_names = [col['name'] for col in swings_columns]
        
        # Check if new columns exist
        has_status = 'status' in column_names
        has_error_message = 'error_message' in column_names
        has_title = 'title' in column_names
        has_notes = 'notes' in column_names
        
        # Count records
        user_count = db.execute(text("SELECT COUNT(*) FROM users")).scalar()
        swing_count = db.execute(text("SELECT COUNT(*) FROM swings")).scalar()
        
        # Try to get status breakdown if column exists
        status_breakdown = {}
        if has_status:
            try:
                result = db.execute(text("SELECT status, COUNT(*) FROM swings GROUP BY status"))
                status_breakdown = {row[0]: row[1] for row in result}
            except:
                status_breakdown = {"error": "Could not query status"}
        
        return {
            "database": "connected",
            "migration_status": {
                "status_column": has_status,
                "error_message_column": has_error_message,
                "title_column": has_title,
                "notes_column": has_notes,
                "all_columns_present": has_status and has_error_message and has_title and has_notes
            },
            "record_counts": {
                "users": user_count,
                "swings": swing_count
            },
            "swing_status_breakdown": status_breakdown if has_status else "status column not yet migrated",
            "all_columns": column_names
        }
    except Exception as e:
        return {
            "database": "error",
            "error": str(e)
        }

# ========== DATABASE CRUD ENDPOINTS ==========

@app.post("/api/users", response_model=dict)
async def create_user(email: str, username: str, db: Session = Depends(get_db)):
    """Create a new user"""
    # Check if user already exists
    existing_user = db.query(User).filter(
        (User.email == email) | (User.username == username)
    ).first()
    
    if existing_user:
        raise HTTPException(status_code=400, detail="User with this email or username already exists")
    
    user = User(email=email, username=username)
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return {"id": user.id, "email": user.email, "username": user.username, "created_at": str(user.created_at)}

@app.get("/api/users/{user_id}")
async def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get user by ID"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"id": user.id, "email": user.email, "username": user.username, "created_at": str(user.created_at)}

@app.get("/api/auth/login")
async def login(email: str, db: Session = Depends(get_db)):
    """Simple email-based login (no password)"""
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"id": user.id, "email": user.email, "username": user.username, "created_at": str(user.created_at)}

@app.get("/api/users/{user_id}/swings")
async def get_user_swings(user_id: int, db: Session = Depends(get_db)):
    """Get all completed swings for a user"""
    try:
        # Try to filter by status (if column exists)
        swings = db.query(Swing).filter(
            Swing.user_id == user_id,
            Swing.status == SwingStatus.COMPLETED
        ).all()
    except Exception as e:
        # Fallback if status column doesn't exist yet (migration pending)
        logger.warning(f"Status filter failed, returning all swings: {str(e)}")
        swings = db.query(Swing).filter(Swing.user_id == user_id).all()
    
    return [
        {
            "id": swing.id,
            "filename": swing.filename,
            "title": getattr(swing, 'title', None),  # DM-57: Custom title
            "notes": getattr(swing, 'notes', None),  # DM-57: User notes
            "video_url": swing.video_url,
            "status": swing.status.value if hasattr(swing, 'status') and swing.status else 'completed',  # DM-56: Status tracking
            "created_at": str(swing.created_at),
            "has_analysis": swing.analysis is not None
        }
        for swing in swings
    ]

@app.get("/api/swings/{swing_id}/analysis")
async def get_swing_analysis(swing_id: int, db: Session = Depends(get_db)):
    """Get analysis result for a swing"""
    swing = db.query(Swing).filter(Swing.id == swing_id).first()
    if not swing:
        raise HTTPException(status_code=404, detail="Swing not found")
    
    if not swing.analysis:
        raise HTTPException(status_code=404, detail="Analysis not found for this swing")
    
    analysis = swing.analysis
    return {
        "id": analysis.id,
        "swing_id": analysis.swing_id,
        "skeletal_data": analysis.skeletal_data,
        "total_frames": analysis.total_frames,
        "frames_with_person": analysis.frames_with_person,
        "fps": analysis.fps,
        "bat_trail": analysis.bat_trail,
        "phase": analysis.phase,
        "score": analysis.score,
        "feedback": analysis.feedback,
        "drill": analysis.drill,
        "drill_explanation": analysis.drill_explanation,
        "created_at": str(analysis.created_at)
    }

@app.patch("/api/swings/{swing_id}")
async def update_swing(swing_id: int, title: str = None, notes: str = None, db: Session = Depends(get_db)):
    """Update swing title and/or notes (DM-57)"""
    swing = db.query(Swing).filter(Swing.id == swing_id).first()
    if not swing:
        raise HTTPException(status_code=404, detail="Swing not found")
    
    # Update fields if provided
    if title is not None:
        swing.title = title
    if notes is not None:
        swing.notes = notes
    
    db.commit()
    db.refresh(swing)
    
    logger.info(f"Updated swing {swing_id}: title='{swing.title}', notes length={len(swing.notes or '')}")
    
    return {
        "id": swing.id,
        "title": swing.title,
        "notes": swing.notes,
        "updated": True
    }

@app.delete("/api/swings/{swing_id}")
async def delete_swing(swing_id: int, db: Session = Depends(get_db)):
    """Delete a swing and its analysis (DM-57)"""
    swing = db.query(Swing).filter(Swing.id == swing_id).first()
    if not swing:
        raise HTTPException(status_code=404, detail="Swing not found")
    
    swing_filename = swing.filename
    
    # CASCADE will automatically delete analysis_results due to FK constraint
    db.delete(swing)
    db.commit()
    
    logger.info(f"Deleted swing {swing_id} (filename: {swing_filename})")
    
    return {"deleted": True, "swing_id": swing_id}

# ✅ Proxy Endpoint for Downloads
@app.get("/api/videos/download/{filename}")
async def download_video(filename: str):
    """Proxies the file download from AI Service to the Client."""
    async def iterfile():
        async with httpx.AsyncClient(timeout=600.0) as client:
            async with client.stream("GET", f"{AI_SERVICE_URL}/download/{filename}") as r:
                if r.status_code != 200:
                    raise HTTPException(status_code=r.status_code, detail="Could not retrieve video")
                async for chunk in r.aiter_bytes():
                    yield chunk

    return StreamingResponse(iterfile(), media_type="video/mp4")

async def process_video_background(file_data: bytes, filename: str, content_type: str, job_id: str, user_id: int = None):
    """Refactored async processor - saves file in background and stores results in database"""
    print(f"Background: 🎬 Starting processing for Job {job_id}")
    temp_path = None
    try:
        # Save file to temp in background
        temp_dir = "/tmp" if os.path.exists("/tmp") else "."
        ext = filename.split(".")[-1].lower()
        temp_path = os.path.join(temp_dir, f"upload_{job_id}.{ext}")
        
        print(f"Background: 💾 Saving file to {temp_path}...")
        with open(temp_path, "wb") as f:
            f.write(file_data)
        print(f"Background: ✅ File saved ({len(file_data)} bytes)")
        
        # Stream to AI Service
        with open(temp_path, "rb") as f:
            files = {"file": (filename, f, content_type)}
            
            # Explicit Timeout - 15 minutes to handle cold starts
            timeout_config = httpx.Timeout(900.0, connect=60.0)

            async with httpx.AsyncClient(timeout=timeout_config) as client:
                start_time = time.time()
                print(f"Background: 📤 Sending to AI Service for Job {job_id}...")
                response = await client.post(
                    f"{AI_SERVICE_URL}/analyze/pose", 
                    files=files,
                    params={"job_id": job_id}
                )
                duration = time.time() - start_time
                print(f"Background: ✅ AI Service responded in {duration:.2f}s")

        if response.status_code == 200:
             result = response.json()
             if "video_filename" in result:
                result["download_url"] = f"/api/videos/download/{result['video_filename']}"
             
             # 💾 Save to database if user_id is provided
             if user_id:
                 try:
                     from app.database import SessionLocal
                     db = SessionLocal()
                     
                     # Create Swing record with status='processing'
                     swing = Swing(
                         user_id=user_id,
                         filename=filename,
                         video_url=result.get("download_url"),
                         status=SwingStatus.PROCESSING
                     )
                     db.add(swing)
                     db.commit()
                     db.refresh(swing)
                     print(f"Background: 💾 Saved swing to database (ID: {swing.id}, status=processing)")
                     
                     # Create AnalysisResult record
                     analysis = AnalysisResult(
                         swing_id=swing.id,
                         skeletal_data=result.get("frames"),
                         total_frames=result.get("total_frames"),
                         frames_with_person=result.get("frames_with_person"),
                         fps=result.get("fps"),
                         bat_trail=result.get("bat_trail")
                     )
                     db.add(analysis)
                     db.commit()
                     
                     # Update swing status to 'completed'
                     swing.status = SwingStatus.COMPLETED
                     db.commit()
                     db.refresh(analysis)
                     print(f"Background: 💾 Saved analysis to database (ID: {analysis.id})")
                     print(f"Background: ✅ Swing {swing.id} marked as completed")
                     
                     # Add database IDs to result
                     result["swing_id"] = swing.id
                     result["analysis_id"] = analysis.id
                     
                     db.close()
                 except Exception as db_error:
                     print(f"Background: ⚠️ Database save failed: {str(db_error)}")
                     # Mark swing as failed if it was created
                     try:
                         if 'swing' in locals() and swing.id:
                             swing.status = SwingStatus.FAILED
                             swing.error_message = f"Database error: {str(db_error)[:500]}"
                             db.commit()
                             print(f"Background: ❌ Swing {swing.id} marked as failed")
                     except:
                         pass
                     # Continue anyway - don't fail the whole request
             
             await manager.send_result(job_id, result)
        else:
            # Truncate long error responses (e.g., HTML error pages)
            error_text = response.text[:200] if len(response.text) > 200 else response.text
            error_msg = f"AI Error {response.status_code}: {error_text}"
            print(f"Background Error: {error_msg}")
            await manager.send_error(job_id, error_msg)

    except Exception as e:
        error_str = str(e)[:200] if len(str(e)) > 200 else str(e)
        print(f"Background Error: {error_str}")
        
        # Mark swing as failed if it exists
        if user_id:
            try:
                from app.database import SessionLocal
                db = SessionLocal()
                # Find the swing by job_id (we'd need to store job_id, or find by recent upload)
                # For now, just log the error - cleanup job will handle orphaned swings
                print(f"Background: ⚠️ Upload failed for user {user_id}, cleanup job will remove orphaned records")
                db.close()
            except:
                pass
        
        await manager.send_error(job_id, error_str)
    finally:
        # Cleanup temp file
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)
            print(f"Background: 🧹 Cleaned up {temp_path}")

@app.post("/api/videos/upload")
async def upload_and_analyze(file: UploadFile = File(...), job_id: str = None, user_id: int = None):
    """
    ⚡️ ASYNC UPLOAD PATTERN:
    1. Read file into memory immediately (non-blocking)
    2. Return 202 Accepted ASAP (prevents load balancer timeout)
    3. Save & Process file in background task
    4. Push results via WebSocket
    
    Optional: Provide user_id to save results to database
    """
    allowed_extensions = ["mp4", "mov", "avi"]
    ext = file.filename.split(".")[-1].lower()
    if ext not in allowed_extensions:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {ext}")

    try:
        print(f"Backend: 📥 Received upload request for Job {job_id} (User: {user_id or 'anonymous'})")
        
        # ⚡️ KEY FIX: Read file into memory WITHOUT blocking the response
        # This is fast enough (<5s) to avoid timeout, then we return immediately
        file_data = await file.read()
        file_size_mb = len(file_data) / (1024 * 1024)
        print(f"Backend: 📦 File read into memory ({file_size_mb:.2f} MB)")
        
        # ⚡️ IMMEDIATE RESPONSE: Return 202 before any processing
        # This closes the HTTP connection in <5 seconds, avoiding the 60s timeout
        import asyncio
        asyncio.create_task(
            process_video_background(file_data, file.filename, file.content_type, job_id, user_id)
        )
        
        print(f"Backend: ✅ Returning 202 Accepted (Job {job_id} queued)")
        return {"status": "processing", "message": "Video accepted for background processing", "job_id": job_id}

    except Exception as e:
        logger.error(f"❌ Upload Handling Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))