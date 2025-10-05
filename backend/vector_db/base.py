"""
Vector database integration for the Space Biology Knowledge Engine.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Tuple
import logging
import asyncio
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    """Search result from vector database."""
    id: str
    score: float
    metadata: Dict[str, Any]
    content: str
    embedding: Optional[List[float]] = None


class BaseVectorDB(ABC):
    """Abstract base class for vector databases."""
    
    def __init__(self, config):
        """Initialize vector database client."""
        self.config = config
        self.logger = logger.getChild(self.__class__.__name__)
    
    @abstractmethod
    async def create_collection(self, name: str, schema: Dict[str, Any]) -> bool:
        """Create a new collection/index."""
        pass
    
    @abstractmethod
    async def delete_collection(self, name: str) -> bool:
        """Delete a collection/index."""
        pass
    
    @abstractmethod
    async def insert_documents(self, collection: str, documents: List[Dict[str, Any]]) -> bool:
        """Insert documents into collection."""
        pass
    
    @abstractmethod
    async def update_document(self, collection: str, doc_id: str, document: Dict[str, Any]) -> bool:
        """Update a document in collection."""
        pass
    
    @abstractmethod
    async def delete_document(self, collection: str, doc_id: str) -> bool:
        """Delete a document from collection."""
        pass
    
    @abstractmethod
    async def search(
        self, 
        collection: str, 
        query_vector: List[float], 
        limit: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """Search for similar documents."""
        pass
    
    @abstractmethod
    async def get_document(self, collection: str, doc_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific document by ID."""
        pass
    
    @abstractmethod
    async def list_collections(self) -> List[str]:
        """List all collections."""
        pass
    
    @abstractmethod
    async def collection_stats(self, collection: str) -> Dict[str, Any]:
        """Get collection statistics."""
        pass
    
    async def health_check(self) -> bool:
        """Check if database is healthy."""
        try:
            collections = await self.list_collections()
            return isinstance(collections, list)
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return False


class VectorDBManager:
    """Manager for vector database operations."""
    
    def __init__(self, db_client: BaseVectorDB):
        """Initialize manager."""
        self.db = db_client
        self.logger = logger.getChild("VectorDBManager")
    
    async def setup_collections(self) -> bool:
        """Set up all required collections."""
        from config import DatabaseConfig
        
        collections = [
            DatabaseConfig.PUBLICATIONS_INDEX,
            DatabaseConfig.DATASETS_INDEX, 
            DatabaseConfig.TASKBOOK_INDEX
        ]
        
        success = True
        for collection in collections:
            try:
                await self._create_collection_if_not_exists(collection)
                self.logger.info(f"Collection '{collection}' ready")
            except Exception as e:
                self.logger.error(f"Failed to setup collection '{collection}': {e}")
                success = False
        
        return success
    
    async def _create_collection_if_not_exists(self, collection_name: str):
        """Create collection if it doesn't exist."""
        existing = await self.db.list_collections()
        
        if collection_name not in existing:
            schema = self._get_collection_schema(collection_name)
            await self.db.create_collection(collection_name, schema)
    
    def _get_collection_schema(self, collection_name: str) -> Dict[str, Any]:
        """Get schema for collection."""
        # Base schema for all collections
        base_schema = {
            "properties": {
                "id": {"dataType": ["string"]},
                "title": {"dataType": ["string"]},
                "content": {"dataType": ["text"]},
                "source_type": {"dataType": ["string"]},
                "url": {"dataType": ["string"]},
                "keywords": {"dataType": ["string[]"]},
                "organisms": {"dataType": ["string[]"]},
                "tissues": {"dataType": ["string[]"]},
                "missions": {"dataType": ["string[]"]},
                "publication_date": {"dataType": ["date"]},
                "embedding": {"dataType": ["number[]"]}
            },
            "vectorizer": "none"  # We'll provide embeddings
        }
        
        # Collection-specific additions
        from config import DatabaseConfig
        
        if collection_name == DatabaseConfig.PUBLICATIONS_INDEX:
            base_schema["properties"].update({
                "authors": {"dataType": ["string[]"]},
                "journal": {"dataType": ["string"]},
                "doi": {"dataType": ["string"]},
                "citation_count": {"dataType": ["int"]}
            })
        elif collection_name == DatabaseConfig.DATASETS_INDEX:
            base_schema["properties"].update({
                "organism": {"dataType": ["string"]},
                "tissue": {"dataType": ["string"]},
                "experiment_type": {"dataType": ["string"]},
                "measurement_type": {"dataType": ["string[]"]},
                "file_count": {"dataType": ["int"]},
                "file_size": {"dataType": ["string"]}
            })
        elif collection_name == DatabaseConfig.TASKBOOK_INDEX:
            base_schema["properties"].update({
                "principal_investigator": {"dataType": ["string"]},
                "institution": {"dataType": ["string"]},
                "status": {"dataType": ["string"]},
                "funding_amount": {"dataType": ["number"]},
                "research_area": {"dataType": ["string"]}
            })
        
        return base_schema
    
    async def batch_insert(
        self, 
        collection: str, 
        documents: List[Dict[str, Any]], 
        batch_size: int = 100
    ) -> int:
        """Insert documents in batches."""
        inserted_count = 0
        
        for i in range(0, len(documents), batch_size):
            batch = documents[i:i + batch_size]
            
            try:
                success = await self.db.insert_documents(collection, batch)
                if success:
                    inserted_count += len(batch)
                    self.logger.info(f"Inserted batch {i//batch_size + 1}: {len(batch)} documents")
                else:
                    self.logger.error(f"Failed to insert batch {i//batch_size + 1}")
            except Exception as e:
                self.logger.error(f"Error inserting batch {i//batch_size + 1}: {e}")
        
        return inserted_count
    
    async def hybrid_search(
        self,
        query_vector: List[float],
        query_text: str,
        collections: List[str],
        limit: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """Perform hybrid search across multiple collections."""
        all_results = []
        
        # Search each collection
        for collection in collections:
            try:
                results = await self.db.search(
                    collection=collection,
                    query_vector=query_vector,
                    limit=limit,
                    filters=filters
                )
                
                # Add collection info to metadata
                for result in results:
                    result.metadata['collection'] = collection
                
                all_results.extend(results)
                
            except Exception as e:
                self.logger.error(f"Error searching collection {collection}: {e}")
        
        # Sort by score and limit results
        all_results.sort(key=lambda x: x.score, reverse=True)
        return all_results[:limit]
    
    async def get_collection_info(self) -> Dict[str, Dict[str, Any]]:
        """Get information about all collections."""
        collections = await self.db.list_collections()
        info = {}
        
        for collection in collections:
            try:
                stats = await self.db.collection_stats(collection)
                info[collection] = stats
            except Exception as e:
                self.logger.error(f"Error getting stats for {collection}: {e}")
                info[collection] = {"error": str(e)}
        
        return info


# Export classes
__all__ = [
    "BaseVectorDB",
    "SearchResult", 
    "VectorDBManager"
]