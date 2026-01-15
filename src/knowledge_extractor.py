import json
import os
import re
from typing import List, Dict, Any
from dataclasses import dataclass, asdict
from .document_parser import ProjectKnowledge, IndustrialAutomationParser
from .config import Config

@dataclass
class KnowledgePattern:
    pattern_type: str  # 'hardware_compatibility', 'time_estimation', 'common_issues'
    industry: str
    hardware_combination: str
    success_rate: float
    avg_time_deviation: float  # actual vs estimated hours
    common_issues: List[str]
    recommended_solutions: List[str]
    confidence_score: float

class KnowledgeExtractor:
    def __init__(self):
        self.config = Config()
        self.parser = IndustrialAutomationParser()
        self.knowledge_base = []

    def extract_from_commissioning_report(self, pdf_path: str) -> ProjectKnowledge:
        """Extract knowledge from commissioning reports"""
        text = self.parser.extract_text_from_pdf(pdf_path)

        # Extract project ID from filename
        project_id = os.path.basename(pdf_path).split()[0]

        # Extract time information
        actual_hours = self._extract_actual_hours(text)
        estimated_hours = self._extract_estimated_hours(text)

        # Extract issues and solutions
        issues = self._extract_issues(text)
        solutions = self._extract_solutions(text)

        # Determine hardware combination and industry
        hardware_combo = self._extract_hardware_combination(text)
        industry = self._classify_industry(text)

        return ProjectKnowledge(
            project_id=project_id,
            actual_hours=actual_hours,
            estimated_hours=estimated_hours,
            issues_encountered=issues,
            solutions_applied=solutions,
            hardware_combination=hardware_combo,
            industry_type=industry
        )

    def _extract_actual_hours(self, text: str) -> float:
        """Extract actual hours from commissioning reports"""
        patterns = [
            # English patterns
            r'actual.*?(?:hours?|time).*?(\d+(?:\.\d+)?)',
            r'commissioning.*?(?:took|required).*?(\d+(?:\.\d+)?).*?hours?',
            r'total.*?(?:hours?|time).*?(\d+(?:\.\d+)?)',
            # Danish patterns
            r'faktisk.*?(?:timer?|tid).*?(\d+(?:[,.]\d+)?)',
            r'ibrugtagning.*?(?:tog|krævede).*?(\d+(?:[,.]\d+)?).*?timer?',
            r'total.*?(?:timer?|tid).*?(\d+(?:[,.]\d+)?)',
            r'brugt.*?(?:timer?|tid).*?(\d+(?:[,.]\d+)?)',
            r'(\d+(?:[,.]\d+)?).*?timer?\s+(?:faktisk|total)',
            r'(\d+(?:[,.]\d+)?).*?timer?\s+(?:blev|var|tog)',  # More flexible Danish
            r'tog.*?(?:faktisk.*?)?(\d+(?:[,.]\d+)?).*?timer?',  # "tog faktisk X timer"
            r'krævede.*?(?:i\s+alt.*?)?(\d+(?:[,.]\d+)?).*?timer?'  # "krævede i alt X timer"
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                # Handle Danish decimal comma
                value_str = match.group(1).replace(',', '.')
                return float(value_str)
        return 0.0

    def _extract_estimated_hours(self, text: str) -> float:
        """Extract estimated hours"""
        patterns = [
            # English patterns
            r'estimat.*?(?:hours?|time).*?(\d+(?:\.\d+)?)',
            r'planned.*?(?:hours?|time).*?(\d+(?:\.\d+)?)',
            # Danish patterns
            r'estimat.*?(?:timer?|tid).*?(\d+(?:[,.]\d+)?)',
            r'planlagt.*?(?:timer?|tid).*?(\d+(?:[,.]\d+)?)',
            r'forventet.*?(?:timer?|tid).*?(\d+(?:[,.]\d+)?)',
            r'beregn.*?(?:timer?|tid).*?(\d+(?:[,.]\d+)?)',
            r'budgetteret.*?(?:timer?|tid).*?(\d+(?:[,.]\d+)?)',
            r'(\d+(?:[,.]\d+)?).*?timer?\s+(?:estimeret|planlagt|forventet)',
            r'(\d+(?:[,.]\d+)?).*?timer?\s+(?:ifølge\s+)?(?:estimat|plan)'
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                # Handle Danish decimal comma
                value_str = match.group(1).replace(',', '.')
                return float(value_str)
        return 0.0

    def _extract_issues(self, text: str) -> List[str]:
        """Extract issues encountered"""
        issue_keywords = [
            # English keywords
            'issue', 'problem', 'error', 'fault', 'failure', 'delay', 'bug', 'defect',
            # Danish keywords
            'fejl', 'problem', 'svigt', 'forsinkelse', 'defekt', 'fejlbehæftet', 'havari',
            'problemer', 'fejlfunktion', 'forstyrrelse', 'afbrydelse', 'funktionsfejl'
        ]
        issues = []

        for keyword in issue_keywords:
            pattern = f'{keyword}.*?([^.]+)'
            matches = re.findall(pattern, text, re.IGNORECASE)
            issues.extend(matches)

        return list(set(issues))

    def _extract_solutions(self, text: str) -> List[str]:
        """Extract solutions applied"""
        solution_keywords = [
            # English keywords
            'solution', 'resolved', 'fixed', 'implemented', 'applied', 'corrected', 'repaired',
            # Danish keywords
            'løsning', 'rettet', 'fikseret', 'implementeret', 'anvendt', 'korrigeret', 'repareret',
            'løst', 'gennemført', 'udført', 'afhjulpet', 'forbedret'
        ]
        solutions = []

        for keyword in solution_keywords:
            pattern = f'{keyword}.*?([^.]+)'
            matches = re.findall(pattern, text, re.IGNORECASE)
            solutions.extend(matches)

        return list(set(solutions))

    def _extract_hardware_combination(self, text: str) -> str:
        """Extract PLC/SCADA hardware combination"""
        plc_patterns = ['Siemens', 'Schneider', 'Rockwell', 'Beckhoff', 'ABB']
        scada_patterns = ['WinCC', 'Wonderware', 'iFix', 'Citect', 'Ignition']

        plc_found = None
        scada_found = None

        for plc in plc_patterns:
            if plc.lower() in text.lower():
                plc_found = plc
                break

        for scada in scada_patterns:
            if scada.lower() in text.lower():
                scada_found = scada
                break

        if plc_found and scada_found:
            return f"{plc_found} + {scada_found}"
        elif plc_found:
            return plc_found
        elif scada_found:
            return scada_found
        else:
            return "Unknown"

    def _classify_industry(self, text: str) -> str:
        """Classify industry type"""
        industries = {
            'pharma': [
                # English
                'pharma', 'pharmaceutical', 'medic', 'drug',
                # Danish
                'medicinal', 'lægemiddel', 'farmakologi'
            ],
            'food': [
                # English
                'food', 'beverage', 'dairy', 'brewery',
                # Danish
                'fødevare', 'drikkevare', 'mejeri', 'bryggeri', 'levnedsmiddel'
            ],
            'energy': [
                # English
                'energy', 'power', 'utility', 'hofor',
                # Danish
                'energi', 'kraft', 'forsyning', 'elforsyning', 'varmeforsyning'
            ],
            'water': [
                # English
                'water', 'wastewater', 'sewage', 'treatment',
                # Danish
                'vand', 'vandværk', 'spildevand', 'rensningsanlæg', 'renseanlæg',
                'vandforsyning', 'affaldsvand', 'dræning', 'behandling'
            ],
            'chemical': [
                # English
                'chemical', 'petro', 'refinery',
                # Danish
                'kemikalie', 'kemisk', 'raffinaderi', 'petrokemisk', 'procesindustri'
            ]
        }

        for industry, keywords in industries.items():
            for keyword in keywords:
                if keyword.lower() in text.lower():
                    return industry

        return "general"

    def analyze_patterns(self, projects: List[ProjectKnowledge]) -> List[KnowledgePattern]:
        """Analyze patterns across completed projects"""
        patterns = []

        # Group by hardware combination and industry
        hardware_groups = {}
        for project in projects:
            key = (project.hardware_combination, project.industry_type)
            if key not in hardware_groups:
                hardware_groups[key] = []
            hardware_groups[key].append(project)

        for (hardware, industry), project_list in hardware_groups.items():
            if len(project_list) < 2:  # Need at least 2 projects for pattern analysis
                continue

            # Calculate success metrics
            time_deviations = []
            all_issues = []
            all_solutions = []

            for project in project_list:
                if project.estimated_hours > 0:
                    deviation = (project.actual_hours - project.estimated_hours) / project.estimated_hours
                    time_deviations.append(deviation)
                all_issues.extend(project.issues_encountered)
                all_solutions.extend(project.solutions_applied)

            success_rate = len([p for p in project_list if p.actual_hours <= p.estimated_hours * 1.2]) / len(project_list)
            avg_time_deviation = sum(time_deviations) / len(time_deviations) if time_deviations else 0

            pattern = KnowledgePattern(
                pattern_type="hardware_compatibility",
                industry=industry,
                hardware_combination=hardware,
                success_rate=success_rate,
                avg_time_deviation=avg_time_deviation,
                common_issues=list(set(all_issues))[:5],  # Top 5 issues
                recommended_solutions=list(set(all_solutions))[:5],  # Top 5 solutions
                confidence_score=min(len(project_list) / 10, 1.0)  # Confidence based on sample size
            )

            patterns.append(pattern)

        return patterns

    def save_knowledge_base(self, filename: str = "knowledge_base.json"):
        """Save extracted knowledge to file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump([asdict(p) for p in self.knowledge_base], f, indent=2, ensure_ascii=False)