#!/bin/bash

# Script to create all 60 GitHub issues for Moderation AI project
# Usage: ./create-issues.sh

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to create an issue
create_issue() {
    local title="$1"
    local body="$2"
    local labels="$3"
    local milestone="$4"

    echo -e "${BLUE}Creating issue: ${title}${NC}"

    gh issue create \
        --title "$title" \
        --body "$body" \
        --label "$labels" \
        ${milestone:+--milestone "$milestone"} \
        || echo -e "${YELLOW}Failed to create issue: $title${NC}"
}

echo -e "${GREEN}Starting GitHub issue creation...${NC}\n"

# Phase 0: Foundation (5 issues)
echo -e "${YELLOW}=== Phase 0: Foundation ===${NC}"

create_issue \
    "[SETUP] Initialize Project Structure" \
    "Create all necessary directories and files for the project structure.

## Acceptance Criteria
- [x] Directory structure created
- [x] .gitignore configured
- [x] requirements.txt created
- [x] pyproject.toml configured
- [x] Initial git commit

## Related Files
- .gitignore
- requirements.txt
- pyproject.toml" \
    "setup,phase-0" \
    "Phase 0: Foundation"

create_issue \
    "[DOCS] Create Core Documentation" \
    "Create the foundational documentation files for the project.

## Files to Create
- [ ] README.md
- [ ] ARCHITECTURE.md
- [ ] CONTRIBUTING.md
- [ ] LICENSE

## Acceptance Criteria
- [ ] All files complete
- [ ] Clear and comprehensive
- [ ] Following markdown standards
- [ ] Reviewed and approved" \
    "documentation,phase-0" \
    "Phase 0: Foundation"

create_issue \
    "[DOCS] Define LLM Context Consumption Guide" \
    "Create documentation explaining how LLMs should consume this library.

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
- comment-analysis/README.md" \
    "documentation,phase-0" \
    "Phase 0: Foundation"

create_issue \
    "[DOCS] Define Standards and Metrics Framework" \
    "Create comprehensive moderation standards and metrics definitions.

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
- [ ] Moderation actions specified" \
    "documentation,phase-0" \
    "Phase 0: Foundation"

create_issue \
    "[SETUP] Create GitHub Issues and Organize Tracking" \
    "Create all 60 GitHub issues for the project and set up tracking.

## Tasks
- [ ] Create all 60 issues from issue list
- [ ] Apply appropriate labels
- [ ] Assign to milestones/phases
- [ ] Create project board
- [ ] Set up issue templates

## Related Documentation
- docs/implementation-phases.md" \
    "setup,phase-0" \
    "Phase 0: Foundation"

# Phase 1: API Reference & Standards (6 issues)
echo -e "\n${YELLOW}=== Phase 1: API Reference & Standards ===${NC}"

create_issue \
    "[DOCS] Create Unified API Reference Index" \
    "Create the main API reference documentation.

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
- common-patterns.md" \
    "documentation,phase-1" \
    "Phase 1: API Reference & Standards"

create_issue \
    "[DOCS] Document Authentication Patterns" \
    "Document authentication patterns across all platforms.

## File
- docs/api-reference/authentication.md

## Coverage
- [ ] OAuth patterns
- [ ] API key authentication
- [ ] Token management
- [ ] Credential storage
- [ ] Security best practices
- [ ] Platform-specific auth variations" \
    "documentation,phase-1" \
    "Phase 1: API Reference & Standards"

create_issue \
    "[DOCS] Document Rate Limiting Strategies" \
    "Document rate limiting approaches for all platforms.

## File
- docs/api-reference/rate-limiting.md

## Content
- [ ] Rate limit headers
- [ ] Backoff strategies
- [ ] Batch processing
- [ ] Queue management
- [ ] Multi-account strategies
- [ ] Platform-specific limits" \
    "documentation,phase-1" \
    "Phase 1: API Reference & Standards"

create_issue \
    "[DOCS] Document Error Handling Guidelines" \
    "Create error handling patterns and guidelines.

## File
- docs/api-reference/error-handling.md

## Content
- [ ] Common error types
- [ ] HTTP status codes
- [ ] Retry logic
- [ ] Logging patterns
- [ ] User-friendly messages
- [ ] Exception hierarchy" \
    "documentation,phase-1" \
    "Phase 1: API Reference & Standards"

create_issue \
    "[DOCS] Document Webhook Patterns" \
    "Document webhook implementation patterns.

## File
- docs/api-reference/webhooks.md

