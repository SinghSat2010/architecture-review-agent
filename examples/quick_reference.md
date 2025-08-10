# Architecture Review Agent - Quick Reference

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
    python architecture_review_agent.py docs/architecture.md \
      --output architecture-review.html --format html
```

### Review Checklist
- [ ] All critical security issues addressed
- [ ] Scalability patterns documented
- [ ] Monitoring strategy defined
- [ ] Compliance requirements met
- [ ] Architecture patterns followed
