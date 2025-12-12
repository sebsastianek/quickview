"""Command-line interface for QuickView."""

import argparse
import sys
from pathlib import Path

from quickview import __version__
from quickview.app import QuickViewApp


def main() -> None:
    """Main entry point for QuickView CLI."""
    parser = argparse.ArgumentParser(
        prog="quickview",
        description="QuickView - Terminal File Viewer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Supported file types:
  CSV/TSV   - Tabular view with navigation
  Excel     - .xlsx, .xls, .xlsm with tabbed sheets
  PDF       - Text extraction with page tabs
  Word      - .docx text and table extraction
  ZIP       - Archive contents listing
  Audio     - MP3, WAV, FLAC, OGG, M4A (waveform)
  Images    - JPEG, PNG, GIF, BMP, WebP (ASCII art)
  Text      - Fallback for other text files

Controls:
  q/Esc     - Quit
  ↑/↓       - Navigate rows
  ←/→       - Scroll horizontally
  PgUp/PgDn - Page navigation
  Home/End  - Jump to start/end
  Tab       - Switch sheets/pages

Examples:
  quickview data.csv
  quickview report.xlsx
  quickview document.pdf
  quickview song.mp3
        """,
    )
    parser.add_argument("file", help="File to view")
    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    args = parser.parse_args()

    filepath = Path(args.file)
    if not filepath.exists():
        print(f"Error: File not found: {args.file}", file=sys.stderr)
        sys.exit(1)

    app = QuickViewApp(str(filepath.resolve()))
    app.run()


if __name__ == "__main__":
    main()
