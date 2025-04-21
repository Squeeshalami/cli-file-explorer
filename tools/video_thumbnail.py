from pathlib import Path
import subprocess
import io

from PIL import Image
from rich_pixels import Pixels
from rich.console import RenderableType

class VideoThumbnailer:
    """
    Extract the first frame of a video and render it as:
     - a rich_pixels.Renderable (rich_preview)
     - an ASCII‐art string (ascii_preview)
    """

    def __init__(self,
                 max_width: int = 40,
                 max_height: int = 20,
                 ascii_chars: str = "@%#*+=-:. "):
        self.max_width = max_width
        self.max_height = max_height
        self.ascii_chars = ascii_chars

    def _get_frame(self, file_path: str) -> Image.Image:
        path = Path(file_path)
        if not path.exists() or not path.is_file():
            raise FileNotFoundError(f"Video not found: {file_path}")

        # Use ffmpeg to pull out frame 0 as PNG bytes on stdout
        cmd = [
            "ffmpeg", "-v", "error",
            "-ss", "0", "-i", str(path),
            "-frames:v", "1",
            "-f", "image2pipe", "-vcodec", "png", "pipe:1"
        ]
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        data = proc.stdout.read()
        proc.wait()

        img = Image.open(io.BytesIO(data))
        return img

    def rich_preview(self, file_path: str) -> RenderableType:
        """
        Returns a rich_pixels.Pixels object of the first frame,
        scaled to fit within (max_width, max_height).
        """
        img = self._get_frame(file_path)
        img.thumbnail((self.max_width, self.max_height))
        return Pixels.from_image(img)

    def ascii_preview(self, file_path: str) -> str:
        """
        Converts the first frame to grayscale ASCII art.
        """
        img = self._get_frame(file_path).convert("L")
        img.thumbnail((self.max_width, self.max_height))

        rows: list[str] = []
        for y in range(img.height):
            row_chars: list[str] = []
            for x in range(img.width):
                pixel = img.getpixel((x, y))
                idx = pixel * (len(self.ascii_chars) - 1) // 255
                row_chars.append(self.ascii_chars[idx])
            rows.append("".join(row_chars))

        return "\n".join(rows)
