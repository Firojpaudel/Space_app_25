"""
Main data ingestion script for the Space Biology Knowledge Engine.
"""
import asyncio
import logging
import sys
import argparse
from pathlib import Path
from typing import List, Dict, Any

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config import settings
from data_ingestion import CSVIngestionPipeline, OSDRIngestionPipeline
from models.schemas import Publication, Dataset, TaskBookProject

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataIngestionManager:
    """Manages the complete data ingestion process."""
    
    def __init__(self):
        """Initialize ingestion manager."""
        self.publications = []
        self.datasets = []
        self.projects = []
    
    async def ingest_csv_publications(self, file_path: str) -> int:
        """Ingest publications from CSV file."""
        logger.info(f"Starting CSV publication ingestion from {file_path}")
        
        try:
            pipeline = CSVIngestionPipeline(
                file_path=file_path,
                output_path="data/processed/publications.json"
            )
            
            publications = await pipeline.run(batch_size=100)
            self.publications.extend(publications)
            
            logger.info(f"Successfully ingested {len(publications)} publications")
            return len(publications)
            
        except Exception as e:
            logger.error(f"Error ingesting CSV publications: {e}")
            return 0
    
    async def ingest_osdr_datasets(self) -> int:
        """Ingest datasets from NASA OSDR."""
        logger.info("Starting OSDR dataset ingestion")
        
        try:
            pipeline = OSDRIngestionPipeline(
                output_path="data/processed/osdr_datasets.json"
            )
            
            datasets = await pipeline.run(batch_size=50)
            self.datasets.extend(datasets)
            
            logger.info(f"Successfully ingested {len(datasets)} datasets")
            return len(datasets)
            
        except Exception as e:
            logger.error(f"Error ingesting OSDR datasets: {e}")
            return 0
    
    async def ingest_taskbook_projects(self) -> int:
        """Ingest projects from NASA TaskBook."""
        logger.info("Starting TaskBook project ingestion")
        
        # TaskBook ingestion would be implemented here
        # For now, return 0 as placeholder
        logger.warning("TaskBook ingestion not yet implemented")
        return 0
    
    async def generate_embeddings(self):
        """Generate embeddings for all ingested data."""
        logger.info("Generating embeddings for ingested data...")
        
        # Import embedding utilities
        from rag_system.embeddings import EmbeddingGenerator
        
        try:
            embedding_gen = EmbeddingGenerator()
            
            # Generate embeddings for publications
            if self.publications:
                logger.info(f"Generating embeddings for {len(self.publications)} publications")
                for pub in self.publications:
                    text = f"{pub.title} {pub.abstract or ''}"
                    pub.embedding = await embedding_gen.generate_embedding(text)
            
            # Generate embeddings for datasets
            if self.datasets:
                logger.info(f"Generating embeddings for {len(self.datasets)} datasets")
                for dataset in self.datasets:
                    text = f"{dataset.title} {dataset.description or ''}"
                    dataset.embedding = await embedding_gen.generate_embedding(text)
            
            # Generate embeddings for projects
            if self.projects:
                logger.info(f"Generating embeddings for {len(self.projects)} projects")
                for project in self.projects:
                    text = f"{project.title} {project.description or ''}"
                    project.embedding = await embedding_gen.generate_embedding(text)
            
            logger.info("Embedding generation completed")
            
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
    
    async def store_in_vector_db(self):
        """Store data in vector database."""
        logger.info("Storing data in vector database...")
        
        try:
            from vector_db import PineconeDB, VectorDBManager
            from config import DatabaseConfig
            
            # Initialize vector DB
            if settings.vector_db_type.lower() == 'pinecone':
                config = {
                    'api_key': settings.pinecone_api_key,
                    'environment': settings.pinecone_environment,
                    'index_name': settings.pinecone_index_name,
                    'dimension': 768  # Gemini embedding dimension
                }
                vector_client = PineconeDB(config)
            else:
                from vector_db import WeaviateDB
                config = {
                    'url': settings.weaviate_url,
                    'api_key': settings.weaviate_api_key
                }
                vector_client = WeaviateDB(config)
            
            manager = VectorDBManager(vector_client)
            
            # Store publications
            if self.publications:
                pub_docs = [self._publication_to_doc(pub) for pub in self.publications]
                count = await manager.batch_insert(
                    DatabaseConfig.PUBLICATIONS_INDEX,
                    pub_docs
                )
                logger.info(f"Stored {count} publications in vector DB")
            
            # Store datasets
            if self.datasets:
                dataset_docs = [self._dataset_to_doc(dataset) for dataset in self.datasets]
                count = await manager.batch_insert(
                    DatabaseConfig.DATASETS_INDEX,
                    dataset_docs
                )
                logger.info(f"Stored {count} datasets in vector DB")
            
            # Store projects
            if self.projects:
                project_docs = [self._project_to_doc(project) for project in self.projects]
                count = await manager.batch_insert(
                    DatabaseConfig.TASKBOOK_INDEX,
                    project_docs
                )
                logger.info(f"Stored {count} projects in vector DB")
            
        except Exception as e:
            logger.error(f"Error storing data in vector DB: {e}")
    
    async def store_in_knowledge_graph(self):
        """Store data in knowledge graph."""
        logger.info("Storing data in knowledge graph...")
        
        try:
            from knowledge_graph.neo4j_client import Neo4jClient
            
            # Initialize Neo4j client
            config = {
                'uri': settings.neo4j_uri,
                'user': settings.neo4j_user,
                'password': settings.neo4j_password
            }
            neo4j_client = Neo4jClient(config)
            
            # Store publications
            if self.publications:
                await neo4j_client.batch_create_publications(self.publications)
                logger.info(f"Stored {len(self.publications)} publications in knowledge graph")
            
            # Store datasets  
            if self.datasets:
                await neo4j_client.batch_create_datasets(self.datasets)
                logger.info(f"Stored {len(self.datasets)} datasets in knowledge graph")
            
            # Create relationships
            await neo4j_client.create_relationships(
                self.publications, 
                self.datasets, 
                self.projects
            )
            logger.info("Created relationships in knowledge graph")
            
        except Exception as e:
            logger.error(f"Error storing data in knowledge graph: {e}")
    
    def _publication_to_doc(self, pub: Publication) -> Dict[str, Any]:
        """Convert publication to vector DB document."""
        return {
            'id': pub.id,
            'title': pub.title,
            'content': f"{pub.title} {pub.abstract or ''}",
            'source_type': 'publication',
            'url': str(pub.url) if pub.url else None,
            'authors': pub.authors,
            'journal': pub.journal,
            'keywords': pub.keywords,
            'organisms': pub.organisms,
            'tissues': pub.tissues,
            'missions': pub.missions,
            'publication_date': pub.publication_date,
            'embedding': pub.embedding
        }
    
    def _dataset_to_doc(self, dataset: Dataset) -> Dict[str, Any]:
        """Convert dataset to vector DB document."""
        return {
            'id': dataset.id,
            'title': dataset.title,
            'content': f"{dataset.title} {dataset.description or ''}",
            'source_type': 'dataset',
            'url': str(dataset.url) if dataset.url else None,
            'organism': dataset.organism,
            'tissue': dataset.tissue,
            'experiment_type': dataset.experiment_type,
            'keywords': dataset.keywords,
            'organisms': [dataset.organism] if dataset.organism else [],
            'tissues': [dataset.tissue] if dataset.tissue else [],
            'missions': [dataset.mission] if dataset.mission else [],
            'publication_date': dataset.publication_date,
            'embedding': dataset.embedding
        }
    
    def _project_to_doc(self, project: TaskBookProject) -> Dict[str, Any]:
        """Convert project to vector DB document."""
        return {
            'id': project.id,
            'title': project.title,
            'content': f"{project.title} {project.description or ''}",
            'source_type': 'project',
            'url': str(project.url) if project.url else None,
            'principal_investigator': project.principal_investigator,
            'institution': project.institution,
            'keywords': project.keywords,
            'organisms': project.organisms,
            'tissues': project.tissues, 
            'missions': project.missions,
            'publication_date': project.start_date,
            'embedding': project.embedding
        }
    
    def get_stats(self) -> Dict[str, int]:
        """Get ingestion statistics."""
        return {
            'publications': len(self.publications),
            'datasets': len(self.datasets),
            'projects': len(self.projects),
            'total': len(self.publications) + len(self.datasets) + len(self.projects)
        }


