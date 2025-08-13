#!/usr/bin/env python3
"""
Architecture Review Agent - Main CLI Interface
Performs automated architecture reviews of various document types
"""

import argparse
import json
import sys
import os
import re
from pathlib import Path
from typing import Dict, Any, List, Optional

# Add safe printing for Windows compatibility
def safe_print(text: str) -> None:
    """Safely print text that may contain Unicode characters"""
    try:
        print(text)
    except UnicodeEncodeError:
        # Fallback for Windows console encoding issues
        safe_text = text.encode('ascii', 'replace').decode('ascii')
        print(safe_text)

"""
Architecture Review Agent

This agent reads solution architecture, architecture patterns, and architecture standards
artifacts to provide review comments and prepare enterprise architects for reviews.
"""

import re
from dataclasses import dataclass
from enum import Enum


class ArtifactType(Enum):
    SOLUTION_ARCHITECTURE = "solution_architecture"
    ARCHITECTURE_PATTERN = "architecture_pattern"
    ARCHITECTURE_STANDARD = "architecture_standard"
    DESIGN_DOCUMENT = "design_document"
    TECHNICAL_SPECIFICATION = "technical_specification"


class ReviewSeverity(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class ReviewComment:
    """Represents a review comment with context and recommendations"""
    section: str
    severity: ReviewSeverity
    category: str
    issue: str
    recommendation: str
    references: List[str]
    line_number: Optional[int] = None


@dataclass
class ArchitectureArtifact:
    """Represents an architecture artifact to be reviewed"""
    file_path: str
    artifact_type: ArtifactType
    content: str
    metadata: Dict[str, Any]


class ArchitectureReviewAgent:
    """Main agent class for reviewing architecture artifacts"""
    
    def __init__(self, standards_dir: str = None):
        self.standards_dir = standards_dir or "standards"
        self.review_rules = self._load_review_rules()
        self.architecture_patterns = self._load_architecture_patterns()
        self.standards = self._load_standards()
        
    def _load_review_rules(self) -> Dict[str, Any]:
        """Load review rules and criteria"""
        default_rules = {
            "completeness": {
                "required_sections": [
                    "executive_summary",
                    "business_requirements",
                    "technical_requirements",
                    "architecture_overview",
                    "component_design",
                    "security_considerations",
                    "performance_requirements",
                    "scalability_design",
                    "deployment_architecture",
                    "monitoring_logging",
                    "disaster_recovery",
                    "cost_analysis"
                ],
                "severity": "high"
            },
            "security": {
                "patterns": [
                    r"authentication",
                    r"authorization",
                    r"encryption",
                    r"ssl/tls",
                    r"oauth",
                    r"jwt",
                    r"api\s*key",
                    r"security\s*group",
                    r"firewall",
                    r"vpc"
                ],
                "severity": ReviewSeverity.CRITICAL
            },
            "scalability": {
                "patterns": [
                    r"load\s*balancer",
                    r"auto\s*scaling",
                    r"horizontal\s*scaling",
                    r"vertical\s*scaling",
                    r"caching",
                    r"cdn",
                    r"database\s*sharding",
                    r"microservices"
                ],
                "severity": ReviewSeverity.HIGH
            },
            "monitoring": {
                "patterns": [
                    r"monitoring",
                    r"logging",
                    r"alerting",
                    r"metrics",
                    r"dashboard",
                    r"observability"
                ],
                "severity": ReviewSeverity.MEDIUM
            },
            "compliance": {
                "patterns": [
                    r"gdpr",
                    r"hipaa",
                    r"sox",
                    r"pci\s*dss",
                    r"compliance",
                    r"audit",
                    r"data\s*retention"
                ],
                "severity": ReviewSeverity.HIGH
            }
        }
        
        rules_file = Path(self.standards_dir) / "review_rules.json"
        if rules_file.exists():
            try:
                with open(rules_file, 'r', encoding='utf-8') as f:
                    custom_rules = json.load(f)
                    default_rules.update(custom_rules)
            except Exception as e:
                print(f"Warning: Could not load custom rules: {e}")
        
        return default_rules
    
    def _load_architecture_patterns(self) -> Dict[str, Any]:
        """Load known architecture patterns for validation"""
        default_patterns = {
            "microservices": {
                "description": "Microservices architecture pattern",
                "characteristics": ["service independence", "api gateway", "service discovery"],
                "best_practices": [
                    "Each service should have a single responsibility",
                    "Services should communicate via well-defined APIs",
                    "Implement circuit breakers for resilience"
                ]
            },
            "layered": {
                "description": "Layered (N-tier) architecture pattern",
                "characteristics": ["presentation layer", "business layer", "data layer"],
                "best_practices": [
                    "Clear separation of concerns",
                    "Dependencies should flow downward",
                    "Avoid circular dependencies"
                ]
            },
            "event_driven": {
                "description": "Event-driven architecture pattern",
                "characteristics": ["event producers", "event consumers", "event store"],
                "best_practices": [
                    "Design events to be immutable",
                    "Implement idempotent event handlers",
                    "Consider event versioning strategy"
                ]
            }
        }
        
        patterns_file = Path(self.standards_dir) / "architecture_patterns.json"
        if patterns_file.exists():
            try:
                with open(patterns_file, 'r', encoding='utf-8') as f:
                    custom_patterns = json.load(f)
                    default_patterns.update(custom_patterns)
            except Exception as e:
                print(f"Warning: Could not load custom patterns: {e}")
        
        return default_patterns
    
    def _load_standards(self) -> Dict[str, Any]:
        """Load organization-specific architecture standards"""
        standards = {}
        standards_path = Path(self.standards_dir)
        
        if standards_path.exists():
            for file_path in standards_path.glob("*.json"):
                if file_path.name not in ["review_rules.json", "architecture_patterns.json"]:
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            standards[file_path.stem] = json.load(f)
                    except Exception as e:
                        print(f"Warning: Could not load standard {file_path}: {e}")
        
        return standards
    
    def load_artifact(self, file_path: str, artifact_type: ArtifactType = None) -> ArchitectureArtifact:
        """Load an architecture artifact from file"""
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"Artifact file not found: {file_path}")
        
        # Use document processor for supported file types
        try:
            from document_processor import DocumentProcessor
            processor = DocumentProcessor()
            content, metadata = processor.process_document(str(path))
            
            # Convert document metadata to our format
            artifact_metadata = {
                "file_name": path.name,
                "file_size": metadata.file_size,
                "last_modified": metadata.last_modified,
                "document_format": metadata.format.value,
                "word_count": metadata.word_count,
                "sections": metadata.sections,
                "tables_count": metadata.tables_count,
                "images_count": metadata.images_count
            }
            
        except (ImportError, Exception) as e:
            # Fallback to plain text reading if document processor fails
            print(f"Warning: Document processor not available, falling back to plain text: {e}")
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            artifact_metadata = {
                "file_name": path.name,
                "file_size": path.stat().st_size,
                "last_modified": path.stat().st_mtime
            }
        
        # Auto-detect artifact type if not specified
        if artifact_type is None:
            artifact_type = self._detect_artifact_type(content, path.name)
        
        return ArchitectureArtifact(
            file_path=str(path),
            artifact_type=artifact_type,
            content=content,
            metadata=artifact_metadata
        )
    
    def _detect_artifact_type(self, content: str, filename: str) -> ArtifactType:
        """Auto-detect the type of architecture artifact"""
        content_lower = content.lower()
        filename_lower = filename.lower()
        
        if any(term in filename_lower for term in ["solution", "architecture"]):
            return ArtifactType.SOLUTION_ARCHITECTURE
        elif any(term in filename_lower for term in ["pattern", "template"]):
            return ArtifactType.ARCHITECTURE_PATTERN
        elif any(term in filename_lower for term in ["standard", "guideline"]):
            return ArtifactType.ARCHITECTURE_STANDARD
        elif any(term in content_lower for term in ["solution architecture", "system design"]):
            return ArtifactType.SOLUTION_ARCHITECTURE
        else:
            return ArtifactType.DESIGN_DOCUMENT
    
    def review_artifact(self, artifact: ArchitectureArtifact) -> List[ReviewComment]:
        """Perform comprehensive review of an architecture artifact"""
        comments = []
        
        # Check completeness
        comments.extend(self._check_completeness(artifact))
        
        # Check security considerations
        comments.extend(self._check_security(artifact))
        
        # Check scalability design
        comments.extend(self._check_scalability(artifact))
        
        # Check monitoring and observability
        comments.extend(self._check_monitoring(artifact))
        
        # Check compliance requirements
        comments.extend(self._check_compliance(artifact))
        
        # Check against architecture patterns
        comments.extend(self._check_patterns(artifact))
        
        # Check against standards
        comments.extend(self._check_standards(artifact))
        
        return comments
    
    def _check_completeness(self, artifact: ArchitectureArtifact) -> List[ReviewComment]:
        """Check if all required sections are present"""
        comments = []
        content_lower = artifact.content.lower()
        
        required_sections = self.review_rules["completeness"]["required_sections"]
        missing_sections = []
        
        for section in required_sections:
            section_pattern = section.replace("_", r"[\s_-]")
            if not re.search(section_pattern, content_lower):
                missing_sections.append(section)
        
        if missing_sections:
            severity_str = self.review_rules["completeness"]["severity"]
            if isinstance(severity_str, str):
                severity = ReviewSeverity(severity_str)
            else:
                severity = severity_str
            
            comments.append(ReviewComment(
                section="Document Structure",
                severity=severity,
                category="Completeness",
                issue=f"Missing required sections: {', '.join(missing_sections)}",
                recommendation="Add the missing sections to ensure comprehensive architecture documentation",
                references=["Architecture Documentation Standards"]
            ))
        
        return comments
    
    def _check_security(self, artifact: ArchitectureArtifact) -> List[ReviewComment]:
        """Check security considerations and patterns"""
        comments = []
        content_lower = artifact.content.lower()
        
        security_patterns = self.review_rules["security"]["patterns"]
        found_patterns = []
        
        for pattern in security_patterns:
            if re.search(pattern, content_lower):
                found_patterns.append(pattern)
        
        if len(found_patterns) < 3:  # Minimum security coverage threshold
            comments.append(ReviewComment(
                section="Security",
                severity=ReviewSeverity.CRITICAL,
                category="Security",
                issue="Insufficient security considerations documented",
                recommendation="Ensure authentication, authorization, encryption, and network security are addressed",
                references=["Security Architecture Standards", "OWASP Guidelines"]
            ))
        
        # Check for common security anti-patterns
        if re.search(r"password\s*in\s*plain\s*text", content_lower):
            comments.append(ReviewComment(
                section="Security",
                severity=ReviewSeverity.CRITICAL,
                category="Security",
                issue="Plain text passwords mentioned",
                recommendation="Use secure credential management and avoid plain text passwords",
                references=["Credential Management Standards"]
            ))
        
        return comments
    
    def _check_scalability(self, artifact: ArchitectureArtifact) -> List[ReviewComment]:
        """Check scalability design patterns"""
        comments = []
        content_lower = artifact.content.lower()
        
        scalability_patterns = self.review_rules["scalability"]["patterns"]
        found_patterns = sum(1 for pattern in scalability_patterns 
                           if re.search(pattern, content_lower))
        
        if found_patterns < 2:  # Minimum scalability coverage
            comments.append(ReviewComment(
                section="Scalability",
                severity=ReviewSeverity.HIGH,
                category="Performance",
                issue="Limited scalability design considerations",
                recommendation="Include horizontal scaling, load balancing, and caching strategies",
                references=["Scalability Design Patterns"]
            ))
        
        return comments
    
    def _check_monitoring(self, artifact: ArchitectureArtifact) -> List[ReviewComment]:
        """Check monitoring and observability"""
        comments = []
        content_lower = artifact.content.lower()
        
        monitoring_patterns = self.review_rules["monitoring"]["patterns"]
        found_patterns = sum(1 for pattern in monitoring_patterns 
                           if re.search(pattern, content_lower))
        
        if found_patterns < 2:
            comments.append(ReviewComment(
                section="Monitoring",
                severity=ReviewSeverity.MEDIUM,
                category="Observability",
                issue="Insufficient monitoring and observability design",
                recommendation="Include logging, metrics, alerting, and dashboard specifications",
                references=["Monitoring Standards", "Observability Best Practices"]
            ))
        
        return comments
    
    def _check_compliance(self, artifact: ArchitectureArtifact) -> List[ReviewComment]:
        """Check compliance requirements"""
        comments = []
        content_lower = artifact.content.lower()
        
        compliance_patterns = self.review_rules["compliance"]["patterns"]
        has_compliance = any(re.search(pattern, content_lower) 
                           for pattern in compliance_patterns)
        
        if "financial" in content_lower or "healthcare" in content_lower or "personal data" in content_lower:
            if not has_compliance:
                comments.append(ReviewComment(
                    section="Compliance",
                    severity=ReviewSeverity.HIGH,
                    category="Compliance",
                    issue="Regulatory compliance requirements not addressed",
                    recommendation="Document relevant compliance requirements (GDPR, HIPAA, SOX, etc.)",
                    references=["Compliance Framework", "Regulatory Requirements"]
                ))
        
        return comments
    
    def _check_patterns(self, artifact: ArchitectureArtifact) -> List[ReviewComment]:
        """Check against known architecture patterns"""
        comments = []
        content_lower = artifact.content.lower()
        
        detected_patterns = []
        for pattern_name, pattern_info in self.architecture_patterns.items():
            if pattern_name in content_lower:
                detected_patterns.append(pattern_name)
                
                # Check if best practices are mentioned
                best_practices = pattern_info.get("best_practices", [])
                missing_practices = []
                
                for practice in best_practices:
                    if not any(keyword in content_lower 
                             for keyword in practice.lower().split()[:3]):
                        missing_practices.append(practice)
                
                if missing_practices:
                    comments.append(ReviewComment(
                        section="Architecture Patterns",
                        severity=ReviewSeverity.MEDIUM,
                        category="Best Practices",
                        issue=f"Missing best practices for {pattern_name} pattern",
                        recommendation=f"Consider implementing: {'; '.join(missing_practices[:2])}",
                        references=[f"{pattern_name.title()} Pattern Guide"]
                    ))
        
        return comments
    
    def _check_standards(self, artifact: ArchitectureArtifact) -> List[ReviewComment]:
        """Check against organization standards"""
        comments = []
        
        for standard_name, standard_rules in self.standards.items():
            # This is a placeholder for organization-specific standard checks
            # Organizations can customize this based on their specific standards
            pass
        
        return comments
    
    def generate_review_report(self, artifact: ArchitectureArtifact, 
                             comments: List[ReviewComment]) -> Dict[str, Any]:
        """Generate a comprehensive review report"""
        severity_counts = {severity.value: 0 for severity in ReviewSeverity}
        category_counts = {}
        
        for comment in comments:
            severity_counts[comment.severity.value] += 1
            category_counts[comment.category] = category_counts.get(comment.category, 0) + 1
        
        # Calculate overall score (0-100)
        total_issues = len(comments)
        critical_weight = severity_counts["critical"] * 10
        high_weight = severity_counts["high"] * 5
        medium_weight = severity_counts["medium"] * 3
        low_weight = severity_counts["low"] * 1
        
        total_weight = critical_weight + high_weight + medium_weight + low_weight
        score = max(0, 100 - total_weight)
        
        return {
            "artifact_info": {
                "file_path": artifact.file_path,
                "artifact_type": artifact.artifact_type.value,
                "file_size": artifact.metadata.get("file_size", 0),
                "last_modified": artifact.metadata.get("last_modified", 0)
            },
            "review_summary": {
                "total_comments": total_issues,
                "overall_score": score,
                "severity_breakdown": severity_counts,
                "category_breakdown": category_counts
            },
            "comments": [
                {
                    "section": comment.section,
                    "severity": comment.severity.value,
                    "category": comment.category,
                    "issue": comment.issue,
                    "recommendation": comment.recommendation,
                    "references": comment.references,
                    "line_number": comment.line_number
                }
                for comment in comments
            ],
            "preparation_notes": self._generate_preparation_notes(comments)
        }
    
    def _generate_preparation_notes(self, comments: List[ReviewComment]) -> List[str]:
        """Generate preparation notes for enterprise architect review"""
        notes = []
        
        critical_issues = [c for c in comments if c.severity == ReviewSeverity.CRITICAL]
        if critical_issues:
            notes.append("[CRITICAL] CRITICAL: Address security and critical architectural issues before review")
        
        high_issues = [c for c in comments if c.severity == ReviewSeverity.HIGH]
        if high_issues:
            notes.append("[HIGH] HIGH: Review scalability and completeness concerns")
        
        categories = list(set(c.category for c in comments))
        if categories:
            notes.append(f"[FOCUS] Focus areas for discussion: {', '.join(categories)}")
        
        notes.append("[REVIEW] Review all referenced standards and guidelines before the meeting")
        notes.append("[PREPARE] Prepare specific examples and alternatives for flagged issues")
        
        return notes
    
    def export_report(self, report: Dict[str, Any], output_file: str, format_type: str = "json"):
        """Export the review report to various formats"""
        output_path = Path(output_file)
        
        if format_type.lower() == "json":
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
        
        elif format_type.lower() == "html":
            html_content = self._generate_html_report(report)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
        
        elif format_type.lower() == "md":
            md_content = self._generate_markdown_report(report)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(md_content)
    
    def _generate_html_report(self, report: Dict[str, Any]) -> str:
        """Generate HTML report"""
        html_template = """<!DOCTYPE html>
<html>
<head>
    <title>Architecture Review Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
        .summary {{ display: flex; gap: 20px; margin: 20px 0; }}
        .metric {{ background-color: #e8f4f8; padding: 15px; border-radius: 5px; text-align: center; }}
        .comments {{ margin-top: 20px; }}
        .comment {{ border-left: 4px solid #ccc; padding: 10px; margin: 10px 0; }}
        .critical {{ border-left-color: #ff0000; }}
        .high {{ border-left-color: #ff8800; }}
        .medium {{ border-left-color: #ffaa00; }}
        .low {{ border-left-color: #00aa00; }}
        .preparation {{ background-color: #fff3cd; padding: 15px; border-radius: 5px; margin-top: 20px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Architecture Review Report</h1>
        <p><strong>File:</strong> {file_path}</p>
        <p><strong>Type:</strong> {artifact_type}</p>
    </div>
    
    <div class="summary">
        <div class="metric">
            <h3>{overall_score}</h3>
            <p>Overall Score</p>
        </div>
        <div class="metric">
            <h3>{total_comments}</h3>
            <p>Total Issues</p>
        </div>
        <div class="metric">
            <h3>{critical_count}</h3>
            <p>Critical Issues</p>
        </div>
    </div>
    
    <div class="comments">
        <h2>Review Comments</h2>
        {comments_html}
    </div>
    
    <div class="preparation">
        <h2>Preparation Notes</h2>
        <ul>
            {preparation_notes}
        </ul>
    </div>
</body>
</html>"""
        
        comments_html = ""
        for comment in report["comments"]:
            comments_html += f"""
            <div class="comment {comment['severity']}">
                <h4>{comment['section']} - {comment['category']}</h4>
                <p><strong>Issue:</strong> {comment['issue']}</p>
                <p><strong>Recommendation:</strong> {comment['recommendation']}</p>
                <p><small><strong>References:</strong> {', '.join(comment['references'])}</small></p>
            </div>
            """
        
        preparation_notes = "".join(f"<li>{note}</li>" for note in report["preparation_notes"])
        
        return html_template.format(
            file_path=report["artifact_info"]["file_path"],
            artifact_type=report["artifact_info"]["artifact_type"],
            overall_score=report["review_summary"]["overall_score"],
            total_comments=report["review_summary"]["total_comments"],
            critical_count=report["review_summary"]["severity_breakdown"]["critical"],
            comments_html=comments_html,
            preparation_notes=preparation_notes
        )
    
    def _generate_markdown_report(self, report: Dict[str, Any]) -> str:
        """Generate Markdown report"""
        md_content = f"""# Architecture Review Report

## Artifact Information
- **File:** {report['artifact_info']['file_path']}
- **Type:** {report['artifact_info']['artifact_type']}
- **Overall Score:** {report['review_summary']['overall_score']}/100

## Review Summary
- **Total Issues:** {report['review_summary']['total_comments']}
- **Critical:** {report['review_summary']['severity_breakdown']['critical']}
- **High:** {report['review_summary']['severity_breakdown']['high']}
- **Medium:** {report['review_summary']['severity_breakdown']['medium']}
- **Low:** {report['review_summary']['severity_breakdown']['low']}

## Review Comments

"""
        
        for comment in report['comments']:
            severity_emoji = {
                'critical': '[CRITICAL]',
                'high': '[HIGH]',
                'medium': '[MEDIUM]',
                'low': '[LOW]',
                'info': '[INFO]'
            }
            
            emoji = severity_emoji.get(comment['severity'], '[INFO]')
            md_content += f"""### {emoji} {comment['section']} - {comment['category']}
**Severity:** {comment['severity'].upper()}

**Issue:** {comment['issue']}

**Recommendation:** {comment['recommendation']}

**References:** {', '.join(comment['references'])}

---

"""
        
        md_content += "## Preparation Notes\n\n"
        for note in report['preparation_notes']:
            md_content += f"- {note}\n"
        
        return md_content


