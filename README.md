# QuickView

A powerful terminal-based file viewer built with [Textual](https://textual.textualize.io/). Quickly preview various file formats directly in your terminal without leaving the command line.

![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## Features

| Format | Extensions | Description |
|--------|------------|-------------|
| **CSV/TSV** | `.csv`, `.tsv` | Tabular view with auto-delimiter detection |
| **Excel** | `.xlsx`, `.xls`, `.xlsm` | Spreadsheet viewer with tabbed sheets |
| **PDF** | `.pdf` | Text extraction with page-by-page tabs |
| **Word** | `.docx` | Document text and table extraction |
| **ZIP** | `.zip` | Archive listing with sizes and compression stats |
| **Audio** | `.mp3`, `.wav`, `.flac`, `.ogg`, `.m4a` | Waveform visualization |
| **Video** | `.mp4`, `.mkv`, `.avi`, `.mov`, `.webm` | Animated frame preview |
| **Images** | `.jpg`, `.png`, `.bmp`, `.webp` | True color pixel rendering |
| **GIF** | `.gif` | Animated GIF playback |
| **SVG** | `.svg` | Vector graphics rendering |
| **Text** | `*` | Fallback viewer with line numbers |

## Installation

### From PyPI (recommended)

```bash
# Install with all features
pip install quickview[all]

# Or install only what you need
pip install quickview[excel,pdf]
pip install quickview[audio]

# Minimal install (CSV, ZIP, text only)
pip install quickview
```

### From Source

```bash
git clone https://github.com/sebsastianek/quickview.git
cd quickview
pip install -e .[all]
```

### Optional: ffmpeg for Audio/Video Support

Audio waveform and video preview require ffmpeg:

```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt install ffmpeg

# Windows (with Chocolatey)
choco install ffmpeg

# Windows (with Scoop)
scoop install ffmpeg
```

## Usage

```bash
# Full command
quickview <file>

# Short alias
qv <file>
```

### Examples

```bash
# View a CSV file
quickview data.csv

# View an Excel spreadsheet
qv report.xlsx

# View a PDF document
qv document.pdf

# View a Word document
qv proposal.docx

# Browse a ZIP archive
qv backup.zip

# View audio waveform
qv song.mp3

# Preview a video
qv movie.mp4

# View an image
qv photo.jpg

# View animated GIF
qv animation.gif

# View any text file
qv config.yaml
```

## Controls

| Key | Action |
|-----|--------|
| `q` / `Esc` | Quit |
| `↑` / `↓` | Navigate rows |
| `←` / `→` | Scroll horizontally |
| `PgUp` / `PgDn` | Page up/down |
| `Home` / `End` | Jump to start/end |
| `Tab` | Switch sheets/pages (Excel, PDF) |

## Screenshots

### CSV/Excel View
```
┌─────────────────────────────────────────────────────┐
│  #  │ Name          │ Age │ City        │ Salary   │
├─────────────────────────────────────────────────────┤
│  1  │ John Smith    │ 32  │ New York    │ 75000    │
│  2  │ Jane Doe      │ 28  │ Los Angeles │ 82000    │
│  3  │ Bob Johnson   │ 45  │ Chicago     │ 95000    │
└─────────────────────────────────────────────────────┘
```

### Audio Waveform
```
♫ Audio File: song.mp3

Duration:   3:24.50
Channels:   2 (Stereo)
Sample Rate: 44,100 Hz
Bit Depth:  16-bit

Waveform:

      ▂▄▆█▇▅▃▁    ▁▃▅▇█▆▄▂    ▂▄▆█▇▅▃
    ▃▅▇█████▇▅▃▂▂▃▅▇█████▇▅▃▂▃▅▇█████▇▅▃
─────────────────────────────────────────────
    ▃▅▇█████▇▅▃▂▂▃▅▇█████▇▅▃▂▃▅▇█████▇▅▃
      ▂▄▆█▇▅▃▁    ▁▃▅▇█▆▄▂    ▂▄▆█▇▅▃
0:00                                    END
```

### Image View
```
Uses half-block characters (▀) with true RGB colors
to render images at 2x vertical resolution in the terminal.
```

## Optional Dependencies

| Feature | Package | Install Command |
|---------|---------|-----------------|
| Excel | openpyxl | `pip install quickview[excel]` |
| PDF | pypdf | `pip install quickview[pdf]` |
| Images/GIF/Video | Pillow + ffmpeg | `pip install quickview[image]` |
| SVG | cairosvg | `pip install quickview[svg]` |
| Word | python-docx | `pip install quickview[docx]` |
| Audio | pydub + ffmpeg | `pip install quickview[audio]` |

## Development

```bash
# Clone the repository
git clone https://github.com/sebsastianek/quickview.git
cd quickview

# Install in development mode with all dependencies
pip install -e .[all,dev]

# Run tests
pytest

# Run linting
ruff check .

# Run type checking
mypy quickview
```

## Adding Custom Viewers

QuickView is modular - you can easily add support for new file types:

1. Create a new viewer in `quickview/viewers/`:

```python
# quickview/viewers/myformat_viewer.py
from quickview.viewers.base import BaseViewer
from textual.app import ComposeResult
from textual.widgets import Static

class MyFormatViewer(BaseViewer):
    extensions = [".myext", ".other"]

    def compose(self) -> ComposeResult:
        yield Static(id="my-content")

    def load(self) -> None:
        content = self.app.query_one("#my-content", Static)
        # Load and display your file
        content.update("File content here")
```

2. Register it in `quickview/viewers/__init__.py`
3. Add it to `VIEWERS` list in `quickview/app.py`

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

MIT License - see [LICENSE](LICENSE) for details.

## Acknowledgments

- Built with [Textual](https://textual.textualize.io/) - the amazing TUI framework
- Inspired by the need to quickly preview files without leaving the terminal
