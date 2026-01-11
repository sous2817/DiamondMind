# GenAI Feature Set Implementation Plan
## DM-43, DM-44, DM-45, DM-46

Comprehensive plan for implementing Vector DB infrastructure, RAG coaching feedback, similarity search, and comparison explanations.

---

## User Review Required

> [!IMPORTANT]
> **Technology Decisions**
> 
> - **Vector DB:** Pinecone (free tier: 1 index, 100K vectors)
> - **LLM Provider:** OpenAI GPT-4 (most reliable, good docs)
> - **Embedding Model:** OpenAI text-embedding-3-small (cost-effective)
> - **Estimated API Costs:** $100-200 for development/testing

> [!WARNING]
> **Data Requirements**
> 
> - Need 10-20 pro swing videos for similarity search (DM-45)
> - Need 50-100 coaching tips/manuals for RAG (DM-44)
> - Consider sourcing strategy before starting implementation

---

## Implementation Phases

### Phase 1: Vector DB Infrastructure (DM-43)

**Goal:** Establish persistent vector storage for swing data and coaching content

#### Backend Changes

##### [NEW] [vector_store.py](file:///c:/dm/backend/app/vector_store.py)

Vector DB service module:
```python
from pinecone import Pinecone, ServerlessSpec
import os
import numpy as np

class VectorStore:
    def __init__(self):
        self.pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        self.index_name = "diamondmind-swings"
        self._ensure_index()
    
    def _ensure_index(self):
        """Create index if it doesn't exist"""
        if self.index_name not in self.pc.list_indexes().names():
            self.pc.create_index(
                name=self.index_name,
                dimension=132,  # 33 landmarks * 4 attributes
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region="us-east-1")
            )
    
    def upsert_swing(self, swing_id: int, user_id: int, landmarks: list, metadata: dict):
        """Store swing vector with metadata"""
        index = self.pc.Index(self.index_name)
        
        # Flatten landmarks to vector
        vector = self._flatten_landmarks(landmarks)
        
        index.upsert(vectors=[{
            "id": f"swing_{swing_id}",
            "values": vector,
            "metadata": {
                "swing_id": swing_id,
                "user_id": user_id,
                "timestamp": metadata.get("timestamp"),
                "type": metadata.get("type", "user"),  # user or pro
                **metadata
            }
        }])
    
    def _flatten_landmarks(self, landmarks: list) -> list:
        """Flatten 33 landmarks * 4 attributes to 132-dim vector"""
        vector = []
        for frame_landmarks in landmarks:
            for landmark in frame_landmarks:
                vector.extend([
                    landmark.get("x", 0),
                    landmark.get("y", 0),
                    landmark.get("z", 0),
                    landmark.get("visibility", 0)
                ])
        return vector[:132]  # Ensure fixed dimension
    
    def search_similar(self, swing_id: int, top_k: int = 3, filter_dict: dict = None):
        """Find similar swings using cosine similarity"""
        index = self.pc.Index(self.index_name)
        
        # Get the query vector
        result = index.fetch(ids=[f"swing_{swing_id}"])
        if not result.vectors:
            raise ValueError(f"Swing {swing_id} not found in vector DB")
        
        query_vector = result.vectors[f"swing_{swing_id}"].values
        
        # Search for similar vectors
        results = index.query(
            vector=query_vector,
            top_k=top_k + 1,  # +1 to exclude self
            include_metadata=True,
            filter=filter_dict
        )
        
        # Filter out the query swing itself
        matches = [m for m in results.matches if m.id != f"swing_{swing_id}"]
        return matches[:top_k]
```

##### [MODIFY] [requirements.txt](file:///c:/dm/backend/requirements.txt)

Add dependencies:
```
pinecone-client==3.0.0
openai==1.12.0
langchain==0.1.0
langchain-openai==0.0.5
```

##### [MODIFY] [.env.example](file:///c:/dm/backend/.env.example)

Add new environment variables:
```bash
# Vector DB
PINECONE_API_KEY=your_pinecone_api_key_here

# LLM
OPENAI_API_KEY=your_openai_api_key_here
```

---

#### AI Service Changes

##### [MODIFY] [main.py](file:///c:/dm/ai-service/main.py)

