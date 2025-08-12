#!/usr/bin/env python3
"""
Performance Analyzer Plugin

Analyzes architecture documents for performance considerations and bottlenecks.
"""

import re
from typing import Dict, List, Any
from plugin_system import AnalyzerPlugin, PluginInfo, PluginType
from architecture_review_agent import ArchitectureArtifact, ReviewComment, ReviewSeverity


class PerformanceAnalyzer(AnalyzerPlugin):
    """Analyzes performance patterns and potential bottlenecks"""
    
    @property
    def info(self) -> PluginInfo:
        return PluginInfo(
            name="Performance Analyzer",
            version="1.2.0",
            description="Analyzes performance requirements, caching strategies, and potential bottlenecks",
            author="Performance Engineering Team",
            plugin_type=PluginType.ANALYZER,
            dependencies=["re"]
        )
    
    def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize the performance analyzer"""
        self.performance_patterns = config.get("performance_patterns", [
            "response.time", "latency", "throughput", "load.test",
            "performance.test", "benchmark", "sla", "slo"
        ])
        
        self.caching_patterns = config.get("caching_patterns", [
            "cache", "redis", "memcached", "cdn", "edge.cache"
        ])
        
        self.bottleneck_indicators = config.get("bottleneck_indicators", [
            "single.point", "synchronous", "blocking", "sequential"
        ])
        
        return True
    
    def execute(self, artifact: ArchitectureArtifact, context: Dict[str, Any]) -> List[ReviewComment]:
        """Execute performance analysis"""
        comments = []
        content_lower = artifact.content.lower()
        
        # Check for performance requirements
        perf_patterns_found = sum(1 for pattern in self.performance_patterns 
                                if re.search(pattern.replace(".", r"\s*"), content_lower))
        
        if perf_patterns_found < 2:
            comments.append(ReviewComment(
                section="Performance Requirements",
                severity=ReviewSeverity.HIGH,
                category="Performance",
                issue="Insufficient performance requirements documentation",
                recommendation="Define specific SLAs, response time targets, throughput requirements, and load testing strategy",
                references=["Performance Engineering Guidelines", "SLA Definition Standards"]
            ))
        
        # Check for caching strategy
        caching_found = any(re.search(pattern.replace(".", r"\s*"), content_lower) 
                          for pattern in self.caching_patterns)
        
        if not caching_found:
            comments.append(ReviewComment(
                section="Performance Optimization",
                severity=ReviewSeverity.MEDIUM,
                category="Caching",
                issue="No caching strategy mentioned",
                recommendation="Implement appropriate caching layers (application cache, CDN, database cache) to improve performance",
                references=["Caching Patterns Guide", "Performance Optimization Strategies"]
            ))
        
        # Check for database performance considerations
        if re.search(r"database|sql|nosql", content_lower):
            if not re.search(r"index|query.optimization|connection.pool|read.replica", content_lower):
                comments.append(ReviewComment(
                    section="Database Performance",
                    severity=ReviewSeverity.MEDIUM,
                    category="Database Design",
                    issue="Database performance optimization strategies not addressed",
                    recommendation="Include database indexing strategy, query optimization, connection pooling, and read replicas",
                    references=["Database Performance Tuning Guide", "Database Scaling Patterns"]
                ))
        
        return comments
