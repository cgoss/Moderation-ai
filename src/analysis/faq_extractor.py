"""
FAQ extraction module.

This module provides functionality to extract frequently
asked questions and common queries from comments.
"""

from typing import Any, Dict, List, Optional, Tuple
import re
from collections import Counter, defaultdict

from .base import Analyzer
from ..core.base import Comment, AnalysisResult


class FAQExtractor(Analyzer):
    """
    Analyzer for FAQ extraction.

    Identifies frequently asked questions and common
    queries from comment discussions.
    """

    # Question patterns
    QUESTION_PATTERNS = [
        r"\?",
        r"\b(how|what|when|where|why|who|which|can|could|would|should|is|are|do|does)\b",
        r"\b(could you|can you|would you|will you)\b",
        r"\b(anyone|someone|somebody)\s+(know|tell|explain|show)",
    ]

    # Question starters
    QUESTION_STARTERS = [
        "how do i",
        "how can i",
        "how to",
        "what is",
        "what are",
        "what does",
        "when does",
        "when will",
        "when is",
        "where can i",
        "where do i",
        "why is",
        "why does",
        "why don't",
        "who can",
        "who should",
        "who is",
    ]

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize FAQ extractor.

        Args:
            config: Optional configuration
        """
        super().__init__(config)
        self._min_occurrences = config.get("min_occurrences", 3) if config else 3
        self._similarity_threshold = (
            config.get("similarity_threshold", 0.7) if config else 0.7
        )

    def analyze(self, comment: Comment) -> AnalysisResult:
        """
        Analyze a comment for FAQ extraction.

        Args:
            comment: The comment to analyze

        Returns:
            AnalysisResult with FAQ data
        """
        if not self.validate_comment(comment):
            return self._create_error_result(comment, "Invalid comment")

        text = comment.text

        # Check if it's a question
        is_question = self._is_question(text)

        # Extract question components
        question_parts = self._extract_question_parts(text)

        # Classify question type
        question_type = self._classify_question_type(text)

        # Extract key terms
        key_terms = self._extract_key_terms(text)

        data = {
            "is_question": is_question,
            "question_type": question_type if is_question else None,
            "question_parts": question_parts if is_question else [],
            "key_terms": key_terms,
            "length": len(text),
            "word_count": len(text.split()),
        }

        confidence = 0.9 if is_question else 0.1
        return self._create_result(comment, data, confidence=confidence)

    def analyze_batch(self, comments: List[Comment]) -> List[AnalysisResult]:
        """
        Analyze multiple comments for FAQ extraction.

        Args:
            comments: List of comments to analyze

        Returns:
            List of AnalysisResult objects
        """
        return [self.analyze(comment) for comment in comments]

    def _is_question(self, text: str) -> bool:
        """
        Check if text is a question.

        Args:
            text: The text to check

        Returns:
            True if question detected
        """
        text_lower = text.lower()

        # Check for question marks
        if "?" in text:
            return True

        # Check for question starters
        for starter in self.QUESTION_STARTERS:
            if text_lower.startswith(starter):
                return True

        # Check for question patterns
        for pattern in self.QUESTION_PATTERNS:
            if re.search(pattern, text_lower):
                return True

        return False

    def _extract_question_parts(self, text: str) -> List[str]:
        """
        Extract parts of a question.

        Args:
            text: The question text

        Returns:
            List of question parts
        """
        # Split on common delimiters
        parts = re.split(r"[.?;]", text)

        # Clean and filter
        cleaned = []
        for part in parts:
            part = part.strip()
            if len(part) > 3:
                cleaned.append(part)

        return cleaned[:5]

    def _classify_question_type(self, text: str) -> str:
        """
        Classify the type of question.

        Args:
            text: The question text

        Returns:
            Question type classification
        """
        text_lower = text.lower()

        # How-to questions
        if text_lower.startswith("how"):
            return "how_to"

        # What questions
        elif text_lower.startswith("what"):
            return "what"

        # Why questions
        elif text_lower.startswith("why"):
            return "why"

        # When questions
        elif text_lower.startswith("when"):
            return "when"

        # Where questions
        elif text_lower.startswith("where"):
            return "where"

        # Who questions
        elif text_lower.startswith("who"):
            return "who"

        # Yes/No questions
        elif any(
            word in text_lower
            for word in ["is", "are", "do", "does", "can", "will", "should"]
        ):
            return "yes_no"

        # Multiple choice
        elif "or" in text_lower and "," in text_lower:
            return "multiple_choice"

        # Open-ended
        else:
            return "open_ended"

    def _extract_key_terms(self, text: str) -> List[str]:
        """
        Extract key terms from text.

        Args:
            text: The text to analyze

        Returns:
            List of key terms
        """
        # Remove question words
        stop_words = {
            "how",
            "what",
            "when",
            "where",
            "why",
            "who",
            "which",
            "can",
            "could",
            "would",
            "should",
            "is",
            "are",
            "do",
            "does",
            "will",
            "did",
            "the",
            "a",
            "an",
            "to",
            "for",
            "of",
            "in",
        }

        words = text.lower().split()

        # Filter out stop words and short words
        key_terms = [word for word in words if word not in stop_words and len(word) > 2]

        return key_terms[:10]

    def extract_faqs(
        self, comments: List[Comment], limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Extract FAQs from multiple comments.

        Args:
            comments: List of comments
            limit: Maximum number of FAQs to return

        Returns:
            List of FAQ dictionaries
        """
        results = self.analyze_batch(comments)

        # Extract all questions
        questions = []
        for result in results:
            if result.success and result.data.get("is_question"):
                questions.append(
                    {
                        "comment_id": result.comment.id,
                        "text": result.comment.text,
                        "question_type": result.data.get("question_type"),
                        "key_terms": result.data.get("key_terms", []),
                    }
                )

        # Group similar questions
        faqs = self._group_similar_questions(questions)

        # Sort by frequency
        sorted_faqs = sorted(faqs, key=lambda x: x["frequency"], reverse=True)[:limit]

        return sorted_faqs

    def _group_similar_questions(
        self, questions: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Group similar questions together.

        Args:
            questions: List of question dictionaries

        Returns:
            List of grouped FAQs
        """
        grouped = []

        for question in questions:
            # Check if similar question already exists
            found_similar = False
            for faq in grouped:
                if self._are_similar(
                    question["text"], faq["text"], self._similarity_threshold
                ):
                    faq["frequency"] += 1
                    faq["examples"].append(question["text"])
                    found_similar = True
                    break

            if not found_similar:
                grouped.append(
                    {
                        "text": question["text"],
                        "frequency": 1,
                        "question_type": question["question_type"],
                        "key_terms": question["key_terms"],
                        "examples": [question["text"]],
                    }
                )

        # Filter by minimum occurrences
        filtered = [faq for faq in grouped if faq["frequency"] >= self._min_occurrences]

        return filtered

    def _are_similar(self, text1: str, text2: str, threshold: float) -> bool:
        """
        Check if two texts are similar.

        Args:
            text1: First text
            text2: Second text
            threshold: Similarity threshold

        Returns:
            True if similar enough
        """
        # Simple Jaccard similarity
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())

        if not words1 or not words2:
            return False

        intersection = len(words1 & words2)
        union = len(words1 | words2)

        similarity = intersection / union if union > 0 else 0.0

        return similarity >= threshold

    def get_question_types_distribution(
        self, comments: List[Comment]
    ) -> Dict[str, float]:
        """
        Get distribution of question types.

        Args:
            comments: List of comments

        Returns:
            Dictionary mapping question types to percentages
        """
        results = self.analyze_batch(comments)

        type_counts: Counter = Counter()

        for result in results:
            if result.success:
                qtype = result.data.get("question_type")
                if qtype:
                    type_counts[qtype] += 1

        total = sum(type_counts.values())
        if total == 0:
            return {}

        return {qtype: count / total for qtype, count in type_counts.items()}

    def get_common_key_terms(
        self, comments: List[Comment], limit: int = 20
    ) -> List[Tuple[str, int]]:
        """
        Get most common key terms.

        Args:
            comments: List of comments
            limit: Maximum number of terms to return

        Returns:
            List of (term, count) tuples
        """
        results = self.analyze_batch(comments)

        term_counts: Counter = Counter()

        for result in results:
            if result.success:
                terms = result.data.get("key_terms", [])
                for term in terms:
                    term_counts[term] += 1

        return term_counts.most_common(limit)
