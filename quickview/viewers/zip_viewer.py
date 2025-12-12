"""ZIP archive viewer."""

import zipfile
from datetime import datetime

from textual.app import ComposeResult
from textual.widgets import DataTable

from quickview.viewers.base import BaseViewer
from quickview.utils import format_size


class ZipViewer(BaseViewer):
    """Viewer for ZIP archives."""

    extensions = [".zip"]

    def compose(self) -> ComposeResult:
        yield DataTable(id="zip-table")

    def load(self) -> None:
        table = self.app.query_one("#zip-table", DataTable)
        table.cursor_type = "row"
        table.zebra_stripes = True

        try:
            with zipfile.ZipFile(self.filepath, "r") as zf:
                table.add_column("Name", key="name", width=50)
                table.add_column("Size", key="size", width=12)
                table.add_column("Compressed", key="compressed", width=12)
                table.add_column("Modified", key="modified", width=20)

                infos = sorted(zf.infolist(), key=lambda x: x.filename)

                total_size = 0
                total_compressed = 0

                for info in infos:
                    size = format_size(info.file_size)
                    compressed = format_size(info.compress_size)
                    total_size += info.file_size
                    total_compressed += info.compress_size

                    try:
                        dt = datetime(*info.date_time)
                        modified = dt.strftime("%Y-%m-%d %H:%M")
                    except Exception:
                        modified = "-"

                    name = info.filename
                    if info.is_dir():
                        name = f"[bold blue]{name}[/bold blue]"

                    table.add_row(name, size, compressed, modified)

                ratio = (1 - total_compressed / total_size) * 100 if total_size > 0 else 0
                self.app.notify(
                    f"{len(infos)} files, {format_size(total_size)} → {format_size(total_compressed)} ({ratio:.1f}% saved)",
                    severity="information",
                )

        except zipfile.BadZipFile:
            table.add_column("Error")
            table.add_row("[red]Invalid or corrupted ZIP file[/red]")
        except Exception as e:
            table.add_column("Error")
            table.add_row(f"[red]Error loading ZIP: {e}[/red]")
