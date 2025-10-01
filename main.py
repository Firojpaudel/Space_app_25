#!/usr/bin/env python3
"""
Main entry point for the Space Biology Knowledge Engine.
"""
import sys
import argparse
import asyncio
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Space Biology Knowledge Engine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Commands:
  init       Initialize databases and setup the system
  ingest     Ingest data from various sources
  dashboard  Launch the interactive dashboard
  search     Perform a search query
  health     Check system health

Examples:
  python main.py init
  python main.py ingest --csv-file data/publications.csv
  python main.py dashboard
  python main.py search "bone density microgravity"
        """
    )
    
    parser.add_argument(
        "command",
        choices=["init", "ingest", "dashboard", "search", "health"],
        help="Command to execute"
    )
    
    parser.add_argument("--csv-file", help="CSV file path for ingestion")
    parser.add_argument("--query", help="Search query")
    parser.add_argument("--port", type=int, default=8501, help="Dashboard port")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    
    args = parser.parse_args()
    
    if args.command == "init":
        asyncio.run(init_system())
    elif args.command == "ingest":
        asyncio.run(ingest_data(args.csv_file))
    elif args.command == "dashboard":
        launch_dashboard(args.port)
    elif args.command == "search":
        query = args.query or input("Enter search query: ")
        asyncio.run(perform_search(query))
    elif args.command == "health":
        asyncio.run(check_health())


async def init_system():
    """Initialize the system."""
    print("🚀 Initializing Space Biology Knowledge Engine...")
    
    try:
        from scripts.init_databases import main as init_main
        await init_main()
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please ensure all dependencies are installed: pip install -r requirements.txt")
    except Exception as e:
        print(f"❌ Initialization failed: {e}")


async def ingest_data(csv_file=None):
    """Ingest data into the system."""
    print("📥 Starting data ingestion...")
    
    try:
        from scripts.ingest_data import main as ingest_main
        
        # Mock the arguments for the ingest script
        sys.argv = ["ingest_data.py"]
        if csv_file:
            sys.argv.extend(["--csv-file", csv_file])
        
        await ingest_main()
    except ImportError as e:
        print(f"❌ Import error: {e}")
    except Exception as e:
        print(f"❌ Data ingestion failed: {e}")


def launch_dashboard(port=8501):
    """Launch the Streamlit dashboard."""
    print(f"🎛️ Launching dashboard on port {port}...")
    
    try:
        import subprocess
        import os
        
        dashboard_path = Path(__file__).parent / "dashboard" / "app.py"
        
        # Launch Streamlit
        cmd = [
            sys.executable, "-m", "streamlit", "run", 
            str(dashboard_path), 
            "--server.port", str(port),
            "--server.headless", "true"
        ]
        
        subprocess.run(cmd, cwd=str(project_root))
        
    except Exception as e:
        print(f"❌ Failed to launch dashboard: {e}")
        print("Try running manually: streamlit run dashboard/app.py")


async def perform_search(query):
    """Perform a search query using RAG system."""
    print(f"🔍 Searching for: {query}")
    
    try:
        from config.settings import Settings
        from rag_system.chat import SpaceBiologyRAG
        
        settings = Settings()
        rag_system = SpaceBiologyRAG(settings)
        
        print("⏳ Processing query...")
        result = await rag_system.chat(query)
        
        print("\n🤖 AI Response:")
        print("=" * 50)
        print(result["response"])
        
        if result.get("sources"):
            print("\n📚 Sources:")
            print("-" * 30)
            for i, source in enumerate(result["sources"][:5], 1):
                print(f"{i}. {source.get('title', 'Unknown Title')}")
                print(f"   Authors: {source.get('authors', 'Unknown')}")
                print(f"   Similarity: {source.get('score', '0.000')}")
                print()
        
        print("=" * 50)
        
    except Exception as e:
        print(f"❌ Search failed: {e}")
    print("Results would appear here...")


async def check_health():
    """Check system health."""
    print("🏥 Checking system health...")
    
    health_status = {
        "Vector Database": "❓ Unknown",
        "Knowledge Graph": "❓ Unknown", 
        "Embedding Service": "❓ Unknown",
        "Configuration": "❓ Unknown"
    }
    
    try:
        # Check configuration
        from config import settings
        health_status["Configuration"] = "✅ OK"
        
        # Check vector database
        try:
            if settings.vector_db_type.lower() == 'pinecone':
                from vector_db import PineconeDB
                config = {
                    'api_key': settings.pinecone_api_key,
                    'environment': settings.pinecone_environment,
                    'index_name': settings.pinecone_index_name,
                    'dimension': 768
                }
                vector_client = PineconeDB(config)
            else:
                from vector_db import WeaviateDB
                config = {
                    'url': settings.weaviate_url,
                    'api_key': settings.weaviate_api_key
                }
                vector_client = WeaviateDB(config)
            
            if await vector_client.health_check():
                health_status["Vector Database"] = "✅ OK"
            else:
                health_status["Vector Database"] = "❌ Failed"
        except Exception as e:
            health_status["Vector Database"] = f"❌ Error: {str(e)[:50]}"
        
        # Check knowledge graph
        try:
            from knowledge_graph import Neo4jClient
            config = {
                'uri': settings.neo4j_uri,
                'user': settings.neo4j_user,
                'password': settings.neo4j_password
            }
            neo4j_client = Neo4jClient(config)
            if await neo4j_client.health_check():
                health_status["Knowledge Graph"] = "✅ OK"
            else:
                health_status["Knowledge Graph"] = "❌ Failed"
        except Exception as e:
            health_status["Knowledge Graph"] = f"❌ Error: {str(e)[:50]}"
        
        # Check embedding service
        try:
            from rag_system import EmbeddingGenerator
            embedding_gen = EmbeddingGenerator()
            test_embedding = await embedding_gen.generate_embedding("test")
            if test_embedding and len(test_embedding) > 0:
                health_status["Embedding Service"] = "✅ OK"
            else:
                health_status["Embedding Service"] = "❌ Failed"
        except Exception as e:
            health_status["Embedding Service"] = f"❌ Error: {str(e)[:50]}"
            
    except Exception as e:
        print(f"❌ Health check error: {e}")
    
    # Print results
    print("\n📊 System Health Status:")
    print("=" * 50)
    for component, status in health_status.items():
        print(f"{component:<20}: {status}")
    print("=" * 50)


if __name__ == "__main__":
    main()