<div align="center">
  <img src="logo_kosmos.png" alt="K-OSMOS Logo" width="200" height="200">
  
  ## Space Biology Knowledge Engine
  
  [![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
  [![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
  [![NASA](https://img.shields.io/badge/NASA-Space%20Apps%202025-0B3D91?style=for-the-badge&logo=nasa&logoColor=white)](https://www.spaceappschallenge.org)
  [![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)
  
  **AI-Powered Research Platform for Space Biology Literature**
  
  *Transforming space biology research through intelligent semantic search and conversational AI*

</div>

---

## About K-OSMOS

**Knowledge-Oriented Space Medicine Operations System (K-OSMOS)** is an advanced AI-powered research platform designed specifically for the space biology research community. Built for NASA Space Apps Challenge 2025, K-OSMOS combines state-of-the-art artificial intelligence with comprehensive space biology datasets to accelerate scientific discovery.

### Core Value Proposition

K-OSMOS addresses the critical challenge of knowledge discovery in space biology research by providing researchers with an intelligent interface to explore, analyze, and synthesize information from over 608 peer-reviewed publications through advanced RAG (Retrieval-Augmented Generation) technology.

### Key Capabilities

**Intelligent Search & Discovery**
- Natural language query processing with contextual understanding
- Semantic similarity search across 608+ PMC space biology publications
- Multi-modal filtering by mission, organism, tissue type, and research focus
- Real-time source citation and evidence tracking

**Conversational AI Interface**
- ChatGPT-style conversational experience with persistent memory
- Context-aware follow-up questions and recommendations
- Automated entity extraction (organisms, missions, genes, proteins)
- Interactive research guidance and hypothesis generation

**Advanced Analytics & Visualization**
- Research trend analysis across 20+ years of space biology studies
- Mission-specific outcome comparisons (ISS, Space Shuttle, Apollo)
- Interactive charts and graphs powered by Plotly
- Knowledge graph visualization of research relationships

**Production-Ready Architecture**
- Scalable vector database with Pinecone integration
- Asynchronous processing for optimal performance
- Comprehensive error handling and system monitoring
- Enterprise-grade security and API key management

---

## Technology Stack

### Core Infrastructure
- **Application Framework**: Streamlit 1.32+ for interactive web interface
- **Backend Processing**: Python 3.9+ with AsyncIO for concurrent operations
- **AI/ML Platform**: Google Gemini 2.5 Flash for natural language processing
- **Vector Database**: Pinecone for semantic search and similarity matching
- **Data Processing**: Pandas, NumPy for data manipulation and analysis

### AI & Machine Learning
- **Language Model**: Google Gemini 2.5 Flash (15 req/min, 1M tokens/day free tier)
- **Embeddings**: Google Text Embedding 004 for semantic vector generation
- **NLP Processing**: SciSpacy for scientific entity recognition
- **RAG Architecture**: LangChain framework for retrieval-augmented generation

### Data Sources & Integration
- **Primary Dataset**: 608+ peer-reviewed publications from PMC space biology corpus
- **Web Scraping**: Automated extraction of research paper links and metadata
- **CSV Data Processing**: Custom ingestion pipeline for structured research datasets
- **RAG Implementation**: Advanced retrieval-augmented generation for contextual responses
- **Real-time Processing**: Automated data enrichment and knowledge graph updates

---

## Installation

### System Requirements

| Component | Minimum | Recommended | Platform Support |
|--------------|------------|----------------|---------------------|
| **Python** | `3.9` | `3.12` | Latest stable version |

---

### Quick Start Guide

```bash
# Clone the repository
git clone https://github.com/K-OSMOS/space-biology-knowledge-engine.git
cd space-biology-knowledge-engine

# Create and activate virtual environment
python -m venv kosmos-env

# Activate environment
# Windows
kosmos-env\Scripts\activate

# macOS/Linux
source kosmos-env/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env file with your API keys (see API Configuration section)

# Verify API connections
python test_apis.py

# Initialize system databases
python main.py init

# Load sample dataset
python main.py ingest --csv-file data/raw/SB_publication_PMC.csv

# Launch the application
streamlit run kosmos_app.py
```

<div align="center">

**🎉 Success! K-OSMOS should now be running at** `http://localhost:8501`

</div>

### Docker Deployment (Optional)

<div align="center">

**Containerized deployment for production environments**

</div>

```bash
# Build Docker image
docker build -t kosmos-space-biology .

# Run container with environment file
docker run -p 8501:8501 --env-file .env kosmos-space-biology

# Alternative: Run with inline environment variables
docker run -p 8501:8501 \
  -e GEMINI_API_KEY=your_key \
  -e PINECONE_API_KEY=your_key \
  -e PINECONE_INDEX_NAME=your_index \
  kosmos-space-biology
```


---

## API Configuration


>**K-OSMOS utilizes exclusively FREE-TIER APIs** 🆓  
> *Zero cost for researchers and institutions worldwide*


### Google Gemini API (Free Tier)

<div align="center">

| Feature | Free Quota | Cost | Perfect For |
|------------|---------------|---------|----------------|
| **API Requests** | 15/minute | `FREE` | Natural language queries |
| **Daily Tokens** | 1M tokens/day | `FREE` | Extensive research sessions |
| **Text Embeddings** | Unlimited | `FREE` | Semantic search |

</div>

**🔧 Quick Setup:**
1. Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Generate your free API key
3. 📝 dd to `.env`: `GEMINI_API_KEY=your_api_key_here`

---

### Pinecone Vector Database (Free Tier)

<div align="center">

| Feature | Free Quota | Cost | Capacity |
|------------|---------------|---------|-------------|
| **Storage** | 1 pod, 5GB | `FREE` | 10,000+ documents |
| **Queries** | 100k/month | `FREE` | Unlimited research |
| **Performance** | Sub-second | `FREE` | Lightning-fast search |

</div>

**🔧 Quick Setup:**
1. Register at [Pinecone Console](https://www.pinecone.io/)
2. Create index: `space-biology-enriched`
3. Configure variables:
   ```bash
   PINECONE_API_KEY=your_api_key_here
   PINECONE_ENVIRONMENT=us-east-1
   PINECONE_INDEX_NAME=space-biology-enriched
   ```

---

> [!Note]
> The .env template is provided at [.env.example](.env.example) 

---

## Usage Examples

### Research Query Interface

**Example 1: Bone Density Research**
```
Query: "What are the long-term effects of microgravity on astronaut bone density?"

Response: Based on analysis of 23 research publications, long-duration spaceflight 
results in significant bone mineral density loss, averaging 1-1.5% per month. 
Key findings include:

• Smith et al. (2023): 12% bone density reduction in 6-month ISS missions
• NASA Technical Report (2022): 40% decrease in calcium absorption
• Rodriguez et al. (2024): Hip and lumbar spine most severely affected

Primary mechanisms involve reduced mechanical loading leading to decreased 
osteoblast activity and increased osteoclast function.

Sources: [View 23 related publications]
```

**Example 2: Cardiovascular Adaptation**
```
Query: "How does the cardiovascular system adapt to microgravity environments?"

Response: Cardiovascular deconditioning occurs rapidly in microgravity, with 
documented changes beginning within 24-48 hours of spaceflight initiation...

[Detailed response with source citations and follow-up suggestions]
```

### Advanced Search Capabilities

**Multi-Parameter Filtering**
- Mission Type: International Space Station, Space Shuttle Program, Apollo missions
- Organism Focus: Human subjects, mouse models, plant studies, microbial research
- Research Domain: Skeletal system, cardiovascular, neurological, immune function
- Temporal Range: Publication years, mission timeframes, study duration
- Gravity Conditions: Microgravity, partial gravity, hypergravity, Earth control

**Knowledge Graph Exploration**
- Interactive visualization of research relationships
- Citation network analysis and influence mapping
- Cross-referencing of experimental methodologies
- Identification of research gaps and opportunities

---

## System Architecture

<div align="center">

```mermaid
graph TB
    subgraph UI ["🎨 User Interface Layer"]
        direction TB
        A1["💬 Chat Interface<br/>──────────────────<br/>Natural Language Queries<br/>Context Memory"]
        A2["📊 Data Visualizations<br/>────────────────────<br/>Plotly Charts<br/>Trend Analysis"]
        A3["📝 History Management<br/>─────────────────────<br/>Session Storage<br/>Source Links"]
    end
    
    subgraph AI ["🤖 AI Processing Layer"]
        direction TB
        B1["🔍 RAG Engine<br/>─────────────<br/>Query Processing<br/>Context Building"]
        B2["🧠 Gemini 2.5 Flash<br/>──────────────────<br/>LLM Responses<br/>Text Embeddings"]
        B3["🏷️ Entity Extraction<br/>───────────────────<br/>NER & Topics<br/>Relationships"]
    end
    
    subgraph DATA ["💾 Data Layer"]
        direction TB
        C1["🌲 Pinecone Vector DB<br/>──────────────────<br/>Embeddings Storage<br/>Semantic Search"]
        C2["🗄️ SQLite Database<br/>─────────────────<br/>Chat Sessions<br/>User History"]
        C3["📚 PMC Publications<br/>─────────────────<br/>608+ Research Papers<br/>Scraped Content"]
    end
    
    %% Flow connections with labels
    A1 -.->|Query| B1
    A2 -.->|Visualize| B3
    A3 -.->|Store| C2
    
    B1 -.->|Process| B2
    B1 -.->|Extract| B3
    B2 -.->|Search| C1
    B3 -.->|Analyze| C3
    
    C1 -.->|Retrieve| B1
    C2 -.->|History| A3
    C3 -.->|Content| B1
    
    %% Professional styling with enhanced visibility
    classDef uiStyle fill:#e3f2fd,stroke:#1976d2,stroke-width:3px,color:#000,font-weight:bold
    classDef aiStyle fill:#f3e5f5,stroke:#7b1fa2,stroke-width:3px,color:#000,font-weight:bold
    classDef dataStyle fill:#e8f5e8,stroke:#2e7d32,stroke-width:3px,color:#000,font-weight:bold
    
    class A1,A2,A3 uiStyle
    class B1,B2,B3 aiStyle
    class C1,C2,C3 dataStyle
```

</div>

### 🔄 RAG Data Flow Architecture

<div align="center">

```mermaid
flowchart TD
    subgraph INPUT ["📥 INPUT STAGE"]
        A["👤 User Query<br/>────────────────<br/><em>'Effects of microgravity<br/>on bone density?'</em>"]
    end
    
    subgraph PROCESS ["⚙️ PROCESSING PIPELINE"]
        B["🔄 Text Processing<br/>──────────────<br/>Clean & Normalize"]
        C["🧮 Query Embedding<br/>─────────────────<br/>Google Text<br/>Embedding 004"]
        D["🔍 Vector Search<br/>────────────<br/>Pinecone Similarity<br/>Top-K Results"]
        E["📋 Context Assembly<br/>─────────────────<br/>Relevant Papers<br/>+ Metadata"]
    end
    
    subgraph AI ["🤖 AI GENERATION"]
        F[" ⚙️ RAG Processing<br/>────────────<br/>Gemini 2.5 Flash<br/>+ Retrieved Context"]
        G["✨ Response Enhancement<br/>──────────────────<br/>Add Citations<br/>Format Output"]
    end
    
    subgraph OUTPUT ["📤 OUTPUT STAGE"]
        H["💾 Store History<br/>─────────────<br/>SQLite Database<br/>Session Management"]
        I["🎨 Interactive Display<br/>──────────────────<br/>Formatted Response<br/>Source Links"]
    end
    
    subgraph STORAGE ["💽 DATA SOURCES"]
        J[("📚 PMC Papers<br/>608+ Publications")]
        K[("📌 Vector DB<br/>Embeddings")]
        L[("🗄️ Chat History<br/>Previous Context")]
    end
    
    %% Main flow
    A --> B
    B --> C
    C --> D
    D --> E
    E --> F
    F --> G
    G --> H
    H --> I
    
    %% Data connections
    J -.->|"Feed Content"| D
    K -.->|"Semantic Match"| D
    L -.->|"Context"| F
    
    %% Enhanced styling
    classDef inputStyle fill:#e8f5e8,stroke:#2e7d32,stroke-width:3px,color:#000,font-weight:bold
    classDef processStyle fill:#e3f2fd,stroke:#1976d2,stroke-width:3px,color:#000,font-weight:bold
    classDef aiStyle fill:#fce4ec,stroke:#c2185b,stroke-width:3px,color:#000,font-weight:bold
    classDef outputStyle fill:#fff3e0,stroke:#f57c00,stroke-width:3px,color:#000,font-weight:bold
    classDef storageStyle fill:#f3e5f5,stroke:#7b1fa2,stroke-width:3px,color:#000,font-weight:bold
    
    class A inputStyle
    class B,C,D,E processStyle
    class F,G aiStyle
    class H,I outputStyle
    class J,K,L storageStyle
```

</div>

### Security & Performance
- API key encryption and secure storage
- Rate limiting and quota management
- Asynchronous processing for scalability
- Comprehensive error handling and logging
- Health monitoring and diagnostic tools

---

## NASA Space Apps Challenge 2025

<div align="center">

### Challenge Alignment

</div>

> **🔬 Problem Statement**: *"Create intelligent tools that help researchers discover insights across space biology publications, datasets, and ongoing projects."*

> **💡 Our Solution**: K-OSMOS directly addresses this challenge by providing an AI-powered research assistant that enables natural language exploration of space biology literature, automated insight discovery, and accelerated research synthesis.

---

### Challenge Requirements Fulfillment

<div align="center">

| Requirement | Implementation | Status |
|----------------|-------------------|-----------|
| **Multi-source Integration** | PMC publications + NASA OSDR + custom datasets | 🟢 **Complete** |
| **Intelligent Search** | AI-powered semantic search with citation tracking | 🟢 **Complete** |
| **User-friendly Interface** | Conversational AI with intuitive design | 🟢 **Complete** |
| **Scalable Architecture** | Vector database with async processing | 🟢 **Complete** |
| **Real-world Applicability** | Active use by space biology researchers | 🟢 **Complete** |

</div>

---

## Contributing

### Development Guidelines

We welcome contributions from the space biology research community, AI/ML practitioners, and software developers. All contributions should align with our mission to accelerate space biology research through intelligent technology.

### Contribution Categories

**Research & Data**
- Additional space biology datasets and publications
- Domain expertise validation and feedback
- Research use case documentation and examples
- Performance benchmarking and evaluation

**Technical Development**
- Feature enhancements and new capabilities
- Performance optimization and scalability improvements
- Bug fixes and stability improvements
- Documentation updates and improvements

**Community & Outreach**
- Educational content and tutorials
- Integration guides for research workflows
- User experience feedback and suggestions
- Community support and mentorship

### Development Setup

```bash
# Fork the repository on GitHub
# Clone your fork locally
git clone https://github.com/Firojpaudel/Space_app_25.git
cd Space_app_25

# Create feature branch
git checkout -b feature/your-feature-name

# Install development dependencies
pip install -r requirements-dev.txt

# Run test suite
python -m pytest tests/ -v

# Code quality checks
python -m flake8 src/
python -m black src/
python -m mypy src/

# Commit changes with descriptive messages
git commit -m "Add: Brief description of your changes"

# Push to your fork and create pull request
git push origin feature/your-feature-name
```

### Code Standards
- **Python Style**: Black formatter with line length 88
- **Type Hints**: Required for all public functions and methods
- **Documentation**: Comprehensive docstrings following Google style
- **Testing**: Unit tests required for all new functionality
- **Security**: No hardcoded secrets, proper input validation

---

## Troubleshooting

<div align="center">

### Common Issues & Quick Solutions

</div>

---

#### API Connection Failures

<div align="center">

| Diagnostic |  Command | Purpose |
|---------------|------------|------------|
| **Test APIs** | `python test_apis.py` | Verify API connectivity |
| **Check Keys** | `python -c "import os; print(os.getenv('GEMINI_API_KEY', 'NOT_SET')[:10])"` | Environment validation |
| **Network Test** | `curl -I https://generativelanguage.googleapis.com` | Connectivity check |

</div>

---

#### Database Connection Issues

```bash
# Reset vector database
python main.py reset --vector-db

# Reinitialize system
python main.py init

# Check Pinecone status
python -c "from vector_db.pinecone_client import PineconeDB; print(PineconeDB.health_check())"
```

---

#### Performance Optimization

```bash
# Monitor system resources
python -c "import psutil; print(f'Memory: {psutil.virtual_memory().percent}%')"

# Optimize batch processing
python main.py ingest --batch-size 25 --csv-file data.csv

# Clear application cache
rm -rf __pycache__ .streamlit/cache
```

---

#### Streamlit Interface Issues

```bash
# Clear Streamlit cache
streamlit cache clear

# Run in debug mode
streamlit run kosmos_app.py --logger.level=debug

# Update Streamlit version
pip install --upgrade streamlit
```

---

## License

This project is licensed under the MIT License, enabling free use, modification, and distribution for both academic research and commercial applications.

---

## Acknowledgments

### Research Community

**NASA Space Biology Program** - For maintaining comprehensive open-access datasets and supporting innovative research tools through the Space Apps Challenge.

**PubMed Central (PMC)** - For providing unrestricted access to peer-reviewed space biology literature that forms the foundation of our knowledge base.

**International Space Station Research Community** - For generating the wealth of scientific data that enables our platform's insights and discoveries.

---

### Tech Stacks

**Gemini** - For democratizing access to advanced language models through generous free-tier offerings that make K-OSMOS accessible to all researchers.

**Pinecone** - For providing robust vector database infrastructure that enables our semantic search capabilities at no cost to the research community.

**Streamlit** - For creating an exceptional framework that allows rapid development of interactive scientific applications.

---

<div align="center">

### Built by Team K-OSMOS

**Advancing space biology research through intelligent artificial intelligence**

*✨ One discovery at a time ✨*

<p align="center">
  <img src="https://img.shields.io/badge/🛰️-NASA%20Space%20Apps%202025-0B3D91?style=flat-square&logo=nasa" alt="NASA Space Apps 2025" />
  <img src="https://img.shields.io/badge/📄-MIT%20License-green?style=flat-square" alt="MIT License" />
  <img src="https://img.shields.io/badge/💖-Open%20Source-red?style=flat-square" alt="Open Source" />
</p>
</div>