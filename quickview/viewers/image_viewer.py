"""Image file viewer (ASCII art conversion)."""

from textual import work
from textual.app import ComposeResult
from textual.widgets import Static

from quickview.viewers.base import BaseViewer


class ImageWidget(Static):
    """Widget to display images as ASCII art."""

    ASCII_CHARS = " .:-=+*#%@"

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
            self.call_from_thread(
                self.update,
                "[red]Error: Pillow not installed. Run: pip install quickview[image][/red]",
            )
            return

        try:
            img = Image.open(self.filepath)

            target_width = 120
            aspect_ratio = img.height / img.width
            new_height = int(target_width * aspect_ratio * 0.5)

            img = img.resize((target_width, new_height))
            img = img.convert("L")

            pixels = list(img.getdata())
            lines = []

            for i in range(0, len(pixels), target_width):
                row_pixels = pixels[i : i + target_width]
                line = ""
                for pixel in row_pixels:
                    char_index = min(
                        int(pixel / 256 * len(self.ASCII_CHARS)),
                        len(self.ASCII_CHARS) - 1,
                    )
                    line += self.ASCII_CHARS[char_index]
                lines.append(line)

            self.call_from_thread(self.update, "\n".join(lines))

        except Exception as e:
            self.call_from_thread(self.update, f"[red]Error loading image: {e}[/red]")


class ImageViewer(BaseViewer):
    """Viewer for image files."""

    extensions = [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"]

    def compose(self) -> ComposeResult:
        yield ImageWidget(self.filepath, id="image-view")

    def load(self) -> None:
        # Loading is handled by ImageWidget.on_mount
        pass
