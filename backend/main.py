from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import openai
import os
import tempfile
from retrieve_hospitals import get_retriever
from config import OPENAI_API_KEY
import uvicorn

app = FastAPI(title="Loop AI - Hospital Voice Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

openai.api_key = OPENAI_API_KEY

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    query: str
    response_text: str
    hospitals_found: int

@app.on_event("startup")
async def startup_event():
    print("Initializing Hospital Retriever...")
    get_retriever()
    print("Server ready!")

@app.get("/")
async def root():
    return {"message": "Loop AI Hospital Voice Agent API", "status": "running"}

@app.post("/voice")
async def process_voice(audio: UploadFile = File(...)):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
            content = await audio.read()
            temp_audio.write(content)
            temp_audio_path = temp_audio.name
        
        with open(temp_audio_path, "rb") as audio_file:
            transcript = openai.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language="en"
            )
        
        user_query = transcript.text
        print(f"Transcribed: {user_query}")
        
        retriever = get_retriever()
        results = retriever.query(user_query)
        response_text = retriever.format_response(user_query, results)
        
        print(f"Response: {response_text}")
        
        tts_response = openai.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=response_text
        )
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_tts:
            temp_tts.write(tts_response.content)
            tts_path = temp_tts.name
        
        os.unlink(temp_audio_path)
        
        return FileResponse(
            tts_path,
            media_type="audio/mpeg",
            headers={
                "X-Transcribed-Text": user_query,
                "X-Response-Text": response_text,
                "X-Hospitals-Found": str(len(results))
            }
        )
    
    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    try:
        retriever = get_retriever()
        return {
            "status": "healthy",
            "hospitals_indexed": len(retriever.metadata)
        }
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)