#!/usr/bin/env python3
"""
Quick test script to verify Architecture Review Agent installation
"""

import sys
import os
from pathlib import Path

def test_installation():
    """Test if the Architecture Review Agent is properly installed"""
    
    print("🧪 Testing Architecture Review Agent Installation...")
    print("=" * 60)
    
    # Test 1: Check Python version
    print("1. Python Version Check:")
    if sys.version_info >= (3, 7):
        print(f"   ✅ Python {sys.version.split()[0]} (Compatible)")
    else:
        print(f"   ❌ Python {sys.version.split()[0]} (Requires Python 3.7+)")
        return False
    
    # Test 2: Check main files exist
    print("\n2. File Structure Check:")
    required_files = [
        "architecture_review_agent.py",
        "review_architecture.py", 
        "README.md",
        "requirements.txt",
        "standards/review_rules.json",
        "standards/architecture_patterns.json"
    ]
    
    all_files_exist = True
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ {file_path} (Missing)")
            all_files_exist = False
    
    if not all_files_exist:
        print("\n❌ Some required files are missing!")
        return False
    
    # Test 3: Try importing the main agent
    print("\n3. Module Import Check:")
    try:
        sys.path.insert(0, '.')
        from architecture_review_agent import ArchitectureReviewAgent, ArtifactType
        print("   ✅ Main modules imported successfully")
    except ImportError as e:
        print(f"   ❌ Import failed: {e}")
        return False
    
    # Test 4: Test basic functionality
    print("\n4. Basic Functionality Test:")
    try:
        agent = ArchitectureReviewAgent()
        if hasattr(agent, 'review_artifact') and hasattr(agent, 'generate_review_report'):
            print("   ✅ Agent initialized with required methods")
        else:
            print("   ❌ Agent missing required methods")
            return False
    except Exception as e:
        print(f"   ❌ Agent initialization failed: {e}")
        return False
    
    # Test 5: Test with sample document
    print("\n5. Sample Document Test:")
    if Path("sample_architecture.md").exists():
        try:
            artifact = agent.load_artifact("sample_architecture.md")
            comments = agent.review_artifact(artifact)
            report = agent.generate_review_report(artifact, comments)
            
            print(f"   ✅ Sample document analyzed successfully")
            print(f"   📊 Score: {report['review_summary']['overall_score']}/100")
            print(f"   📝 Issues found: {report['review_summary']['total_comments']}")
        except Exception as e:
            print(f"   ❌ Sample document test failed: {e}")
            return False
    else:
        print("   ⚠️  Sample document not found (optional)")
    
    print("\n" + "=" * 60)
    print("🎉 All tests passed! Architecture Review Agent is ready to use.")
    print("\n🚀 Quick Start:")
    print("   python review_architecture.py sample_architecture.md")
    print("   python review_architecture.py your_document.md report.html")
    
    return True

if __name__ == "__main__":
    try:
        success = test_installation()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n❌ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error during testing: {e}")
        sys.exit(1)
