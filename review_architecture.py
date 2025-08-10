#!/usr/bin/env python3
"""
Simple CLI runner for the Architecture Review Agent
"""

import sys
from pathlib import Path
from architecture_review_agent import ArchitectureReviewAgent, ArtifactType, ReviewSeverity

def main():
    if len(sys.argv) < 2:
        print("""
🏗️ Architecture Review Agent - Quick Runner

Usage:
    python review_architecture.py <architecture_file> [output_file]

Examples:
    python review_architecture.py my_architecture.md
    python review_architecture.py my_architecture.md report.html

This will analyze the architecture document and provide:
✅ Completeness check (required sections)
🔒 Security considerations review  
📈 Scalability pattern analysis
📊 Monitoring & observability check
🏛️ Compliance requirements validation
🏗️ Architecture pattern best practices

For advanced options, use: python architecture_review_agent.py --help
        """)
        return

    file_path = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not Path(file_path).exists():
        print(f"❌ Error: File '{file_path}' not found")
        return

    print(f"🔍 Analyzing architecture document: {file_path}")
    print("=" * 60)

    try:
        # Initialize the agent
        agent = ArchitectureReviewAgent()
        
        # Load and analyze the artifact
        artifact = agent.load_artifact(file_path)
        print(f"📄 Document type: {artifact.artifact_type.value}")
        print(f"📊 File size: {artifact.metadata['file_size']:,} bytes")
        
        # Perform review
        comments = agent.review_artifact(artifact)
        report = agent.generate_review_report(artifact, comments)
        
        # Display results
        print("\n" + "=" * 60)
        print("📊 REVIEW RESULTS")
        print("=" * 60)
        
        score = report['review_summary']['overall_score']
        total_issues = report['review_summary']['total_comments']
        
        if score >= 90:
            status = "🟢 EXCELLENT"
        elif score >= 75:
            status = "🟡 GOOD"
        elif score >= 60:
            status = "🟠 NEEDS IMPROVEMENT" 
        else:
            status = "🔴 REQUIRES MAJOR CHANGES"
        
        print(f"Overall Score: {score}/100 {status}")
        print(f"Total Issues: {total_issues}")
        
        severity_counts = report['review_summary']['severity_breakdown']
        print(f"  🚨 Critical: {severity_counts['critical']}")
        print(f"  ⚠️  High: {severity_counts['high']}")
        print(f"  ⚡ Medium: {severity_counts['medium']}")
        print(f"  ℹ️  Low: {severity_counts['low']}")
        
        # Show detailed issues
        if comments:
            print("\n" + "=" * 60)
            print("📋 DETAILED REVIEW COMMENTS")
            print("=" * 60)
            
            for i, comment in enumerate(comments, 1):
                severity_emoji = {
                    'critical': '🚨',
                    'high': '⚠️',
                    'medium': '⚡',
                    'low': 'ℹ️',
                    'info': '📋'
                }
                
                emoji = severity_emoji.get(comment.severity.value, '📋')
                print(f"\n{i}. {emoji} {comment.section} - {comment.category}")
                print(f"   Severity: {comment.severity.value.upper()}")
                print(f"   Issue: {comment.issue}")
                print(f"   Recommendation: {comment.recommendation}")
                if comment.references:
                    print(f"   References: {', '.join(comment.references)}")
        
        # Show preparation notes
        print("\n" + "=" * 60)
        print("🎯 ENTERPRISE ARCHITECT PREPARATION NOTES")
        print("=" * 60)
        
        for note in report['preparation_notes']:
            print(f"• {note}")
        
        # Export detailed report if requested
        if output_file:
            format_type = "html" if output_file.endswith('.html') else \
                         "md" if output_file.endswith('.md') else "json"
            
            agent.export_report(report, output_file, format_type)
            print(f"\n📁 Detailed report exported to: {output_file}")
        
        print("\n" + "=" * 60)
        print("✅ Review completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error during review: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
