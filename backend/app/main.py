from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
import json
from google import genai
from PIL import Image
from dotenv import load_dotenv
from sqlalchemy.orm import Session

# Local Imports
from . import models, database, prompts

# 1. Load Environment Variables
load_dotenv()

app = FastAPI()

# 2. Setup Database Tables
# This creates "diamond_mind.db" automatically if it doesn't exist
models.Base.metadata.create_all(bind=database.engine)

# 3. Setup CORS (Optional but good for Frontend)
# Allows your React app to talk to this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, change this to your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 4. Configure Google Gemini
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("No API Key found. Please check your .env file.")

client = genai.Client(api_key=API_KEY)

# 5. Setup Upload Directory
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# --- ROUTES ---

@app.get("/")
def read_root():
    return {"status": "Diamond Mind API is running ⚾"}

@app.post("/analyze")
async def analyze_image(
    file: UploadFile = File(...), 
    db: Session = Depends(database.get_db)
):
    print(f"👁️ Receiving image: {file.filename}...", flush=True)
    
    file_location = f"{UPLOAD_DIR}/{file.filename}"
    
    try:
        # A. Save the file locally
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        print("🧠 Image saved. Loading AI...", flush=True)
        img = Image.open(file_location)

        # B. Get the Prompt from our new file
        coach_prompt = prompts.get_coach_prompt()

        # C. Call the AI
        # Using gemini-3.0-flash-preview (or gemini-3-flash-preview if you prefer)
        print("🚀 Sending to Gemini...", flush=True)
        response = client.models.generate_content(
            model="gemini-3-flash-preview", 
            contents=[img, coach_prompt]
        )
        
        # D. Clean & Parse JSON
        raw_text = response.text.strip()
        # Remove markdown code blocks if the AI added them
        if raw_text.startswith("```json"):
            raw_text = raw_text.replace("```json", "").replace("```", "")
        elif raw_text.startswith("```"):
             raw_text = raw_text.replace("```", "")
        
        ai_data = json.loads(raw_text)
        print(f"🗣️ Coach Score: {ai_data.get('score', 0)}/10", flush=True)

        # E. Save to Database
        new_swing = models.SwingAnalysis(
            filename=file.filename,
            phase=ai_data.get("phase", "Unknown"),
            score=ai_data.get("score", 0),
            feedback=ai_data.get("feedback", []),
            drill=ai_data.get("drill", "None"),
            drill_explanation=ai_data.get("drill_explanation", "")
        )
        
        db.add(new_swing)
        db.commit()
        db.refresh(new_swing)
        
        print(f"💾 Saved to DB with ID: {new_swing.id}", flush=True)

        return {
            "message": "Analysis Complete & Saved",
            "id": new_swing.id,
            "data": ai_data 
        }

    except json.JSONDecodeError:
        print(f"❌ JSON Error. Raw text was: {raw_text}", flush=True)
        return {"message": "Error parsing AI response", "raw_response": raw_text}
        
    except Exception as e:
        print(f"❌ CRITICAL ERROR: {str(e)}", flush=True)
        return {"message": "Internal Server Error", "description": str(e)}

@app.get("/history")
def get_history(limit: int = 10, db: Session = Depends(database.get_db)):
    """Fetch the last 'limit' swings, newest first."""
    swings = db.query(models.SwingAnalysis).order_by(models.SwingAnalysis.id.desc()).limit(limit).all()
    return swings