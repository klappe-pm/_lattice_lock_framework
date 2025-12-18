from typing import Any, Optional
import json
from rich.console import Console
from rich.theme import Theme
from rich.panel import Panel
from rich.table import Table
from rich import box

# Design-compliant theme
custom_theme = Theme(
    {
        "info": "cyan",
        "warning": "yellow",
        "error": "bold red",
        "success": "spring_green1",
        "muted": "grey50",
    }
)

class LatticeConsole:
    def __init__(self):
        self._console = Console(theme=custom_theme)
        self._json_mode = False
        self._verbose = False

    def set_json_mode(self, enabled: bool) -> None:
        self._json_mode = enabled
        if enabled:
            self._console = Console(quiet=True)  # Silence rich output in JSON mode

    def set_verbose(self, enabled: bool) -> None:
        self._verbose = enabled

    @property
    def internal_console(self) -> Console:
        return self._console

    def print(self, *args, **kwargs):
        if not self._json_mode:
            self._console.print(*args, **kwargs)

    def success(self, message: str):
        if not self._json_mode:
            self._console.print(f"[success]✔[/] {message}")

    def info(self, message: str):
        if not self._json_mode:
            self._console.print(f"[info]ℹ[/] {message}")

    def warning(self, message: str):
        if not self._json_mode:
            self._console.print(f"[warning]⚠ {message}[/]")

    def error(self, title: str, message: str, suggestion: Optional[str] = None):
        """Standardized error panel."""
        if self._json_mode:
             # In JSON mode, we might want to print a JSON error object, 
             # but usually the command logic handles the final JSON response.
             # This method is primarily for human-readable output.
             return

        content = f"{message}"
        if suggestion:
            content += f"\n\n[dim]Suggestion: {suggestion}[/]"
        
        panel = Panel(
            content,
            title=f"[error]{title}[/]",
            border_style="red",
            expand=False
        )
        self._console.print(panel)

    def print_json(self, data: Any):
        """Always prints JSON to stdout, regardless of mode, but usually used when json_mode is True."""
        # We use strict print here to ensure it goes to stdout even if console is quieted
        print(json.dumps(data, indent=2))

console = LatticeConsole()

def get_console() -> LatticeConsole:
    """Get the global console wrapper."""
    return console
