"""
Pinecone vector database implementation for free tier usage.
"""
import asyncio
from typing import List, Dict, Any, Optional
import logging
import time

try:
    from pinecone import Pinecone, PodSpec
    PINECONE_AVAILABLE = True
except ImportError:
    Pinecone = None
    PodSpec = None
    PINECONE_AVAILABLE = False

from .base import BaseVectorDB, SearchResult

logger = logging.getLogger(__name__)


class PineconeDB(BaseVectorDB):
    """Pinecone vector database implementation for free tier."""
    
    def __init__(self, config):
        """Initialize Pinecone client."""
        super().__init__(config)
        
        if not PINECONE_AVAILABLE:
            raise ImportError("Pinecone client not available. Install with: pip install pinecone")
        
        # Handle both dict and Settings object
        if hasattr(config, 'pinecone_api_key'):
            # Settings object
            self.api_key = config.pinecone_api_key
            self.environment = config.pinecone_environment
            self.index_name = config.pinecone_index_name
            self.dimension = 768  # Default for Gemini embeddings
        else:
            # Dictionary
            self.api_key = config.get('api_key')
            self.environment = config.get('environment', 'gcp-starter')
            self.index_name = config.get('index_name', 'space-biology-index')
            self.dimension = config.get('dimension', 768)  # Default for Gemini embeddings
        
        if not self.api_key:
            raise ValueError("Pinecone API key is required")
        
        self.pc = None
        self.index = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Pinecone client."""
        try:
            # Initialize Pinecone
            self.pc = Pinecone(api_key=self.api_key)
            
            # Create index if it doesn't exist
            existing_indexes = [index.name for index in self.pc.list_indexes()]
            
            if self.index_name not in existing_indexes:
                self.logger.info(f"Creating Pinecone index: {self.index_name}")
                self.pc.create_index(
                    name=self.index_name,
                    dimension=self.dimension,
                    metric='cosine',
                    spec=PodSpec(
                        environment=self.environment,
                        pod_type='starter',  # Free tier
                        pods=1
                    )
                )
                # Wait for index to be ready
                time.sleep(60)  # Index creation takes time
            
            # Connect to index
            self.index = self.pc.Index(self.index_name)
            self.logger.info(f"Connected to Pinecone index: {self.index_name}")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Pinecone: {e}")
            raise
    
    async def create_collection(self, name: str, schema: Dict[str, Any]) -> bool:
        """Create a namespace in Pinecone (collections are namespaces)."""
        try:
            # In Pinecone, we use namespaces instead of separate collections
            # The namespace will be created automatically when we insert data
            self.logger.info(f"Namespace '{name}' will be created on first insert")
            return True
        except Exception as e:
            self.logger.error(f"Error creating namespace '{name}': {e}")
            return False
    
    async def delete_collection(self, name: str) -> bool:
        """Delete a namespace in Pinecone."""
        try:
            # Delete all vectors in the namespace
            self.index.delete(delete_all=True, namespace=name)
            self.logger.info(f"Deleted namespace '{name}'")
            return True
        except Exception as e:
            self.logger.error(f"Error deleting namespace '{name}': {e}")
            return False
    
    async def insert_documents(self, collection: str, documents: List[Dict[str, Any]]) -> bool:
        """Insert documents into Pinecone namespace."""
        try:
            vectors = []
            
            for doc in documents:
                if 'embedding' not in doc or not doc['embedding']:
                    self.logger.warning(f"Document {doc.get('id', 'unknown')} has no embedding")
                    continue
                
                # Prepare metadata (Pinecone has metadata size limits)
                metadata = self._prepare_metadata(doc)
                
                vectors.append({
                    'id': str(doc['id']),
                    'values': doc['embedding'],
                    'metadata': metadata
                })
            
            if vectors:
                # Batch insert with rate limiting for free tier
                batch_size = 100  # Free tier limit
                for i in range(0, len(vectors), batch_size):
                    batch = vectors[i:i + batch_size]
                    self.index.upsert(vectors=batch, namespace=collection)
                    
                    # Rate limiting for free tier (max 5 requests/second)
                    if i + batch_size < len(vectors):
                        await asyncio.sleep(0.2)
                
                self.logger.info(f"Inserted {len(vectors)} documents into namespace '{collection}'")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error inserting documents into '{collection}': {e}")
            return False
    
    async def update_document(self, collection: str, doc_id: str, document: Dict[str, Any]) -> bool:
        """Update a document in Pinecone namespace."""
        try:
            if 'embedding' not in document or not document['embedding']:
                self.logger.warning(f"Document {doc_id} has no embedding for update")
                return False
            
            metadata = self._prepare_metadata(document)
            
            self.index.upsert(
                vectors=[{
                    'id': str(doc_id),
                    'values': document['embedding'],
                    'metadata': metadata
                }],
                namespace=collection
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating document '{doc_id}': {e}")
            return False
    
    async def delete_document(self, collection: str, doc_id: str) -> bool:
        """Delete a document from Pinecone namespace."""
        try:
            self.index.delete(ids=[str(doc_id)], namespace=collection)
            return True
        except Exception as e:
            self.logger.error(f"Error deleting document '{doc_id}': {e}")
            return False
    
    async def search(
        self,
        collection: str,
        query_vector: List[float],
        limit: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """Search for similar documents in Pinecone."""
        try:
            # Prepare filter for Pinecone
            pinecone_filter = self._build_pinecone_filter(filters) if filters else None
            
            # Perform search
            results = self.index.query(
                vector=query_vector,
                top_k=min(limit, 10000),  # Pinecone limit
                namespace=collection,
                filter=pinecone_filter,
                include_metadata=True,
                include_values=False
            )
            
            # Convert to SearchResult objects
            search_results = []
            for match in results.matches:
                search_results.append(SearchResult(
                    id=match.id,
                    score=float(match.score),
                    content=match.metadata.get('content', ''),
                    metadata=match.metadata
                ))
            
            return search_results
            
        except Exception as e:
            self.logger.error(f"Error searching namespace '{collection}': {e}")
            return []
    
    async def get_document(self, collection: str, doc_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific document by ID."""
        try:
            result = self.index.fetch(ids=[str(doc_id)], namespace=collection)
            
            if str(doc_id) in result.vectors:
                vector_data = result.vectors[str(doc_id)]
                return vector_data.metadata
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting document '{doc_id}': {e}")
            return None
    
    async def list_collections(self) -> List[str]:
        """List all namespaces (collections) in Pinecone."""
        try:
            # Get index stats to see namespaces
            stats = self.index.describe_index_stats()
            namespaces = list(stats.namespaces.keys()) if stats.namespaces else []
            return namespaces
        except Exception as e:
            self.logger.error(f"Error listing namespaces: {e}")
            return []
    
    async def collection_stats(self, collection: str) -> Dict[str, Any]:
        """Get namespace statistics."""
        try:
            stats = self.index.describe_index_stats()
            
            if collection in stats.namespaces:
                ns_stats = stats.namespaces[collection]
                return {
                    'name': collection,
                    'document_count': ns_stats.vector_count,
                    'status': 'active'
                }
            else:
                return {
                    'name': collection,
                    'document_count': 0,
                    'status': 'empty'
                }
                
        except Exception as e:
            self.logger.error(f"Error getting stats for '{collection}': {e}")
            return {'name': collection, 'error': str(e)}
    
    def _prepare_metadata(self, doc: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare metadata for Pinecone (with size limits)."""
        metadata = {}
        
        # Pinecone metadata limits: 40KB total, scalar values only
        allowed_fields = [
            'id', 'title', 'content', 'source_type', 'url', 'journal',
            'organism', 'tissue', 'mission', 'experiment_type', 'publication_date'
        ]
        
        for field in allowed_fields:
            if field in doc and doc[field] is not None:
                value = doc[field]
                
                # Convert to string and truncate if needed
                if isinstance(value, (list, tuple)):
                    value = ', '.join(str(v) for v in value[:5])  # Limit array size
                else:
                    value = str(value)
                
                # Truncate long strings
                if len(value) > 1000:
                    value = value[:1000] + "..."
                
                metadata[field] = value
        
        return metadata
    
    def _build_pinecone_filter(self, filters: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Build Pinecone-compatible filter."""
        if not filters:
            return None
        
        pinecone_filter = {}
        
        for key, value in filters.items():
            if isinstance(value, list):
                if len(value) == 1:
                    pinecone_filter[key] = {"$eq": str(value[0])}
                else:
                    pinecone_filter[key] = {"$in": [str(v) for v in value]}
            else:
                pinecone_filter[key] = {"$eq": str(value)}
        
        return pinecone_filter


# Export class
__all__ = ["PineconeDB"]