## Content
- [ ] Webhook payload structure
- [ ] Event types
- [ ] Delivery guarantees
- [ ] Signature verification
- [ ] Retry behavior
- [ ] Platform-specific webhooks" \
    "documentation,phase-1" \
    "Phase 1: API Reference & Standards"

create_issue \
    "[DOCS] Document Common API Patterns" \
    "Document patterns shared across platform APIs.

## File
- docs/api-reference/common-patterns.md

## Content
- [ ] Pagination patterns
- [ ] Query parameters
- [ ] Response formats
- [ ] Status codes
- [ ] Error responses
- [ ] Timestamp formats" \
    "documentation,phase-1" \
    "Phase 1: API Reference & Standards"

# Phase 1: Comment Analysis (8 issues)
echo -e "\n${YELLOW}=== Phase 1: Comment Analysis Framework ===${NC}"

create_issue \
    "[DOCS] Create Comment Analysis Framework Overview" \
    "Create overview of comment analysis methodologies.

## File
- docs/comment-analysis/README.md

## Content
- [ ] Analysis framework overview
- [ ] Available techniques
- [ ] Use cases
- [ ] Integration with moderation
- [ ] Links to detailed docs
- [ ] Example workflows" \
    "documentation,phase-1" \
    "Phase 1: API Reference & Standards"

create_issue \
    "[DOCS] Document Summarization Techniques" \
    "Document comment summarization methodology.

## File
- docs/comment-analysis/summarization.md

## Content
- [ ] Summarization approach
- [ ] Algorithm selection
- [ ] Key point extraction
- [ ] Handling long threads
- [ ] Quality metrics
- [ ] Examples" \
    "documentation,phase-1" \
    "Phase 1: API Reference & Standards"

create_issue \
    "[DOCS] Define Categorization Taxonomy" \
    "Define comment categorization system.

## File
- docs/comment-analysis/categorization.md

## Content
- [ ] Category taxonomy
- [ ] Assignment rules
- [ ] Edge cases
- [ ] Example classifications
- [ ] Use in moderation
- [ ] Custom categories" \
    "documentation,phase-1" \
    "Phase 1: API Reference & Standards"

create_issue \
    "[DOCS] Document Sentiment Analysis Methodology" \
    "Document sentiment/tone detection approach.

## File
- docs/comment-analysis/sentiment-analysis.md

## Content
- [ ] Sentiment categories
- [ ] Detection methodology
- [ ] Confidence scoring
- [ ] Context awareness
- [ ] Examples with scores
- [ ] Platform variations" \
    "documentation,phase-1" \
    "Phase 1: API Reference & Standards"

create_issue \
    "[DOCS] Document FAQ Extraction Process" \
    "Document FAQ identification from comments.

## File
- docs/comment-analysis/faq-extraction.md

## Content
- [ ] FAQ identification criteria
- [ ] Question pattern detection
- [ ] Frequency analysis
- [ ] Topic clustering
- [ ] Output format
- [ ] Examples" \
    "documentation,phase-1" \
    "Phase 1: API Reference & Standards"

create_issue \
    "[DOCS] Document Content Ideation Process" \
    "Document content suggestion from comments.

## File
- docs/comment-analysis/content-ideation.md

## Content
- [ ] Need identification
- [ ] Gap analysis
- [ ] Topic trending
- [ ] Suggestion generation
- [ ] Validation criteria
- [ ] Examples" \
    "documentation,phase-1" \
    "Phase 1: API Reference & Standards"

create_issue \
    "[DOCS] Define Community Metrics" \
    "Document community-level analytics.

## File
- docs/comment-analysis/community-metrics.md

## Content
- [ ] Engagement metrics
- [ ] Sentiment trends
- [ ] Comment volume patterns
- [ ] Audience growth
- [ ] Topic trends
- [ ] Visualization approaches" \
    "documentation,phase-1" \
    "Phase 1: API Reference & Standards"

create_issue \
    "[DOCS] Document Abuse Detection Methodology" \
    "Document abuse and bullying identification.

## File
- docs/comment-analysis/abuse-detection.md

## Content
- [ ] Abuse types
- [ ] Detection signals
- [ ] Confidence scoring
- [ ] Context consideration
- [ ] Severity classification
- [ ] Examples and non-examples" \
    "documentation,phase-1" \
    "Phase 1: API Reference & Standards"

# Platform Documentation Issues (6 issues)
echo -e "\n${YELLOW}=== Platform Documentation ===${NC}"

