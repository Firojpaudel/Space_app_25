"""
Data models for the Space Biology Knowledge Engine.
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, HttpUrl
from enum import Enum


class DataSourceType(str, Enum):
    """Enumeration of data source types."""
    CSV_PUBLICATION = "csv_publication"
    OSDR_DATASET = "osdr_dataset"
    TASKBOOK_PROJECT = "taskbook_project"


class GravityCondition(str, Enum):
    """Enumeration of gravity conditions."""
    MICROGRAVITY = "microgravity"
    PARTIAL_GRAVITY = "partial_gravity"
    HYPERGRAVITY = "hypergravity"
    EARTH_GRAVITY = "earth_gravity"
    GROUND_CONTROL = "ground_control"


class StudyType(str, Enum):
    """Enumeration of study types."""
    OBSERVATIONAL = "observational"
    EXPERIMENTAL = "experimental"
    COMPUTATIONAL = "computational"
    REVIEW = "review"
    META_ANALYSIS = "meta_analysis"


class Publication(BaseModel):
    """Model for scientific publications."""
    
    id: str = Field(..., description="Unique identifier")
    title: str = Field(..., description="Publication title")
    abstract: Optional[str] = Field(None, description="Publication abstract")
    authors: List[str] = Field(default_factory=list, description="List of authors")
    journal: Optional[str] = Field(None, description="Journal name")
    publication_date: Optional[datetime] = Field(None, description="Publication date")
    doi: Optional[str] = Field(None, description="Digital Object Identifier")
    url: Optional[HttpUrl] = Field(None, description="Publication URL")
    keywords: List[str] = Field(default_factory=list, description="Keywords")
    mesh_terms: List[str] = Field(default_factory=list, description="MeSH terms")
    organisms: List[str] = Field(default_factory=list, description="Studied organisms")
    tissues: List[str] = Field(default_factory=list, description="Studied tissues")
    genes: List[str] = Field(default_factory=list, description="Mentioned genes")
    proteins: List[str] = Field(default_factory=list, description="Mentioned proteins")
    missions: List[str] = Field(default_factory=list, description="Related missions")
    gravity_condition: Optional[GravityCondition] = Field(None, description="Gravity condition")
    study_type: Optional[StudyType] = Field(None, description="Type of study")
    citation_count: Optional[int] = Field(None, description="Number of citations")
    embedding: Optional[List[float]] = Field(None, description="Text embedding vector")
    
    class Config:
        use_enum_values = True


class Dataset(BaseModel):
    """Model for NASA OSDR datasets."""
    
    id: str = Field(..., description="Dataset identifier")
    title: str = Field(..., description="Dataset title")
    description: Optional[str] = Field(None, description="Dataset description")
    organism: Optional[str] = Field(None, description="Study organism")
    tissue: Optional[str] = Field(None, description="Tissue type")
    cell_type: Optional[str] = Field(None, description="Cell type")
    mission: Optional[str] = Field(None, description="Space mission")
    experiment_type: Optional[str] = Field(None, description="Type of experiment")
    measurement_type: List[str] = Field(default_factory=list, description="Types of measurements")
    gravity_condition: Optional[GravityCondition] = Field(None, description="Gravity condition")
    duration: Optional[str] = Field(None, description="Experiment duration")
    sample_size: Optional[int] = Field(None, description="Number of samples")
    data_types: List[str] = Field(default_factory=list, description="Types of data")
    file_formats: List[str] = Field(default_factory=list, description="File formats")
    file_count: Optional[int] = Field(None, description="Number of files")
    file_size: Optional[str] = Field(None, description="Total file size")
    publication_date: Optional[datetime] = Field(None, description="Publication date")
    last_updated: Optional[datetime] = Field(None, description="Last update date")
    url: Optional[HttpUrl] = Field(None, description="Dataset URL")
    download_url: Optional[HttpUrl] = Field(None, description="Download URL")
    related_publications: List[str] = Field(default_factory=list, description="Related publication IDs")
    keywords: List[str] = Field(default_factory=list, description="Keywords")
    embedding: Optional[List[float]] = Field(None, description="Text embedding vector")
    
    class Config:
        use_enum_values = True


class TaskBookProject(BaseModel):
    """Model for NASA TaskBook projects."""
    
    id: str = Field(..., description="Project identifier")
    title: str = Field(..., description="Project title")
    description: Optional[str] = Field(None, description="Project description")
    principal_investigator: Optional[str] = Field(None, description="Principal investigator")
    institution: Optional[str] = Field(None, description="Institution")
    start_date: Optional[datetime] = Field(None, description="Project start date")
    end_date: Optional[datetime] = Field(None, description="Project end date")
    status: Optional[str] = Field(None, description="Project status")
    funding_amount: Optional[float] = Field(None, description="Funding amount")
    research_area: Optional[str] = Field(None, description="Research area")
    objectives: List[str] = Field(default_factory=list, description="Project objectives")
    milestones: List[str] = Field(default_factory=list, description="Project milestones")
    deliverables: List[str] = Field(default_factory=list, description="Project deliverables")
    organisms: List[str] = Field(default_factory=list, description="Studied organisms")
    tissues: List[str] = Field(default_factory=list, description="Studied tissues")
    missions: List[str] = Field(default_factory=list, description="Related missions")
    gravity_condition: Optional[GravityCondition] = Field(None, description="Gravity condition")
    keywords: List[str] = Field(default_factory=list, description="Keywords")
    related_datasets: List[str] = Field(default_factory=list, description="Related dataset IDs")
    related_publications: List[str] = Field(default_factory=list, description="Related publication IDs")
    url: Optional[HttpUrl] = Field(None, description="Project URL")
    annual_reports: List[Dict[str, Any]] = Field(default_factory=list, description="Annual reports")
    embedding: Optional[List[float]] = Field(None, description="Text embedding vector")
    
    class Config:
        use_enum_values = True


class Entity(BaseModel):
    """Model for extracted biological entities."""
    
    id: str = Field(..., description="Entity identifier")
    name: str = Field(..., description="Entity name")
    entity_type: str = Field(..., description="Type of entity")
    description: Optional[str] = Field(None, description="Entity description")
    synonyms: List[str] = Field(default_factory=list, description="Alternative names")
    external_ids: Dict[str, str] = Field(default_factory=dict, description="External database IDs")
    ontology_terms: List[str] = Field(default_factory=list, description="Ontology terms")
    confidence_score: Optional[float] = Field(None, description="Extraction confidence")
    source_documents: List[str] = Field(default_factory=list, description="Source document IDs")


class Relationship(BaseModel):
    """Model for relationships between entities."""
    
    id: str = Field(..., description="Relationship identifier")
    source_id: str = Field(..., description="Source entity ID")
    target_id: str = Field(..., description="Target entity ID")
    relationship_type: str = Field(..., description="Type of relationship")
    confidence_score: Optional[float] = Field(None, description="Relationship confidence")
    evidence: List[str] = Field(default_factory=list, description="Supporting evidence")
    source_documents: List[str] = Field(default_factory=list, description="Source document IDs")


class SearchQuery(BaseModel):
    """Model for search queries."""
    
    query: str = Field(..., description="Search query text")
    filters: Dict[str, Any] = Field(default_factory=dict, description="Search filters")
    limit: int = Field(default=10, description="Maximum results")
    offset: int = Field(default=0, description="Result offset")
    include_embeddings: bool = Field(default=False, description="Include embeddings in results")


class SearchResult(BaseModel):
    """Model for search results."""
    
    id: str = Field(..., description="Result identifier")
    title: str = Field(..., description="Result title")
    content: str = Field(..., description="Result content/abstract")
    source_type: DataSourceType = Field(..., description="Type of data source")
    url: Optional[HttpUrl] = Field(None, description="Result URL")
    score: float = Field(..., description="Relevance score")
    highlights: List[str] = Field(default_factory=list, description="Highlighted excerpts")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class RAGResponse(BaseModel):
    """Model for RAG system responses."""
    
    query: str = Field(..., description="Original query")
    answer: str = Field(..., description="Generated answer")
    sources: List[SearchResult] = Field(default_factory=list, description="Source documents")
    confidence_score: Optional[float] = Field(None, description="Answer confidence")
    processing_time: Optional[float] = Field(None, description="Processing time in seconds")
    simplified_explanation: Optional[str] = Field(None, description="Simplified explanation for education")


# Export all models
__all__ = [
    "DataSourceType",
    "GravityCondition", 
    "StudyType",
    "Publication",
    "Dataset",
    "TaskBookProject",
    "Entity",
    "Relationship",
    "SearchQuery",
    "SearchResult",
    "RAGResponse"
]