import os
from fuzzywuzzy import fuzz
from textual.screen import Screen
from textual.widgets import Input, Button, ListView, ListItem, Static
from textual.reactive import reactive

class FuzzySearchScreen(Screen):
    BINDINGS = [
        ("escape", "app.pop_screen", "Back"),
        ("enter", "do_search", "Search"),
    ]

    threshold: reactive[int] = reactive(50)

    def compose(self):
        yield Static("🔍  Fuzzy File Search", classes="header")
        yield Input(placeholder="Search query (blank = exact match)", id="query_input")
        yield Input(placeholder="File types (e.g. .py .txt, blank = all)", id="types_input")
        yield Input(placeholder="Root directory (blank = /)", id="root_input")
        yield Button(label="Search", id="search_btn")
        yield ListView(id="results_view")

    async def on_button_pressed(self, event):
        if event.button.id == "search_btn":
            await self.perform_search()

    async def action_do_search(self):
        await self.perform_search()

    async def perform_search(self):
        query     = self.query_one("#query_input", Input).value.strip().lower()
        types_txt = self.query_one("#types_input",  Input).value.strip()
        root_val  = self.query_one("#root_input",   Input).value.strip()
        root      = root_val or "/"

        exts = types_txt.split() if types_txt else []
        view = self.query_one("#results_view", ListView)
        view.clear()

        for dirpath, _, filenames in os.walk(root):
            for fname in filenames:
                if exts and not any(fname.lower().endswith(ext.lower()) for ext in exts):
                    continue
                full = os.path.join(dirpath, fname)
                score = fuzz.token_sort_ratio(query, fname.lower()) if query else 100
                if score >= self.threshold:
                    item = ListItem(Static(f"{fname} — {dirpath}"))
                    item.data = full
                    view.append(item)

        if not view.children:
            view.append(ListItem(Static("[dim]No matches found.[/]")))

    async def on_list_view_selected(self, event):
        selected = event.item.data
        await self.app.pop_screen()
        # <-- call the App's method directly
        self.app.jump_to_path(selected)
