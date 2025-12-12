"""Audio file viewer - displays waveform as ASCII art."""

import array

from textual import work
from textual.app import ComposeResult
from textual.widgets import Static

from quickview.viewers.base import BaseViewer


class AudioWidget(Static):
    """Widget to display audio waveform."""

    def __init__(self, filepath: str, **kwargs):
        super().__init__(**kwargs)
        self.filepath = filepath

    def on_mount(self) -> None:
        self._load_audio()

    @work(thread=True)
    def _load_audio(self) -> None:
        try:
            from pydub import AudioSegment
        except ImportError:
            self.app.call_from_thread(
                self.update,
                "[red]Error: pydub not installed. Run: pip install quickview[audio][/red]\n\n"
                "[dim]Note: You also need ffmpeg installed on your system.[/dim]",
            )
            return

        try:
            audio = AudioSegment.from_file(self.filepath)

            duration_sec = len(audio) / 1000
            duration_min = int(duration_sec // 60)
            duration_remaining = duration_sec % 60
            channels = audio.channels
            sample_rate = audio.frame_rate
            bit_depth = audio.sample_width * 8

            if channels > 1:
                audio_mono = audio.set_channels(1)
            else:
                audio_mono = audio

            samples = array.array(audio_mono.array_type, audio_mono.raw_data)

            waveform = self._generate_waveform(samples, width=100, height=20)

            lines = [
                f"[bold cyan]♫ Audio File: {self.filepath.split('/')[-1]}[/bold cyan]",
                "",
                f"[dim]Duration:[/dim]  {duration_min}:{duration_remaining:05.2f}",
                f"[dim]Channels:[/dim]  {channels} ({'Stereo' if channels == 2 else 'Mono' if channels == 1 else f'{channels}ch'})",
                f"[dim]Sample Rate:[/dim] {sample_rate:,} Hz",
                f"[dim]Bit Depth:[/dim]  {bit_depth}-bit",
                "",
                "[bold]Waveform:[/bold]",
                "",
            ]
            lines.extend(waveform)
            lines.append("")
            lines.append("[dim]─" * 100 + "[/dim]")

            self.app.call_from_thread(self.update, "\n".join(lines))

        except Exception as e:
            error_msg = str(e)
            if "ffmpeg" in error_msg.lower() or "ffprobe" in error_msg.lower():
                self.app.call_from_thread(
                    self.update,
                    "[red]Error: ffmpeg not found.[/red]\n\n"
                    "[yellow]Install ffmpeg:[/yellow]\n"
                    "  macOS:   brew install ffmpeg\n"
                    "  Ubuntu:  sudo apt install ffmpeg\n"
                    "  Windows: choco install ffmpeg",
                )
            else:
                self.app.call_from_thread(
                    self.update,
                    f"[red]Error loading audio: {e}[/red]",
                )

    def _generate_waveform(
        self, samples: array.array, width: int = 100, height: int = 20
    ) -> list[str]:
        """Generate ASCII waveform from audio samples."""
        if not samples:
            return ["[dim]<No audio data>[/dim]"]

        num_samples = len(samples)
        samples_per_col = max(1, num_samples // width)

        columns = []
        for i in range(width):
            start = i * samples_per_col
            end = min(start + samples_per_col, num_samples)
            chunk = samples[start:end]

            if chunk:
                chunk_min = min(chunk)
                chunk_max = max(chunk)
                columns.append((chunk_min, chunk_max))
            else:
                columns.append((0, 0))

        max_amplitude = max(max(abs(c[0]), abs(c[1])) for c in columns)
        if max_amplitude == 0:
            max_amplitude = 1

        half_height = height // 2
        lines = []

        BLOCK_CHARS = " ▁▂▃▄▅▆▇█"

        for row in range(height):
            line = ""
            row_from_center = row - half_height

            for col_min, col_max in columns:
                norm_min = int((col_min / max_amplitude) * half_height)
                norm_max = int((col_max / max_amplitude) * half_height)

                if row_from_center == 0:
                    if norm_min <= 0 <= norm_max:
                        line += "[green]─[/green]"
                    else:
                        line += "[dim]─[/dim]"
                elif row_from_center < 0:
                    threshold = -row_from_center
                    if norm_max >= threshold:
                        intensity = min(8, int((norm_max - threshold + 1) / half_height * 8) + 4)
                        line += f"[cyan]{BLOCK_CHARS[intensity]}[/cyan]"
                    else:
                        line += " "
                else:
                    threshold = -row_from_center
                    if norm_min <= threshold:
                        intensity = min(8, int((threshold - norm_min + 1) / half_height * 8) + 4)
                        line += f"[blue]{BLOCK_CHARS[intensity]}[/blue]"
                    else:
                        line += " "

            lines.append(line)

        time_line = "[dim]0:00"
        time_line += " " * (width - 10)
        time_line += "END[/dim]"
        lines.append(time_line)

        return lines


class AudioViewer(BaseViewer):
    """Viewer for audio files - displays waveform."""

    extensions = [".mp3", ".wav", ".flac", ".ogg", ".m4a", ".aac", ".wma"]

    def compose(self) -> ComposeResult:
        yield AudioWidget(self.filepath, id="audio-content")

    def load(self) -> None:
        # Loading is handled by AudioWidget.on_mount
        pass
