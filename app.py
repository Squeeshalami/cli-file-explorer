# app.py

from pathlib import Path
import threading
from typing import Iterable

from textual.app import App, ComposeResult
from textual.reactive import reactive
from textual.widgets import DirectoryTree, Header, Footer, Static
from textual.containers import Horizontal

from audio_player import AudioPlayer
from image_previewer import ImagePreviewer
from fuzzy_search import FuzzySearchScreen

class HideableDirectoryTree(DirectoryTree):
    """A DirectoryTree that can include or exclude hidden items."""
    show_hidden: reactive[bool] = reactive(False)

    def filter_paths(self, paths: Iterable[Path]) -> Iterable[Path]:
        """
        Exclude any name starting with '.' unless show_hidden is True.
        """
        if self.show_hidden:
            return paths
        return [path for path in paths if not path.name.startswith(".")]

class FileExplorer(App):
    CSS = """
    DirectoryTree, HideableDirectoryTree {
        width: 40%;
        border: round #666;
    }
    Static {
        border: round #444;
        padding: 1;
    }
    """

    SCREENS = {
        "fuzzy_search": FuzzySearchScreen,
    }

    BINDINGS = [
        ("p", "play_audio", "Play/Stop Audio"),
        ("/", "push_search", "Search Files"),
        ("escape", "reset_root", "Go Home"),
        ("h", "toggle_hidden", "Show/Hide Hidden"),  # ← new binding
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_file: Path | None = None
        self.player = AudioPlayer()
        self.previewer = ImagePreviewer(max_width=40, max_height=20)
        self.last_played: Path | None = None


    def on_mount(self) -> None:
        self.theme = "gruvbox"
        
    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Horizontal():
            # Use our hideable tree here
            yield HideableDirectoryTree(Path.home(), id="tree")
            yield Static("Select a file to preview its contents", id="preview")
        yield Footer()

    def on_directory_tree_file_selected(self, event: DirectoryTree.FileSelected) -> None:
        """Preview audio, images, or text when a file is selected."""
        filepath = Path(event.path)
        self.current_file = filepath
        preview = self.query_one("#preview", Static)

        if filepath.is_file():
            ext = filepath.suffix.lower()
            if ext in ('.mp3', '.wav', '.flac', '.ogg'):
                preview.update(f"[audio file] {filepath.name}\nPress 'p' to play or stop.")
            elif ext in ('.png', '.jpg', '.jpeg', '.bmp', '.gif'):
                try:
                    preview.update(self.previewer.rich_preview(str(filepath)))
                except Exception:
                    preview.update(self.previewer.ascii_preview(str(filepath)))
            else:
                try:
                    text = filepath.read_text(encoding="utf-8")
                    preview.update(text[:10000])
                except Exception as e:
                    preview.update(f"Error reading file: {e}")
        else:
            preview.update("<directory>")

    def action_play_audio(self) -> None:
        """Toggle audio playback on the selected file with 'p'."""
        preview = self.query_one("#preview", Static)
        if (
            not self.current_file
            or not self.current_file.is_file()
            or self.current_file.suffix.lower() not in ('.mp3', '.wav', '.flac', '.ogg')
        ):
            preview.update("No audio file selected or unsupported format.")
            return

        if self.player.process and self.player.process.poll() is None and self.last_played == self.current_file:
            self.player.process.terminate()
            preview.update(f"Stopped: {self.current_file.name}")
            self.last_played = None
        else:
            self.last_played = self.current_file
            threading.Thread(
                target=self.player.play,
                args=(str(self.current_file),),
                daemon=True
            ).start()
            preview.update(f"Playing: {self.current_file.name}\nPress 'p' again to stop.")

    async def action_push_search(self) -> None:
        """Push the fuzzy‑search screen when '/' is pressed."""
        await self.push_screen("fuzzy_search")

    def jump_to_path(self, path_str: str) -> None:
        """Navigate the tree to the parent directory of a selected file."""
        tree = self.query_one("#tree", HideableDirectoryTree)
        tree.path = Path(path_str).parent

    def action_reset_root(self) -> None:
        """Reset the explorer back to the home directory when Esc is pressed."""
        tree = self.query_one("#tree", HideableDirectoryTree)
        tree.path = Path.home()
        preview = self.query_one("#preview", Static)
        preview.update("Select a file to preview its contents")
        self.current_file = None
        self.last_played = None

    async def action_toggle_hidden(self) -> None:
        """
        Toggle showing of hidden files/folders and reload the tree.
        """
        tree = self.query_one("#tree", HideableDirectoryTree)
        tree.show_hidden = not tree.show_hidden
        await tree.reload()  # refresh contents :contentReference[oaicite:1]{index=1}


if __name__ == "__main__":
    FileExplorer().run()
