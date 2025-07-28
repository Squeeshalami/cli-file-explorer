from pathlib import Path
from rich.console import RenderableType
from PIL import Image
import io
try:
    import cairosvg
    CAIROSVG_AVAILABLE = True
except ImportError:
    CAIROSVG_AVAILABLE = False

from .image_previewer import ImagePreviewer

class SVGPreviewer:
    """
    Render SVG files by converting them to PNG and using the existing ImagePreviewer.
    Falls back to showing SVG source code if cairosvg is not available.
    """
    def __init__(self, max_width: int = 1000, max_height: int = 1000):
        self.max_width = max_width
        self.max_height = max_height
        self.image_previewer = ImagePreviewer(max_width, max_height)

    def rich_preview(self, file_path: str) -> RenderableType:
        """
        Convert SVG to PNG and use ImagePreviewer to display it.
        """
        if not CAIROSVG_AVAILABLE:
            raise ImportError("cairosvg not available")
            
        path = Path(file_path)
        if not path.exists() or not path.is_file():
            raise FileNotFoundError(f"SVG file not found: {file_path}")

        try:
            # Read SVG content
            svg_content = path.read_text(encoding="utf-8")
            
            # Convert SVG to PNG bytes
            png_bytes = cairosvg.svg2png(
                bytestring=svg_content.encode("utf-8"),
                output_width=self.max_width,
                output_height=self.max_height
            )
            
            # Create PIL Image from PNG bytes
            png_image = Image.open(io.BytesIO(png_bytes))
            
            # Use rich_pixels to display the PNG
            from rich_pixels import Pixels
            pixels = Pixels.from_image(png_image)
            return pixels
            
        except Exception as e:
            raise Exception(f"Failed to render SVG: {e}")

    def ascii_preview(self, file_path: str) -> str:
        """
        Fallback: Convert SVG to PNG and create ASCII art.
        """
        if not CAIROSVG_AVAILABLE:
            return self.text_preview(file_path)
            
        try:
            path = Path(file_path)
            svg_content = path.read_text(encoding="utf-8")
            
            # Use smaller dimensions for ASCII to keep it readable
            ascii_width = min(80, self.max_width // 10)
            ascii_height = min(40, self.max_height // 10)
            
            png_bytes = cairosvg.svg2png(
                bytestring=svg_content.encode("utf-8"),
                output_width=ascii_width * 2, 
                output_height=ascii_height * 2
            )
            
            # Create ASCII art using ImagePreviewer
            png_image = Image.open(io.BytesIO(png_bytes))
            
            # Convert to grayscale and create ASCII
            img = png_image.convert("L")
            img.thumbnail((ascii_width, ascii_height))
            
            ascii_chars = "@%#*+=-:. "
            output = []
            for y in range(img.height):
                row = []
                for x in range(img.width):
                    pixel = img.getpixel((x, y))
                    idx = pixel * (len(ascii_chars) - 1) // 255
                    row.append(ascii_chars[idx])
                output.append("".join(row))
            return "\n".join(output)
            
        except Exception:
            return self.text_preview(file_path)

    def text_preview(self, file_path: str) -> str:
        """
        Fallback: Show SVG source code as text.
        """
        try:
            path = Path(file_path)
            return path.read_text(encoding="utf-8")
        except Exception as e:
            return f"Error reading SVG file: {e}"
