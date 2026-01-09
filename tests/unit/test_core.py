"""Unit tests for core modules."""

import pytest
from datetime import datetime
from pathlib import Path

from src.core.base import (
    Comment,
    Violation,
    ModerationResult,
    AnalysisResult,
    Post,
    ModerationAction,
    Severity,
    Sentiment,
)
from src.core.config import (
    Config,
    CoreConfig,
    LogLevel,
    LLMProvider,
    Platform,
)
from src.core.standards import StandardsEngine, Standard, Metric
from src.core.metrics import MetricsValidator, TextAnalyzer


@pytest.fixture
def sample_comment():
    """Create a sample comment for testing."""
    return Comment(
        id="123",
        text="This is a test comment",
        author_id="user1",
        author_name="Test User",
        created_at=datetime.utcnow(),
        platform="test",
        post_id="post1",
    )


@pytest.fixture
def sample_post():
    """Create a sample post for testing."""
    return Post(
        id="post1",
        title="Test Post",
        content="This is test content",
        author_id="user1",
        author_name="Test User",
        created_at=datetime.utcnow(),
        platform="test",
        url="https://example.com/post1",
    )


class TestComment:
    """Tests for Comment dataclass."""

    def test_comment_creation(self, sample_comment):
        """Test comment creation."""
        assert sample_comment.id == "123"
        assert sample_comment.text == "This is a test comment"
        assert sample_comment.author_id == "user1"
        assert sample_comment.author_name == "Test User"
        assert sample_comment.platform == "test"
        assert sample_comment.post_id == "post1"
        assert sample_comment.likes == 0
        assert sample_comment.replies_count == 0
        assert sample_comment.parent_id is None

    def test_comment_with_parent_id(self):
        """Test comment with parent_id."""
        comment = Comment(
            id="124",
            text="Reply comment",
            author_id="user2",
            author_name="Test User 2",
            created_at=datetime.utcnow(),
            platform="test",
            post_id="post1",
            parent_id="123",
        )
        assert comment.parent_id == "123"

    def test_comment_with_likes(self):
        """Test comment with likes."""
        comment = Comment(
            id="125",
            text="Popular comment",
            author_id="user1",
            author_name="Test User",
            created_at=datetime.utcnow(),
            platform="test",
            post_id="post1",
            likes=10,
            replies_count=5,
        )
        assert comment.likes == 10
        assert comment.replies_count == 5

    def test_comment_to_dict(self, sample_comment):
        """Test comment conversion to dictionary."""
        comment_dict = sample_comment.to_dict()
        assert comment_dict["id"] == "123"
        assert comment_dict["text"] == "This is a test comment"
        assert comment_dict["author_id"] == "user1"
        assert isinstance(comment_dict["created_at"], str)

    def test_comment_from_dict(self):
        """Test comment creation from dictionary."""
        comment_dict = {
            "id": "126",
            "text": "Test from dict",
            "author_id": "user1",
            "author_name": "Test User",
            "created_at": datetime.utcnow().isoformat(),
            "platform": "test",
            "post_id": "post1",
        }
        comment = Comment.from_dict(comment_dict)
        assert comment.id == "126"
        assert comment.text == "Test from dict"


class TestPost:
    """Tests for Post dataclass."""

    def test_post_creation(self, sample_post):
        """Test post creation."""
        assert sample_post.id == "post1"
        assert sample_post.title == "Test Post"
        assert sample_post.content == "This is test content"
        assert sample_post.platform == "test"
        assert sample_post.url == "https://example.com/post1"
        assert sample_post.likes == 0
        assert sample_post.shares == 0
        assert sample_post.comments_count == 0

    def test_post_with_metrics(self):
        """Test post with engagement metrics."""
        post = Post(
            id="post2",
            title="Popular Post",
            content="Content",
            author_id="user1",
            author_name="Test User",
            created_at=datetime.utcnow(),
            platform="test",
            url="https://example.com/post2",
            likes=100,
            shares=50,
            comments_count=25,
        )
        assert post.likes == 100
        assert post.shares == 50
        assert post.comments_count == 25

    def test_post_to_dict(self, sample_post):
        """Test post conversion to dictionary."""
        post_dict = sample_post.to_dict()
        assert post_dict["id"] == "post1"
        assert post_dict["title"] == "Test Post"
        assert isinstance(post_dict["created_at"], str)


