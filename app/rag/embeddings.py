import os
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from typing import List, Tuple
import requests

class GoogleEmbeddings:
    """
    Custom embedding class for Google Gemini.
    Switches between multiple API keys if one fails.
    """
    def __init__(self, api_keys: List[str], model: str = "gemini-embedding-1"):
        self.api_keys = api_keys
        self.current_key_index = 0
        self.model = model
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models/{}:embedContent"
        
    def _get_current_key(self) -> str:
        return self.api_keys[self.current_key_index]
    
    def _get_next_key(self) -> str:
        self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
        return self._get_current_key()
    
    def embed_documents(self, texts: List[str]) -> Tuple[List[List[float]], List[dict]]:
        """
        Embeds multiple documents.
        Returns (embeddings, info)
        """
        num_texts = len(texts)
        embeddings = []
        info = {"model": self.model, "num_texts": num_texts, "total_tokens": 0}
        
        # Gemini returns 10024 tokens for 1000 1024-char texts
        # Let's chunk if necessary, but usually we can send many at once
        
        for attempt in range(2 * len(self.api_keys)): # Max 2 attempts per key
            api_key = self._get_current_key()
            url = self.base_url.format(self.model)
            
            try:
                payload = {
                    "contents": texts,
                    "taskType": "SEMANTIC_SIMILARITY",
                    "config": {
                        "outputDimensionality": 768 # Common for search
                    }
                }
                
                params = {"key": api_key}
                
                response = requests.post(url, json=payload, params=params, timeout=30)
                
                if response.status_code == 200:
                    result = response.json()
                    
                    if "embeddings" in result:
                        for embed_obj in result["embeddings"]:
                            if "values" in embed_obj:
                                embeddings.append(embed_obj["values"])
                                
                    if "usageMetadata" in result:
                        info["total_tokens"] += result["usageMetadata"].get("totalTokenCount", 0)
                        
                    # Check if we got all embeddings
                    if len(embeddings) == num_texts:
                        return embeddings, info
                
                elif response.status_code == 429: # Rate limit or Quota exceeded
                    self._get_next_key()
                    continue
                
                else:
                    # Other errors, try next key
                    self._get_next_key()
                    continue
                    
            except Exception as e:
                # Network error or timeout
                self._get_next_key()
                continue
        
        # If we fall through, return what we have or raise error
        # For now, let's return partial or empty
        return embeddings, info

    def embed_query(self, text: str) -> List[float]:
        """
        Embeds a single query.
        """
        embeddings, info = self.embed_documents([text])
        if embeddings:
            return embeddings[0]
        return []

def get_embedding_function():
    api_keys = [
        os.getenv("GOOGLE_API_KEY"),
        os.getenv("GOOGLE_API_KEY_2"),
        os.getenv("GOOGLE_API_KEY_3"),
        os.getenv("GOOGLE_API_KEY_4")
    ]
    
    # Filter out None or empty keys
    valid_keys = [k for k in api_keys if k and k.strip()]
    
    if not valid_keys:
        raise ValueError("No valid Google API keys found. Please set GOOGLE_API_KEY or related env vars.")
    
    return GoogleEmbeddings(valid_keys)