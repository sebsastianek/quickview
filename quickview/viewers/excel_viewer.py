"""Excel file viewer."""

from textual import work
from textual.app import ComposeResult
from textual.widgets import DataTable, Static, TabbedContent, TabPane

from quickview.viewers.base import BaseViewer


class ExcelViewer(BaseViewer):
    """Viewer for Excel files."""

    extensions = [".xlsx", ".xls", ".xlsm"]

    def compose(self) -> ComposeResult:
        try:
            import openpyxl

            wb = openpyxl.load_workbook(self.filepath, read_only=True, data_only=True)
            sheet_names = wb.sheetnames
            wb.close()

            with TabbedContent():
                for sheet_name in sheet_names:
                    with TabPane(sheet_name, id=f"sheet-{sheet_name}"):
                        yield DataTable(id=f"table-{sheet_name}", classes="excel-table")

        except ImportError:
            yield Static("[red]Error: openpyxl not installed. Run: pip install quickview[excel][/red]")
        except Exception as e:
            yield Static(f"[red]Error loading Excel file: {e}[/red]")

    def load(self) -> None:
        self._load_async()

    @work(thread=True)
    def _load_async(self) -> None:
        try:
            import openpyxl
        except ImportError:
            return

        try:
            wb = openpyxl.load_workbook(self.filepath, read_only=True, data_only=True)

            for sheet_name in wb.sheetnames:
                sheet = wb[sheet_name]
                rows = list(sheet.iter_rows(values_only=True))

                if rows:
                    self.app.call_from_thread(self._populate_table, sheet_name, rows)

            wb.close()

        except Exception as e:
            self.app.call_from_thread(
                self.app.notify, f"Error loading Excel: {e}", severity="error"
            )

    def _populate_table(self, sheet_name: str, rows: list) -> None:
        try:
            table = self.app.query_one(f"#table-{sheet_name}", DataTable)
        except Exception:
            return

        table.cursor_type = "row"
        table.zebra_stripes = True

        if rows:
            max_cols = max(len(row) for row in rows if row)

            def col_name(n: int) -> str:
                result = ""
                while n >= 0:
                    result = chr(65 + (n % 26)) + result
                    n = n // 26 - 1
                return result

            for i in range(max_cols):
                table.add_column(col_name(i), key=f"col_{i}")

            for row in rows:
                if row:
                    str_row = [str(cell) if cell is not None else "" for cell in row]
                    while len(str_row) < max_cols:
                        str_row.append("")
                    table.add_row(*str_row[:max_cols])
