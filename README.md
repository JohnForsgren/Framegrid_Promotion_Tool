# Framegrid Promotion Tool

A reusable Windows tool for making small text, timing and image changes to the current Framegrid horizontal promotional video. It preserves the established six-example animation and exports a silent 1920×1080 MP4.

Repository: https://github.com/JohnForsgren/Framegrid_Promotion_Tool

## Current video

The latest selected export is `Saved-Videos/framegrid_main_horizontal_v8.mp4`:

- 56.5 seconds
- 1920×1080 at 30 fps
- Silent
- Full decode and frame-count validation passed
- Ending: “Discover what is possible”

`Saved-Videos` is tracked by Git. Put videos there when you deliberately want to preserve and push them. The normal render folder, `Videos`, is ignored so repeated test renders do not fill the Git history.

## Edit and render

1. Double-click `start-editor.cmd` and keep the command window open.
2. Adjust durations in seconds:
   - **Show inputs** controls how long the source images remain on screen before the transformation.
   - **Reveal result** controls the transformation duration.
   - **Hold result** controls how long the completed result remains visible.
3. Expand **Video text** to change the on-screen wording. Keep replacement text reasonably short. Text already baked into an image, such as a poster title, cannot be changed here.
4. Click **Save & render video** and wait for “Render complete”.
5. Review the result in the player or open `Videos/framegrid_main_horizontal_v8.mp4`.
6. When you want to keep that version, copy it into `Saved-Videos` with a useful filename, then commit and push it.

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

Tracked content includes the generator, settings, documentation and selected exports in `Saved-Videos`. Routine outputs, previews, logs, installed packages and videos left in `Videos` are ignored.

## Setup on another Windows computer

Install Python 3.11 or newer, place the external image library beside this repository, and run:

```powershell
py -3.11 -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
```

The launchers prefer `.venv`. On the original Codex computer they can fall back to the bundled Codex Python runtime. Rendering uses Windows Segoe UI fonts and requires no model API, AI credits or internet connection once dependencies are installed.

For a separate MP4 with timing information burned into the picture, run `film.py --render --demo` with the configured Python. This does not replace the normal clean export.
