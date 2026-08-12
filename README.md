# AI-Powered Project Management & Consultation Tool

> **ARCHIVED (August 2026)** — This project is no longer under active development.  
> Read the closeout note: **[ARCHIVE.md](ARCHIVE.md)** · Español: **[CIERRE.md](CIERRE.md)**

**Historical prototype:** Next Level RAG + human-in-the-loop (spike 2025)

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Archived-lightgrey.svg)]()

Prefer Spanish? Read the documentation in Spanish: [LEAME.md](LEAME.md)

## Overview

> The sections below describe the **historical design** of this spike. They are kept for reference and are not a claim of production readiness.

This project explored an evolution from a simple RAG system toward a semi-autonomous project-management agent with human-in-the-loop capabilities, inspired by HumanLayer practices and Context Engineering.

It was an experiment in intelligent consultation, automated project analysis, and human oversight for critical decisions. **Development stopped in 2025; the repo was formally archived in August 2026** because modern coding agents (e.g. Cursor) already cover most of the intended day-to-day value.

## 🎯 Key Capabilities

- Intelligent task specification: contracts and structured prompts from natural queries
- Advanced context management: summarization, budget control, logging and dashboard
- Hybrid retrieval: semantic vectors + BM25 with reranking and rich metadata
- Subagent pipeline: analysis, synthesis, verification with orchestrated flow
- Human-in-the-loop: approval gates, risk detection, notifications, async handling
- GitHub integration: PR/Issue indexing for enriched project context
- Metrics and auditability end-to-end

## 🏗️ Architecture

### **Core Components**

```
┌─────────────────────────────────────────────────────────────┐
│                    Next Level RAG System                    │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │ Spec Layer  │  │   Context   │  │  Retrieval  │          │
│  │             │  │  Manager    │  │   System    │          │
│  └─────────────┘  └─────────────┘  └─────────────┘          │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │ Subagents   │  │ Human Loop  │  │  Pipeline   │          │
│  │ Pipeline    │  │   System    │  │  Metrics    │          │
│  └─────────────┘  └─────────────┘  └─────────────┘          │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │   GitHub    │  │  Milvus     │  │  Advanced   │          │
│  │ Integration │  │  Vector DB  │  │  Analytics  │          │
│  └─────────────┘  └─────────────┘  └─────────────┘          │
└─────────────────────────────────────────────────────────────┘
```

### **Project Structure**

```
Herramienta_de_Diagnostico_Consulta_Con_IA/
├── 📁 app/                          # Core application modules
│   ├── 📁 api/                      # FastAPI endpoints
│   ├── 📁 retrieval/                # Hybrid retrieval system
│   ├── 📁 subagents/                # Subagent pipeline
│   ├── 📁 specs/                    # Task contract templates
│   ├── 📁 prompts/                  # System prompts
│   ├── 📁 eval/                     # Evaluation components
│   ├── context_manager.py           # Advanced context management
│   ├── context_logger.py            # Context logging
│   ├── dashboard_context.py         # Streamlit dashboard
│   ├── pipeline_metrics.py          # Pipeline performance
│   ├── spec_layer.py                # Spec-first architecture
│   ├── human_loop.py                # Human-in-the-loop system
│   └── cursor_agent.py              # Background task agent
├── 📁 config/                       # Configuration files
│   ├── spec_layer.yml               # Spec layer configuration
│   ├── human_loop.yml               # Human loop settings
│   ├── cursor_agent.yml             # Cursor agent config
│   ├── evaluation.yml               # Evaluation system config
│   └── github_indexing.yml          # GitHub integration config
├── 📁 docs/                         # Comprehensive documentation
│   ├── README.md                    # Documentation index
│   ├── MANUAL_USUARIO.md            # User Manual (Spanish)
│   ├── USER_MANUAL.md               # User Manual (English)
│   ├── README_NEXT_LEVEL.md         # Architecture & evolution plan
│   └── PROGRESS.md                  # Progress & roadmap
├── 📁 tests/                        # Tests, examples & audits
│   ├── README.md                    # Tests documentation
│   ├── audit_system_completeness.py # System completeness audit
│   ├── example_spec_layer.py        # Spec layer examples
│   ├── example_human_loop.py        # Human loop examples
│   ├── example_cursor_integration.py # Cursor integration examples
│   ├── example_evaluation_system.py # Evaluation system examples
│   ├── example_pipeline_subagents.py # Subagent pipeline examples
│   └── test_github_indexing.py      # GitHub indexing tests
├── 📁 scripts/                      # Utility scripts
│   └── index_github.py              # GitHub PR/Issue indexer
├── 📁 eval/                         # Evaluation & metrics
│   └── evaluate_plans.py            # Plan evaluator system
├── 📁 logs/                         # Audit logs & metrics
│   └── audit.jsonl                  # Comprehensive audit trail
├── 📁 knowledge_base/               # Knowledge base files
├── README.md                        # Main project documentation (English)
├── LEAME.md                         # Main project documentation (Spanish)
├── requirements.txt                 # Python dependencies
└── setup.py                         # Project setup & installation
```

### **Data Flow**

1. **Query Input** → Spec Layer generates task contract
2. **Context Analysis** → Context Manager provides relevant history
3. **Intelligent Retrieval** → Hybrid system finds relevant information
4. **Subagent Processing** → Analysis, synthesis, and verification
5. **Human Oversight** → Critical decisions require human approval
6. **Execution** → Background agents perform approved actions
7. **Audit Trail** → Complete logging of all decisions and actions

## 🚀 Quick Start

### **Prerequisites**

- Python 3.8+
- Docker (for Milvus)
- GitHub Personal Access Token
- Slack Webhook URL (optional)