create_issue \
    "[PLATFORM-DOCS] Document Twitter/X Platform" \
    "Create comprehensive documentation for Twitter/X integration.

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
- [PLATFORM] Create Twitter Integration Tests" \
    "documentation,platform,twitter,phase-2" \
    "Phase 2: Tier 1 Docs"

create_issue \
    "[PLATFORM-DOCS] Document Reddit Platform" \
    "Create comprehensive documentation for Reddit integration.

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
- Phase 2: Tier 1 Platform Docs" \
    "documentation,platform,reddit,phase-2" \
    "Phase 2: Tier 1 Docs"

create_issue \
    "[PLATFORM-DOCS] Document YouTube Platform" \
    "Create comprehensive documentation for YouTube integration.

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
- Phase 2: Tier 1 Platform Docs" \
    "documentation,platform,youtube,phase-2" \
    "Phase 2: Tier 1 Docs"

create_issue \
    "[PLATFORM-DOCS] Document Instagram Platform" \
    "Create comprehensive documentation for Instagram integration.

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
- Phase 4: Tier 2 Platform Docs" \
    "documentation,platform,instagram,phase-4" \
    "Phase 4: Tier 2 Docs"

create_issue \
    "[PLATFORM-DOCS] Document Medium Platform" \
    "Create comprehensive documentation for Medium integration.

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
- Phase 4: Tier 2 Platform Docs" \
    "documentation,platform,medium,phase-4" \
    "Phase 4: Tier 2 Docs"

create_issue \
    "[PLATFORM-DOCS] Document TikTok Platform" \
    "Create comprehensive documentation for TikTok integration.

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
- Phase 4: Tier 2 Platform Docs" \
    "documentation,platform,tiktok,phase-4" \
    "Phase 4: Tier 2 Docs"

# Core Implementation Issues (5 issues)
echo -e "\n${YELLOW}=== Phase 3: Core Implementation ===${NC}"

create_issue \
    "[CORE] Implement Standards Engine" \
    "Implement core/standards.py with StandardsEngine class.

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
- Base Analyzer" \
    "implementation,core,phase-3" \
    "Phase 3: Core Library"

create_issue \
    "[CORE] Implement Metrics Calculator" \
    "Implement core/metrics.py with MetricsValidator class.

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
- Comment Analysis modules" \
    "implementation,core,phase-3" \
    "Phase 3: Core Library"

create_issue \
    "[CORE] Implement Base Analyzer Framework" \
    "Implement core/analyzer.py with BaseAnalyzer abstract class.

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
- Other analysis modules" \
    "implementation,core,phase-3" \
    "Phase 3: Core Library"

create_issue \
    "[CORE] Implement Configuration Management" \
    "Implement core/config.py for configuration management.

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
- Rate limits" \
    "implementation,core,phase-3" \
    "Phase 3: Core Library"

create_issue \
    "[CORE] Create Testing Framework" \
    "Set up comprehensive testing infrastructure.

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
- coverage setup" \
    "implementation,testing,phase-3" \
    "Phase 3: Core Library"

# Analysis Module Issues (7 issues)
echo -e "\n${YELLOW}=== Phase 3: Analysis Modules ===${NC}"

create_issue \
    "[ANALYSIS] Implement Comment Summarizer" \
    "Implement analysis/summarizer.py for comment summarization.

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
- Community metrics" \
    "implementation,analysis,phase-3" \
    "Phase 3: Core Library"

create_issue \
    "[ANALYSIS] Implement Comment Categorizer" \
    "Implement analysis/categorizer.py for comment categorization.

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
- [ ] Unit tests (80%+ coverage)" \
    "implementation,analysis,phase-3" \
    "Phase 3: Core Library"

create_issue \
    "[ANALYSIS] Implement Sentiment Analyzer" \
    "Implement analysis/sentiment.py for sentiment/tone detection.

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
- [ ] Unit tests (80%+ coverage)" \
    "implementation,analysis,phase-3" \
    "Phase 3: Core Library"

create_issue \
    "[ANALYSIS] Implement FAQ Extractor" \
    "Implement analysis/faq_extractor.py for FAQ identification.

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
- [ ] Unit tests (80%+ coverage)" \
    "implementation,analysis,phase-3" \
    "Phase 3: Core Library"

create_issue \
    "[ANALYSIS] Implement Content Ideation Module" \
    "Implement analysis/content_ideation.py for content suggestions.

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
- [ ] Unit tests (80%+ coverage)" \
    "implementation,analysis,phase-3" \
    "Phase 3: Core Library"

create_issue \
    "[ANALYSIS] Implement Community Metrics Calculator" \
    "Implement analysis/community_metrics.py for community analytics.

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
- [ ] Unit tests (80%+ coverage)" \
    "implementation,analysis,phase-3" \
    "Phase 3: Core Library"

