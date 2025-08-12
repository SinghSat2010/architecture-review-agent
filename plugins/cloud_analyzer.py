#!/usr/bin/env python3
"""
Cloud Architecture Analyzer Plugin

Analyzes architecture documents for cloud-specific patterns and best practices.
"""

import re
from typing import Dict, List, Any
from plugin_system import AnalyzerPlugin, PluginInfo, PluginType
from architecture_review_agent import ArchitectureArtifact, ReviewComment, ReviewSeverity


class CloudArchitectureAnalyzer(AnalyzerPlugin):
    """Analyzes cloud architecture patterns and compliance"""
    
    @property
    def info(self) -> PluginInfo:
        return PluginInfo(
            name="Cloud Architecture Analyzer",
            version="1.0.0",
            description="Analyzes cloud architecture patterns, multi-cloud strategies, and cloud-native practices",
            author="Architecture Review Team",
            plugin_type=PluginType.ANALYZER,
            dependencies=["re"]
        )
    
    def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize the cloud analyzer with configuration"""
        self.cloud_patterns = config.get("cloud_patterns", {
            "aws": ["ec2", "s3", "lambda", "rds", "cloudfront", "api gateway"],
            "azure": ["virtual machines", "blob storage", "functions", "sql database", "cdn"],
            "gcp": ["compute engine", "cloud storage", "cloud functions", "cloud sql"]
        })
        
        self.multi_cloud_indicators = config.get("multi_cloud_indicators", [
            "multi.cloud", "cloud.agnostic", "vendor.neutral", "hybrid.cloud"
        ])
        
        self.cloud_native_patterns = config.get("cloud_native_patterns", [
            "containerization", "kubernetes", "docker", "microservices",
            "serverless", "auto.scaling", "load.balancing"
        ])
        
        return True
    
    def execute(self, artifact: ArchitectureArtifact, context: Dict[str, Any]) -> List[ReviewComment]:
        """Execute cloud architecture analysis"""
        comments = []
        content_lower = artifact.content.lower()
        
        # Check for cloud provider diversity
        cloud_providers_mentioned = []
        for provider, services in self.cloud_patterns.items():
            if any(service in content_lower for service in services):
                cloud_providers_mentioned.append(provider)
        
        if len(cloud_providers_mentioned) == 1:
            comments.append(ReviewComment(
                section="Cloud Strategy",
                severity=ReviewSeverity.MEDIUM,
                category="Vendor Lock-in Risk",
                issue=f"Architecture appears to rely solely on {cloud_providers_mentioned[0].upper()}",
                recommendation="Consider multi-cloud strategy or cloud-agnostic design patterns to avoid vendor lock-in",
                references=["Multi-Cloud Architecture Patterns", "Cloud Vendor Neutrality Guidelines"]
            ))
        
        # Check for cloud-native patterns
        cloud_native_found = sum(1 for pattern in self.cloud_native_patterns 
                               if re.search(pattern.replace(".", r"\s*"), content_lower))
        
        if cloud_native_found < 3:
            comments.append(ReviewComment(
                section="Cloud Architecture",
                severity=ReviewSeverity.HIGH,
                category="Cloud-Native Design",
                issue="Limited cloud-native patterns detected",
                recommendation="Incorporate more cloud-native patterns like containerization, auto-scaling, and serverless architectures",
                references=["Cloud-Native Architecture Guide", "12-Factor App Principles"]
            ))
        
        # Check for disaster recovery across regions
        if not re.search(r"multi.region|cross.region|disaster.recovery", content_lower):
            comments.append(ReviewComment(
                section="Disaster Recovery",
                severity=ReviewSeverity.HIGH,
                category="Resilience",
                issue="No multi-region disaster recovery strategy mentioned",
                recommendation="Design cross-region disaster recovery with appropriate RPO/RTO targets",
                references=["Cloud Disaster Recovery Patterns", "Multi-Region Architecture Guide"]
            ))
        
        return comments
