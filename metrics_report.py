#!/usr/bin/env python3
"""
metrics_report.py
Produce human-readable metrics for:
 - persistent learning (storage/persistent_patterns.json / storage/project_records.json)
 - Chroma index (./storage/chroma_db)
 - Knowledge Graph (storage/knowledge_graph.json)
"""
import json
import os
import sys
import re
from collections import Counter, defaultdict

# Add src directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

PERSISTENT_FILE = "storage/persistent_patterns.json"
RECORDS_FILE = "storage/project_records.json"
CHROMA_DIR = "./chroma_db"

def load_json(path):
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error reading {path}: {e}")
        return []

def patterns_metrics(patterns):
    if not patterns:
        return {}
    total = len(patterns)
    avg_success = sum(p.get("success_rate", 0) for p in patterns) / total
    avg_time_dev = sum(p.get("avg_time_deviation", 0) for p in patterns) / total
    avg_sample = sum(p.get("sample_size", p.get("project_count", 1)) for p in patterns) / total
    by_industry = Counter(p.get("industry", "unknown") for p in patterns)
    issues = Counter()
    sols = Counter()
    for p in patterns:
        for i in p.get("common_issues", []):
            issues[i.strip()] += 1
        for s in p.get("recommended_solutions", []):
            sols[s.strip()] += 1
    return {
        "patterns_count": total,
        "avg_success_rate": avg_success,
        "avg_time_deviation": avg_time_dev,
        "avg_sample_size": avg_sample,
        "by_industry": dict(by_industry.most_common()),
        "top_issues": issues.most_common(10),
        "top_solutions": sols.most_common(10),
    }

def records_metrics(records):
    if not records:
        return {}
    total_projects = len(records)
    ests = [r.get("estimated_hours") for r in records if r.get("estimated_hours")]
    acts = [r.get("actual_hours") for r in records if r.get("actual_hours")]
    avg_est = sum(ests)/len(ests) if ests else None
    avg_act = sum(acts)/len(acts) if acts else None
    by_hardware = Counter(r.get("hardware_combination","unknown") for r in records)
    by_industry = Counter(r.get("industry","unknown") for r in records)
    return {
        "total_projects": total_projects,
        "avg_estimated_hours": avg_est,
        "avg_actual_hours": avg_act,
        "by_hardware_top": by_hardware.most_common(8),
        "by_industry_top": by_industry.most_common(8),
    }

def chroma_metrics():
    try:
        import chromadb
        client = chromadb.PersistentClient(path=CHROMA_DIR)
        coll = client.get_or_create_collection(name="industrial_automation_kb")
        try:
            n = coll.count()
        except Exception:
            n = "unknown"
        sqlite_path = os.path.join(CHROMA_DIR, "chroma.sqlite3")
        db_size_bytes = os.path.getsize(sqlite_path) if os.path.exists(sqlite_path) else None
        return {"chroma_collection_name": coll.name, "num_items": n, "sqlite_bytes": db_size_bytes}
    except Exception as e:
        return {"error": f"Chroma unavailable or failed: {e}"}

def print_report():
    print("=== Persistent patterns metrics ===")
    patterns = load_json(PERSISTENT_FILE)
    pm = patterns_metrics(patterns)
    if not pm:
        print("No persistent patterns found.")
    else:
        print(f"Patterns: {pm['patterns_count']}")
        print(f"Average success rate: {pm['avg_success_rate']:.2%}")
        print(f"Average time deviation: {pm['avg_time_deviation']:.2%}")
        print(f"Average sample size: {pm['avg_sample_size']:.1f}")
        # warn if patterns have small sample sizes
        small = [p for p in patterns if (p.get('project_count', p.get('sample_size', 0)) < 5)]
        if small:
            print("\n⚠️ Warning: Some patterns have low sample sizes (<5). Treat success rates as unreliable for these:")
            for p in small:
                pc = p.get('project_count', p.get('sample_size', 0))
                conf = min(pc/10, 1.0)
                print(f"  - {p.get('hardware_combination','?')} in {p.get('industry','?')} (count={pc}, confidence={conf:.2%})")
        print("Top industries:", pm["by_industry"])
        print("Top issues (sample):")
        for it, c in pm["top_issues"][:8]:
            print(f"  - {it[:120]} ({c})")
        print("Top solutions (sample):")
        for s, c in pm["top_solutions"][:8]:
            print(f"  - {s[:120]} ({c})")

    print("\n=== Project records metrics ===")
    records = load_json(RECORDS_FILE)
    rm = records_metrics(records)
    if not rm:
        print("No project records found.")
    else:
        print(f"Total projects: {rm['total_projects']}")
        print(f"Avg estimated hours: {rm['avg_estimated_hours']}")
        print(f"Avg actual hours: {rm['avg_actual_hours']}")
        print("Top hardware combos:", rm["by_hardware_top"])
        print("Top industries:", rm["by_industry_top"])

    print("\n=== Chroma DB metrics ===")
    # Skip ChromaDB metrics to avoid segfaults in this environment
    print("ChromaDB metrics temporarily disabled (run 'python -c \"import chromadb; print(\'Chroma available\')\"' to test)")

    # Temporarily disabled knowledge graph metrics to avoid segfaults
    print("\n=== Knowledge Graph ===")
    kg_file = "storage/knowledge_graph.json"
    if os.path.exists(kg_file):
        print(f"Knowledge graph exists: {kg_file}")
        print("Run 'python test_knowledge_graph.py' for detailed analysis")
    else:
        print("Knowledge graph not yet created (run persistent_learning_system.py to generate it)")

if __name__ == "__main__":
    print_report()