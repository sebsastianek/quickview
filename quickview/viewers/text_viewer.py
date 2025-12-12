"""Plain text file viewer (fallback)."""

from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.widgets import Static

from quickview.viewers.base import BaseViewer


class TextViewer(BaseViewer):
    """Fallback viewer for text files."""

    extensions = []  # Fallback, matches anything

    def compose(self) -> ComposeResult:
        with VerticalScroll():
            yield Static(id="text-content")

    def load(self) -> None:
        content = self.app.query_one("#text-content", Static)
        try:
            with open(self.filepath, "r", encoding="utf-8", errors="replace") as f:
                lines = f.readlines()

            numbered_lines = []
            for i, line in enumerate(lines, 1):
                numbered_lines.append(f"[dim]{i:5d}[/dim] │ {line.rstrip()}")

            content.update("\n".join(numbered_lines))

        except Exception as e:
            content.update(f"[red]Error loading file: {e}[/red]")
