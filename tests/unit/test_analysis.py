"""Unit tests for analysis modules."""

import os
import sys
import pytest
from datetime import datetime

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from src.core.base import Comment, Sentiment, Severity
from src.analysis.sentiment import SentimentAnalyzer
from src.analysis.categorizer import Categorizer
from src.analysis.summarizer import Summarizer
from src.analysis.abuse_detector import AbuseDetector
from src.analysis.faq_extractor import FAQExtractor
from src.analysis.content_ideation import ContentIdeation
from src.analysis.community_metrics import CommunityMetrics


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


class TestSentimentAnalyzer:
    """Tests for SentimentAnalyzer."""

    @pytest.fixture
    def analyzer(self):
        """Create sentiment analyzer instance."""
        return SentimentAnalyzer()

    def test_analyzer_creation(self, analyzer):
        """Test analyzer creation."""
        assert analyzer.POSITIVE_WORDS
        assert analyzer.NEGATIVE_WORDS
        assert analyzer.EMOTION_KEYWORDS

    def test_analyze_positive_comment(self, analyzer):
        """Test analysis of positive comment."""
        comment = Comment(
            id="1",
            text="This is great! I love it!",
            author_id="user1",
            author_name="User",
            created_at=datetime.utcnow(),
            platform="test",
            post_id="post1",
        )
        result = analyzer.analyze(comment)
        assert result.success is True
        assert result.data is not None

    def test_analyze_negative_comment(self, analyzer):
        """Test analysis of negative comment."""
        comment = Comment(
            id="2",
            text="This is terrible! I hate it!",
            author_id="user1",
            author_name="User",
            created_at=datetime.utcnow(),
            platform="test",
            post_id="post1",
        )
        result = analyzer.analyze(comment)
        assert result.success is True
        assert result.data is not None

    def test_analyze_neutral_comment(self, analyzer, sample_comment):
        """Test analysis of neutral comment."""
        result = analyzer.analyze(sample_comment)
        assert result.success is True
        assert result.data is not None

    def test_analyze_batch(self, analyzer, sample_comment):
        """Test batch analysis."""
        comments = [sample_comment]
        results = analyzer.analyze_batch(comments)
        assert len(results) == 1
        assert all(r.success for r in results)

    def test_sentiment_classification_positive(self, analyzer):
        """Test positive sentiment classification."""
        polarity = 0.8
        sentiment = analyzer._classify_sentiment(polarity)
        assert sentiment == Sentiment.POSITIVE

    def test_sentiment_classification_negative(self, analyzer):
        """Test negative sentiment classification."""
        polarity = -0.8
        sentiment = analyzer._classify_sentiment(polarity)
        assert sentiment == Sentiment.NEGATIVE

    def test_sentiment_classification_neutral(self, analyzer):
        """Test neutral sentiment classification."""
        polarity = 0.0
        sentiment = analyzer._classify_sentiment(polarity)
        assert sentiment == Sentiment.NEUTRAL

    def test_emotion_detection(self, analyzer):
        """Test emotion detection."""
        text = "I'm so happy and excited!"
        words = text.split()
        emotions = analyzer._detect_emotions(words)
        assert isinstance(emotions, dict)

    def test_dominant_emotion(self, analyzer):
        """Test dominant emotion extraction."""
        emotions = {"joy": 0.6, "anger": 0.2, "sadness": 0.2}
        dominant = analyzer._get_dominant_emotion(emotions)
        assert dominant == "joy"

    def test_dominant_emotion_empty(self, analyzer):
        """Test dominant emotion with empty dict."""
        dominant = analyzer._get_dominant_emotion({})
        assert dominant is None

    def test_tone_detection(self, analyzer):
        """Test tone detection."""
        text = "Respectfully, I have a question about this."
        words = text.split()
        tone = analyzer._detect_tone(words)
        assert isinstance(tone, dict)


