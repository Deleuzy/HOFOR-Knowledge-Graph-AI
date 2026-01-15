#!/usr/bin/env python3
"""
knowledge_graph.py
Del 2: Intelligent Knowledge Graph System
Self-organizing knowledge system with standards, best practices, employee profiles, and confidence scoring
"""

import json
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict, field
from datetime import datetime, timedelta
import re

@dataclass
class KnowledgeNode:
    """Represents a node in the knowledge graph"""
    id: str
    type: str  # 'standard', 'best_practice', 'employee', 'hardware', 'project', 'risk'
    name: str
    description: str
    confidence_score: float = 1.0
    last_updated: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    relationships: List[str] = field(default_factory=list)  # IDs of related nodes

@dataclass
class KnowledgeEdge:
    """Represents a relationship between nodes"""
    source_id: str
    target_id: str
    relationship_type: str  # 'knows', 'uses', 'has_experience', 'follows_standard', etc.
    strength: float = 1.0
    last_updated: str = ""

@dataclass
class EmployeeProfile:
    """Employee expertise profile"""
    employee_id: str
    name: str
    role: str
    expertise_areas: List[str] = field(default_factory=list)
    hardware_experience: List[str] = field(default_factory=list)
    project_history: List[str] = field(default_factory=list)
    certifications: List[str] = field(default_factory=list)
    confidence_score: float = 1.0
    last_active: str = ""