create_issue \
    "[ANALYSIS] Implement Abuse Detector" \
    "Implement analysis/abuse_detector.py for abuse/bullying detection.

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
- [ ] Unit tests (80%+ coverage)" \
    "implementation,analysis,phase-3" \
    "Phase 3: Core Library"

# Utility Module Issues (4 issues)
echo -e "\n${YELLOW}=== Phase 3: Utility Modules ===${NC}"

create_issue \
    "[UTILS] Implement Rate Limiter" \
    "Implement utils/rate_limiter.py for API rate limiting.

## Specification
- docs/api-reference/rate-limiting.md

## Requirements
- [ ] Track API call counts
- [ ] Implement exponential backoff
- [ ] Read rate limit headers
- [ ] Optimize batch operations
- [ ] Thread-safe operations
- [ ] Type hints
- [ ] Unit tests" \
    "implementation,utils,phase-3" \
    "Phase 3: Core Library"

create_issue \
    "[UTILS] Implement Authentication Manager" \
    "Implement utils/auth_manager.py for credential management.

## Specification
- docs/api-reference/authentication.md

## Requirements
- [ ] Store API credentials securely
- [ ] Handle token refresh
- [ ] Support multiple credentials
- [ ] Environment variable loading
- [ ] Secure secret storage
- [ ] Type hints
- [ ] Unit tests" \
    "implementation,utils,phase-3" \
    "Phase 3: Core Library"

create_issue \
    "[UTILS] Implement Error Handler" \
    "Implement utils/error_handler.py for standardized error handling.

## Specification
- docs/api-reference/error-handling.md

## Requirements
- [ ] Define exception hierarchy
- [ ] Implement retry logic
- [ ] Structured logging
- [ ] User-friendly messages
- [ ] Error tracking
- [ ] Type hints
- [ ] Unit tests" \
    "implementation,utils,phase-3" \
    "Phase 3: Core Library"

create_issue \
    "[UTILS] Create Base Platform Interface" \
    "Implement platforms/base.py with BasePlatform abstract class.

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
- TikTokAPI" \
    "implementation,platforms,phase-3" \
    "Phase 3: Core Library"

# Platform Integration Issues - Tier 1
echo -e "\n${YELLOW}=== Phase 5: Tier 1 Platform Integration ===${NC}"

create_issue \
    "[PLATFORM] Implement Twitter API Integration" \
    "Implement src/platforms/twitter.py with TwitterAPI class.

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
- [ ] Error scenarios tested" \
    "implementation,platform,twitter,phase-5" \
    "Phase 5: Tier 1 Integration"

create_issue \
    "[PLATFORM] Create Twitter Integration Tests" \
    "Create comprehensive tests for Twitter API integration.

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
- [PLATFORM] Implement Twitter API Integration" \
    "testing,platform,twitter,phase-5" \
    "Phase 5: Tier 1 Integration"

create_issue \
    "[PLATFORM] Implement Reddit API Integration" \
    "Implement src/platforms/reddit.py with RedditAPI class.

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
- [ ] Error scenarios" \
    "implementation,platform,reddit,phase-5" \
    "Phase 5: Tier 1 Integration"

create_issue \
    "[PLATFORM] Create Reddit Integration Tests" \
    "Create comprehensive tests for Reddit API integration.

## File
- tests/platforms/test_reddit.py

## Requirements
- [ ] All method tests
- [ ] Integration tests
- [ ] Error tests
- [ ] Rate limit tests
- [ ] Mocks and fixtures
- [ ] 80%+ coverage
- [ ] Documentation" \
    "testing,platform,reddit,phase-5" \
    "Phase 5: Tier 1 Integration"

create_issue \
    "[PLATFORM] Implement YouTube API Integration" \
    "Implement src/platforms/youtube.py with YouTubeAPI class.

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
- [ ] Error scenarios" \
    "implementation,platform,youtube,phase-5" \
    "Phase 5: Tier 1 Integration"

create_issue \
    "[PLATFORM] Create YouTube Integration Tests" \
    "Create comprehensive tests for YouTube API integration.

## File
- tests/platforms/test_youtube.py

## Requirements
- [ ] All method tests
- [ ] Integration tests
- [ ] Error tests
- [ ] Rate limit tests
- [ ] Mocks and fixtures
- [ ] 80%+ coverage
- [ ] Documentation" \
    "testing,platform,youtube,phase-5" \
    "Phase 5: Tier 1 Integration"

