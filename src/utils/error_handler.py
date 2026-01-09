"""
Error handling utilities for Moderation AI.

This module provides comprehensive error handling patterns including custom
exception classes, error handlers, and logging utilities.
"""

from typing import Any, Dict, Optional, Callable, Type
from functools import wraps
from datetime import datetime
import traceback
import logging

from ..core.config import get_config


class ModerationError(Exception):
    """Base exception for all moderation errors."""

    def __init__(
        self,
        message: str,
        code: str = "MOD_ERROR",
        details: Optional[Dict[str, Any]] = None,
        original_error: Optional[Exception] = None,
    ):
        """
        Initialize moderation error.

        Args:
            message: Error message
            code: Error code for identification
            details: Additional error details
            original_error: Original exception if wrapped
        """
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details or {}
        self.original_error = original_error
        self.timestamp = datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary."""
        return {
            "code": self.code,
            "message": self.message,
            "details": self.details,
            "timestamp": self.timestamp.isoformat(),
            "type": self.__class__.__name__,
        }


class ConfigurationError(ModerationError):
    """Error in configuration."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, code="CONFIG_ERROR", details=details)


class ValidationError(ModerationError):
    """Error in validation."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, code="VALIDATION_ERROR", details=details)


class AuthenticationError(ModerationError):
    """Error in authentication."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, code="AUTH_ERROR", details=details)


class RateLimitError(ModerationError):
    """Error due to rate limiting."""

    def __init__(
        self,
        message: str,
        retry_after: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        if details is None:
            details = {}
        if retry_after is not None:
            details["retry_after"] = retry_after
        super().__init__(message, code="RATE_LIMIT_ERROR", details=details)


class APIError(ModerationError):
    """Error in API communication."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        if details is None:
            details = {}
        if status_code is not None:
            details["status_code"] = status_code
        super().__init__(message, code="API_ERROR", details=details)


class PlatformError(ModerationError):
    """Error from platform integration."""

    def __init__(
        self, message: str, platform: str, details: Optional[Dict[str, Any]] = None
    ):
        if details is None:
            details = {}
        details["platform"] = platform
        super().__init__(message, code="PLATFORM_ERROR", details=details)


class AnalysisError(ModerationError):
    """Error in analysis operation."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, code="ANALYSIS_ERROR", details=details)


class ErrorHandler:
    """
    Centralized error handler for the application.

    Provides consistent error handling, logging, and recovery strategies.
    """

    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize error handler.

        Args:
            logger: Logger instance (creates default if None)
        """
        self.logger = logger or self._setup_logger()
        self._error_handlers: Dict[Type[Exception], Callable] = {}
        self._fallback_handler = self._default_fallback

    def _setup_logger(self) -> logging.Logger:
        """Set up default logger."""
        logger = logging.getLogger("moderation_ai")

        try:
            config = get_config()
            log_level = getattr(config.core.log_level, "value", "INFO")
        except Exception:
            log_level = "INFO"

        logger.setLevel(getattr(logging, log_level))

        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        return logger

    def handle(self, error: Exception) -> None:
        """
        Handle an error.

        Args:
            error: The exception to handle
        """
        error_type = type(error)

        # Find specific handler
        handler = self._error_handlers.get(error_type)

        # Try parent classes
        if handler is None:
            for registered_type, registered_handler in self._error_handlers.items():
                if isinstance(error, registered_type):
                    handler = registered_handler
                    break

        # Use fallback if no handler found
        if handler is None:
            handler = self._fallback_handler

        try:
            handler(error)
        except Exception as e:
            self.logger.error(f"Error in error handler: {e}")

    def register_handler(
        self, error_type: Type[Exception], handler: Callable[[Exception], None]
    ) -> None:
        """
        Register a handler for a specific error type.

        Args:
            error_type: The exception type to handle
            handler: The handler function
        """
        self._error_handlers[error_type] = handler

    def unregister_handler(self, error_type: Type[Exception]) -> bool:
        """
        Unregister a handler for a specific error type.

        Args:
            error_type: The exception type to unregister

        Returns:
            True if handler was removed, False if not found
        """
        if error_type in self._error_handlers:
            del self._error_handlers[error_type]
            return True
        return False

    def _default_fallback(self, error: Exception) -> None:
        """
        Default fallback error handler.

        Args:
            error: The exception to handle
        """
        if isinstance(error, ModerationError):
            self.logger.error(
                f"{error.code}: {error.message}", extra={"details": error.details}
            )
        else:
            self.logger.error(f"Unexpected error: {str(error)}", exc_info=error)

    def wrap(
        self,
        error_type: Type[ModerationError],
        message: str = "An error occurred",
        reraise: bool = True,
    ) -> Callable:
        """
        Decorator to wrap functions with error handling.

        Args:
            error_type: The type of error to raise
            message: Error message to use
            reraise: Whether to reraise the error after handling

        Returns:
            Decorator function
        """

        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args: Any, **kwargs: Any) -> Any:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    # Log the error
                    self.logger.error(f"Error in {func.__name__}: {str(e)}", exc_info=e)

                    # Handle the error
                    self.handle(e)

                    # Raise custom error if needed
                    if reraise:
                        raise error_type(
                            message=message,
                            original_error=e,
                            details={"function": func.__name__},
                        ) from e

                    return None

            return wrapper

        return decorator

    def retry_on_error(
        self,
        error_types: Optional[list[Type[Exception]]] = None,
        max_retries: int = 3,
        backoff_factor: float = 1.0,
    ) -> Callable:
        """
        Decorator to retry functions on specific errors.

        Args:
            error_types: List of error types to retry on
            max_retries: Maximum number of retry attempts
            backoff_factor: Exponential backoff factor

        Returns:
            Decorator function
        """
        if error_types is None:
            error_types = [APIError, RateLimitError]

        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args: Any, **kwargs: Any) -> Any:
                import time

                last_error: Optional[Exception] = None
                for attempt in range(max_retries + 1):
                    try:
                        return func(*args, **kwargs)
                    except tuple(error_types) as e:
                        last_error = e

                        if attempt < max_retries:
                            wait_time = backoff_factor * (2**attempt)
                            self.logger.warning(
                                f"Retry {attempt + 1}/{max_retries} for {func.__name__} "
                                f"after {wait_time}s due to: {str(e)}"
                            )
                            time.sleep(wait_time)
                        else:
                            self.logger.error(
                                f"Max retries exceeded for {func.__name__}"
                            )

                if last_error is not None:
                    raise last_error
                else:
                    raise RuntimeError("Unexpected error in retry logic")

            return wrapper

        return decorator


def create_error_response(
    error: ModerationError, include_traceback: bool = False
) -> Dict[str, Any]:
    """
    Create a standardized error response dictionary.

    Args:
        error: The moderation error
        include_traceback: Whether to include traceback

    Returns:
        Dictionary with error information
    """
    response = error.to_dict()

    if include_traceback:
        response["traceback"] = traceback.format_exc()

    return response


def wrap_errors(
    error_type: Type[ModerationError], message: str = "An error occurred"
) -> Callable:
    """
    Convenience decorator for error wrapping.

    Args:
        error_type: The type of error to raise
        message: Error message to use

    Returns:
        Decorator function
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return func(*args, **kwargs)
            except ModerationError:
                raise
            except Exception as e:
                raise error_type(
                    message=message,
                    original_error=e,
                    details={"function": func.__name__},
                ) from e

        return wrapper

    return decorator