def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(description="Architecture Review Agent")
    parser.add_argument("artifact_file", help="Path to the architecture artifact file")
    parser.add_argument("--type", choices=[t.value for t in ArtifactType], 
                       help="Artifact type (auto-detected if not specified)")
    parser.add_argument("--standards-dir", default="standards", 
                       help="Directory containing standards and rules")
    parser.add_argument("--output", "-o", help="Output file for the review report")
    parser.add_argument("--format", choices=["json", "html", "md"], default="json",
                       help="Output format for the report")
    
    args = parser.parse_args()
    
    # Initialize the agent
    agent = ArchitectureReviewAgent(standards_dir=args.standards_dir)
    
    try:
        # Load the artifact
        artifact_type = ArtifactType(args.type) if args.type else None
        artifact = agent.load_artifact(args.artifact_file, artifact_type)
        
        safe_print(f"Analyzing {artifact.artifact_type.value}: {artifact.file_path}")
        
        # Perform the review
        comments = agent.review_artifact(artifact)
        
        # Generate the report
        report = agent.generate_review_report(artifact, comments)
        
        # Display summary
        safe_print(f"\n[REPORT] Review Summary:")
        safe_print(f"   Overall Score: {report['review_summary']['overall_score']}/100")
        safe_print(f"   Total Issues: {report['review_summary']['total_comments']}")
        safe_print(f"   Critical: {report['review_summary']['severity_breakdown']['critical']}")
        safe_print(f"   High: {report['review_summary']['severity_breakdown']['high']}")
        
        # Export report if specified
        if args.output:
            agent.export_report(report, args.output, args.format)
            safe_print(f"\n[FILE] Report exported to: {args.output}")
        else:
            # Print key issues to console
            critical_issues = [c for c in comments if c.severity == ReviewSeverity.CRITICAL]
            if critical_issues:
                safe_print("\n[CRITICAL] Critical Issues:")
                for issue in critical_issues[:3]:  # Show top 3
                    safe_print(f"   • {issue.issue}")
        
        safe_print("\n[SUCCESS] Review completed successfully!")
        
    except FileNotFoundError as e:
        safe_print(f"[ERROR] Error: {e}")
    except Exception as e:
        safe_print(f"[ERROR] Unexpected error: {e}")


if __name__ == "__main__":
    main()
