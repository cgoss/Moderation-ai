"""
Configuration management module for Moderation AI.

This module provides centralized configuration management using Pydantic for
settings validation and environment variable loading.
"""

from typing import Optional, Dict, Any, List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator
from enum import Enum
import os
from pathlib import Path


class LogLevel(str, Enum):
    """Log levels for the application."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LLMProvider(str, Enum):
    """Supported LLM providers."""

    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    LOCAL = "local"


class ModerationAction(str, Enum):
    """Possible moderation actions."""

    APPROVE = "approve"
    FLAG = "flag"
    HIDE = "hide"
    REMOVE = "remove"


class Severity(str, Enum):
    """Severity levels for violations."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Platform(str, Enum):
    """Supported social media platforms."""

    TWITTER = "twitter"
    REDDIT = "reddit"
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    MEDIUM = "medium"
    TIKTOK = "tiktok"


class CoreConfig(BaseSettings):
    """Core application configuration."""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore"
    )

    # Application
    app_name: str = Field(default="moderation-ai", description="Application name")
    version: str = Field(default="0.1.0", description="Application version")
    environment: str = Field(
        default="development", description="Environment (development/production)"
    )
    debug: bool = Field(default=False, description="Debug mode")
    log_level: LogLevel = Field(default=LogLevel.INFO, description="Logging level")

    # Paths
    base_dir: Path = Field(default_factory=lambda: Path(__file__).parent.parent.parent)
    data_dir: Path = Field(
        default_factory=lambda: Path(__file__).parent.parent.parent / "data"
    )
    logs_dir: Path = Field(
        default_factory=lambda: Path(__file__).parent.parent.parent / "logs"
    )

    # LLM Configuration
    llm_provider: LLMProvider = Field(
        default=LLMProvider.OPENAI, description="Default LLM provider"
    )
    llm_model: str = Field(default="gpt-3.5-turbo", description="Default LLM model")
    llm_temperature: float = Field(
        default=0.7, ge=0.0, le=2.0, description="LLM temperature"
    )
    llm_max_tokens: int = Field(default=500, ge=1, description="LLM max tokens")
    llm_timeout: int = Field(
        default=30, ge=1, description="LLM request timeout (seconds)"
    )

    # Moderation Settings
    auto_moderate: bool = Field(
        default=False, description="Enable automatic moderation"
    )
    violation_threshold: float = Field(
        default=0.7, ge=0.0, le=1.0, description="Violation threshold"
    )
    require_review: bool = Field(
        default=True, description="Require human review for violations"
    )

    # Rate Limiting
    enable_rate_limiting: bool = Field(default=True, description="Enable rate limiting")
    requests_per_minute: int = Field(
        default=60, ge=1, description="Requests per minute limit"
    )
    requests_per_hour: int = Field(
        default=1000, ge=1, description="Requests per hour limit"
    )

    # Caching
    enable_cache: bool = Field(default=True, description="Enable caching")
    cache_ttl: int = Field(default=3600, ge=0, description="Cache TTL in seconds")

    # Analysis
    enable_sentiment_analysis: bool = Field(
        default=True, description="Enable sentiment analysis"
    )
    enable_abuse_detection: bool = Field(
        default=True, description="Enable abuse detection"
    )
    enable_categorization: bool = Field(
        default=True, description="Enable categorization"
    )
    enable_summarization: bool = Field(default=True, description="Enable summarization")

    @field_validator("data_dir", "logs_dir", mode="before")
    @classmethod
    def create_dirs(cls, v: Optional[Path]) -> Path:
        """Create directories if they don't exist."""
        if v is None:
            v = (
                Path(__file__).parent.parent.parent / "data"
                if "data_dir" in str(v)
                else Path(__file__).parent.parent.parent / "logs"
            )
        v.mkdir(parents=True, exist_ok=True)
        return v


