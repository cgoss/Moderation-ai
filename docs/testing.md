# Testing Documentation

## Overview

This document describes the testing framework and guidelines for the Moderation Bot project.

## Test Structure

```
tests/
├── conftest.py                    # Pytest configuration and shared fixtures
├── fixtures/                      # Reusable test fixtures
│   ├── __init__.py
│   ├── api_mocks.py              # Mock API clients
│   ├── auth_fixtures.py          # Authentication fixtures
│   ├── data_fixtures.py          # Sample test data
│   └── platform_fixtures.py     # Platform-specific fixtures
├── unit/                         # Unit tests
│   └── platforms/               # Platform adapter unit tests
│       ├── test_instagram.py
│       ├── test_medium.py
│       └── test_tiktok.py
└── integration/                   # Integration tests
    ├── test_api_clients.py
    ├── test_auth_flows.py
    ├── test_error_handling.py
    ├── test_platform_integration.py
    ├── test_rate_limiting.py
    └── test_webhooks.py
```

## Running Tests

### Run All Tests

```bash
pytest
```

### Run Specific Test File

```bash
pytest tests/unit/platforms/test_instagram.py
```

### Run Specific Test Class

```bash
pytest tests/unit/platforms/test_instagram.py::TestInstagramAPIClient
```

### Run Specific Test Method

```bash
pytest tests/unit/platforms/test_instagram.py::TestInstagramAPIClient::test_client_initialization
```

### Run with Markers

```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Run only network tests
pytest -m network

# Run only fast tests (skip slow tests)
pytest -m "not slow"
```

### Run with Coverage

```bash
# Terminal output
pytest --cov=src --cov-report=term-missing

# HTML report
pytest --cov=src --cov-report=html

# Both
pytest --cov=src --cov-report=term-missing --cov-report=html
```

### Run with Verbose Output

```bash
pytest -v
```

### Run with Parallel Execution

```bash
# Install pytest-xdist first: pip install pytest-xdist
pytest -n auto
```

## Test Fixtures

### API Mocks

**MockInstagramAPI**
```python
from tests.fixtures import MockInstagramAPI

api = MockInstagramAPI()
media = api.get_media("test_media_id")
assert media["id"] == "test_media_id"
```

**MockMediumAPI**
```python
from tests.fixtures import MockMediumAPI

api = MockMediumAPI()
articles = api.get_user_articles("test_user_id")
assert len(articles) == 3
```

**MockTikTokAPI**
```python
from tests.fixtures import MockTikTokAPI

api = MockTikTokAPI()
videos = api.get_user_videos()
assert len(videos) == 3
```

### Sample Data

**Sample Comment**
```python
from tests.fixtures import sample_comment

comment = sample_comment()
assert "id" in comment
assert "text" in comment
```

**Sample Post**
```python
from tests.fixtures import sample_post

post = sample_post()
assert "id" in post
assert "title" in post
```

**Sample Video**
```python
from tests.fixtures import sample_video

video = sample_video()
assert "id" in video
assert "title" in video
```

### List Generators

**Generate Sample Comments**
```python
from tests.fixtures import sample_comments_list

comments = sample_comments_list(count=10)
assert len(comments) == 10
```

**Generate Sample Posts**
```python
from tests.fixtures import sample_posts_list

posts = sample_posts_list(count=5)
assert len(posts) == 5
```

## Test Markers

The project uses the following pytest markers:

- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.network` - Tests that require network access
- `@pytest.mark.slow` - Slow tests (take >1 second)
- `@pytest.mark.auth` - Authentication tests
- `@pytest.mark.moderation` - Moderation tests

### Using Markers

```python
import pytest

@pytest.mark.unit
def test_unit_feature():
    pass

@pytest.mark.integration
@pytest.mark.network
def test_integration_feature():
    pass

@pytest.mark.slow
def test_slow_feature():
    pass
```

## Writing Tests

### Unit Test Template

```python
import pytest
from unittest.mock import Mock, patch
from tests.fixtures import sample_comment

class TestFeature:
    """Tests for [Feature]"""
    
    def test_basic_functionality(self, sample_comment):
        """Test basic functionality"""
        # Arrange
        input_data = sample_comment()
        
        # Act
        result = process_comment(input_data)
        
        # Assert
        assert result is not None
        assert "id" in result
    
    def test_error_handling(self):
        """Test error handling"""
        # Arrange
        invalid_input = None
        
        # Act & Assert
        with pytest.raises(ValueError):
            process_comment(invalid_input)
    
    @pytest.mark.parametrize("input,expected", [
        ("test1", "expected1"),
        ("test2", "expected2"),
        ("test3", "expected3"),
    ])
    def test_multiple_scenarios(self, input, expected):
        """Test multiple scenarios"""
        result = process_input(input)
        assert result == expected