async def main():
    """Main ingestion function."""
    parser = argparse.ArgumentParser(description="Ingest data for Space Biology Knowledge Engine")
    parser.add_argument("--csv-file", help="Path to CSV file with publications")
    parser.add_argument("--skip-osdr", action="store_true", help="Skip OSDR ingestion")
    parser.add_argument("--skip-taskbook", action="store_true", help="Skip TaskBook ingestion")
    parser.add_argument("--skip-embeddings", action="store_true", help="Skip embedding generation")
    parser.add_argument("--skip-storage", action="store_true", help="Skip database storage")
    
    args = parser.parse_args()
    
    logger.info("Starting data ingestion process...")
    
    # Initialize manager
    manager = DataIngestionManager()
    
    # Ingestion phase
    total_ingested = 0
    
    # Ingest CSV publications
    if args.csv_file:
        count = await manager.ingest_csv_publications(args.csv_file)
        total_ingested += count
    else:
        # Try default path
        default_csv = Path("data/raw/bioscience_publications.csv")
        if default_csv.exists():
            count = await manager.ingest_csv_publications(str(default_csv))
            total_ingested += count
        else:
            logger.warning("No CSV file provided and default file not found")
    
    # Ingest OSDR datasets
    if not args.skip_osdr:
        count = await manager.ingest_osdr_datasets()
        total_ingested += count
    
    # Ingest TaskBook projects
    if not args.skip_taskbook:
        count = await manager.ingest_taskbook_projects()
        total_ingested += count
    
    # Processing phase
    if total_ingested > 0:
        # Generate embeddings
        if not args.skip_embeddings:
            await manager.generate_embeddings()
        
        # Store in databases
        if not args.skip_storage:
            await manager.store_in_vector_db()
            await manager.store_in_knowledge_graph()
        
        # Print statistics
        stats = manager.get_stats()
        logger.info("Ingestion completed!")
        logger.info(f"Statistics: {stats}")
        
    else:
        logger.warning("No data was ingested")


if __name__ == "__main__":
    asyncio.run(main())