class OpenAIConfig(BaseSettings):
    """OpenAI API configuration."""

    model_config = SettingsConfigDict(
        env_prefix="OPENAI_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    api_key: str = Field(default="", description="OpenAI API key")
    model: str = Field(default="gpt-3.5-turbo", description="OpenAI model")
    max_retries: int = Field(default=3, ge=0, description="Max retry attempts")
    timeout: int = Field(default=30, ge=1, description="Request timeout (seconds)")


class AnthropicConfig(BaseSettings):
    """Anthropic API configuration."""

    model_config = SettingsConfigDict(
        env_prefix="ANTHROPIC_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    api_key: str = Field(default="", description="Anthropic API key")
    model: str = Field(
        default="claude-3-sonnet-20240229", description="Anthropic model"
    )
    max_retries: int = Field(default=3, ge=0, description="Max retry attempts")
    timeout: int = Field(default=30, ge=1, description="Request timeout (seconds)")


class TwitterConfig(BaseSettings):
    """Twitter/X API configuration."""

    model_config = SettingsConfigDict(
        env_prefix="TWITTER_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    api_key: str = Field(default="", description="Twitter API key")
    api_secret: str = Field(default="", description="Twitter API secret")
    access_token: str = Field(default="", description="Twitter access token")
    access_token_secret: str = Field(
        default="", description="Twitter access token secret"
    )
    bearer_token: str = Field(default="", description="Twitter bearer token")
    timeout: int = Field(default=30, ge=1, description="Request timeout (seconds)")


class RedditConfig(BaseSettings):
    """Reddit API configuration."""

    model_config = SettingsConfigDict(
        env_prefix="REDDIT_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    client_id: str = Field(default="", description="Reddit client ID")
    client_secret: str = Field(default="", description="Reddit client secret")
    user_agent: str = Field(
        default="moderation-ai/0.1", description="Reddit user agent"
    )
    username: str = Field(default="", description="Reddit username")
    password: str = Field(default="", description="Reddit password")
    timeout: int = Field(default=30, ge=1, description="Request timeout (seconds)")


class YouTubeConfig(BaseSettings):
    """YouTube API configuration."""

    model_config = SettingsConfigDict(
        env_prefix="YOUTUBE_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    api_key: str = Field(default="", description="YouTube API key")
    timeout: int = Field(default=30, ge=1, description="Request timeout (seconds)")


class InstagramConfig(BaseSettings):
    """Instagram API configuration."""

    model_config = SettingsConfigDict(
        env_prefix="INSTAGRAM_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    access_token: str = Field(default="", description="Instagram access token")
    app_id: str = Field(default="", description="Instagram app ID")
    app_secret: str = Field(default="", description="Instagram app secret")
    timeout: int = Field(default=30, ge=1, description="Request timeout (seconds)")


class MediumConfig(BaseSettings):
    """Medium API configuration."""

    model_config = SettingsConfigDict(
        env_prefix="MEDIUM_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    api_key: str = Field(default="", description="Medium API key")
    timeout: int = Field(default=30, ge=1, description="Request timeout (seconds)")


class TikTokConfig(BaseSettings):
    """TikTok API configuration."""

    model_config = SettingsConfigDict(
        env_prefix="TIKTOK_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_key: str = Field(default="", description="TikTok app key")
    app_secret: str = Field(default="", description="TikTok app secret")
    timeout: int = Field(default=30, ge=1, description="Request timeout (seconds)")


class Config:
    """Main configuration class that aggregates all settings."""

    _instance: Optional["Config"] = None
    _core: Optional[CoreConfig] = None
    _openai: Optional[OpenAIConfig] = None
    _anthropic: Optional[AnthropicConfig] = None
    _twitter: Optional[TwitterConfig] = None
    _reddit: Optional[RedditConfig] = None
    _youtube: Optional[YouTubeConfig] = None
    _instagram: Optional[InstagramConfig] = None
    _medium: Optional[MediumConfig] = None
    _tiktok: Optional[TikTokConfig] = None

    def __new__(cls) -> "Config":
        """Singleton pattern for configuration."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @property
    def core(self) -> CoreConfig:
        """Get core configuration."""
        if self._core is None:
            self._core = CoreConfig()
        assert self._core is not None
        return self._core

    @property
    def openai(self) -> OpenAIConfig:
        """Get OpenAI configuration."""
        if self._openai is None:
            self._openai = OpenAIConfig()
        assert self._openai is not None
        return self._openai

    @property
    def anthropic(self) -> AnthropicConfig:
        """Get Anthropic configuration."""
        if self._anthropic is None:
            self._anthropic = AnthropicConfig()
        assert self._anthropic is not None
        return self._anthropic

    @property
    def twitter(self) -> TwitterConfig:
        """Get Twitter configuration."""
        if self._twitter is None:
            self._twitter = TwitterConfig()
        assert self._twitter is not None
        return self._twitter

    @property
    def reddit(self) -> RedditConfig:
        """Get Reddit configuration."""
        if self._reddit is None:
            self._reddit = RedditConfig()
        assert self._reddit is not None
        return self._reddit

    @property
    def youtube(self) -> YouTubeConfig:
        """Get YouTube configuration."""
        if self._youtube is None:
            self._youtube = YouTubeConfig()
        assert self._youtube is not None
        return self._youtube

    @property
    def instagram(self) -> InstagramConfig:
        """Get Instagram configuration."""
        if self._instagram is None:
            self._instagram = InstagramConfig()
        assert self._instagram is not None
        return self._instagram

    @property
    def medium(self) -> MediumConfig:
        """Get Medium configuration."""
        if self._medium is None:
            self._medium = MediumConfig()
        assert self._medium is not None
        return self._medium

    @property
    def tiktok(self) -> TikTokConfig:
        """Get TikTok configuration."""
        if self._tiktok is None:
            self._tiktok = TikTokConfig()
        assert self._tiktok is not None
        return self._tiktok

    def get_platform_config(self, platform: Platform) -> Any:
        """Get configuration for a specific platform."""
        platform_configs = {
            Platform.TWITTER: self.twitter,
            Platform.REDDIT: self.reddit,
            Platform.YOUTUBE: self.youtube,
            Platform.INSTAGRAM: self.instagram,
            Platform.MEDIUM: self.medium,
            Platform.TIKTOK: self.tiktok,
        }
        return platform_configs.get(platform)

    def reload(self) -> None:
        """Reload all configurations from environment variables."""
        self._core = CoreConfig()
        self._openai = OpenAIConfig()
        self._anthropic = AnthropicConfig()
        self._twitter = TwitterConfig()
        self._reddit = RedditConfig()
        self._youtube = YouTubeConfig()
        self._instagram = InstagramConfig()
        self._medium = MediumConfig()
        self._tiktok = TikTokConfig()

    def validate(self) -> bool:
        """Validate that required configuration is present."""
        validation_errors = []

        # Check LLM provider
        if self.core.llm_provider == LLMProvider.OPENAI and not self.openai.api_key:
            validation_errors.append(
                "OpenAI API key is required when using OpenAI provider"
            )
        elif (
            self.core.llm_provider == LLMProvider.ANTHROPIC
            and not self.anthropic.api_key
        ):
            validation_errors.append(
                "Anthropic API key is required when using Anthropic provider"
            )

        if validation_errors:
            raise ValueError(
                f"Configuration validation failed:\n" + "\n".join(validation_errors)
            )

        return True

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary (excluding sensitive values)."""
        return {
            "core": self.core.model_dump(exclude={"data_dir", "logs_dir"}),
            "environment": self.core.environment,
            "llm_provider": self.core.llm_provider,
            "auto_moderate": self.core.auto_moderate,
        }


# Global configuration instance
config = Config()


def get_config() -> Config:
    """Get the global configuration instance."""
    return config