class TestCategorizer:
    """Tests for Categorizer."""

    @pytest.fixture
    def analyzer(self):
        """Create categorizer instance."""
        return Categorizer()

    def test_analyzer_creation(self, analyzer):
        """Test analyzer creation."""
        assert analyzer.TOPIC_CATEGORIES
        assert analyzer.CONTENT_TYPES

    def test_categorize_tech_comment(self, analyzer):
        """Test categorization of tech comment."""
        comment = Comment(
            id="1",
            text="This API is great for software development!",
            author_id="user1",
            author_name="User",
            created_at=datetime.utcnow(),
            platform="test",
            post_id="post1",
        )
        result = analyzer.analyze(comment)
        assert result.success is True
        assert result.data is not None

    def test_categorize_sports_comment(self, analyzer):
        """Test categorization of sports comment."""
        comment = Comment(
            id="2",
            text="Great game! The team played well.",
            author_id="user1",
            author_name="User",
            created_at=datetime.utcnow(),
            platform="test",
            post_id="post1",
        )
        result = analyzer.analyze(comment)
        assert result.success is True

    def test_categorize_question(self, analyzer):
        """Test categorization of question."""
        comment = Comment(
            id="3",
            text="How does this work?",
            author_id="user1",
            author_name="User",
            created_at=datetime.utcnow(),
            platform="test",
            post_id="post1",
        )
        result = analyzer.analyze(comment)
        assert result.success is True
        assert result.data.get("content_type") == "question"

    def test_categorize_general(self, analyzer, sample_comment):
        """Test categorization of general comment."""
        result = analyzer.analyze(sample_comment)
        assert result.success is True
        assert result.data is not None

    def test_categorize_length(self, analyzer):
        """Test length categorization."""
        short_text = "Short"
        medium_text = "This is a medium length comment that has some more content"
        long_text = "A" * 200

        short_len = analyzer._categorize_length(len(short_text))
        medium_len = analyzer._categorize_length(len(medium_text))
        long_len = analyzer._categorize_length(len(long_text))

        assert short_len == "short"
        assert medium_len == "medium"
        assert long_len == "long"

    def test_batch_categorization(self, analyzer, sample_comment):
        """Test batch categorization."""
        comments = [sample_comment]
        results = analyzer.analyze_batch(comments)
        assert len(results) == 1


class TestSummarizer:
    """Tests for Summarizer."""

    @pytest.fixture
    def analyzer(self):
        """Create summarizer instance."""
        return Summarizer()

    def test_analyzer_creation(self, analyzer):
        """Test analyzer creation."""
        assert analyzer is not None

    def test_summarize_short_text(self, analyzer):
        """Test summarization of short text."""
        comment = Comment(
            id="1",
            text="This is a test",
            author_id="user1",
            author_name="User",
            created_at=datetime.utcnow(),
            platform="test",
            post_id="post1",
        )
        result = analyzer.analyze(comment)
        assert result.success is True
        assert result.data is not None

    def test_summarize_long_text(self, analyzer):
        """Test summarization of long text."""
        sentences = ["This is sentence {}.".format(i) for i in range(20)]
        text = " ".join(sentences)
        comment = Comment(
            id="2",
            text=text,
            author_id="user1",
            author_name="User",
            created_at=datetime.utcnow(),
            platform="test",
            post_id="post1",
        )
        result = analyzer.analyze(comment)
        assert result.success is True
        assert "summary" in result.data

    def test_extract_key_phrases(self, analyzer):
        """Test key phrase extraction."""
        text = "machine learning and artificial intelligence are important technologies"
        key_phrases = analyzer._extract_key_phrases(text)
        assert isinstance(key_phrases, list)

    def test_batch_summarization(self, analyzer, sample_comment):
        """Test batch summarization."""
        comments = [sample_comment]
        results = analyzer.analyze_batch(comments)
        assert len(results) == 1


class TestAbuseDetector:
    """Tests for AbuseDetector."""

    @pytest.fixture
    def analyzer(self):
        """Create abuse detector instance."""
        return AbuseDetector()

    def test_analyzer_creation(self, analyzer):
        """Test analyzer creation."""
        assert analyzer.DIRECT_ATTACK_PATTERNS
        assert analyzer.HARASSMENT_PATTERNS
        assert analyzer.THREAT_PATTERNS

    def test_analyze_clean_comment(self, analyzer, sample_comment):
        """Test analysis of clean comment."""
        result = analyzer.analyze(sample_comment)
        assert result.success is True
        assert result.data.get("is_abusive") is False

    def test_analyze_abusive_comment(self, analyzer):
        """Test analysis of abusive comment."""
        comment = Comment(
            id="1",
            text="You are stupid and idiotic!",
            author_id="user1",
            author_name="User",
            created_at=datetime.utcnow(),
            platform="test",
            post_id="post1",
        )
        result = analyzer.analyze(comment)
        assert result.success is True
        assert result.data.get("is_abusive") is True
        assert result.data.get("severity") is not None

    def test_detect_direct_attack(self, analyzer):
        """Test direct attack detection."""
        text = "You are a complete idiot!"
        detected = analyzer._detect_direct_attack(text)
        assert detected["detected"] is True
        assert detected["match_count"] > 0

    def test_detect_harassment(self, analyzer):
        """Test harassment detection."""
        text = "Stop doing this!"
        detected = analyzer._detect_harassment(text)
        assert detected is not None

    def test_detect_threats(self, analyzer):
        """Test threat detection."""
        text = "I will find you!"
        detected = analyzer._detect_threats(text)
        assert detected is not None

    def test_severity_classification(self, analyzer):
        """Test severity classification."""
        low_severity = analyzer._classify_severity(0.2)
        medium_severity = analyzer._classify_severity(0.5)
        high_severity = analyzer._classify_severity(0.7)
        critical_severity = analyzer._classify_severity(0.9)

        assert low_severity == Severity.LOW
        assert medium_severity == Severity.MEDIUM
        assert high_severity == Severity.HIGH
        assert critical_severity == Severity.CRITICAL

    def test_is_severe_abuse(self, analyzer):
        """Test severe abuse detection."""
        comment = Comment(
            id="1",
            text="You are worthless!",
            author_id="user1",
            author_name="User",
            created_at=datetime.utcnow(),
            platform="test",
            post_id="post1",
        )
        is_severe = analyzer.is_severe_abuse(comment)
        assert isinstance(is_severe, bool)

    def test_batch_analysis(self, analyzer, sample_comment):
        """Test batch analysis."""
        comments = [sample_comment]
        results = analyzer.analyze_batch(comments)
        assert len(results) == 1


