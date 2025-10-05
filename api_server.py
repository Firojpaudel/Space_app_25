#!/usr/bin/env python3
"""
FastAPI server for K-OSMOS frontend integration.
This wraps the existing RAG system and exposes REST API endpoints.
"""
import asyncio
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from config.settings import Settings
from rag_system.chat import SpaceBiologyRAG
from utils.entity_extraction import BiologicalEntityExtractor
from utils.chat_database import ChatDatabase

# Initialize FastAPI app
app = FastAPI(
    title="K-OSMOS API",
    description="AI-Powered Research Platform for Space Biology Literature",
    version="1.0.0"
)

# CORS middleware for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:8000",
        "https://k-osmos.streamlit.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
settings = Settings()
rag_system = None
entity_extractor = None
chat_db = None


# Request/Response Models
class ChatRequest(BaseModel):
    message: str = Field(..., description="User message")
    session_id: Optional[str] = Field(None, description="Chat session ID")


class ChatResponse(BaseModel):
    response: str
    sources: List[Dict[str, Any]] = []
    entities: List[Dict[str, Any]] = []
    session_id: str


class SearchRequest(BaseModel):
    query: str
    filters: Optional[Dict[str, Any]] = None
    limit: int = 10


class SearchResult(BaseModel):
    id: str
    title: str
    content: str
    source_type: str
    url: Optional[str] = None
    score: float
    metadata: Dict[str, Any] = {}


class EntityExtractionRequest(BaseModel):
    text: str


class SessionResponse(BaseModel):
    session_id: str


# Dependency to get initialized services
async def get_rag_system():
    global rag_system
    if rag_system is None:
        rag_system = SpaceBiologyRAG(settings)
    return rag_system


async def get_entity_extractor():
    global entity_extractor
    if entity_extractor is None:
        entity_extractor = BiologicalEntityExtractor()
    return entity_extractor


async def get_chat_db():
    global chat_db
    if chat_db is None:
        chat_db = ChatDatabase()
    return chat_db


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "K-OSMOS API"
    }


