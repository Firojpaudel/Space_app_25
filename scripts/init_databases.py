"""
Initialize databases and setup the Space Biology Knowledge Engine.
"""
import asyncio
import logging
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config import settings, DatabaseConfig
from vector_db import WeaviateDB, VectorDBManager
from knowledge_graph.neo4j_client import Neo4jClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def initialize_vector_database():
    """Initialize vector database."""
    logger.info("Initializing vector database...")
    
    try:
        # Initialize vector DB client
        if settings.vector_db_type.lower() == 'pinecone':
            from vector_db import PineconeDB
            config = {
                'api_key': settings.pinecone_api_key,
                'environment': settings.pinecone_environment,
                'index_name': settings.pinecone_index_name,
                'dimension': 768  # Gemini embedding dimension
            }
            vector_client = PineconeDB(config)
        elif settings.vector_db_type.lower() == 'weaviate':
            config = {
                'url': settings.weaviate_url,
                'api_key': settings.weaviate_api_key
            }
            vector_client = WeaviateDB(config)
        else:
            logger.error(f"Unsupported vector DB type: {settings.vector_db_type}")
            return False
        
        # Test connection
        if not await vector_client.health_check():
            logger.error("Vector database health check failed")
            return False
        
        # Setup collections
        manager = VectorDBManager(vector_client)
        success = await manager.setup_collections()
        
        if success:
            logger.info("Vector database initialized successfully")
            return True
        else:
            logger.error("Failed to setup vector database collections")
            return False
            
    except Exception as e:
        logger.error(f"Error initializing vector database: {e}")
        return False


async def initialize_knowledge_graph():
    """Initialize knowledge graph database."""
    logger.info("Initializing knowledge graph...")
    
    try:
        # Initialize Neo4j client
        config = {
            'uri': settings.neo4j_uri,
            'user': settings.neo4j_user,
            'password': settings.neo4j_password
        }
        
        neo4j_client = Neo4jClient(config)
        
        # Test connection
        if not await neo4j_client.health_check():
            logger.error("Knowledge graph health check failed")
            return False
        
        # Setup schema
        success = await neo4j_client.setup_schema()
        
        if success:
            logger.info("Knowledge graph initialized successfully")
            return True
        else:
            logger.error("Failed to setup knowledge graph schema")
            return False
            
    except Exception as e:
        logger.error(f"Error initializing knowledge graph: {e}")
        return False


def create_data_directories():
    """Create necessary data directories."""
    logger.info("Creating data directories...")
    
    directories = [
        'data/raw',
        'data/processed',
        'data/embeddings',
        'logs',
        'cache'
    ]
    
    for directory in directories:
        dir_path = Path(directory)
        dir_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Created directory: {directory}")


def validate_configuration():
    """Validate configuration settings."""
    logger.info("Validating configuration...")
    
    required_settings = [
        ('gemini_api_key', settings.gemini_api_key),
        ('pinecone_api_key', settings.pinecone_api_key),
        ('neo4j_password', settings.neo4j_password)
    ]
    
    missing_settings = []
    
    for setting_name, setting_value in required_settings:
        if not setting_value:
            missing_settings.append(setting_name)
    
    if missing_settings:
        logger.error(f"Missing required settings: {', '.join(missing_settings)}")
        logger.error("Please check your .env file and ensure all required settings are provided")
        return False
    
    logger.info("Configuration validation passed")
    return True


async def main():
    """Main initialization function."""
    logger.info("Starting Space Biology Knowledge Engine initialization...")
    
    # Validate configuration
    if not validate_configuration():
        logger.error("Configuration validation failed. Exiting.")
        sys.exit(1)
    
    # Create directories
    create_data_directories()
    
    # Initialize databases
    vector_success = await initialize_vector_database()
    graph_success = await initialize_knowledge_graph()
    
    if vector_success and graph_success:
        logger.info("✅ All databases initialized successfully!")
        logger.info("You can now run data ingestion with: python scripts/ingest_data.py")
        logger.info("Or start the dashboard with: streamlit run dashboard/app.py")
    else:
        logger.error("❌ Database initialization failed")
        if not vector_success:
            logger.error("- Vector database initialization failed")
        if not graph_success:
            logger.error("- Knowledge graph initialization failed")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())