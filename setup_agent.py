#!/usr/bin/env python3
"""
Setup script for the Architecture Review Agent
"""

import os
import json
from pathlib import Path

def create_project_structure():
    """Create the basic project structure"""
    print("🏗️ Setting up Architecture Review Agent...")
    
    # Create directories
    dirs_to_create = [
        "examples",
        "reports", 
        "custom_standards"
    ]
    
    for dir_name in dirs_to_create:
        Path(dir_name).mkdir(exist_ok=True)
        print(f"✅ Created directory: {dir_name}/")
    
    # Create example custom standard
    custom_standard_example = {
        "name": "Enterprise Security Standards",
        "version": "1.0",
        "requirements": {
            "authentication": {
                "patterns": ["multi-factor", "sso", "ldap"],
                "mandatory": True
            },
            "data_encryption": {
                "patterns": ["aes-256", "tls 1.3", "end-to-end"],
                "mandatory": True
            }
        },
        "guidelines": [
            "All data must be encrypted in transit and at rest",
            "Multi-factor authentication is required for all systems",
            "Regular security audits must be conducted"
        ]
    }
    
    custom_standards_file = Path("custom_standards/enterprise_security.json")
    with open(custom_standards_file, 'w') as f:
        json.dump(custom_standard_example, f, indent=2)
    print(f"✅ Created example custom standard: {custom_standards_file}")
    
    # Create example architecture document template
    arch_template = """# Solution Architecture Template

## Executive Summary
Brief overview of the solution and its business value.

## Business Requirements
- Business objective 1
- Business objective 2
- Success criteria

## Technical Requirements
- Performance requirements
- Scalability requirements
- Integration requirements

## Architecture Overview
High-level architecture description and key components.

## Component Design
### Service 1
Description and responsibilities

### Service 2  
Description and responsibilities

## Security Considerations
- Authentication and authorization
- Data encryption
- Network security
- Security monitoring

## Performance Requirements
- Expected load
- Response time requirements
- Throughput requirements

## Scalability Design
- Horizontal scaling approach
- Load balancing strategy
- Auto-scaling configuration

## Deployment Architecture
- Infrastructure overview
- Environment setup
- CI/CD pipeline

## Monitoring and Logging
- Monitoring strategy
- Logging approach
- Alerting configuration
- Dashboard design

## Disaster Recovery
- Backup strategy
- Recovery procedures
- RTO and RPO objectives

## Cost Analysis
- Infrastructure costs
- Operational costs
- Cost optimization strategies

## Risk Assessment
- Technical risks
- Business risks
- Mitigation strategies

## Testing Strategy
- Unit testing approach
- Integration testing
- Performance testing
- Security testing
"""
    
    template_file = Path("examples/architecture_template.md")
    with open(template_file, 'w') as f:
        f.write(arch_template)
    print(f"✅ Created architecture template: {template_file}")
    
    # Create quick reference guide
    quick_ref = """# Architecture Review Agent - Quick Reference

## Basic Usage

### Simple Review
```bash
python review_architecture.py my_architecture.md
```

### Generate HTML Report
```bash
python review_architecture.py my_architecture.md report.html
```

### Advanced Options
```bash
python architecture_review_agent.py architecture.md --output report.html --format html --standards-dir custom_standards
```

## Review Categories

The agent evaluates documents across these dimensions:

### 🔒 Security (Critical)
- Authentication mechanisms
- Authorization patterns  
- Data encryption
- Network security

### 📈 Scalability (High)
- Horizontal/vertical scaling
- Load balancing
- Caching strategies
- Auto-scaling

### 📊 Monitoring (Medium)
- Logging strategies
- Metrics collection
- Alerting setup
- Observability

### ✅ Completeness (High)
- Required sections
- Documentation standards
- Technical specifications

### 🏛️ Compliance (High)
- Regulatory requirements
- Industry standards
- Data governance

## Scoring System

- **90-100**: 🟢 EXCELLENT - Ready for implementation
- **75-89**: 🟡 GOOD - Minor improvements needed  
- **60-74**: 🟠 NEEDS IMPROVEMENT - Several issues to address
- **<60**: 🔴 REQUIRES MAJOR CHANGES - Significant rework needed

## Customization

1. **Review Rules**: Edit `standards/review_rules.json`
2. **Architecture Patterns**: Modify `standards/architecture_patterns.json` 
3. **Custom Standards**: Add JSON files to `custom_standards/`

## Enterprise Integration

### CI/CD Pipeline
Add to your build pipeline:
```yaml
- name: Architecture Review
  run: |
    python architecture_review_agent.py docs/architecture.md \\
      --output architecture-review.html --format html
```

### Review Checklist
- [ ] All critical security issues addressed
- [ ] Scalability patterns documented
- [ ] Monitoring strategy defined
- [ ] Compliance requirements met
- [ ] Architecture patterns followed
"""

    ref_file = Path("examples/quick_reference.md")
    with open(ref_file, 'w', encoding='utf-8') as f:
        f.write(quick_ref)
    print(f"✅ Created quick reference: {ref_file}")
    
    print("\n🎉 Setup completed successfully!")
    print("\n📁 Project structure:")
    print("├── architecture_review_agent.py  # Main agent")
    print("├── review_architecture.py       # Simple CLI runner")
    print("├── standards/                   # Default standards & rules")
    print("├── custom_standards/            # Your custom standards")
    print("├── examples/                    # Templates and examples")
    print("└── reports/                     # Generated reports")
    
    print("\n🚀 Quick start:")
    print("1. Copy your architecture document to this folder")
    print("2. Run: python review_architecture.py your_document.md")
    print("3. Review the results and recommendations")
    print("4. Generate HTML report: python review_architecture.py your_document.md report.html")
    
    print("\n📖 See examples/quick_reference.md for detailed usage information")
    
def main():
    create_project_structure()

if __name__ == "__main__":
    main()