class TestViolation:
    """Tests for Violation dataclass."""

    def test_violation_creation(self):
        """Test violation creation."""
        violation = Violation(
            standard="profanity",
            description="Contains profanity",
            severity=Severity.MEDIUM,
            confidence=0.8,
            violated_metrics=["profanity"],
            reasoning="Found 2 profanity words",
        )
        assert violation.standard == "profanity"
        assert violation.severity == Severity.MEDIUM
        assert violation.confidence == 0.8
        assert violation.violated_metrics == ["profanity"]
        assert violation.position is None

    def test_violation_with_position(self):
        """Test violation with position."""
        violation = Violation(
            standard="spam",
            description="Spam content",
            severity=Severity.LOW,
            confidence=0.6,
            violated_metrics=["spam"],
            reasoning="Too many links",
            position=10,
        )
        assert violation.position == 10

    def test_violation_to_dict(self):
        """Test violation conversion to dictionary."""
        violation = Violation(
            standard="profanity",
            description="Contains profanity",
            severity=Severity.MEDIUM,
            confidence=0.8,
            violated_metrics=["profanity"],
            reasoning="Found 2 profanity words",
        )
        violation_dict = violation.to_dict()
        assert violation_dict["standard"] == "profanity"
        assert violation_dict["severity"] == "medium"
        assert violation_dict["confidence"] == 0.8


class TestModerationResult:
    """Tests for ModerationResult dataclass."""

    def test_moderation_result_creation(self, sample_comment):
        """Test moderation result creation."""
        result = ModerationResult(
            comment=sample_comment,
            action=ModerationAction.FLAG,
            violations=[],
            score=0.5,
            confidence=0.7,
            reasoning="Moderate confidence",
        )
        assert result.action == ModerationAction.FLAG
        assert result.score == 0.5
        assert result.confidence == 0.7
        assert result.has_violations is False
        assert result.is_severe is False

    def test_moderation_result_with_violations(self, sample_comment):
        """Test moderation result with violations."""
        violations = [
            Violation(
                standard="profanity",
                description="Profanity",
                severity=Severity.HIGH,
                confidence=0.9,
                violated_metrics=["profanity"],
                reasoning="Profanity detected",
            )
        ]
        result = ModerationResult(
            comment=sample_comment,
            action=ModerationAction.REMOVE,
            violations=violations,
            score=0.8,
            confidence=0.9,
            reasoning="Severe violation",
        )
        assert result.has_violations is True
        assert result.is_severe is True

    def test_moderation_result_is_severe_low(self, sample_comment):
        """Test is_severe with low severity."""
        violations = [
            Violation(
                standard="spam",
                description="Spam",
                severity=Severity.LOW,
                confidence=0.5,
                violated_metrics=["spam"],
                reasoning="Spam detected",
            )
        ]
        result = ModerationResult(
            comment=sample_comment,
            action=ModerationAction.FLAG,
            violations=violations,
            score=0.3,
            confidence=0.5,
            reasoning="Low violation",
        )
        assert result.has_violations is True
        assert result.is_severe is False

    def test_moderation_result_to_dict(self, sample_comment):
        """Test moderation result conversion to dictionary."""
        result = ModerationResult(
            comment=sample_comment,
            action=ModerationAction.APPROVE,
            violations=[],
            score=0.1,
            confidence=0.9,
            reasoning="Clean comment",
        )
        result_dict = result.to_dict()
        assert result_dict["action"] == "approve"
        assert result_dict["score"] == 0.1
        assert isinstance(result_dict["timestamp"], str)


