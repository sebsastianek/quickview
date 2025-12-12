"""Main QuickView application."""

from pathlib import Path

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import DataTable, Footer, Header

from quickview.viewers import (
    AudioViewer,
    CSVViewer,
    DocxViewer,
    ExcelViewer,
    ImageViewer,
    PDFViewer,
    TextViewer,
    ZipViewer,
)
from quickview.viewers.base import BaseViewer

# Viewer registry - order matters (first match wins)
VIEWERS: list[type[BaseViewer]] = [
    CSVViewer,
    ExcelViewer,
    PDFViewer,
    ZipViewer,
    DocxViewer,
    AudioViewer,
    ImageViewer,
    TextViewer,  # Fallback, must be last
]


def get_viewer(filepath: str, app: App) -> BaseViewer:
    """Get appropriate viewer for file."""
    ext = Path(filepath).suffix.lower()

    for viewer_cls in VIEWERS:
        if viewer_cls.supports(ext):
            return viewer_cls(filepath, app)

    # Fallback to text viewer
    return TextViewer(filepath, app)


class QuickViewApp(App):
    """Terminal file viewer application."""

    CSS = """
    Screen {
        background: $surface;
    }

    DataTable {
        height: 1fr;
    }

    .info-bar {
        dock: bottom;
        height: 1;
        background: $primary;
        color: $text;
        padding: 0 1;
    }

    #image-view {
        height: 1fr;
        overflow: auto scroll;
    }

    #text-content {
        height: 1fr;
        overflow: auto scroll;
    }

    TabbedContent {
        height: 1fr;
    }

    PDFContentWidget {
        height: 1fr;
        overflow: auto scroll;
        padding: 1;
    }

    .pdf-page {
        height: 1fr;
        overflow: auto scroll;
    }

    #docx-content {
        height: 1fr;
        overflow: auto scroll;
        padding: 1 2;
    }

    #audio-content {
        height: 1fr;
        overflow: auto scroll;
        padding: 1 2;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("escape", "quit", "Quit"),
        Binding("home", "scroll_home", "Top", show=False),
        Binding("end", "scroll_end", "Bottom", show=False),
    ]

    def __init__(self, filepath: str):
        super().__init__()
        self.filepath = filepath
        self.filename = Path(filepath).name
        self.viewer: BaseViewer | None = None

    def compose(self) -> ComposeResult:
        yield Header()

        self.viewer = get_viewer(self.filepath, self)
        yield from self.viewer.compose()

        yield Footer()

    def on_mount(self) -> None:
        self.title = f"QuickView - {self.filename}"
        if self.viewer:
            self.viewer.load()

    def action_scroll_home(self) -> None:
        try:
            table = self.query_one(DataTable)
            table.scroll_home()
        except Exception:
            pass

    def action_scroll_end(self) -> None:
        try:
            table = self.query_one(DataTable)
            table.scroll_end()
        except Exception:
            pass
