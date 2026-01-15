import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any, Optional
import numpy as np
import openai
from .config import Config

class VectorStore:
    def __init__(self):
        self.config = Config()
        self.client = chromadb.PersistentClient(path=self.config.CHROMA_PERSIST_DIR)
        self.collection = self.client.get_or_create_collection(
            name="industrial_automation_kb",
            metadata={"description": "Knowledge base for industrial automation projects"}
        )
        self.openai_client = openai.OpenAI(api_key=self.config.OPENAI_API_KEY)

    def _get_embedding(self, text: str) -> List[float]:
        """Get embeddings using OpenAI"""
        response = self.openai_client.embeddings.create(
            input=text,
            model=self.config.EMBEDDING_MODEL
        )
        return response.data[0].embedding

    def add_technical_requirements(self, requirements: Dict[str, Any], document_id: str):
        """Add technical requirements to vector store"""
        # Create searchable chunks from requirements
        chunks = self._create_requirement_chunks(requirements)

        for i, chunk in enumerate(chunks):
            embedding = self._get_embedding(chunk['text'])

            self.collection.add(
                embeddings=[embedding],
                documents=[chunk['text']],
                metadatas=[{
                    **chunk['metadata'],
                    'document_id': document_id,
                    'chunk_type': 'technical_requirements',
                    'chunk_id': f"{document_id}_req_{i}"
                }],
                ids=[f"{document_id}_req_{i}"]
            )

    def add_project_knowledge(self, knowledge: Dict[str, Any], project_id: str):
        """Add project knowledge to vector store"""
        chunks = self._create_knowledge_chunks(knowledge)

        for i, chunk in enumerate(chunks):
            embedding = self._get_embedding(chunk['text'])

            self.collection.add(
                embeddings=[embedding],
                documents=[chunk['text']],
                metadatas=[{
                    **chunk['metadata'],
                    'project_id': project_id,
                    'chunk_type': 'project_knowledge',
                    'chunk_id': f"{project_id}_kb_{i}"
                }],
                ids=[f"{project_id}_kb_{i}"]
            )

    def add_patterns(self, patterns: List[Dict[str, Any]]):
        """Add analyzed patterns to vector store"""
        for pattern in patterns:
            text = self._create_pattern_text(pattern)
            embedding = self._get_embedding(text)

            self.collection.add(
                embeddings=[embedding],
                documents=[text],
                metadatas=[{
                    'pattern_type': pattern['pattern_type'],
                    'industry': pattern['industry'],
                    'hardware_combination': pattern['hardware_combination'],
                    'success_rate': pattern['success_rate'],
                    'confidence_score': pattern['confidence_score'],
                    'chunk_type': 'pattern_analysis'
                }],
                ids=[f"pattern_{pattern['pattern_type']}_{pattern['industry']}_{hash(str(pattern)) % 10000}"]
            )

    def search_similar(self, query: str, n_results: int = 5, filter_metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """Search for similar content in the knowledge base"""
        query_embedding = self._get_embedding(query)

        where_clause = None
        if filter_metadata:
            where_clause = filter_metadata

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where_clause
        )

        return results

    def _create_requirement_chunks(self, requirements: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create searchable chunks from technical requirements"""
        chunks = []

        # I/O points chunk
        if requirements.get('io_points'):
            io_text = f"I/O Points: {', '.join([f'{k}: {v}' for k, v in requirements['io_points'].items()])}"
            chunks.append({
                'text': io_text,
                'metadata': {'category': 'io_points'}
            })

        # Protocols chunk
        if requirements.get('protocols'):
            protocol_text = f"Communication Protocols: {', '.join(requirements['protocols'])}"
            chunks.append({
                'text': protocol_text,
                'metadata': {'category': 'protocols'}
            })

        # Response times chunk
        if requirements.get('response_times'):
            timing_text = f"Response Time Requirements: {', '.join(requirements['response_times'])}"
            chunks.append({
                'text': timing_text,
                'metadata': {'category': 'timing'}
            })

        # Redundancy chunk
        if requirements.get('redundancy_requirements'):
            redundancy_text = f"Redundancy Requirements: {', '.join(requirements['redundancy_requirements'])}"
            chunks.append({
                'text': redundancy_text,
                'metadata': {'category': 'redundancy'}
            })

        return chunks

    def _create_knowledge_chunks(self, knowledge: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create searchable chunks from project knowledge"""
        chunks = []

        # Time analysis chunk
        if knowledge.get('actual_hours') and knowledge.get('estimated_hours'):
            time_text = f"Project {knowledge['project_id']}: Estimated {knowledge['estimated_hours']}h, Actual {knowledge['actual_hours']}h"
            chunks.append({
                'text': time_text,
                'metadata': {
                    'category': 'time_analysis',
                    'time_deviation': knowledge['actual_hours'] - knowledge['estimated_hours']
                }
            })

        # Issues and solutions chunk
        if knowledge.get('issues_encountered'):
            issues_text = f"Issues encountered: {', '.join(knowledge['issues_encountered'])}"
            chunks.append({
                'text': issues_text,
                'metadata': {'category': 'issues'}
            })

        if knowledge.get('solutions_applied'):
            solutions_text = f"Solutions applied: {', '.join(knowledge['solutions_applied'])}"
            chunks.append({
                'text': solutions_text,
                'metadata': {'category': 'solutions'}
            })

        # Hardware combination chunk
        if knowledge.get('hardware_combination'):
            hardware_text = f"Hardware combination: {knowledge['hardware_combination']} in {knowledge.get('industry_type', 'unknown')} industry"
            chunks.append({
                'text': hardware_text,
                'metadata': {
                    'category': 'hardware',
                    'industry': knowledge.get('industry_type', 'unknown'),
                    'hardware': knowledge['hardware_combination']
                }
            })

        return chunks

    def _create_pattern_text(self, pattern: Dict[str, Any]) -> str:
        """Create searchable text from pattern analysis"""
        return f"""Pattern Analysis - {pattern['pattern_type']}:
Industry: {pattern['industry']}
Hardware: {pattern['hardware_combination']}
Success Rate: {pattern['success_rate']:.2%}
Average Time Deviation: {pattern['avg_time_deviation']:.2%}
Common Issues: {', '.join(pattern['common_issues'])}
Recommended Solutions: {', '.join(pattern['recommended_solutions'])}
Confidence: {pattern['confidence_score']:.2%}
"""