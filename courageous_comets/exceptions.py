from dataclasses import dataclass


class CourageousCometsError(Exception):
    """Base class for all Courageous Comets exceptions."""


class AuthenticationError(CourageousCometsError):
    """Raised when authentication with an external service fails."""


@dataclass(kw_only=True)
class ConfigurationValueError[T](CourageousCometsError):
    """
    Raised when a configuration value is invalid.

    Attributes
    ----------
    key : str
        The configuration key.
    value : T, optional
        The invalid value provided.
    reason : str
        The reason why the value is considered invalid.
    """

    key: str
    value: T | None
    reason: str

    def __str__(self) -> str:
        return f"Invalid value '{self.value}' for configuration key '{self.key}': {self.reason}"


class DatabaseConnectionError(CourageousCometsError):
    """Raised when a connection to the database cannot be established."""


class NltkInitializationError(CourageousCometsError):
    """Raised when the application fails to download the NLTK dependencies on startup."""


class HuggingFaceModelDownloadError(CourageousCometsError):
    """Raised when the application fails to download a huggingface model on startup."""
