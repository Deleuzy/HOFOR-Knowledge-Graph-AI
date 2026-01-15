#!/usr/bin/env python3
"""
Persistent Learning RAG System - JSON-based
Demonstrates real learning that persists between runs
"""

import json
import os
import sys
import re
from collections import Counter
from typing import Dict, List, Any
from dataclasses import dataclass, asdict, field
from datetime import datetime

# Add src directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.knowledge_graph import IntelligentKnowledgeGraph

# Danish language support
DANISH_ISSUE_KEYWORDS = [
    'fejl', 'problem', 'svigt', 'forsinkelse', 'defekt', 'havari',
    'problemer', 'fejlfunktion', 'forstyrrelse', 'afbrydelse', 'funktionsfejl'
]

DANISH_SOLUTION_KEYWORDS = [
    'løsning', 'rettet', 'fikseret', 'implementeret', 'anvendt', 'korrigeret',
    'løst', 'gennemført', 'udført', 'afhjulpet', 'forbedret'
]

@dataclass
class LearningPattern:
    industry: str
    hardware_combination: str
    success_rate: float
    common_issues: List[str]
    recommended_solutions: List[str]
    project_count: int
    last_updated: str
    risk_drivers: List[str] = field(default_factory=list)

class PersistentKnowledgeBase:
    def __init__(self, storage_file: str = "storage/persistent_patterns.json"):
        self.storage_file = storage_file
        self.patterns = []
        self.load_patterns()

    def load_patterns(self):
        """Load patterns from JSON file"""
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.patterns = [LearningPattern(**p) for p in data]
                print(f"📚 Loaded {len(self.patterns)} learning patterns from {self.storage_file}")
            except Exception as e:
                print(f"⚠️ Could not load patterns: {e}")
                self.patterns = []
        else:
            print("🆕 No existing patterns found - starting fresh")
            self.patterns = []

    def save_patterns(self):
        """Save patterns to JSON file"""
        try:
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump([asdict(p) for p in self.patterns], f, indent=2, ensure_ascii=False)
            print(f"💾 Saved {len(self.patterns)} patterns to {self.storage_file}")
        except Exception as e:
            print(f"❌ Could not save patterns: {e}")

    def find_similar_patterns(self, requirements: Dict[str, Any]) -> List[LearningPattern]:
        """Find patterns that match the requirements"""
        matching_patterns = []

        # Check for protocol matches
        protocols = requirements.get('protocols', [])
        if 'PROFINET' in protocols:
            matching_patterns.extend([p for p in self.patterns if 'Siemens' in p.hardware_combination])

        if 'MODBUS' in protocols:
            matching_patterns.extend([p for p in self.patterns if 'Rockwell' in p.hardware_combination])

        # Check for redundancy requirements
        redundancy = requirements.get('redundancy_requirements', [])
        if redundancy:
            matching_patterns.extend([p for p in self.patterns if p.success_rate > 0.8])

        # Remove duplicates
        seen = set()
        unique_patterns = []
        for pattern in matching_patterns:
            pattern_key = (pattern.industry, pattern.hardware_combination)
            if pattern_key not in seen:
                seen.add(pattern_key)
                unique_patterns.append(pattern)

        return unique_patterns

    def learn_from_project(self, project_data: Dict[str, Any]):
        """Learn from a completed project"""
        industry = project_data.get('industry', 'general')
        hardware = project_data.get('hardware_combination', 'Unknown')
        # Structured inputs
        raw_success = project_data.get('success', None)
        issues = project_data.get('issues', [])
        solutions = project_data.get('solutions', [])
        est = project_data.get('estimated_hours')
        act = project_data.get('actual_hours')
        tests = project_data.get('test_results', [])
        tickets = project_data.get('support_tickets', [])

        # Normalize issue/solution strings to short phrases
        def normalize_list(str_list):
            out = []
            for s in str_list:
                if not s:
                    continue
                t = re.sub(r'\\s+', ' ', s.replace('\\n', ' ')).strip()
                # take first sentence or up to 140 chars
                first = t.split('.', 1)[0][:140].strip()
                out.append(first)
            return list(dict.fromkeys(out))  # unique, preserve order

        issues = normalize_list(issues)
        solutions = normalize_list(solutions)

        # Determine success with stricter rules:
        # - time_ok: actual <= 1.1 * estimated when both present
        # - test_ok: if tests present, require >=80% passed
        # - ticket_ok: if tickets present, require none unresolved
        time_ok = False
        if est is not None and act is not None:
            try:
                time_ok = float(act) <= 1.1 * float(est)
            except Exception:
                time_ok = False

        test_ok = True
        if tests:
            passed = sum(1 for t in tests if t.get('passed'))
            test_ok = (passed / max(1, len(tests))) >= 0.8

        ticket_ok = True
        if tickets:
            ticket_ok = not any(not t.get('resolved', False) for t in tickets)

        # Final success decision:
        if raw_success is not None:
            success = bool(raw_success)
        else:
            # If we have any structured evidence, require them to pass
            if tests or tickets or (est is not None and act is not None):
                success = time_ok and test_ok and ticket_ok
            else:
                # No structured evidence -> treat as unknown -> False to avoid overconfidence
                success = False

        # Find existing pattern or create new one
        existing_pattern = None
        for pattern in self.patterns:
            if pattern.industry == industry and pattern.hardware_combination == hardware:
                existing_pattern = pattern
                break

        if existing_pattern:
            # Update existing pattern
            existing_pattern.project_count += 1
            # Update success rate (weighted average)
            total_projects = existing_pattern.project_count
            existing_pattern.success_rate = ((existing_pattern.success_rate * (total_projects - 1)) + (1.0 if success else 0.0)) / total_projects

            # Add new issues and solutions
            existing_pattern.common_issues.extend(issues)
            existing_pattern.recommended_solutions.extend(solutions)

            # Keep only top 5 most common
            # normalize and keep top 5
            existing_pattern.common_issues = normalize_list(existing_pattern.common_issues)[:5]
            existing_pattern.recommended_solutions = normalize_list(existing_pattern.recommended_solutions)[:5]

            existing_pattern.last_updated = str(datetime.now())

            print(f"🔄 Updated existing pattern for {hardware} in {industry} industry")

        else:
            # Create new pattern
            new_pattern = LearningPattern(
                industry=industry,
                hardware_combination=hardware,
                success_rate=1.0 if success else 0.0,
                common_issues=issues[:5],
                recommended_solutions=solutions[:5],
                project_count=1,
                last_updated=str(datetime.now())
            )
            self.patterns.append(new_pattern)
            print(f"🆕 Created new learning pattern for {hardware} in {industry} industry")

        # Save updated patterns
        # If we have estimated and actual hours, compute risk drivers for high-risk projects (>=20% over)
        try:
            if est is not None and act is not None:
                pct = (float(act) - float(est)) / float(est) * 100.0
                if pct >= 20.0:
                    # extract simple keywords from issues and add as risk_drivers
                    kw_counter = Counter()
                    for txt in issues:
                        tokens = re.findall(r'[A-Za-zÆØÅæøå0-9\-]+', txt)
                        for t in tokens:
                            tt = t.lower()
                            if len(tt) <= 2:
                                continue
                            kw_counter[tt] += 1
                    top = [k for k, _ in kw_counter.most_common(6)]
                    # attach to existing or newly created pattern
                    target_pattern = existing_pattern if existing_pattern else new_pattern
                    if top:
                        prev = getattr(target_pattern, "risk_drivers", []) or []
                        merged = list(dict.fromkeys(prev + top))[:6]
                        target_pattern.risk_drivers = merged
        except Exception:
            pass

        self.save_patterns()