class IntelligentKnowledgeGraph:
    def __init__(self, storage_file: str = "knowledge_graph.json"):
        self.storage_file = storage_file
        self.nodes: Dict[str, KnowledgeNode] = {}
        self.edges: List[KnowledgeEdge] = []
        self.employee_profiles: Dict[str, EmployeeProfile] = {}
        self.load_graph()

        # Initialize with standard knowledge
        if not self.nodes:
            self._initialize_standards_and_best_practices()

    def load_graph(self):
        """Load the knowledge graph from JSON file"""
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.nodes = {k: KnowledgeNode(**v) for k, v in data.get('nodes', {}).items()}
                    self.edges = [KnowledgeEdge(**e) for e in data.get('edges', [])]
                    self.employee_profiles = {k: EmployeeProfile(**v) for k, v in data.get('employees', {}).items()}
                print(f"📚 Loaded knowledge graph: {len(self.nodes)} nodes, {len(self.edges)} relationships, {len(self.employee_profiles)} employees")
            except Exception as e:
                print(f"⚠️ Could not load knowledge graph: {e}")
                self._initialize_standards_and_best_practices()
        else:
            print("🆕 Initializing new knowledge graph")
            self._initialize_standards_and_best_practices()

    def save_graph(self):
        """Save the knowledge graph to JSON file"""
        try:
            data = {
                'nodes': {k: asdict(v) for k, v in self.nodes.items()},
                'edges': [asdict(e) for e in self.edges],
                'employees': {k: asdict(v) for k, v in self.employee_profiles.items()},
                'last_updated': str(datetime.now())
            }
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"💾 Saved knowledge graph to {self.storage_file}")
        except Exception as e:
            print(f"❌ Could not save knowledge graph: {e}")

    def _initialize_standards_and_best_practices(self):
        """Initialize the graph with industry standards and best practices"""
        standards = [
            {
                'id': 'iec61131',
                'name': 'IEC 61131-3',
                'description': 'International standard for programmable controllers - programming languages (LD, FBD, ST, IL, SFC)',
                'type': 'standard',
                'confidence_score': 0.95
            },
            {
                'id': 'iec61508',
                'name': 'IEC 61508',
                'description': 'Functional safety of electrical/electronic/programmable electronic safety-related systems',
                'type': 'standard',
                'confidence_score': 0.98
            },
            {
                'id': 'iec61511',
                'name': 'IEC 61511',
                'description': 'Functional safety - Safety instrumented systems for the process industry sector',
                'type': 'standard',
                'confidence_score': 0.95
            },
            {
                'id': 'isa88',
                'name': 'ISA-88',
                'description': 'Batch control standard - models and terminology for batch processes',
                'type': 'standard',
                'confidence_score': 0.90
            },
            {
                'id': 'isa95',
                'name': 'ISA-95',
                'description': 'Enterprise-Control System Integration - defines terminology and models',
                'type': 'standard',
                'confidence_score': 0.90
            }
        ]

        best_practices = [
            {
                'id': 'siemens_profinet',
                'name': 'Siemens Profinet Best Practices',
                'description': 'Use MRP (Media Redundancy Protocol) for ring topology, dedicated switches, proper cable screening',
                'type': 'best_practice',
                'metadata': {'platform': 'Siemens', 'protocol': 'PROFINET'},
                'confidence_score': 0.88
            },
            {
                'id': 'rockwell_modbus',
                'name': 'Rockwell Modbus Best Practices',
                'description': 'Use Logix controllers with dedicated Ethernet ports, implement proper error handling',
                'type': 'best_practice',
                'metadata': {'platform': 'Rockwell', 'protocol': 'MODBUS'},
                'confidence_score': 0.85
            },
            {
                'id': 'abb_safety',
                'name': 'ABB Safety System Integration',
                'description': 'Always perform SIL verification testing, use certified safety PLCs for SIL 2/3 applications',
                'type': 'best_practice',
                'metadata': {'platform': 'ABB', 'safety': 'SIL'},
                'confidence_score': 0.92
            },
            {
                'id': 'sil_certification',
                'name': 'SIL Certification Process',
                'description': 'Document all safety requirements, perform FMEDA analysis, validate with third-party certification',
                'type': 'best_practice',
                'metadata': {'safety': 'SIL', 'certification': True},
                'confidence_score': 0.95
            }
        ]

        # Add all nodes
        for std in standards:
            node = KnowledgeNode(
                id=std['id'],
                type=std['type'],
                name=std['name'],
                description=std['description'],
                confidence_score=std['confidence_score'],
                last_updated=str(datetime.now())
            )
            self.nodes[std['id']] = node

        for bp in best_practices:
            node = KnowledgeNode(
                id=bp['id'],
                type=bp['type'],
                name=bp['name'],
                description=bp['description'],
                confidence_score=bp['confidence_score'],
                last_updated=str(datetime.now()),
                metadata=bp.get('metadata', {})
            )
            self.nodes[bp['id']] = node

        # Create relationships between standards and best practices
        self._add_edge('iec61508', 'sil_certification', 'supports')
        self._add_edge('iec61511', 'sil_certification', 'supports')
        self._add_edge('iec61131', 'siemens_profinet', 'enables')
        self._add_edge('iec61131', 'rockwell_modbus', 'enables')

    def _add_edge(self, source_id: str, target_id: str, relationship_type: str, strength: float = 1.0):
        """Add a relationship edge between nodes"""
        if source_id in self.nodes and target_id in self.nodes:
            edge = KnowledgeEdge(
                source_id=source_id,
                target_id=target_id,
                relationship_type=relationship_type,
                strength=strength,
                last_updated=str(datetime.now())
            )
            self.edges.append(edge)

    def add_employee_profile(self, employee_data: Dict[str, Any]):
        """Add or update an employee profile"""
        emp_id = employee_data['employee_id']

        if emp_id in self.employee_profiles:
            # Update existing profile
            profile = self.employee_profiles[emp_id]
            profile.expertise_areas.extend(employee_data.get('expertise_areas', []))
            profile.hardware_experience.extend(employee_data.get('hardware_experience', []))
            profile.project_history.extend(employee_data.get('project_history', []))
            profile.certifications.extend(employee_data.get('certifications', []))
            profile.last_active = str(datetime.now())

            # Remove duplicates
            profile.expertise_areas = list(set(profile.expertise_areas))
            profile.hardware_experience = list(set(profile.hardware_experience))
            profile.project_history = list(set(profile.project_history))
            profile.certifications = list(set(profile.certifications))

        else:
            # Create new profile
            profile = EmployeeProfile(
                employee_id=emp_id,
                name=employee_data['name'],
                role=employee_data['role'],
                expertise_areas=employee_data.get('expertise_areas', []),
                hardware_experience=employee_data.get('hardware_experience', []),
                project_history=employee_data.get('project_history', []),
                certifications=employee_data.get('certifications', []),
                last_active=str(datetime.now())
            )
            self.employee_profiles[emp_id] = profile

        # Update confidence score based on experience
        self._update_employee_confidence(emp_id)

        # Create knowledge node for employee
        self._create_employee_node(emp_id)

        print(f"👤 {'Updated' if emp_id in self.employee_profiles else 'Added'} employee profile: {employee_data['name']}")

    def _create_employee_node(self, employee_id: str):
        """Create a knowledge node for an employee"""
        profile = self.employee_profiles[employee_id]
        node = KnowledgeNode(
            id=f"emp_{employee_id}",
            type='employee',
            name=profile.name,
            description=f"{profile.role} - Expertise: {', '.join(profile.expertise_areas)}",
            confidence_score=profile.confidence_score,
            last_updated=profile.last_active,
            metadata={
                'role': profile.role,
                'expertise_areas': profile.expertise_areas,
                'hardware_experience': profile.hardware_experience,
                'certifications': profile.certifications
            }
        )
        self.nodes[node.id] = node

    def _update_employee_confidence(self, employee_id: str):
        """Update employee confidence score based on experience factors"""
        profile = self.employee_profiles[employee_id]

        # Base confidence from project count
        project_count = len(profile.project_history)
        base_confidence = min(project_count / 20, 0.8)  # Max 0.8 from projects

        # Bonus for certifications
        cert_bonus = len(profile.certifications) * 0.05
        cert_bonus = min(cert_bonus, 0.15)

        # Bonus for hardware experience
        hw_bonus = len(profile.hardware_experience) * 0.03
        hw_bonus = min(hw_bonus, 0.1)

        # Recency factor (older profiles lose confidence)
        if profile.last_active:
            last_active = datetime.fromisoformat(profile.last_active.replace('Z', '+00:00'))
            days_since_active = (datetime.now() - last_active).days
            recency_factor = max(0.5, 1.0 - (days_since_active / 365))  # Lose 50% over a year
        else:
            recency_factor = 1.0

        profile.confidence_score = (base_confidence + cert_bonus + hw_bonus) * recency_factor
        profile.confidence_score = min(profile.confidence_score, 1.0)

    def add_project_to_graph(self, project_data: Dict[str, Any]):
        """Add a new project to the knowledge graph - dynamic update"""
        project_id = project_data.get('project_id', f"proj_{datetime.now().strftime('%Y%m%d_%H%M%S')}")

        # Create project node
        risk_level = self._calculate_project_risk_level(project_data)
        project_node = KnowledgeNode(
            id=project_id,
            type='project',
            name=f"Project {project_id}",
            description=f"{project_data.get('industry', 'Unknown')} project with {project_data.get('hardware_combination', 'Unknown hardware')}",
            confidence_score=0.9,  # New projects start with high confidence
            last_updated=str(datetime.now()),
            metadata={
                'industry': project_data.get('industry'),
                'hardware_combination': project_data.get('hardware_combination'),
                'estimated_hours': project_data.get('estimated_hours'),
                'actual_hours': project_data.get('actual_hours'),
                'risk_level': risk_level,
                'issues': project_data.get('issues', []),
                'solutions': project_data.get('solutions', [])
            }
        )
        self.nodes[project_id] = project_node

        # Connect to hardware node (create if doesn't exist)
        hw_combo = project_data.get('hardware_combination', 'Unknown')
        hw_node_id = f"hw_{hw_combo.replace(' ', '_').replace('+', '_')}"
        if hw_node_id not in self.nodes:
            hw_node = KnowledgeNode(
                id=hw_node_id,
                type='hardware',
                name=f"Hardware: {hw_combo}",
                description=f"Hardware combination: {hw_combo}",
                confidence_score=0.8,
                last_updated=str(datetime.now())
            )
            self.nodes[hw_node_id] = hw_node

        self._add_edge(project_id, hw_node_id, 'uses_hardware', 1.0)

        # Connect to risk level node
        risk_node_id = f"risk_{risk_level.lower()}"
        if risk_node_id not in self.nodes:
            risk_descriptions = {
                'LOW': 'Projects completed within time and budget with minimal issues',
                'MEDIUM': 'Projects with some overruns or issues but manageable',
                'HIGH': 'Projects with significant overruns, safety issues, or major problems',
                'CRITICAL': 'Projects with severe overruns (>20%), safety failures, or system failures'
            }
            risk_node = KnowledgeNode(
                id=risk_node_id,
                type='risk',
                name=f"Risk Level: {risk_level}",
                description=risk_descriptions.get(risk_level, 'Unknown risk level'),
                confidence_score=0.95,
                last_updated=str(datetime.now())
            )
            self.nodes[risk_node_id] = risk_node

        self._add_edge(project_id, risk_node_id, 'has_risk_level', 1.0)

        # Connect project to involved employees (if provided)
        if 'engineer_id' in project_data:
            emp_id = project_data['engineer_id']
            if emp_id in self.employee_profiles:
                emp_node_id = f"emp_{emp_id}"
                self._add_edge(emp_node_id, project_id, 'worked_on', 1.0)
                self._add_edge(emp_node_id, hw_node_id, 'has_experience', 0.8)

        # Connect to relevant best practices based on issues
        self._connect_to_best_practices(project_id, project_data)

        print(f"🔗 Added project {project_id} to knowledge graph - connected to hardware and risk level")
        self.save_graph()

    def _calculate_project_risk_level(self, project_data: Dict[str, Any]) -> str:
        """Calculate risk level for a project - FORCED calculation, no UNKNOWN allowed"""
        est = project_data.get('estimated_hours')
        act = project_data.get('actual_hours')

        # If we have both actual and estimated hours, use the percentage calculation
        if est is not None and act is not None:
            try:
                overrun_pct = ((act - est) / est) * 100
                if overrun_pct > 20:
                    return "CRITICAL"
                elif overrun_pct > 10:
                    return "HIGH"
                elif overrun_pct > -10:
                    return "MEDIUM"
                else:
                    return "OPTIMAL"
            except:
                pass  # Fall through to fallback logic

        # FORCED FALLBACK: If we don't have actual hours, analyze issues text
        issues_text = ' '.join(project_data.get('issues', [])).lower()

        # Check for Danish risk keywords
        risk_keywords = ['fejl', 'forsinkelse', 'problemer', 'defekt', 'havari', 'svigt', 'forstyrrelse']
        has_risk_indicators = any(keyword in issues_text for keyword in risk_keywords)

        # If we have issues indicating problems, assume HIGH RISK
        if has_risk_indicators:
            return "HIGH"

        # If we have estimated hours but no actual, assume MEDIUM risk (unknown outcome)
        if est is not None:
            return "MEDIUM"

        # Absolute fallback: if no data at all, assume MEDIUM risk
        return "MEDIUM"

    def _connect_to_best_practices(self, project_id: str, project_data: Dict[str, Any]):
        """Connect project to relevant best practices based on issues and hardware"""
        hw = project_data.get('hardware_combination', '').lower()
        issues = ' '.join(project_data.get('issues', [])).lower()

        # Connect to best practices based on hardware
        for node_id, node in self.nodes.items():
            if node.type == 'best_practice':
                # Check if best practice is relevant to hardware
                if any(platform.lower() in hw for platform in ['siemens', 'rockwell', 'abb']):
                    if node.metadata.get('platform', '').lower() in hw:
                        self._add_edge(project_id, node_id, 'should_follow', 0.7)

                # Check if best practice addresses issues
                if 'sil' in issues and 'safety' in node.metadata:
                    self._add_edge(project_id, node_id, 'addresses_issue', 0.9)
                elif 'profinet' in issues and 'profinet' in node.description.lower():
                    self._add_edge(project_id, node_id, 'addresses_issue', 0.9)

    def find_experts_for_hardware(self, hardware_combination: str) -> List[Dict[str, Any]]:
        """Find employees with expertise in specific hardware"""
        experts = []
        for emp_id, profile in self.employee_profiles.items():
            if any(hw.lower() in hardware_combination.lower() for hw in profile.hardware_experience):
                experts.append({
                    'employee_id': emp_id,
                    'name': profile.name,
                    'role': profile.role,
                    'confidence_score': profile.confidence_score,
                    'last_active': profile.last_active
                })

        # Sort by confidence score
        experts.sort(key=lambda x: x['confidence_score'], reverse=True)
        return experts

    def get_risk_assessment(self, hardware_combination: str) -> Dict[str, Any]:
        """Get risk assessment for hardware combination"""
        # Find projects with this hardware
        projects = [node for node in self.nodes.values()
                   if node.type == 'project' and node.metadata.get('hardware_combination') == hardware_combination]

        if not projects:
            return {'risk_level': 'UNKNOWN', 'confidence': 0.0, 'project_count': 0}

        # Calculate average risk
        risk_levels = {'LOW': 1, 'MEDIUM': 2, 'HIGH': 3, 'CRITICAL': 4}
        risk_scores = []

        for project in projects:
            risk_level = project.metadata.get('risk_level', 'UNKNOWN')
            if risk_level in risk_levels:
                risk_scores.append(risk_levels[risk_level])

        if not risk_scores:
            return {'risk_level': 'UNKNOWN', 'confidence': 0.0, 'project_count': len(projects)}

        avg_risk = sum(risk_scores) / len(risk_scores)
        confidence = min(len(projects) / 10, 1.0)  # More projects = higher confidence

        # Convert back to risk level
        if avg_risk >= 3.5:
            risk_level = 'CRITICAL'
        elif avg_risk >= 2.5:
            risk_level = 'HIGH'
        elif avg_risk >= 1.5:
            risk_level = 'MEDIUM'
        else:
            risk_level = 'LOW'

        return {
            'risk_level': risk_level,
            'confidence': confidence,
            'project_count': len(projects),
            'avg_risk_score': avg_risk
        }

    def get_graph_statistics(self) -> Dict[str, Any]:
        """Get statistics about the knowledge graph"""
        node_types = {}
        for node in self.nodes.values():
            node_types[node.type] = node_types.get(node.type, 0) + 1

        relationship_types = {}
        for edge in self.edges:
            relationship_types[edge.relationship_type] = relationship_types.get(edge.relationship_type, 0) + 1

        avg_confidence = sum(node.confidence_score for node in self.nodes.values()) / len(self.nodes) if self.nodes else 0

        return {
            'total_nodes': len(self.nodes),
            'total_edges': len(self.edges),
            'total_employees': len(self.employee_profiles),
            'node_types': node_types,
            'relationship_types': relationship_types,
            'avg_confidence': avg_confidence,
            'last_updated': str(datetime.now())
        }

    def visualize_graph(self, output_file: str = "knowledge_graph.html"):
        """Generate an HTML visualization of the knowledge graph"""
        # Temporarily allow larger graphs for demonstration
        if len(self.nodes) > 50:  # Increased limit to allow current graph
            print(f"Graph too large for visualization ({len(self.nodes)} nodes). Skipping HTML generation.")
            return

        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Industrial Automation Knowledge Graph</title>
    <script src="https://cdn.jsdelivr.net/npm/vis-network@9.1.2/dist/vis-network.min.js"></script>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        #network {{ width: 100%; height: 600px; border: 1px solid #ddd; }}
        .stats {{ background: #f5f5f5; padding: 10px; margin: 10px 0; }}
    </style>
</head>
<body>
    <h1>Industrial Automation Knowledge Graph</h1>
    <div class="stats">
        <h3>Graph Statistics</h3>
        <p>Nodes: {len(self.nodes)}, Edges: {len(self.edges)}, Employees: {len(self.employee_profiles)}</p>
        <p>Average Confidence: {sum(n.get('confidence_score', 0) for n in self.nodes.values()) / len(self.nodes):.2%}</p>
    </div>
    <div id="network"></div>

    <script>
        const nodes = [
"""

        # Add nodes
        for node_id, node in self.nodes.items():
            color_map = {
                'standard': '#4CAF50',
                'best_practice': '#2196F3',
                'employee': '#FF9800',
                'hardware': '#9C27B0',
                'project': '#607D8B',
                'risk': '#F44336'
            }
            node_type = node.get('type', 'unknown')
            color = color_map.get(node_type, '#757575')
            label = node.get('name', node_id)[:25]  # Limit label length
            description = node.get('description', '')[:100]  # Limit description length
            html_content += f'            {{ id: "{node_id}", label: "{label}", color: "{color}", title: "{description}", shape: "dot" }},\n'

        html_content += """
        ];

        const edges = [
"""

        # Add edges
        for edge in self.edges:
            source = edge.get('source_id', '')
            target = edge.get('target_id', '')
            relation = edge.get('relationship_type', 'related')
            html_content += f'            {{ from: "{source}", to: "{target}", label: "{relation}", arrows: "to" }},\n'

        html_content += """
        ];

        const container = document.getElementById('network');
        const data = { nodes: nodes, edges: edges };
        const options = {
            physics: { stabilization: false },
            nodes: { font: { size: 12 } },
            edges: { font: { size: 10, align: 'middle' } }
        };
        new vis.Network(container, data, options);
    </script>
</body>
</html>
"""

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)

        print(f"📊 Knowledge graph visualization saved to {output_file}")

# Integration with persistent learning system
def integrate_with_persistent_learning():
    """Integrate the knowledge graph with the persistent learning system"""

    # Load existing project records
    records_file = "project_records.json"
    if os.path.exists(records_file):
        with open(records_file, 'r', encoding='utf-8') as f:
            records = json.load(f)
    else:
        records = []

    # Initialize knowledge graph
    kg = IntelligentKnowledgeGraph()

    # Add sample employees
    sample_employees = [
        {
            'employee_id': 'EMP001',
            'name': 'Jens Hansen',
            'role': 'Senior PLC Engineer',
            'expertise_areas': ['Siemens S7', 'PROFINET', 'SIL Safety'],
            'hardware_experience': ['Siemens S7-1500', 'WinCC', 'SEW Eurodrive'],
            'project_history': ['Kvæsthusbroen', 'Nordhavn'],
            'certifications': ['Siemens Certified', 'TÜV Functional Safety']
        },
        {
            'employee_id': 'EMP002',
            'name': 'Lars Jensen',
            'role': 'SCADA Specialist',
            'expertise_areas': ['WinCC', 'OPC UA', 'HMI Design'],
            'hardware_experience': ['Siemens WinCC', 'Wonderware'],
            'project_history': ['HOFOR Water Treatment'],
            'certifications': ['Siemens WinCC Expert']
        }
    ]

    for emp in sample_employees:
        kg.add_employee_profile(emp)

    # Add existing projects to graph
    for record in records:
        # Add engineer assignment (simulate)
        record['engineer_id'] = 'EMP001' if 'Siemens' in record.get('hardware_combination', '') else 'EMP002'
        kg.add_project_to_graph(record)

    # Save the integrated system
    kg.save_graph()

    return kg

if __name__ == "__main__":
    # Demonstrate the knowledge graph
    print("🧠 Intelligent Knowledge Graph Demo")
    print("=" * 50)

    kg = integrate_with_persistent_learning()

    # Show some capabilities
    print("\n📊 Graph Statistics:")
    stats = kg.get_graph_statistics()
    for key, value in stats.items():
        print(f"   {key}: {value}")

    # Find experts
    print("\n👨‍💼 Experts for Siemens hardware:")
    experts = kg.find_experts_for_hardware("Siemens + WinCC")
    for exp in experts[:3]:
        print(f"   • {exp['name']} ({exp['role']}) - Confidence: {exp['confidence_score']:.2%}")

    # Risk assessment
    print("\n⚠️ Risk Assessment for Siemens + WinCC:")
    risk = kg.get_risk_assessment("Siemens + WinCC")
    print(f"   Risk Level: {risk['risk_level']}")
    print(f"   Confidence: {risk['confidence']:.2%}")
    print(f"   Based on {risk['project_count']} projects")

    # Generate visualization
    kg.visualize_graph()

    print("\n✅ Knowledge Graph ready! Open 'knowledge_graph.html' to visualize connections.")
    print("💡 The graph automatically updates when new projects are added to project_records.json")