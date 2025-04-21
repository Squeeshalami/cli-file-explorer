# app.py

from pathlib import Path
import threading

from textual.app import App, ComposeResult
from textual.reactive import reactive
from textual.widgets import DirectoryTree, Header, Footer, Static, Input, Button
from textual.containers import Horizontal, Vertical
from textual.screen import Screen

from rich.syntax import Syntax

from tools.audio_player import AudioPlayer
from tools.image_previewer import ImagePreviewer
from tools.video_thumbnail import VideoThumbnailer
from tools.fuzzy_search import FuzzySearchScreen
from tools.utils import LANGUAGE_MAP
class HideableDirectoryTree(DirectoryTree):
    show_hidden: reactive[bool] = reactive(False)

    def filter_paths(self, paths, /):
        if self.show_hidden:
            return paths
        return [p for p in paths if not p.name.startswith(".")]

class RenameScreen(Screen):
    BINDINGS = [
        ("escape", "app.pop_screen", "Cancel"),
        ("enter",  "confirm",        "Rename"),
    ]

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
    BINDINGS = [
        ("escape", "app.pop_screen", "Cancel"),
        ("enter",  "confirm",        "Move"),
    ]

    def compose(self) -> ComposeResult:
        yield Static("📂  Move File", classes="header")
        yield Input(placeholder="Destination folder", id="dest_folder")
        yield Button("Move", id="do_move")

    async def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "do_move":
            dest = self.query_one("#dest_folder", Input).value.strip()
            await self.app.move_file(dest)
            await self.app.pop_screen()

class DeleteConfirmScreen(Screen):
    BINDINGS = [("escape", "app.pop_screen", "Cancel")]

    def compose(self) -> ComposeResult:
        file = self.app.file_to_delete
        name = file.name if file else ""
        yield Static("⚠️  Confirm Delete", classes="header")
        yield Static(f"Delete {name}?", id="file_name")
        with Horizontal(id="confirm_actions"):
            yield Button("Yes", id="confirm_yes")
            yield Button("No",  id="confirm_no")

    async def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "confirm_yes":
            await self.app.delete_file_confirmed()
        await self.app.pop_screen()

