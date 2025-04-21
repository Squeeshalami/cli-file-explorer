# Terminal File Explorer

A **Terminal‑based file explorer** built with [Textual](https://github.com/Textualize/textual), originally designed for headless Raspberry Pi (or any Linux machine) over SSH. Browse directories in a collapsible tree, preview files (text, code, images, video, audio), perform file operations, and run fuzzy search all from the comfort of your terminal. The interface is fully function over SSH.

---

## Features

- **Directory Tree**  
  Navigate your filesystem in a collapsible tree view, with optional hiding of dot‑files and dot‑folders.

- **File Previews**  
  - **Text files** (`.txt`, `.log`, etc.)  
    View the **full contents** in a scrollable panel.  
  - **Code files** (`.py`, `.js`, `.ts`, `.java`, `.c`, `.cpp`, `.html`, `.css`, `.json`, `.md`, etc.)  
    Syntax‑highlighted (via Rich’s `Syntax`) with line numbers in your terminal.  
  - **Image files** (`.png`, `.jpg`, `.jpeg`, `.bmp`, `.gif`)  
    Pixel‑based thumbnails via `rich_pixels`, with an ASCII‑art fallback.  
  - **Video files** (`.mp4`, `.mov`, `.mkv`, `.avi`, `.webm`)  
    Displays the **first frame** as a thumbnail (or ASCII fallback) using `ffmpeg`.  
  - **Audio files** (`.mp3`, `.wav`, `.flac`, `.ogg`)  
    Press **`p`** to play/stop via `aplay`/`mpg123`/`ffplay`.

- **File Operations**  
  Buttons to **Rename**, **Move**, or **Delete** the currently selected file or empty folder.  
  Deletion is protected by a **confirmation dialog** to prevent accidents.

- **Fuzzy Search** (`/`)  
  Instantly search your filesystem (or any subdirectory) by filename, with optional extension filters.

- **Hidden Files Toggle** (`h`)  
  Show or hide all dot‑files and dot‑folders in the tree.

- **Go Home** (`Esc`)  
  Reset the tree back to your home directory and clear the preview.

- **Preview Resizing** (`+` / `=` to enlarge, `-` / `_` to shrink)  
  Dynamically adjust the maximum dimensions used when rendering images, video thumbnails, and ASCII previews.

- **Scrollable Preview Panel**  
  The preview area auto‑scrolls whenever the content exceeds the viewport, keeping action buttons always in view.

- **Theming**  
  Pick a built‑in or custom [Textual theme](https://textual.textualize.io/themes/) by setting `self.theme` in code.

---


## Key-Bind CheatSheet
```
'/'          "Search Files"
'esc'        "Go Home"
'h'          "Show/Hide Hidden"
'p'          "Play/Stop Audio"
'+' / '='    "Increase Preview Size"
'-' / '_'    "Decrease Preview Size"
```

---

## Installation with UV

More info on UV: https://docs.astral.sh/uv/getting-started/installation/

1. **Clone this repo**  
   ```bash
   git clone https://github.com/Squeeshalami/cli-file-explorer.git
   cd ssh-file-explorer
    ```
2. **Install Dependencies**
    ```
    uv sync 
    ```
3. **Run the App**
    ```
    uv run app.py 
    ```


## Installation with venv
1. **Clone this repo**  
   ```bash 
   git clone https://github.com/Squeeshalami/cli-file-explorer.git
   cd cli-file-explorer
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv venv

   # On Windows
   venv\Scripts\activate

   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   
   # Or install directly from pyproject.toml
   pip install .
   ```

4. **Run the App**
   ```bash
   python app.py
   ```
