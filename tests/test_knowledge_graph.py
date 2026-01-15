#!/usr/bin/env python3
"""
test_knowledge_graph.py
Test the intelligent knowledge graph integration
"""

import sys
import os
# Add the parent directory to the path so we can import from src/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.knowledge_graph import IntelligentKnowledgeGraph

def test_knowledge_graph():
    print("🧠 Testing Intelligent Knowledge Graph")
    print("=" * 50)

    kg = IntelligentKnowledgeGraph()
    # Use separate storage file for testing (don't overwrite real data)
    kg.storage_file = 'storage/test_knowledge_graph.json'
    print("📁 Using separate test storage: storage/test_knowledge_graph.json")

    # Test employee addition
    print("\n👤 Adding test employee...")
    test_employee = {
        'employee_id': 'TEST001',
        'name': 'Test Engineer',
        'role': 'PLC Engineer',
        'expertise_areas': ['Siemens', 'PROFINET', 'Safety'],
        'hardware_experience': ['Siemens S7-1500', 'WinCC'],
        'project_history': ['Test Project'],
        'certifications': ['Siemens Certified']
    }
    kg.add_employee_profile(test_employee)

    # Test project addition
    print("\n📋 Adding test project...")
    test_project = {
        'project_id': 'TEST_PROJ_001',
        'industry': 'water',
        'hardware_combination': 'Siemens + WinCC',
        'estimated_hours': 120.0,
        'actual_hours': 145.0,
        'issues': ['PROFINET communication issues', 'SIL 2 certification delay'],
        'solutions': ['Upgraded network switches', 'Additional safety testing'],
        'engineer_id': 'TEST001'
    }
    kg.add_project_to_graph(test_project)

    # Show results
    print("\n📊 Updated Graph Statistics:")
    stats = kg.get_graph_statistics()
    for key, value in stats.items():
        print(f"   {key}: {value}")

    print("\n👨‍💼 Experts found:")
    experts = kg.find_experts_for_hardware("Siemens + WinCC")
    for exp in experts:
        print(f"   • {exp['name']} - Confidence: {exp['confidence_score']:.2%}")

    print("\n⚠️ Risk Assessment:")
    risk = kg.get_risk_assessment("Siemens + WinCC")
    print(f"   Risk Level: {risk['risk_level']} (Confidence: {risk['confidence']:.2%})")

    # Generate visualization (separate file for test)
    kg.visualize_graph("test_knowledge_graph.html")
    print("\n✅ Test complete! Open 'test_knowledge_graph.html' to see the test graph.")
    print("💡 Your real knowledge graph remains unchanged in 'storage/knowledge_graph.json'")

if __name__ == "__main__":
    test_knowledge_graph()