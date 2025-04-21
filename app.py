from pathlib import Path
import threading

from textual.app import App, ComposeResult
from textual.reactive import reactive
from textual.widgets import DirectoryTree, Header, Footer, Static, Input, Button
from textual.containers import Horizontal, Vertical
from textual.screen import Screen

from tools.audio_player import AudioPlayer
from tools.image_previewer import ImagePreviewer
from tools.fuzzy_search import FuzzySearchScreen

class HideableDirectoryTree(DirectoryTree):
    """A DirectoryTree that can include or exclude hidden items."""
    show_hidden: reactive[bool] = reactive(False)

    def filter_paths(self, paths, /):
        if self.show_hidden:
            return paths
        return [path for path in paths if not path.name.startswith(".")]

class RenameScreen(Screen):
    BINDINGS = [("escape", "app.pop_screen", "Cancel"), ("enter", "confirm", "Rename")]

    def compose(self) -> ComposeResult:
        yield Static("✏️  Rename File", classes="header")
        yield Input(placeholder="New filename", id="new_name")
        yield Button("Rename", id="do_rename")

    async def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "do_rename":
            new_name = self.query_one("#new_name", Input).value.strip()
            await self.app.rename_file(new_name)
            await self.app.pop_screen()

class MoveScreen(Screen):
    BINDINGS = [("escape", "app.pop_screen", "Cancel"), ("enter", "confirm", "Move")]

    def compose(self) -> ComposeResult:
        yield Static("📂  Move File", classes="header")
        yield Input(placeholder="Destination folder", id="dest_folder")
        yield Button("Move", id="do_move")

    async def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "do_move":
            dest = self.query_one("#dest_folder", Input).value.strip()
            await self.app.move_file(dest)
            await self.app.pop_screen()

class FileExplorer(App):
    CSS = """
    DirectoryTree, HideableDirectoryTree {
        width: 40%;
        border: round #666;
    }

    /* right‑hand panel */
    #preview_panel {
        width: 60%;
        border: round #444;
        padding: 1;
        layout: vertical;
    }

    /* button strip inside the preview panel */
    #preview_actions {
        height: 3;
        padding-bottom: 1;
        content-align: center middle;
    }

    /* the actual preview box */
    #preview {
        height: auto;
        overflow: auto;
    }
    """

    SCREENS = {
        "fuzzy_search": FuzzySearchScreen,
        "rename":       RenameScreen,
        "move":         MoveScreen,
    }

    BINDINGS = [
        ("escape", "reset_root","Go Home"),
        ("/", "push_search",    "Search Files"),
        ("h", "toggle_hidden",  "Show/Hide Hidden"),
        ("p", "play_audio",     "Play/Stop Audio"),
        ("+", "increase_size",  "Increase Preview Size"),
        ("-", "decrease_size",  "Decrease Preview Size"),
        ("=", "increase_size",  "Increase Preview Size"),
        ("_", "decrease_size",  "Decrease Preview Size"),
    ]

    # Reactive attributes for preview size
    preview_width  = reactive(100, recompose=False, init=False)
    preview_height = reactive(50,  recompose=False, init=False)
    SIZE_STEP_WIDTH  = 20
    SIZE_STEP_HEIGHT = 10
    MIN_WIDTH   = 20
    MIN_HEIGHT  = 10

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_file: Path | None = None
        self.player = AudioPlayer()
        self.previewer = ImagePreviewer(max_width=self.preview_width, max_height=self.preview_height)
        self.last_played: Path | None = None

    # Update previewer dimensions
    def watch_preview_width(self, new_width: int) -> None:
        self.previewer.max_width = new_width
        self._refresh_preview()

    def watch_preview_height(self, new_height: int) -> None:
        self.previewer.max_height = new_height
        self._refresh_preview()

    def _refresh_preview(self) -> None:
        if self.current_file and self.current_file.is_file():
            ext = self.current_file.suffix.lower()
            preview = self.query_one("#preview", Static)
            if ext in ('.png', '.jpg', '.jpeg', '.bmp', '.gif'):
                try:
                    preview.update(self.previewer.rich_preview(str(self.current_file)))
                except Exception:
                    preview.update(self.previewer.ascii_preview(str(self.current_file)))

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)

        with Horizontal():
            # ─── left: directory tree
            yield HideableDirectoryTree(Path.home(), id="tree")

            # ─── right: preview panel with its own buttons
            with Vertical(id="preview_panel"):
                with Horizontal(id="preview_actions"):
                    yield Button("Rename", id="rename_btn")
                    yield Button("Move",   id="move_btn")

                yield Static("Select a file to preview its contents", id="preview")

        yield Footer()

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "rename_btn":
            await self.push_screen("rename")
        elif event.button.id == "move_btn":
            await self.push_screen("move")
        else:
            await super().on_button_pressed(event)

    def on_directory_tree_file_selected(self, event) -> None:
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
                    preview.update(filepath.read_text(encoding="utf-8")[:10000])
                except Exception as e:
                    preview.update(f"Error reading file: {e}")
        else:
            preview.update("<directory>")

    def action_play_audio(self) -> None:
        preview = self.query_one("#preview", Static)
        if (
            not self.current_file 
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
        await self.push_screen("fuzzy_search")

    def jump_to_path(self, path_str: str) -> None:
        tree = self.query_one("#tree", HideableDirectoryTree)
        tree.path = Path(path_str).parent

    def action_reset_root(self) -> None:
        tree = self.query_one("#tree", HideableDirectoryTree)
        tree.path = Path.home()
        self.query_one("#preview", Static).update("Select a file to preview its contents")
        self.current_file = None
        self.last_played  = None

    async def action_toggle_hidden(self) -> None:
        tree = self.query_one("#tree", HideableDirectoryTree)
        tree.show_hidden = not tree.show_hidden
        await tree.reload()

    def action_increase_size(self) -> None:
        self.preview_width  += self.SIZE_STEP_WIDTH
        self.preview_height += self.SIZE_STEP_HEIGHT

    def action_decrease_size(self) -> None:
        self.preview_width  = max(self.MIN_WIDTH, self.preview_width - self.SIZE_STEP_WIDTH)
        self.preview_height = max(self.MIN_HEIGHT, self.preview_height - self.SIZE_STEP_HEIGHT)

    # ─── File operations ─────────────────────────────────
    async def rename_file(self, new_name: str) -> None:
        if not self.current_file:
            return
        old = self.current_file
        target = old.with_name(new_name)
        old.rename(target)
        self.current_file = target
        tree = self.query_one("#tree", HideableDirectoryTree)
        tree.path = target.parent
        self.query_one("#preview", Static).update(f"Renamed to {target.name}")
        await tree.reload()

    async def move_file(self, dest_folder: str) -> None:
        if not self.current_file:
            return
        old = self.current_file
        dest = Path(dest_folder) / old.name
        old.rename(dest)
        self.current_file = dest
        tree = self.query_one("#tree", HideableDirectoryTree)
        tree.path = dest.parent
        self.query_one("#preview", Static).update(f"Moved to {dest}")
        await tree.reload()

if __name__ == "__main__":
    FileExplorer().run()