### **Installation**

```bash
# Clone the repository
git clone https://github.com/polsebas/Herramienta_de_Diagnostico_Consulta_Con_IA.git
cd Herramienta_de_Diagnostico_Consulta_Con_IA

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export GITHUB_TOKEN="your_github_token"
export MILVUS_URI="localhost:19530"
export SLACK_WEBHOOK_URL="your_slack_webhook"  # Optional
```

### **Basic Usage**

```python
from app.spec_layer import build_task_contract, render_system_prompt
from app.context_manager import ContextManager
from app.subagents.orchestrator import SubagentOrchestrator

# Generate task contract
contract = build_task_contract(
    query="How to implement JWT authentication?",
    user_role="developer",
    risk_level="medium"
)

# Get system prompt
system_prompt = render_system_prompt(contract)

# Initialize components
context_manager = ContextManager()
orchestrator = SubagentOrchestrator(
    hybrid_retriever=hybrid_retriever,
    context_manager=context_manager
)

# Process query
result = await orchestrator.process_query(
    query="How to implement JWT authentication?",
    user_role="developer",
    risk_level="medium"
)
```

### **GitHub Indexing**

```bash
# Index repository PRs and issues
python scripts/index_github.py --repo owner/repo --limit 50

# Index only PRs
python scripts/index_github.py --repo owner/repo --type prs --limit 25

# Index from specific date
python scripts/index_github.py --repo owner/repo --since 2025-01-01
```

### **Human-in-the-Loop Demo**

```bash
# Run comprehensive demo
python example_human_loop.py

# This demonstrates:
# - Basic approval workflows
# - Critical action detection
# - Multi-channel notifications
# - Timeout handling
# - Callback system
```

## 📊 Performance Metrics

### **Current Achievements**

- **Context Compression**: 30-70% optimal compression ratio
- **Verification Score**: ≥0.8 average (vs. baseline 0.6)
- **Hallucination Detection**: +40% precision improvement
- **Retrieval Recall**: +20% with hybrid search + reranking
- **Human Response Time**: <1 hour average for approvals

### **Target Metrics**

- **Plan Precision**: ≥90% accuracy on golden set
- **Automation Rate**: ≥70% subtasks without human intervention
- **Traceability**: 100% actions with complete audit trail
- **Quality Score**: ≥0.9 average verification score

## 🔧 Configuration

### **Environment Variables**

```bash
# Required
GITHUB_TOKEN=your_github_token
MILVUS_URI=localhost:19530

# Optional
SLACK_WEBHOOK_URL=your_slack_webhook
MILVUS_COLLECTION=github_items
GITHUB_INDEXING_CONFIG=config/custom_config.yml
```

### **Configuration Files**

- `config/github_indexing.yml` - GitHub indexing parameters
- `config/human_loop.yml` - Human-in-the-Loop settings
- `app/specs/*.yaml` - Task contract templates

## 🧪 Testing

### **Run All Tests**

```bash
# GitHub indexing tests
python scripts/test_github_indexing.py

# Human loop demo
python example_human_loop.py

# Pipeline demo
python example_pipeline_subagents.py
```

### **Test Coverage**

- See `tests/` folder and example scripts for runnable demos and checks

## 📁 Project Structure

```
├── app/                          # Core application modules
│   ├── spec_layer.py            # Task contract generation
│   ├── context_manager.py       # Context management and compaction
│   ├── context_logger.py        # Advanced logging system
│   ├── dashboard_context.py     # Streamlit dashboard
│   ├── human_loop.py            # Human-in-the-Loop system
│   ├── subagents/               # Subagent pipeline
│   │   ├── orchestrator.py      # Pipeline coordination
│   │   ├── verification.py      # Quality verification
│   │   ├── analysis.py          # Content analysis
│   │   ├── synthesis.py         # Response generation
│   │   └── retrieval.py         # Information retrieval
│   ├── retrieval/               # Retrieval system
│   │   ├── hybrid.py            # Hybrid search engine
│   │   ├── milvus_store.py      # Vector database integration
│   │   └── bm25_index.py        # Keyword search index
│   ├── specs/                   # Task contract templates
│   └── prompts/                 # Prompt templates
├── scripts/                      # Utility scripts
│   ├── index_github.py          # GitHub indexing
│   └── test_github_indexing.py  # Indexing tests
├── config/                       # Configuration files
│   ├── github_indexing.yml      # GitHub indexing config
│   └── human_loop.yml           # Human loop config
├── examples/                     # Example scripts
├── logs/                         # Log files
└── docs/                         # Documentation
```

## Roadmap

**Frozen.** Historical progress notes: [`docs/PROGRESS.md`](docs/PROGRESS.md).  
Closeout and archival rationale: [`ARCHIVE.md`](ARCHIVE.md).

## Contributing

This repository is **archived**. No new features or contributions are accepted. See [ARCHIVE.md](ARCHIVE.md).

## Documentation

- Closeout: [`ARCHIVE.md`](ARCHIVE.md) / [`CIERRE.md`](CIERRE.md)
- Historical docs index: [`docs/README.md`](docs/README.md)
- Historical progress: [`docs/PROGRESS.md`](docs/PROGRESS.md)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- **HumanLayer**: Inspiration for human-in-the-loop architecture
- **Context Engineering**: Best practices for context management
- **Milvus**: Vector database used in the spike
- **Coding agents (Cursor et al.)**: Ecosystem that absorbed most of the original use case

## Support

Archived project — no active support. New issues should be closed as out of scope.

---

**Archived (August 2026).** See [ARCHIVE.md](ARCHIVE.md) for learnings and what (if anything) is worth reusing elsewhere. 