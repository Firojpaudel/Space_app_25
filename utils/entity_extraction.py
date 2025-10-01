"""
Biological entity extraction utilities using NLP models.
"""
import re
import asyncio
from typing import Dict, List, Optional, Set
import logging

# Import spaCy and scispacy when available
try:
    import spacy
    from scispacy.linking import EntityLinker
    SPACY_AVAILABLE = True
except ImportError:
    spacy = None
    EntityLinker = None
    SPACY_AVAILABLE = False

from models.schemas import GravityCondition, StudyType
from config import ModelConfig

logger = logging.getLogger(__name__)


class BiologicalEntityExtractor:
    """Extract biological entities from text using NLP models."""
    
    def __init__(self):
        """Initialize the entity extractor."""
        self.nlp = None
        self.entity_linker = None
        self._load_models()
        
        # Define entity patterns
        self.organism_patterns = [
            r'\b(?:mus musculus|mouse|mice)\b',
            r'\b(?:homo sapiens|human|humans)\b',
            r'\b(?:rattus norvegicus|rat|rats)\b',
            r'\b(?:drosophila|fruit fly|flies)\b',
            r'\b(?:caenorhabditis elegans|c\.?\s*elegans|nematode)\b',
            r'\b(?:arabidopsis|plant|plants)\b',
            r'\b(?:zebrafish|danio rerio)\b',
            r'\b(?:saccharomyces cerevisiae|yeast)\b'
        ]
        
        self.tissue_patterns = [
            r'\b(?:bone|bones|skeletal)\b',
            r'\b(?:muscle|muscles|muscular)\b',
            r'\b(?:brain|neural|neuronal)\b',
            r'\b(?:heart|cardiac|cardiovascular)\b',
            r'\b(?:liver|hepatic)\b',
            r'\b(?:kidney|renal)\b',
            r'\b(?:lung|pulmonary|respiratory)\b',
            r'\b(?:skin|dermal|epidermal)\b',
            r'\b(?:blood|hematologic|immune)\b',
            r'\b(?:stem cell|stem-cell)\b'
        ]
        
        self.mission_patterns = [
            r'\b(?:iss|international space station)\b',
            r'\b(?:space shuttle|shuttle)\b',
            r'\b(?:apollo|gemini|mercury)\b',
            r'\b(?:mars|lunar|moon)\b',
            r'\b(?:spacex|dragon)\b',
            r'\b(?:soyuz|progress)\b'
        ]
        
        self.gravity_patterns = {
            GravityCondition.MICROGRAVITY: [
                r'\bmicrogravity\b', r'\bzero.?g\b', r'\bspace.?flight\b',
                r'\bweightless\b', r'\borbital\b'
            ],
            GravityCondition.PARTIAL_GRAVITY: [
                r'\bpartial.?gravity\b', r'\breduced.?gravity\b', 
                r'\blunar.?gravity\b', r'\bmars.?gravity\b'
            ],
            GravityCondition.HYPERGRAVITY: [
                r'\bhypergravity\b', r'\bcentrifuge\b', r'\bincreased.?gravity\b'
            ]
        }
    
    def _load_models(self):
        """Load NLP models if available."""
        if not SPACY_AVAILABLE:
            logger.warning("spaCy and scispacy not available, using pattern-based extraction")
            return
        
        try:
            # Load scientific English model
            self.nlp = spacy.load(ModelConfig.SCISPACY_MODEL)
            
            # Add entity linker for MeSH terms (if available)
            try:
                self.entity_linker = EntityLinker(
                    resolve_abbreviations=True,
                    name="mesh"
                )
                self.nlp.add_pipe(self.entity_linker)
            except:
                logger.warning("Could not load MeSH entity linker")
                
        except OSError:
            logger.warning(f"Could not load {ModelConfig.SCISPACY_MODEL}, using basic extraction")
            self.nlp = None
    
    async def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """
        Extract biological entities from text.
        
        Args:
            text: Input text
            
        Returns:
            Dict[str, List[str]]: Extracted entities by type
        """
        if not text:
            return self._empty_result()
        
        entities = self._empty_result()
        
        # Use spaCy if available
        if self.nlp:
            entities.update(await self._extract_with_spacy(text))
        
        # Pattern-based extraction (always run as fallback/supplement)
        pattern_entities = await self._extract_with_patterns(text)
        
        # Merge results
        for key, values in pattern_entities.items():
            if key in entities:
                entities[key].extend(values)
                entities[key] = list(set(entities[key]))  # Remove duplicates
            else:
                entities[key] = values
        
        # Extract special conditions
        entities['gravity_condition'] = self._extract_gravity_condition(text)
        entities['study_type'] = self._extract_study_type(text)
        
        return entities
    
    async def _extract_with_spacy(self, text: str) -> Dict[str, List[str]]:
        """Extract entities using spaCy/scispacy."""
        entities = self._empty_result()
        
        try:
            doc = self.nlp(text)
            
            for ent in doc.ents:
                # Map spaCy entity types to our categories
                if ent.label_ in ['PERSON']:
                    continue  # Skip person names
                elif ent.label_ in ['ORG', 'ORGANIZATION']:
                    continue  # Skip organizations for now
                elif ent.label_ in ['CHEMICAL', 'DRUG']:
                    entities['proteins'].append(ent.text)
                elif ent.label_ in ['DISEASE']:
                    entities['keywords'].append(ent.text)
                else:
                    # Add to keywords if not specifically categorized
                    entities['keywords'].append(ent.text)
            
            # Extract MeSH terms if entity linker is available
            if self.entity_linker:
                for ent in doc.ents:
                    if hasattr(ent._, 'kb_ents') and ent._.kb_ents:
                        for kb_ent in ent._.kb_ents:
                            entities['mesh_terms'].append(kb_ent[0])
            
        except Exception as e:
            logger.error(f"Error in spaCy extraction: {e}")
        
        return entities
    
    async def _extract_with_patterns(self, text: str) -> Dict[str, List[str]]:
        """Extract entities using regex patterns."""
        entities = self._empty_result()
        text_lower = text.lower()
        
        # Extract organisms
        for pattern in self.organism_patterns:
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            entities['organisms'].extend(matches)
        
        # Extract tissues
        for pattern in self.tissue_patterns:
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            entities['tissues'].extend(matches)
        
        # Extract missions
        for pattern in self.mission_patterns:
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            entities['missions'].extend(matches)
        
        # Extract gene-like patterns (uppercase sequences)
        gene_pattern = r'\b[A-Z]{2,10}\d?\b'
        gene_matches = re.findall(gene_pattern, text)
        # Filter out common non-gene abbreviations
        non_genes = {'DNA', 'RNA', 'PCR', 'RT', 'PBS', 'NASA', 'ISS', 'USA'}
        entities['genes'] = [g for g in gene_matches if g not in non_genes]
        
        # Remove duplicates
        for key in entities:
            if isinstance(entities[key], list):
                entities[key] = list(set(entities[key]))
        
        return entities
    
    def _extract_gravity_condition(self, text: str) -> Optional[GravityCondition]:
        """Extract gravity condition from text."""
        text_lower = text.lower()
        
        for condition, patterns in self.gravity_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    return condition
        
        return None
    
    def _extract_study_type(self, text: str) -> Optional[StudyType]:
        """Extract study type from text."""
        text_lower = text.lower()
        
        study_patterns = {
            StudyType.EXPERIMENTAL: [
                r'\bexperiment\b', r'\btrial\b', r'\btreatment\b'
            ],
            StudyType.OBSERVATIONAL: [
                r'\bobservation\b', r'\bobserved\b', r'\bsurvey\b'
            ],
            StudyType.COMPUTATIONAL: [
                r'\bmodel\b', r'\bsimulation\b', r'\bcomputational\b'
            ],
            StudyType.REVIEW: [
                r'\breview\b', r'\bmeta.?analysis\b', r'\bsystematic\b'
            ]
        }
        
        for study_type, patterns in study_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    return study_type
        
        return None
    
    def _empty_result(self) -> Dict[str, List[str]]:
        """Return empty entity extraction result."""
        return {
            'organisms': [],
            'tissues': [],
            'genes': [],
            'proteins': [],
            'missions': [],
            'keywords': [],
            'mesh_terms': []
        }


# Global extractor instance
_extractor = None


async def extract_biological_entities(text: str) -> Dict[str, List[str]]:
    """
    Extract biological entities from text.
    
    Args:
        text: Input text
        
    Returns:
        Dict[str, List[str]]: Extracted entities
    """
    global _extractor
    
    if _extractor is None:
        _extractor = BiologicalEntityExtractor()
    
    return await _extractor.extract_entities(text)


def get_entity_types() -> List[str]:
    """Get list of supported entity types."""
    return [
        'organisms',
        'tissues', 
        'genes',
        'proteins',
        'missions',
        'keywords',
        'mesh_terms'
    ]


# Export functions
__all__ = [
    "BiologicalEntityExtractor",
    "extract_biological_entities",
    "get_entity_types"
]