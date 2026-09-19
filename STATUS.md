# Generator handover

Current export: `Videos/framegrid_main_horizontal_v8.mp4`, 56.5s silent, 1920×1080, 30fps, 1695 frames. Full decode passed. Four sampled pre-closing previews are pixel-identical to v7. Closing shows “Discover what is possible” with technology/guidance wording; final creative approval is the user's.

Start with README.md. `editor.py` serves loopback-only text/timing controls; `editor.html` derives its timing overlay from the exported snapshot, not unsaved inputs. `film.py` owns scenes, transitions, exports and validation. `simple_demo.py` owns the illustrated reference/prompt/result sequence. `config.py` validates copy and loads images. No historical renderer imports remain.

Inputs: `content.json`, `timings.json`, `assets.json`, `project.json`. Image library remains in neighboring `framegrid-video-prototype`; do not delete it. Existing asset crops are deliberate. Code changes must preserve the six-example layout unless requested. Application source remains read-only.

Verification: `test_workflow.py` passes three tests covering invalid duration/text rejection, HTTP save persistence and origin protection. All scene-boundary frames and demo-overlay frame rendered; editor save, scene jump, overlay and matching-export indicator checked in browser. `output/validation.json` stores the actual export inputs and timeline; demo uses a separate manifest. Browser preview overlays never appear in the normal MP4.

Runtime: launcher prefers .venv then bundled Codex Python; .packages holds imageio-ffmpeg. Sandboxed agent processes may require escalation to read the encoder install. Normal desktop launchers run as the user. Do not run multiple renderers against the same output concurrently. Direct JSON edits require an editor reload; avoid changing files during rendering.

Separate repository on main, local initial commit; no remote/public push. README gives setup/push commands. Ignore rules exclude videos, packages and generated previews/logs. Keep the authoritative Drive Visual Promotion & Video Handover current; avoid copying historical logs here.
