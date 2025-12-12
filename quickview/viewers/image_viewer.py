"""Image file viewer (true color pixel rendering with GIF animation)."""

from textual import work
from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.widgets import Static

from quickview.viewers.base import BaseViewer


class ImageWidget(Static):
    """Widget to display images using true color block characters."""

    def __init__(self, filepath: str, **kwargs):
        super().__init__(**kwargs)
        self.filepath = filepath
        self._frames: list[str] = []
        self._frame_durations: list[float] = []
        self._current_frame = 0
        self._timer = None
        self._is_animated = False

    def on_mount(self) -> None:
        self._load_image()

    def on_unmount(self) -> None:
        if self._timer:
            self._timer.stop()

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

            # Check if animated GIF
            is_animated = hasattr(img, 'n_frames') and img.n_frames > 1

            if is_animated:
                self._load_animated_gif(img, orig_width, orig_height)
            else:
                self._load_static_image(img, orig_width, orig_height)

        except Exception as e:
            self.app.call_from_thread(self.update, f"[red]Error loading image: {e}[/red]")

    def _load_static_image(self, img, orig_width: int, orig_height: int) -> None:
        """Load a static image."""
        from PIL import Image

        target_width = 100
        aspect_ratio = img.height / img.width
        target_height = int(target_width * aspect_ratio)
        target_height = target_height + (target_height % 2)

        img = img.resize((target_width, target_height), Image.Resampling.LANCZOS)
        img = img.convert("RGB")

        rendered = self._render_frame(img, target_width, target_height)
        header = f"[bold cyan]Image: {orig_width}x{orig_height} → {target_width}x{target_height}[/bold cyan]\n\n"

        self.app.call_from_thread(self.update, header + rendered)

    def _load_animated_gif(self, img, orig_width: int, orig_height: int) -> None:
        """Load and prepare animated GIF frames."""
        from PIL import Image

        target_width = 80  # Slightly smaller for smoother animation
        aspect_ratio = img.height / img.width
        target_height = int(target_width * aspect_ratio)
        target_height = target_height + (target_height % 2)

        frames = []
        durations = []
        n_frames = img.n_frames

        header = f"[bold cyan]GIF: {orig_width}x{orig_height} | {n_frames} frames[/bold cyan]\n\n"

        # Extract and render all frames
        for frame_idx in range(n_frames):
            img.seek(frame_idx)
            frame = img.copy()
            frame = frame.resize((target_width, target_height), Image.Resampling.LANCZOS)
            frame = frame.convert("RGB")

            rendered = self._render_frame(frame, target_width, target_height)
            frames.append(header + rendered)

            # Get frame duration (default 100ms if not specified)
            duration = img.info.get('duration', 100) / 1000.0
            durations.append(max(duration, 0.05))  # Min 50ms

        self._frames = frames
        self._frame_durations = durations
        self._is_animated = True
        self._current_frame = 0

        # Show first frame and start animation
        self.app.call_from_thread(self._start_animation)

    def _render_frame(self, img, target_width: int, target_height: int) -> str:
        """Render a single frame to half-block characters."""
        pixels = list(img.getdata())
        lines = []

        for y in range(0, target_height, 2):
            line = ""
            for x in range(target_width):
                top_idx = y * target_width + x
                top_r, top_g, top_b = pixels[top_idx]

                bottom_idx = (y + 1) * target_width + x
                if bottom_idx < len(pixels):
                    bot_r, bot_g, bot_b = pixels[bottom_idx]
                else:
                    bot_r, bot_g, bot_b = top_r, top_g, top_b

                line += f"[rgb({top_r},{top_g},{top_b}) on rgb({bot_r},{bot_g},{bot_b})]▀[/]"

            lines.append(line)

        return "\n".join(lines)

    def _start_animation(self) -> None:
        """Start the animation timer."""
        if self._frames:
            self.update(self._frames[0])
            self._schedule_next_frame()

    def _schedule_next_frame(self) -> None:
        """Schedule the next frame."""
        if not self._is_animated or not self._frames:
            return

        duration = self._frame_durations[self._current_frame]
        self._timer = self.set_timer(duration, self._next_frame)

    def _next_frame(self) -> None:
        """Display the next frame."""
        if not self._is_animated or not self._frames:
            return

        self._current_frame = (self._current_frame + 1) % len(self._frames)
        self.update(self._frames[self._current_frame])
        self._schedule_next_frame()


class ImageViewer(BaseViewer):
    """Viewer for image files."""

    extensions = [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"]

    def compose(self) -> ComposeResult:
        with VerticalScroll():
            yield ImageWidget(self.filepath, id="image-view")

    def load(self) -> None:
        # Loading is handled by ImageWidget.on_mount
        pass
