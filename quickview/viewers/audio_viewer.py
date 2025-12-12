"""Audio file viewer - displays waveform as ASCII art."""

from textual import work
from textual.app import ComposeResult
from textual.widgets import Static

from quickview.viewers.base import BaseViewer


class AudioViewer(BaseViewer):
    """Viewer for audio files - displays waveform."""

    extensions = [".mp3", ".wav", ".flac", ".ogg", ".m4a", ".aac", ".wma"]

    def compose(self) -> ComposeResult:
        yield Static(id="audio-content", classes="audio-view")

    def load(self) -> None:
        self._load_async()

    @work(thread=True)
    def _load_async(self) -> None:
        try:
            from pydub import AudioSegment
            import array
        except ImportError:
            self.app.call_from_thread(
                self._update_content,
                "[red]Error: pydub not installed. Run: pip install quickview[audio][/red]\n\n"
                "[dim]Note: You also need ffmpeg installed on your system.[/dim]",
            )
            return

        try:
            # Load audio file
            audio = AudioSegment.from_file(self.filepath)

            # Get audio info
            duration_sec = len(audio) / 1000
            duration_min = int(duration_sec // 60)
            duration_remaining = duration_sec % 60
            channels = audio.channels
            sample_rate = audio.frame_rate
            bit_depth = audio.sample_width * 8

            # Convert to mono for waveform display
            if channels > 1:
                audio_mono = audio.set_channels(1)
            else:
                audio_mono = audio

            # Get raw samples
            samples = array.array(audio_mono.array_type, audio_mono.raw_data)

            # Generate waveform
            waveform = self._generate_waveform(samples, width=100, height=20)

            # Build output
            lines = [
                f"[bold cyan]♫ Audio File: {self.app.filename}[/bold cyan]",
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

            self.app.call_from_thread(self._update_content, "\n".join(lines))

        except Exception as e:
            error_msg = str(e)
            if "ffmpeg" in error_msg.lower() or "ffprobe" in error_msg.lower():
                self.app.call_from_thread(
                    self._update_content,
                    f"[red]Error: ffmpeg not found.[/red]\n\n"
                    f"[yellow]Install ffmpeg:[/yellow]\n"
                    f"  macOS:   brew install ffmpeg\n"
                    f"  Ubuntu:  sudo apt install ffmpeg\n"
                    f"  Windows: choco install ffmpeg",
                )
            else:
                self.app.call_from_thread(
                    self._update_content,
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

        # Calculate min/max for each column
        columns = []
        for i in range(width):
            start = i * samples_per_col
            end = min(start + samples_per_col, num_samples)
            chunk = samples[start:end]

            if chunk:
                # Get min and max for this chunk
                chunk_min = min(chunk)
                chunk_max = max(chunk)
                columns.append((chunk_min, chunk_max))
            else:
                columns.append((0, 0))

        # Normalize to height
        max_amplitude = max(
            max(abs(c[0]), abs(c[1])) for c in columns
        )
        if max_amplitude == 0:
            max_amplitude = 1

        # Build the waveform display
        half_height = height // 2
        lines = []

        # Characters for waveform
        BLOCK_CHARS = " ▁▂▃▄▅▆▇█"

        for row in range(height):
            line = ""
            row_from_center = row - half_height

            for col_min, col_max in columns:
                # Normalize values to -half_height to +half_height
                norm_min = int((col_min / max_amplitude) * half_height)
                norm_max = int((col_max / max_amplitude) * half_height)

                # Determine character for this position
                if row_from_center == 0:
                    # Center line
                    if norm_min <= 0 <= norm_max:
                        line += "[green]─[/green]"
                    else:
                        line += "[dim]─[/dim]"
                elif row_from_center < 0:
                    # Upper half (negative row means visual top = positive amplitude)
                    threshold = -row_from_center
                    if norm_max >= threshold:
                        intensity = min(8, int((norm_max - threshold + 1) / half_height * 8) + 4)
                        line += f"[cyan]{BLOCK_CHARS[intensity]}[/cyan]"
                    else:
                        line += " "
                else:
                    # Lower half (positive row means visual bottom = negative amplitude)
                    threshold = -row_from_center
                    if norm_min <= threshold:
                        intensity = min(8, int((threshold - norm_min + 1) / half_height * 8) + 4)
                        line += f"[blue]{BLOCK_CHARS[intensity]}[/blue]"
                    else:
                        line += " "

            lines.append(line)

        # Add time markers
        time_line = "[dim]0:00"
        time_line += " " * (width - 10)
        time_line += "END[/dim]"
        lines.append(time_line)

        return lines

    def _update_content(self, content: str) -> None:
        try:
            widget = self.app.query_one("#audio-content", Static)
            widget.update(content)
        except Exception:
            pass
