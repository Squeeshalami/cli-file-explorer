from pathlib import Path
from pdfminer.high_level import extract_text
from rich.console import RenderableType
from rich.markdown import Markdown

class PDFPreviewer:
    """
    Extracts text from the first page of a PDF and renders it:
     - as a Rich Markdown renderable (rich_preview)
     - as plain text (text_preview)
    """

    def __init__(self, max_pages: int = 2, max_chars: int = 5000):
        """
        :param max_pages: how many pages to pull (default 1)
        :param max_chars: truncate the extracted text to this length
        """
        self.max_pages = max_pages
        self.max_chars = max_chars

    def rich_preview(self, file_path: str) -> RenderableType:
        """
        Returns a rich.markdown.Markdown object for the first page,
        truncated to max_chars.
        """
        text = self._extract_text(file_path)
        snippet = text[: self.max_chars]
        # wrap in a markdown code block (so PDF text shows in a scrollable block)
        md = Markdown(f"```\n{snippet}\n```")
        return md

    def text_preview(self, file_path: str) -> str:
        """
        Returns plain text (first page only), truncated.
        """
        text = self._extract_text(file_path)
        return text[: self.max_chars]

    def _extract_text(self, file_path: str) -> str:
        path = Path(file_path)
        if not path.exists() or not path.is_file():
            raise FileNotFoundError(f"PDF not found: {file_path}")
        # extract_text returns a string of all pages; maxpages limits it
        text = extract_text(str(path), maxpages=self.max_pages)
        return text or "[No text found on first page]"
