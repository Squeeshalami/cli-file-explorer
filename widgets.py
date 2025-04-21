from pathlib import Path
from textual.reactive import reactive
from textual.widgets import DirectoryTree

class HideableDirectoryTree(DirectoryTree):
    show_hidden: reactive[bool] = reactive(False)

    def filter_paths(self, paths: list[Path]) -> list[Path]:
        if self.show_hidden:
            return paths
        return [p for p in paths if not p.name.startswith(".")] 