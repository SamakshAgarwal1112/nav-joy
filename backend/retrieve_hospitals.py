import faiss
import pickle
import json
from sentence_transformers import SentenceTransformer
from config import FAISS_INDEX_PATH, METADATA_PATH, EMBEDDING_MODEL, TOP_K_RESULTS

class HospitalRetriever:
    def __init__(self):
        self.index = faiss.read_index(FAISS_INDEX_PATH)
        
        print("Loading metadata...")
        with open(METADATA_PATH, 'rb') as f:
            self.metadata = pickle.load(f)
        
        print("Loading embedding model...")
        self.model = SentenceTransformer(EMBEDDING_MODEL)
        
        print(f"Retriever ready with {len(self.metadata)} hospitals")

    def extract_entities(self, query):

        try:
            data = json.loads(query)
        except Exception as e:
            print("JSON extraction failed:", e)
            return {"city": None, "hospital_name": None}

        if not isinstance(data, list) or len(data) == 0:
            return {"city": None, "hospital_name": None}

        obj = data[0]

        city = obj.get("city")
        hospital = obj.get("hospital")
        # address = obj.get("address")

        return {
            "city": city if city else None,
            "hospital_name": hospital if hospital else None
        }
    
    def exact_match(self, hospital_name, city = None):
        results = []
        
        for meta in self.metadata:
            if city is not None:
                city_match = str(city).lower() in str(meta['city']).lower()
                if city_match:
                    name_match = not hospital_name or str(hospital_name).lower() in str(meta['hospital_name']).lower()
                    if city_match and name_match:
                        results.append(meta)
            else:
                name_match = hospital_name and str(hospital_name).lower() in str(meta['hospital_name']).lower()
                if name_match:
                    results.append(meta)
        
        return results
    
    def semantic_search(self, query, top_k = TOP_K_RESULTS, city_filter = None):
        query_embedding = self.model.encode([query], convert_to_numpy=True)
        faiss.normalize_L2(query_embedding)
        
        distances, indices = self.index.search(query_embedding.astype('float32'), top_k * 3)
        
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx < len(self.metadata):
                meta = self.metadata[idx]
                
                if city_filter and city_filter not in meta['city']:
                    continue
                
                meta_with_score = meta.copy()
                meta_with_score['score'] = float(dist)
                results.append(meta_with_score)
                
                if len(results) >= top_k:
                    break
        
        return results
    
    def query(self, user_query):
        
        entities = self.extract_entities(user_query)
        print(f"Entities: {entities}")
        hospital_name = entities.get("hospital_name")
        city = entities.get("city")
        
        if hospital_name or city:
            exact_results = self.exact_match(hospital_name, city)
            if exact_results:
                print(f"Found {len(exact_results)} exact matches")
                return exact_results[:TOP_K_RESULTS]
            
        search_query = hospital_name or city or user_query
        
        semantic_results = self.semantic_search(
            search_query, 
            top_k=TOP_K_RESULTS,
            city_filter=city
        )
        
        return semantic_results
    
    def format_response(self, query, results):
        """Format results into natural language response"""
        if not results:
            return "I couldn't find any hospitals matching your query. Could you please provide more details or specify a city?"
        
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['confirm', 'check', 'verify', 'is', 'network']):
            hospital = results[0]
            return f"Yes, {hospital['hospital_name'].title()} in {hospital['city'].title()} is part of your network. It's located at {hospital['address']}."
        
        if len(results) == 1:
            hospital = results[0]
            return f"I found {hospital['hospital_name'].title()} in {hospital['city'].title()}, located at {hospital['address']}."
        
        city_name = results[0]['city'].title() if results[0]['city'] else "your area"
        response = f"Here are {len(results)} hospitals around {city_name}:\n\n"
        
        for i, hospital in enumerate(results, 1):
            response += f"{i}. {hospital['hospital_name'].title()}, located at {hospital['address']}, {hospital['city'].title()}.\n"
        
        return response.strip()

retriever = None

def get_retriever():
    global retriever
    if retriever is None:
        retriever = HospitalRetriever()
    return retriever