class DanishDocumentAnalyzer:
    def __init__(self):
        self.knowledge_base = PersistentKnowledgeBase()
        self.knowledge_graph = IntelligentKnowledgeGraph()

    def analyze_danish_document(self, document_text: str, document_name: str = "unknown") -> Dict[str, Any]:
        """Analyze a Danish document and learn from it"""

        # Extract information using Danish keywords
        issues = self._extract_issues(document_text)
        solutions = self._extract_solutions(document_text)
        times = self._extract_times(document_text)
        hardware = self._extract_hardware(document_text)
        industry = self._classify_industry(document_text)

        # Extract technical requirements
        requirements = {
            'io_points': self._extract_io_points(document_text),
            'protocols': self._extract_protocols(document_text),
            'response_times': self._extract_response_times(document_text),
            'redundancy_requirements': self._extract_redundancy(document_text)
        }

        # Find similar patterns
        similar_patterns = self.knowledge_base.find_similar_patterns(requirements)

        # Generate analysis
        analysis = {
            'document_name': document_name,
            'extracted_data': {
                'issues': issues,
                'solutions': solutions,
                'time_info': times,
                'hardware': hardware,
                'industry': industry,
                'requirements': requirements
            },
            'similar_patterns': len(similar_patterns),
            'learning_insights': self._generate_insights(similar_patterns, requirements),
            'confidence_score': min(len(similar_patterns) / 5, 1.0)
        }

        return analysis

    def learn_from_danish_project(self, project_data: Dict[str, Any]):
        """Learn from a completed Danish project"""
        # First learn in the existing system
        self.knowledge_base.learn_from_project(project_data)

        # Then add to knowledge graph for dynamic connections
        self.knowledge_graph.add_project_to_graph(project_data)

    def _extract_issues(self, text: str) -> List[str]:
        """Extract Danish issues"""
        issues = []
        for keyword in DANISH_ISSUE_KEYWORDS:
            pattern = f'{keyword}.*?([^.]+)'
            matches = re.findall(pattern, text, re.IGNORECASE)
            issues.extend(matches)
        return list(set(issues))

    def _extract_solutions(self, text: str) -> List[str]:
        """Extract Danish solutions"""
        solutions = []
        for keyword in DANISH_SOLUTION_KEYWORDS:
            pattern = f'{keyword}.*?([^.]+)'
            matches = re.findall(pattern, text, re.IGNORECASE)
            solutions.extend(matches)
        return list(set(solutions))

    def _extract_times(self, text: str) -> Dict[str, Any]:
        """Extract time information"""
        actual_patterns = [r'faktisk.*?(?:timer?|tid).*?(\d+(?:[,.]\d+)?)']
        estimate_patterns = [r'planlagt.*?(?:timer?|tid).*?(\d+(?:[,.]\d+)?)']

        actual_hours = None
        estimated_hours = None

        for pattern in actual_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                actual_hours = float(match.group(1).replace(',', '.'))
                break

        for pattern in estimate_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                estimated_hours = float(match.group(1).replace(',', '.'))
                break

        return {'actual': actual_hours, 'estimated': estimated_hours}

    def _extract_hardware(self, text: str) -> List[str]:
        """Extract hardware mentions"""
        hardware_brands = ['Siemens', 'WinCC', 'Rockwell', 'Wonderware', 'SEW Eurodrive', 'Endress+Hauser']
        found = [brand for brand in hardware_brands if brand.lower() in text.lower()]
        return found

    def _classify_industry(self, text: str) -> str:
        """Classify industry from Danish text"""
        industries = {
            'water': ['vand', 'vandværk', 'spildevand', 'rensningsanlæg', 'hofor'],
            'energy': ['energi', 'kraft', 'forsyning', 'elforsyning', 'varmeforsyning'],
            'pharma': ['medicinal', 'lægemiddel', 'farmakologi'],
            'food': ['fødevare', 'drikkevare', 'mejeri', 'bryggeri', 'levnedsmiddel']
        }

        for industry, keywords in industries.items():
            for keyword in keywords:
                if keyword.lower() in text.lower():
                    return industry
        return "general"

    def _extract_io_points(self, text: str) -> Dict[str, List[str]]:
        """Extract I/O points"""
        io_patterns = {
            'analog_input': r'AI\d+',
            'digital_input': r'DI\d+',
            'digital_output': r'DO\d+',
            'safety_input': r'SI\d+'
        }
        io_points = {}
        for io_type, pattern in io_patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                io_points[io_type] = list(set(matches))
        return io_points

    def _extract_protocols(self, text: str) -> List[str]:
        """Extract communication protocols"""
        protocols = []
        protocol_patterns = ['profinet', 'modbus', 'opc.?ua']
        for pattern in protocol_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                protocols.append(pattern.upper())
        return protocols

    def _extract_response_times(self, text: str) -> List[str]:
        """Extract response times"""
        patterns = [r'\d+ms.*?response', r'\d+ms.*?cycle']
        times = []
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            times.extend(matches)
        return list(set(times))

    def _extract_redundancy(self, text: str) -> List[str]:
        """Extract redundancy requirements"""
        patterns = [r'high.availability', r'redundan', r'safety.integrity.level']
        requirements = []
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            requirements.extend(matches)
        return list(set(requirements))

    def _generate_insights(self, similar_patterns: List[LearningPattern], requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Generate insights based on similar patterns"""
        insights = {
            'risk_assessment': "Low risk - standard requirements",
            'recommendations': [],
            'time_estimation': "120-160 hours (standard project)",
            'success_prediction': 0.8
        }

        if similar_patterns:
            # Use the best pattern for recommendations
            best_pattern = max(similar_patterns, key=lambda p: p.success_rate)

            insights['recommendations'].append(f"Consider {best_pattern.hardware_combination} (proven in {best_pattern.industry} industry)")

            if best_pattern.success_rate < 0.8:
                insights['risk_assessment'] = f"Medium risk - similar projects had {best_pattern.success_rate:.1%} success rate"

            insights['success_prediction'] = best_pattern.success_rate

        # Add protocol-specific recommendations
        if 'PROFINET' in requirements.get('protocols', []):
            insights['recommendations'].append("Use Profinet ring topology with MRP for redundancy")
            insights['time_estimation'] = "140-180 hours (+20% for Profinet setup)"

        return insights

def demonstrate_persistent_learning():
    """Demonstrate persistent learning across multiple runs"""

    print("🧠 Persistent Learning RAG System Demo")
    print("=" * 50)

    analyzer = DanishDocumentAnalyzer()

    # Show current learning state
    print(f"📊 Current Knowledge Base: {len(analyzer.knowledge_base.patterns)} patterns")

    # Sample Danish HOFOR commissioning report
    danish_hofor_report = """
    HOFOR Kvæsthusbroen Projekt - Ibrugtagning Rapport

    Projektet blev afsluttet med følgende resultater:

    Tidsforbrug:
    - Planlagt tid: 120 timer
    - Faktisk forbrug: 145,5 timer
    - Forsinkelse skyldtes problemer med Profinet kommunikation

    Problemer oplevet:
    - Fejl i sikkerhedssystemet (SIL 2 krav ikke opfyldt)
    - Forsinkelse i I/O konfiguration (DI005, AI001 signalkonflikter)
    - Defekt i frekvensomformer fra SEW Eurodrive

    Løsninger implementeret:
    - Kommunikationsproblemet blev løst ved at opgradere Profinet switch
    - Sikkerhedssystemet er nu rettet og certificeret
    - I/O konflikter er fikseret i den endelige konfiguration
    - Reservedele til frekvensomformere er bestilt

    Hardware anvendt:
    - Siemens S7-1500 PLC med Profinet
    - WinCC SCADA system
    - SEW Eurodrive frekvensomformere
    - Endress+Hauser tryktransmittere

    Anbefalinger til fremtidige projekter:
    - Øg tidsestimat med 20% for Profinet konfiguration
    - Inkluder ekstra testtid for SIL sikkerhedssystemer
    - Bestil reservedele på forhånd for SEW komponenter
    """

    # Analyze the document
    print("\n📄 Analyzing Danish HOFOR Commissioning Report...")
    analysis = analyzer.analyze_danish_document(danish_hofor_report, "Kvæsthusbroen_Commissioning")

    print("✅ Extracted Issues:", len(analysis['extracted_data']['issues']))
    print("✅ Extracted Solutions:", len(analysis['extracted_data']['solutions']))
    print("✅ Time Info:", analysis['extracted_data']['time_info'])
    print("✅ Hardware Found:", analysis['extracted_data']['hardware'])
    print("✅ Industry Classified:", analysis['extracted_data']['industry'])
    print("✅ Similar Patterns Found:", analysis['similar_patterns'])
    print("✅ Confidence Score:", f"{analysis['confidence_score']:.1%}")

    # Learn from this project
    print("\n🎓 Learning from this Danish HOFOR project...")
    project_learning = {
        'industry': analysis['extracted_data']['industry'],
        'hardware_combination': 'Siemens + WinCC',  # Most common in extracted hardware
        'success': True,  # Assume successful completion
        'issues': analysis['extracted_data']['issues'][:3],  # Top 3 issues
        'solutions': analysis['extracted_data']['solutions'][:3]  # Top 3 solutions
    }

    # Persist project record for metrics and tracking
    records_file = "storage/project_records.json"
    try:
        existing_records = json.load(open(records_file, 'r', encoding='utf-8'))
    except Exception:
        existing_records = []

    # If actual hours missing, prompt the user for a value (interactive fallback)
    estimated_val = analysis['extracted_data']['time_info'].get('estimated')
    actual_val = analysis['extracted_data']['time_info'].get('actual')
    if actual_val is None:
        try:
            user_input = input(f"No actual hours extracted (estimated {estimated_val}). "
                               "Enter actual hours now or leave blank to skip: ").strip()
            if user_input:
                actual_val = float(user_input.replace(',', '.'))
                print(f"Using actual_hours={actual_val}")
            else:
                actual_val = None
                print("No actual hours provided; leaving as null.")
        except Exception as e:
            print(f"Invalid input, leaving actual_hours as null ({e})")
            actual_val = None

    record = {
        "project_id": f"Kvaesthus_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "industry": project_learning.get("industry"),
        "hardware_combination": project_learning.get("hardware_combination"),
        "estimated_hours": estimated_val,
        "actual_hours": actual_val,
        "issues": project_learning.get("issues", []),
        "solutions": project_learning.get("solutions", []),
        "test_results": project_learning.get("test_results", []),
        "support_tickets": project_learning.get("support_tickets", []),
        "date": str(datetime.now())
    }

    existing_records.append(record)
    try:
        with open(records_file, 'w', encoding='utf-8') as rf:
            json.dump(existing_records, rf, indent=2, ensure_ascii=False)
        print(f"💾 Appended project record to {records_file}")
    except Exception as e:
        print(f"❌ Failed to append project record: {e}")

    analyzer.learn_from_danish_project(project_learning)

    # Show updated knowledge base
    print(f"\n📈 Updated Knowledge Base: {len(analyzer.knowledge_base.patterns)} patterns")

    # Demonstrate that learning persists
    print("\n🔄 Testing Persistence - Creating new analyzer instance...")
    new_analyzer = DanishDocumentAnalyzer()
    print(f"✅ Loaded {len(new_analyzer.knowledge_base.patterns)} patterns from file")

    # Analyze a similar document to show improved recommendations
    similar_project = """
    Nyt HOFOR projekt - Vandbehandlingssystem

    Planlagt tid: 130 timer
    Hardware: Siemens S7-1500, WinCC, Profinet kommunikation
    Krav: SIL 2 sikkerhed, redundans
    """

    print("\n📄 Analyzing Similar Danish HOFOR Project...")
    similar_analysis = new_analyzer.analyze_danish_document(similar_project, "New_HOFOR_Project")

    print("🎯 Smart Recommendations based on learned patterns:")
    for rec in similar_analysis['learning_insights']['recommendations']:
        print(f"   • {rec}")

    print("\n⚡ Success! The system now has persistent learning!")
    print("   - Remembers patterns between runs")
    print("   - Improves recommendations over time")
    print("   - Learns from Danish HOFOR projects")
    print("   - Uses JSON file storage (no complex dependencies)")

    print("\n📁 Check 'storage/persistent_patterns.json' to see the learned knowledge!")
if __name__ == "__main__":
    demonstrate_persistent_learning()