"""PDF file viewer."""

from textual import work
from textual.app import ComposeResult
from textual.widgets import Static, TabbedContent, TabPane

from quickview.viewers.base import BaseViewer


class PDFContentWidget(Static):
    """Widget to display PDF page content."""

    pass


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
                yield PDFContentWidget("", id="pdf-single")
            else:
                with TabbedContent():
                    for i in range(self.num_pages):
                        with TabPane(f"Page {i + 1}", id=f"pdf-page-{i}"):
                            yield PDFContentWidget("", id=f"pdf-content-{i}", classes="pdf-page")

        except ImportError:
            yield Static("[red]Error: pypdf not installed. Run: pip install quickview[pdf][/red]")
        except Exception as e:
            yield Static(f"[red]Error loading PDF: {e}[/red]")

    def load(self) -> None:
        self._load_async()

    @work(thread=True)
    def _load_async(self) -> None:
        try:
            import pypdf
        except ImportError:
            return

        try:
            reader = pypdf.PdfReader(self.filepath)
            num_pages = len(reader.pages)
            empty_pages = 0

            for i, page in enumerate(reader.pages):
                text = page.extract_text()

                has_images = len(page.images) > 0 if hasattr(page, "images") else False

                if not text or not text.strip():
                    empty_pages += 1
                    if has_images:
                        text = "[yellow]⚠ This page contains images only - text extraction not supported.\n   Consider using OCR software for scanned documents.[/yellow]"
                    else:
                        text = "[dim]<Empty page>[/dim]"

                formatted_text = self._format_text(text, i + 1, num_pages)
                self.app.call_from_thread(self._update_page, i, formatted_text, num_pages)

            if empty_pages == num_pages:
                self.app.call_from_thread(
                    self.app.notify,
                    "This PDF appears to be image-based (scanned). Text extraction is not supported.",
                    severity="warning",
                )
            elif empty_pages > num_pages / 2:
                self.app.call_from_thread(
                    self.app.notify,
                    f"{empty_pages} of {num_pages} pages have no extractable text.",
                    severity="warning",
                )

        except Exception as e:
            self.app.call_from_thread(
                self.app.notify, f"Error loading PDF: {e}", severity="error"
            )

    def _format_text(self, text: str, page_num: int, total_pages: int) -> str:
        is_markup = text.startswith("[yellow]") or text.startswith("[dim]")

        lines = text.split("\n")
        formatted_lines = [f"[bold cyan]─── Page {page_num} of {total_pages} ───[/bold cyan]", ""]

        for line in lines:
            if not is_markup:
                line = line.replace("[", "\\[")
            formatted_lines.append(line)

        return "\n".join(formatted_lines)

    def _update_page(self, page_index: int, text: str, num_pages: int) -> None:
        try:
            if num_pages == 1:
                viewer = self.app.query_one("#pdf-single", PDFContentWidget)
            else:
                viewer = self.app.query_one(f"#pdf-content-{page_index}", PDFContentWidget)
            viewer.update(text)
        except Exception:
            pass
