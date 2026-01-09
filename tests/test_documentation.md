# Testing Documentation

## Overview

This guide provides comprehensive documentation for the test suite created for the Moderation Bot platform adapters.

## Test Structure

```
tests/
├── conftest.py                 # Pytest configuration and fixtures
├── fixtures/                   # Test fixtures and mocks
│   ├── __init__.py
│   ├── api_mocks.py          # Platform API mock objects
│   ├── auth_fixtures.py       # Authentication fixtures
│   ├── data_fixtures.py       # Sample test data
│   └── platform_fixtures.py    # Platform-specific fixtures
├── unit/                      # Unit tests
│   ├── __init__.py
│   ├── platforms/              # Platform adapter tests
│   │   ├── __init__.py
│   │   ├── test_instagram.py
│   │   ├── test_medium.py
│   │   └── test_tiktok.py
├── integration/                 # Integration tests
│   ├── __init__.py
│   ├── test_platform_integration.py
│   ├── test_auth_flows.py
│   ├── test_rate_limiting.py
│   └── test_webhooks.py
├── api_client_tests.py           # API client tests
├── auth_flows_tests.py          # Authentication flow tests
├── error_handling_tests.py         # Error handling tests
├── test_auth_flow.py           # Authentication flow tests
└── test_documentation.md    # This file
```

## Running Tests

### Run All Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/unit/platforms/test_instagram.py

# Run with verbose output
pytest -v

# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Skip slow tests
pytest -m "not slow"
```

## Test Organization

### Platform Tests

#### Instagram (`tests/unit/platforms/test_instagram.py`)
- **TestInstagramAPIClient**: Instagram API client tests
- **TestInstagramPostTracker**: Post tracking tests
- **TestInstagramCommentModerator**: Comment moderation tests
- **TestInstagramRateLimiter**: Rate limiting tests
- **TestInstagramWebhookHandler**: Webhook tests
- **TestInstagramErrorHandling**: Error handling tests
- **TestInstagramIntegration**: Integration tests

#### Medium (`tests/unit/platforms/test_medium.py`)
- **TestMediumAPIClient**: Medium API client tests
- **TestMediumPostTracker**: Post tracking tests
- **TestMediumCommentModerator**: Comment moderation tests
- **TestMediumRateLimiter**: Rate limiting tests
- **TestMediumWebhookHandler**: Webhook tests
- **TestMediumErrorHandling**: Error handling tests

#### TikTok (`tests/unit/platforms/test_tiktok.py`)
- **TestTikTokAPIClient**: TikTok API client tests
- **TestTikTokVideoTracker**: Video tracking tests
- **TestTikTokCommentModerator**: Comment moderation tests
- **TestTikTokRateLimiter**: Rate limiting tests
- **TestTikTokWebhookHandler**: Webhook tests
- **TestTikTokErrorHandling**: Error handling tests

### Integration Tests

#### Platform Integration (`tests/integration/test_platform_integration.py`)
- Cross-platform integration tests
- API client lifecycle tests
- Comment tracking workflow tests
- Authentication flow tests
- Rate limiting enforcement tests
- Webhook event handling tests
- Error recovery mechanisms
- Batch processing performance
- Data consistency checks

#### Authentication Tests (`tests/integration/test_auth_flows.py`)
- OAuth 2.0 flow tests
- Token refresh mechanism tests
- Multi-platform authentication
- State validation
- Token expiration handling
- Concurrent request handling

#### Rate Limiting Tests (`tests/integration/test_rate_limiting.py`)
- API rate limiting enforcement
- Rate limit recovery
- Cross-platform consistency
- Backoff algorithm tests
- Sliding window algorithm
- Performance benchmarks

#### Webhook Tests (`tests/integration/test_webhooks.py`)
- Webhook signature verification
- Event type handling
- Security validation
- Delivery reliability
- Concurrent webhook handling

#### API Client Tests (`tests/integration/test_api_clients.py`)
- Connection timeout handling
- Request retry logic
- Response parsing
- JSON handling
- Error recovery
- Response caching

#### Error Handling Tests (`tests/integration/test_error_handling.py`)
- Network error recovery
- Rate limit handling
- Authentication errors
- Invalid grant errors
- Resource not found
- Forbidden errors

#### Authentication Tests (`tests/integration/test_auth_flow.py`)
- Complete OAuth flow tests
- Token exchange
- Token refresh
- Multiple user authentication
- Concurrent auth requests
- Token state validation

#### Data Validation Tests (`tests/integration/test_data_validation.py`)
- Data model validation
- Schema validation
- Type checking
- Required field validation
- Cross-platform consistency

## Test Markers

```python
import pytest

