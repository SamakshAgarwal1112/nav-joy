from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import google.generativeai as genai
# import openai
import os
import tempfile
from retrieve_hospitals import get_retriever
from config import OPENAI_API_KEY, GEMINI_API_KEY
import uvicorn
from gtts import gTTS
import os

genai.configure(api_key=GEMINI_API_KEY)

app = FastAPI(title="Loop AI - Hospital Voice Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# openai.api_key = OPENAI_API_KEY

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

def gemini_transcribe(audio_path):
    model = genai.GenerativeModel("models/gemini-2.5-flash")
    prompt = """
    You are an information extraction engine. 
    Given a user's spoken question about hospitals, extract ONLY the entities
    and output valid JSON.

    STRICT RULES:
    - Output ONLY RAW JSON.
    - DO NOT wrap JSON in ``` or ```json or any code block.
    - DO NOT add commentary.
    - DO NOT answer the question.
    - DO NOT include markdown.
    - The FIRST character of your response MUST be '['.
    - If city/hospital/address not mentioned → use null.
    - If city is Bangalore, convert it to bengaluru.

    Return JSON EXACTLY like this:
    [
    {
        "city": string or null,
        "hospital": string or null,
        "address": string or null
    }
    ]
    """

    with open(audio_path, "rb") as f:
        audio_bytes = f.read()

    response = model.generate_content(
        [
            prompt,
            {
                "mime_type": "audio/wav",
                "data": audio_bytes,
            }
        ]
    )
    return response.text.strip()

def sanitize_header(text: str) -> str:
    return text.replace("\n", " ").replace("\r", " ").replace("*", "")


def gemini_tts(text, output_path):
    if not output_path.endswith(".mp3"):
        output_path = output_path + ".mp3"

    tts = gTTS(text=text, lang="en", slow=False)
    tts.save(output_path)

@app.post("/voice")
async def process_voice(audio: UploadFile = File(...)):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
            content = await audio.read()
            temp_audio.write(content)
            temp_audio_path = temp_audio.name

        print("Temp Audio Path", temp_audio_path)

        user_query = gemini_transcribe(temp_audio_path)
        # with open(temp_audio_path, "rb") as audio_file:
        #     transcript = openai.audio.transcriptions.create(
        #         model="whisper-1",
        #         file=audio_file,
        #         language="en"
        #     )
        
        # user_query = transcript.text
        print(f"User Query: {user_query}")

        retriever = get_retriever()
        results = retriever.query(user_query)
        response_text = retriever.format_response(user_query, results)

        print(f"Response: {response_text}")

        # tts_response = openai.audio.speech.create(
        #     model="tts-1",
        #     voice="alloy",
        #     input=response_text
        # )
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_tts:
            # temp_tts.write(tts_response.content)
            gemini_tts(response_text, temp_tts.name)
            tts_path = temp_tts.name

        os.unlink(temp_audio_path)

        return FileResponse(
            tts_path,
            media_type="audio/mpeg",
            headers={
                "X-Transcribed-Text": sanitize_header(user_query),
                "X-Response-Text": sanitize_header(response_text),
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