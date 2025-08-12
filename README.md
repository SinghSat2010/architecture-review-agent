# Architecture Review Agent

An intelligent agent that reads solution architecture, architecture patterns, and architecture standards artifacts to provide comprehensive review comments and prepare enterprise architects for reviews.

## Features

🔍 **Comprehensive Analysis**
- Automatically detects architecture artifact types
- Checks for completeness and required sections
- Validates security considerations and best practices
- Reviews scalability and performance design
- Assesses monitoring and observability patterns
- Evaluates compliance requirements

📊 **Intelligent Scoring**
- Calculates overall architecture quality score (0-100)
- Provides severity-based issue categorization (Critical, High, Medium, Low)
- Generates weighted assessments based on importance

📝 **Multiple Output Formats**
- JSON reports for programmatic processing
- HTML reports for web viewing
- Markdown reports for documentation
- Console output for quick feedback

🎯 **Enterprise Architect Preparation**
- Generates preparation notes for review meetings
- Highlights critical issues requiring immediate attention
- Provides reference materials and standards links
- Suggests discussion topics and focus areas

📄 **Multi-Format Document Support**
- **Word Documents**: .docx and .doc files with full text extraction
- **PDF Files**: Comprehensive text extraction with layout preservation
- **Text Files**: Plain text (.txt) and rich text (.rtf) documents
- **Markdown**: .md files with header-based section detection
- **HTML**: Web documents with structured content extraction
- **Excel**: Spreadsheet data extraction and analysis
- **PowerPoint**: Presentation content extraction (coming soon)

## Installation

1. **Clone or download the files:**
```bash
# Download the main files to your working directory
# - architecture_review_agent.py
# - requirements.txt
# - standards/ directory with configuration files
```

2. **Install dependencies (optional):**
```bash
pip install -r requirements.txt
```

The agent works with Python's standard library, but optional dependencies provide enhanced functionality.

### Document Processing Dependencies

For full document format support, install the enhanced dependencies:

```bash
# Core document processing
pip install python-docx python-docx2txt PyPDF2 pdfplumber

# Additional formats
pip install openpyxl beautifulsoup4 lxml

# Or install all at once
pip install -r requirements.txt
```

**Supported formats by dependency:**
- **python-docx**: Word .docx files
- **python-docx2txt**: Word .doc files  
- **PyPDF2/pdfplumber**: PDF files
- **openpyxl**: Excel files
- **beautifulsoup4**: HTML files
- **Built-in**: Text, Markdown files

## Quick Start

### 1. Basic Review
```bash
# Markdown files
python architecture_review_agent.py sample_architecture.md

# Word documents
python architecture_review_agent.py architecture.docx
python architecture_review_agent.py architecture.doc

# PDF files
python architecture_review_agent.py architecture.pdf

# Text files
python architecture_review_agent.py architecture.txt
```

### 2. Generate HTML Report
```bash
python architecture_review_agent.py sample_architecture.md --output report.html --format html
```

### 3. Specify Artifact Type
```bash
python architecture_review_agent.py my_doc.docx --type solution_architecture --output review.json
```

## Configuration

### Standards Directory Structure
```
standards/
├── review_rules.json          # Review criteria and patterns
├── architecture_patterns.json # Known architecture patterns
└── custom_standard.json      # Organization-specific standards
```

### Customizing Review Rules

Edit `standards/review_rules.json` to customize:

```json
{
  "security": {
    "patterns": ["authentication", "authorization", "encryption"],
    "severity": "critical",
    "minimum_coverage": 4,
    "weight": 35
  },
  "completeness": {
    "required_sections": [
      "executive_summary",
      "architecture_overview", 
      "security_considerations"
    ],
    "severity": "high"
  }
}
```

### Adding Architecture Patterns

Add new patterns to `standards/architecture_patterns.json`:

```json
{
  "my_pattern": {
    "description": "Custom architecture pattern",
    "characteristics": ["feature1", "feature2"],
    "best_practices": [
      "Best practice 1",
      "Best practice 2"
    ],
    "when_to_use": ["Use case 1", "Use case 2"]
  }
}
```

## Usage Examples

### Command Line Interface

```bash
# Basic review with console output
python architecture_review_agent.py architecture.md

# Generate detailed HTML report
python architecture_review_agent.py architecture.md -o report.html --format html

# Use custom standards directory
python architecture_review_agent.py doc.md --standards-dir ./my-standards

# Review specific artifact type
python architecture_review_agent.py doc.md --type technical_specification
```

### Programmatic Usage

```python
from architecture_review_agent import ArchitectureReviewAgent, ArtifactType

# Initialize agent
agent = ArchitectureReviewAgent(standards_dir="./standards")

# Load and review artifact
artifact = agent.load_artifact("architecture.md", ArtifactType.SOLUTION_ARCHITECTURE)
comments = agent.review_artifact(artifact)

# Generate report
report = agent.generate_review_report(artifact, comments)
print(f"Overall Score: {report['review_summary']['overall_score']}/100")

# Export report
agent.export_report(report, "review_report.html", "html")
```

## Review Categories

The agent evaluates architecture documents across multiple dimensions:

### 🔒 Security
- Authentication and authorization mechanisms
- Encryption and data protection
- Network security configurations
- Security audit trails

### 📈 Scalability  
- Horizontal and vertical scaling strategies
- Load balancing and auto-scaling
- Caching and performance optimization
- Database scaling approaches

### 📊 Monitoring & Observability
- Logging and monitoring strategies
- Metrics and alerting configurations
- Dashboard and visualization plans
- Distributed tracing capabilities

### ✅ Completeness
- Required documentation sections
- Architecture diagrams and models
- Technical specifications
- Implementation guidelines

### 🏛️ Compliance
- Regulatory requirements (GDPR, HIPAA, SOX)
- Industry standards compliance
- Data retention and privacy policies
- Audit and governance frameworks

### 🏗️ Architecture Patterns
- Microservices best practices
- Layered architecture principles
- Event-driven design patterns
- Serverless architecture guidelines

## Report Output

### Console Output
```
📊 Review Summary:
   Overall Score: 75/100
   Total Issues: 8
   Critical: 1
   High: 3

🚨 Critical Issues:
   • Insufficient security considerations documented
```

### JSON Report Structure
```json
{
  "artifact_info": {
    "file_path": "architecture.md",
    "artifact_type": "solution_architecture",
    "overall_score": 75
  },
  "review_summary": {
    "total_comments": 8,
    "severity_breakdown": {
      "critical": 1,
      "high": 3,
      "medium": 3,
      "low": 1
    }
  },
  "comments": [...],
  "preparation_notes": [...]
}
```