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
    ".html": "html",
    ".css":  "css",
    ".java": "java",
    ".c":    "c",
    ".cpp":  "cpp",
    ".cs":   "csharp",
    ".csproj": "xml",
    ".go":   "go",
    ".lua":  "lua",
    ".swift": "swift",
    ".kt":   "kotlin",
    ".rb":   "ruby",
    ".php":  "php",
    ".json": "json",
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
    ".rs":   "rust",
    ".dart": "dart",
    ".ps1":  "powershell",
    ".psm1": "powershell",
    ".bat":  "batch",
    ".gitignore": "gitignore",
    ".gitconfig": "gitconfig",
    ".gitmodules": "gitmodules",
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
