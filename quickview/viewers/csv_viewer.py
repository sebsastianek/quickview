"""CSV/TSV file viewer."""

import csv

from textual.app import ComposeResult
from textual.widgets import DataTable

from quickview.viewers.base import BaseViewer


class CSVViewer(BaseViewer):
    """Viewer for CSV and TSV files."""

    extensions = [".csv", ".tsv"]

    def __init__(self, filepath: str, app, delimiter: str | None = None):
        super().__init__(filepath, app)
        # Auto-detect delimiter from extension if not provided
        if delimiter is None:
            self.delimiter = "\t" if filepath.lower().endswith(".tsv") else ","
        else:
            self.delimiter = delimiter

    def compose(self) -> ComposeResult:
        yield DataTable(id="csv-table")

    def load(self) -> None:
        table = self.app.query_one("#csv-table", DataTable)
        table.cursor_type = "row"
        table.zebra_stripes = True

        try:
            with open(self.filepath, "r", newline="", encoding="utf-8", errors="replace") as f:
                reader = csv.reader(f, delimiter=self.delimiter)
                rows = list(reader)

            if rows:
                headers = rows[0]
                for i, header in enumerate(headers):
                    table.add_column(header or f"Col {i+1}", key=f"col_{i}")

                for row in rows[1:]:
                    while len(row) < len(headers):
                        row.append("")
                    table.add_row(*row[: len(headers)])

        except Exception as e:
            table.add_column("Error")
            table.add_row(f"Error loading file: {e}")
