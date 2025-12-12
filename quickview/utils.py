"""Utility functions for QuickView."""


def format_size(size: int) -> str:
    """Format file size in human readable format."""
    for unit in ["B", "KB", "MB", "GB"]:
        if size < 1024:
            return f"{size:.1f} {unit}" if unit != "B" else f"{size} {unit}"
        size /= 1024
    return f"{size:.1f} TB"


def escape_markup(text: str) -> str:
    """Escape Rich markup characters in text."""
    return text.replace("[", "\\[")