Add vector storage after successful analysis:
```python
from vector_store import VectorStore

vector_store = VectorStore()

@app.post("/analyze")
async def analyze_video(request: AnalysisRequest):
    # ... existing MediaPipe processing ...
    
    # After successful analysis, store in vector DB
    try:
        vector_store.upsert_swing(
            swing_id=request.swing_id,
            user_id=request.user_id,
            landmarks=skeletal_data,
            metadata={
                "timestamp": datetime.now().isoformat(),
                "type": "user",
                "fps": fps,
                "total_frames": total_frames
            }
        )
        logger.info(f"Stored swing {request.swing_id} in vector DB")
    except Exception as e:
        logger.error(f"Failed to store in vector DB: {e}")
        # Don't fail the analysis if vector storage fails
```

##### [NEW] [vector_store.py](file:///c:/dm/ai-service/vector_store.py)

Copy the same VectorStore class from backend (shared module).

---

### Phase 2A: RAG Coaching Feedback (DM-44)

**Goal:** Generate natural language coaching feedback using RAG

#### Data Preparation

##### [NEW] [coaching_data/](file:///c:/dm/backend/coaching_data/)

Directory structure:
```
coaching_data/
├── swing_mechanics.txt
├── common_flaws.txt
├── drills.txt
└── terminology.txt
```

Sample content for `common_flaws.txt`:
```
Casting: When the hands push away from the body too early in the swing, creating a long, sweeping path. 
Fix: Keep hands close to body during load phase. Practice short, direct path to ball.

Early Extension: Rising up out of athletic stance before contact, losing power and bat control.
Fix: Maintain knee flex through contact. Focus on staying "in the legs."

Bar Out: Leading with the barrel instead of hands, causing weak contact.
Fix: Lead with hands, let barrel lag behind. Practice inside-out swing path.
```

##### [NEW] [ingest_coaching_data.py](file:///c:/dm/backend/scripts/ingest_coaching_data.py)

Script to populate vector DB with coaching content:
```python
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from pinecone import Pinecone
import os

def ingest_coaching_data():
    """Load coaching manuals into vector DB"""
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    
    # Create separate index for coaching content
    index_name = "diamondmind-coaching"
    if index_name not in pc.list_indexes().names():
        pc.create_index(
            name=index_name,
            dimension=1536,  # OpenAI embedding dimension
            metric="cosine"
        )
    
    index = pc.Index(index_name)
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    
    # Load and chunk coaching texts
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    
    coaching_dir = "coaching_data"
    for filename in os.listdir(coaching_dir):
        with open(os.path.join(coaching_dir, filename), 'r') as f:
            text = f.read()
            chunks = text_splitter.split_text(text)
            
            for i, chunk in enumerate(chunks):
                vector = embeddings.embed_query(chunk)
                index.upsert(vectors=[{
                    "id": f"{filename}_{i}",
                    "values": vector,
                    "metadata": {
                        "text": chunk,
                        "source": filename,
                        "category": filename.replace('.txt', '')
                    }
                }])
    
    print(f"✅ Ingested coaching data into {index_name}")

if __name__ == "__main__":
    ingest_coaching_data()
```

---

#### Backend Changes

##### [NEW] [rag_service.py](file:///c:/dm/backend/app/rag_service.py)

RAG retrieval and generation:
```python
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.prompts import ChatPromptTemplate
from pinecone import Pinecone
import os

class RAGService:
    def __init__(self):
        self.pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        self.coaching_index = self.pc.Index("diamondmind-coaching")
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        self.llm = ChatOpenAI(model="gpt-4", temperature=0.7)
    
    def generate_feedback(self, pose_deviations: dict) -> str:
        """Generate coaching feedback based on detected flaws"""
        
        # Construct query from deviations
        query = self._build_query(pose_deviations)
        
        # Retrieve relevant coaching content
        context = self._retrieve_context(query)
        
        # Generate feedback using LLM
        feedback = self._generate_with_llm(query, context)
        
        return feedback
    
    def _build_query(self, deviations: dict) -> str:
        """Convert pose deviations to natural language query"""
        issues = []
        
        if deviations.get("hands_too_far"):
            issues.append("hands pushing away from body")
        if deviations.get("rising_up"):
            issues.append("losing knee flex before contact")
        if deviations.get("barrel_first"):
            issues.append("barrel leading hands")
        
        return " ".join(issues) if issues else "general swing mechanics"
    
    def _retrieve_context(self, query: str, top_k: int = 3) -> str:
        """Retrieve relevant coaching tips from vector DB"""
        query_vector = self.embeddings.embed_query(query)
        
        results = self.coaching_index.query(
            vector=query_vector,
            top_k=top_k,
            include_metadata=True
        )
        
        context_chunks = [match.metadata["text"] for match in results.matches]
        return "\n\n".join(context_chunks)
    
    def _generate_with_llm(self, query: str, context: str) -> str:
        """Synthesize coaching feedback using LLM"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a professional baseball hitting coach. 
            Based on the swing analysis and coaching knowledge provided, 
            give clear, actionable feedback. Be specific and encouraging.
            
            Coaching Knowledge:
            {context}
            """),
            ("user", "Detected issues: {query}\n\nProvide coaching feedback:")
        ])
        
        chain = prompt | self.llm
        response = chain.invoke({"context": context, "query": query})
        
        return response.content
```

