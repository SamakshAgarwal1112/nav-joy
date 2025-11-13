# Loop AI – Hospital Voice Assistant

A voice-enabled AI agent that answers hospital network queries using:

- Gemini 2.5 Flash for Speech-to-Text and entity extraction
- FAISS for fast hospital retrieval
- SentenceTransformers for embeddings
- gTTS for Text-to-Speech
- FastAPI backend
- A large hospitals CSV dataset

This system converts user voice into structured JSON, performs retrieval, and responds back with synthesized speech.

## Features

### Speech-to-Text with Gemini

- Converts user audio into structured JSON
- Extracts: city, hospital, address
- Strict JSON output enforced

### Retrieval Using FAISS

- Exact match search (Working but Commented for now to use semantic search)
- Semantic search
- SentenceTransformer embeddings
- City filtering for accuracy

## Full Voice Pipeline

Audio → Gemini → JSON → Retrieval → Answer → MP3

## Installation

1. Clone the repository
```
git clone <repo-url>
cd backend
```

2. Make a virtual environment

3. Install dependencies
```
pip install -r requirements.txt
```

4. Add .env file to the root

Create a .env file:
```
GEMINI_API_KEY=your_api_key_here
NEXT_PUBLIC_API_URL=http://localhost:8000
```

5. Build FAISS Index (Important step)
```
python build_faiss_index.py
```

This generates:
- hospital_faiss.index
- hospital_metadata.pkl

These files must exist for the server to respond to queries.

6. Running the Server
```
uvicorn main:app --reload --port 8000
```

7. Go to frontend directory. Open a new terminal.
```
cd frontend
```

8. Install dependencies and run client
```
npm i
npm run dev
```
