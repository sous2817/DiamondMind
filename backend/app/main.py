from fastapi import FastAPI, UploadFile, File
import shutil
import os
from google import genai
from PIL import Image
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()

# --- CONFIGURATION ---
# 1. Setup the AI Client
# REPLACE THIS WITH YOUR ACTUAL KEY
API_KEY = os.getenv("API_KEY")
if not API_KEY:
    raise ValueError("No API Key found. Please check your .env file.")

client = genai.Client(api_key=API_KEY)

# 2. Setup Upload Folder
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.get("/health")
def health_check():
    return {"status": "ok", "brain": "Gemini 2.0 Active"}

@app.post("/analyze")
async def analyze_image(file: UploadFile = File(...)):   
    # flush=True forces the text to appear instantly in Windows PowerShell
    print(f"👁️ Receiving image: {file.filename}...", flush=True)
    
    file_location = f"{UPLOAD_DIR}/{file.filename}"
    
    try:
        # 1. Save the file
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # 2. Open image
        print("🧠 Image saved. Loading AI...", flush=True)

        # --- NEW PROMPT ---
        coach_prompt = """
                You are an elite hitting coach for 13U travel baseball players. Your job is to identify mechanical flaws based on a single snapshot.
                
                STEP 1: IDENTIFY THE PHASE
                First, determine which phase of the swing is shown in the image:
                - Stance (Waiting for pitch)
                - Load/Stride (gathering energy)
                - Connection/Contact (Bat meeting ball)
                - Extension/Follow-through (After contact)
                
                STEP 2: ANALYZE BASED ON PHASE
                Provide 3 specific bullet points of feedback RELEVANT TO THAT PHASE ONLY.
                
                If it is STANCE:
                - Check: Are knees inside feet? Are hands high (near ear)? Is the bat angle 45 degrees?
                
                If it is LOAD/STRIDE:
                - Check: Is the weight back? Have the hands separated back while the front foot moves forward?
                
                If it is CONTACT:
                - Check: Is the front leg firm (blocking)? Is the back elbow tucked (in the slot)? Is the head down on the ball?
                
                STEP 3: THE VERDICT
                Give a score out of 10 for this specific snapshot and one drill to improve.
                
                Analyze the image and provide output in strict JSON format.
        
                Your output must follow this exact schema:
                {
                    "phase": "String (Stance, Load, Contact, or Extension)",
                    "score": Integer (1-10),
                    "feedback": ["String", "String", "String"],
                    "drill": "String (Name of one specific drill)",
                    "drill_explanation": "String (One sentence explaining the drill)"
                }

                Do not include markdown formatting (like ```json). Just return the raw JSON string.
                """

        img = Image.open(file_location)

        # 3. Call the AI (Using the STABLE 1.5 Model)
        print("🚀 Sending to Gemini 2.5...", flush=True)
        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=[img, coach_prompt]
        )
        
        # 4. Extract text
        ai_description = response.text
        print(f"🗣️ Coach Said: {ai_description}", flush=True)

        return {
            "message": "Analysis Complete",
            "description": ai_description
        }

    except Exception as e:
        print(f"❌ CRITICAL ERROR: {type(e).__name__}", flush=True)
        print(f"❌ DETAILS: {str(e)}", flush=True)
        return {
            "message": "Error analyzing image",
            "description": f"Internal Error: {str(e)}"
        }