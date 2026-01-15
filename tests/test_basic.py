#!/usr/bin/env python3

# Simple test script to verify basic functionality

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from src.config import Config
    print("✓ Config module loaded successfully")
    config = Config()
    print(f"✓ Config initialized - documents dir: {config.DOCUMENTS_DIR}")
except Exception as e:
    print(f"✗ Config failed: {e}")
    sys.exit(1)

try:
    from src.document_parser import IndustrialAutomationParser, TechnicalRequirements
    print("✓ Document parser module loaded successfully")
except Exception as e:
    print(f"✗ Document parser module failed: {e}")
    sys.exit(1)

try:
    # Test basic functionality without external dependencies
    parser = IndustrialAutomationParser()
    print("✓ Parser initialized successfully")

    # Test text analysis
    test_text = """
    AI001 Temperature sensor
    DI005 Motor status
    Profinet communication
    100ms response time
    High availability required
    """

    io_points = parser.extract_io_points(test_text)
    print(f"✓ I/O extraction works: {io_points}")

    protocols = parser.extract_protocols(test_text)
    print(f"✓ Protocol extraction works: {protocols}")

    response_times = parser.extract_response_times(test_text)
    print(f"✓ Response time extraction works: {response_times}")

    redundancy = parser.extract_redundancy_requirements(test_text)
    print(f"✓ Redundancy extraction works: {redundancy}")

except Exception as e:
    print(f"✗ Basic functionality failed: {e}")
    import traceback
    traceback.print_exc()

print("Basic functionality test completed!")