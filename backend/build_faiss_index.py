import pandas as pd
import faiss
import pickle
from sentence_transformers import SentenceTransformer
from config import CSV_PATH, FAISS_INDEX_PATH, METADATA_PATH, EMBEDDING_MODEL

def preprocess_text(text):
    if pd.isna(text):
        return ""
    return str(text).strip().lower()

def create_hospital_chunk(row):
    parts = []
    
    if row.get('HOSPITAL NAME'):
        parts.append(row['HOSPITAL NAME'])
    
    if row.get('Address'):
        parts.append(f"located at {row['Address']}")
    
    if row.get('CITY'):
        parts.append(row['CITY'])
    
    return ", ".join(parts) + "."

def build_faiss_index():
    df = pd.read_csv(CSV_PATH)
    
    df.columns = df.columns.str.strip()
    
    print(f"Loaded {len(df)} hospital records")
    
    text_columns = ['HOSPITAL NAME', 'Address', 'CITY']
    for col in text_columns:
        if col in df.columns:
            df[col] = df[col].apply(preprocess_text)
    
    chunks = []
    metadata = []
    
    for idx, row in df.iterrows():
        chunk_text = create_hospital_chunk(row)
        chunks.append(chunk_text)
        
        meta = {
            'id': idx,
            'hospital_name': row.get('HOSPITAL NAME', ''),
            'address': row.get('Address', ''),
            'city': row.get('CITY', ''),
            'chunk_text': chunk_text
        }
        metadata.append(meta)
    
    print(f"Loading embedding model: {EMBEDDING_MODEL}")
    model = SentenceTransformer(EMBEDDING_MODEL)
    
    embeddings = model.encode(chunks, show_progress_bar=True, convert_to_numpy=True)
    
    dimension = embeddings.shape[1]
    
    index = faiss.IndexFlatL2(dimension)
    
    faiss.normalize_L2(embeddings)
    
    index.add(embeddings.astype('float32'))
    
    print(f"Saving FAISS index to {FAISS_INDEX_PATH}")
    faiss.write_index(index, FAISS_INDEX_PATH)
    
    with open(METADATA_PATH, 'wb') as f:
        pickle.dump(metadata, f)
    
    print(f"Index built successfully!")
    print(f"  - Total records: {len(metadata)}")
    print(f"  - Embedding dimension: {dimension}")

if __name__ == "__main__":
    build_faiss_index()