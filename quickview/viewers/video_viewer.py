"""Video file viewer - extracts frames and displays as animation."""

import subprocess
import tempfile
from pathlib import Path

from textual import work
from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.widgets import Static

from quickview.viewers.base import BaseViewer


class VideoWidget(Static):
    """Widget to display video frames as animation."""

    def __init__(self, filepath: str, **kwargs):
        super().__init__(**kwargs)
        self.filepath = filepath
        self._frames: list[str] = []
        self._current_frame = 0
        self._timer = None
        self._temp_dir = None

    def on_mount(self) -> None:
        self._load_video()

    def on_unmount(self) -> None:
        if self._timer:
            self._timer.stop()
        # Cleanup temp files
        if self._temp_dir:
            import shutil
            try:
                shutil.rmtree(self._temp_dir)
            except Exception:
                pass

    @work(thread=True)
    def _load_video(self) -> None:
        try:
            from PIL import Image
        except ImportError:
            self.app.call_from_thread(
                self.update,
                "[red]Error: Pillow not installed. Run: pip install quickview[image][/red]",
            )
            return

        # Check if ffmpeg is available
        try:
            subprocess.run(
                ["ffmpeg", "-version"],
                capture_output=True,
                check=True
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.app.call_from_thread(
                self.update,
                "[red]Error: ffmpeg not found.[/red]\n\n"
                "[yellow]Install ffmpeg:[/yellow]\n"
                "  macOS:   brew install ffmpeg\n"
                "  Ubuntu:  sudo apt install ffmpeg\n"
                "  Windows: choco install ffmpeg",
            )
            return

        try:
            # Get video info
            duration = self._get_duration()
            if duration is None or duration <= 0:
                self.app.call_from_thread(
                    self.update,
                    "[red]Error: Could not read video duration[/red]"
                )
                return

            # Extract frames
            num_frames = min(20, max(8, int(duration)))  # 8-20 frames based on duration
            self._temp_dir = tempfile.mkdtemp(prefix="quickview_")

            self.app.call_from_thread(
                self.update,
                f"[dim]Extracting {num_frames} frames from video...[/dim]"
            )

            frames = self._extract_frames(num_frames, duration)

            if not frames:
                self.app.call_from_thread(
                    self.update,
                    "[red]Error: Could not extract frames from video[/red]"
                )
                return

            # Get video dimensions from first frame
            first_frame = Image.open(frames[0])
            orig_width, orig_height = first_frame.size
            first_frame.close()

            # Render frames
            target_width = 80
            aspect_ratio = orig_height / orig_width
            target_height = int(target_width * aspect_ratio)
            target_height = target_height + (target_height % 2)

            filename = Path(self.filepath).name
            header = f"[bold cyan]Video: {filename}[/bold cyan]\n"
            header += f"[dim]{orig_width}x{orig_height} | {duration:.1f}s | {num_frames} preview frames[/dim]\n\n"

            rendered_frames = []
            for frame_path in frames:
                img = Image.open(frame_path)
                img = img.resize((target_width, target_height), Image.Resampling.LANCZOS)
                img = img.convert("RGB")
                rendered = self._render_frame(img, target_width, target_height)
                rendered_frames.append(header + rendered)
                img.close()

            self._frames = rendered_frames

            # Start animation
            self.app.call_from_thread(self._start_animation)

        except Exception as e:
            self.app.call_from_thread(
                self.update,
                f"[red]Error loading video: {e}[/red]"
            )

    def _get_duration(self) -> float | None:
        """Get video duration using ffprobe."""
        try:
            result = subprocess.run(
                [
                    "ffprobe", "-v", "error",
                    "-show_entries", "format=duration",
                    "-of", "default=noprint_wrappers=1:nokey=1",
                    self.filepath
                ],
                capture_output=True,
                text=True
            )
            return float(result.stdout.strip())
        except (ValueError, subprocess.CalledProcessError):
            return None

    def _extract_frames(self, num_frames: int, duration: float) -> list[str]:
        """Extract frames from video at regular intervals."""
        frames = []
        interval = duration / (num_frames + 1)

        for i in range(num_frames):
            timestamp = interval * (i + 1)
            output_path = Path(self._temp_dir) / f"frame_{i:03d}.png"

            try:
                subprocess.run(
                    [
                        "ffmpeg", "-y",
                        "-ss", str(timestamp),
                        "-i", self.filepath,
                        "-vframes", "1",
                        "-q:v", "2",
                        str(output_path)
                    ],
                    capture_output=True,
                    check=True
                )

                if output_path.exists():
                    frames.append(str(output_path))
            except subprocess.CalledProcessError:
                continue

        return frames

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
            self._current_frame = 0
            self.update(self._frames[0])
            self._timer = self.set_timer(0.5, self._next_frame)  # 0.5s per frame

    def _next_frame(self) -> None:
        """Display the next frame."""
        if not self._frames:
            return

        self._current_frame = (self._current_frame + 1) % len(self._frames)
        self.update(self._frames[self._current_frame])
        self._timer = self.set_timer(0.5, self._next_frame)


class VideoViewer(BaseViewer):
    """Viewer for video files - shows animated preview."""

    extensions = [".mp4", ".mkv", ".avi", ".mov", ".webm", ".wmv", ".flv", ".m4v"]

    def compose(self) -> ComposeResult:
        with VerticalScroll():
            yield VideoWidget(self.filepath, id="video-view")

    def load(self) -> None:
        # Loading is handled by VideoWidget.on_mount
        pass
