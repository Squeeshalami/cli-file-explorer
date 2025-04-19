# image_previewer.py
# Provides image renderable using rich_pixels and ASCII fallback

from pathlib import Path
from rich_pixels import Pixels
from rich.console import RenderableType
from PIL import Image

class ImagePreviewer:
    """
    Render image files in terminal via `rich_pixels` for color output,
    with an ASCII-art fallback.
    """
    def __init__(self, max_width: int = 40, max_height: int = 20, ascii_chars: str = "@%#*+=-:. "):
        self.max_width = max_width
        self.max_height = max_height
        self.ascii_chars = ascii_chars

    def rich_preview(self, file_path: str) -> RenderableType:
        """
        Return a Pixels renderable from rich_pixels, scaled to fit max dimensions.
        """
        path = Path(file_path)
        if not path.exists() or not path.is_file():
            raise FileNotFoundError(f"Image not found: {file_path}")
        with Image.open(path) as img:
            # Resize image preserving aspect ratio
            img.thumbnail((self.max_width, self.max_height))
            pixels = Pixels.from_image(img)
        return pixels

    def ascii_preview(self, file_path: str) -> str:
        """
        Convert the image to a grayscale ASCII-art string,
        resizing to (max_width x max_height) to fit terminal.
        """
        path = Path(file_path)
        if not path.exists() or not path.is_file():
            raise FileNotFoundError(f"Image not found: {file_path}")

        img = Image.open(path).convert("L")
        img.thumbnail((self.max_width, self.max_height))
        output = []
        for y in range(img.height):
            row = []
            for x in range(img.width):
                pixel = img.getpixel((x, y))
                idx = pixel * (len(self.ascii_chars) - 1) // 255
                row.append(self.ascii_chars[idx])
            output.append("".join(row))
        return "\n".join(output)

# Example usage:
# from rich.console import Console
# console = Console()
# previewer = ImagePreviewer(max_width=50,max_height=20)
# console.print(previewer.rich_preview("/path/to/image.png"))
# print(previewer.ascii_preview("/path/to/image.png"))
