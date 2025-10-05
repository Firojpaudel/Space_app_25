"""
Configuration settings for the Space Biology Knowledge Engine.
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    app_name: str = Field(default="Space Biology Knowledge Engine", env="APP_NAME")
    app_version: str = Field(default="1.0.0", env="APP_VERSION")
    debug: bool = Field(default=False, env="DEBUG")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    
    # Google Gemini API (Free)
    gemini_api_key: str = Field(..., env="GEMINI_API_KEY")
    
    # Vector Database - Pinecone (Free)
    pinecone_api_key: str = Field(..., env="PINECONE_API_KEY")
    pinecone_environment: str = Field(default="us-east-1", env="PINECONE_ENVIRONMENT")
    pinecone_index_name: str = Field(default="space-biology-index", env="PINECONE_INDEX_NAME")
    
    # Graph Database
    neo4j_uri: str = Field(default="bolt://localhost:7687", env="NEO4J_URI")
    neo4j_user: str = Field(default="neo4j", env="NEO4J_USER")
    neo4j_password: str = Field(..., env="NEO4J_PASSWORD")
    
    # NASA APIs
    nasa_api_key: Optional[str] = Field(default=None, env="NASA_API_KEY")
    
    # Data Sources
    csv_data_path: str = Field(default="data/raw/SB_publication_PMC.csv", env="CSV_DATA_PATH")
    osdr_base_url: str = Field(default="https://osdr.nasa.gov/bio/repo", env="OSDR_BASE_URL")
    taskbook_base_url: str = Field(default="https://taskbook.nasaprs.com", env="TASKBOOK_BASE_URL")
    
    # Model Settings - Gemini (Free)
    embedding_model: str = Field(default="models/text-embedding-004", env="EMBEDDING_MODEL")
    llm_model: str = Field(default="gemini-2.5-flash", env="LLM_MODEL")
    max_tokens: int = Field(default=8192, env="MAX_TOKENS")  # Increased for very detailed responses
    temperature: float = Field(default=0.2, env="TEMPERATURE")  # Slightly increased for more detailed responses
    
    # Processing Settings
    chunk_size: int = Field(default=512, env="CHUNK_SIZE")
    chunk_overlap: int = Field(default=50, env="CHUNK_OVERLAP")
    batch_size: int = Field(default=50, env="BATCH_SIZE")
    
    model_config = {"env_file": ".env", "case_sensitive": False, "extra": "ignore"}
    
    @property
    def csv_file_path(self) -> str:
        """Compatibility property for csv_data_path."""
        return self.csv_data_path


# Global settings instance - removed to avoid validation errors
# settings = Settings()


class DatabaseConfig:
    """Database configuration constants."""
    
    # Vector DB Collections/Indexes
    PUBLICATIONS_INDEX = "publications"
    DATASETS_INDEX = "datasets"
    TASKBOOK_INDEX = "taskbook_projects"
    
    # Graph DB Node Labels
    PUBLICATION_LABEL = "Publication"
    DATASET_LABEL = "Dataset"
    PROJECT_LABEL = "Project"
    ORGANISM_LABEL = "Organism"
    TISSUE_LABEL = "Tissue"
    MISSION_LABEL = "Mission"
    GENE_LABEL = "Gene"
    PROTEIN_LABEL = "Protein"
    
    # Graph DB Relationship Types
    STUDIES_REL = "STUDIES"
    USES_REL = "USES"
    CONDUCTED_ON_REL = "CONDUCTED_ON"
    RELATES_TO_REL = "RELATES_TO"
    CITES_REL = "CITES"
    PART_OF_REL = "PART_OF"


class ModelConfig:
    """ML Model configuration constants."""
    
    # NER Models
    SCISPACY_MODEL = "en_core_sci_lg"
    BIOBERT_MODEL = "dmis-lab/biobert-base-cased-v1.1"
    
    # Embedding Models
    GEMINI_EMBEDDING_MODEL = "models/text-embedding-004"
    HUGGINGFACE_EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
    
    # Text Generation Models
    GEMINI_LLM_MODEL = "gemini-2.5-flash"
    HUGGINGFACE_LLM_MODEL = "microsoft/BioGPT-Large"
    
    # Entity Types for NER
    ENTITY_TYPES = [
        "ORGANISM",
        "TISSUE",
        "GENE",
        "PROTEIN",
        "DISEASE",
        "CHEMICAL",
        "CELL_TYPE",
        "MISSION",
        "EXPERIMENT_TYPE"
    ]


class APIConfig:
    """API endpoint configuration."""
    
    # NASA OSDR API endpoints
    OSDR_SEARCH_ENDPOINT = "/bio/repo/data"
    OSDR_METADATA_ENDPOINT = "/bio/repo/data/{dataset_id}"
    
    # TaskBook API endpoints (hypothetical - may need web scraping)
    TASKBOOK_SEARCH_ENDPOINT = "/api/search"
    TASKBOOK_PROJECT_ENDPOINT = "/api/project/{project_id}"
    
    # Rate limiting
    MAX_REQUESTS_PER_MINUTE = 60
    REQUEST_TIMEOUT = 30


# Export all configurations
__all__ = [
    "Settings",
    "settings",
    "DatabaseConfig",
    "ModelConfig", 
    "APIConfig"
]