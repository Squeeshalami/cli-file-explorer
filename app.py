from pathlib import Path
import threading
import shutil

from textual.app import App, ComposeResult
from textual.reactive import reactive
from textual.widgets import DirectoryTree, Header, Footer, Static, Input, Button
from textual.containers import Horizontal, Vertical
from textual.screen import Screen

from rich.syntax import Syntax

from tools.audio_player import AudioPlayer
from tools.image_previewer import ImagePreviewer
from tools.video_thumbnail import VideoThumbnailer
from tools.pdf_previewer import PDFPreviewer
from tools.fuzzy_search import FuzzySearchScreen
from utils import LANGUAGE_MAP, register_custom_themes
from themes import *

from widgets import HideableDirectoryTree
from screens import RenameScreen, MoveScreen, DeleteConfirmScreen, NewFolderScreen, CopyScreen

DEFAULT_THEME = deep_space

class FileExplorer(App):
    CSS = """
    DirectoryTree, HideableDirectoryTree {
      width: 35%;
      border: round #666;
    }

    /* Preview Panel Styling */
    #preview_panel {
      width: 70%;
      height: 100%;
      border: round #444;
      padding: 1;
      layout: vertical;
      content-align: left top;
    }
    #preview_actions {
      padding-bottom: 1;
      content-align: center middle;
    }
    #preview_actions > Button {
      padding: 0 5;
      margin: 0 1;
      content-align: center middle;
      border: none;
    }
    #preview_scroll {
      height: 90%;
      overflow-y: auto;
    }
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
        "copy":           CopyScreen,
        "confirm_delete": DeleteConfirmScreen,
        "new_folder":     NewFolderScreen,
    }

    BINDINGS = [
        # Core Bindings
        ("/",      "push_search",   "Search"),
        ("escape", "reset_root",    "Go Home"),
        ("delete", "delete",        "Delete"),
        ("F",      "new_folder",    "New Folder"),
        ("h",      "toggle_hidden", "Show/Hide Hidden"),
        ("R",      "rename",        "Rename"),
        ("M",      "move",          "Move To"),
        ("C",      "copy",          "Copy To"),

        # Preview Bindings
        ("p",      "play_audio",    "Play/Stop Audio"),
        ("+",      "increase_size", "Img Size"),
        ("-",      "decrease_size", "Img Size"),

        # Redundant Bindings
        ("H",      "toggle_hidden", "Show/Hide Hidden"),
        ("=",      "increase_size", "Img Size"),
        ("_",      "decrease_size", "Img Size"),
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
        self.current_dir:    Path        = Path.home()
        self.file_to_delete: Path | None = None

        self.player = AudioPlayer()
        self.previewer = ImagePreviewer(max_width=self.preview_width,
                                        max_height=self.preview_height)
        self.video_preview = VideoThumbnailer(max_width=self.preview_width,
                                              max_height=self.preview_height)
        self.pdf_preview = PDFPreviewer(max_pages=1, max_chars=8000)
        self.last_played:   Path | None = None
        self.LANGUAGE_MAP = LANGUAGE_MAP

    def on_mount(self) -> None:
        register_custom_themes(self)
        self.theme = DEFAULT_THEME.name

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
        self.preview_width  = max(self.MIN_WIDTH,
                                  self.preview_width  - self.SIZE_STEP_WIDTH)
        self.preview_height = max(self.MIN_HEIGHT,
                                  self.preview_height - self.SIZE_STEP_HEIGHT)

    async def action_push_search(self) -> None:
        await self.push_screen("fuzzy_search")

    def action_play_audio(self) -> None:
        preview = self.query_one("#preview", Static)
        if (not self.current_file
            or self.current_file.suffix.lower() not in ('.mp3','.wav','.flac','.ogg')):
            preview.update("No audio file selected or unsupported format.")
            return
        if (self.player.process and self.player.process.poll() is None
            and self.last_played == self.current_file):
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

        elif ext == '.pdf':
            try:
                preview.update(self.pdf_preview.rich_preview(str(self.current_file)))
            except:
                preview.update(self.pdf_preview.text_preview(str(self.current_file)))

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
            yield HideableDirectoryTree(Path.home(), id="tree")

            with Vertical(id="preview_panel"):
                with Vertical(id="preview_scroll"):
                    yield Static("Select a file to preview its contents", id="preview")
                with Horizontal(id="preview_actions"):
                    yield Button("Rename", id="rename_btn")
                    yield Button("Move",   id="move_btn")
                    yield Button("Copy To", id="copy_btn")
                    yield Button("Delete", id="delete_btn")

        yield Footer()

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "rename_btn":
            await self.push_screen("rename")
        elif event.button.id == "move_btn":
            await self.push_screen("move")
        elif event.button.id == "copy_btn":
            await self.push_screen("copy")
        elif event.button.id == "delete_btn":
            if self.current_file:
                self.file_to_delete = self.current_file
            else:
                self.file_to_delete = self.current_dir
            await self.push_screen("confirm_delete")


    ## Delete File ##
    async def action_delete(self) -> None:
        if self.current_file:
            self.file_to_delete = self.current_file
        else:
            self.file_to_delete = self.current_dir
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

    ## Create Folder ##
    async def action_new_folder(self) -> None:
        await self.push_screen("new_folder")

    async def create_folder(self, name: str) -> None:
        parent = self.current_dir or Path.home()
        new_path = parent / name
        preview = self.query_one("#preview", Static)
        try:
            new_path.mkdir()
        except Exception as e:
            preview.update(f"[red]Failed to create folder {name}: {e}[/]")
        else:
            preview.update(f"[green]Created folder:[/] {new_path}")
            tree = self.query_one("#tree", HideableDirectoryTree)
            await tree.reload()

    ## Rename File ##
    async def action_rename(self) -> None:
        await self.push_screen("rename")

    async def rename_file(self, new_name: str) -> None:
        """Rename the currently selected file to `new_name`."""
        if not self.current_file:
            return
        old_path = self.current_file
        new_path = old_path.with_name(new_name)
        preview = self.query_one("#preview", Static)
        try:
            old_path.rename(new_path)
        except Exception as e:
            preview.update(f"[red]Rename failed: {e}[/]")
            return

        # Update state
        self.current_file = new_path
        self.current_dir  = new_path.parent

        # Refresh the tree and preview pane
        tree = self.query_one("#tree", HideableDirectoryTree)
        await tree.reload()
        self._refresh_preview()


    ## Move File ##
    async def action_move(self) -> None:
        await self.push_screen("move")

    async def move_file(self, dest_str: str) -> None:
        dest = Path(dest_str).expanduser()
        preview = self.query_one("#preview", Static)
        if not dest.is_dir():
            preview.update(f"[red]Destination not a directory: {dest}[/]")
            return
        try:
            shutil.move(str(self.current_file), str(dest / self.current_file.name))
        except Exception as e:
            preview.update(f"[red]Move failed: {e}[/]")
            return
        self.current_file = dest / self.current_file.name
        self.current_dir  = dest
        tree = self.query_one("#tree", HideableDirectoryTree)
        await tree.reload()
        self._refresh_preview()


    ## Copy File ##
    async def action_copy(self) -> None:
        await self.push_screen("copy")

    async def copy_file(self, dest_str: str) -> None:
        preview = self.query_one("#preview", Static)

        # Make sure a file is selected
        if not self.current_file:
            preview.update("[red]No file selected to copy.[/]")
            return

        # Resolve destination
        dest = Path(dest_str).expanduser()
        if not dest.is_dir():
            preview.update(f"[red]Destination not a directory: {dest}[/]")
            return

        # Perform the copy
        try:
            shutil.copy2(str(self.current_file),
                         str(dest / self.current_file.name))
        except Exception as e:
            preview.update(f"[red]Copy failed: {e}[/]")
            return

        # Reload the tree so you can immediately see the new file
        tree = self.query_one("#tree", HideableDirectoryTree)
        await tree.reload()
        preview.update(f"[green]Copied to:[/] {dest / self.current_file.name}")


    ## File Selected ##
    def on_directory_tree_file_selected(self, event) -> None:
        self.current_file = Path(event.path)
        self.current_dir  = self.current_file.parent
        self._refresh_preview()

    ## Directory Selected ##
    def on_directory_tree_directory_selected(self, event) -> None:
        self.current_file = None
        self.current_dir  = Path(event.path)
        self.query_one("#preview", Static).update(f"[bold]Directory:[/] {self.current_dir}")

    ## Reset Root ##
    async def action_reset_root(self) -> None:
        tree = self.query_one("#tree", HideableDirectoryTree)
        tree.path = Path.home()
        await tree.reload()
        self.query_one("#preview", Static).update("Select a file to preview its contents")
        self.current_file = None
        self.last_played  = None
        self.current_dir  = Path.home()

    ## Toggle Hidden ##
    async def action_toggle_hidden(self) -> None:
        tree = self.query_one("#tree", HideableDirectoryTree)
        tree.show_hidden = not tree.show_hidden
        await tree.reload()

    ## Jump to Path ##
    async def jump_to_path(self, path_str: str) -> None:
        target_path = Path(path_str)
        if target_path.is_file():
            self.current_file = target_path
            self.current_dir  = target_path.parent
            self._refresh_preview()
            try:
                tree = self.query_one(HideableDirectoryTree)
                tree.path = target_path.parent
                await tree.reload()
            except Exception as e:
                self.query_one("#preview", Static).update(f"[red]Error navigating tree: {e}[/]")
        else:
            self.query_one("#preview", Static).update(f"[red]Path not found or not a file: {path_str}[/]")

if __name__ == "__main__":
    FileExplorer().run()
