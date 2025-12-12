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
        self._explicit_delimiter = delimiter

    def _detect_delimiter(self, sample: str) -> str:
        """Auto-detect CSV delimiter using csv.Sniffer or fallback heuristics."""
        # Try csv.Sniffer first
        try:
            dialect = csv.Sniffer().sniff(sample, delimiters=',;\t|')
            return dialect.delimiter
        except csv.Error:
            pass

        # Fallback: count common delimiters and pick most frequent
        delimiters = [';', ',', '\t', '|']
        counts = {d: sample.count(d) for d in delimiters}
        best = max(counts, key=counts.get)
        return best if counts[best] > 0 else ','

    def compose(self) -> ComposeResult:
        yield DataTable(id="csv-table")

    def load(self) -> None:
        table = self.app.query_one("#csv-table", DataTable)
        table.cursor_type = "row"
        table.zebra_stripes = True

        try:
            with open(self.filepath, "r", newline="", encoding="utf-8", errors="replace") as f:
                content = f.read()

            # Determine delimiter
            if self._explicit_delimiter:
                delimiter = self._explicit_delimiter
            elif self.filepath.lower().endswith(".tsv"):
                delimiter = "\t"
            else:
                # Auto-detect from first few KB
                sample = content[:8192]
                delimiter = self._detect_delimiter(sample)

            reader = csv.reader(content.splitlines(), delimiter=delimiter)
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
