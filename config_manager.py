#!/usr/bin/env python3
"""
Configuration Manager for Architecture Review Agent

Handles loading, validation, and management of standards, rules, and patterns.
"""

import json
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
import os


class ConfigFormat(Enum):
    JSON = "json"
    YAML = "yaml"
    YML = "yml"


@dataclass
class ConfigFile:
    """Represents a configuration file with metadata"""
    path: Path
    format: ConfigFormat
    last_modified: float
    content: Dict[str, Any]
    checksum: str = ""


class ConfigManager:
    """Advanced configuration management for the Architecture Review Agent"""
    
    def __init__(self, config_dir: str = "standards", custom_dir: str = "custom_standards"):
        self.config_dir = Path(config_dir)
        self.custom_dir = Path(custom_dir)
        self.loaded_configs = {}
        self.config_cache = {}
        
        # Create directories if they don't exist
        self.config_dir.mkdir(exist_ok=True)
        self.custom_dir.mkdir(exist_ok=True)
        
    def load_all_configs(self) -> Dict[str, Any]:
        """Load all configuration files with caching and validation"""
        merged_config = {
            "review_rules": {},
            "architecture_patterns": {},
            "custom_standards": {},
            "templates": {}
        }
        
        # Load base configurations
        base_configs = self._load_directory_configs(self.config_dir)
        merged_config.update(base_configs)
        
        # Load custom configurations (overrides base)
        custom_configs = self._load_directory_configs(self.custom_dir)
        self._merge_configs(merged_config, custom_configs)
        
        # Validate configurations
        self._validate_configs(merged_config)
        
        return merged_config
    
    def _load_directory_configs(self, directory: Path) -> Dict[str, Any]:
        """Load all configuration files from a directory"""
        configs = {}
        
        if not directory.exists():
            return configs
            
        for file_path in directory.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() in ['.json', '.yaml', '.yml']:
                try:
                    config_data = self._load_config_file(file_path)
                    config_key = file_path.stem
                    configs[config_key] = config_data
                except Exception as e:
                    print(f"Warning: Failed to load config {file_path}: {e}")
                    
        return configs
    
    def _load_config_file(self, file_path: Path) -> Dict[str, Any]:
        """Load a single configuration file"""
        format_type = ConfigFormat(file_path.suffix.lower().lstrip('.'))
        
        with open(file_path, 'r', encoding='utf-8') as f:
            if format_type == ConfigFormat.JSON:
                content = json.load(f)
            elif format_type in [ConfigFormat.YAML, ConfigFormat.YML]:
                content = yaml.safe_load(f)
            else:
                raise ValueError(f"Unsupported config format: {format_type}")
        
        # Cache the loaded config with metadata
        config_file = ConfigFile(
            path=file_path,
            format=format_type,
            last_modified=file_path.stat().st_mtime,
            content=content
        )
        
        self.loaded_configs[str(file_path)] = config_file
        return content
    
    def _merge_configs(self, base: Dict[str, Any], custom: Dict[str, Any]):
        """Merge custom configurations into base, with custom taking precedence"""
        for key, value in custom.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge_dicts(base[key], value)
            else:
                base[key] = value
    
    def _deep_merge_dicts(self, base_dict: Dict[str, Any], update_dict: Dict[str, Any]):
        """Deep merge two dictionaries"""
        for key, value in update_dict.items():
            if key in base_dict and isinstance(base_dict[key], dict) and isinstance(value, dict):
                self._deep_merge_dicts(base_dict[key], value)
            else:
                base_dict[key] = value
    
    def _validate_configs(self, config: Dict[str, Any]):
        """Validate configuration structure and content"""
        required_sections = {
            'review_rules': ['completeness', 'security', 'scalability'],
            'architecture_patterns': []  # Patterns are optional
        }
        
        for section, required_keys in required_sections.items():
            if section not in config:
                print(f"Warning: Missing required section '{section}' in configuration")
                continue
                
            for required_key in required_keys:
                if required_key not in config[section]:
                    print(f"Warning: Missing required key '{required_key}' in {section}")
    
    def get_review_rules(self) -> Dict[str, Any]:
        """Get consolidated review rules"""
        all_configs = self.load_all_configs()
        return all_configs.get('review_rules', {})
    
    def get_architecture_patterns(self) -> Dict[str, Any]:
        """Get consolidated architecture patterns"""
        all_configs = self.load_all_configs()
        return all_configs.get('architecture_patterns', {})
    
    def get_custom_standards(self) -> Dict[str, Any]:
        """Get all custom standards"""
        all_configs = self.load_all_configs()
        return all_configs.get('custom_standards', {})
    
    def add_custom_standard(self, name: str, standard: Dict[str, Any], format_type: str = "json"):
        """Add a new custom standard"""
        file_extension = f".{format_type.lower()}"
        file_path = self.custom_dir / f"{name}{file_extension}"
        
        with open(file_path, 'w', encoding='utf-8') as f:
            if format_type.lower() == "json":
                json.dump(standard, f, indent=2, ensure_ascii=False)
            elif format_type.lower() in ["yaml", "yml"]:
                yaml.dump(standard, f, default_flow_style=False, allow_unicode=True)
        
        print(f"✅ Added custom standard: {file_path}")
    
    def list_available_configs(self) -> Dict[str, List[str]]:
        """List all available configuration files"""
        configs = {
            "base_configs": [],
            "custom_configs": []
        }
        
        if self.config_dir.exists():
            configs["base_configs"] = [f.name for f in self.config_dir.glob("*.json")]
        
        if self.custom_dir.exists():
            configs["custom_configs"] = [f.name for f in self.custom_dir.rglob("*") if f.suffix in ['.json', '.yaml', '.yml']]
        
        return configs
    
    def validate_standard_format(self, standard: Dict[str, Any]) -> List[str]:
        """Validate that a custom standard follows expected format"""
        issues = []
        
        required_fields = ['name', 'version']
        for field in required_fields:
            if field not in standard:
                issues.append(f"Missing required field: {field}")
        
        if 'requirements' in standard:
            if not isinstance(standard['requirements'], dict):
                issues.append("Requirements field must be a dictionary")
        
        return issues
    
    def get_effective_config(self) -> Dict[str, Any]:
        """Get the final merged configuration that will be used"""
        return self.load_all_configs()
    
    def reload_configs(self):
        """Force reload of all configurations (clears cache)"""
        self.loaded_configs.clear()
        self.config_cache.clear()
        print("🔄 Configuration cache cleared, configs will be reloaded")


