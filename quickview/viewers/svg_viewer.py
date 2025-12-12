"""SVG file viewer - renders SVG as colored pixels."""

import io

from textual import work
from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.widgets import Static

from quickview.viewers.base import BaseViewer


class SVGWidget(Static):
    """Widget to display SVG images."""

    def __init__(self, filepath: str, **kwargs):
        super().__init__(**kwargs)
        self.filepath = filepath

    def on_mount(self) -> None:
        self._load_svg()

    @work(thread=True)
    def _load_svg(self) -> None:
        try:
            import cairosvg
            from PIL import Image
        except ImportError as e:
            missing = []
            try:
                import cairosvg
            except ImportError:
                missing.append("cairosvg")
            try:
                from PIL import Image
            except ImportError:
                missing.append("Pillow")

            self.app.call_from_thread(
                self.update,
                f"[red]Error: Missing dependencies: {', '.join(missing)}[/red]\n\n"
                "[yellow]Install with:[/yellow]\n"
                "  pip install quickview[svg]",
            )
            return

        try:
            # Convert SVG to PNG in memory
            png_data = cairosvg.svg2png(url=self.filepath)
            img = Image.open(io.BytesIO(png_data))
            orig_width, orig_height = img.size

            # Calculate target size
            target_width = 100
            aspect_ratio = img.height / img.width
            target_height = int(target_width * aspect_ratio)
            target_height = target_height + (target_height % 2)

            img = img.resize((target_width, target_height), Image.Resampling.LANCZOS)
            img = img.convert("RGBA")

            pixels = list(img.getdata())
            lines = []

            lines.append(f"[bold cyan]SVG: {orig_width}x{orig_height} → {target_width}x{target_height}[/bold cyan]")
            lines.append("")

            # Render using half-block characters
            for y in range(0, target_height, 2):
                line = ""
                for x in range(target_width):
                    top_idx = y * target_width + x
                    top_r, top_g, top_b, top_a = pixels[top_idx]

                    bottom_idx = (y + 1) * target_width + x
                    if bottom_idx < len(pixels):
                        bot_r, bot_g, bot_b, bot_a = pixels[bottom_idx]
                    else:
                        bot_r, bot_g, bot_b, bot_a = top_r, top_g, top_b, top_a

                    # Handle transparency - blend with dark background
                    if top_a < 255:
                        bg = 30  # dark background
                        top_r = (top_r * top_a + bg * (255 - top_a)) // 255
                        top_g = (top_g * top_a + bg * (255 - top_a)) // 255
                        top_b = (top_b * top_a + bg * (255 - top_a)) // 255
                    if bot_a < 255:
                        bg = 30
                        bot_r = (bot_r * bot_a + bg * (255 - bot_a)) // 255
                        bot_g = (bot_g * bot_a + bg * (255 - bot_a)) // 255
                        bot_b = (bot_b * bot_a + bg * (255 - bot_a)) // 255

                    line += f"[rgb({top_r},{top_g},{top_b}) on rgb({bot_r},{bot_g},{bot_b})]▀[/]"

                lines.append(line)

            self.app.call_from_thread(self.update, "\n".join(lines))

        except Exception as e:
            self.app.call_from_thread(
                self.update,
                f"[red]Error loading SVG: {e}[/red]",
            )


class SVGViewer(BaseViewer):
    """Viewer for SVG files."""

    extensions = [".svg"]

    def compose(self) -> ComposeResult:
        with VerticalScroll():
            yield SVGWidget(self.filepath, id="svg-view")

    def load(self) -> None:
        # Loading is handled by SVGWidget.on_mount
        pass
