"""
Base data ingestion interface for the Space Biology Knowledge Engine.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, AsyncGenerator
import logging
from models.schemas import Publication, Dataset, TaskBookProject

logger = logging.getLogger(__name__)


class BaseIngester(ABC):
    """Abstract base class for data ingesters."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the ingester with configuration."""
        self.config = config
        self.logger = logger.getChild(self.__class__.__name__)
    
    @abstractmethod
    async def ingest(self) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Ingest data from the source.
        
        Yields:
            Dict[str, Any]: Raw data records
        """
        pass
    
    @abstractmethod
    async def validate_record(self, record: Dict[str, Any]) -> bool:
        """
        Validate a data record.
        
        Args:
            record: Raw data record
            
        Returns:
            bool: True if record is valid
        """
        pass
    
    @abstractmethod
    async def transform_record(self, record: Dict[str, Any]) -> Any:
        """
        Transform raw record to standardized model.
        
        Args:
            record: Raw data record
            
        Returns:
            Publication | Dataset | TaskBookProject: Transformed record
        """
        pass
    
    async def process_batch(self, records: List[Dict[str, Any]]) -> List[Any]:
        """
        Process a batch of records.
        
        Args:
            records: List of raw data records
            
        Returns:
            List[Any]: List of transformed records
        """
        processed = []
        
        for record in records:
            try:
                if await self.validate_record(record):
                    transformed = await self.transform_record(record)
                    processed.append(transformed)
                else:
                    self.logger.warning(f"Invalid record skipped: {record.get('id', 'unknown')}")
            except Exception as e:
                self.logger.error(f"Error processing record {record.get('id', 'unknown')}: {e}")
                continue
        
        return processed
    
    async def run_ingestion(self, batch_size: int = 100) -> AsyncGenerator[List[Any], None]:
        """
        Run the complete ingestion process.
        
        Args:
            batch_size: Number of records to process in each batch
            
        Yields:
            List[Any]: Batches of processed records
        """
        batch = []
        
        async for record in self.ingest():
            batch.append(record)
            
            if len(batch) >= batch_size:
                processed_batch = await self.process_batch(batch)
                if processed_batch:
                    yield processed_batch
                batch = []
        
        # Process remaining records
        if batch:
            processed_batch = await self.process_batch(batch)
            if processed_batch:
                yield processed_batch
    
    def get_stats(self) -> Dict[str, int]:
        """Get ingestion statistics."""
        return {
            "total_processed": getattr(self, '_total_processed', 0),
            "total_errors": getattr(self, '_total_errors', 0),
            "total_skipped": getattr(self, '_total_skipped', 0)
        }