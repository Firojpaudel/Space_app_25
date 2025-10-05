"""
CSV data ingestion for bioscience publications.
"""
import pandas as pd
import asyncio
from datetime import datetime
from typing import List, Dict, Any, AsyncGenerator, Optional
from pathlib import Path

from .base import BaseIngester
from models.schemas import Publication, DataSourceType
from utils.text_processing import extract_keywords, clean_text
from utils.entity_extraction import extract_biological_entities


class CSVPublicationIngester(BaseIngester):
    """Ingester for CSV files containing bioscience publications."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize CSV ingester."""
        super().__init__(config)
        self.file_path = config.get('file_path')
        self.encoding = config.get('encoding', 'utf-8')
        self.chunk_size = config.get('chunk_size', 1000)
        
        if not self.file_path or not Path(self.file_path).exists():
            raise ValueError(f"CSV file not found: {self.file_path}")
    
    async def ingest(self) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Ingest publications from CSV file.
        
        Yields:
            Dict[str, Any]: Raw publication records
        """
        self.logger.info(f"Starting CSV ingestion from {self.file_path}")
        
        try:
            # Read CSV in chunks to handle large files
            chunk_reader = pd.read_csv(
                self.file_path,
                encoding=self.encoding,
                chunksize=self.chunk_size,
                low_memory=False
            )
            
            for chunk_idx, chunk in enumerate(chunk_reader):
                self.logger.info(f"Processing chunk {chunk_idx + 1} with {len(chunk)} records")
                
                for _, row in chunk.iterrows():
                    yield row.to_dict()
                    
                # Add small delay to prevent blocking
                await asyncio.sleep(0.001)
                
        except Exception as e:
            self.logger.error(f"Error reading CSV file: {e}")
            raise
    
    async def validate_record(self, record: Dict[str, Any]) -> bool:
        """
        Validate a publication record.
        
        Args:
            record: Raw publication record
            
        Returns:
            bool: True if record is valid
        """
        # Check required fields - handle both uppercase and lowercase
        title_field = record.get('Title') or record.get('title')
        
        if not title_field or pd.isna(title_field):
            self.logger.warning(f"Missing required field 'Title/title' in record")
            return False
        
        # Check title length
        title = str(title_field)
        if len(title.strip()) < 10:
            self.logger.warning(f"Title too short: {title[:50]}...")
            return False
        
        return True
    
    async def transform_record(self, record: Dict[str, Any]) -> Publication:
        """
        Transform raw CSV record to Publication model.
        
        Args:
            record: Raw CSV record
            
        Returns:
            Publication: Transformed publication
        """
        # Clean and extract basic fields - handle both uppercase and lowercase
        title_field = record.get('Title') or record.get('title')
        title = clean_text(str(title_field)) if title_field else ''
        url_field = record.get('Link') or record.get('url')
        url = str(url_field) if url_field and not pd.isna(url_field) else None
        
        # Extract additional fields from our enhanced CSV format
        abstract_field = record.get('Abstract') or record.get('abstract')
        abstract = clean_text(str(abstract_field)) if abstract_field and not pd.isna(abstract_field) else None
        
        authors_field = record.get('Authors') or record.get('authors')
        authors = str(authors_field).split(', ') if authors_field and not pd.isna(authors_field) else []
        
        journal_field = record.get('Journal') or record.get('journal')
        journal = str(journal_field) if journal_field and not pd.isna(journal_field) else None
        
        # Parse publication date
        pub_date = None
        date_field = record.get('Publication_Date') or record.get('publication_date')
        if date_field and not pd.isna(date_field):
            try:
                pub_date = pd.to_datetime(str(date_field)).to_pydatetime()
            except:
                pass
        
        # Extract DOI
        doi_field = record.get('DOI') or record.get('doi')
        doi = str(doi_field) if doi_field and not pd.isna(doi_field) else None
        
        # Extract keywords from CSV or generate from text
        keywords_field = record.get('Keywords') or record.get('keywords')
        if keywords_field and not pd.isna(keywords_field):
            keywords = [k.strip() for k in str(keywords_field).split(',')]
        else:
            keywords = await extract_keywords(title)
        
        # Extract biological entities from title and abstract
        text_for_entities = f"{title} {abstract or ''}"
        entities = await extract_biological_entities(text_for_entities)
        
        # Extract PMC ID from URL
        pmcid = None
        if url and 'PMC' in url:
            import re
            pmc_match = re.search(r'PMC(\d+)', url)
            if pmc_match:
                pmcid = f"PMC{pmc_match.group(1)}"
        
        # Create publication ID
        pub_id = pmcid or f"pmc_{hash(title)}"
        
        return Publication(
            id=str(pub_id),
            title=title,
            abstract=abstract,
            authors=authors,
            journal=journal,
            publication_date=pub_date,
            doi=doi,
            url=url,
            keywords=keywords,
            mesh_terms=entities.get('mesh_terms', []),
            organisms=entities.get('organisms', []),
            tissues=entities.get('tissues', []),
            genes=entities.get('genes', []),
            proteins=entities.get('proteins', []),
            missions=entities.get('missions', []),
            gravity_condition=entities.get('gravity_condition'),
            study_type=entities.get('study_type'),
            citation_count=None  # Not available in PMC CSV
        )


class CSVIngestionPipeline:
    """Pipeline for CSV data ingestion."""
    
    def __init__(self, file_path: str, output_path: Optional[str] = None):
        """Initialize pipeline."""
        self.file_path = file_path
        self.output_path = output_path or "data/processed/publications.json"
        self.ingester = None
    
    async def run(self, batch_size: int = 100) -> List[Publication]:
        """
        Run the complete CSV ingestion pipeline.
        
        Args:
            batch_size: Batch size for processing
            
        Returns:
            List[Publication]: Processed publications
        """
        config = {
            'file_path': self.file_path,
            'chunk_size': batch_size
        }
        
        self.ingester = CSVPublicationIngester(config)
        publications = []
        
        async for batch in self.ingester.run_ingestion(batch_size):
            publications.extend(batch)
        
        # Save processed data
        if self.output_path:
            await self._save_publications(publications)
        
        return publications
    
    async def _save_publications(self, publications: List[Publication]):
        """Save publications to JSON file."""
        import json
        from pathlib import Path
        
        output_file = Path(self.output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert to JSON-serializable format
        data = [pub.dict() for pub in publications]
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str, ensure_ascii=False)
        
        print(f"Saved {len(publications)} publications to {output_file}")


# Export classes
__all__ = [
    "CSVPublicationIngester",
    "CSVIngestionPipeline"
]