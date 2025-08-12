#!/usr/bin/env python3
"""
Enhanced Architecture Review Agent

Advanced version with plugin support, configuration management, and improved analysis capabilities.
"""

import os
import json
import re
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import hashlib

from architecture_review_agent import (
    ArchitectureReviewAgent, ArchitectureArtifact, ReviewComment, 
    ReviewSeverity, ArtifactType
)
from config_manager import ConfigManager
from plugin_system import PluginManager, PluginType


@dataclass
class ReviewSession:
    """Represents a review session with metadata"""
    session_id: str
    timestamp: datetime
    artifact_path: str
    reviewer: str
    config_version: str
    plugin_versions: Dict[str, str]
    total_comments: int
    score: int
    duration_seconds: float


class EnhancedArchitectureReviewAgent(ArchitectureReviewAgent):
    """Enhanced Architecture Review Agent with plugin support and advanced features"""
    
    def __init__(self, standards_dir: str = None, custom_dir: str = None, 
                 plugin_dir: str = None, enable_plugins: bool = True):
        
        # Initialize configuration manager
        self.config_manager = ConfigManager(
            config_dir=standards_dir or "standards",
            custom_dir=custom_dir or "custom_standards"
        )
        
        # Initialize plugin manager
        self.plugin_manager = None
        if enable_plugins:
            self.plugin_manager = PluginManager(plugin_dir or "plugins")
            self.plugin_manager.load_all_plugins()
        
        # Load configurations
        self.configs = self.config_manager.load_all_configs()
        
        # Initialize base agent with loaded configurations
        super().__init__(standards_dir or "standards")
        
        # Override with enhanced configurations
        self.review_rules = self.configs.get("review_rules", self.review_rules)
        self.architecture_patterns = self.configs.get("architecture_patterns", self.architecture_patterns)
        self.custom_standards = self.configs.get("custom_standards", {})
        
        # Session tracking
        self.current_session: Optional[ReviewSession] = None
        self.review_history: List[ReviewSession] = []
        
        print(f"🚀 Enhanced Architecture Review Agent initialized")
        print(f"   📁 Config sections loaded: {len(self.configs)}")
        if self.plugin_manager:
            plugin_count = len(self.plugin_manager.loaded_plugins)
            print(f"   🔌 Plugins loaded: {plugin_count}")
    
    def start_review_session(self, artifact_path: str, reviewer: str = "system") -> str:
        """Start a new review session"""
        session_id = hashlib.md5(f"{artifact_path}_{datetime.now().isoformat()}".encode()).hexdigest()[:8]
        
        plugin_versions = {}
        if self.plugin_manager:
            plugins = self.plugin_manager.list_plugins()
            plugin_versions = {name: info["version"] for name, info in plugins.items()}
        
        self.current_session = ReviewSession(
            session_id=session_id,
            timestamp=datetime.now(),
            artifact_path=artifact_path,
            reviewer=reviewer,
            config_version="2.0",  # Version of the enhanced agent
            plugin_versions=plugin_versions,
            total_comments=0,
            score=0,
            duration_seconds=0.0
        )
        
        print(f"📋 Started review session: {session_id}")
        return session_id
    
    def review_artifact(self, artifact: ArchitectureArtifact, 
                       enable_plugins: bool = True) -> List[ReviewComment]:
        """Enhanced review artifact with plugin support"""
        start_time = datetime.now()
        
        # Start session if not already started
        if not self.current_session:
            self.start_review_session(artifact.file_path)
        
        # Run base reviews
        comments = super().review_artifact(artifact)
        
        # Run plugin analyzers if enabled
        if enable_plugins and self.plugin_manager:
            try:
                plugin_comments = self.plugin_manager.execute_analyzers(artifact)
                comments.extend(plugin_comments)
                print(f"🔌 Plugin analyzers added {len(plugin_comments)} comments")
            except Exception as e:
                print(f"⚠️  Plugin execution failed: {e}")
        
        # Run custom standard checks
        custom_comments = self._check_custom_standards(artifact)
        comments.extend(custom_comments)
        
        # Update session metrics
        if self.current_session:
            duration = (datetime.now() - start_time).total_seconds()
            self.current_session.duration_seconds = duration
            self.current_session.total_comments = len(comments)
        
        return comments
    
    def _check_custom_standards(self, artifact: ArchitectureArtifact) -> List[ReviewComment]:
        """Check against custom organizational standards"""
        comments = []
        
        for standard_name, standard_config in self.custom_standards.items():
            if not isinstance(standard_config, dict):
                continue
                
            requirements = standard_config.get("requirements", {})
            for req_name, req_config in requirements.items():
                if not isinstance(req_config, dict):
                    continue
                    
                patterns = req_config.get("patterns", [])
                mandatory = req_config.get("mandatory", False)
                severity = req_config.get("severity", "medium")
                
                # Check if patterns are found in the content
                content_lower = artifact.content.lower()
                found_patterns = [p for p in patterns if p.lower() in content_lower]
                
                if mandatory and not found_patterns:
                    comments.append(ReviewComment(
                        section=f"Custom Standards ({standard_name})",
                        severity=ReviewSeverity(severity),
                        category="Custom Standard Compliance",
                        issue=f"Required {req_name} patterns not found: {', '.join(patterns)}",
                        recommendation=f"Implement {req_name} as per {standard_name} requirements",
                        references=[f"{standard_name} Standard", "Custom Standards Guide"]
                    ))
                elif found_patterns:
                    # Positive validation - could add info-level comments for compliance
                    pass
        
        return comments
    
    def generate_enhanced_report(self, artifact: ArchitectureArtifact, 
                               comments: List[ReviewComment]) -> Dict[str, Any]:
        """Generate enhanced report with additional metadata and insights"""
        base_report = self.generate_review_report(artifact, comments)
        
        # Add enhanced information
        enhanced_report = {
            **base_report,
            "session_info": asdict(self.current_session) if self.current_session else {},
            "configuration_info": {
                "standards_loaded": len(self.configs),
                "custom_standards": list(self.custom_standards.keys()),
                "plugins_enabled": self.plugin_manager is not None,
                "plugin_count": len(self.plugin_manager.loaded_plugins) if self.plugin_manager else 0
            },
            "advanced_metrics": self._calculate_advanced_metrics(comments),
            "recommendations_summary": self._generate_recommendations_summary(comments),
            "compliance_matrix": self._generate_compliance_matrix(artifact, comments)
        }
        
        # Update session score
        if self.current_session:
            self.current_session.score = enhanced_report["review_summary"]["overall_score"]
        
        return enhanced_report
    
    def _calculate_advanced_metrics(self, comments: List[ReviewComment]) -> Dict[str, Any]:
        """Calculate advanced metrics for the review"""
        if not comments:
            return {"trend": "excellent", "risk_score": 0, "complexity_indicator": "low"}
        
        # Calculate risk score based on severity distribution
        severity_weights = {
            ReviewSeverity.CRITICAL: 10,
            ReviewSeverity.HIGH: 5,
            ReviewSeverity.MEDIUM: 3,
            ReviewSeverity.LOW: 1,
            ReviewSeverity.INFO: 0
        }
        
        risk_score = sum(severity_weights.get(comment.severity, 0) for comment in comments)
        
        # Determine complexity based on number of categories
        categories = set(comment.category for comment in comments)
        complexity = "low" if len(categories) <= 3 else "medium" if len(categories) <= 6 else "high"
        
        # Determine trend based on overall score
        score = max(0, 100 - risk_score)
        if score >= 90:
            trend = "excellent"
        elif score >= 75:
            trend = "good"
        elif score >= 60:
            trend = "improving"
        else:
            trend = "concerning"
        
        return {
            "risk_score": risk_score,
            "complexity_indicator": complexity,
            "trend": trend,
            "categories_count": len(categories),
            "average_severity": sum(severity_weights.get(c.severity, 0) for c in comments) / len(comments) if comments else 0
        }
    
    def _generate_recommendations_summary(self, comments: List[ReviewComment]) -> Dict[str, List[str]]:
        """Generate prioritized recommendations summary"""
        recommendations = {
            "immediate_actions": [],
            "short_term_improvements": [],
            "long_term_enhancements": []
        }
        
        for comment in comments:
            if comment.severity in [ReviewSeverity.CRITICAL, ReviewSeverity.HIGH]:
                recommendations["immediate_actions"].append({
                    "action": comment.recommendation,
                    "category": comment.category,
                    "section": comment.section
                })
            elif comment.severity == ReviewSeverity.MEDIUM:
                recommendations["short_term_improvements"].append({
                    "action": comment.recommendation,
                    "category": comment.category,
                    "section": comment.section
                })
            else:
                recommendations["long_term_enhancements"].append({
                    "action": comment.recommendation,
                    "category": comment.category,
                    "section": comment.section
                })
        
        return recommendations
    
    def _generate_compliance_matrix(self, artifact: ArchitectureArtifact, 
                                  comments: List[ReviewComment]) -> Dict[str, Any]:
        """Generate compliance matrix against standards"""
        matrix = {
            "base_standards": {
                "security": {"status": "compliant", "issues": 0},
                "scalability": {"status": "compliant", "issues": 0},
                "monitoring": {"status": "compliant", "issues": 0},
                "completeness": {"status": "compliant", "issues": 0}
            },
            "custom_standards": {},
            "overall_compliance": 0
        }
        
        # Check base standards compliance
        for comment in comments:
            category_lower = comment.category.lower()
            for standard in matrix["base_standards"]:
                if standard in category_lower:
                    matrix["base_standards"][standard]["issues"] += 1
                    if comment.severity in [ReviewSeverity.CRITICAL, ReviewSeverity.HIGH]:
                        matrix["base_standards"][standard]["status"] = "non-compliant"
                    elif comment.severity == ReviewSeverity.MEDIUM and matrix["base_standards"][standard]["status"] == "compliant":
                        matrix["base_standards"][standard]["status"] = "partially_compliant"
        
        # Check custom standards compliance
        for standard_name in self.custom_standards.keys():
            custom_issues = [c for c in comments if standard_name.lower() in c.section.lower()]
            matrix["custom_standards"][standard_name] = {
                "status": "compliant" if not custom_issues else "non-compliant",
                "issues": len(custom_issues)
            }
        
        # Calculate overall compliance percentage
        total_standards = len(matrix["base_standards"]) + len(matrix["custom_standards"])
        compliant_standards = sum(1 for std in matrix["base_standards"].values() if std["status"] == "compliant")
        compliant_standards += sum(1 for std in matrix["custom_standards"].values() if std["status"] == "compliant")
        
        matrix["overall_compliance"] = (compliant_standards / total_standards * 100) if total_standards > 0 else 100
        
        return matrix
    
    def export_enhanced_report(self, report: Dict[str, Any], output_file: str, 
                             format_type: str = "json", include_session: bool = True):
        """Export enhanced report with additional formats"""
        if format_type.lower() == "json":
            self._export_json_report(report, output_file, include_session)
        elif format_type.lower() == "html":
            self._export_enhanced_html_report(report, output_file)
        elif format_type.lower() == "xlsx":
            self._export_excel_report(report, output_file)
        else:
            # Fall back to base implementation
            super().export_report(report, output_file, format_type)
    
    def _export_json_report(self, report: Dict[str, Any], output_file: str, include_session: bool):
        """Export JSON report with session information"""
        export_data = report.copy()
        if include_session and self.current_session:
            export_data["session_info"] = asdict(self.current_session)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False, default=str)
    
    def _export_enhanced_html_report(self, report: Dict[str, Any], output_file: str):
        """Export enhanced HTML report with better styling and interactivity"""
        html_template = """<!DOCTYPE html>
<html>
<head>
    <title>Enhanced Architecture Review Report</title>
    <meta charset="utf-8">
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 8px 8px 0 0; }}
        .header h1 {{ margin: 0; font-size: 2.5em; }}
        .header p {{ margin: 5px 0 0 0; opacity: 0.9; }}
        .content {{ padding: 30px; }}
        .metrics-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin: 20px 0; }}
        .metric-card {{ background: #f8f9fa; border: 1px solid #e9ecef; border-radius: 8px; padding: 20px; text-align: center; }}
        .metric-value {{ font-size: 2em; font-weight: bold; color: #495057; margin-bottom: 5px; }}
        .metric-label {{ color: #6c757d; font-size: 0.9em; }}
        .score-excellent {{ color: #28a745; }}
        .score-good {{ color: #ffc107; }}
        .score-needs-improvement {{ color: #fd7e14; }}
        .score-critical {{ color: #dc3545; }}
        .section {{ margin: 30px 0; }}
        .section h2 {{ color: #495057; border-bottom: 2px solid #e9ecef; padding-bottom: 10px; }}
        .comment {{ border-left: 4px solid #ccc; padding: 15px; margin: 15px 0; background: #f8f9fa; border-radius: 0 8px 8px 0; }}
        .comment.critical {{ border-left-color: #dc3545; background: #f8d7da; }}
        .comment.high {{ border-left-color: #fd7e14; background: #fff3cd; }}
        .comment.medium {{ border-left-color: #ffc107; background: #fff3cd; }}
        .comment.low {{ border-left-color: #28a745; background: #d4edda; }}
        .comment h4 {{ margin: 0 0 10px 0; color: #495057; }}
        .comment p {{ margin: 5px 0; line-height: 1.5; }}
        .recommendations {{ background: #e8f4f8; border: 1px solid #bee5eb; border-radius: 8px; padding: 20px; margin: 20px 0; }}
        .compliance-matrix {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0; }}
        .compliance-item {{ background: white; border: 1px solid #dee2e6; border-radius: 8px; padding: 15px; text-align: center; }}
        .compliance-compliant {{ border-color: #28a745; background: #f8fff9; }}
        .compliance-partial {{ border-color: #ffc107; background: #fffbf0; }}
        .compliance-non-compliant {{ border-color: #dc3545; background: #fff5f5; }}
        .tab-container {{ margin: 20px 0; }}
        .tab-buttons {{ display: flex; background: #f8f9fa; border-radius: 8px 8px 0 0; }}
        .tab-button {{ flex: 1; padding: 15px; text-align: center; background: none; border: none; cursor: pointer; font-size: 1em; }}
        .tab-button.active {{ background: white; border-bottom: 2px solid #667eea; }}
        .tab-content {{ display: none; padding: 20px; border: 1px solid #dee2e6; border-top: none; }}
        .tab-content.active {{ display: block; }}
    </style>
    <script>
        function showTab(tabName) {
            // Hide all tabs
            document.querySelectorAll('.tab-content').forEach(tab => tab.classList.remove('active'));
            document.querySelectorAll('.tab-button').forEach(btn => btn.classList.remove('active'));
            
            // Show selected tab
            document.getElementById(tabName).classList.add('active');
            document.querySelector(`[onclick="showTab('${tabName}')"]`).classList.add('active');
        }
    </script>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏗️ Architecture Review Report</h1>
            <p><strong>File:</strong> {artifact_file}</p>
            <p><strong>Type:</strong> {artifact_type} | <strong>Generated:</strong> {timestamp}</p>
        </div>
        
        <div class="content">
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-value {score_class}">{overall_score}</div>
                    <div class="metric-label">Overall Score</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{total_comments}</div>
                    <div class="metric-label">Total Issues</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{compliance_percentage}%</div>
                    <div class="metric-label">Compliance Rate</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{risk_indicator}</div>
                    <div class="metric-label">Risk Level</div>
                </div>
            </div>
            
            <div class="tab-container">
                <div class="tab-buttons">
                    <button class="tab-button active" onclick="showTab('comments')">Review Comments</button>
                    <button class="tab-button" onclick="showTab('recommendations')">Recommendations</button>
                    <button class="tab-button" onclick="showTab('compliance')">Compliance Matrix</button>
                    <button class="tab-button" onclick="showTab('session')">Session Info</button>
                </div>
                
                <div id="comments" class="tab-content active">
                    <h2>📋 Review Comments</h2>
                    {comments_html}
                </div>
                
                <div id="recommendations" class="tab-content">
                    <h2>🎯 Prioritized Recommendations</h2>
                    {recommendations_html}
                </div>
                
                <div id="compliance" class="tab-content">
                    <h2>✅ Compliance Matrix</h2>
                    {compliance_html}
                </div>
                
                <div id="session" class="tab-content">
                    <h2>📊 Session Information</h2>
                    {session_html}
                </div>
            </div>
        </div>
    </div>
    
    <script>
        // Initialize first tab as active
        showTab('comments');
    </script>
</body>
</html>"""
        
        # Prepare template variables
        score = report["review_summary"]["overall_score"]
        score_class = ("score-excellent" if score >= 90 else 
                      "score-good" if score >= 75 else 
                      "score-needs-improvement" if score >= 60 else 
                      "score-critical")
        
        # Generate comments HTML
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
        
        # Generate recommendations HTML
        recommendations_html = self._format_recommendations_html(report.get("recommendations_summary", {}))
        
        # Generate compliance HTML
        compliance_html = self._format_compliance_html(report.get("compliance_matrix", {}))
        
        # Generate session HTML
        session_html = self._format_session_html(report.get("session_info", {}))
        
        # Format and save HTML
        formatted_html = html_template.format(
            artifact_file=report["artifact_info"]["file_path"],
            artifact_type=report["artifact_info"]["artifact_type"],
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            overall_score=score,
            score_class=score_class,
            total_comments=report["review_summary"]["total_comments"],
            compliance_percentage=int(report.get("compliance_matrix", {}).get("overall_compliance", 0)),
            risk_indicator=report.get("advanced_metrics", {}).get("trend", "unknown").title(),
            comments_html=comments_html,
            recommendations_html=recommendations_html,
            compliance_html=compliance_html,
            session_html=session_html
        )
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(formatted_html)
    
    def _format_recommendations_html(self, recommendations: Dict[str, List[Dict]]) -> str:
        """Format recommendations for HTML display"""
        html = ""
        
        sections = [
            ("immediate_actions", "🚨 Immediate Actions", "critical"),
            ("short_term_improvements", "⚡ Short-term Improvements", "medium"),
            ("long_term_enhancements", "📈 Long-term Enhancements", "low")
        ]
        
        for key, title, css_class in sections:
            items = recommendations.get(key, [])
            if items:
                html += f"<h3>{title}</h3>"
                for item in items:
                    html += f"""
                    <div class="comment {css_class}">
                        <p><strong>{item['section']} ({item['category']}):</strong> {item['action']}</p>
                    </div>
                    """
        
        return html or "<p>No specific recommendations available.</p>"
    
    def _format_compliance_html(self, compliance_matrix: Dict[str, Any]) -> str:
        """Format compliance matrix for HTML display"""
        html = "<div class='compliance-matrix'>"
        
        # Base standards
        base_standards = compliance_matrix.get("base_standards", {})
        for standard, info in base_standards.items():
            status_class = f"compliance-{info['status'].replace('_', '-')}"
            html += f"""
            <div class="compliance-item {status_class}">
                <h4>{standard.title()}</h4>
                <p>Status: {info['status'].replace('_', ' ').title()}</p>
                <p>Issues: {info['issues']}</p>
            </div>
            """
        
        # Custom standards
        custom_standards = compliance_matrix.get("custom_standards", {})
        for standard, info in custom_standards.items():
            status_class = f"compliance-{info['status'].replace('_', '-')}"
            html += f"""
            <div class="compliance-item {status_class}">
                <h4>{standard}</h4>
                <p>Status: {info['status'].replace('_', ' ').title()}</p>
                <p>Issues: {info['issues']}</p>
            </div>
            """
        
        html += "</div>"
        return html
    
    def _format_session_html(self, session_info: Dict[str, Any]) -> str:
        """Format session information for HTML display"""
        if not session_info:
            return "<p>No session information available.</p>"
        
        html = f"""
        <div class="metric-card">
            <p><strong>Session ID:</strong> {session_info.get('session_id', 'N/A')}</p>
            <p><strong>Reviewer:</strong> {session_info.get('reviewer', 'N/A')}</p>
            <p><strong>Duration:</strong> {session_info.get('duration_seconds', 0):.2f} seconds</p>
            <p><strong>Config Version:</strong> {session_info.get('config_version', 'N/A')}</p>
        </div>
        """
        
        plugin_versions = session_info.get('plugin_versions', {})
        if plugin_versions:
            html += "<h3>🔌 Plugins Used</h3><ul>"
            for plugin, version in plugin_versions.items():
                html += f"<li>{plugin}: v{version}</li>"
            html += "</ul>"
        
        return html
    
    def finish_review_session(self):
        """Finish the current review session and add to history"""
        if self.current_session:
            self.review_history.append(self.current_session)
            print(f"✅ Review session {self.current_session.session_id} completed")
            self.current_session = None
    
    def get_review_history(self) -> List[Dict[str, Any]]:
        """Get review history"""
        return [asdict(session) for session in self.review_history]