# Platform markers
@pytest.mark.instagram
def test_instagram_feature():
    """Instagram-specific test"""
    pass

@pytest.mark.medium
def test_medium_feature():
    """Medium-specific test"""
    pass

@pytest.mark.tiktok
def test_tiktok_feature():
    """TikTok-specific test"""
    pass

# Test type markers
@pytest.mark.unit
def test_unit_test():
    """Unit test"""
    pass

@pytest.mark.integration
def test_integration_test():
    """Integration test"""
    pass

@pytest.mark.e2e
def test_end_to_end():
    """End-to-end test"""
    pass

# Behavior markers
@pytest.mark.slow
def test_slow_operation():
    """Slow running test"""
    pass

@pytest.mark.network
def test_network_operation():
    """Test requiring network access"""
    pass

@pytest.mark.auth
def test_auth_flow():
    """Test requiring authentication"""
    pass

# Conditional markers
@pytest.mark.skip_ci
@skip_ci("Skipped in CI environment")
def test_ci_skipped():
    """Test skipped in CI"""
    pass
```

## Test Fixtures

### API Mocks
- `MockInstagramAPI`: Instagram API mock with call tracking
- `MockMediumAPI`: Medium API mock with call tracking
- `MockTikTokAPI`: TikTok API mock with call tracking
- `mock_response_factory`: Generic response factory

### Authentication Fixtures
- `valid_auth_token`: Valid auth token
- `expired_auth_token`: Expired auth token
- `auth_headers`: Auth headers
- `oauth_credentials`: OAuth credentials
- `mock_oauth_flow`: Mock OAuth flow generator
- `mock_token_manager`: Mock token manager

### Data Fixtures
- `sample_comment`: Sample comment data
- `sample_post`: Sample post data
- `sample_video`: Sample video data
- `sample_article`: Sample article data (Medium)
- `sample_media`: Sample media (Instagram)
- `sample_user`: Sample user data
- `sample_comments_list`: Generate comment lists
- `sample_posts_list`: Generate post lists
- `sample_videos_list`: Generate video lists
- `sample_articles_list`: Generate article lists (Medium)
- `sample_media_list`: Generate media lists (Instagram)

### Platform Fixtures
- `instagram_config`: Instagram configuration
- `medium_config`: Medium configuration
- `tiktok_config`: TikTok configuration
- `instagram_client`: Instagram client fixture
- `medium_client`: Medium client fixture
- `tiktok_client`: TikTok client fixture

### Rate Limiting Fixtures
- `mock_rate_limiter`: Mock rate limiter
- `sample_rate_limit_info`: Sample rate limit info
- `mock_pagination_result`: Sample pagination info

### Webhook Fixtures
- `mock_webhook_event`: Mock webhook event
- `webhook_signature`: Webhook signature
- `create_webhook_event`: Create webhook event

## Test Configuration

### Environment Variables

```bash
# Test environment
TEST_ENV=local
ALLOW_NETWORK_TESTS=false
LOG_LEVEL=DEBUG
TEST_TIMEOUT=30
MAX_RETRIES=3

# Platform-specific test configurations
INSTAGRAM_CLIENT_ID=test_instagram_client_id
INSTAGRAM_CLIENT_SECRET=test_instagram_client_secret
MEDIUM_CLIENT_ID=test_medium_client_id
MEDIUM_CLIENT_SECRET=test_medium_client_secret
TIKTOK_CLIENT_KEY=test_tiktok_client_key
TIKTOK_CLIENT_SECRET=test_tiktok_client_secret
```

## Coverage Goals

- Unit test coverage: > 80%
- Integration test coverage: > 70%
- Authentication flow coverage: > 90%
- Rate limiting coverage: > 85%
- Error handling coverage: > 85%
- Webhook coverage: > 80%

## Continuous Integration

Tests are designed for continuous integration (CI/CD):

```yaml
# .github/workflows/test.yml
name: Test Suite

on:
  push:
    branches: [main, develop]
  paths-ignore: ['**/node_modules/**', '**/__pycache__/**']
  
