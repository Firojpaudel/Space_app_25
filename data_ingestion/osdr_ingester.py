"""
NASA OSDR (Open Science Data Repository) data ingestion using official API.
"""
import aiohttp
import asyncio
from datetime import datetime
from typing import List, Dict, Any, AsyncGenerator, Optional
import json
import re
from urllib.parse import urljoin, urlencode

from .base import BaseIngester
from models.schemas import Dataset, GravityCondition
from utils.text_processing import clean_text
from utils.entity_extraction import extract_biological_entities

# Create settings instance
try:
    from config.settings import Settings
    settings = Settings()
except Exception:
    # Fallback for missing .env file
    class MockSettings:
        osdr_base_url = "https://osdr.nasa.gov/bio/repo"
        nasa_api_key = None
    settings = MockSettings()


class OSDRIngester(BaseIngester):
    """Ingester for NASA OSDR datasets using official API."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize OSDR ingester."""
        super().__init__(config)
        self.base_url = config.get('base_url', settings.osdr_base_url)
        self.api_key = config.get('api_key', settings.nasa_api_key)
        self.max_concurrent = config.get('max_concurrent', 10)
        self.request_delay = config.get('request_delay', 1.0)
        
        # API endpoints
        self.studies_api = "https://osdr.nasa.gov/geode-py/ws/studies"
        self.metadata_api = "https://osdr.nasa.gov/osdr/data/osd/meta"
        self.search_api = "https://osdr.nasa.gov/osdr/data/search"
        self.files_api = "https://osdr.nasa.gov/osdr/data/osd/files"
        
        # Initialize session with headers
        self.headers = {
            'User-Agent': 'Space-Biology-Knowledge-Engine/1.0',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        if self.api_key:
            self.headers['X-API-Key'] = self.api_key
    
    async def ingest(self) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Ingest datasets from NASA OSDR using the official API.
        
        Yields:
            Dict[str, Any]: Raw dataset records
        """
        self.logger.info("Starting OSDR dataset ingestion using official API")
        
        async with aiohttp.ClientSession(headers=self.headers) as session:
            # Get list of all study IDs from the API
            study_ids = await self._fetch_study_ids(session)
            
            # Process studies in batches to avoid overwhelming the server
            semaphore = asyncio.Semaphore(self.max_concurrent)
            
            for study_id in study_ids:
                async with semaphore:
                    try:
                        # Extract numeric ID from OSD-XXX format
                        numeric_id = study_id.replace('OSD-', '') if study_id.startswith('OSD-') else study_id
                        
                        study_metadata = await self._fetch_study_metadata(session, numeric_id)
                        if study_metadata:
                            yield study_metadata
                        
                        # Add delay between requests
                        await asyncio.sleep(self.request_delay)
                        
                    except Exception as e:
                        self.logger.error(f"Error fetching study {study_id}: {e}")
                        continue
    
    async def _fetch_study_ids(self, session: aiohttp.ClientSession) -> List[str]:
        """
        Fetch list of all available study IDs from the OSDR API.
        
        Args:
            session: HTTP session
            
        Returns:
            List[str]: List of study IDs
        """
        try:
            url = self.studies_api
            
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    study_ids = data.get('content', [])
                    self.logger.info(f"Found {len(study_ids)} studies in OSDR")
                    return study_ids
                else:
                    self.logger.error(f"HTTP {response.status} for study list")
                    return []
                    
        except Exception as e:
            self.logger.error(f"Error fetching study list: {e}")
            return []
    
    async def _fetch_study_metadata(self, session: aiohttp.ClientSession, study_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetch detailed metadata for a specific study using the official API.
        
        Args:
            session: HTTP session
            study_id: Study identifier (numeric, e.g., 877)
            
        Returns:
            Optional[Dict[str, Any]]: Study metadata
        """
        try:
            url = f"{self.metadata_api}/{study_id}"
            
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    return await self._parse_api_metadata(data, study_id)
                else:
                    self.logger.warning(f"HTTP {response.status} for study {study_id}")
                    return None
                    
        except Exception as e:
            self.logger.error(f"Error fetching study metadata {study_id}: {e}")
            return None
    
    async def _parse_api_metadata(self, api_data: Dict[str, Any], study_id: str) -> Dict[str, Any]:
        """
        Parse study details from OSDR API metadata response.
        
        Args:
            api_data: JSON response from OSDR metadata API
            study_id: Study identifier
            
        Returns:
            Dict[str, Any]: Parsed study details
        """
        study_data = {
            'id': f"OSD-{study_id}",
            'study_id': f"OSD-{study_id}",
            'url': f"https://osdr.nasa.gov/bio/repo/data/studies/OSD-{study_id}"
        }
        
        try:
            # Navigate the API response structure
            study_info = api_data.get('study', {})
            if isinstance(study_info, dict) and f'OSD-{study_id}' in study_info:
                study_details = study_info[f'OSD-{study_id}']
            else:
                self.logger.warning(f"Unexpected API structure for study {study_id}")
                return study_data
            
            # Extract basic study information
            studies_list = study_details.get('studies', [])
            if studies_list:
                main_study = studies_list[0]  # Take the first study
                
                # Extract title and description
                title = main_study.get('title', f'Study OSD-{study_id}')
                description = main_study.get('description', '')
                
                study_data.update({
                    'title': clean_text(title),
                    'name': clean_text(title),
                    'description': clean_text(description),
                    'summary': clean_text(description)
                })
                
                # Extract dates
                if main_study.get('publicReleaseDate'):
                    try:
                        pub_date = datetime.strptime(main_study['publicReleaseDate'], '%d-%b-%Y')
                        study_data['publication_date'] = pub_date.isoformat()
                    except:
                        study_data['publication_date'] = main_study['publicReleaseDate']
                
                if main_study.get('submissionDate'):
                    try:
                        sub_date = datetime.strptime(main_study['submissionDate'], '%d-%b-%Y')
                        study_data['submitted_date'] = sub_date.isoformat()
                    except:
                        study_data['submitted_date'] = main_study['submissionDate']
                
                # Extract organisms
                organisms = []
                additional_info = study_details.get('additionalInformation', {})
                organisms_info = additional_info.get('organisms', {})
                if organisms_info and 'links' in organisms_info:
                    for org_key, org_link in organisms_info['links'].items():
                        # Extract organism name from the link text
                        organism_match = re.search(r'>([^<]+)<', org_link)
                        if organism_match:
                            organisms.append(organism_match.group(1).strip())
                
                study_data['organisms'] = organisms
                
                # Extract assays and measurement types
                assays = []
                measurement_types = []
                assays_info = additional_info.get('assays', {})
                for assay_key, assay_data in assays_info.items():
                    # Parse assay name from the key (format: a_OSD-137_measurement-type_technology-type_platform)
                    assay_parts = assay_key.split('_')
                    if len(assay_parts) >= 3:
                        measurement_type = assay_parts[2].replace('-', ' ').title()
                        technology_type = assay_parts[3].replace('-', ' ').title() if len(assay_parts) > 3 else ''
                        
                        assays.append({
                            'measurement_type': measurement_type,
                            'technology_type': technology_type
                        })
                        measurement_types.append(measurement_type)
                
                study_data['assays'] = assays
                study_data['measurement_types'] = measurement_types
                
                # Extract project information from comments
                project_data = {}
                comments = main_study.get('comments', [])
                for comment in comments:
                    name = comment.get('name', '').lower().replace(' ', '_')
                    value = comment.get('value', '')
                    if name and value:
                        project_data[name] = value
                
                study_data['project'] = project_data
                
                # Extract mission information
                mission = None
                if 'flight_program' in project_data:
                    mission = project_data['flight_program']
                elif 'mission_name' in project_data:
                    mission = project_data['mission_name']
                study_data['mission'] = mission
                
                # Extract DOI
                if 'doi' in project_data:
                    study_data['doi'] = project_data['doi']
                
                # Extract funding information
                if 'funding' in project_data:
                    study_data['funding'] = project_data['funding']
                
                # Extract publications
                publications = main_study.get('publications', [])
                study_data['related_publications'] = [pub.get('title', '') for pub in publications]
                
                # Set study type and experiment type
                study_data['study_type'] = 'biological'
                study_data['experiment_type'] = 'space biology'
                
                # Determine gravity condition
                gravity_condition = None
                if mission and any(term in mission.lower() for term in ['space', 'iss', 'apollo', 'shuttle']):
                    gravity_condition = 'MICROGRAVITY'
                elif 'ground' in description.lower() or 'ground' in title.lower():
                    gravity_condition = 'GROUND_CONTROL'
                study_data['gravity_condition'] = gravity_condition
            
        except Exception as e:
            self.logger.error(f"Error parsing API metadata for study {study_id}: {e}")
        
        return study_data
    
    async def validate_record(self, record: Dict[str, Any]) -> bool:
        """
        Validate a dataset record.
        
        Args:
            record: Raw dataset record from API
            
        Returns:
            bool: True if record is valid
        """
        # Check required fields
        if not record.get('title') and not record.get('name'):
            return False
        
        # Must have some form of identifier
        if not any([record.get('id'), record.get('study_id'), record.get('dataset_id')]):
            return False
        
        # Basic content check
        title = record.get('title', '')
        if len(title.strip()) < 5:  # Too short to be meaningful
            return False
        
        return True
    
    async def transform_record(self, record: Dict[str, Any]) -> Dataset:
        """
        Transform raw OSDR record to Dataset model.
        
        Args:
            record: Raw OSDR record from API
            
        Returns:
            Dataset: Transformed dataset
        """
        # Extract basic information
        title = clean_text(record.get('title') or record.get('name', ''))
        description = clean_text(record.get('description') or record.get('summary', ''))
        
        # Create dataset ID
        dataset_id = (record.get('id') or 
                     record.get('study_id') or 
                     record.get('dataset_id') or 
                     f"osdr_{hash(title)}")
        
        # Extract biological information
        text_for_entities = f"{title} {description}"
        entities = await extract_biological_entities(text_for_entities)
        
        # Parse dates
        pub_date = None
        update_date = None
        
        if record.get('publication_date'):
            try:
                date_str = record.get('publication_date')
                if 'T' not in date_str and len(date_str) > 10:
                    # ISO format from parsing
                    pub_date = datetime.fromisoformat(date_str)
                else:
                    pub_date = datetime.fromisoformat(str(date_str).replace('Z', '+00:00'))
            except:
                pass
        
        if record.get('last_updated'):
            try:
                date_str = record.get('last_updated')
                if 'T' not in date_str and len(date_str) > 10:
                    update_date = datetime.fromisoformat(date_str)
                else:
                    update_date = datetime.fromisoformat(str(date_str).replace('Z', '+00:00'))
            except:
                pass
        
        # Extract measurement and data types
        measurement_types = record.get('measurement_types', [])
        data_types = []
        file_formats = []
        
        # Look for assay information
        if record.get('assays'):
            for assay in record.get('assays', []):
                if assay.get('measurement_type') and assay['measurement_type'] not in measurement_types:
                    measurement_types.append(assay['measurement_type'])
                if assay.get('technology_type'):
                    data_types.append(assay['technology_type'])
        
        # Use organisms from API data or entity extraction
        organisms_list = record.get('organisms', [])
        if not organisms_list:
            organisms_list = entities.get('organisms', [])
        
        # Extract mission information
        mission = None
        if record.get('project', {}).get('flight_program'):
            mission = record['project']['flight_program']
        elif record.get('mission'):
            mission = record['mission']
        elif entities.get('missions'):
            mission = entities['missions'][0]
        
        # Determine gravity condition
        gravity_condition = None
        gravity_str = record.get('gravity_condition')
        if gravity_str:
            if gravity_str.upper() == 'MICROGRAVITY':
                gravity_condition = GravityCondition.MICROGRAVITY
            elif gravity_str.upper() == 'GROUND_CONTROL':
                gravity_condition = GravityCondition.GROUND_CONTROL
        elif (mission and any(term in mission.lower() for term in ['space', 'apollo', 'iss', 'shuttle'])) or \
             'space' in title.lower() or 'microgravity' in description.lower() or \
             'spaceflight' in description.lower():
            gravity_condition = GravityCondition.MICROGRAVITY
        elif 'ground' in title.lower() or 'ground' in description.lower():
            gravity_condition = GravityCondition.GROUND_CONTROL
        
        return Dataset(
            id=str(dataset_id),
            title=title,
            description=description,
            organism=organisms_list[0] if organisms_list else (entities.get('organisms', [None]) + [None])[0],
            tissue=(entities.get('tissues', [None]) + [None])[0],
            cell_type=record.get('cell_type'),
            mission=mission,
            experiment_type=record.get('experiment_type') or record.get('study_type', 'space biology'),
            measurement_type=list(set(measurement_types)),
            gravity_condition=gravity_condition,
            duration=record.get('duration'),
            sample_size=record.get('sample_size') or record.get('sample_count'),
            data_types=list(set(data_types)),
            file_formats=list(set(file_formats)),
            file_count=record.get('file_count'),
            file_size=record.get('file_size'),
            publication_date=pub_date,
            last_updated=update_date,
            url=record.get('url'),
            download_url=record.get('download_url'),
            related_publications=record.get('related_publications', []),
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