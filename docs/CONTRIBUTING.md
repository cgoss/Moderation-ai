# Contributing to Moderation Bot

Thank you for your interest in contributing to Moderation Bot!

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)
- [Project Structure](#project-structure)
- [Documentation](#documentation)

## Code of Conduct

### Our Pledge

In the interest of fostering an open and welcoming environment, we pledge to make participation in our project and our community a harassment-free experience for everyone.

### Our Standards

Examples of behavior that contributes to a positive environment:
- Using welcoming and inclusive language
- Being respectful of differing viewpoints and experiences
- Gracefully accepting constructive criticism
- Focusing on what is best for the community
- Showing empathy towards other community members

Unacceptable behavior:
- Harassment, insults, or derogatory comments
- Personal or political attacks
- Public or private harassment
- Publishing private information without permission
- Other unethical or unprofessional conduct

## Getting Started

### Prerequisites

- Python 3.10+
- Docker (optional but recommended)
- Git
- Text editor or IDE

### Development Setup

```bash
# Fork the repository
git fork https://github.com/your-org/moderation-bot.git

# Clone your fork
git clone https://github.com/your-username/moderation-bot.git
cd moderation-bot

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -e .[dev]
```

### Configure Environment

```bash
# Copy environment template
cp .env.template .env

# Edit with your values
nano .env
```

Required development settings:
```env
ENVIRONMENT=development
LOG_LEVEL=debug
DEBUG=true
DATABASE_URL=sqlite:///data/moderation_bot.db
```

### Run Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/unit/platforms/test_instagram.py

# Run with coverage
pytest --cov=src --cov-report=html
```

## Development Workflow

### Branching Strategy

- `main` - Production-ready code
- `develop` - Integration branch for staging
- `feature/*` - New features
- `bugfix/*` - Bug fixes
- `hotfix/*` - Critical fixes

### Git Workflow

```bash
# 1. Create feature branch
git checkout -b feature/your-feature-name

# 2. Make changes
# ... work on feature ...

# 3. Commit changes
git add .
git commit -m "feat: add your feature description"

# 4. Push to fork
git push origin feature/your-feature-name

# 5. Create pull request
# Via GitHub UI
```

### Commit Message Format

Follow conventional commits:

```
<type>(<scope>): <subject>

<body>

<footer>
```

Types:
- `feat` - New feature
- `fix` - Bug fix
- `docs` - Documentation
- `style` - Code style (formatting, etc.)
- `refactor` - Code refactoring
- `test` - Adding tests
- `chore` - Maintenance tasks

Examples:
```
feat(instagram): add comment bulk deletion
fix(auth): resolve token refresh issue
docs(api): update webhook documentation
test(redis): add rate limiter tests
```

## Coding Standards

### Python Code Style

Follow PEP 8 guidelines:
- Maximum line length: 100 characters
- Indentation: 4 spaces (no tabs)
- Imports: Organized by type, grouped
- Docstrings: Use Google style
- Type hints: Required for all functions

### Code Formatting

Use Black and isort:

```bash
# Format code
black src tests

# Sort imports
isort src tests

# Check formatting
black --check src tests
isort --check-only src tests
```

### Documentation Style

Use docstrings for all functions and classes:

```python
def moderate_comment(comment: Comment) -> ModerationResult:
    """
    Moderate a comment based on configured rules.
    
    Args:
        comment: The comment to moderate
        
    Returns:
        ModerationResult with action and reasoning
    """
    # Implementation...
```

### Error Handling

- Use specific exceptions
- Provide meaningful error messages
- Log errors with context
- Handle edge cases
- Never expose sensitive data in errors

## Testing

### Test Requirements

- Unit tests for all new features
- Integration tests for cross-platform workflows
- Code coverage minimum: 80%
- Tests must pass before merging

### Writing Tests

Use pytest framework:

```python
def test_comment_moderation():
    """Test comment moderation with profanity"""
    comment = Comment(
        id="test_1",
        text="This comment contains profanity",
        user_id="user_1"
    )
    
    result = moderate_comment(comment)
    
    assert result.action == "delete"
    assert "profanity" in result.reasoning
```

### Test Organization

```
tests/
├── unit/              # Unit tests
│   ├── platforms/      # Platform-specific tests
│   ├── analysis/       # Analysis module tests
│   └── core/          # Core module tests
├── integration/        # Integration tests
└── fixtures/          # Test fixtures
```

## Submitting Changes

### Pull Request Process

1. **Update documentation** - Add/update relevant docs
2. **Write tests** - Ensure test coverage
3. **Run tests** - All tests must pass
4. **Format code** - Run Black and isort
5. **Create PR** - Use clear title and description

### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] All tests passing

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-reviewed code
- [ ] Commented complex code
- [ ] Updated documentation
- [ ] No new warnings
- [ ] Added/updated tests
- [ ] All tests passing
```

### Review Process

- Maintain focus on provided PR description
- Provide constructive feedback
- Suggest improvements
- Ask clarifying questions
- Be respectful and collaborative

## Project Structure

```
moderation-bot/
├── src/                  # Source code
│   ├── analysis/         # Analysis modules
│   ├── core/            # Core functionality
│   └── platforms/        # Platform adapters
├── tests/               # Test suite
│   ├── fixtures/        # Test fixtures
│   ├── unit/           # Unit tests
│   └── integration/    # Integration tests
├── docs/              # Documentation
│   ├── platforms/       # Platform docs
│   ├── api/           # API docs
│   └── guides/        # User guides
├── scripts/            # Utility scripts
├── .github/            # GitHub Actions
│   └── workflows/      # CI/CD workflows
├── docker-compose.yml   # Docker configuration
└── Dockerfile          # Docker build
```

## Documentation

### Updating Documentation

If you add a new feature or change behavior:
1. Update relevant documentation in `docs/`
2. Add examples to user guides
3. Update API reference if endpoints changed
4. Add or update FAQ entries
5. Update CHANGELOG

### Documentation Standards

- Use Markdown format
- Include code examples
- Provide clear explanations
- Add diagrams where helpful
- Keep user guides up-to-date

### Code Comments

- Comment complex logic
- Explain non-obvious behavior
- Note platform-specific quirks
- Reference relevant documentation
- Keep comments up-to-date

## Feature Requests

### Proposing New Features

1. Check existing issues first
2. Search for similar requests
3. Create detailed proposal with:
   - Use case description
   - Proposed solution
   - Implementation approach
   - Alternative considerations

### Large Features

For significant features:
1. Discuss in issue first
2. Get consensus on approach
3. Break into smaller PRs
4. Maintain backward compatibility
5. Update documentation

## Reporting Issues

### Bug Reports

Include:
- Clear title
- Steps to reproduce
- Expected behavior
- Actual behavior
- Environment details
- Screenshots/logs if relevant
- Severity level

### Security Issues

For security vulnerabilities:
- Do not create public issue
- Email security team: security@example.com
- Include full details and reproduction steps
- We will respond within 24 hours

## Questions

### Where to Ask Questions

- GitHub Discussions (general questions)
- GitHub Issues (bugs, feature requests)
- Email security@example.com (security issues only)

### Getting Help

- Check existing documentation
- Search for similar issues
- Join community Discord
- Ask on GitHub Discussions

## Recognition

Contributors will be recognized in:
- CHANGELOG for each release
- Contributors section in README
- Annual project summary
- Special thanks for major contributions

Thank you for contributing to Moderation Bot!

---

**Contributing Guide v1.0** - Last Updated: January 8, 2026
