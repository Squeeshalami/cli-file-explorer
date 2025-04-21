import inspect
from textual.app import App
from textual.theme import Theme
import themes  

LANGUAGE_MAP = {
    ".py":   "python",
    ".js":   "javascript",
    ".jsx":  "javascriptreact",
    ".ts":   "typescript",
    ".tsx":  "typescriptreact",
    ".java": "java",
    ".c":    "c",
    ".cpp":  "cpp",
    ".cs":   "csharp",
    ".csproj": "xml",
    ".lua":  "lua",
    ".go":   "go",
    ".swift": "swift",
    ".kt":   "kotlin",
    ".rb":   "ruby",
    ".php":  "php",
    ".json": "json",
    ".html": "html",
    ".css":  "css",
    ".md":   "markdown",
    ".txt":  "text",
    ".sh":   "bash",
    ".yaml": "yaml",
    ".yml":  "yaml",
    ".toml": "toml",
    ".xml":  "xml",
    ".csv":  "csv",
    ".jsonl": "jsonl",
    ".gd":   "gdscript",
    ".lock": "lock",
}


def register_custom_themes(app: App) -> None:
    """Dynamically finds and registers all Theme instances from the themes module."""
    custom_themes = []
    count = 0
    # Get all members of the themes module
    for name, obj in inspect.getmembers(themes):
        # Check if the member is a Theme instance
        if isinstance(obj, Theme):
            # Add the Theme instance to the list of custom themes
            custom_themes.append(obj)
    # Register each custom theme with the app
    for theme in custom_themes:
        app.register_theme(theme)
        count += 1

    if count > 0:
        print(f"Registered {count} themes dynamically.")
    else:
        print("No custom themes found in themes.py to register.")
