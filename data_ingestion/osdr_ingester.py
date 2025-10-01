"""
NASA OSDR (Open Science Data Repository) data ingestion.
"""
import aiohttp
import asyncio
from datetime import datetime
from typing import List, Dict, Any, AsyncGenerator, Optional
import json
from urllib.parse import urljoin, urlencode

from .base import BaseIngester
from models.schemas import Dataset, GravityCondition
from utils.text_processing import clean_text
from utils.entity_extraction import extract_biological_entities
from config import settings


class OSDRIngester(BaseIngester):
    """Ingester for NASA OSDR datasets."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize OSDR ingester."""
        super().__init__(config)
        self.base_url = config.get('base_url', settings.osdr_base_url)
        self.api_key = config.get('api_key', settings.nasa_api_key)
        self.max_concurrent = config.get('max_concurrent', 10)
        self.request_delay = config.get('request_delay', 1.0)  # seconds
        
        # Initialize session with headers
        self.headers = {
            'User-Agent': 'Space-Biology-Knowledge-Engine/1.0',
            'Accept': 'application/json'
        }
        if self.api_key:
            self.headers['X-API-Key'] = self.api_key
    
    async def ingest(self) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Ingest datasets from NASA OSDR.
        
        Yields:
            Dict[str, Any]: Raw dataset records
        """
        self.logger.info("Starting OSDR dataset ingestion")
        
        async with aiohttp.ClientSession(headers=self.headers) as session:
            # Get list of all datasets
            datasets = await self._fetch_dataset_list(session)
            
            # Process datasets in batches to avoid overwhelming the API
            semaphore = asyncio.Semaphore(self.max_concurrent)
            
            for dataset_info in datasets:
                dataset_id = dataset_info.get('id') or dataset_info.get('dataset_id')
                if dataset_id:
                    async with semaphore:
                        try:
                            dataset_details = await self._fetch_dataset_details(session, dataset_id)
                            if dataset_details:
                                yield dataset_details
                            
                            # Add delay between requests
                            await asyncio.sleep(self.request_delay)
                            
                        except Exception as e:
                            self.logger.error(f"Error fetching dataset {dataset_id}: {e}")
                            continue
    
    async def _fetch_dataset_list(self, session: aiohttp.ClientSession) -> List[Dict[str, Any]]:
        """
        Fetch list of all available datasets.
        
        Args:
            session: HTTP session
            
        Returns:
            List[Dict[str, Any]]: List of dataset info
        """
        datasets = []
        page = 1
        page_size = 100
        
        while True:
            try:
                # Construct search URL
                params = {
                    'page': page,
                    'size': page_size,
                    'type': 'study'  # Focus on biological studies
                }
                
                url = f"{self.base_url}/data/search?" + urlencode(params)
                
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Extract datasets from response
                        page_datasets = data.get('results', []) or data.get('data', [])
                        if not page_datasets:
                            break
                        
                        datasets.extend(page_datasets)
                        
                        # Check if there are more pages
                        total = data.get('total', 0)
                        if len(datasets) >= total or len(page_datasets) < page_size:
                            break
                        
                        page += 1
                        
                    else:
                        self.logger.warning(f"HTTP {response.status} for dataset list page {page}")
                        break
                        
            except Exception as e:
                self.logger.error(f"Error fetching dataset list page {page}: {e}")
                break
        
        self.logger.info(f"Found {len(datasets)} datasets in OSDR")
        return datasets
    
    async def _fetch_dataset_details(self, session: aiohttp.ClientSession, dataset_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetch detailed information for a specific dataset.
        
        Args:
            session: HTTP session
            dataset_id: Dataset identifier
            
        Returns:
            Optional[Dict[str, Any]]: Dataset details
        """
        try:
            url = f"{self.base_url}/data/{dataset_id}"
            
            async with session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    self.logger.warning(f"HTTP {response.status} for dataset {dataset_id}")
                    return None
                    
        except Exception as e:
            self.logger.error(f"Error fetching dataset {dataset_id}: {e}")
            return None
    
    async def validate_record(self, record: Dict[str, Any]) -> bool:
        """
        Validate a dataset record.
        
        Args:
            record: Raw dataset record
            
        Returns:
            bool: True if record is valid
        """
        # Check required fields
        if not record.get('title') and not record.get('name'):
            return False
        
        # Must have some form of identifier
        if not any([record.get('id'), record.get('dataset_id'), record.get('accession')]):
            return False
        
        return True
    
    async def transform_record(self, record: Dict[str, Any]) -> Dataset:
        """
        Transform raw OSDR record to Dataset model.
        
        Args:
            record: Raw OSDR record
            
        Returns:
            Dataset: Transformed dataset
        """
        # Extract basic information
        title = clean_text(record.get('title') or record.get('name', ''))
        description = clean_text(record.get('description') or record.get('summary', ''))
        
        # Create dataset ID
        dataset_id = (record.get('id') or 
                     record.get('dataset_id') or 
                     record.get('accession') or 
                     f"osdr_{hash(title)}")
        
        # Extract biological information
        text_for_entities = f"{title} {description}"
        entities = await extract_biological_entities(text_for_entities)
        
        # Parse dates
        pub_date = None
        update_date = None
        
        if record.get('publication_date'):
            try:
                pub_date = datetime.fromisoformat(str(record.get('publication_date')).replace('Z', '+00:00'))
            except:
                pass
        
        if record.get('last_updated') or record.get('modified_date'):
            try:
                date_str = record.get('last_updated') or record.get('modified_date')
                update_date = datetime.fromisoformat(str(date_str).replace('Z', '+00:00'))
            except:
                pass
        
        # Extract measurement and data types
        measurement_types = []
        data_types = []
        file_formats = []
        
        # Look for assay information
        if record.get('assays'):
            for assay in record.get('assays', []):
                if assay.get('measurement_type'):
                    measurement_types.append(assay['measurement_type'])
                if assay.get('technology_type'):
                    data_types.append(assay['technology_type'])
        
        # Look for file information
        if record.get('files'):
            files = record.get('files', [])
            file_count = len(files) if isinstance(files, list) else None
            
            for file_info in files if isinstance(files, list) else []:
                if file_info.get('format'):
                    file_formats.append(file_info['format'])
        else:
            file_count = record.get('file_count')
        
        # Determine gravity condition from mission or description
        gravity_condition = None
        mission = entities.get('missions', [])
        if mission or 'space' in title.lower() or 'microgravity' in description.lower():
            gravity_condition = GravityCondition.MICROGRAVITY
        
        return Dataset(
            id=str(dataset_id),
            title=title,
            description=description,
            organism=entities.get('organisms', [None])[0] if entities.get('organisms') else None,
            tissue=entities.get('tissues', [None])[0] if entities.get('tissues') else None,
            cell_type=record.get('cell_type'),
            mission=mission[0] if mission else None,
            experiment_type=record.get('experiment_type') or record.get('study_type'),
            measurement_type=list(set(measurement_types)),
            gravity_condition=gravity_condition,
            duration=record.get('duration'),
            sample_size=record.get('sample_size') or record.get('sample_count'),
            data_types=list(set(data_types)),
            file_formats=list(set(file_formats)),
            file_count=file_count,
            file_size=record.get('file_size'),
            publication_date=pub_date,
            last_updated=update_date,
            url=record.get('url') or record.get('web_url'),
            download_url=record.get('download_url'),
            related_publications=record.get('publications', []),
            keywords=entities.get('keywords', [])
        )


