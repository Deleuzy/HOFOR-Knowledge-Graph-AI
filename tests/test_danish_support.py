#!/usr/bin/env python3
"""
Test script to verify Danish language support in the Self-Learning Impact Analysis System
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.knowledge_extractor import KnowledgeExtractor

def test_danish_issue_extraction():
    """Test extraction of Danish issue keywords"""
    extractor = KnowledgeExtractor()

    # Test Danish text with various issue keywords
    danish_text = """
    Projektet havde flere problemer under implementeringen.
    Der opstod en fejl i kommunikationsprotokollen.
    Forsinkelsen skyldtes defekte komponenter.
    Systemet havde svigt i sikkerhedsfunktionerne.
    Der var funktionsfejl i PLC-programmeringen.
    """

    issues = extractor._extract_issues(danish_text)
    print("🧪 Danish Issue Extraction Test:")
    print(f"Text: {danish_text.strip()}")
    print(f"Extracted issues: {issues}")

    # Check if Danish keywords were found
    expected_danish_words = ['problemer', 'fejl', 'forsinkelsen', 'defekte', 'svigt', 'funktionsfejl']
    found_danish = any(any(word in issue.lower() for word in expected_danish_words) for issue in issues)

    if found_danish:
        print("✅ Danish issue keywords detected successfully!")
    else:
        print("❌ Danish issue keywords not detected")

    return found_danish

def test_danish_solution_extraction():
    """Test extraction of Danish solution keywords"""
    extractor = KnowledgeExtractor()

    # Test Danish text with solution keywords
    danish_text = """
    Problemet blev løst ved at opdatere firmware.
    Fejlen er nu rettet i den nye version.
    Kommunikationsproblemet er fikseret.
    Sikkerhedssystemet er implementeret korrekt.
    """

    solutions = extractor._extract_solutions(danish_text)
    print("\n🧪 Danish Solution Extraction Test:")
    print(f"Text: {danish_text.strip()}")
    print(f"Extracted solutions: {solutions}")

    # Check if Danish keywords were found
    expected_danish_words = ['løst', 'rettet', 'fikseret', 'implementeret']
    found_danish = any(any(word in solution.lower() for word in expected_danish_words) for solution in solutions)

    if found_danish:
        print("✅ Danish solution keywords detected successfully!")
    else:
        print("❌ Danish solution keywords not detected")

    return found_danish

def test_danish_industry_classification():
    """Test Danish industry classification"""
    extractor = KnowledgeExtractor()

    test_cases = [
        ("HOFOR vandværksprojekt med spildevandsbehandling", "water"),
        ("Medicinal produktion og lægemiddel fremstilling", "pharma"),
        ("Fødevare industri og bryggeri proces", "food"),
        ("Elforskyning og energiproduktion", "energy"),
        ("Kemisk proces og raffinaderi", "chemical")
    ]

    print("\n🧪 Danish Industry Classification Test:")
    all_passed = True

    for text, expected_industry in test_cases:
        industry = extractor._classify_industry(text)
        status = "✅" if industry == expected_industry else "❌"
        print(f"{status} '{text}' → {industry} (expected: {expected_industry})")
        if industry != expected_industry:
            all_passed = False

    if all_passed:
        print("✅ All Danish industry classifications working!")
    else:
        print("❌ Some Danish industry classifications failed")

    return all_passed

def test_danish_time_extraction():
    """Test Danish time extraction patterns"""
    extractor = KnowledgeExtractor()

    test_cases = [
        ("Projektet tog faktisk 45,5 timer at gennemføre", 45.5),
        ("Estimerede timer var 32,0 ifølge planen", 32.0),
        ("Ibrugtagningen krævede 28 timer total", 28.0),
        ("Brugt tid: 67,5 timer på fejlfinding", 67.5)
    ]

    print("\n🧪 Danish Time Extraction Test:")
    all_passed = True

    for text, expected_hours in test_cases:
        actual_hours = extractor._extract_actual_hours(text)
        estimated_hours = extractor._extract_estimated_hours(text)

        # Check if either extraction worked
        extracted = actual_hours if actual_hours > 0 else estimated_hours
        status = "✅" if abs(extracted - expected_hours) < 0.01 else "❌"
        print(f"{status} '{text}' → {extracted}h (expected: {expected_hours}h)")

        if abs(extracted - expected_hours) >= 0.01:
            all_passed = False

    if all_passed:
        print("✅ All Danish time extractions working!")
    else:
        print("❌ Some Danish time extractions failed")

    return all_passed

def main():
    print("🇩🇰 Danish Language Support Test for RAG System")
    print("=" * 55)

    tests = [
        test_danish_issue_extraction,
        test_danish_solution_extraction,
        test_danish_industry_classification,
        test_danish_time_extraction
    ]

    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
            results.append(False)

    print("\n" + "=" * 55)
    passed = sum(results)
    total = len(results)
    print(f"📊 Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All Danish language support tests passed!")
        print("Your system is now ready for Danish HOFOR documents! 🇩🇰")
    else:
        print("⚠️ Some tests failed. Danish support may need further tuning.")

if __name__ == "__main__":
    main()