class FileExplorer(App):
    CSS = """
    DirectoryTree, HideableDirectoryTree {
      width: 40%;
      border: round #666;
    }

    #preview_panel {
      width: 60%;
      border: round #444;
      padding: 1;
      layout: vertical;
      content-align: left top;
    }

    /* action buttons stay at top */
    #preview_actions {
      padding-bottom: 1;
      content-align: center middle;
    }
    #preview_actions > Button {
      padding: 0 2;
      margin: 0 1;
      content-align: center middle;
      border: none;
    }

    /* scrollable area under buttons */
    #preview_scroll {
      height: 1fr;
      overflow-y: auto;
    }

    /* the actual preview content */
    #preview {
      height: auto;
    }

    #confirm_actions {
      padding-top: 1;
      content-align: center middle;
    }
    """

    SCREENS = {
        "fuzzy_search":   FuzzySearchScreen,
        "rename":         RenameScreen,
        "move":           MoveScreen,
        "confirm_delete": DeleteConfirmScreen,
    }

    BINDINGS = [
        ("p",      "play_audio",    "Play/Stop Audio"),
        ("/",      "push_search",   "Search Files"),
        ("escape","reset_root",     "Go Home"),
        ("h",      "toggle_hidden", "Show/Hide Hidden"),
        ("+",      "increase_size", "Increase Preview Size"),
        ("-",      "decrease_size", "Decrease Preview Size"),
        ("=",      "increase_size", "Increase Preview Size"),
        ("_",      "decrease_size", "Decrease Preview Size"),
    ]

    preview_width   = reactive(100, recompose=False, init=False)
    preview_height  = reactive(50,  recompose=False, init=False)
    SIZE_STEP_WIDTH  = 20
    SIZE_STEP_HEIGHT = 10
    MIN_WIDTH       = 20
    MIN_HEIGHT      = 10


    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_file:   Path | None = None
        self.file_to_delete: Path | None = None
        self.player = AudioPlayer()
        self.previewer = ImagePreviewer(max_width=self.preview_width, max_height=self.preview_height)
        self.video_preview = VideoThumbnailer(max_width=self.preview_width, max_height=self.preview_height)
        self.last_played:   Path | None = None
        self.LANGUAGE_MAP = LANGUAGE_MAP
    def watch_preview_width(self, new_width: int) -> None:
        self.previewer.max_width = new_width
        self.video_preview.max_width = new_width
        self._refresh_preview()

    def watch_preview_height(self, new_height: int) -> None:
        self.previewer.max_height = new_height
        self.video_preview.max_height = new_height
        self._refresh_preview()

    def action_increase_size(self) -> None:
        self.preview_width  += self.SIZE_STEP_WIDTH
        self.preview_height += self.SIZE_STEP_HEIGHT

    def action_decrease_size(self) -> None:
        self.preview_width  = max(self.MIN_WIDTH,  self.preview_width  - self.SIZE_STEP_WIDTH)
        self.preview_height = max(self.MIN_HEIGHT, self.preview_height - self.SIZE_STEP_HEIGHT)

    async def action_push_search(self) -> None:
        await self.push_screen("fuzzy_search")

    def action_play_audio(self) -> None:
        preview = self.query_one("#preview", Static)
        if not self.current_file or self.current_file.suffix.lower() not in ('.mp3','.wav','.flac','.ogg'):
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

    def _refresh_preview(self) -> None:
        if not self.current_file or not self.current_file.is_file():
            return

        ext = self.current_file.suffix.lower()
        preview = self.query_one("#preview", Static)

        if ext in ('.png','.jpg','.jpeg','.bmp','.gif'):
            try:
                preview.update(self.previewer.rich_preview(str(self.current_file)))
            except:
                preview.update(self.previewer.ascii_preview(str(self.current_file)))

        elif ext in ('.mp4','.mov','.mkv','.avi','.webm'):
            try:
                preview.update(self.video_preview.rich_preview(str(self.current_file)))
            except:
                preview.update(self.video_preview.ascii_preview(str(self.current_file)))

        elif ext in self.LANGUAGE_MAP:
            try:
                code = self.current_file.read_text(encoding="utf-8")
                syntax = Syntax(code, self.LANGUAGE_MAP[ext], line_numbers=True)
                preview.update(syntax)
            except:
                preview.update("No Preview Available")

        else:
            try:
                text = self.current_file.read_text(encoding="utf-8")
                preview.update(text)
            except:
                preview.update("No Preview Available")

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)

        with Horizontal():
            # file tree
            yield HideableDirectoryTree(Path.home(), id="tree")

            # preview panel
            with Vertical(id="preview_panel"):
                # scrollable region below
                with Vertical(id="preview_scroll"):
                    yield Static("Select a file to preview its contents", id="preview")
                
                # buttons at top
                with Horizontal(id="preview_actions"):
                    yield Button("Rename", id="rename_btn")
                    yield Button("Move",   id="move_btn")
                    yield Button("Delete", id="delete_btn")


        yield Footer()

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "rename_btn":
            await self.push_screen("rename")
        elif event.button.id == "move_btn":
            await self.push_screen("move")
        elif event.button.id == "delete_btn":
            self.file_to_delete = self.current_file
            if self.file_to_delete:
                await self.push_screen("confirm_delete")

    async def delete_file_confirmed(self) -> None:
        if not self.file_to_delete:
            return
        path = self.file_to_delete
        preview = self.query_one("#preview", Static)
        try:
            if path.is_file():
                path.unlink()
            elif path.is_dir():
                path.rmdir()
        except Exception as e:
            preview.update(f"[red]Failed to delete {path.name}: {e}[/]")
            return

        self.current_file   = None
        self.file_to_delete = None
        tree = self.query_one("#tree", HideableDirectoryTree)
        await tree.reload()
        preview.update("Deleted. Select a file to preview its contents.")

    def on_directory_tree_file_selected(self, event) -> None:
        self.current_file = Path(event.path)
        self._refresh_preview()

    async def action_reset_root(self) -> None:
        tree = self.query_one("#tree", HideableDirectoryTree)
        tree.path = Path.home()
        self.query_one("#preview", Static).update("Select a file to preview its contents")
        self.current_file = None
        self.last_played  = None

    async def action_toggle_hidden(self) -> None:
        tree = self.query_one("#tree", HideableDirectoryTree)
        tree.show_hidden = not tree.show_hidden
        await tree.reload()

if __name__ == "__main__":
    FileExplorer().run()
