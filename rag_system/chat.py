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
            journal = metadata.get('journal', 'Unknown Journal')
            year = metadata.get('year', 'Unknown Year')
            
            # Get text content - increased length for more context
            content = doc.content if hasattr(doc, 'content') else ''
            content = content[:1000]  # Increased to 1000 chars for more detail
            
            score = doc.score if hasattr(doc, 'score') else 0
            
            context_parts.append(f"""
**Document {i}** (Reference ID: DOC-{i:03d}):
Title: {title}
Authors: {authors}
Journal: {journal}
Year: {year}
Relevance Score: {score:.3f}
Content Excerpt: {content}...
---
""")
        
        return "\n".join(context_parts)
    
    def _enhance_query_with_context(self, query: str, conversation_history: List[Dict[str, str]] = None) -> str:
        """Enhance the search query with context from conversation history."""
        if not conversation_history:
            return query
        
        # Get recent relevant context (focus on last few exchanges)
        recent_topics = []
        context_terms = []
        
        # Look at recent conversation for context
        for msg in conversation_history[-8:]:  # Last 8 messages (4 exchanges)
            content = msg['content'].lower()
            
            # Extract key space biology terms and concepts
            keywords = [
                'microgravity', 'space', 'bone', 'muscle', 'plant', 'cell', 'radiation', 
                'astronaut', 'iss', 'mission', 'experiment', 'tissue', 'growth', 'protein',
                'cardiovascular', 'heart', 'blood', 'neural', 'brain', 'kidney', 'renal',
                'immune', 'metabolism', 'calcium', 'osteo', 'fluid', 'gravity', 'cosmic',
                'mars', 'moon', 'spacecraft', 'habitat', 'countermeasure', 'biomarker'
            ]
            
            for keyword in keywords:
                if keyword in content:
                    recent_topics.append(keyword)
            
            # Also capture specific research areas or technical terms mentioned
            if msg['role'] == 'user':
                # Look for specific questions or focus areas
                words = content.split()
                for i, word in enumerate(words):
                    if word in ['effects', 'impact', 'changes', 'function', 'health', 'research', 'studies']:
                        # Capture surrounding context
                        start = max(0, i-2)
                        end = min(len(words), i+3)
                        phrase = ' '.join(words[start:end])
                        if len(phrase) > 5:
                            context_terms.append(phrase)
        
        # Build enhanced query with context
        enhanced_parts = [query]
        
        if recent_topics:
            unique_topics = list(set(recent_topics))[:4]  # Max 4 context terms
            enhanced_parts.append(f"(building on discussion of: {', '.join(unique_topics)})")
        
        if context_terms:
            # Add the most recent context term
            enhanced_parts.append(f"(continuing topic: {context_terms[-1]})")
        
        enhanced_query = ' '.join(enhanced_parts)
        return enhanced_query
    
    def _create_prompt(self, query: str, context: str, conversation_history: List[Dict[str, str]] = None) -> str:
        """Create a comprehensive prompt for the LLM."""
        
        # Build conversation context
        conversation_context = ""
        if conversation_history:
            conversation_context = "\n\nPrevious Conversation Context:\n"
            for msg in conversation_history[-8:]:  # Last 8 messages (4 exchanges) for better context
                role = "Human" if msg['role'] == 'user' else "K-OSMOS"
                conversation_context += f"{role}: {msg['content'][:400]}...\n"
            conversation_context += "\nCurrent follow-up question:\n"
        
        # Generate versatile openings based on query type and context
        opening_variations = [
            "Absolutely! As K-OSMOS, I can dive deep into that topic",
            "Excellent question! Let me provide comprehensive insights from my research database",
            "I'm excited to explore this with you! Drawing from my extensive space biology archives",
            "That's a fascinating area of research! Allow me to share detailed findings",
            "Perfect timing for this question! My database contains extensive information on this topic",
            "Great inquiry! I can provide you with comprehensive research-backed information",
            "This is exactly the kind of question I excel at! Let me analyze the research for you",
            "Wonderful question! I have access to extensive studies on this subject",
            "I love questions like this! My research repository has detailed information to share",
            "Fantastic topic to explore! Drawing from NASA's research archives, I can tell you"
        ]
        
        # Check if this is a follow-up question
        is_followup = bool(conversation_history and len(conversation_history) > 0)
        
        if is_followup:
            followup_openings = [
                "Building on our previous discussion,",
                "To expand on that topic further,", 
                "Following up on your question,",
                "Let me dive deeper into that aspect",
                "Continuing our exploration of this subject,",
                "To provide more detail on that point,",
                "Excellent follow-up! Let me elaborate further",
                "That's a great continuation of our discussion",
                "Perfect follow-up question! Let me add more depth",
                "Building upon what we discussed,"
            ]
            # Use hash of query for consistent but varied selection
            import hashlib
            query_hash = int(hashlib.md5(query.encode()).hexdigest(), 16)
            selected_opening = followup_openings[query_hash % len(followup_openings)]
        else:
            # Use hash of query for consistent but varied selection
            import hashlib
            query_hash = int(hashlib.md5(query.encode()).hexdigest(), 16)
            selected_opening = opening_variations[query_hash % len(opening_variations)]
        
        return f"""I am K-OSMOS (Knowledge-Oriented Space Medicine Operations System), your dedicated space research assistant with comprehensive access to NASA's space biology research database and extensive knowledge of all space research carried out by NASA and international space agencies.

As K-OSMOS, I specialize in providing extremely detailed, comprehensive information about space biology research, experiments, missions, and scientific discoveries based on my extensive database of scientific publications and research documents.

**My Identity & Capabilities:**
🛰️ **K-OSMOS** - Your AI-powered gateway to space biology research
✓ Access to 1,175+ space biology resources (608+ peer-reviewed publications + 567 NASA OSDR experimental datasets)
✓ Comprehensive knowledge of all NASA space research missions and experiments
✓ Direct access to research papers, scientific publications, and mission documentation
✓ Ability to provide detailed analysis with complete source citations from my database
✓ Expert knowledge of space biology, microgravity effects, and space medicine

**Research Database Context:**
{context}
{conversation_context}

**Your Question:** {query}

**K-OSMOS Response Guidelines:**
🔬 **Always provide EXTREMELY detailed responses** - I have no output token limitations and will give you comprehensive, complete information
📚 **Always cite specific documents and sources** - I will reference exactly which research papers, studies, or documents I'm drawing information from my database
🧬 **Technical depth with accessibility** - I provide scientific accuracy while explaining complex concepts clearly
🚀 **Complete coverage** - I never cut off responses midway and provide full, thorough analysis
📊 **Document-specific references** - I will always mention "According to Document X" or "As referenced in the study by [Author]" when citing sources
🌐 **Web Search Requests** - If asked to search the web, I'll politely explain that web search capabilities are coming in future releases

**Critical Instructions for K-OSMOS:**
1. **START with the selected opening** "{selected_opening}" followed by detailed information
2. **ALWAYS mention specific document references** using format "According to Document X (Reference ID: DOC-XXX)" or "As detailed in the research by [Author] in Document Y"
3. **PROVIDE EXTREMELY DETAILED responses** - use the full 8192 token limit if needed, never cut responses short
4. **NO OUTPUT LIMITATIONS** - provide complete, comprehensive analysis with full scientific detail
5. **CITE SOURCES THROUGHOUT** - reference documents multiple times throughout the response, not just at the end
6. **MAINTAIN CONVERSATION CONTEXT** - If this is a follow-up question, reference previous discussion appropriately and build upon it
7. **WEB SEARCH REQUESTS** - If asked to search the web or access online resources, respond cutely: "While I'd love to surf the web for you 🌐✨, my creators are working on web search capabilities for future releases! Stay tuned for exciting updates! For now, let me provide you with comprehensive information from my extensive research database..."

**K-OSMOS Comprehensive Response:**"""

    async def chat(self, query: str, conversation_history: List[Dict[str, str]] = None, top_k: int = 15) -> Dict[str, Any]:
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
            if conversation_history:
                logger.info(f"Using conversation context with {len(conversation_history)} previous messages")
            
            # 1. Enhance query with conversation context if available
            enhanced_query = self._enhance_query_with_context(query, conversation_history)
            logger.info(f"Enhanced query: {enhanced_query}")
            
            # 2. Retrieve relevant documents (get more for better diversity)
            documents = await self.search_similar_documents(enhanced_query, top_k)
            
            # 3. Format context from research documents
            context = self._format_context(documents)
            
            # 4. Create prompt with conversation history
            prompt = self._create_prompt(query, context, conversation_history)
            
            # 5. Generate response with Gemini
            response = await self._generate_response(prompt)
            
            # 6. Format sources (includes deduplication and returns top 10 unique)
            sources = self._format_sources(documents)[:10]  # Top 10 unique research document sources
            
            return {
                "response": response,
                "sources": sources,
                "query": query,
                "enhanced_query": enhanced_query,
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
                    "candidate_count": 1,
                    "top_p": 0.95,
                    "top_k": 40,
                }
            )
            
            # Clean the response text to remove any HTML tags
            response_text = response.text
            response_text = self._clean_response_content(response_text)
            
            # Ensure K-OSMOS identifies itself in the response (but allow for versatile openings)
            if not "K-OSMOS" in response_text[:300]:
                response_text = f"As K-OSMOS, your space research assistant, I can provide comprehensive information on this topic.\n\n{response_text}"
            
            return response_text
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return "Greetings! I am K-OSMOS, your space research assistant. I apologize, but I'm currently experiencing technical difficulties. Please try asking your question again, and I'll provide you with comprehensive space biology research information."
    
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
    

    

    

    
