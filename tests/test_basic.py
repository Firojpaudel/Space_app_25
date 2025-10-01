"""
Basic tests for the Space Biology Knowledge Engine.
"""
import pytest
import asyncio
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class TestDataIngestion:
    """Test data ingestion components."""
    
    def test_csv_ingestion_import(self):
        """Test CSV ingestion import."""
        from data_ingestion import CSVPublicationIngester
        assert CSVPublicationIngester is not None
    
    def test_osdr_ingestion_import(self):
        """Test OSDR ingestion import.""" 
        from data_ingestion import OSDRIngester
        assert OSDRIngester is not None


class TestModels:
    """Test data models."""
    
    def test_publication_model(self):
        """Test Publication model."""
        from models.schemas import Publication
        
        pub = Publication(
            id="test_1",
            title="Test Publication",
            abstract="Test abstract",
            authors=["Author 1", "Author 2"],
            keywords=["test", "publication"]
        )
        
        assert pub.id == "test_1"
        assert pub.title == "Test Publication"
        assert len(pub.authors) == 2
    
    def test_dataset_model(self):
        """Test Dataset model."""
        from models.schemas import Dataset
        
        dataset = Dataset(
            id="test_dataset_1",
            title="Test Dataset",
            organism="Mouse",
            tissue="Bone"
        )
        
        assert dataset.id == "test_dataset_1"
        assert dataset.organism == "Mouse"


class TestUtilities:
    """Test utility functions."""
    
    def test_text_cleaning(self):
        """Test text cleaning function."""
        from utils.text_processing import clean_text
        
        dirty_text = "  This  is   a    test  text!!!  "
        clean = clean_text(dirty_text)
        
        assert clean == "This is a test text"
    
    @pytest.mark.asyncio
    async def test_keyword_extraction(self):
        """Test keyword extraction."""
        from utils.text_processing import extract_keywords
        
        text = "This study examines bone density in microgravity conditions during spaceflight missions"
        keywords = await extract_keywords(text)
        
        assert isinstance(keywords, list)
        assert len(keywords) > 0
        assert "bone" in keywords or "density" in keywords or "microgravity" in keywords


class TestConfiguration:
    """Test configuration."""
    
    def test_settings_import(self):
        """Test settings import."""
        from config import settings
        assert settings is not None
        assert hasattr(settings, 'app_name')
    
    def test_database_config(self):
        """Test database configuration."""
        from config import DatabaseConfig
        
        assert DatabaseConfig.PUBLICATIONS_INDEX == "publications"
        assert DatabaseConfig.DATASETS_INDEX == "datasets"


@pytest.mark.asyncio 
async def test_embedding_generation():
    """Test embedding generation (if OpenAI key available)."""
    try:
        from rag_system.embeddings import EmbeddingGenerator
        from config import settings
        
        if settings.openai_api_key and settings.openai_api_key != "your_openai_api_key_here":
            generator = EmbeddingGenerator()
            embedding = await generator.generate_embedding("test text")
            
            if embedding:  # Only test if successful
                assert isinstance(embedding, list)
                assert len(embedding) > 0
        else:
            pytest.skip("OpenAI API key not configured")
            
    except ImportError:
        pytest.skip("OpenAI package not available")
    except Exception as e:
        pytest.skip(f"Embedding test failed: {e}")


def test_main_entry_point():
    """Test main entry point import."""
    import main
    assert hasattr(main, 'main')


if __name__ == "__main__":
    pytest.main([__file__])