def create_sample_configs():
    """Create sample configuration files for demonstration"""
    config_manager = ConfigManager()
    
    # Sample YAML configuration for cloud architecture standards
    cloud_standard = {
        "name": "Cloud Architecture Standards",
        "version": "2.0",
        "description": "Enterprise cloud architecture standards and best practices",
        "requirements": {
            "cloud_native": {
                "patterns": ["containerization", "orchestration", "service mesh"],
                "mandatory": True,
                "severity": "high"
            },
            "multi_cloud": {
                "patterns": ["cloud agnostic", "vendor neutrality", "hybrid cloud"],
                "mandatory": False,
                "severity": "medium"
            },
            "cost_optimization": {
                "patterns": ["resource tagging", "auto-scaling", "reserved instances"],
                "mandatory": True,
                "severity": "medium"
            }
        },
        "guidelines": [
            "Use infrastructure as code for all deployments",
            "Implement proper resource tagging strategy",
            "Design for cloud-native scalability patterns",
            "Ensure data sovereignty compliance"
        ],
        "anti_patterns": [
            "Lift and shift without optimization",
            "Single cloud vendor lock-in",
            "Untagged resources"
        ]
    }
    
    config_manager.add_custom_standard("cloud_architecture", cloud_standard, "yaml")
    
    # Sample API design standards
    api_standard = {
        "name": "API Design Standards",
        "version": "1.5",
        "description": "REST API design standards and conventions",
        "requirements": {
            "rest_compliance": {
                "patterns": ["rest", "http verbs", "status codes", "resource naming"],
                "mandatory": True,
                "severity": "high"
            },
            "api_versioning": {
                "patterns": ["versioning strategy", "backward compatibility"],
                "mandatory": True,
                "severity": "high"
            },
            "documentation": {
                "patterns": ["openapi", "swagger", "api documentation"],
                "mandatory": True,
                "severity": "medium"
            }
        },
        "guidelines": [
            "Use noun-based resource URLs",
            "Implement proper HTTP status codes",
            "Provide comprehensive API documentation",
            "Follow semantic versioning for API versions"
        ]
    }
    
    config_manager.add_custom_standard("api_design", api_standard, "json")
    
    print("✅ Sample configuration files created!")
    return config_manager


if __name__ == "__main__":
    # Demonstrate the configuration manager
    print("🔧 Configuration Manager Demo")
    print("=" * 50)
    
    # Create sample configurations
    config_manager = create_sample_configs()
    
    # List available configurations
    configs = config_manager.list_available_configs()
    print(f"\n📁 Available configurations:")
    for category, files in configs.items():
        print(f"  {category}: {files}")
    
    # Load and display effective configuration
    effective_config = config_manager.get_effective_config()
    print(f"\n⚙️  Loaded {len(effective_config)} configuration sections")
    
    # Show custom standards
    custom_standards = config_manager.get_custom_standards()
    print(f"\n📋 Custom Standards: {list(custom_standards.keys())}")
