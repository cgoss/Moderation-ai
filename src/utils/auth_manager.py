"""
Authentication management for social media platforms.

This module provides centralized authentication handling for multiple
social media platforms, including credential storage and token management.
"""

from typing import Any, Dict, Optional
from datetime import datetime, timedelta
import json
from pathlib import Path

from ..core.config import get_config
from .error_handler import AuthenticationError


class AuthManager:
    """
    Manages authentication credentials and tokens.

    Provides secure credential storage, token refresh, and
    authentication status tracking for multiple platforms.
    """

    def __init__(self, config_dir: Optional[Path] = None):
        """
        Initialize authentication manager.

        Args:
            config_dir: Directory to store credentials (uses default if None)
        """
        self.config = get_config()
        self.config_dir = config_dir or self.config.core.data_dir / "auth"
        self.credentials_file = self.config_dir / "credentials.json"

        self._ensure_config_dir()
        self._credentials: Dict[str, Dict[str, Any]] = {}

        # Load existing credentials
        self._load_credentials()

    def _ensure_config_dir(self) -> None:
        """Ensure configuration directory exists."""
        self.config_dir.mkdir(parents=True, exist_ok=True)

    def _load_credentials(self) -> None:
        """Load credentials from file."""
        if self.credentials_file.exists():
            try:
                with open(self.credentials_file, "r") as f:
                    self._credentials = json.load(f)
            except Exception as e:
                raise AuthenticationError(
                    f"Failed to load credentials: {str(e)}",
                    details={"file": str(self.credentials_file)},
                )

    def _save_credentials(self) -> None:
        """Save credentials to file."""
        try:
            with open(self.credentials_file, "w") as f:
                json.dump(self._credentials, f, indent=2)
        except Exception as e:
            raise AuthenticationError(
                f"Failed to save credentials: {str(e)}",
                details={"file": str(self.credentials_file)},
            )

    def add_credentials(self, platform: str, credentials: Dict[str, Any]) -> None:
        """
        Add credentials for a platform.

        Args:
            platform: Platform name
            credentials: Dictionary of credentials
        """
        if platform not in self._credentials:
            self._credentials[platform] = {}

        self._credentials[platform].update(credentials)
        self._credentials[platform]["updated_at"] = datetime.utcnow().isoformat()

        self._save_credentials()

    def get_credentials(self, platform: str) -> Optional[Dict[str, Any]]:
        """
        Get credentials for a platform.

        Args:
            platform: Platform name

        Returns:
            Credentials dictionary or None if not found
        """
        return self._credentials.get(platform)

    def remove_credentials(self, platform: str) -> bool:
        """
        Remove credentials for a platform.

        Args:
            platform: Platform name

        Returns:
            True if removed, False if not found
        """
        if platform in self._credentials:
            del self._credentials[platform]
            self._save_credentials()
            return True
        return False

    def has_credentials(self, platform: str) -> bool:
        """
        Check if credentials exist for a platform.

        Args:
            platform: Platform name

        Returns:
            True if credentials exist, False otherwise
        """
        return platform in self._credentials

    def update_credential(self, platform: str, key: str, value: Any) -> None:
        """
        Update a specific credential for a platform.

        Args:
            platform: Platform name
            key: Credential key
            value: Credential value
        """
        if platform not in self._credentials:
            self._credentials[platform] = {}

        self._credentials[platform][key] = value
        self._credentials[platform]["updated_at"] = datetime.utcnow().isoformat()

        self._save_credentials()

    def get_credential(self, platform: str, key: str) -> Optional[Any]:
        """
        Get a specific credential for a platform.

        Args:
            platform: Platform name
            key: Credential key

        Returns:
            Credential value or None if not found
        """
        platform_creds = self._credentials.get(platform)
        if platform_creds:
            return platform_creds.get(key)
        return None

    def is_authenticated(self, platform: str) -> bool:
        """
        Check if platform is authenticated.

        Args:
            platform: Platform name

        Returns:
            True if authenticated, False otherwise
        """
        creds = self.get_credentials(platform)
        if not creds:
            return False

        # Check for required credentials based on platform
        if platform == "twitter":
            required = ["api_key", "api_secret"]
        elif platform == "reddit":
            required = ["client_id", "client_secret"]
        elif platform == "youtube":
            required = ["api_key"]
        elif platform == "instagram":
            required = ["access_token"]
        elif platform == "medium":
            required = ["api_key"]
        elif platform == "tiktok":
            required = ["app_key", "app_secret"]
        else:
            return False

        return all(creds.get(req) for req in required)

    def clear_all_credentials(self) -> None:
        """Clear all stored credentials."""
        self._credentials = {}
        self._save_credentials()

    def export_credentials(self, exclude_secrets: bool = True) -> Dict[str, Any]:
        """
        Export credentials for backup or transfer.

        Args:
            exclude_secrets: Whether to exclude secret values

        Returns:
            Dictionary of credentials
        """
        export_data = {}

        for platform, creds in self._credentials.items():
            if exclude_secrets:
                export_data[platform] = {
                    key: "***"
                    if any(
                        secret in key.lower()
                        for secret in ["secret", "password", "key", "token"]
                    )
                    else value
                    for key, value in creds.items()
                }
            else:
                export_data[platform] = creds.copy()

        return export_data

    def import_credentials(
        self, credentials: Dict[str, Any], merge: bool = False
    ) -> None:
        """
        Import credentials from dictionary.

        Args:
            credentials: Dictionary of credentials to import
            merge: Whether to merge with existing credentials
        """
        if not merge:
            self._credentials = {}

        for platform, creds in credentials.items():
            if isinstance(creds, dict):
                if platform not in self._credentials:
                    self._credentials[platform] = {}
                self._credentials[platform].update(creds)
                self._credentials[platform]["updated_at"] = (
                    datetime.utcnow().isoformat()
                )

        self._save_credentials()


