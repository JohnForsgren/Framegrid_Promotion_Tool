# Promotion editor status — October 20, 2026

Relocated to Framegrid app/tools/framegrid-video; independent repository remains https://github.com/JohnForsgren/Framegrid_Promotion_Tool on main. Parent app ignores this nested checkout. Generator source/config/docs are tracked; selected videos, all other media, installed packages and output remain local and ignored. Old commits may contain the former selected MP4; history is not rewritten. The renamed selected export remains at Saved-Videos/Framegrid Promotional Video (2026-09-19).mp4.

project.json resolves ../framegrid-video-prototype relative to the tool. All20 configured image-file paths were verified present after relocation. Existing Windows launchers/runtime/font assumptions remain; no new Python environment or render was executed during Git preparation. Earlier validation of the56.5s silent1920×1080 export and three workflow tests is historical, not a fresh render check.

editor.py/editor.html own the loopback text/timing UI; film.py owns render/export; simple_demo.py owns the illustrated ending; config.py validates copy/assets. Keep source images in place, avoid simultaneous renders and reload the editor after direct JSON changes.

Owner's October20 material-improvement task supersedes the old fixed six-example creative constraint. Prioritize larger visuals, minimal wording, an obvious website CTA and purposeful smooth animation. Final exports belong locally AND in Framegrid Promotional-related files: https://drive.google.com/drive/folders/1NRObjKSDmUjcad51F7hIfiuVsL0Xv4uy . Existing source/selected-master library: https://drive.google.com/drive/folders/1zW4vbxRawIcOOmOZnz0cG7AEn5vjl2bA . See ../PROMOTION-PROJECTS.md and Drive Visual Promotion & Video Handover for current directions and restoration caveats.