# Chat endpoints
@app.post("/api/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    rag: SpaceBiologyRAG = Depends(get_rag_system),
    extractor: BiologicalEntityExtractor = Depends(get_entity_extractor),
    db: ChatDatabase = Depends(get_chat_db)
):
    """
    Send a message and get AI response with sources.
    """
    try:
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())
        
        # Get RAG response
        result = await rag.chat(request.message)
        
        # Extract entities from the response
        entities = []
        try:
            extracted = await extractor.extract_entities(result.get("response", ""))
            # Convert dictionary format to list format
            for entity_type, entity_list in extracted.items():
                if isinstance(entity_list, list):
                    for entity_value in entity_list:
                        entities.append({
                            "type": entity_type,
                            "value": entity_value,
                            "confidence": 1.0
                        })
                elif entity_list:  # For single values like gravity_condition, study_type
                    entities.append({
                        "type": entity_type,
                        "value": str(entity_list),
                        "confidence": 1.0
                    })
        except Exception as e:
            print(f"Entity extraction error: {e}")
        
        # Format sources
        sources = []
        for source in result.get("sources", [])[:10]:
            sources.append({
                "id": source.get("id", str(uuid.uuid4())),
                "title": source.get("title", "Unknown Title"),
                "authors": source.get("authors", "Unknown"),
                "score": source.get("score", 0.0),
                "url": source.get("url", ""),
                "type": source.get("type", "publication"),
                "abstract": source.get("abstract", "")
            })
        
        # Save to database
        try:
            db.add_message(
                session_id=session_id,
                role="user",
                content=request.message
            )
            db.add_message(
                session_id=session_id,
                role="assistant",
                content=result.get("response", ""),
                sources=sources
            )
        except Exception as e:
            print(f"Database save error: {e}")
        
        return ChatResponse(
            response=result.get("response", ""),
            sources=sources,
            entities=entities,
            session_id=session_id
        )
        
    except Exception as e:
        print(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/chat/session", response_model=SessionResponse)
async def create_session():
    """Create a new chat session."""
    session_id = str(uuid.uuid4())
    return SessionResponse(session_id=session_id)


@app.get("/api/chat/history/{session_id}")
async def get_chat_history(
    session_id: str,
    db: ChatDatabase = Depends(get_chat_db)
):
    """Get chat history for a session."""
    try:
        messages = db.get_session_messages(session_id)
        return {"messages": messages}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Search endpoints
@app.post("/api/search", response_model=List[SearchResult])
async def search(
    request: SearchRequest,
    rag: SpaceBiologyRAG = Depends(get_rag_system)
):
    """
    Perform semantic search across space biology resources.
    """
    try:
        results = await rag.search_similar_documents(
            query=request.query,
            top_k=request.limit,
            filters=request.filters or {}
        )
        
        search_results = []
        for result in results:
            metadata = result.metadata if hasattr(result, 'metadata') else result.get('metadata', {})
            
            search_results.append(SearchResult(
                id=metadata.get('id', str(uuid.uuid4())),
                title=metadata.get('title', 'Unknown'),
                content=result.page_content if hasattr(result, 'page_content') else result.get('content', ''),
                source_type=metadata.get('type', 'publication'),
                url=metadata.get('url', ''),
                score=result.score if hasattr(result, 'score') else result.get('score', 0.0),
                metadata=metadata
            ))
        
        return search_results
        
    except Exception as e:
        print(f"Search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/search/semantic")
async def semantic_search(
    query: str,
    top_k: int = 5,
    rag: SpaceBiologyRAG = Depends(get_rag_system)
):
    """Semantic similarity search."""
    try:
        results = await rag.search_similar_documents(query=query, top_k=top_k)
        
        return {
            "results": [
                {
                    "content": r.page_content if hasattr(r, 'page_content') else r.get('content', ''),
                    "metadata": r.metadata if hasattr(r, 'metadata') else r.get('metadata', {}),
                    "score": r.score if hasattr(r, 'score') else r.get('score', 0.0)
                }
                for r in results
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Entity extraction endpoint
@app.post("/api/entities/extract")
async def extract_entities(
    request: EntityExtractionRequest,
    extractor: BiologicalEntityExtractor = Depends(get_entity_extractor)
):
    """Extract biological entities from text."""
    try:
        entities = await extractor.extract_entities(request.text)
        return {"entities": entities}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Analytics endpoints
@app.get("/api/analytics/trends")
async def get_trends():
    """Get research trends data."""
    # Placeholder - implement based on your data
    return {
        "trends": [
            {"year": 2020, "count": 45, "category": "Bone Density"},
            {"year": 2021, "count": 52, "category": "Bone Density"},
            {"year": 2022, "count": 61, "category": "Bone Density"},
            {"year": 2023, "count": 73, "category": "Bone Density"},
            {"year": 2024, "count": 68, "category": "Bone Density"},
        ]
    }


@app.post("/api/analytics/missions")
async def get_mission_comparison(missions: List[str]):
    """Get mission comparison data."""
    # Placeholder - implement based on your data
    return {
        "missions": [
            {"mission": "ISS", "count": 345, "organisms": ["Mouse", "Human", "Plant"]},
            {"mission": "Apollo", "count": 67, "organisms": ["Human"]},
            {"mission": "Space Shuttle", "count": 123, "organisms": ["Mouse", "Plant"]},
        ]
    }


@app.get("/api/analytics/entities")
async def get_entity_distribution():
    """Get entity distribution data."""
    # Placeholder - implement based on your data
    return {
        "entities": [
            {"entity": "Mouse", "count": 234, "type": "organism"},
            {"entity": "Human", "count": 189, "type": "organism"},
            {"entity": "Bone", "count": 156, "type": "tissue"},
            {"entity": "Muscle", "count": 134, "type": "tissue"},
        ]
    }


if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Starting K-OSMOS API Server...")
    print("📍 API will be available at: http://localhost:8000")
    print("📚 API docs at: http://localhost:8000/docs")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