##### [MODIFY] [main.py](file:///c:/dm/backend/app/main.py)

Add RAG feedback to analysis endpoint:
```python
from rag_service import RAGService

rag_service = RAGService()

@app.post("/api/analysis/generate-feedback")
async def generate_feedback(swing_id: int, db: Session = Depends(get_db)):
    """Generate natural language coaching feedback"""
    
    swing = db.query(Swing).filter(Swing.id == swing_id).first()
    if not swing or not swing.analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    # Extract pose deviations from analysis
    deviations = extract_deviations(swing.analysis.skeletal_data)
    
    # Generate feedback using RAG
    feedback = rag_service.generate_feedback(deviations)
    
    # Store feedback in database
    swing.analysis.ai_feedback = feedback
    db.commit()
    
    return {"feedback": feedback}
```

---

### Phase 2B: Similarity Search (DM-45)

**Goal:** Find similar swings using vector similarity

#### Backend Changes

##### [NEW] [/api/swings/search](file:///c:/dm/backend/app/main.py)

Similarity search endpoint:
```python
@app.get("/api/swings/search")
async def search_similar_swings(
    swing_id: int,
    top_k: int = 3,
    filter_type: str = None,  # "pro" or "user"
    db: Session = Depends(get_db)
):
    """Find similar swings using vector similarity"""
    
    # Build filter for pro vs user swings
    filter_dict = {"type": filter_type} if filter_type else None
    
    # Search vector DB
    matches = vector_store.search_similar(
        swing_id=swing_id,
        top_k=top_k,
        filter_dict=filter_dict
    )
    
    # Fetch swing details from database
    similar_swings = []
    for match in matches:
        match_swing_id = match.metadata["swing_id"]
        swing = db.query(Swing).filter(Swing.id == match_swing_id).first()
        
        if swing:
            similar_swings.append({
                "id": swing.id,
                "video_url": swing.video_url,
                "title": swing.title or swing.filename,
                "similarity_score": match.score,
                "type": match.metadata.get("type"),
                "metadata": match.metadata
            })
    
    return {"similar_swings": similar_swings}
```

---

#### Data Preparation

##### [NEW] [scripts/ingest_pro_swings.py](file:///c:/dm/backend/scripts/ingest_pro_swings.py)

Script to populate pro swing dataset:
```python
import os
from app.vector_store import VectorStore
from app.database import SessionLocal
from app.models import Swing

def ingest_pro_swings():
    """Ingest pro swing videos into vector DB"""
    vector_store = VectorStore()
    db = SessionLocal()
    
    # Directory with pro swing videos
    pro_swings_dir = "data/pro_swings"
    
    for filename in os.listdir(pro_swings_dir):
        if filename.endswith(".mp4"):
            # Process video through MediaPipe
            # (reuse existing analysis pipeline)
            
            # Store in vector DB with type="pro"
            vector_store.upsert_swing(
                swing_id=swing_id,
                user_id=0,  # System user for pro swings
                landmarks=landmarks,
                metadata={
                    "type": "pro",
                    "player_name": extract_player_name(filename),
                    "timestamp": datetime.now().isoformat()
                }
            )
    
    print("✅ Ingested pro swings")

if __name__ == "__main__":
    ingest_pro_swings()
```

---

### Phase 3: Comparison Explanations (DM-46)

**Goal:** Explain why swings are similar using LLM

#### Backend Changes

##### [MODIFY] [rag_service.py](file:///c:/dm/backend/app/rag_service.py)

