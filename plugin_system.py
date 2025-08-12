#!/usr/bin/env python3
"""
Plugin System for Architecture Review Agent

Enables extensible review capabilities through plugins.
"""

import importlib
import inspect
import sys
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Any, Type, Optional
from dataclasses import dataclass
from enum import Enum

from architecture_review_agent import ArchitectureArtifact, ReviewComment, ReviewSeverity


class PluginType(Enum):
    """Types of plugins supported"""
    ANALYZER = "analyzer"
    FORMATTER = "formatter"
    VALIDATOR = "validator"
    EXPORTER = "exporter"


@dataclass
class PluginInfo:
    """Plugin metadata"""
    name: str
    version: str
    description: str
    author: str
    plugin_type: PluginType
    dependencies: List[str]
    enabled: bool = True


class ReviewPlugin(ABC):
    """Base class for all review plugins"""
    
    @property
    @abstractmethod
    def info(self) -> PluginInfo:
        """Plugin information and metadata"""
        pass
    
    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize the plugin with configuration"""
        pass
    
    @abstractmethod
    def execute(self, artifact: ArchitectureArtifact, context: Dict[str, Any]) -> List[ReviewComment]:
        """Execute the plugin's review logic"""
        pass
    
    def cleanup(self):
        """Cleanup resources when plugin is unloaded"""
        pass


class AnalyzerPlugin:
    """Base class for analyzer plugins"""
    
    def __init__(self):
        self.plugin_type = PluginType.ANALYZER


class FormatterPlugin(ReviewPlugin):
    """Base class for formatter plugins"""
    
    def __init__(self):
        self.plugin_type = PluginType.FORMATTER
    
    @abstractmethod
    def format_report(self, report: Dict[str, Any]) -> str:
        """Format a review report"""
        pass


class PluginManager:
    """Manages loading, unloading, and execution of plugins"""
    
    def __init__(self, plugin_dir: str = "plugins"):
        self.plugin_dir = Path(plugin_dir)
        self.loaded_plugins: Dict[str, ReviewPlugin] = {}
        self.plugin_configs: Dict[str, Dict[str, Any]] = {}
        
        # Create plugin directory if it doesn't exist
        self.plugin_dir.mkdir(exist_ok=True)
        
        # Add plugin directory to Python path
        if str(self.plugin_dir) not in sys.path:
            sys.path.insert(0, str(self.plugin_dir))
    
    def discover_plugins(self) -> List[str]:
        """Discover available plugins in the plugin directory"""
        plugin_files = []
        
        for file_path in self.plugin_dir.glob("*.py"):
            if not file_path.name.startswith("_"):
                plugin_files.append(file_path.stem)
        
        return plugin_files
    
    def load_plugin(self, plugin_name: str, config: Dict[str, Any] = None) -> bool:
        """Load a specific plugin"""
        try:
            # Import the plugin module
            module = importlib.import_module(plugin_name)
            
            # Find plugin classes in the module
            plugin_classes = []
            for name, obj in inspect.getmembers(module):
                if (inspect.isclass(obj) and 
                    (issubclass(obj, AnalyzerPlugin) or 
                     (hasattr(obj, 'info') and hasattr(obj, 'initialize') and hasattr(obj, 'execute'))) and 
                    obj not in [ReviewPlugin, AnalyzerPlugin, FormatterPlugin] and
                    not obj.__name__.startswith('Base')):
                    plugin_classes.append(obj)
            
            if not plugin_classes:
                print(f"⚠️  No plugin classes found in {plugin_name}")
                return False
            
            # Instantiate and initialize each plugin class
            for plugin_class in plugin_classes:
                plugin_instance = plugin_class()
                plugin_config = config or self.plugin_configs.get(plugin_name, {})
                
                if plugin_instance.initialize(plugin_config):
                    plugin_key = f"{plugin_name}_{plugin_instance.info.name}"
                    self.loaded_plugins[plugin_key] = plugin_instance
                    print(f"✅ Loaded plugin: {plugin_instance.info.name} v{plugin_instance.info.version}")
                else:
                    print(f"❌ Failed to initialize plugin: {plugin_instance.info.name}")
                    return False
            
            return True
            
        except Exception as e:
            print(f"❌ Error loading plugin {plugin_name}: {e}")
            return False
    
    def load_all_plugins(self) -> int:
        """Load all discovered plugins"""
        plugins = self.discover_plugins()
        loaded_count = 0
        
        for plugin_name in plugins:
            if self.load_plugin(plugin_name):
                loaded_count += 1
        
        print(f"🔌 Loaded {loaded_count}/{len(plugins)} plugins")
        return loaded_count
    
    def unload_plugin(self, plugin_key: str) -> bool:
        """Unload a specific plugin"""
        if plugin_key in self.loaded_plugins:
            plugin = self.loaded_plugins[plugin_key]
            plugin.cleanup()
            del self.loaded_plugins[plugin_key]
            print(f"🔌 Unloaded plugin: {plugin_key}")
            return True
        return False
    
    def get_plugins_by_type(self, plugin_type: PluginType) -> List[ReviewPlugin]:
        """Get all loaded plugins of a specific type"""
        return [plugin for plugin in self.loaded_plugins.values() 
                if plugin.info.plugin_type == plugin_type]
    
    def execute_analyzers(self, artifact: ArchitectureArtifact, context: Dict[str, Any] = None) -> List[ReviewComment]:
        """Execute all analyzer plugins"""
        comments = []
        context = context or {}
        
        analyzers = self.get_plugins_by_type(PluginType.ANALYZER)
        for analyzer in analyzers:
            if analyzer.info.enabled:
                try:
                    plugin_comments = analyzer.execute(artifact, context)
                    comments.extend(plugin_comments)
                except Exception as e:
                    print(f"⚠️  Error executing analyzer {analyzer.info.name}: {e}")
        
        return comments
    
    def execute_formatters(self, report: Dict[str, Any]) -> Dict[str, str]:
        """Execute all formatter plugins"""
        formatted_reports = {}
        
        formatters = self.get_plugins_by_type(PluginType.FORMATTER)
        for formatter in formatters:
            if formatter.info.enabled:
                try:
                    formatted_report = formatter.format_report(report)
                    formatted_reports[formatter.info.name] = formatted_report
                except Exception as e:
                    print(f"⚠️  Error executing formatter {formatter.info.name}: {e}")
        
        return formatted_reports
    
    def list_plugins(self) -> Dict[str, Dict[str, Any]]:
        """List all loaded plugins with their information"""
        plugin_list = {}
        
        for key, plugin in self.loaded_plugins.items():
            plugin_list[key] = {
                "name": plugin.info.name,
                "version": plugin.info.version,
                "description": plugin.info.description,
                "author": plugin.info.author,
                "type": plugin.info.plugin_type.value,
                "enabled": plugin.info.enabled,
                "dependencies": plugin.info.dependencies
            }
        
        return plugin_list
    
    def enable_plugin(self, plugin_key: str) -> bool:
        """Enable a specific plugin"""
        if plugin_key in self.loaded_plugins:
            self.loaded_plugins[plugin_key].info.enabled = True
            return True
        return False
    
    def disable_plugin(self, plugin_key: str) -> bool:
        """Disable a specific plugin"""
        if plugin_key in self.loaded_plugins:
            self.loaded_plugins[plugin_key].info.enabled = False
            return True
        return False