```

### Integration Test Template

```python
import pytest
from tests.fixtures import MockInstagramAPI

@pytest.mark.integration
@pytest.mark.network
class TestIntegrationFeature:
    """Integration tests for [Feature]"""
    
    def test_end_to_end_workflow(self, instagram_client):
        """Test end-to-end workflow"""
        # Step 1: Get media
        media = instagram_client.get_media("test_id")
        assert media["id"] == "test_id"
        
        # Step 2: Get comments
        comments = instagram_client.get_media_comments("test_id")
        assert len(comments) > 0
        
        # Step 3: Process comments
        for comment in comments:
            result = process_comment(comment)
            assert result is not None
```

## Test Coverage Goals

### Target Coverage
- **Unit tests**: 90%+ coverage per module
- **Integration tests**: 80%+ coverage for critical paths
- **Overall**: 85%+ coverage

### Checking Coverage

```bash
# Terminal summary
pytest --cov=src --cov-report=term-missing

# HTML report (detailed)
pytest --cov=src --cov-report=html
open htmlcov/index.html
```

## Best Practices

### 1. Use Descriptive Test Names

```python
# Bad
def test_1():
    pass

# Good
def test_get_media_returns_valid_response():
    pass
```

### 2. Use Fixtures for Reusable Data

```python
# Bad
def test_comment_processing():
    comment = {
        "id": "123",
        "text": "test",
        # ... many more fields
    }
    result = process(comment)
    assert result is not None

# Good
def test_comment_processing(sample_comment):
    comment = sample_comment()
    result = process(comment)
    assert result is not None
```

### 3. Use Arrange-Act-Assert Pattern

```python
def test_moderation_flow(sample_comment):
    # Arrange
    comment = sample_comment()
    comment["text"] = "spam comment"
    
    # Act
    action = moderate_comment(comment)
    
    # Assert
    assert action == "delete"
```

### 4. Test Edge Cases

```python
def test_empty_comment(sample_comment):
    comment = sample_comment()
    comment["text"] = ""
    
    with pytest.raises(ValueError):
        process_comment(comment)

def test_very_long_comment(sample_comment):
    comment = sample_comment()
    comment["text"] = "a" * 10000
    
    result = process_comment(comment)
    assert result is not None
```

### 5. Use Parameterized Tests

```python
@pytest.mark.parametrize("text,expected_action", [
    ("normal comment", "allow"),
    ("spam comment", "delete"),
    ("profanity comment", "hide"),
])
def test_moderation_rules(text, expected_action):
    comment = {"text": text}
    action = moderate_comment(comment)
    assert action == expected_action
```

### 6. Mock External Dependencies

```python
from unittest.mock import patch

def test_api_call():
    with patch('requests.get') as mock_get:
        mock_get.return_value.json.return_value = {"id": "test"}
        
        result = fetch_data("test_id")
        
        assert result["id"] == "test"
        mock_get.assert_called_once()
```

### 7. Clean Up in Tests

```python
def test_file_operation():
    # Setup
    test_file = "test.txt"
    with open(test_file, 'w') as f:
        f.write("test")
    
    try:
        # Test
        result = process_file(test_file)
        assert result is not None
    finally:
        # Cleanup
        if os.path.exists(test_file):
            os.remove(test_file)
```

## Continuous Integration

### GitHub Actions Workflow

The project uses GitHub Actions for CI/CD. Tests run automatically on:
- Push to main branch
- Pull requests
- Manual trigger

### Local Testing Before Push

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run linting
flake8 src tests
black --check src tests
isort --check-only src tests
mypy src
```

## Troubleshooting

### Tests Fail Due to Missing Fixtures

```bash
# Ensure all fixtures are properly imported
python -m pytest --collect-only
```

### Tests Timeout

```bash
# Increase timeout for slow tests
pytest --timeout=300
```

### Import Errors

```bash
# Ensure src directory is in Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
pytest
```

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Pytest-Mock Documentation](https://pytest-mock.readthedocs.io/)
- [Pytest-Cov Documentation](https://pytest-cov.readthedocs.io/)
- [Testing Best Practices](https://docs.python-guide.org/writing/tests/)

## Next Steps

1. Add more integration tests for cross-platform workflows
2. Add performance tests for high-load scenarios
3. Add stress tests for rate limiting
4. Add end-to-end tests with real APIs (optional)
5. Improve test coverage for edge cases
