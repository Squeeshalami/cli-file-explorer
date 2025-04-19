# SSH File Explorer

A **terminal‑based file explorer** built with [Textual](https://github.com/Textualize/textual), designed for headless Raspberry Pi (or any Linux) over SSH. Browse directories in a collapsible tree, preview files (text, images, audio), and run fuzzy search from the comfort of your terminal.

---

## Features

- **Directory Tree**  
  Navigate your filesystem in a collapsible tree view.

- **File Previews**  
  - **Text files:** view the first 10 000 characters.  
  - **Image files:** render pixel‑based thumbnails via `rich_pixels`, with an ASCII fallback.  
  - **Audio files:** play/stop with `p` using `aplay`/`mpg123`/`ffplay` under the hood.

- **Fuzzy Search** (`/`)  
  Instantly search your entire filesystem (or a subdirectory) by filename, with optional extension filtering.

- **Hidden Files Toggle** (`h`)  
  Show or hide dot‑files and dot‑folders in the tree.

- **Go Home** (`Esc`)  
  Reset the tree back to your home directory and clear the preview.

- **Theming**  
  Pick a built‑in or custom [Textual theme](https://textual.textualize.io/themes/) by setting `self.theme` in code.

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