class OSDRIngestionPipeline:
    """Pipeline for OSDR data ingestion."""
    
    def __init__(self, output_path: Optional[str] = None):
        """Initialize pipeline."""
        self.output_path = output_path or "data/processed/osdr_datasets.json"
    
    async def run(self, batch_size: int = 100) -> List[Dataset]:
        """
        Run the complete OSDR ingestion pipeline.
        
        Args:
            batch_size: Batch size for processing
            
        Returns:
            List[Dataset]: Processed datasets
        """
        config = {
            'base_url': settings.osdr_base_url,
            'api_key': settings.nasa_api_key
        }
        
        ingester = OSDRIngester(config)
        datasets = []
        
        async for batch in ingester.run_ingestion(batch_size):
            datasets.extend(batch)
        
        # Save processed data
        if self.output_path:
            await self._save_datasets(datasets)
        
        return datasets
    
    async def _save_datasets(self, datasets: List[Dataset]):
        """Save datasets to JSON file."""
        import json
        from pathlib import Path
        
        output_file = Path(self.output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert to JSON-serializable format
        data = [dataset.dict() for dataset in datasets]
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str, ensure_ascii=False)
        
        print(f"Saved {len(datasets)} datasets to {output_file}")


# Export classes
__all__ = [
    "OSDRIngester", 
    "OSDRIngestionPipeline"
]