Add comparison method:
```python
def generate_comparison(self, user_swing_data: dict, pro_swing_data: dict, pro_name: str) -> str:
    """Generate comparison explanation between user and pro swing"""
    
    # Extract keyframes from both swings
    user_keyframes = self._extract_keyframes(user_swing_data)
    pro_keyframes = self._extract_keyframes(pro_swing_data)
    
    # Build comparison prompt
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a baseball hitting coach comparing two swings.
        Explain the similarities and differences in simple terms.
        Focus on 3-4 key points. Be encouraging but honest."""),
        ("user", """Compare this user's swing to {pro_name}'s swing:
        
        User Swing Keyframes:
        - Stance: {user_stance}
        - Load: {user_load}
        - Contact: {user_contact}
        - Follow-through: {user_followthrough}
        
        {pro_name}'s Swing Keyframes:
        - Stance: {pro_stance}
        - Load: {pro_load}
        - Contact: {pro_contact}
        - Follow-through: {pro_followthrough}
        
        Provide a comparison summary:""")
    ])
    
    chain = prompt | self.llm
    response = chain.invoke({
        "pro_name": pro_name,
        "user_stance": user_keyframes["stance"],
        "user_load": user_keyframes["load"],
        "user_contact": user_keyframes["contact"],
        "user_followthrough": user_keyframes["followthrough"],
        "pro_stance": pro_keyframes["stance"],
        "pro_load": pro_keyframes["load"],
        "pro_contact": pro_keyframes["contact"],
        "pro_followthrough": pro_keyframes["followthrough"],
    })
    
    return response.content

def _extract_keyframes(self, swing_data: dict) -> dict:
    """Extract key swing phases from full landmark data"""
    # Simplified keyframe extraction
    # In reality, would use phase detection from existing analysis
    
    total_frames = len(swing_data["frames"])
    
    return {
        "stance": self._summarize_frame(swing_data["frames"][0]),
        "load": self._summarize_frame(swing_data["frames"][total_frames // 4]),
        "contact": self._summarize_frame(swing_data["frames"][total_frames // 2]),
        "followthrough": self._summarize_frame(swing_data["frames"][-1])
    }

def _summarize_frame(self, frame: dict) -> str:
    """Convert frame landmarks to text description"""
    # Extract key body positions
    landmarks = frame["landmarks"]
    
    # Calculate key angles/positions
    hand_height = landmarks[15]["y"]  # Right wrist
    knee_angle = calculate_angle(landmarks[23], landmarks[25], landmarks[27])
    
    return f"Hand height: {hand_height:.2f}, Knee angle: {knee_angle:.0f}°"
```

##### [NEW] [/api/swings/compare](file:///c:/dm/backend/app/main.py)

Comparison endpoint:
```python
@app.get("/api/swings/compare")
async def compare_swings(
    user_swing_id: int,
    pro_swing_id: int,
    db: Session = Depends(get_db)
):
    """Generate comparison explanation between user and pro swing"""
    
    user_swing = db.query(Swing).filter(Swing.id == user_swing_id).first()
    pro_swing = db.query(Swing).filter(Swing.id == pro_swing_id).first()
    
    if not user_swing or not pro_swing:
        raise HTTPException(status_code=404, detail="Swing not found")
    
    # Generate comparison using RAG
    comparison = rag_service.generate_comparison(
        user_swing_data=user_swing.analysis.skeletal_data,
        pro_swing_data=pro_swing.analysis.skeletal_data,
        pro_name=pro_swing.title or "Pro Player"
    )
    
    return {
        "user_swing_id": user_swing_id,
        "pro_swing_id": pro_swing_id,
        "pro_name": pro_swing.title,
        "comparison": comparison
    }
```

---

## Verification Plan

### DM-43 Testing
- Verify Pinecone index creation
- Test swing vector upsert
- Validate vector dimensions (132)
- Check metadata storage

### DM-44 Testing
- Test coaching data ingestion
- Verify RAG retrieval quality
- Test LLM feedback generation
- Validate no hallucinations

### DM-45 Testing
- Test similarity search accuracy
- Verify pro swing filtering
- Test edge case: no similar swings found
- Validate self-exclusion from results

### DM-46 Testing
- Test comparison generation
- Verify keyframe extraction
- Test token limit handling
- Validate comparison quality

---

## Deployment Checklist

- [ ] Add Pinecone API key to Render environment
- [ ] Add OpenAI API key to Render environment
- [ ] Run coaching data ingestion script
- [ ] Run pro swing ingestion script
- [ ] Update API documentation
- [ ] Monitor LLM API costs
- [ ] Set up error tracking for RAG failures
