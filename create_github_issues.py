#!/usr/bin/env python3
"""
Script to create all 60 GitHub issues for Moderation AI project
Requires: gh CLI installed and authenticated
"""

import subprocess
import sys
from typing import List, Dict

# Color codes for output
GREEN = '\033[0;32m'
BLUE = '\033[0;34m'
YELLOW = '\033[1;33m'
RED = '\033[0;31m'
NC = '\033[0m'  # No Color

def create_issue(title: str, body: str, labels: str) -> bool:
    """Create a single GitHub issue"""
    try:
        cmd = [
            'gh', 'issue', 'create',
            '--title', title,
            '--body', body,
            '--label', labels
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=".")
        if result.returncode == 0:
            print(f"{GREEN}[OK]{NC} {title}")
            return True
        else:
            print(f"{RED}[FAIL]{NC} {title}")
            print(f"  Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"{RED}[FAIL]{NC} {title} - Exception: {e}")
        return False

def main():
    """Create all 60 GitHub issues"""
    issues = [
        # Phase 0: Foundation (5 issues)
        {
            "title": "[SETUP] Initialize Project Structure",
            "body": """Create all necessary directories and files for the project structure.

## Acceptance Criteria
- [x] Directory structure created
- [x] .gitignore configured
- [x] requirements.txt created
- [x] pyproject.toml configured
- [x] Initial git commit

## Related Files
- .gitignore
- requirements.txt
- pyproject.toml
- LICENSE""",
            "labels": "setup,phase-0"
        },
        {
            "title": "[DOCS] Create Core Documentation",
            "body": """Create the foundational documentation files for the project.

## Files to Create
- [x] README.md
- [x] ARCHITECTURE.md
- [x] CONTRIBUTING.md
- [x] LICENSE

## Acceptance Criteria
- [x] All files complete
- [x] Clear and comprehensive
- [x] Following markdown standards
- [x] Reviewed and approved""",
            "labels": "documentation,phase-0"
        },
        {
            "title": "[DOCS] Define LLM Context Consumption Guide",
            "body": """Create documentation explaining how LLMs should consume this library.

## File
- docs/llm-context-guide.md

## Sections
- [ ] Purpose and overview
- [ ] Document hierarchy
- [ ] Usage patterns
- [ ] Navigation strategies
- [ ] Context optimization tips
- [ ] Common mistakes to avoid

## Related Documentation
- standards-and-metrics.md
- api-reference/README.md
- comment-analysis/README.md""",
            "labels": "documentation,phase-0"
        },
        {
            "title": "[DOCS] Define Standards and Metrics Framework",
            "body": """Create comprehensive moderation standards and metrics definitions.

## File
- docs/standards-and-metrics.md

## Standards to Define
- [ ] Safety (threats, harassment, hate speech)
- [ ] Quality (on-topic, constructive)
- [ ] Spam (promotional, repetitive)
- [ ] Policy (platform-specific)
- [ ] Engagement (respectful communication)

## Acceptance Criteria
- [ ] All 5 standards defined
- [ ] Metrics testable and measurable
- [ ] Examples provided
- [ ] Moderation actions specified""",
            "labels": "documentation,phase-0"
        },
        {
            "title": "[SETUP] Create GitHub Issues and Project Board",
            "body": """Create all GitHub issues and set up project tracking.

## Tasks
- [x] Create all 60 issues
- [ ] Apply appropriate labels
- [ ] Create GitHub project
- [ ] Add issues to project
- [ ] Set up milestones

## Related Documentation
- docs/implementation-phases.md""",
            "labels": "setup,phase-0"
        },

        # Phase 1: API Reference (6 issues)
        {
            "title": "[DOCS] Create Unified API Reference Index",
            "body": """Create the main API reference documentation.

## File
- docs/api-reference/README.md

## Content
- [ ] Overview of all platform APIs
- [ ] Common patterns across platforms
- [ ] Links to detailed guides
- [ ] Authentication overview
- [ ] Rate limiting overview

## Related Files
- authentication.md
- rate-limiting.md
- common-patterns.md""",
            "labels": "documentation,phase-1"
        },
        {
            "title": "[DOCS] Document Authentication Patterns",
            "body": """Document authentication patterns across all platforms.

## File
- docs/api-reference/authentication.md

## Coverage
- [ ] OAuth patterns
- [ ] API key authentication
- [ ] Token management
- [ ] Credential storage
- [ ] Security best practices
- [ ] Platform-specific auth variations""",
            "labels": "documentation,phase-1"
        },
        {
            "title": "[DOCS] Document Rate Limiting Strategies",
            "body": """Document rate limiting approaches for all platforms.

## File
- docs/api-reference/rate-limiting.md

## Content
- [ ] Rate limit headers
- [ ] Backoff strategies
- [ ] Batch processing
- [ ] Queue management
- [ ] Multi-account strategies
- [ ] Platform-specific limits""",
            "labels": "documentation,phase-1"
        },
        {
            "title": "[DOCS] Document Error Handling Guidelines",
            "body": """Create error handling patterns and guidelines.

## File
- docs/api-reference/error-handling.md

## Content
- [ ] Common error types
- [ ] HTTP status codes
- [ ] Retry logic
- [ ] Logging patterns
- [ ] User-friendly messages
- [ ] Exception hierarchy""",
            "labels": "documentation,phase-1"
        },
        {
            "title": "[DOCS] Document Webhook Patterns",
            "body": """Document webhook implementation patterns.

## File
- docs/api-reference/webhooks.md

## Content
- [ ] Webhook payload structure
- [ ] Event types
- [ ] Delivery guarantees
- [ ] Signature verification
- [ ] Retry behavior
- [ ] Platform-specific webhooks""",
            "labels": "documentation,phase-1"
        },
        {
            "title": "[DOCS] Document Common API Patterns",
            "body": """Document patterns shared across platform APIs.

## File
- docs/api-reference/common-patterns.md

## Content
- [ ] Pagination patterns
- [ ] Query parameters
- [ ] Response formats
- [ ] Status codes
- [ ] Error responses
- [ ] Timestamp formats""",
            "labels": "documentation,phase-1"
        },

        # Phase 1: Comment Analysis (8 issues)
        {
            "title": "[DOCS] Create Comment Analysis Framework Overview",
            "body": """Create overview of comment analysis methodologies.

## File
- docs/comment-analysis/README.md

## Content
- [ ] Analysis framework overview
- [ ] Available techniques
- [ ] Use cases
- [ ] Integration with moderation
- [ ] Links to detailed docs
- [ ] Example workflows""",
            "labels": "documentation,phase-1"
        },
        {
            "title": "[DOCS] Document Summarization Techniques",
            "body": """Document comment summarization methodology.

## File
- docs/comment-analysis/summarization.md

## Content
- [ ] Summarization approach
- [ ] Algorithm selection
- [ ] Key point extraction
- [ ] Handling long threads
- [ ] Quality metrics
- [ ] Examples""",
            "labels": "documentation,phase-1"
        },
        {
            "title": "[DOCS] Define Categorization Taxonomy",
            "body": """Define comment categorization system.

## File
- docs/comment-analysis/categorization.md

## Content
- [ ] Category taxonomy
- [ ] Assignment rules
- [ ] Edge cases
- [ ] Example classifications
- [ ] Use in moderation
- [ ] Custom categories""",
            "labels": "documentation,phase-1"
        },
        {
            "title": "[DOCS] Document Sentiment Analysis Methodology",
            "body": """Document sentiment/tone detection approach.

## File
- docs/comment-analysis/sentiment-analysis.md

## Content
- [ ] Sentiment categories
- [ ] Detection methodology
- [ ] Confidence scoring
- [ ] Context awareness
- [ ] Examples with scores
- [ ] Platform variations""",
            "labels": "documentation,phase-1"
        },
        {
            "title": "[DOCS] Document FAQ Extraction Process",
            "body": """Document FAQ identification from comments.

## File
- docs/comment-analysis/faq-extraction.md

## Content
- [ ] FAQ identification criteria
- [ ] Question pattern detection
- [ ] Frequency analysis
- [ ] Topic clustering
- [ ] Output format
- [ ] Examples""",
            "labels": "documentation,phase-1"
        },
        {
            "title": "[DOCS] Document Content Ideation Process",
            "body": """Document content suggestion from comments.

## File
- docs/comment-analysis/content-ideation.md

## Content
- [ ] Need identification
- [ ] Gap analysis
- [ ] Topic trending
- [ ] Suggestion generation
- [ ] Validation criteria
- [ ] Examples""",
            "labels": "documentation,phase-1"
        },
        {
            "title": "[DOCS] Define Community Metrics",
            "body": """Document community-level analytics.

## File
- docs/comment-analysis/community-metrics.md

## Content
- [ ] Engagement metrics
- [ ] Sentiment trends
- [ ] Comment volume patterns
- [ ] Audience growth
- [ ] Topic trends
- [ ] Visualization approaches""",
            "labels": "documentation,phase-1"
        },
        {
            "title": "[DOCS] Document Abuse Detection Methodology",
            "body": """Document abuse and bullying identification.

## File
- docs/comment-analysis/abuse-detection.md

## Content
- [ ] Abuse types
- [ ] Detection signals
- [ ] Confidence scoring
- [ ] Context consideration
- [ ] Severity classification
- [ ] Examples and non-examples""",
            "labels": "documentation,phase-1"
        },

        # Platform Documentation (6 issues)
        {
            "title": "[PLATFORM-DOCS] Document Twitter/X Platform",
            "body": """Create comprehensive documentation for Twitter/X integration.

## Files to Create (10 files)
- [ ] platforms/twitter/README.md
- [ ] platforms/twitter/api-guide.md
- [ ] platforms/twitter/authentication.md
- [ ] platforms/twitter/rate-limits.md
- [ ] platforms/twitter/post-tracking.md
- [ ] platforms/twitter/comment-moderation.md
- [ ] platforms/twitter/data-models.md
- [ ] platforms/twitter/examples/fetch-comments.md
- [ ] platforms/twitter/examples/moderate-comment.md
- [ ] platforms/twitter/examples/track-post.md

## Phase
- Phase 2: Tier 1 Platform Docs

## Related Implementation Issues
- [PLATFORM] Implement Twitter API Integration
- [PLATFORM] Create Twitter Integration Tests""",
            "labels": "documentation,platform,twitter,phase-2"
        },
        {
            "title": "[PLATFORM-DOCS] Document Reddit Platform",
            "body": """Create comprehensive documentation for Reddit integration.

## Files to Create
- platforms/reddit/README.md
- platforms/reddit/api-guide.md
- platforms/reddit/authentication.md
- platforms/reddit/rate-limits.md
- platforms/reddit/post-tracking.md
- platforms/reddit/comment-moderation.md
- platforms/reddit/data-models.md
- platforms/reddit/examples/ (3 examples)

## Phase
- Phase 2: Tier 1 Platform Docs""",
            "labels": "documentation,platform,reddit,phase-2"
        },
        {
            "title": "[PLATFORM-DOCS] Document YouTube Platform",
            "body": """Create comprehensive documentation for YouTube integration.

## Files to Create
- platforms/youtube/README.md
- platforms/youtube/api-guide.md
- platforms/youtube/authentication.md
- platforms/youtube/rate-limits.md
- platforms/youtube/post-tracking.md
- platforms/youtube/comment-moderation.md
- platforms/youtube/data-models.md
- platforms/youtube/examples/ (3 examples)

## Phase
- Phase 2: Tier 1 Platform Docs""",
            "labels": "documentation,platform,youtube,phase-2"
        },
        {
            "title": "[PLATFORM-DOCS] Document Instagram Platform",
            "body": """Create comprehensive documentation for Instagram integration.

## Files to Create
- platforms/instagram/README.md
- platforms/instagram/api-guide.md
- platforms/instagram/authentication.md
- platforms/instagram/rate-limits.md
- platforms/instagram/post-tracking.md
- platforms/instagram/comment-moderation.md
- platforms/instagram/data-models.md
- platforms/instagram/examples/ (3 examples)

## Phase
- Phase 4: Tier 2 Platform Docs""",
            "labels": "documentation,platform,instagram,phase-4"
        },
        {
            "title": "[PLATFORM-DOCS] Document Medium Platform",
            "body": """Create comprehensive documentation for Medium integration.

## Files to Create
- platforms/medium/README.md
- platforms/medium/api-guide.md
- platforms/medium/authentication.md
- platforms/medium/rate-limits.md
- platforms/medium/post-tracking.md
- platforms/medium/comment-moderation.md
- platforms/medium/data-models.md
- platforms/medium/examples/ (3 examples)

## Phase
- Phase 4: Tier 2 Platform Docs""",
            "labels": "documentation,platform,medium,phase-4"
        },
        {
            "title": "[PLATFORM-DOCS] Document TikTok Platform",
            "body": """Create comprehensive documentation for TikTok integration.

## Files to Create
- platforms/tiktok/README.md
- platforms/tiktok/api-guide.md
- platforms/tiktok/authentication.md
- platforms/tiktok/rate-limits.md
- platforms/tiktok/post-tracking.md
- platforms/tiktok/comment-moderation.md
- platforms/tiktok/data-models.md
- platforms/tiktok/examples/ (3 examples)

## Phase
- Phase 4: Tier 2 Platform Docs""",
            "labels": "documentation,platform,tiktok,phase-4"
        },

        # Core Implementation (5 issues)
        {
            "title": "[CORE] Implement Standards Engine",
            "body": """Implement core/standards.py with StandardsEngine class.

## Specification
- docs/standards-and-metrics.md

## Requirements
- [ ] Load moderation standards
- [ ] Validate comments against standards
- [ ] Calculate violation scores
- [ ] Return detailed reasoning
- [ ] Support custom standards
- [ ] Type hints on all methods
- [ ] Comprehensive docstrings
- [ ] Unit tests (80%+ coverage)

## Related
- Metrics Validator
- Base Analyzer""",
            "labels": "implementation,core,phase-3"
        },
        {
            "title": "[CORE] Implement Metrics Calculator",
            "body": """Implement core/metrics.py with MetricsValidator class.

## Requirements
- [ ] Calculate metrics for comments
- [ ] Track community-level metrics
- [ ] Validate against thresholds
- [ ] Generate analytics
- [ ] Handle edge cases
- [ ] Type hints
- [ ] Docstrings
- [ ] Unit tests (80%+ coverage)

## Related
- Standards Engine
- Comment Analysis modules""",
            "labels": "implementation,core,phase-3"
        },
        {
            "title": "[CORE] Implement Base Analyzer Framework",
            "body": """Implement core/analyzer.py with BaseAnalyzer abstract class.

## Requirements
- [ ] Define analyzer interface
- [ ] analyze() method
- [ ] batch_analyze() method
- [ ] Error handling
- [ ] Logging integration
- [ ] Resource management
- [ ] Type hints
- [ ] Abstract base class pattern

## Used By
- Sentiment Analyzer
- Comment Categorizer
- FAQ Extractor
- Abuse Detector
- Other analysis modules""",
            "labels": "implementation,core,phase-3"
        },
        {
            "title": "[CORE] Implement Configuration Management",
            "body": """Implement core/config.py for configuration management.

## Requirements
- [ ] Load from environment variables
- [ ] Load from .env files
- [ ] Support configuration hierarchy
- [ ] Validate configurations
- [ ] Type hints
- [ ] Docstrings
- [ ] Unit tests

## Configuration Categories
- Platform credentials
- Standards and thresholds
- LLM settings
- Logging configuration
- Rate limits""",
            "labels": "implementation,core,phase-3"
        },
        {
            "title": "[CORE] Create Testing Framework",
            "body": """Set up comprehensive testing infrastructure.

## Requirements
- [ ] pytest configuration
- [ ] Test fixtures
- [ ] Mock objects for APIs
- [ ] Test data generators
- [ ] Coverage reporting
- [ ] CI/CD integration
- [ ] Documentation

## Deliverables
- pytest.ini configuration
- conftest.py with fixtures
- test utilities
- coverage setup""",
            "labels": "implementation,testing,phase-3"
        },

        # Analysis Modules (7 issues)
        {
            "title": "[ANALYSIS] Implement Comment Summarizer",
            "body": """Implement analysis/summarizer.py for comment summarization.

## Specification
- docs/comment-analysis/summarization.md

## Requirements
- [ ] Extend BaseAnalyzer
- [ ] Implement analyze() method
- [ ] Implement batch_analyze() method
- [ ] Extract key points
- [ ] Handle long threads
- [ ] Return structured output
- [ ] Type hints
- [ ] Unit tests (80%+ coverage)

## Related
- Sentiment analyzer
- Categorizer
- Community metrics""",
            "labels": "implementation,analysis,phase-3"
        },
        {
            "title": "[ANALYSIS] Implement Comment Categorizer",
            "body": """Implement analysis/categorizer.py for comment categorization.

## Specification
- docs/comment-analysis/categorization.md

## Requirements
- [ ] Extend BaseAnalyzer
- [ ] Define category taxonomy
- [ ] Implement classification logic
- [ ] Handle ambiguous cases
- [ ] Return confidence scores
- [ ] Support custom categories
- [ ] Type hints
- [ ] Unit tests (80%+ coverage)""",
            "labels": "implementation,analysis,phase-3"
        },
        {
            "title": "[ANALYSIS] Implement Sentiment Analyzer",
            "body": """Implement analysis/sentiment.py for sentiment/tone detection.

## Specification
- docs/comment-analysis/sentiment-analysis.md

## Requirements
- [ ] Extend BaseAnalyzer
- [ ] Detect sentiment (positive/negative/neutral)
- [ ] Calculate confidence scores
- [ ] Handle context
- [ ] Detect tone (respectful/aggressive/etc)
- [ ] Return structured output
- [ ] Type hints
- [ ] Unit tests (80%+ coverage)""",
            "labels": "implementation,analysis,phase-3"
        },
        {
            "title": "[ANALYSIS] Implement FAQ Extractor",
            "body": """Implement analysis/faq_extractor.py for FAQ identification.

## Specification
- docs/comment-analysis/faq-extraction.md

## Requirements
- [ ] Extend BaseAnalyzer
- [ ] Identify questions
- [ ] Cluster similar questions
- [ ] Calculate frequency
- [ ] Extract key information
- [ ] Return structured output
- [ ] Type hints
- [ ] Unit tests (80%+ coverage)""",
            "labels": "implementation,analysis,phase-3"
        },
        {
            "title": "[ANALYSIS] Implement Content Ideation Module",
            "body": """Implement analysis/content_ideation.py for content suggestions.

## Specification
- docs/comment-analysis/content-ideation.md

## Requirements
- [ ] Extend BaseAnalyzer
- [ ] Identify content needs
- [ ] Detect gaps
- [ ] Find trending topics
- [ ] Generate suggestions
- [ ] Return structured output
- [ ] Type hints
- [ ] Unit tests (80%+ coverage)""",
            "labels": "implementation,analysis,phase-3"
        },
        {
            "title": "[ANALYSIS] Implement Community Metrics Calculator",
            "body": """Implement analysis/community_metrics.py for community analytics.

## Specification
- docs/comment-analysis/community-metrics.md

## Requirements
- [ ] Calculate engagement metrics
- [ ] Track sentiment trends
- [ ] Analyze volume patterns
- [ ] Detect audience growth
- [ ] Find topic trends
- [ ] Generate reports
- [ ] Type hints
- [ ] Unit tests (80%+ coverage)""",
            "labels": "implementation,analysis,phase-3"
        },
        {
            "title": "[ANALYSIS] Implement Abuse Detector",
            "body": """Implement analysis/abuse_detector.py for abuse/bullying detection.

## Specification
- docs/comment-analysis/abuse-detection.md

## Requirements
- [ ] Extend BaseAnalyzer
- [ ] Detect abuse types
- [ ] Calculate severity scores
- [ ] Consider context
- [ ] Handle false positives
- [ ] Return structured output
- [ ] Type hints
- [ ] Unit tests (80%+ coverage)""",
            "labels": "implementation,analysis,phase-3"
        },

        # Utilities (4 issues)
        {
            "title": "[UTILS] Implement Rate Limiter",
            "body": """Implement utils/rate_limiter.py for API rate limiting.

## Specification
- docs/api-reference/rate-limiting.md

## Requirements
- [ ] Track API call counts
- [ ] Implement exponential backoff
- [ ] Read rate limit headers
- [ ] Optimize batch operations
- [ ] Thread-safe operations
- [ ] Type hints
- [ ] Unit tests""",
            "labels": "implementation,utils,phase-3"
        },
        {
            "title": "[UTILS] Implement Authentication Manager",
            "body": """Implement utils/auth_manager.py for credential management.

## Specification
- docs/api-reference/authentication.md

## Requirements
- [ ] Store API credentials securely
- [ ] Handle token refresh
- [ ] Support multiple credentials
- [ ] Environment variable loading
- [ ] Secure secret storage
- [ ] Type hints
- [ ] Unit tests""",
            "labels": "implementation,utils,phase-3"
        },
        {
            "title": "[UTILS] Implement Error Handler",
            "body": """Implement utils/error_handler.py for standardized error handling.

## Specification
- docs/api-reference/error-handling.md

## Requirements
- [ ] Define exception hierarchy
- [ ] Implement retry logic
- [ ] Structured logging
- [ ] User-friendly messages
- [ ] Error tracking
- [ ] Type hints
- [ ] Unit tests""",
            "labels": "implementation,utils,phase-3"
        },
        {
            "title": "[UTILS] Create Base Platform Interface",
            "body": """Implement platforms/base.py with BasePlatform abstract class.

## Requirements
- [ ] Define platform interface
- [ ] authenticate() method
- [ ] fetch_posts() method
- [ ] fetch_comments() method
- [ ] moderate_comment() method
- [ ] track_post() method
- [ ] Error handling
- [ ] Type hints

## Extended By
- TwitterAPI
- RedditAPI
- InstagramAPI
- MediumAPI
- YouTubeAPI
- TikTokAPI""",
            "labels": "implementation,platforms,phase-3"
        },

        # Platform Integration - Tier 1
        {
            "title": "[PLATFORM] Implement Twitter API Integration",
            "body": """Implement src/platforms/twitter.py with TwitterAPI class.

## Specification
- platforms/twitter/api-guide.md
- platforms/twitter/authentication.md

## Requirements
- [ ] Extend BasePlatform
- [ ] Implement authenticate()
- [ ] Implement fetch_posts()
- [ ] Implement fetch_comments()
- [ ] Implement moderate_comment()
- [ ] Implement track_post()
- [ ] Handle rate limiting
- [ ] Error handling
- [ ] Type hints
- [ ] Docstrings

## Testing
- [ ] Integration tests created
- [ ] Sandbox API validation
- [ ] Error scenarios tested""",
            "labels": "implementation,platform,twitter,phase-5"
        },
        {
            "title": "[PLATFORM] Create Twitter Integration Tests",
            "body": """Create comprehensive tests for Twitter API integration.

## File
- tests/platforms/test_twitter.py

## Requirements
- [ ] Unit tests for all methods
- [ ] Integration tests with sandbox
- [ ] Error handling tests
- [ ] Rate limit tests
- [ ] Mock objects for testing
- [ ] 80%+ code coverage
- [ ] Documentation

## Related
- [PLATFORM] Implement Twitter API Integration""",
            "labels": "testing,platform,twitter,phase-5"
        },
        {
            "title": "[PLATFORM] Implement Reddit API Integration",
            "body": """Implement src/platforms/reddit.py with RedditAPI class.

## Specification
- platforms/reddit/api-guide.md
- platforms/reddit/authentication.md

## Requirements
- [ ] Extend BasePlatform
- [ ] Implement all required methods
- [ ] Handle PRAW library integration
- [ ] Rate limiting
- [ ] Error handling
- [ ] Type hints
- [ ] Docstrings

## Testing
- [ ] Integration tests
- [ ] Sandbox validation
- [ ] Error scenarios""",
            "labels": "implementation,platform,reddit,phase-5"
        },
        {
            "title": "[PLATFORM] Create Reddit Integration Tests",
            "body": """Create comprehensive tests for Reddit API integration.

## File
- tests/platforms/test_reddit.py

## Requirements
- [ ] All method tests
- [ ] Integration tests
- [ ] Error tests
- [ ] Rate limit tests
- [ ] Mocks and fixtures
- [ ] 80%+ coverage
- [ ] Documentation""",
            "labels": "testing,platform,reddit,phase-5"
        },
        {
            "title": "[PLATFORM] Implement YouTube API Integration",
            "body": """Implement src/platforms/youtube.py with YouTubeAPI class.

## Specification
- platforms/youtube/api-guide.md
- platforms/youtube/authentication.md

## Requirements
- [ ] Extend BasePlatform
- [ ] Google API client integration
- [ ] All required methods
- [ ] Rate limiting
- [ ] Error handling
- [ ] Type hints
- [ ] Docstrings

## Testing
- [ ] Integration tests
- [ ] Sandbox validation
- [ ] Error scenarios""",
            "labels": "implementation,platform,youtube,phase-5"
        },
        {
            "title": "[PLATFORM] Create YouTube Integration Tests",
            "body": """Create comprehensive tests for YouTube API integration.

## File
- tests/platforms/test_youtube.py

## Requirements
- [ ] All method tests
- [ ] Integration tests
- [ ] Error tests
- [ ] Rate limit tests
- [ ] Mocks and fixtures
- [ ] 80%+ coverage
- [ ] Documentation""",
            "labels": "testing,platform,youtube,phase-5"
        },

        # Platform Integration - Tier 2
        {
            "title": "[PLATFORM] Implement Instagram API Integration",
            "body": """Implement src/platforms/instagram.py with InstagramAPI class.

## Specification
- platforms/instagram/api-guide.md
- platforms/instagram/authentication.md

## Requirements
- [ ] Extend BasePlatform
- [ ] Implement all required methods
- [ ] Graph API integration
- [ ] Rate limiting
- [ ] Error handling
- [ ] Type hints
- [ ] Docstrings

## Phase
- Phase 6: Tier 2 Integration""",
            "labels": "implementation,platform,instagram,phase-6"
        },
        {
            "title": "[PLATFORM] Create Instagram Integration Tests",
            "body": """Create comprehensive tests for Instagram API integration.

## File
- tests/platforms/test_instagram.py

## Requirements
- [ ] All method tests
- [ ] Integration tests
- [ ] Error tests
- [ ] Rate limit tests
- [ ] Mocks and fixtures
- [ ] 80%+ coverage

## Phase
- Phase 6: Tier 2 Integration""",
            "labels": "testing,platform,instagram,phase-6"
        },
        {
            "title": "[PLATFORM] Implement Medium API Integration",
            "body": """Implement src/platforms/medium.py with MediumAPI class.

## Specification
- platforms/medium/api-guide.md
- platforms/medium/authentication.md

## Requirements
- [ ] Extend BasePlatform
- [ ] All required methods
- [ ] Medium API integration
- [ ] Rate limiting
- [ ] Error handling
- [ ] Type hints
- [ ] Docstrings

## Phase
- Phase 6: Tier 2 Integration""",
            "labels": "implementation,platform,medium,phase-6"
        },
        {
            "title": "[PLATFORM] Create Medium Integration Tests",
            "body": """Create comprehensive tests for Medium API integration.

## File
- tests/platforms/test_medium.py

## Requirements
- [ ] All method tests
- [ ] Integration tests
- [ ] Error tests
- [ ] Rate limit tests
- [ ] Mocks and fixtures
- [ ] 80%+ coverage

## Phase
- Phase 6: Tier 2 Integration""",
            "labels": "testing,platform,medium,phase-6"
        },
        {
            "title": "[PLATFORM] Implement TikTok API Integration",
            "body": """Implement src/platforms/tiktok.py with TikTokAPI class.

## Specification
- platforms/tiktok/api-guide.md
- platforms/tiktok/authentication.md

## Requirements
- [ ] Extend BasePlatform
- [ ] All required methods
- [ ] TikTok API integration
- [ ] Rate limiting
- [ ] Error handling
- [ ] Type hints
- [ ] Docstrings

## Note
- TikTok API may have access restrictions
- Consider alternative approaches if needed

## Phase
- Phase 6: Tier 2 Integration""",
            "labels": "implementation,platform,tiktok,phase-6"
        },
        {
            "title": "[PLATFORM] Create TikTok Integration Tests",
            "body": """Create comprehensive tests for TikTok API integration.

## File
- tests/platforms/test_tiktok.py

## Requirements
- [ ] All method tests
- [ ] Integration tests
- [ ] Error tests
- [ ] Rate limit tests
- [ ] Mocks and fixtures
- [ ] 80%+ coverage

## Phase
- Phase 6: Tier 2 Integration""",
            "labels": "testing,platform,tiktok,phase-6"
        },

        # Examples
        {
            "title": "[EXAMPLES] Create Basic Moderation Example",
            "body": """Create basic_moderation.py demonstrating simple workflow.

## File
- examples/basic_moderation.py

## Demonstrates
- [ ] Initializing moderation engine
- [ ] Analyzing single comment
- [ ] Making moderation decision
- [ ] Executing action
- [ ] Error handling
- [ ] Documentation
- [ ] Comments for explanation

## Phase
- Phase 5: Can start once core + 1 platform done""",
            "labels": "examples,phase-5"
        },
        {
            "title": "[EXAMPLES] Create Multi-Platform Analysis Example",
            "body": """Create multi_platform_analysis.py for cross-platform analysis.

## File
- examples/multi_platform_analysis.py

## Demonstrates
- [ ] Analyzing comments from multiple platforms
- [ ] Cross-platform sentiment comparison
- [ ] Aggregating metrics
- [ ] Comparative analysis
- [ ] Documentation

## Phase
- Phase 6: After 3+ platforms implemented""",
            "labels": "examples,phase-6"
        },
        {
            "title": "[EXAMPLES] Create LLM Integration Example",
            "body": """Create llm_integration.py for LLM-driven moderation.

## File
- examples/llm_integration.py

## Demonstrates
- [ ] Reading context library
- [ ] Integrating with LLM (OpenAI/Anthropic)
- [ ] Prompt engineering for moderation
- [ ] Processing LLM responses
- [ ] Decision making
- [ ] Documentation

## Phase
- Phase 7: Integration & Release""",
            "labels": "examples,phase-7"
        },
        {
            "title": "[INTEGRATION] End-to-End Testing and Validation",
            "body": """Perform comprehensive end-to-end testing.

## Testing Scope
- [ ] Full moderation workflow tested
- [ ] All 6 platforms tested
- [ ] Real-world scenarios tested
- [ ] Performance validated
- [ ] Error scenarios handled
- [ ] Documentation accuracy verified
- [ ] Security review completed

## Deliverables
- [ ] Test report
- [ ] Bug fixes as needed
- [ ] Performance metrics
- [ ] Security sign-off

## Phase
- Phase 7: Release & LLM""",
            "labels": "testing,integration,phase-7"
        },

        # CI/CD and Quality
        {
            "title": "[CI] Set Up GitHub Actions for Tests",
            "body": """Configure GitHub Actions for automated testing.

## Tasks
- [ ] Create .github/workflows/tests.yml
- [ ] Run pytest on every push
- [ ] Run on multiple Python versions
- [ ] Generate coverage reports
- [ ] Badge generation
- [ ] Notifications on failure

## Triggers
- Push to main
- Pull requests
- Schedule (daily)

## Phase
- Phase 3: Start early, improve throughout""",
            "labels": "ci-cd,automation"
        },
        {
            "title": "[CI] Set Up Documentation Validation",
            "body": """Configure documentation quality checks.

## Tasks
- [ ] Link checking
- [ ] Markdown linting
- [ ] Spell checking
- [ ] Style validation
- [ ] Example code validation

## Deliverables
- [ ] .github/workflows/docs.yml
- [ ] Documentation checklist
- [ ] Style guide automation

## Phase
- Phase 0-1: Documentation creation""",
            "labels": "ci-cd,documentation"
        },
        {
            "title": "[QUALITY] Final Documentation Review and Refinement",
            "body": """Perform final quality review of all documentation.

## Review Areas
- [ ] Accuracy of all technical content
- [ ] Consistency across documents
- [ ] LLM consumability verification
- [ ] Example correctness
- [ ] Link validation
- [ ] Completeness
- [ ] Clarity and readability

## Deliverables
- [ ] Issue list for refinements
- [ ] Updates to documentation
- [ ] Sign-off on v1.0 readiness

## Phase
- Phase 7: Final review before release""",
            "labels": "quality,review"
        },
    ]

    print(f"{BLUE}Creating {len(issues)} GitHub issues...{NC}\n")

    successful = 0
    failed = 0

    for i, issue in enumerate(issues, 1):
        print(f"{YELLOW}[{i}/{len(issues)}]{NC} ", end="")
        if create_issue(issue["title"], issue["body"], issue["labels"]):
            successful += 1
        else:
            failed += 1

    print(f"\n{GREEN}[SUCCESS] Created: {successful} issues{NC}")
    if failed > 0:
        print(f"{RED}[FAILED] {failed} issues{NC}")

    print(f"\n{BLUE}GitHub issues created!{NC}")
    print(f"View them at: https://github.com/cgoss/Moderation-ai/issues")

    return 0 if failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
