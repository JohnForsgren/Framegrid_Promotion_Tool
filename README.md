# Framegrid Promotion Tool

A reusable Windows tool for making small text, timing and image changes to the current Framegrid horizontal promotional video. It preserves the established six-example animation and exports a silent 1920×1080 MP4.

Repository: https://github.com/JohnForsgren/Framegrid_Promotion_Tool

## Local location

Moved on 2026-10-20 from Documents/ChatGPT/Framegrid Local Assistant into the Framegrid application's tools/framegrid-video folder. Double-click start-editor.cmd here to open the editor. Required image library moved alongside it to tools/framegrid-video-prototype; project.json needs no path change. Keep both folders together.

This tool retains its separate Git repository, original history and GitHub remote (Framegrid_Promotion_Tool). The selected video was already renamed locally before relocation. Routine rendering still writes Videos/framegrid_main_horizontal_v8.mp4.

## Current video

The latest selected export is `Saved-Videos/Framegrid Promotional Video (2026-09-19).mp4`:

- 56.5 seconds
- 1920×1080 at 30 fps
- Silent
- Full decode and frame-count validation passed
- Ending: “Discover what is possible”

`Saved-Videos`, `Videos`, all media and installed packages are ignored. Keep selected exports locally and upload them to the Drive folder below; do not commit videos to either Git repository.

## Edit and render

1. Double-click `start-editor.cmd` and keep the command window open.
2. Adjust durations in seconds:
   - **Show inputs** controls how long the source images remain on screen before the transformation.
   - **Reveal result** controls the transformation duration.
   - **Hold result** controls how long the completed result remains visible.
3. Expand **Video text** to change the on-screen wording. Keep replacement text reasonably short. Text already baked into an image, such as a poster title, cannot be changed here.
4. Click **Save & render video** and wait for “Render complete”.
5. Review the result in the player or open `Videos/framegrid_main_horizontal_v8.mp4`.
6. When you want to keep that version, copy it into `Saved-Videos` with a useful filename, then upload it to the designated Drive media folder.

**Save settings** stores text and timing changes without rendering. A successful render replaces the current file in `Videos`; a failed render leaves the previous MP4 intact.

## Review timing without covering the video

Enable **Show timing information · below video** to display the current scene, phase, elapsed time and matching `timings.json` setting below the player. The scene buttons jump directly to each part of the exported video. The information panel and playback-speed control affect only the preview; the normal exported MP4 remains clean.

The player and timing panel describe the last successful export. If settings have changed since that export, the editor reports that a new render is needed.

## Files you may edit directly

- `content.json` — all editable on-screen wording.
- `timings.json` — opening, chapter phases, illustrated example and ending durations.
- `assets.json` — image paths and crop definitions.
- `project.json` — location of the external image library.

After editing JSON while the browser editor is open, reload the editor before continuing. You can also double-click `render-video.cmd` to render directly from the JSON files.

Simple image replacements should use roughly the same proportions as the original. Different dimensions, crops, input/result pairings or layout changes should be handled with an AI coding agent and visually reviewed afterward.

## Image dependency

The generator currently reuses images from the neighboring folder:

```text
../framegrid-video-prototype
```

Keep that folder in place. If it moves, change `asset_root` in `project.json`. The selected MP4 in `Saved-Videos` can be downloaded and watched without this dependency, but rendering a new video requires the external image library.

## Git workflow

The GitHub remote is already configured. For later changes:

```powershell
git add .
git commit -m "Describe the update"
git push
```

Tracked content includes generator source, settings and documentation only. Selected exports, routine outputs, previews, logs and installed packages are ignored. The parent application ignores this independent repository; push changes from this folder separately.

## Setup on another Windows computer

Install Python 3.11 or newer, place the external image library beside this repository, and run:

```powershell
py -3.11 -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
```

The launchers prefer `.venv`. On the original Codex computer they can fall back to the bundled Codex Python runtime. Rendering uses Windows Segoe UI fonts and requires no model API, AI credits or internet connection once dependencies are installed.

For a separate MP4 with timing information burned into the picture, run `film.py --render --demo` with the configured Python. This does not replace the normal clean export.

## Media and creative direction (October 20, 2026)

Final promotional images/videos: keep locally and upload to https://drive.google.com/drive/folders/1NRObjKSDmUjcad51F7hIfiuVsL0Xv4uy (Framegrid Promotional-related files). Existing source/selected-master library: https://drive.google.com/drive/folders/1zW4vbxRawIcOOmOZnz0cG7AEn5vjl2bA . See ../PROMOTION-PROJECTS.md for checkout restoration and repository boundaries. This supersedes old instructions to commit selected MP4s.

The owner now prioritizes large visuals, minimal copy, clear website CTA and smoother purposeful animation. This older six-example composition is a reusable tool, not the required direction. The imported Windows launchers retain their existing Python/runtime assumptions; no new Windows environment is authorized by this import. Framegrid coding agents follow the repository's existing WSL/venv-linux policy.
