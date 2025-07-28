from textual.app import ComposeResult
from textual.widgets import Static, Input, Button
from textual.containers import Horizontal
from textual.screen import Screen

class RenameScreen(Screen):
    BINDINGS = [
        ("escape", "app.pop_screen", "Cancel"),
        ("enter",  "confirm",        "Rename"),
    ]

    def compose(self) -> ComposeResult:
        yield Static("✏️  Rename", classes="header")
        yield Input(placeholder="New name", id="new_name")
        yield Button("Rename", id="do_rename")

    def on_show(self) -> None:
        """Populate the input with the current filename or directory name when the screen is shown."""
        new_name_input = self.query_one("#new_name", Input)
        # Use current_file if a file is selected, otherwise use current_dir for directory
        target = self.app.current_file if self.app.current_file else self.app.current_dir
        if target:
            # strip off any path, just the filename/directory name
            new_name_input.value = target.name
        new_name_input.focus()

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
        yield Static("📂  Move", classes="header")
        yield Input(placeholder="Destination folder", id="dest_folder")
        yield Button("Move", id="do_move")

    async def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "do_move":
            dest = self.query_one("#dest_folder", Input).value.strip()
            await self.app.move_file(dest)
            await self.app.pop_screen()


class CopyScreen(Screen):
    BINDINGS = [
        ("escape", "app.pop_screen", "Cancel"),
        ("enter",  "confirm",        "Copy"),
    ]

    def compose(self) -> ComposeResult:
        yield Static("📋  Copy", classes="header")
        yield Input(placeholder="Destination folder", id="dest_folder")
        yield Button("Copy", id="do_copy")

    async def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "do_copy":
            dest = self.query_one("#dest_folder", Input).value.strip()
            await self.app.copy_file(dest)
            await self.app.pop_screen()


class DeleteConfirmScreen(Screen):
    BINDINGS = [("escape", "app.pop_screen", "Cancel")]

    def compose(self) -> ComposeResult:
        file_or_dir = self.app.file_to_delete
        name = file_or_dir.name if file_or_dir else ""
        item_type = "directory" if file_or_dir and file_or_dir.is_dir() else "file"
        yield Static("⚠️  Confirm Delete", classes="header")
        yield Static(f"Delete {item_type} '{name}'?", id="file_name")
        with Horizontal(id="confirm_actions"):
            yield Button("Yes", id="confirm_yes")
            yield Button("No",  id="confirm_no")

    async def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "confirm_yes":
            await self.app.delete_file_confirmed()
        await self.app.pop_screen()


class NewFolderScreen(Screen):
    BINDINGS = [
        ("escape", "app.pop_screen", "Cancel"),
        ("enter",  "confirm",        "Create"),
    ]

    def compose(self) -> ComposeResult:
        yield Static("📁  Create New Folder", classes="header")
        yield Input(placeholder="Folder name", id="folder_name")
        yield Button("Create", id="do_create")

    async def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "do_create":
            name = self.query_one("#folder_name", Input).value.strip()
            if name:
                await self.app.create_folder(name)
            await self.app.pop_screen()
