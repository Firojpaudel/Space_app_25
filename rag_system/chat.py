"""
RAG (Retrieval-Augmented Generation) system for Space Biology Knowledge Engine.
Uses Gemini for LLM and Pinecone for vector search.
"""
import logging
from typing import List, Dict, Any, Optional, Tuple
import asyncio

import google.generativeai as genai
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
 
from config.settings import Settings
from vector_db.pinecone_client import PineconeDB
from rag_system.embeddings import EmbeddingGenerator

logger = logging.getLogger(__name__)


class SpaceBiologyRAG:
    """RAG system for space biology research queries."""
    
    def __init__(self, settings: Settings):
        """Initialize the RAG system."""
        self.settings = settings
        self.vector_db = PineconeDB(settings)
        self.embedder = EmbeddingGenerator(settings)
        
        # Configure Gemini
        genai.configure(api_key=settings.gemini_api_key)
        self.model = genai.GenerativeModel(settings.llm_model)
        
        logger.info("Initialized Space Biology RAG system")
    
    async def search_similar_documents(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar documents using vector similarity."""
        try:
            # Generate query embedding
            query_embedding = await self.embedder.generate_embedding(query)
            if not query_embedding:
                return []
            
            # Search vector database (use default namespace where data is stored)
            results = await self.vector_db.search(
                collection="",  # Default namespace where the data was uploaded
                query_vector=query_embedding,
                limit=top_k
            )
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            return []
    
    def _format_context(self, documents) -> str:
        """Format retrieved documents as context for the LLM."""
        if not documents:
            return "No relevant documents found."
        
        context_parts = []
        for i, doc in enumerate(documents, 1):
            # Handle SearchResult objects
            metadata = doc.metadata if hasattr(doc, 'metadata') else {}
            title = metadata.get('title', 'Unknown Title')
            authors = metadata.get('authors', 'Unknown Authors')
            
            # Get text content
            content = doc.content if hasattr(doc, 'content') else ''
            content = content[:500]  # Limit to 500 chars
            
            score = doc.score if hasattr(doc, 'score') else 0
            
            context_parts.append(f"""
Document {i}:
Title: {title}
Authors: {authors}
Content: {content}...
Score: {score:.3f}
""")
        
        return "\n".join(context_parts)
    
    def _enhance_query_with_context(self, query: str, conversation_history: List[Dict[str, str]] = None) -> str:
        """Enhance the search query with context from conversation history."""
        if not conversation_history:
            return query
        
        # Get recent relevant context (last 2-3 user messages)
        recent_topics = []
        for msg in conversation_history[-6:]:  # Last 6 messages
            if msg['role'] == 'user':
                # Extract key terms from previous questions
                content = msg['content'].lower()
                # Look for space biology terms
                terms = []
                keywords = ['microgravity', 'space', 'bone', 'muscle', 'plant', 'cell', 'radiation', 
                           'astronaut', 'iss', 'mission', 'experiment', 'tissue', 'growth', 'protein']
                for keyword in keywords:
                    if keyword in content:
                        terms.append(keyword)
                if terms:
                    recent_topics.extend(terms)
        
        # Enhance query with context if we found relevant terms
        if recent_topics:
            unique_topics = list(set(recent_topics))[:3]  # Max 3 context terms
            enhanced_query = f"{query} (related to: {', '.join(unique_topics)})"
            return enhanced_query
        
        return query
    
    def _create_prompt(self, query: str, context: str, conversation_history: List[Dict[str, str]] = None) -> str:
        """Create a comprehensive prompt for the LLM."""
        
        # Build conversation context
        conversation_context = ""
        if conversation_history:
            conversation_context = "\n\nPrevious Conversation:\n"
            for msg in conversation_history[-6:]:  # Last 6 messages (3 exchanges)
                role = "Human" if msg['role'] == 'user' else "Assistant"
                conversation_context += f"{role}: {msg['content'][:300]}...\n"
            conversation_context += "\n"
        
        return f"""You are a space biology research assistant with access to a database of scientific publications. Answer the user's question using the provided research context and considering the conversation history.

Context from Space Biology Research Papers:
{context}
{conversation_context}
Current User Question: {query}

Instructions:
- Provide a comprehensive answer based on the research context
- Consider the conversation history to maintain context and provide follow-up information
- If referring to previous topics, acknowledge them naturally
- Cite specific papers when referencing information
- If the context doesn't contain relevant information, say so clearly
- Focus on scientific accuracy and space biology research
- Mention specific organisms, experiments, or missions when available
- Use technical terms appropriately but explain complex concepts

Answer:"""

    async def chat(self, query: str, conversation_history: List[Dict[str, str]] = None, top_k: int = 10) -> Dict[str, Any]:
        """
        Main chat function that retrieves relevant documents and generates response.
        
        Args:
            query: User's question
            conversation_history: Previous messages for context
            top_k: Number of documents to retrieve (increased for better diversity before deduplication)
            
        Returns:
            Dict containing response, sources, and metadata
        """
        try:
            logger.info(f"Processing RAG query: {query}")
            
            # 1. Enhance query with conversation context if available
            enhanced_query = self._enhance_query_with_context(query, conversation_history)
            
            # 2. Retrieve relevant documents (get more for better diversity)
            documents = await self.search_similar_documents(enhanced_query, top_k)
            
            # 3. Format context (will be deduplicated in _format_sources)
            context = self._format_context(documents)
            
            # 4. Create prompt with conversation history
            prompt = self._create_prompt(query, context, conversation_history)
            
            # 5. Generate response with Gemini
            response = await self._generate_response(prompt)
            
            # 6. Format sources (includes deduplication and returns top 5 unique)
            sources = self._format_sources(documents)[:5]  # Limit to 5 unique sources for display
            
            return {
                "response": response,
                "sources": sources,
                "query": query,
                "num_sources": len(sources),
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Error in RAG chat: {e}")
            return {
                "response": f"I apologize, but I encountered an error while processing your question: {str(e)}",
                "sources": [],
                "query": query,
                "num_sources": 0,
                "success": False
            }
    
    async def _generate_response(self, prompt: str) -> str:
        """Generate response using Gemini with rate limiting."""
        try:
            # Add small delay for rate limiting
            await asyncio.sleep(1)
            
            response = self.model.generate_content(
                prompt,
                generation_config={
                    "temperature": self.settings.temperature,
                    "max_output_tokens": self.settings.max_tokens,
                }
            )
            
            # Clean the response text to remove any HTML tags
            response_text = response.text
            response_text = self._clean_response_content(response_text)
            
            return response_text
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return "I apologize, but I'm currently unable to generate a response. Please try again."
    
    def _clean_response_content(self, content: str) -> str:
        """Clean response content to remove HTML tags and unwanted elements."""
        import re
        
        if not content:
            return content
        
        # Remove HTML tags (including div, span, etc.)
        content = re.sub(r'<[^>]+>', '', content)
        
        # Remove stray closing tags that might appear as text
        content = re.sub(r'</?\w+>', '', content)
        
        # Remove multiple consecutive newlines
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        # Remove leading/trailing whitespace
        content = content.strip()
        
        return content
    
    def _format_sources(self, documents) -> List[Dict[str, Any]]:
        """Format document sources for display with deduplication."""
        sources = []
        seen_titles = set()
        
        for doc in documents:
            # Handle SearchResult objects
            metadata = doc.metadata if hasattr(doc, 'metadata') else {}
            score = doc.score if hasattr(doc, 'score') else 0
            
            title = metadata.get('title', 'Unknown Title')
            
            # Skip duplicates (case-insensitive comparison)
            title_lower = title.lower().strip()
            if title_lower in seen_titles or title_lower == 'unknown title':
                continue
            seen_titles.add(title_lower)
            
            # Handle authors - could be a list or string
            authors = metadata.get('authors', 'Unknown Authors')
            if isinstance(authors, list):
                authors = ', '.join(authors) if authors else 'Unknown Authors'
            
            source = {
                "title": title,
                "authors": authors, 
                "journal": metadata.get('journal', 'Unknown Journal'),
                "year": metadata.get('year', 'Unknown Year'),
                "url": metadata.get('url', metadata.get('link', '')),  # Try both url and link
                "score": score  # Keep as float for percentage calculation
            }
            sources.append(source)
        
        # Sort by score (highest first) to ensure best matches come first
        sources.sort(key=lambda x: x.get('score', 0), reverse=True)
        
        return sources
    
    async def get_research_summary(self, topic: str) -> Dict[str, Any]:
        """Get a research summary for a specific topic."""
        query = f"Summarize current research on {topic} in space biology"
        return await self.chat(query, top_k=10)
    
    async def compare_studies(self, study1: str, study2: str) -> Dict[str, Any]:
        """Compare two research areas or studies."""
        query = f"Compare research on {study1} versus {study2} in space biology"
        return await self.chat(query, top_k=8)
    
    async def get_mission_studies(self, mission: str) -> Dict[str, Any]:
        """Get studies related to a specific space mission."""
        query = f"What research was conducted during or related to the {mission} mission?"
        return await self.chat(query, top_k=7)