"""Image file viewer (true color pixel rendering)."""

from textual import work
from textual.app import ComposeResult
from textual.widgets import Static

from quickview.viewers.base import BaseViewer


class ImageWidget(Static):
    """Widget to display images using true color block characters."""

    def __init__(self, filepath: str, **kwargs):
        super().__init__(**kwargs)
        self.filepath = filepath

    def on_mount(self) -> None:
        self._load_image()

    @work(thread=True)
    def _load_image(self) -> None:
        try:
            from PIL import Image
        except ImportError:
            self.app.call_from_thread(
                self.update,
                "[red]Error: Pillow not installed. Run: pip install quickview[image][/red]",
            )
            return

        try:
            img = Image.open(self.filepath)
            orig_width, orig_height = img.size

            # Calculate target size based on terminal
            # Using half-block chars (▀) we get 2 vertical pixels per character
            target_width = 100
            aspect_ratio = img.height / img.width
            # Double height because we use half-blocks for 2 rows per line
            target_height = int(target_width * aspect_ratio)
            # Make height even for half-block rendering
            target_height = target_height + (target_height % 2)

            img = img.resize((target_width, target_height), Image.Resampling.LANCZOS)
            img = img.convert("RGB")

            pixels = list(img.getdata())
            lines = []

            # Header with image info
            lines.append(f"[bold cyan]Image: {orig_width}x{orig_height} → {target_width}x{target_height}[/bold cyan]")
            lines.append("")

            # Render using half-block characters (▀)
            # Each character represents 2 vertical pixels:
            # - Foreground color = top pixel
            # - Background color = bottom pixel
            for y in range(0, target_height, 2):
                line = ""
                for x in range(target_width):
                    # Top pixel (foreground)
                    top_idx = y * target_width + x
                    top_r, top_g, top_b = pixels[top_idx]

                    # Bottom pixel (background)
                    bottom_idx = (y + 1) * target_width + x
                    if bottom_idx < len(pixels):
                        bot_r, bot_g, bot_b = pixels[bottom_idx]
                    else:
                        bot_r, bot_g, bot_b = top_r, top_g, top_b

                    # Use upper half block with fg=top, bg=bottom
                    line += f"[rgb({top_r},{top_g},{top_b}) on rgb({bot_r},{bot_g},{bot_b})]▀[/]"

                lines.append(line)

            self.app.call_from_thread(self.update, "\n".join(lines))

        except Exception as e:
            self.app.call_from_thread(self.update, f"[red]Error loading image: {e}[/red]")


class ImageViewer(BaseViewer):
    """Viewer for image files."""

    extensions = [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"]

    def compose(self) -> ComposeResult:
        yield ImageWidget(self.filepath, id="image-view")

    def load(self) -> None:
        # Loading is handled by ImageWidget.on_mount
        pass