class TestFAQExtractor:
    """Tests for FAQExtractor."""

    @pytest.fixture
    def analyzer(self):
        """Create FAQ extractor instance."""
        return FAQExtractor()

    def test_analyzer_creation(self, analyzer):
        """Test analyzer creation."""
        assert analyzer.QUESTION_PATTERNS

    def test_extract_question(self, analyzer):
        """Test question extraction."""
        comment = Comment(
            id="1",
            text="How do I get started with this?",
            author_id="user1",
            author_name="User",
            created_at=datetime.utcnow(),
            platform="test",
            post_id="post1",
        )
        result = analyzer.analyze(comment)
        assert result.success is True
        assert result.data.get("is_question") is True

    def test_extract_non_question(self, analyzer, sample_comment):
        """Test extraction of non-question."""
        result = analyzer.analyze(sample_comment)
        assert result.success is True
        assert result.data.get("is_question") is False

    def test_classify_question_type(self, analyzer):
        """Test question type classification."""
        how_to = analyzer._classify_question_type("How does this work?")
        what = analyzer._classify_question_type("What is this?")
        why = analyzer._classify_question_type("Why does this happen?")

        assert how_to == "how-to"
        assert what == "what"
        assert why == "why"

    def test_batch_extraction(self, analyzer, sample_comment):
        """Test batch extraction."""
        comments = [sample_comment]
        results = analyzer.analyze_batch(comments)
        assert len(results) == 1


class TestContentIdeation:
    """Tests for ContentIdeation."""

    @pytest.fixture
    def analyzer(self):
        """Create content ideation instance."""
        return ContentIdeation()

    def test_analyzer_creation(self, analyzer):
        """Test analyzer creation."""
        assert analyzer.CONTENT_REQUEST_PATTERNS
        assert analyzer.TOPIC_CATEGORIES

    def test_extract_content_request(self, analyzer):
        """Test content request extraction."""
        comment = Comment(
            id="1",
            text="It would be great if you made a tutorial!",
            author_id="user1",
            author_name="User",
            created_at=datetime.utcnow(),
            platform="test",
            post_id="post1",
        )
        result = analyzer.analyze(comment)
        assert result.success is True

    def test_categorize_topic(self, analyzer):
        """Test topic categorization."""
        tech_comment = "You should add more API features!"
        comment = Comment(
            id="1",
            text=tech_comment,
            author_id="user1",
            author_name="User",
            created_at=datetime.utcnow(),
            platform="test",
            post_id="post1",
        )
        result = analyzer.analyze(comment)
        assert result.success is True

    def test_batch_ideation(self, analyzer, sample_comment):
        """Test batch ideation."""
        comments = [sample_comment]
        results = analyzer.analyze_batch(comments)
        assert len(results) == 1


class TestCommunityMetrics:
    """Tests for CommunityMetrics."""

    @pytest.fixture
    def analyzer(self):
        """Create community metrics instance."""
        return CommunityMetrics()

    def test_analyzer_creation(self, analyzer):
        """Test analyzer creation."""
        assert analyzer is not None

    def test_calculate_engagement_score(self, analyzer):
        """Test engagement score calculation."""
        comment = Comment(
            id="1",
            text="Engaging comment",
            author_id="user1",
            author_name="User",
            created_at=datetime.utcnow(),
            platform="test",
            post_id="post1",
            likes=10,
            replies_count=5,
        )
        result = analyzer.analyze(comment)
        assert result.success is True
        assert "engagement_score" in result.data

    def test_calculate_influence_score(self, analyzer):
        """Test influence score calculation."""
        comment = Comment(
            id="1",
            text="Influential comment",
            author_id="user1",
            author_name="User",
            created_at=datetime.utcnow(),
            platform="test",
            post_id="post1",
            likes=100,
        )
        result = analyzer.analyze(comment)
        assert result.success is True

    def test_classify_contributor_quality(self, analyzer):
        """Test contributor quality classification."""
        result = analyzer._classify_contributor_quality(50, 0.95)
        assert result in ["low", "medium", "high"]

    def test_calculate_batch_metrics(self, analyzer, sample_comment):
        """Test batch metrics calculation."""
        comments = [sample_comment]
        results = analyzer.analyze_batch(comments)
        assert len(results) == 1
