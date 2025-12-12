"""PDF file viewer."""

from textual import work
from textual.app import ComposeResult
from textual.widgets import Static, TabbedContent, TabPane

from quickview.viewers.base import BaseViewer


class PDFWidget(Static):
    """Widget to display PDF page content."""

    def __init__(self, filepath: str, page_index: int, num_pages: int, **kwargs):
        super().__init__(**kwargs)
        self.filepath = filepath
        self.page_index = page_index
        self.num_pages = num_pages

    def on_mount(self) -> None:
        self._load_page()

    @work(thread=True)
    def _load_page(self) -> None:
        try:
            import pypdf
        except ImportError:
            self.app.call_from_thread(
                self.update,
                "[red]Error: pypdf not installed. Run: pip install quickview[pdf][/red]",
            )
            return

        try:
            reader = pypdf.PdfReader(self.filepath)
            page = reader.pages[self.page_index]
            text = page.extract_text()

            has_images = len(page.images) > 0 if hasattr(page, "images") else False

            if not text or not text.strip():
                if has_images:
                    text = "[yellow]⚠ This page contains images only - text extraction not supported.\n   Consider using OCR software for scanned documents.[/yellow]"
                else:
                    text = "[dim]<Empty page>[/dim]"

            formatted_text = self._format_text(text)
            self.app.call_from_thread(self.update, formatted_text)

        except Exception as e:
            self.app.call_from_thread(
                self.update, f"[red]Error loading page: {e}[/red]"
            )

    def _format_text(self, text: str) -> str:
        is_markup = text.startswith("[yellow]") or text.startswith("[dim]")

        lines = text.split("\n")
        formatted_lines = [
            f"[bold cyan]─── Page {self.page_index + 1} of {self.num_pages} ───[/bold cyan]",
            "",
        ]

        for line in lines:
            if not is_markup:
                line = line.replace("[", "\\[")
            formatted_lines.append(line)

        return "\n".join(formatted_lines)


class PDFViewer(BaseViewer):
    """Viewer for PDF files."""

    extensions = [".pdf"]

    def __init__(self, filepath: str, app):
        super().__init__(filepath, app)
        self.num_pages = 0

    def compose(self) -> ComposeResult:
        try:
            import pypdf

            reader = pypdf.PdfReader(self.filepath)
            self.num_pages = len(reader.pages)

            if self.num_pages == 1:
                yield PDFWidget(self.filepath, 0, 1, id="pdf-single")
            else:
                with TabbedContent():
                    for i in range(self.num_pages):
                        with TabPane(f"Page {i + 1}", id=f"pdf-page-{i}"):
                            yield PDFWidget(
                                self.filepath, i, self.num_pages,
                                id=f"pdf-content-{i}", classes="pdf-page"
                            )

        except ImportError:
            yield Static("[red]Error: pypdf not installed. Run: pip install quickview[pdf][/red]")
        except Exception as e:
            yield Static(f"[red]Error loading PDF: {e}[/red]")

    def load(self) -> None:
        # Loading is handled by PDFWidget.on_mount
        pass