jobs:
  test:
    runs-on: ubuntu-latest
    strategy: matrix
    env:
      - {
          POSTGRES_DB: ${{ secrets.DATABASE_URL }}
          REDIS_URL: ${{ secrets.REDIS_URL }}
        }
      - INSTAGRAM_ACCESS_TOKEN: ${{ secrets.INSTAGRAM_ACCESS_TOKEN }}
        - MEDIUM_ACCESS_TOKEN: ${{ secrets.MEDIUM_ACCESS_TOKEN }}
        - TIKTOK_ACCESS_TOKEN: ${{ secrets.TIKTOK_ACCESS_TOKEN }}
      - ALLOW_NETWORK_TESTS: "false"
        LOG_LEVEL: "DEBUG"
    timeout-minutes: 30
      max_retries: 3
    steps:
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run unit tests
        run: pytest --cov=src --cov-report=xml --cov-report=html
      - name: Run integration tests
        run: pytest -m integration
      - name: Generate coverage report
        run: coverage report
      - name: Upload coverage
        run: coveralls
      - name: Upload to Codecov
        run: curl -X POST ${{ secrets.COVERALLS_TOKEN }} ${{ secrets.COVERALLS_TOKEN }} -F ${{ github.ref }}
    env:
      - COVERALLS_REPO_TOKEN: ${{ secrets.COVERALLS_REPO_TOKEN }}
      COVERALLS_COMMIT_SHA: ${{ github.sha }}"
```

## Best Practices

### Writing Tests

1. **Test isolated functionality**
   - Each test should be independent
   - Use fixtures to set up test state
   - Clean up after each test

2. **Use descriptive test names**
   - Test names should clearly indicate what is being tested
   - Use `test_` prefix for unit tests

3. **Follow AAA pattern**
   - Arrange: Set up test fixtures
   - Act: Execute the test
   - Assert: Verify the result
   - Cleanup: Clean up resources

4. **Mock appropriately**
   - Mock external dependencies
   - Only mock what's needed for the test
   - Use realistic mock data

5. **Test edge cases**
   - Include edge cases (empty lists, null values, etc.)
   - Test error scenarios

6. **Use parameterized tests**
   - Test with different inputs
   - Use `@pytest.mark.parametrize` for multiple test cases

7. **Test asynchronous operations**
   - Use `@pytest.mark.asyncio` for async tests
   - Test async/await patterns

## CI/CD Considerations

### GitHub Actions

```yaml
name: Test CI

on:
  pull_request:
    branches: [main, develop]
    paths:
      - 'tests/**/*.py'

  pull_request:
    branches: [main, develop]

  push:
    branches: [main, develop]
    paths:
      - 'tests/**/*.py'

  workflow: pytest
    name: Run Tests
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        run: pip install -r requirements.txt
      - name: Run tests
        run: pytest --cov=src --cov-report=xml
      - name: Upload coverage
        run: coveralls

  workflow: Codecov
    runs-on: ubuntu-latest
    needs: python
    needs: pytest

  workflow: Test Coverage Report
    if: success()
      - uses: codecov/codecov@v1
      with:
        token: ${{ secrets.CODECOV_TOKEN }}
        repo: ${{ github.repository }}
        env:
          CODECOV_REPO_TOKEN: ${{ secrets.CODECOV_REPO_TOKEN }}
```

## Running Locally

```bash
# Install test dependencies
pip install -r requirements.txt

# Run tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html --cov-report=xml

# Open coverage report
open htmlcov/index.html

# Run specific test
pytest tests/unit/platforms/test_instagram.py

# Run only unit tests
pytest -m unit

# Run only Instagram tests
pytest -m instagram

# Run only integration tests
pytest -m integration
```

## Troubleshooting

### Tests Not Found

If tests are not found:

```bash
# List all test files
find tests -name "*.py" -o -name "test_*.py"

# Check if tests directory structure is correct
tree tests -L 3

# Run pytest in verbose mode to see what's being discovered
pytest -v --collect-only
```

### Tests Not Running

If tests are not running:

```bash
# Check if pytest is installed
pytest --version

# Verify configuration
cat pytest.ini

# Check test discovery
pytest --collect-only

# Run a simple test
pytest tests/fixtures/__init__.py -v --collect-only
```

### Coverage Issues

If coverage is not being generated:

```bash
# Check coverage configuration
cat .coveragerc or .coveragerc

# Check coverage file exists
ls htmlcov/index.html

# Manually trigger coverage
pytest --cov=src --cov-report=xml
```

## Next Steps

1. Create additional integration tests
2. Add performance benchmarks
3. Set up CI/CD pipeline
4. Add performance monitoring
5. Create test reports
6. Document test architecture
