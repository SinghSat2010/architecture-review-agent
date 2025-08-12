#!/usr/bin/env python3
"""
Demonstrate All Supported Document Formats

This script shows the architecture review agent working with
all supported document formats including Word, PDF, text, and markdown.
"""

import os
import sys
from pathlib import Path

def demo_document_processing():
    """Demonstrate document processing capabilities"""
    print("🚀 Architecture Review Agent - Multi-Format Demo")
    print("=" * 60)
    
    try:
        from architecture_review_agent import ArchitectureReviewAgent, ArtifactType
        
        # Initialize the agent
        agent = ArchitectureReviewAgent()
        print("✅ Architecture Review Agent initialized")
        
        # List of sample files to test
        sample_files = [
            "sample_architecture.md",
            "sample_architecture.txt", 
            "sample_architecture.docx"
        ]
        
        print(f"\n📄 Testing {len(sample_files)} document formats:")
        print("-" * 40)
        
        for file_path in sample_files:
            if os.path.exists(file_path):
                print(f"\n🔍 Processing: {file_path}")
                try:
                    # Load and review the artifact
                    artifact = agent.load_artifact(file_path)
                    
                    # Display artifact information
                    print(f"  📊 Format: {artifact.metadata.get('document_format', 'Unknown')}")
                    print(f"  📝 Word Count: {artifact.metadata.get('word_count', 'Unknown')}")
                    print(f"  📋 Sections: {len(artifact.metadata.get('sections', []))}")
                    print(f"  📊 Tables: {artifact.metadata.get('tables_count', 'Unknown')}")
                    print(f"  🖼️  Images: {artifact.metadata.get('images_count', 'Unknown')}")
                    
                    # Run review
                    comments = agent.review_artifact(artifact)
                    
                    # Count issues by severity
                    severity_counts = {}
                    for comment in comments:
                        severity = comment.severity.value
                        severity_counts[severity] = severity_counts.get(severity, 0) + 1
                    
                    print(f"  ⚠️  Issues: {len(comments)} total")
                    for severity, count in severity_counts.items():
                        print(f"    - {severity.title()}: {count}")
                    
                    print(f"  ✅ Review completed successfully!")
                    
                except Exception as e:
                    print(f"  ❌ Error processing {file_path}: {e}")
            else:
                print(f"⚠️  File not found: {file_path}")
        
        # Summary
        print(f"\n🎉 Multi-format document processing demonstration completed!")
        print(f"📁 Test files processed from: {os.getcwd()}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Error importing architecture review agent: {e}")
        return False

def show_supported_formats():
    """Show all supported document formats"""
    print("\n📋 Supported Document Formats")
    print("=" * 40)
    
    try:
        from document_processor import DocumentProcessor
        
        processor = DocumentProcessor()
        
        # Check dependencies
        print("🔍 Dependency Status:")
        deps = processor.check_dependencies()
        for name, available in deps.items():
            status = "✅ Available" if available else "❌ Missing"
            print(f"  {name}: {status}")
        
        # Show supported formats
        print(f"\n📊 Format Support:")
        for fmt, supported in processor.supported_formats.items():
            status = "✅" if supported else "❌"
            print(f"  .{fmt}: {status}")
            
    except ImportError as e:
        print(f"❌ Error importing document processor: {e}")

def create_sample_pdf():
    """Create a sample PDF for testing (if possible)"""
    print("\n📄 Creating Sample PDF")
    print("-" * 30)
    
    try:
        # Try to create a simple PDF using reportlab
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        
        # Create PDF
        c = canvas.Canvas("sample_architecture.pdf", pagesize=letter)
        c.setFont("Helvetica", 16)
        
        # Add content
        c.drawString(100, 750, "Sample Architecture Document")
        c.setFont("Helvetica", 12)
        c.drawString(100, 720, "This is a sample PDF document for testing.")
        c.drawString(100, 700, "Business Requirements:")
        c.drawString(120, 680, "- High availability system")
        c.drawString(120, 660, "- Scalable architecture")
        c.drawString(100, 640, "Security Considerations:")
        c.drawString(120, 620, "- Authentication and authorization")
        c.drawString(120, 600, "- Data encryption")
        
        c.save()
        print("✅ Created sample_architecture.pdf")
        
    except ImportError:
        print("ℹ️  reportlab not available. Install with: pip install reportlab")
    except Exception as e:
        print(f"⚠️  Could not create PDF: {e}")

def main():
    """Main demonstration function"""
    print("🎯 Architecture Review Agent - Multi-Format Capabilities")
    print("=" * 70)
    
    # Show supported formats
    show_supported_formats()
    
    # Create sample PDF if possible
    create_sample_pdf()
    
    # Run the main demonstration
    success = demo_document_processing()
    
    if success:
        print(f"\n🎊 Demonstration completed successfully!")
        print(f"📚 The architecture review agent now supports:")
        print(f"   • Word documents (.doc/.docx)")
        print(f"   • PDF files")
        print(f"   • Text files (.txt)")
        print(f"   • Markdown files (.md)")
        print(f"   • HTML files")
        print(f"   • Excel files")
        print(f"\n💡 Try reviewing different document types:")
        print(f"   python architecture_review_agent.py sample_architecture.docx")
        print(f"   python architecture_review_agent.py sample_architecture.txt")
        print(f"   python architecture_review_agent.py sample_architecture.md")
    else:
        print(f"\n❌ Demonstration failed. Check the error messages above.")

if __name__ == "__main__":
    main()
