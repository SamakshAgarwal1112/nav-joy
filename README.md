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