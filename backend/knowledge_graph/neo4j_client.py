"""
Neo4j knowledge graph client for the Space Biology Knowledge Engine.
"""
import asyncio
from typing import List, Dict, Any, Optional, Tuple
import logging

try:
    from neo4j import AsyncGraphDatabase
    NEO4J_AVAILABLE = True
except ImportError:
    AsyncGraphDatabase = None
    NEO4J_AVAILABLE = False

from models.schemas import Publication, Dataset, TaskBookProject
from config import DatabaseConfig

logger = logging.getLogger(__name__)


class Neo4jClient:
    """Neo4j client for knowledge graph operations."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize Neo4j client."""
        if not NEO4J_AVAILABLE:
            raise ImportError("Neo4j driver not available. Install with: pip install neo4j")
        
        self.uri = config.get('uri')
        self.user = config.get('user')
        self.password = config.get('password')
        self.driver = None
        self.logger = logger.getChild("Neo4jClient")
        
        self._initialize_driver()
    
    def _initialize_driver(self):
        """Initialize Neo4j driver."""
        try:
            self.driver = AsyncGraphDatabase.driver(
                self.uri,
                auth=(self.user, self.password)
            )
            self.logger.info(f"Initialized Neo4j driver for {self.uri}")
        except Exception as e:
            self.logger.error(f"Failed to initialize Neo4j driver: {e}")
            raise
    
    async def health_check(self) -> bool:
        """Check if Neo4j is healthy."""
        try:
            async with self.driver.session() as session:
                result = await session.run("RETURN 1 as test")
                record = await result.single()
                return record['test'] == 1
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return False
    
    async def setup_schema(self) -> bool:
        """Setup Neo4j schema with constraints and indexes."""
        try:
            async with self.driver.session() as session:
                # Create constraints for unique IDs
                constraints = [
                    f"CREATE CONSTRAINT IF NOT EXISTS FOR (p:{DatabaseConfig.PUBLICATION_LABEL}) REQUIRE p.id IS UNIQUE",
                    f"CREATE CONSTRAINT IF NOT EXISTS FOR (d:{DatabaseConfig.DATASET_LABEL}) REQUIRE d.id IS UNIQUE", 
                    f"CREATE CONSTRAINT IF NOT EXISTS FOR (pr:{DatabaseConfig.PROJECT_LABEL}) REQUIRE pr.id IS UNIQUE",
                    f"CREATE CONSTRAINT IF NOT EXISTS FOR (o:{DatabaseConfig.ORGANISM_LABEL}) REQUIRE o.name IS UNIQUE",
                    f"CREATE CONSTRAINT IF NOT EXISTS FOR (t:{DatabaseConfig.TISSUE_LABEL}) REQUIRE t.name IS UNIQUE",
                    f"CREATE CONSTRAINT IF NOT EXISTS FOR (m:{DatabaseConfig.MISSION_LABEL}) REQUIRE m.name IS UNIQUE"
                ]
                
                for constraint in constraints:
                    await session.run(constraint)
                
                # Create indexes for common search fields
                indexes = [
                    f"CREATE INDEX IF NOT EXISTS FOR (p:{DatabaseConfig.PUBLICATION_LABEL}) ON (p.title)",
                    f"CREATE INDEX IF NOT EXISTS FOR (d:{DatabaseConfig.DATASET_LABEL}) ON (d.title)",
                    f"CREATE INDEX IF NOT EXISTS FOR (pr:{DatabaseConfig.PROJECT_LABEL}) ON (pr.title)",
                    f"CREATE INDEX IF NOT EXISTS FOR (p:{DatabaseConfig.PUBLICATION_LABEL}) ON (p.publication_date)"
                ]
                
                for index in indexes:
                    await session.run(index)
                
                self.logger.info("Schema setup completed")
                return True
                
        except Exception as e:
            self.logger.error(f"Error setting up schema: {e}")
            return False
    
    async def create_publication(self, publication: Publication) -> bool:
        """Create publication node in knowledge graph."""
        try:
            async with self.driver.session() as session:
                query = f"""
                CREATE (p:{DatabaseConfig.PUBLICATION_LABEL} {{
                    id: $id,
                    title: $title,
                    abstract: $abstract,
                    authors: $authors,
                    journal: $journal,
                    publication_date: $publication_date,
                    doi: $doi,
                    url: $url,
                    keywords: $keywords,
                    citation_count: $citation_count
                }})
                RETURN p
                """
                
                await session.run(query, 
                    id=publication.id,
                    title=publication.title,
                    abstract=publication.abstract,
                    authors=publication.authors,
                    journal=publication.journal,
                    publication_date=publication.publication_date,
                    doi=publication.doi,
                    url=str(publication.url) if publication.url else None,
                    keywords=publication.keywords,
                    citation_count=publication.citation_count
                )
                
                return True
                
        except Exception as e:
            self.logger.error(f"Error creating publication {publication.id}: {e}")
            return False
    
    async def create_dataset(self, dataset: Dataset) -> bool:
        """Create dataset node in knowledge graph."""
        try:
            async with self.driver.session() as session:
                query = f"""
                CREATE (d:{DatabaseConfig.DATASET_LABEL} {{
                    id: $id,
                    title: $title,
                    description: $description,
                    organism: $organism,
                    tissue: $tissue,
                    mission: $mission,
                    experiment_type: $experiment_type,
                    measurement_type: $measurement_type,
                    file_count: $file_count,
                    publication_date: $publication_date,
                    url: $url,
                    keywords: $keywords
                }})
                RETURN d
                """
                
                await session.run(query,
                    id=dataset.id,
                    title=dataset.title,
                    description=dataset.description,
                    organism=dataset.organism,
                    tissue=dataset.tissue,
                    mission=dataset.mission,
                    experiment_type=dataset.experiment_type,
                    measurement_type=dataset.measurement_type,
                    file_count=dataset.file_count,
                    publication_date=dataset.publication_date,
                    url=str(dataset.url) if dataset.url else None,
                    keywords=dataset.keywords
                )
                
                return True
                
        except Exception as e:
            self.logger.error(f"Error creating dataset {dataset.id}: {e}")
            return False
    
    async def batch_create_publications(self, publications: List[Publication]) -> int:
        """Batch create publication nodes."""
        created_count = 0
        
        try:
            async with self.driver.session() as session:
                for pub in publications:
                    success = await self.create_publication(pub)
                    if success:
                        created_count += 1
                        
                        # Create entity relationships
                        await self._create_publication_entities(session, pub)
                
                self.logger.info(f"Created {created_count} publication nodes")
                return created_count
                
        except Exception as e:
            self.logger.error(f"Error in batch publication creation: {e}")
            return created_count
    
    async def batch_create_datasets(self, datasets: List[Dataset]) -> int:
        """Batch create dataset nodes."""
        created_count = 0
        
        try:
            async with self.driver.session() as session:
                for dataset in datasets:
                    success = await self.create_dataset(dataset)
                    if success:
                        created_count += 1
                        
                        # Create entity relationships
                        await self._create_dataset_entities(session, dataset)
                
                self.logger.info(f"Created {created_count} dataset nodes")
                return created_count
                
        except Exception as e:
            self.logger.error(f"Error in batch dataset creation: {e}")
            return created_count
    
    async def _create_publication_entities(self, session, publication: Publication):
        """Create entity nodes and relationships for publication."""
        # Create organism nodes and relationships
        for organism in publication.organisms:
            await self._create_entity_relationship(
                session, 
                publication.id, 
                DatabaseConfig.PUBLICATION_LABEL,
                organism, 
                DatabaseConfig.ORGANISM_LABEL,
                DatabaseConfig.STUDIES_REL
            )
        
        # Create tissue nodes and relationships
        for tissue in publication.tissues:
            await self._create_entity_relationship(
                session,
                publication.id,
                DatabaseConfig.PUBLICATION_LABEL, 
                tissue,
                DatabaseConfig.TISSUE_LABEL,
                DatabaseConfig.STUDIES_REL
            )
        
        # Create mission nodes and relationships
        for mission in publication.missions:
            await self._create_entity_relationship(
                session,
                publication.id,
                DatabaseConfig.PUBLICATION_LABEL,
                mission,
                DatabaseConfig.MISSION_LABEL,
                DatabaseConfig.RELATES_TO_REL
            )
    
    async def _create_dataset_entities(self, session, dataset: Dataset):
        """Create entity nodes and relationships for dataset."""
        # Create organism relationship
        if dataset.organism:
            await self._create_entity_relationship(
                session,
                dataset.id,
                DatabaseConfig.DATASET_LABEL,
                dataset.organism,
                DatabaseConfig.ORGANISM_LABEL,
                DatabaseConfig.USES_REL
            )
        
        # Create tissue relationship
        if dataset.tissue:
            await self._create_entity_relationship(
                session,
                dataset.id,
                DatabaseConfig.DATASET_LABEL,
                dataset.tissue,
                DatabaseConfig.TISSUE_LABEL,
                DatabaseConfig.USES_REL
            )
        
        # Create mission relationship
        if dataset.mission:
            await self._create_entity_relationship(
                session,
                dataset.id,
                DatabaseConfig.DATASET_LABEL,
                dataset.mission,
                DatabaseConfig.MISSION_LABEL,
                DatabaseConfig.CONDUCTED_ON_REL
            )
    
    async def _create_entity_relationship(
        self, 
        session, 
        source_id: str, 
        source_label: str,
        entity_name: str, 
        entity_label: str, 
        relationship_type: str
    ):
        """Create entity node and relationship."""
        try:
            query = f"""
            MERGE (e:{entity_label} {{name: $entity_name}})
            WITH e
            MATCH (s:{source_label} {{id: $source_id}})
            MERGE (s)-[r:{relationship_type}]->(e)
            RETURN e, r
            """
            
            await session.run(query,
                entity_name=entity_name,
                source_id=source_id
            )
            
        except Exception as e:
            self.logger.error(f"Error creating entity relationship: {e}")
    
    async def create_relationships(
        self, 
        publications: List[Publication],
        datasets: List[Dataset], 
        projects: List[TaskBookProject]
    ):
        """Create relationships between different entity types."""
        try:
            async with self.driver.session() as session:
                # Create publication-dataset relationships based on shared entities
                await self._link_publications_datasets(session, publications, datasets)
                
                self.logger.info("Created cross-entity relationships")
                
        except Exception as e:
            self.logger.error(f"Error creating relationships: {e}")
    
    async def _link_publications_datasets(self, session, publications: List[Publication], datasets: List[Dataset]):
        """Link publications and datasets based on shared entities."""
        for pub in publications:
            for dataset in datasets:
                # Check for shared organisms
                shared_organisms = set(pub.organisms) & {dataset.organism} if dataset.organism else set()
                
                # Check for shared tissues
                shared_tissues = set(pub.tissues) & {dataset.tissue} if dataset.tissue else set()
                
                # Create relationship if there are shared entities
                if shared_organisms or shared_tissues:
                    query = f"""
                    MATCH (p:{DatabaseConfig.PUBLICATION_LABEL} {{id: $pub_id}})
                    MATCH (d:{DatabaseConfig.DATASET_LABEL} {{id: $dataset_id}})
                    MERGE (p)-[r:{DatabaseConfig.RELATES_TO_REL}]->(d)
                    SET r.shared_organisms = $shared_organisms,
                        r.shared_tissues = $shared_tissues
                    RETURN r
                    """
                    
                    await session.run(query,
                        pub_id=pub.id,
                        dataset_id=dataset.id,
                        shared_organisms=list(shared_organisms),
                        shared_tissues=list(shared_tissues)
                    )
    
    async def search_graph(self, query: str, entity_types: List[str] = None) -> List[Dict[str, Any]]:
        """Search the knowledge graph."""
        try:
            async with self.driver.session() as session:
                # Simple text search across nodes
                cypher_query = """
                MATCH (n)
                WHERE any(prop in keys(n) WHERE n[prop] CONTAINS $query)
                RETURN n, labels(n) as node_type
                LIMIT 50
                """
                
                result = await session.run(cypher_query, query=query)
                
                results = []
                async for record in result:
                    node = dict(record['n'])
                    node['node_type'] = record['node_type']
                    results.append(node)
                
                return results
                
        except Exception as e:
            self.logger.error(f"Error searching graph: {e}")
            return []
    
    async def get_entity_connections(self, entity_id: str) -> Dict[str, Any]:
        """Get all connections for an entity."""
        try:
            async with self.driver.session() as session:
                query = """
                MATCH (n {id: $entity_id})-[r]-(connected)
                RETURN n, r, connected, labels(connected) as connected_type
                """
                
                result = await session.run(query, entity_id=entity_id)
                
                connections = {
                    'entity': None,
                    'relationships': []
                }
                
                async for record in result:
                    if connections['entity'] is None:
                        connections['entity'] = dict(record['n'])
                    
                    connections['relationships'].append({
                        'relationship': dict(record['r']),
                        'connected_entity': dict(record['connected']),
                        'connected_type': record['connected_type']
                    })
                
                return connections
                
        except Exception as e:
            self.logger.error(f"Error getting entity connections: {e}")
            return {'entity': None, 'relationships': []}
    
    async def close(self):
        """Close Neo4j driver."""
        if self.driver:
            await self.driver.close()


# Export class
__all__ = ["Neo4jClient"]