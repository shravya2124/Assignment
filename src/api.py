from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from src.rag import RecommendationEngine
import uvicorn
import os
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="SHL Assessment Recommendation API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize engine
try:
    engine = RecommendationEngine()
except Exception as e:
    print(f"Error initializing engine: {e}")
    engine = None

class QueryRequest(BaseModel):
    query: str

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/recommend")
def recommend(request: QueryRequest):
    if not engine:
        raise HTTPException(status_code=500, detail="Recommendation engine not initialized")
    
    try:
        results = engine.recommend(request.query)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from fastapi.responses import FileResponse

@app.get("/")
async def read_index():
    return FileResponse('frontend/index.html')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8085))
    uvicorn.run(app, host="0.0.0.0", port=port)

