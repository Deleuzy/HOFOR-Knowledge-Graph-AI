#!/usr/bin/env python3
"""
Self-Learning Impact Analysis System Demo
=========================================

This demonstrates the core functionality of the RAG-based system for industrial automation
without complex external dependencies.
"""

import re
import os
from typing import Dict, List, Any
from dataclasses import dataclass
from datetime import datetime

# Mock data representing your HOFOR documents
MOCK_DOCUMENTS = {
    "signal_list": """
    I/O Configuration for Kvæsthusbroen Project:
    AI001: Temperature Sensor Input (°C)
    AI002: Pressure Sensor Input (bar)
    DI005: Motor Running Status (boolean)
    DI006: Valve Open Status (boolean)
    DO010: Motor Start Command (boolean)
    DO011: Valve Control Command (boolean)
    SI020: Emergency Stop Input (safety)
    SI021: Safety Door Status (safety)

    Communication Protocols: Profinet, Modbus TCP, OPC UA
    Response Time Requirements: 100ms cycle time, 50ms safety response
    Redundancy: High availability system, SIL 2 safety level
    """,

    "component_list": """
    Hardware Components List:
    PLC System: Siemens S7-1500 with redundancy
    SCADA System: WinCC Professional V17
    Motor Drives: SEW Eurodrive MOVIDRIVE
    Motors: Various 3-phase induction motors
    Instruments: Endress+Hauser pressure/level transmitters

    Network: Profinet ring topology with MRP
    Safety: Siemens Safety Integrated
    """,

    "cable_spec": """
    Cable Specifications:
    Profinet Data Cables: CAT 6A shielded, green
    Power Cables: 5x2.5mm² + ground, blue
    Control Cables: Shielded multi-pair, gray
    Signal Cables: 2x0.5mm² shielded, yellow

    Standards Compliance: IEC 60204, EN 50174-2, IEC 61511
    """
}

@dataclass
class TechnicalRequirements:
    io_points: Dict[str, List[str]]
    protocols: List[str]
    response_times: List[str]
    redundancy_requirements: List[str]

@dataclass
class KnowledgePattern:
    industry: str
    hardware_combination: str
    success_rate: float
    common_issues: List[str]
    recommended_solutions: List[str]

class SimpleParser:
    def __init__(self):
        self.io_patterns = {
            'analog_input': r'AI\d+',
            'analog_output': r'AO\d+',
            'digital_input': r'DI\d+',
            'digital_output': r'DO\d+',
            'safety_input': r'SI\d+',
            'safety_output': r'SO\d+'
        }

        self.protocol_patterns = {
            'profinet': r'profinet',
            'modbus': r'modbus',
            'opc_ua': r'opc.?ua',
            'ethercat': r'ethercat'
        }

    def extract_io_points(self, text: str) -> Dict[str, List[str]]:
        io_points = {}
        for io_type, pattern in self.io_patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                io_points[io_type] = list(set(matches))
        return io_points

    def extract_protocols(self, text: str) -> List[str]:
        protocols = []
        for protocol, pattern in self.protocol_patterns.items():
            if re.search(pattern, text, re.IGNORECASE):
                protocols.append(protocol.upper())
        return protocols

    def extract_response_times(self, text: str) -> List[str]:
        patterns = [r'\d+ms.*?response', r'\d+ms.*?cycle', r'response.*?time.*?\d+ms']
        response_times = []
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            response_times.extend(matches)
        return list(set(response_times))

    def extract_redundancy(self, text: str) -> List[str]:
        patterns = [r'high.availability', r'redundan', r'safety.integrity.level', r'sil.\d']
        requirements = []
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            requirements.extend(matches)
        return list(set(requirements))

    def parse_document(self, content: str) -> TechnicalRequirements:
        return TechnicalRequirements(
            io_points=self.extract_io_points(content),
            protocols=self.extract_protocols(content),
            response_times=self.extract_response_times(content),
            redundancy_requirements=self.extract_redundancy(content)
        )

class SimpleKnowledgeBase:
    def __init__(self):
        self.patterns = [
            KnowledgePattern(
                industry="water",
                hardware_combination="Siemens + WinCC",
                success_rate=0.85,
                common_issues=["Profinet timing issues", "Memory constraints in SCADA"],
                recommended_solutions=["Use dedicated network segments", "Optimize data blocks"]
            ),
            KnowledgePattern(
                industry="energy",
                hardware_combination="Rockwell + Wonderware",
                success_rate=0.78,
                common_issues=["I/O mapping delays", "Tag configuration issues"],
                recommended_solutions=["Pre-configure I/O templates", "Use standardized naming"]
            )
        ]

    def find_similar_patterns(self, requirements: TechnicalRequirements) -> List[KnowledgePattern]:
        """Find patterns that match the requirements"""
        matching_patterns = []

        # Check for protocol matches
        if 'PROFINET' in requirements.protocols:
            matching_patterns.extend([p for p in self.patterns if 'Siemens' in p.hardware_combination])

        if 'MODBUS' in requirements.protocols:
            matching_patterns.extend([p for p in self.patterns if 'Rockwell' in p.hardware_combination])

        # Check for redundancy requirements
        if requirements.redundancy_requirements:
            # Filter for high-reliability patterns
            matching_patterns.extend([p for p in self.patterns if p.success_rate > 0.8])

        # Remove duplicates by converting to list of tuples and back
        seen = set()
        unique_patterns = []
        for pattern in matching_patterns:
            pattern_tuple = (pattern.industry, pattern.hardware_combination, pattern.success_rate)
            if pattern_tuple not in seen:
                seen.add(pattern_tuple)
                unique_patterns.append(pattern)
        return unique_patterns