class TestAnalysisResult:
    """Tests for AnalysisResult dataclass."""

    def test_analysis_result_creation(self, sample_comment):
        """Test analysis result creation."""
        result = AnalysisResult(
            comment=sample_comment,
            success=True,
            data={"key": "value"},
        )
        assert result.success is True
        assert result.data == {"key": "value"}
        assert result.error is None
        assert result.confidence == 1.0

    def test_analysis_result_with_error(self, sample_comment):
        """Test analysis result with error."""
        result = AnalysisResult(
            comment=sample_comment,
            success=False,
            data={},
            error="Analysis failed",
            confidence=0.5,
        )
        assert result.success is False
        assert result.error == "Analysis failed"
        assert result.confidence == 0.5

    def test_analysis_result_to_dict(self, sample_comment):
        """Test analysis result conversion to dictionary."""
        result = AnalysisResult(
            comment=sample_comment,
            success=True,
            data={"sentiment": "positive"},
        )
        result_dict = result.to_dict()
        assert result_dict["success"] is True
        assert result_dict["data"] == {"sentiment": "positive"}
        assert isinstance(result_dict["timestamp"], str)


class TestConfig:
    """Tests for Config class."""

    def test_config_singleton(self):
        """Test that Config is a singleton."""
        config1 = Config()
        config2 = Config()
        assert config1 is config2

    def test_core_config_defaults(self):
        """Test core configuration defaults."""
        config = Config()
        assert config.core.app_name == "moderation-ai"
        assert config.core.version == "0.1.0"
        assert config.core.environment == "development"
        assert config.core.debug is False
        assert config.core.log_level == LogLevel.INFO

    def test_core_config_llm_defaults(self):
        """Test LLM configuration defaults."""
        config = Config()
        assert config.core.llm_provider == LLMProvider.OPENAI
        assert config.core.llm_model == "gpt-3.5-turbo"
        assert config.core.llm_temperature == 0.7
        assert config.core.llm_max_tokens == 500

    def test_core_config_moderation_defaults(self):
        """Test moderation configuration defaults."""
        config = Config()
        assert config.core.auto_moderate is False
        assert config.core.violation_threshold == 0.7
        assert config.core.require_review is True

    def test_openai_config(self):
        """Test OpenAI configuration."""
        config = Config()
        assert config.openai.api_key == ""
        assert config.openai.model == "gpt-3.5-turbo"
        assert config.openai.max_retries == 3
        assert config.openai.timeout == 30

    def test_twitter_config(self):
        """Test Twitter configuration."""
        config = Config()
        assert config.twitter.api_key == ""
        assert config.twitter.bearer_token == ""
        assert config.twitter.timeout == 30

    def test_get_platform_config(self):
        """Test getting platform configuration."""
        config = Config()
        twitter_config = config.get_platform_config(Platform.TWITTER)
        reddit_config = config.get_platform_config(Platform.REDDIT)
        assert twitter_config is not None
        assert reddit_config is not None

    def test_config_validate_no_api_key(self):
        """Test validation fails without API key."""
        config = Config()
        with pytest.raises(ValueError, match="OpenAI API key is required"):
            config.validate()

    def test_config_reload(self):
        """Test configuration reload."""
        config = Config()
        original_debug = config.core.debug
        config.core.debug = True
        config.reload()
        assert config.core.debug == original_debug


class TestTextAnalyzer:
    """Tests for TextAnalyzer utility class."""

    def test_count_words(self):
        """Test word counting."""
        assert TextAnalyzer.count_words("Hello world") == 2
        assert TextAnalyzer.count_words("One") == 1
        assert TextAnalyzer.count_words("") == 0

    def test_count_sentences(self):
        """Test sentence counting."""
        assert TextAnalyzer.count_sentences("Hello. World.") == 2
        assert TextAnalyzer.count_sentences("Hello!") == 1
        assert TextAnalyzer.count_sentences("") == 0

    def test_count_links(self):
        """Test URL counting."""
        text = "Check out https://example.com and www.test.com"
        assert TextAnalyzer.count_links(text) == 2

    def test_count_mentions(self):
        """Test mention counting."""
        text = "Hello @user1 and @user2"
        assert TextAnalyzer.count_mentions(text) == 2

    def test_count_hashtags(self):
        """Test hashtag counting."""
        text = "This is #awesome and #great"
        assert TextAnalyzer.count_hashtags(text) == 2

    def test_detect_caps_abuse(self):
        """Test caps abuse detection."""
        assert TextAnalyzer.detect_caps_abuse("ALL CAPS TEXT") is True
        assert TextAnalyzer.detect_caps_abuse("Normal text") is False
        assert TextAnalyzer.detect_caps_abuse("Mixed CASE") is False

    def test_detect_repetition(self):
        """Test repetition detection."""
        assert TextAnalyzer.detect_repetition("aaaaaaa") is True
        assert TextAnalyzer.detect_repetition("test test test") is True
        assert TextAnalyzer.detect_repetition("normal text") is False

    def test_detect_all_caps(self):
        """Test all caps detection."""
        assert TextAnalyzer.detect_all_caps("ALL CAPS") is True
        assert TextAnalyzer.detect_all_caps("Mixed") is False

    def test_contains_profanity(self):
        """Test profanity detection."""
        assert TextAnalyzer.contains_profanity("This is shit") is True
        assert TextAnalyzer.contains_profanity("Clean text") is False

    def test_extract_keywords(self):
        """Test keyword extraction."""
        text = "The quick brown fox jumps over the lazy dog"
        keywords = TextAnalyzer.extract_keywords(text, top_n=5)
        assert isinstance(keywords, list)
        assert len(keywords) <= 5


