# Quick Start Guide - Moderation AI

## 🚀 Get Started in 5 Steps

### Step 1: Understand the Project (15 minutes)
Read these in order:
1. **[README.md](README.md)** - Project overview and features
2. **[ARCHITECTURE.md](ARCHITECTURE.md)** - System design and components
3. **[docs/implementation-phases.md](docs/implementation-phases.md)** - 7-phase roadmap

### Step 2: Set Up Development Environment (10 minutes)
```bash
# Create virtual environment
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -e ".[dev]"  # Install in development mode

# Verify installation
pytest --version  # Should show pytest version
```

### Step 3: Review Core Documentation (20 minutes)
1. **[docs/llm-context-guide.md](docs/llm-context-guide.md)** - How to use this library
2. **[docs/standards-and-metrics.md](docs/standards-and-metrics.md)** - Moderation standards
3. **[CONTRIBUTING.md](CONTRIBUTING.md)** - Development workflow

### Step 4: Create GitHub Issues (5 minutes)

**Option A: Using GitHub CLI (Recommended)**
```bash
# Make script executable (Unix/Mac)
chmod +x create-issues.sh

# Run the script
./create-issues.sh
```

**Option B: Manual Creation**
Create issues in GitHub using the templates in `.github/ISSUE_TEMPLATE/`

### Step 5: Review Phase 1 Work (5 minutes)
See [docs/implementation-phases.md](docs/implementation-phases.md) **Phase 1** section:
- 6 API Reference documents to create
- 8 Comment Analysis Framework documents
- Due in 2 weeks (Weeks 2-3)

---

## 📋 Phase 0 Checklist (Completed ✅)

Foundation is established:
- [x] Project structure created
- [x] 8 core documentation files written
- [x] 7 phases planned in detail
- [x] GitHub issue templates created
- [x] Issue generation script ready
- [x] Development environment ready

---

## 🎯 Phase 1 Overview (Next: Weeks 2-3)

**Goal**: Document unified API patterns and analysis methodologies

**Deliverables**: 14 markdown documents
- 6 API Reference documents
- 8 Comment Analysis documents

**Start by creating**:
1. `docs/api-reference/README.md`
2. `docs/comment-analysis/README.md`

Then fill in the detailed documents in each section.

---

## 📖 Key Documents to Know

### For Understanding the Project
- **[README.md](README.md)** - Start here for overview
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Understand the system design
- **[docs/standards-and-metrics.md](docs/standards-and-metrics.md)** - Core moderation logic

### For Development
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - How to contribute
- **[docs/implementation-phases.md](docs/implementation-phases.md)** - Full roadmap
- **[pyproject.toml](pyproject.toml)** - Python configuration

### For LLMs
- **[docs/llm-context-guide.md](docs/llm-context-guide.md)** - How to use this library
- **[docs/standards-and-metrics.md](docs/standards-and-metrics.md)** - Moderation rules
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System design

---

## 💡 Common Tasks

### Run Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test
pytest tests/core/test_analyzer.py
```

### Format Code
```bash
# Format with Black
black src/ tests/

# Sort imports
isort src/ tests/

# Check style
flake8 src/
```

### View Project Status
```bash
# Check git status
git status

# View project structure
# (Use file explorer or ls -la)

# View current directory
pwd
```

### Create a New Feature Branch
```bash
# Get latest from main
git fetch origin
git checkout main
git pull

# Create feature branch
git checkout -b feature/my-feature-name
```

---

## 🔧 Important Files and Directories

| Path | Purpose |
|------|---------|
| `README.md` | Project overview |
| `ARCHITECTURE.md` | System design |
| `CONTRIBUTING.md` | Development guide |
| `docs/` | LLM context library |
| `docs/standards-and-metrics.md` | Moderation rules |
| `platforms/` | Platform-specific documentation |
| `src/` | Python source code |
| `tests/` | Test suite |
| `examples/` | Usage examples |
| `.github/ISSUE_TEMPLATE/` | Issue templates |
| `create-issues.sh` | Script to create GitHub issues |
| `pyproject.toml` | Python project configuration |
| `requirements.txt` | Python dependencies |

---

## 🎓 Learning Path

**Day 1: Understand**
- Read README.md
- Skim ARCHITECTURE.md
- Review one platform doc structure

**Day 2: Set Up**
- Set up development environment
- Install dependencies
- Create GitHub issues

**Day 3: Plan**
- Review Phase 1 tasks
- Understand standards framework
- Plan documentation approach

**Week 2-3: Build**
- Create Phase 1 documents
- Review with team
- Prepare for Phase 3 (implementation)

---

## ❓ FAQ

### Q: Where do I start?
**A**: Read README.md, then ARCHITECTURE.md, then understand the 7 phases in docs/implementation-phases.md

### Q: What comes after Phase 0?
**A**: Phase 1 is creating API reference and analysis framework documentation (14 documents in Weeks 2-3)

### Q: How do I contribute?
**A**: See CONTRIBUTING.md for the full workflow

### Q: What's the project goal?
**A**: Create an LLM context library and Python framework for moderating content across 6 social platforms

### Q: What should I do first?
**A**:
1. Read the quick start files (README, ARCHITECTURE)
2. Set up your development environment
3. Create GitHub issues using create-issues.sh
4. Review Phase 1 tasks

### Q: Where is the moderation logic?
**A**: In docs/standards-and-metrics.md - defines 5 core standards with testable metrics

### Q: How does the LLM integration work?
**A**: See docs/llm-context-guide.md for how LLMs consume this library

---

## 🚦 Next Immediate Steps

1. **Right now**:
   - Read README.md (5 min)
   - Review ARCHITECTURE.md (10 min)

2. **Within 1 hour**:
   - Set up virtual environment
   - Install dependencies
   - Make script executable

3. **Before starting Phase 1**:
   - Create GitHub issues: `./create-issues.sh`
   - Assign issues to team
   - Review standards and metrics

4. **Begin Phase 1**:
   - Create API Reference documentation
   - Create Comment Analysis documentation
   - 14 documents total, 2 weeks

---

## 📞 Getting Help

### Documentation
- See the specific document mentioned in error/question
- Check ARCHITECTURE.md for system overview
- Review CONTRIBUTING.md for development help
- Check docs/standards-and-metrics.md for moderation logic

### Code
- Look at the structure in `src/` (not yet implemented)
- Review test examples (to be added in Phase 3)
- Check CONTRIBUTING.md for coding standards

### Planning
- See docs/implementation-phases.md for timeline
- Check GitHub issues (create with `./create-issues.sh`)
- Review Phase-specific documentation

---

## ✅ Success Criteria

You're ready when:
- [x] README understood
- [x] ARCHITECTURE reviewed
- [x] Development environment set up
- [x] GitHub issues created
- [x] Phase 1 scope understood
- [x] Team assigned to tasks
- [x] Documentation structure reviewed

---

## 🎯 Current Status

**Phase 0: COMPLETE ✅**
- Foundation established
- 8 core documents created
- 7 phases planned
- 60 issues ready to create
- Development environment ready

**Next**: Phase 1 - Create API Reference & Analysis Framework

---

**Time to complete this quick start**: ~45 minutes
**Then ready for**: Phase 1 work (API documentation)
**Timeline**: 2 weeks (Weeks 2-3)

Ready to start? Begin with [README.md](README.md) 👇