def main():
    """Enhanced CLI interface"""
    parser = argparse.ArgumentParser(description="Enhanced Architecture Review Agent")
    parser.add_argument("artifact_file", help="Path to the architecture artifact file")
    parser.add_argument("--type", choices=[t.value for t in ArtifactType], 
                       help="Artifact type (auto-detected if not specified)")
    parser.add_argument("--standards-dir", default="standards", 
                       help="Directory containing standards and rules")
    parser.add_argument("--custom-dir", default="custom_standards",
                       help="Directory containing custom standards")
    parser.add_argument("--plugin-dir", default="plugins",
                       help="Directory containing plugins")
    parser.add_argument("--output", "-o", help="Output file for the review report")
    parser.add_argument("--format", choices=["json", "html", "md", "xlsx"], default="json",
                       help="Output format for the report")
    parser.add_argument("--disable-plugins", action="store_true",
                       help="Disable plugin execution")
    parser.add_argument("--reviewer", default="cli-user", 
                       help="Name of the reviewer")
    parser.add_argument("--list-plugins", action="store_true",
                       help="List available plugins and exit")
    
    args = parser.parse_args()
    
    # Initialize the enhanced agent
    agent = EnhancedArchitectureReviewAgent(
        standards_dir=args.standards_dir,
        custom_dir=args.custom_dir,
        plugin_dir=args.plugin_dir,
        enable_plugins=not args.disable_plugins
    )
    
    # List plugins if requested
    if args.list_plugins:
        if agent.plugin_manager:
            plugins = agent.plugin_manager.list_plugins()
            print(f"\n📋 Available Plugins ({len(plugins)}):")
            for key, info in plugins.items():
                status = "✅ Enabled" if info["enabled"] else "❌ Disabled"
                print(f"  - {info['name']} v{info['version']} ({info['type']}) {status}")
                print(f"    {info['description']}")
                print(f"    Author: {info['author']}")
                print()
        else:
            print("🔌 Plugins are disabled")
        return
    
    try:
        # Load the artifact
        artifact_type = ArtifactType(args.type) if args.type else None
        artifact = agent.load_artifact(args.artifact_file, artifact_type)
        
        print(f"\n🔍 Analyzing {artifact.artifact_type.value}: {artifact.file_path}")
        
        # Start review session
        session_id = agent.start_review_session(args.artifact_file, args.reviewer)
        
        # Perform the enhanced review
        comments = agent.review_artifact(artifact, enable_plugins=not args.disable_plugins)
        
        # Generate the enhanced report
        report = agent.generate_enhanced_report(artifact, comments)
        
        # Display summary
        print(f"\n📊 Enhanced Review Summary:")
        print(f"   Overall Score: {report['review_summary']['overall_score']}/100")
        print(f"   Total Issues: {report['review_summary']['total_comments']}")
        print(f"   Compliance Rate: {report['compliance_matrix']['overall_compliance']:.1f}%")
        print(f"   Risk Level: {report['advanced_metrics']['trend'].title()}")
        print(f"   Session Duration: {agent.current_session.duration_seconds:.2f}s")
        
        # Export report if specified
        if args.output:
            agent.export_enhanced_report(report, args.output, args.format)
            print(f"\n📁 Enhanced report exported to: {args.output}")
        
        # Finish the session
        agent.finish_review_session()
        
        print("\n✅ Enhanced review completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
