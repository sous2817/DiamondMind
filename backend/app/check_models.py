from google import genai

# REPLACE WITH YOUR KEY
client = genai.Client(api_key="AIzaSyAnokBwfUrpq2y_Fuf9n_kugKTCQ_8d-2E")

print("🔍 Listing available models...")

try:
    pager = client.models.list() 
    
    for model in pager:
        # Just print the name directly to avoid attribute errors
        print(f"✅ FOUND: {model.name}")
            
except Exception as e:
    print(f"❌ Error listing models: {e}")