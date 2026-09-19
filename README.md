# Framegrid video

Reuse the approved horizontal v7 animation with small text, timing and image changes. The revised export is v8; the original v7 is preserved.

## Everyday use

1. Double-click **start-editor.cmd**. Keep its command window open.
2. Change durations in seconds. **Show inputs** is the pause before a transformation, **Reveal result** is the transition itself, and **Hold result** is the pause afterwards. Larger values make that phase longer.
3. Open **Video text** to change wording. Use short phrases. Wording baked into source images (such as poster titles) requires editing or replacing the image.
4. Click **Save & render video**. Wait for “Render complete”. The player then shows the new export.
5. Find the finished video in **Videos/framegrid_main_horizontal_v8.mp4**.

Turn on **Show timing information** below the player to identify the current scene, phase and matching setting. Scene buttons jump to that part. The information panel sits below the video without covering it. The panel and playback-speed menu affect the preview only; the normal MP4 is clean. The player always describes the last rendered video, not unsaved edits.

**Save settings** saves without rendering. Alternatively, edit `timings.json` and `content.json` in a text editor, then double-click **render-video.cmd**. Close/reopen the editor after editing JSON externally. Every successful render replaces v8, so copy it elsewhere first if you want to keep a variant. Failed renders retain the previous MP4. The video is silent.

## Images and local dependencies

`assets.json` maps images to files and crops. `project.json` points to the existing `../framegrid-video-prototype` folder; keep that folder in place. This repository saves the generator code and settings, while reusing those local images. If you move the folders, update `asset_root` in `project.json` to the prototype folder's absolute path.

For a simple replacement, use an image with similar proportions and update its path in `assets.json`. Existing mappings may include crop operations: they are specific to the original images. Ask an AI agent to handle new proportions, crops, input/result matching, or animation/layout changes, and inspect the result before using it.

## GitHub setup

This is a separate local Git repository. It has no GitHub Actions or application deployment configuration. Generated videos, installed packages and render logs are excluded. After creating an empty GitHub repository, run these commands from this folder, substituting your own repository URL:

```powershell
git remote add origin https://github.com/YOUR-ACCOUNT/YOUR-REPOSITORY.git
git push -u origin main
```

For later changes: `git add .`, `git commit -m "Update video"`, then `git push`. This saves source/settings, not MP4s or the external image library. A clone needs that library and its path configured before rendering.

## One-time setup on another Windows computer

Use Python 3.11 or newer and the existing image library. In this folder:

```powershell
py -3.11 -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
```

The launchers prefer `.venv`; otherwise they use the existing Codex Python runtime. This computer also has the encoder installed in `.packages`. Fonts use Windows Segoe UI. Rendering needs no model API, AI credits or internet connection after dependencies are installed.

For an MP4 with the timing overlay burned in, run `film.py --render --demo` using the configured Python. This writes a separate demo file; the ordinary export stays clean.