class TestMetricsValidator:
    """Tests for MetricsValidator class."""

    @pytest.fixture
    def validator(self):
        """Create a validator with test metrics."""
        metrics = {
            "profanity": Metric(
                name="profanity",
                description="Profanity detection",
                check_pattern=r"\b(shit|fuck|damn)\b",
                severity=Severity.MEDIUM,
                threshold=0.5,
            )
        }
        return MetricsValidator(metrics)

    def test_validator_creation(self, validator):
        """Test validator creation."""
        assert validator.metrics is not None
        assert "profanity" in validator.metrics

    def test_validate_profanity_found(self, validator, sample_comment):
        """Test validation when profanity is found."""
        sample_comment.text = "This contains shit"
        passed, score, reasoning = validator.validate(sample_comment, "profanity")
        assert passed is False
        assert score > 0
        assert "profanity" in reasoning.lower()

    def test_validate_no_match(self, validator, sample_comment):
        """Test validation when no match is found."""
        passed, score, reasoning = validator.validate(sample_comment, "profanity")
        assert passed is True
        assert score == 0.0
        assert "No violations" in reasoning

    def test_validate_all(self, validator, sample_comment):
        """Test validating multiple metrics."""
        results = validator.validate_all(sample_comment, ["profanity"])
        assert isinstance(results, dict)
        assert "profanity" in results

    def test_add_custom_validator(self, validator):
        """Test adding custom validator."""

        def custom_validator(comment, metric):
            return True, 0.0, "Custom check passed"

        validator.add_custom_validator("custom", custom_validator)
        assert "custom" in validator._custom_validators

    def test_add_metric(self, validator):
        """Test adding new metric."""
        new_metric = Metric(
            name="spam",
            description="Spam detection",
            check_pattern=r"\b(buy now|click here)\b",
            severity=Severity.LOW,
            threshold=0.3,
        )
        validator.add_metric(new_metric)
        assert "spam" in validator.metrics


class TestStandardsEngine:
    """Tests for StandardsEngine class."""

    @pytest.fixture
    def engine(self):
        """Create a standards engine with default standards."""
        return StandardsEngine()

    def test_engine_creation(self, engine):
        """Test engine creation."""
        assert engine.standards is not None
        assert "safety" in engine.standards

    def test_moderate_clean_comment(self, engine, sample_comment):
        """Test moderation of clean comment."""
        result = engine.moderate(sample_comment)
        assert isinstance(result, ModerationResult)
        assert result.comment == sample_comment

    def test_moderate_violation_comment(self, engine):
        """Test moderation with violations."""
        comment = Comment(
            id="127",
            text="This is SHIT and FUCK",
            author_id="user1",
            author_name="Test User",
            created_at=datetime.utcnow(),
            platform="test",
            post_id="post1",
        )
        result = engine.moderate(comment)
        assert isinstance(result, ModerationResult)
        assert result.has_violations is True

    def test_moderate_batch(self, engine, sample_comment):
        """Test batch moderation."""
        comments = [sample_comment]
        results = engine.moderate_batch(comments)
        assert len(results) == 1
        assert isinstance(results[0], ModerationResult)
