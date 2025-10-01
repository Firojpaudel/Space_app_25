"""
Embedding generation utilities using FREE APIs (Gemini).
"""
import asyncio
from typing import List, Optional, Dict, Any
import logging
import numpy as np

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    genai = None
    GEMINI_AVAILABLE = False

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SentenceTransformer = None
    SENTENCE_TRANSFORMERS_AVAILABLE = False

from config.settings import Settings, ModelConfig

logger = logging.getLogger(__name__)


class EmbeddingGenerator:
    """Generate embeddings for text using FREE APIs (Gemini)."""
    
    def __init__(self, settings: Settings, model_type: str = "gemini"):
        """Initialize embedding generator."""
        self.settings = settings
        self.model_type = model_type.lower()
        self.logger = logger.getChild("EmbeddingGenerator")
        self.model = None
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize the embedding model."""
        if self.model_type == "gemini":
            if not GEMINI_AVAILABLE:
                raise ImportError("Google GenerativeAI package not available. Install with: pip install google-generativeai")
            
            if not self.settings.gemini_api_key:
                raise ValueError("Gemini API key not provided")
            
            genai.configure(api_key=self.settings.gemini_api_key)
            self.logger.info(f"Initialized Gemini embeddings with model: {self.settings.embedding_model}")
            
        elif self.model_type == "sentence_transformers":
            if not SENTENCE_TRANSFORMERS_AVAILABLE:
                raise ImportError("SentenceTransformers not available. Install with: pip install sentence-transformers")
            
            model_name = ModelConfig.HUGGINGFACE_EMBEDDING_MODEL
            self.model = SentenceTransformer(model_name)
            self.logger.info(f"Initialized SentenceTransformers with model: {model_name}")
            
        else:
            raise ValueError(f"Unsupported model type: {self.model_type}")
    
    async def generate_embedding(self, text: str) -> Optional[List[float]]:
        """
        Generate embedding for a single text.
        
        Args:
            text: Input text
            
        Returns:
            Optional[List[float]]: Embedding vector
        """
        if not text or not text.strip():
            return None
        
        try:
            if self.model_type == "gemini":
                return await self._generate_gemini_embedding(text)
            elif self.model_type == "sentence_transformers":
                return await self._generate_sentence_transformer_embedding(text)
            else:
                raise ValueError(f"Unsupported model type: {self.model_type}")
                
        except Exception as e:
            self.logger.error(f"Error generating embedding: {e}")
            return None
    
    async def generate_batch_embeddings(
        self, 
        texts: List[str], 
        batch_size: int = 100
    ) -> List[Optional[List[float]]]:
        """
        Generate embeddings for multiple texts in batches.
        
        Args:
            texts: List of input texts
            batch_size: Batch size for processing
            
        Returns:
            List[Optional[List[float]]]: List of embedding vectors
        """
        embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            
            if self.model_type == "gemini":
                batch_embeddings = await self._generate_gemini_batch_embeddings(batch)
            elif self.model_type == "sentence_transformers":
                batch_embeddings = await self._generate_sentence_transformer_batch_embeddings(batch)
            else:
                batch_embeddings = [None] * len(batch)
            
            embeddings.extend(batch_embeddings)
            
            # Add delay to respect rate limits for Gemini free tier
            if self.model_type == "gemini":
                await asyncio.sleep(4.0)  # 15 requests/minute = 4 seconds between requests
        
        return embeddings
    
    async def _generate_gemini_embedding(self, text: str) -> Optional[List[float]]:
        """Generate embedding using Gemini API (FREE)."""
        try:
            # Clean text
            cleaned_text = text.replace("\n", " ").strip()
            if not cleaned_text:
                return None
            
            # Use Gemini embedding model
            result = genai.embed_content(
                model=self.settings.embedding_model,
                content=cleaned_text,
                task_type="retrieval_document"
            )
            
            return result['embedding']
            
        except Exception as e:
            self.logger.error(f"Gemini embedding error: {e}")
            return None
    
    async def _generate_gemini_batch_embeddings(self, texts: List[str]) -> List[Optional[List[float]]]:
        """Generate batch embeddings using Gemini API with rate limiting."""
        embeddings = []
        
        for text in texts:
            try:
                embedding = await self._generate_gemini_embedding(text)
                embeddings.append(embedding)
                
                # Rate limiting for free tier (15 requests/minute)
                await asyncio.sleep(4.0)
                
            except Exception as e:
                self.logger.error(f"Gemini batch embedding error for text: {e}")
                embeddings.append(None)
        
        return embeddings
    
    async def _generate_sentence_transformer_embedding(self, text: str) -> Optional[List[float]]:
        """Generate embedding using SentenceTransformers."""
        try:
            # Run in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            embedding = await loop.run_in_executor(
                None, 
                self.model.encode, 
                text
            )
            
            return embedding.tolist()
            
        except Exception as e:
            self.logger.error(f"SentenceTransformer embedding error: {e}")
            return None
    
    async def _generate_sentence_transformer_batch_embeddings(self, texts: List[str]) -> List[Optional[List[float]]]:
        """Generate batch embeddings using SentenceTransformers."""
        try:
            # Run in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            embeddings = await loop.run_in_executor(
                None,
                self.model.encode,
                texts
            )
            
            return [emb.tolist() for emb in embeddings]
            
        except Exception as e:
            self.logger.error(f"SentenceTransformer batch embedding error: {e}")
            return [None] * len(texts)
    
    def get_embedding_dimension(self) -> int:
        """Get the dimension of embeddings produced by this model."""
        if self.model_type == "gemini":
            if "text-embedding-004" in self.settings.embedding_model:
                return 768  # Gemini text-embedding-004 dimension
            else:
                return 768  # Default for Gemini
        elif self.model_type == "sentence_transformers":
            if self.model:
                return self.model.get_sentence_embedding_dimension()
            return 384  # Default for all-MiniLM-L6-v2
        else:
            return 768  # Default


class EmbeddingCache:
    """Cache for embeddings to avoid regenerating."""
    
    def __init__(self, max_size: int = 10000):
        """Initialize cache."""
        self.cache: Dict[str, List[float]] = {}
        self.max_size = max_size
        self.access_count: Dict[str, int] = {}
    
    def get(self, text_hash: str) -> Optional[List[float]]:
        """Get embedding from cache."""
        if text_hash in self.cache:
            self.access_count[text_hash] = self.access_count.get(text_hash, 0) + 1
            return self.cache[text_hash]
        return None
    
    def put(self, text_hash: str, embedding: List[float]):
        """Put embedding in cache."""
        if len(self.cache) >= self.max_size:
            self._evict_least_used()
        
        self.cache[text_hash] = embedding
        self.access_count[text_hash] = 1
    
    def _evict_least_used(self):
        """Evict least used item from cache."""
        if not self.access_count:
            return
        
        least_used = min(self.access_count.items(), key=lambda x: x[1])
        text_hash = least_used[0]
        
        del self.cache[text_hash]
        del self.access_count[text_hash]


def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """Calculate cosine similarity between two vectors."""
    if not vec1 or not vec2:
        return 0.0
    
    try:
        v1 = np.array(vec1)
        v2 = np.array(vec2)
        
        dot_product = np.dot(v1, v2)
        norm1 = np.linalg.norm(v1)
        norm2 = np.linalg.norm(v2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return float(dot_product / (norm1 * norm2))
        
    except Exception:
        return 0.0


def euclidean_distance(vec1: List[float], vec2: List[float]) -> float:
    """Calculate Euclidean distance between two vectors."""
    if not vec1 or not vec2:
        return float('inf')
    
    try:
        v1 = np.array(vec1)
        v2 = np.array(vec2)
        
        return float(np.linalg.norm(v1 - v2))
        
    except Exception:
        return float('inf')


# Export classes and functions
__all__ = [
    "EmbeddingGenerator",
    "EmbeddingCache",
    "cosine_similarity",
    "euclidean_distance"
]