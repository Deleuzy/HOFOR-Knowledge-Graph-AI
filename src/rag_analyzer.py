from typing import Dict, List, Any, Optional
import os
import pandas as pd
import openai
from .config import Config
from .vector_store import VectorStore
from .knowledge_extractor import KnowledgeExtractor

class SelfLearningAnalyzer:
    def __init__(self):
        self.config = Config()
        self.vector_store = VectorStore()
        self.knowledge_extractor = KnowledgeExtractor()

        # Initialize OpenAI client
        self.client = openai.OpenAI(api_key=self.config.OPENAI_API_KEY)

    def initialize_knowledge_base(self):
        """Initialize the knowledge base from existing documents"""
        print("Initializing knowledge base...")

        # Process technical documents
        self._process_technical_documents()

        # Process existing project knowledge
        self._process_project_knowledge()

        # Analyze patterns
        self._analyze_and_store_patterns()

        print("Knowledge base initialization complete!")

    def _process_technical_documents(self):
        """Process all technical documents in the workspace"""
        pdf_files = [f for f in os.listdir(self.config.DOCUMENTS_DIR) if f.endswith('.pdf')]

        for pdf_file in pdf_files:
            pdf_path = os.path.join(self.config.DOCUMENTS_DIR, pdf_file)

            try:
                # Extract technical requirements
                requirements = self.knowledge_extractor.parser.parse_technical_document(pdf_path)

                # Add to vector store
                self.vector_store.add_technical_requirements(
                    requirements.__dict__,
                    os.path.splitext(pdf_file)[0]
                )

                print(f"Processed technical document: {pdf_file}")

            except Exception as e:
                print(f"Error processing {pdf_file}: {e}")

    def _process_project_knowledge(self):
        """Process existing project knowledge"""
        # For now, we'll simulate project knowledge extraction
        # In a real scenario, you'd have commissioning reports, etc.
        pass

    def _analyze_and_store_patterns(self):
        """Analyze patterns and store them"""
        # This would analyze patterns from existing project data
        # For the assignment, we'll create some sample patterns
        sample_patterns = [
            {
                'pattern_type': 'hardware_compatibility',
                'industry': 'energy',
                'hardware_combination': 'Siemens + WinCC',
                'success_rate': 0.85,
                'avg_time_deviation': 0.15,
                'common_issues': ['Profinet timing issues', 'Memory constraints'],
                'recommended_solutions': ['Use dedicated network segments', 'Optimize data blocks'],
                'confidence_score': 0.8
            },
            {
                'pattern_type': 'time_estimation',
                'industry': 'water',
                'hardware_combination': 'Rockwell + Wonderware',
                'success_rate': 0.78,
                'avg_time_deviation': 0.22,
                'common_issues': ['I/O mapping delays', 'Tag configuration issues'],
                'recommended_solutions': ['Pre-configure I/O templates', 'Use standardized naming conventions'],
                'confidence_score': 0.7
            }
        ]

        self.vector_store.add_patterns(sample_patterns)

    def analyze_new_tender(self, tender_document_path: str) -> Dict[str, Any]:
        """Analyze a new tender document using RAG"""

        # Extract requirements from tender
        requirements = self.knowledge_extractor.parser.parse_technical_document(tender_document_path)

        # Create analysis query
        analysis_query = self._create_analysis_query(requirements)

        # Search for similar projects and patterns
        similar_content = self.vector_store.search_similar(analysis_query, n_results=10)

        # Generate comprehensive analysis
        analysis = self._generate_analysis(requirements, similar_content)

        # Store the new analysis for future learning
        self._store_new_analysis(requirements, analysis, os.path.basename(tender_document_path))

        return analysis

    def _create_analysis_query(self, requirements) -> str:
        """Create a search query from technical requirements"""
        query_parts = []

        if requirements.io_points:
            io_types = list(requirements.io_points.keys())
            query_parts.append(f"I/O types: {', '.join(io_types)}")

        if requirements.protocols:
            query_parts.append(f"Protocols: {', '.join(requirements.protocols)}")

        if requirements.redundancy_requirements:
            query_parts.append(f"Redundancy: {', '.join(requirements.redundancy_requirements)}")

        return " ".join(query_parts) if query_parts else "industrial automation project analysis"

    def _generate_analysis(self, requirements, similar_content) -> Dict[str, Any]:
        """Generate comprehensive analysis using RAG"""

        # Prepare context from similar content
        context_parts = []
        if similar_content.get('documents'):
            for doc in similar_content['documents'][:5]:  # Use top 5 results
                context_parts.append(doc)

        context = "\n".join(context_parts)

        # Create analysis prompt
        prompt = f"""
        Based on the following technical requirements and historical project knowledge,
        provide a comprehensive impact analysis for this industrial automation project:

        TECHNICAL REQUIREMENTS:
        - I/O Points: {requirements.io_points}
        - Communication Protocols: {requirements.protocols}
        - Response Time Requirements: {requirements.response_times}
        - Redundancy Requirements: {requirements.redundancy_requirements}

        HISTORICAL CONTEXT:
        {context}

        Please provide:
        1. Risk Assessment: Identify potential technical conflicts and challenges
        2. Time Estimation: Realistic timeline based on similar projects
        3. Recommended Hardware/Software Stack: Based on proven combinations
        4. Critical Success Factors: Key considerations for this project type
        5. Potential Issues: Common problems and their solutions
        6. Knowledge Gaps: Areas where additional expertise may be needed

        Be specific and reference the historical data where relevant.
        """

        # Generate analysis using OpenAI
        response = self.client.chat.completions.create(
            model=self.config.LLM_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=2000
        )

        analysis_response = response.choices[0].message.content

        return {
            'requirements_summary': requirements.__dict__,
            'risk_assessment': self._extract_section(analysis_response, 'Risk Assessment'),
            'time_estimation': self._extract_section(analysis_response, 'Time Estimation'),
            'recommendations': self._extract_section(analysis_response, 'Recommended Hardware/Software Stack'),
            'success_factors': self._extract_section(analysis_response, 'Critical Success Factors'),
            'potential_issues': self._extract_section(analysis_response, 'Potential Issues'),
            'knowledge_gaps': self._extract_section(analysis_response, 'Knowledge Gaps'),
            'confidence_score': self._calculate_confidence(similar_content),
            'similar_projects_count': len(similar_content.get('documents', []))
        }

    def _extract_section(self, text: str, section_name: str) -> str:
        """Extract a specific section from the analysis text"""
        # Simple extraction - in practice you'd want more sophisticated parsing
        lines = text.split('\n')
        section_lines = []
        in_section = False

        for line in lines:
            if section_name.lower() in line.lower():
                in_section = True
                continue
            elif any(other in line.lower() for other in ['1.', '2.', '3.', '4.', '5.', '6.']) and in_section:
                break
            elif in_section:
                section_lines.append(line)

        return '\n'.join(section_lines).strip()

    def _calculate_confidence(self, similar_content) -> float:
        """Calculate confidence score based on available knowledge"""
        doc_count = len(similar_content.get('documents', []))
        return min(doc_count / 10, 1.0)  # Scale confidence by available data

    def _store_new_analysis(self, requirements, analysis: Dict, document_id: str):
        """Store new analysis for continuous learning"""
        # Add the analysis results back to the knowledge base
        analysis_text = f"""
        Analysis for {document_id}:
        Risk Assessment: {analysis.get('risk_assessment', '')}
        Time Estimation: {analysis.get('time_estimation', '')}
        Recommendations: {analysis.get('recommendations', '')}
        Success Factors: {analysis.get('success_factors', '')}
        Potential Issues: {analysis.get('potential_issues', '')}
        Knowledge Gaps: {analysis.get('knowledge_gaps', '')}
        """

        # Add to vector store
        embedding = self.vector_store._get_embedding(analysis_text)
        self.vector_store.collection.add(
            embeddings=[embedding],
            documents=[analysis_text],
            metadatas=[{
                'document_id': document_id,
                'chunk_type': 'analysis_result',
                'confidence_score': analysis.get('confidence_score', 0),
                'analysis_date': str(pd.Timestamp.now())
            }],
            ids=[f"analysis_{document_id}_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}"]
        )

def main():
    """Main function to demonstrate the system"""
    analyzer = SelfLearningAnalyzer()

    # Initialize knowledge base
    analyzer.initialize_knowledge_base()

    # Example: Analyze a new tender document
    # analysis = analyzer.analyze_new_tender("path/to/new/tender.pdf")
    # print(json.dumps(analysis, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()