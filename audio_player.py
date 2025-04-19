import subprocess
from pathlib import Path
from threading import Lock

class AudioPlayer:
    """
    Simple audio playback for various formats using system utilities.
    Ensures only one audio process plays at a time by terminating previous playback.
    """

    def __init__(self, volume: int = 100):
        """
        :param volume: Volume level (0-100)
        """
        self.volume = max(0, min(volume, 100))
        self.process: subprocess.Popen | None = None
        self._lock = Lock()

    def play(self, file_path: str) -> None:
        """
        Play the given audio file, blocking until playback finishes.
        Stops any existing playback before starting.

        :param file_path: Path to the audio file
        :raises FileNotFoundError: If file does not exist
        :raises RuntimeError: If no suitable player is installed
        """
        path = Path(file_path)
        if not path.exists() or not path.is_file():
            raise FileNotFoundError(f"`{file_path}` not found or is not a file.")

        ext = path.suffix.lower()
        if ext == '.wav':
            cmd = ['aplay', str(path)]
        elif ext in ('.mp3', '.flac', '.ogg'):
            # mpg123 volume range: 0-32768
            mpg_vol = int(self.volume / 100 * 32768)
            cmd = ['mpg123', '-f', str(mpg_vol), str(path)]
        else:
            # fallback to ffplay (part of ffmpeg)
            cmd = [
                'ffplay', '-nodisp', '-autoexit', '-loglevel', 'quiet',
                '-volume', str(self.volume), str(path)
            ]

        try:
            with self._lock:
                # Stop previous playback if still running
                if self.process and self.process.poll() is None:
                    self.process.terminate()
                # Start new playback
                self.process = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            # Wait for playback to finish
            self.process.wait()
        except FileNotFoundError:
            raise RuntimeError(f"Required audio player not installed: {cmd[0]}")