def create_sample_plugins():
    """Create sample plugins for demonstration"""
    plugin_dir = Path("plugins")
    plugin_dir.mkdir(exist_ok=True)
    
    # Cloud Architecture Analyzer Plugin
    cloud_plugin = '''#!/usr/bin/env python3
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
                               if re.search(pattern.replace(".", r"\\s*"), content_lower))
        
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
'''
    
    # Performance Analyzer Plugin
    performance_plugin = '''#!/usr/bin/env python3
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
                                if re.search(pattern.replace(".", r"\\s*"), content_lower))
        
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
        caching_found = any(re.search(pattern.replace(".", r"\\s*"), content_lower) 
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
'''
    
    # Write sample plugins to files
    with open(plugin_dir / "cloud_analyzer.py", "w", encoding="utf-8") as f:
        f.write(cloud_plugin)
    
    with open(plugin_dir / "performance_analyzer.py", "w", encoding="utf-8") as f:
        f.write(performance_plugin)
    
    print("✅ Sample plugins created:")
    print("  - plugins/cloud_analyzer.py")
    print("  - plugins/performance_analyzer.py")


if __name__ == "__main__":
    # Demonstrate the plugin system
    print("🔌 Plugin System Demo")
    print("=" * 50)
    
    # Create sample plugins
    create_sample_plugins()
    
    # Initialize plugin manager
    plugin_manager = PluginManager()
    
    # Discover and load plugins
    discovered = plugin_manager.discover_plugins()
    print(f"\\n🔍 Discovered plugins: {discovered}")
    
    loaded_count = plugin_manager.load_all_plugins()
    print(f"\\n✅ Successfully loaded {loaded_count} plugins")
    
    # List loaded plugins
    plugins = plugin_manager.list_plugins()
    print(f"\\n📋 Loaded plugins:")
    for key, info in plugins.items():
        print(f"  - {info['name']} v{info['version']} ({info['type']})")
        print(f"    {info['description']}")