class TwitterAuth:
    """Twitter authentication handler."""

    @staticmethod
    def from_config(config) -> Dict[str, str]:
        """
        Get Twitter credentials from config.

        Args:
            config: Configuration object

        Returns:
            Dictionary of Twitter credentials
        """
        return {
            "api_key": config.twitter.api_key,
            "api_secret": config.twitter.api_secret,
            "access_token": config.twitter.access_token,
            "access_token_secret": config.twitter.access_token_secret,
            "bearer_token": config.twitter.bearer_token,
        }


class RedditAuth:
    """Reddit authentication handler."""

    @staticmethod
    def from_config(config) -> Dict[str, str]:
        """
        Get Reddit credentials from config.

        Args:
            config: Configuration object

        Returns:
            Dictionary of Reddit credentials
        """
        return {
            "client_id": config.reddit.client_id,
            "client_secret": config.reddit.client_secret,
            "user_agent": config.reddit.user_agent,
            "username": config.reddit.username,
            "password": config.reddit.password,
        }


class YouTubeAuth:
    """YouTube authentication handler."""

    @staticmethod
    def from_config(config) -> Dict[str, str]:
        """
        Get YouTube credentials from config.

        Args:
            config: Configuration object

        Returns:
            Dictionary of YouTube credentials
        """
        return {
            "api_key": config.youtube.api_key,
        }


class InstagramAuth:
    """Instagram authentication handler."""

    @staticmethod
    def from_config(config) -> Dict[str, str]:
        """
        Get Instagram credentials from config.

        Args:
            config: Configuration object

        Returns:
            Dictionary of Instagram credentials
        """
        return {
            "access_token": config.instagram.access_token,
            "app_id": config.instagram.app_id,
            "app_secret": config.instagram.app_secret,
        }


class MediumAuth:
    """Medium authentication handler."""

    @staticmethod
    def from_config(config) -> Dict[str, str]:
        """
        Get Medium credentials from config.

        Args:
            config: Configuration object

        Returns:
            Dictionary of Medium credentials
        """
        return {
            "api_key": config.medium.api_key,
        }


class TikTokAuth:
    """TikTok authentication handler."""

    @staticmethod
    def from_config(config) -> Dict[str, str]:
        """
        Get TikTok credentials from config.

        Args:
            config: Configuration object

        Returns:
            Dictionary of TikTok credentials
        """
        return {
            "app_key": config.tiktok.app_key,
            "app_secret": config.tiktok.app_secret,
        }


def setup_platform_credentials(auth_manager: AuthManager) -> None:
    """
    Setup credentials for all platforms from config.

    Args:
        auth_manager: Authentication manager instance
    """
    config = get_config()

    # Twitter
    if config.twitter.api_key:
        auth_manager.add_credentials("twitter", TwitterAuth.from_config(config))

    # Reddit
    if config.reddit.client_id:
        auth_manager.add_credentials("reddit", RedditAuth.from_config(config))

    # YouTube
    if config.youtube.api_key:
        auth_manager.add_credentials("youtube", YouTubeAuth.from_config(config))

    # Instagram
    if config.instagram.access_token:
        auth_manager.add_credentials("instagram", InstagramAuth.from_config(config))

    # Medium
    if config.medium.api_key:
        auth_manager.add_credentials("medium", MediumAuth.from_config(config))

    # TikTok
    if config.tiktok.app_key:
        auth_manager.add_credentials("tiktok", TikTokAuth.from_config(config))