# Platform Integration Issues - Tier 2
echo -e "\n${YELLOW}=== Phase 6: Tier 2 Platform Integration ===${NC}"

create_issue \
    "[PLATFORM] Implement Instagram API Integration" \
    "Implement src/platforms/instagram.py with InstagramAPI class.

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
- Phase 6: Tier 2 Integration" \
    "implementation,platform,instagram,phase-6" \
    "Phase 6: Tier 2 Integration"

create_issue \
    "[PLATFORM] Create Instagram Integration Tests" \
    "Create comprehensive tests for Instagram API integration.

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
- Phase 6: Tier 2 Integration" \
    "testing,platform,instagram,phase-6" \
    "Phase 6: Tier 2 Integration"

create_issue \
    "[PLATFORM] Implement Medium API Integration" \
    "Implement src/platforms/medium.py with MediumAPI class.

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
- Phase 6: Tier 2 Integration" \
    "implementation,platform,medium,phase-6" \
    "Phase 6: Tier 2 Integration"

create_issue \
    "[PLATFORM] Create Medium Integration Tests" \
    "Create comprehensive tests for Medium API integration.

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
- Phase 6: Tier 2 Integration" \
    "testing,platform,medium,phase-6" \
    "Phase 6: Tier 2 Integration"

create_issue \
    "[PLATFORM] Implement TikTok API Integration" \
    "Implement src/platforms/tiktok.py with TikTokAPI class.

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
- Phase 6: Tier 2 Integration" \
    "implementation,platform,tiktok,phase-6" \
    "Phase 6: Tier 2 Integration"

create_issue \
    "[PLATFORM] Create TikTok Integration Tests" \
    "Create comprehensive tests for TikTok API integration.

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
- Phase 6: Tier 2 Integration" \
    "testing,platform,tiktok,phase-6" \
    "Phase 6: Tier 2 Integration"

# Examples and Integration Issues
echo -e "\n${YELLOW}=== Phase 5-7: Examples & Integration ===${NC}"

create_issue \
    "[EXAMPLES] Create Basic Moderation Example" \
    "Create basic_moderation.py demonstrating simple workflow.

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
- Phase 5: Can start once core + 1 platform done" \
    "examples,phase-5" \
    "Phase 5: Tier 1 Integration"

create_issue \
    "[EXAMPLES] Create Multi-Platform Analysis Example" \
    "Create multi_platform_analysis.py for cross-platform analysis.

## File
- examples/multi_platform_analysis.py

## Demonstrates
- [ ] Analyzing comments from multiple platforms
- [ ] Cross-platform sentiment comparison
- [ ] Aggregating metrics
- [ ] Comparative analysis
- [ ] Documentation

## Phase
- Phase 6: After 3+ platforms implemented" \
    "examples,phase-6" \
    "Phase 6: Tier 2 Integration"

create_issue \
    "[EXAMPLES] Create LLM Integration Example" \
    "Create llm_integration.py for LLM-driven moderation.

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
- Phase 7: Integration & Release" \
    "examples,phase-7" \
    "Phase 7: Release & LLM"

create_issue \
    "[INTEGRATION] End-to-End Testing and Validation" \
    "Perform comprehensive end-to-end testing.

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
- Phase 7: Release & LLM" \
    "testing,integration,phase-7" \
    "Phase 7: Release & LLM"

# CI/CD and Quality Issues
echo -e "\n${YELLOW}=== Phase 3-7: CI/CD & Quality ===${NC}"

create_issue \
    "[CI] Set Up GitHub Actions for Tests" \
    "Configure GitHub Actions for automated testing.

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
- Phase 3: Start early, improve throughout" \
    "ci-cd,automation" \
    "Phase 3: Core Library"

create_issue \
    "[CI] Set Up Documentation Validation" \
    "Configure documentation quality checks.

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
- Phase 0-1: Documentation creation" \
    "ci-cd,documentation" \
    "Phase 0: Foundation"

create_issue \
    "[QUALITY] Final Documentation Review and Refinement" \
    "Perform final quality review of all documentation.

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
- Phase 7: Final review before release" \
    "quality,review" \
    "Phase 7: Release & LLM"

echo -e "\n${GREEN}GitHub issue creation complete!${NC}"
echo -e "${YELLOW}Total issues created: 60${NC}"
echo -e "\nNext steps:"
echo -e "1. Review created issues: https://github.com/cgoss/Moderation-ai/issues"
echo -e "2. Set up project board"
echo -e "3. Assign issues to team members"
echo -e "4. Begin Phase 0 work"
