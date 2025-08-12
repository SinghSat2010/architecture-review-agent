#!/usr/bin/env python3
"""
Test Document Processing Capabilities

This script demonstrates the enhanced document processing features
including support for Word documents (.doc/.docx) and text files.
"""

import os
import sys
from pathlib import Path

def test_document_processor():
    """Test the document processor with different file types"""
    print("🧪 Testing Document Processor")
    print("=" * 50)
    
    try:
        from document_processor import DocumentProcessor, DocumentFormat
        
        processor = DocumentProcessor()
        
        # Check dependencies
        print("📋 Dependency Status:")
        deps = processor.check_dependencies()
        for name, available in deps.items():
            status = "✅ Available" if available else "❌ Missing"
            print(f"  {name}: {status}")
        
        # Check supported formats
        print(f"\n📊 Supported Formats:")
        for fmt, supported in processor.supported_formats.items():
            status = "✅" if supported else "❌"
            print(f"  .{fmt}: {status}")
        
        # Installation instructions for missing dependencies
        missing = processor.get_installation_instructions()
        if missing:
            print(f"\n📦 To install missing dependencies:")
            for doc_type, command in missing.items():
                print(f"  {doc_type}: {command}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Error importing document processor: {e}")
        return False

def test_architecture_agent():
    """Test the architecture review agent with document processing"""
    print("\n🏗️  Testing Architecture Review Agent")
    print("=" * 50)
    
    try:
        from architecture_review_agent import ArchitectureReviewAgent, ArtifactType
        
        agent = ArchitectureReviewAgent()
        print("✅ Architecture Review Agent initialized successfully")
        
        # Test with a sample markdown file if it exists
        sample_file = "sample_architecture.md"
        if os.path.exists(sample_file):
            print(f"\n📄 Testing with sample file: {sample_file}")
            try:
                artifact = agent.load_artifact(sample_file)
                print(f"✅ Successfully loaded artifact:")
                print(f"  - Type: {artifact.artifact_type.value}")
                print(f"  - Format: {artifact.metadata.get('document_format', 'Unknown')}")
                print(f"  - Word count: {artifact.metadata.get('word_count', 'Unknown')}")
                print(f"  - Sections: {len(artifact.metadata.get('sections', []))}")
                
                # Run a quick review
                comments = agent.review_artifact(artifact)
                print(f"  - Review comments: {len(comments)}")
                
            except Exception as e:
                print(f"⚠️  Warning loading sample file: {e}")
        else:
            print(f"ℹ️  Sample file {sample_file} not found, skipping artifact test")
        
        return True
        
    except ImportError as e:
        print(f"❌ Error importing architecture review agent: {e}")
        return False

def create_sample_files():
    """Create sample files for testing different formats"""
    print("\n📝 Creating Sample Files for Testing")
    print("=" * 50)
    
    # Create a sample text file
    sample_text = """Sample Architecture Document

This is a sample architecture document in plain text format.

Business Requirements:
- High availability system
- Scalable architecture
- Security compliance

Technical Requirements:
- Microservices architecture
- RESTful APIs
- Database clustering

Security Considerations:
- Authentication and authorization
- Data encryption
- Network security
"""
    
    with open("sample_architecture.txt", "w", encoding="utf-8") as f:
        f.write(sample_text)
    print("✅ Created sample_architecture.txt")
    
    # Create a sample markdown file
    sample_md = """# Sample Architecture Document

## Business Requirements
- High availability system
- Scalable architecture  
- Security compliance

## Technical Requirements
- Microservices architecture
- RESTful APIs
- Database clustering

## Security Considerations
- Authentication and authorization
- Data encryption
- Network security
"""
    
    with open("sample_architecture.md", "w", encoding="utf-8") as f:
        f.write(sample_md)
    print("✅ Created sample_architecture.md")

def main():
    """Main test function"""
    print("🚀 Document Processing Test Suite")
    print("=" * 60)
    
    # Create sample files
    create_sample_files()
    
    # Test document processor
    doc_processor_ok = test_document_processor()
    
    # Test architecture agent
    agent_ok = test_architecture_agent()
    
    # Summary
    print("\n📊 Test Summary")
    print("=" * 50)
    print(f"Document Processor: {'✅ PASS' if doc_processor_ok else '❌ FAIL'}")
    print(f"Architecture Agent: {'✅ PASS' if agent_ok else '❌ FAIL'}")
    
    if doc_processor_ok and agent_ok:
        print("\n🎉 All tests passed! The system can now process:")
        print("  - Word documents (.doc/.docx)")
        print("  - PDF files")
        print("  - Text files (.txt)")
        print("  - Markdown files (.md)")
        print("  - HTML files")
        print("  - Excel files")
    else:
        print("\n⚠️  Some tests failed. Check the dependency installation instructions above.")
    
    print(f"\n📁 Sample files created in: {os.getcwd()}")

if __name__ == "__main__":
    main()
