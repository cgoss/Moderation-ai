# Contributing to Moderation AI

Thank you for your interest in contributing to the Moderation AI project! This document provides guidelines and instructions for contributing.

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [Development Workflow](#development-workflow)
4. [Coding Standards](#coding-standards)
5. [Testing Requirements](#testing-requirements)
6. [Documentation Standards](#documentation-standards)
7. [Submitting Changes](#submitting-changes)
8. [Adding New Platforms](#adding-new-platforms)
9. [Adding Analysis Modules](#adding-analysis-modules)
10. [Reporting Issues](#reporting-issues)

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive environment for all contributors. We pledge to:

- Be respectful and constructive in all interactions
- Welcome diverse perspectives and backgrounds
- Focus on what's best for the community
- Show empathy towards other community members
- Address concerns professionally and promptly

### Expected Behavior

- Use welcoming and inclusive language
- Be respectful of differing opinions and experiences
- Accept constructive criticism gracefully
- Focus on criticism of ideas, not individuals
- Respect the privacy and dignity of all members

### Unacceptable Behavior

- Harassment, discrimination, or exclusion based on protected characteristics
- Intimidation, threats, or aggressive language
- Unwelcome sexual attention or advances
- Trolling, insulting, or derogatory comments
- Any form of abuse or bullying

### Enforcement

Violations of this code of conduct will be addressed promptly. Serious violations may result in removal from the project.

## Getting Started

### Prerequisites

- **Python**: 3.9 or higher
- **Git**: Latest version
- **pip**: Package manager

### 1. Fork the Repository

```bash
# Go to https://github.com/cgoss/Moderation-ai
# Click "Fork" button to create your own fork
```

### 2. Clone Your Fork

```bash
git clone https://github.com/YOUR_USERNAME/Moderation-ai.git
cd Moderation-ai
```

### 3. Add Upstream Remote

```bash
git remote add upstream https://github.com/cgoss/Moderation-ai.git
git remote set-url origin https://github.com/YOUR_USERNAME/Moderation-ai.git
```

### 4. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python -m venv venv
source venv/bin/activate
```

### 5. Install Dependencies

```bash
# Install project dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -e ".[dev]"
```

### 6. Verify Installation

```bash
# Run tests to verify setup
pytest tests/

# Should see output like:
# ===== test session starts =====
# ...
# ===== passed in X.XXs =====
```

## Development Workflow

### 1. Create a Feature Branch

```bash
# Update main branch
git fetch upstream
git checkout main
git merge upstream/main

# Create feature branch with descriptive name
git checkout -b feature/add-abuse-detector
# or
git checkout -b fix/twitter-rate-limit-bug
# or
git checkout -b docs/clarify-authentication
```

### 2. Branch Naming Conventions

- **Features**: `feature/descriptive-name`
- **Bug Fixes**: `fix/descriptive-name`
- **Documentation**: `docs/descriptive-name`
- **Tests**: `test/descriptive-name`
- **Refactoring**: `refactor/descriptive-name`

### 3. Commit Messages

Write clear, descriptive commit messages:

```
Imperative, present tense: "add" not "added"
Don't capitalize first letter
No period (.) at the end
Limit to 50 characters (with exceptions for special cases)

Examples:
- Add comment summarization module
- Fix Twitter API rate limit handling
- Update authentication documentation
- Refactor sentiment analyzer for performance
```

### 4. Keep Commits Atomic

Each commit should represent a single logical change:

```bash
# Good: One feature per commit
git commit -m "add comment summarizer module"
git commit -m "add summarizer tests"

# Avoid: Multiple unrelated changes in one commit
git commit -m "add summarizer and fix twitter bug and update docs"
```

### 5. Push to Your Fork

```bash
git push origin feature/add-abuse-detector
```

### 6. Create Pull Request

1. Go to GitHub: https://github.com/cgoss/Moderation-ai
2. Click "New Pull Request"
3. Select your fork and branch
4. Fill in the PR template
5. Submit for review

## Coding Standards

### Python Style Guide

We follow PEP 8 with some modifications. Use Black formatter and isort.

#### Formatting

```bash
# Format code with Black (100 character line length)
black src/ tests/

# Sort imports with isort
isort src/ tests/
```

#### Code Style

```python
# Good
def analyze_comment(comment: Comment, strict: bool = False) -> AnalysisResult:
    """Analyze a single comment for moderation.

    Args:
        comment: The comment to analyze
        strict: Whether to use strict moderation rules

    Returns:
        AnalysisResult containing moderation decision
    """
    result = AnalysisResult()
    # Implementation
    return result


# Avoid
def analyze_comment(comment, strict=False):
    # No type hints
    result = {}  # No clear return type
    return result
```

#### Type Hints

Use type hints for all public functions:

```python
# Good - complete type hints
def batch_analyze(comments: List[Comment]) -> List[AnalysisResult]:
    pass

# Acceptable - simple cases
def get_config() -> dict:
    pass

# Avoid - no type hints on public API
def analyze(comment):
    pass
```

#### Documentation Strings

Use Google-style docstrings:

```python
def moderate_comment(comment: Comment, action: ModerationAction) -> bool:
    """Moderate a comment by taking specified action.

    This function executes the moderation action on the specified
    comment through the appropriate platform API.

    Args:
        comment: The comment to moderate
        action: The moderation action to take (approve, flag, hide, remove)

    Returns:
        True if moderation was successful, False otherwise

    Raises:
        AuthenticationError: If credentials are invalid
        RateLimitError: If API rate limit exceeded
        PlatformError: If platform-specific error occurs

    Example:
        >>> comment = Comment(id="123", text="Great post!")
        >>> success = moderate_comment(comment, ModerationAction.APPROVE)
        >>> print(success)
        True
    """
    pass
```

### Naming Conventions

```python
# Classes: PascalCase
class CommentAnalyzer:
    pass

# Functions/methods: snake_case
def analyze_sentiment(text: str) -> str:
    pass

# Constants: UPPER_SNAKE_CASE
MAX_RETRIES = 3
RATE_LIMIT_PER_MINUTE = 60

# Private methods: _leading_underscore
def _internal_helper():
    pass

# Module-level (rare): snake_case
DATABASE_URL = "postgresql://..."
```

### Code Organization

```python
# Good organization within a class
class CommentAnalyzer:
    # Class variables
    DEFAULT_TIMEOUT = 30

    def __init__(self):
        # Initialize
        pass

    def analyze(self, comment: Comment) -> AnalysisResult:
        """Public method - main API"""
        pass

    def batch_analyze(self, comments: List[Comment]) -> List[AnalysisResult]:
        """Public method - alternative entry point"""
        pass

    def _preprocess(self, text: str) -> str:
        """Private helper method"""
        pass

    def _extract_features(self, text: str) -> Dict[str, float]:
        """Private helper method"""
        pass
```

### Error Handling

```python
# Good - specific exceptions
try:
    response = api.fetch_comment(comment_id)
except AuthenticationError as e:
    logger.error(f"Auth failed: {e}")
    raise
except RateLimitError as e:
    logger.warning(f"Rate limited, retrying: {e}")
    time.sleep(backoff_time)
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    raise

# Avoid - catching everything
try:
    response = api.fetch_comment(comment_id)
except:
    pass
```

## Testing Requirements

### Test Coverage

- Minimum **80% coverage** for core and analysis modules
- Minimum **70% coverage** for platform integrations
- All public APIs must have tests

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/core/test_analyzer.py

# Run specific test
pytest tests/core/test_analyzer.py::test_analyze_comment

# Run with verbose output
pytest -v

# Run with print statements visible
pytest -s
```

### Test Structure

```python
# tests/core/test_analyzer.py

import pytest
from unittest.mock import Mock, patch
from moderation_ai.core.analyzer import CommentAnalyzer
from moderation_ai.models import Comment, AnalysisResult


class TestCommentAnalyzer:
    """Test suite for CommentAnalyzer"""

    @pytest.fixture
    def analyzer(self):
        """Create analyzer instance for testing"""
        return CommentAnalyzer()

    @pytest.fixture
    def sample_comment(self):
        """Create sample comment for testing"""
        return Comment(
            id="test-123",
            text="Great content!",
            author_id="user-456"
        )

    def test_analyze_returns_result(self, analyzer, sample_comment):
        """Test that analyze returns AnalysisResult"""
        result = analyzer.analyze(sample_comment)
        assert isinstance(result, AnalysisResult)

    def test_analyze_detects_sentiment(self, analyzer, sample_comment):
        """Test that sentiment is detected"""
        result = analyzer.analyze(sample_comment)
        assert result.sentiment in ["positive", "negative", "neutral"]

    @pytest.mark.parametrize("text,expected_sentiment", [
        ("Great!", "positive"),
        ("Terrible", "negative"),
        ("OK", "neutral"),
    ])
    def test_analyze_sentiment_accuracy(self, analyzer, text, expected_sentiment):
        """Test sentiment detection accuracy with multiple inputs"""
        comment = Comment(id="test", text=text, author_id="user")
        result = analyzer.analyze(comment)
        assert result.sentiment == expected_sentiment
```

### Writing Tests

```python
# Good test structure
def test_specific_behavior():
    """Test that [behavior] happens when [condition]"""
    # Setup
    analyzer = CommentAnalyzer()
    comment = Comment(id="1", text="test", author_id="user")

    # Act
    result = analyzer.analyze(comment)

    # Assert
    assert result.sentiment == "neutral"
    assert result.violation_detected is False


# Avoid vague tests
def test_analyze():
    """Test analyze"""
    analyzer = CommentAnalyzer()
    result = analyzer.analyze(...)
    assert result is not None
```

## Documentation Standards

### Markdown Style

All documentation must be in Markdown format with consistent structure:

```markdown
---
title: Document Title
category: [core|platform|api|analysis]
platform: [twitter|reddit|etc]  # If applicable
related:
  - path/to/related/doc.md
---

# Title

Clear introduction paragraph explaining the purpose.

## Section Heading

Content in this section...

### Subsection

More detailed content...

## Code Examples

\`\`\`python
# Code examples should be runnable
def example():
    pass
\`\`\`

## Related Documentation

- [Link to related doc](path/to/doc.md)
```

### Documentation Rules

1. **Clarity**: Use simple, direct language
2. **Completeness**: Cover all important aspects
3. **Examples**: Include practical examples
4. **Links**: Cross-reference related docs
5. **Current**: Keep documentation up-to-date
6. **LLM-Ready**: Structure for LLM consumption

### API Documentation

Document all public classes and methods:

```markdown
## Comment Analyzer

The comment analyzer examines text and generates a comprehensive analysis.

### Methods

#### analyze(comment: Comment) → AnalysisResult

Analyze a single comment.

**Parameters:**
- `comment` (Comment): The comment to analyze

**Returns:**
- `AnalysisResult`: Analysis results including sentiment, categories, violations

**Raises:**
- `ValueError`: If comment text is empty
- `ProcessingError`: If analysis fails

**Example:**
\`\`\`python
analyzer = CommentAnalyzer()
comment = Comment(id="123", text="Great content!")
result = analyzer.analyze(comment)
print(result.sentiment)  # "positive"
\`\`\`
```

## Submitting Changes

### Pull Request Checklist

Before submitting, ensure:

- [ ] Code follows style guide (run `black` and `isort`)
- [ ] All tests pass (`pytest`)
- [ ] Test coverage is adequate (80%+ for new code)
- [ ] Type hints are present on public APIs
- [ ] Docstrings follow Google style
- [ ] Documentation is updated if needed
- [ ] No breaking changes to public API
- [ ] Commit messages are clear and concise
- [ ] Branch is up-to-date with main (`git fetch upstream && git rebase upstream/main`)

### Pull Request Template

```markdown
## Description

Clear description of what this PR does.

## Related Issue

Fixes #issue_number

## Type of Change

- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing

- [ ] Unit tests added/updated
- [ ] Integration tests passed
- [ ] Manual testing completed

## Documentation

- [ ] Documentation updated
- [ ] Code comments added where needed
- [ ] Examples provided for new features

## Screenshots (if applicable)

Include screenshots for UI changes.

## Checklist

- [ ] My code follows style guide
- [ ] Tests pass locally
- [ ] No new warnings generated
- [ ] Documentation is updated
```

### Review Process

1. **Automated Checks**
   - CI/CD pipeline must pass
   - Test coverage maintained
   - Code style checks pass

2. **Code Review**
   - At least one approval required
   - Maintainers may request changes
   - Be respectful and constructive

3. **Merge**
   - Squash commits if needed
   - Delete branch after merge
   - Monitor for any issues

## Adding New Platforms

To add support for a new platform (e.g., LinkedIn):

### 1. Create Platform Documentation

Create `platforms/linkedin/` with:
```
linkedin/
├── README.md                    # Platform overview
├── api-guide.md                 # API interaction guide
├── authentication.md            # Auth setup
├── rate-limits.md              # Rate limit details
├── post-tracking.md            # Post tracking
├── comment-moderation.md       # Moderation guidelines
├── data-models.md              # Data structures
└── examples/
    ├── fetch-comments.md
    ├── moderate-comment.md
    └── track-post.md
```

### 2. Implement Platform Class

Create `src/platforms/linkedin.py`:

```python
from moderation_ai.platforms.base import BasePlatform
from moderation_ai.models import Comment, Post

class LinkedInAPI(BasePlatform):
    """LinkedIn API integration"""

    async def authenticate(self) -> bool:
        # Implement LinkedIn OAuth
        pass

    async def fetch_posts(self, query: str) -> List[Post]:
        # Implement LinkedIn API call
        pass

    async def fetch_comments(self, post_id: str) -> List[Comment]:
        # Implement comment fetching
        pass

    # Implement other required methods...
```

### 3. Add Tests

Create `tests/platforms/test_linkedin.py` with comprehensive tests.

### 4. Update Documentation

Add LinkedIn reference to:
- `docs/api-reference/common-patterns.md`
- `platforms/README.md`
- Main `README.md`

### 5. Create PR

Submit PR with platform documentation and implementation.

## Adding Analysis Modules

To add a new analysis capability (e.g., Language Detection):

### 1. Create Analysis Module

Create `src/analysis/language_detector.py`:

```python
from moderation_ai.core.analyzer import BaseAnalyzer
from moderation_ai.models import Comment, AnalysisResult

class LanguageDetector(BaseAnalyzer):
    """Detect language of comments"""

    def analyze(self, comment: Comment) -> AnalysisResult:
        # Implement language detection
        pass

    def batch_analyze(self, comments: List[Comment]) -> List[AnalysisResult]:
        # Implement batch detection
        pass
```

### 2. Add Tests

Create `tests/analysis/test_language_detector.py` with tests.

### 3. Document

Create `docs/comment-analysis/language-detection.md` with:
- Purpose and use cases
- Supported languages
- Output format
- Examples

### 4. Create PR

Submit PR with implementation and documentation.

## Reporting Issues

### Bug Reports

Include:
- Clear title describing the bug
- Reproduction steps
- Expected vs. actual behavior
- Environment (Python version, OS, etc.)
- Error messages and stack traces
- Code examples if applicable

### Feature Requests

Include:
- Clear title describing the feature
- Detailed description of use case
- How it fits with project goals
- Potential implementation approach
- Examples of desired behavior

### Use GitHub Issues Template

Click "New Issue" and select the appropriate template.

## Getting Help

- **Questions**: Use GitHub Discussions
- **Bugs**: Use GitHub Issues with "bug" label
- **Ideas**: Use GitHub Issues with "enhancement" label
- **Documentation**: Submit a PR with changes

## Recognition

Contributors will be recognized:
- In commit history
- In CONTRIBUTORS.md file
- In release notes
- In project documentation

## License

By contributing to this project, you agree that your contributions will be licensed under the MIT License.

---

**Last Updated**: January 2024
**Maintained By**: Colin Goss
