"""Base viewer class for QuickView."""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from textual.app import ComposeResult

if TYPE_CHECKING:
    from textual.app import App


class BaseViewer(ABC):
    """Base class for all file viewers."""

    # File extensions this viewer handles
    extensions: list[str] = []

    def __init__(self, filepath: str, app: "App"):
        self.filepath = filepath
        self.app = app

    @abstractmethod
    def compose(self) -> ComposeResult:
        """Create the widgets for this viewer."""
        pass

    @abstractmethod
    def load(self) -> None:
        """Load the file content. Called after mount."""
        pass

    @classmethod
    def supports(cls, extension: str) -> bool:
        """Check if this viewer supports the given extension."""
        return extension.lower() in cls.extensions
