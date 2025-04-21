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
        yield Static("✏️  Rename File", classes="header")
        yield Input(placeholder="New filename", id="new_name")
        yield Button("Rename", id="do_rename")

    async def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "do_rename":
            new_name = self.query_one("#new_name", Input).value.strip()
            await self.app.rename_file(new_name) # Assumes app has rename_file
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
            await self.app.move_file(dest) # Assumes app has move_file
            await self.app.pop_screen()

class DeleteConfirmScreen(Screen):
    BINDINGS = [("escape", "app.pop_screen", "Cancel")]

    def compose(self) -> ComposeResult:
        file = self.app.file_to_delete # Assumes app has file_to_delete
        name = file.name if file else ""
        yield Static("⚠️  Confirm Delete", classes="header")
        yield Static(f"Delete {name}?", id="file_name")
        with Horizontal(id="confirm_actions"):
            yield Button("Yes", id="confirm_yes")
            yield Button("No",  id="confirm_no")

    async def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "confirm_yes":
            await self.app.delete_file_confirmed() # Assumes app has delete_file_confirmed
        await self.app.pop_screen() 