class SelfLearningAnalyzer:
    def __init__(self):
        self.parser = SimpleParser()
        self.knowledge_base = SimpleKnowledgeBase()

    def analyze_requirements(self, requirements: TechnicalRequirements) -> Dict[str, Any]:
        """Analyze technical requirements using knowledge base"""

        # Find similar historical patterns
        similar_patterns = self.knowledge_base.find_similar_patterns(requirements)

        # Generate analysis
        analysis = {
            'extracted_requirements': {
                'io_points': requirements.io_points,
                'protocols': requirements.protocols,
                'response_times': requirements.response_times,
                'redundancy': requirements.redundancy_requirements
            },
            'similar_patterns_found': len(similar_patterns),
            'risk_assessment': self._assess_risks(requirements, similar_patterns),
            'recommendations': self._generate_recommendations(requirements, similar_patterns),
            'time_estimation': self._estimate_time(requirements, similar_patterns),
            'confidence_score': min(len(similar_patterns) / 5, 1.0)
        }

        return analysis

    def _assess_risks(self, requirements: TechnicalRequirements, patterns: List[KnowledgePattern]) -> str:
        risks = []

        if 'SI' in str(requirements.io_points) and not requirements.redundancy_requirements:
            risks.append("Safety I/O detected but no redundancy requirements specified")

        if requirements.response_times and any('100ms' in rt for rt in requirements.response_times):
            risks.append("Tight timing requirements may conflict with safety systems")

        if not requirements.protocols:
            risks.append("No communication protocols specified")

        # Add pattern-based risks
        for pattern in patterns:
            if pattern.success_rate < 0.8:
                risks.append(f"Similar projects with {pattern.hardware_combination} had lower success rates")

        return "; ".join(risks) if risks else "Low risk - standard requirements"

    def _generate_recommendations(self, requirements: TechnicalRequirements, patterns: List[KnowledgePattern]) -> str:
        recommendations = []

        if patterns:
            best_pattern = max(patterns, key=lambda p: p.success_rate)
            recommendations.append(f"Recommended: {best_pattern.hardware_combination} (proven in {best_pattern.industry} industry)")

        if 'PROFINET' in requirements.protocols:
            recommendations.append("Use Profinet ring topology with MRP for redundancy")

        if requirements.redundancy_requirements:
            recommendations.append("Implement hot-standby PLC configuration")

        return "; ".join(recommendations)

    def _estimate_time(self, requirements: TechnicalRequirements, patterns: List[KnowledgePattern]) -> str:
        base_time = 120  # Base hours for standard project

        # Adjust based on I/O count
        io_count = sum(len(points) for points in requirements.io_points.values())
        time_adjustment = io_count * 2  # 2 hours per I/O point

        # Adjust based on protocols
        if 'PROFINET' in requirements.protocols:
            time_adjustment += 40  # Additional time for Profinet setup

        if requirements.redundancy_requirements:
            time_adjustment += 60  # Additional time for redundancy

        # Adjust based on historical patterns
        if patterns:
            avg_success = sum(p.success_rate for p in patterns) / len(patterns)
            if avg_success < 0.8:
                time_adjustment *= 1.3  # Add 30% buffer for risky patterns

        estimated_hours = base_time + time_adjustment

        return f"{estimated_hours:.0f} hours ({base_time}h base + {time_adjustment:.0f}h complexity)"

def main():
    print("🏭 Self-Learning Impact Analysis System Demo")
    print("=" * 50)

    analyzer = SelfLearningAnalyzer()

    # Analyze each mock document
    for doc_name, content in MOCK_DOCUMENTS.items():
        print(f"\n📄 Analyzing {doc_name.replace('_', ' ').title()}")
        print("-" * 30)

        # Parse requirements
        requirements = analyzer.parser.parse_document(content)

        # Show extracted data
        print("📋 Extracted Requirements:")
        print(f"  I/O Points: {requirements.io_points}")
        print(f"  Protocols: {requirements.protocols}")
        print(f"  Response Times: {requirements.response_times}")
        print(f"  Redundancy: {requirements.redundancy_requirements}")

        # Generate analysis
        analysis = analyzer.analyze_requirements(requirements)

        print("\n🔍 Analysis Results:")
        print(f"  Risk Assessment: {analysis['risk_assessment']}")
        print(f"  Recommendations: {analysis['recommendations']}")
        print(f"  Time Estimation: {analysis['time_estimation']}")
        print(f"  Confidence Score: {analysis['confidence_score']:.1%}")
        print(f"  Similar Patterns: {analysis['similar_patterns_found']}")

    print("\n🎯 System Learning Demonstration:")
    print("-" * 40)

    # Simulate learning from a new project
    print("📈 Learning from completed project...")
    new_pattern = KnowledgePattern(
        industry="water",
        hardware_combination="Siemens + WinCC",
        success_rate=0.92,
        common_issues=["Initial network configuration"],
        recommended_solutions=["Use HOFOR standard network templates"]
    )

    analyzer.knowledge_base.patterns.append(new_pattern)
    print("✓ Added learning from Kvæsthusbroen project completion")
    print("✓ System now has improved recommendations for water industry projects")

    print("\n✅ Demo completed successfully!")
    print("The system demonstrates:")
    print("  • Automatic requirement extraction from documents")
    print("  • Pattern matching with historical projects")
    print("  • Risk assessment and recommendations")
    print("  • Time estimation based on complexity")
    print("  • Continuous learning capabilities")
if __name__ == "__main__":
    main()