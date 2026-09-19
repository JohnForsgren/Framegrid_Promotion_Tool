"""Local timing editor. Double-click start-editor.cmd; close its window to stop.

Save changes, then render to apply them to the exported video. Render output is
recorded in editor-render.log. Only the explicit routes below are served.
"""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import json
import math
import secrets
import subprocess
import sys
import threading
import webbrowser
from config import validate_content, load_content

ROOT = Path(__file__).resolve().parent
CONFIG = ROOT / 'timings.json'
VIDEO = ROOT / 'Videos' / 'framegrid_main_horizontal_v8.mp4'
CONTENT = ROOT / 'content.json'
TOKEN = secrets.token_urlsafe(32)
LOCK = threading.Lock()
STATE = {'running': False, 'message': 'Ready', 'revision': 0}


def validate(data):
    if not isinstance(data, dict) or set(data) != {'opening', 'chapters', 'references', 'prompt', 'result', 'closing'}:
        raise ValueError('Unexpected timing fields.')
    def seconds(value, low, high):
        if isinstance(value, bool) or not isinstance(value, (float, int)) or not math.isfinite(value) or not low <= value <= high:
            raise ValueError(f'Durations must be numbers between {low} and {high} seconds.')
        return float(value)
    out = {key: seconds(data[key], .5, 60) for key in ('opening', 'references', 'prompt', 'result', 'closing')}
    if not isinstance(data['chapters'], list) or len(data['chapters']) != 6:
        raise ValueError('Exactly six examples are required.')
    out['chapters'] = []
    for chapter in data['chapters']:
        if not isinstance(chapter, dict) or set(chapter) != {'input', 'reveal', 'hold'}:
            raise ValueError('Each example requires input, reveal and hold durations.')
        out['chapters'].append({key: seconds(chapter[key], .3, 30) for key in ('input', 'reveal', 'hold')})
    return out


def render():
    try:
        with (ROOT / 'editor-render.log').open('w', encoding='utf-8') as log:
            process = subprocess.run([sys.executable, '-u', str(ROOT / 'film.py'), '--render'], cwd=ROOT, stdout=log, stderr=subprocess.STDOUT)
        if process.returncode:
            tail = (ROOT / 'editor-render.log').read_text(encoding='utf-8', errors='replace')[-4000:]
            raise RuntimeError(f'Render exited with code {process.returncode}.\n{tail}')
        if not VIDEO.is_file():
            raise RuntimeError(f'Render finished but the video was not found at {VIDEO}')
        with LOCK:
            STATE.update(running=False, message='Render complete. Preview updated.', revision=STATE['revision'] + 1)
    except Exception as error:
        with LOCK:
            STATE.update(running=False, message=str(error)[-4500:])


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *_):
        pass

    def reply(self, status, body, content_type='application/json'):
        payload = json.dumps(body).encode() if content_type == 'application/json' else body
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(payload)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.end_headers()
        self.wfile.write(payload)

    def trusted_host(self):
        return self.headers.get('Host') == f'127.0.0.1:{self.server.server_port}'

    def do_GET(self):
        if not self.trusted_host():
            return self.reply(403, {'error': 'Invalid host'})
        route = self.path.split('?', 1)[0]
        if route == '/':
            return self.reply(200, (ROOT / 'editor.html').read_bytes(), 'text/html; charset=utf-8')
        if route == '/api/state':
            try:
                with LOCK:
                    snapshot = dict(STATE)
                    snapshot.update(timings=validate(json.loads(CONFIG.read_text(encoding='utf-8-sig'))), content=load_content(), token=TOKEN, video=VIDEO.is_file())
                    manifest = ROOT / 'output' / 'validation.json'
                    snapshot['exported'] = json.loads(manifest.read_text(encoding='utf-8')) if manifest.is_file() else None
                return self.reply(200, snapshot)
            except Exception as error:
                return self.reply(500, {'error': str(error)})
        if route == '/video':
            if not VIDEO.is_file():
                return self.reply(404, {'error': 'Render the video first.'})
            # Byte ranges allow the browser to seek without loading the full MP4.
            try:
                with VIDEO.open('rb') as source:
                    size = VIDEO.stat().st_size
                    start, end, status = 0, size - 1, 200
                    requested = self.headers.get('Range')
                    if requested:
                        import re
                        match = re.fullmatch(r'bytes=(\d+)-(\d*)', requested)
                        if not match:
                            return self.reply(416, {'error': 'Unsupported byte range'})
                        start = int(match[1])
                        end = min(int(match[2]), end) if match[2] else end
                        if start > end:
                            return self.reply(416, {'error': 'Invalid byte range'})
                        status = 206
                    self.send_response(status)
                    self.send_header('Content-Type', 'video/mp4')
                    self.send_header('Accept-Ranges', 'bytes')
                    self.send_header('Cache-Control', 'no-store')
                    self.send_header('Content-Length', str(end - start + 1))
                    if status == 206:
                        self.send_header('Content-Range', f'bytes {start}-{end}/{size}')
                    self.end_headers()
                    source.seek(start)
                    remaining = end - start + 1
                    while remaining:
                        chunk = source.read(min(1024 * 1024, remaining))
                        if not chunk:
                            break
                        self.wfile.write(chunk)
                        remaining -= len(chunk)
            except (BrokenPipeError, ConnectionResetError):
                pass
            return
        self.reply(404, {'error': 'Not found'})

    def do_POST(self):
        origin = f'http://127.0.0.1:{self.server.server_port}'
        if not self.trusted_host() or self.headers.get('Origin') != origin or not secrets.compare_digest(self.headers.get('X-Editor-Token', ''), TOKEN):
            return self.reply(403, {'error': 'Reload the editor and try again.'})
        if self.path not in ('/api/save', '/api/render'):
            return self.reply(404, {'error': 'Not found'})
        try:
            length = int(self.headers.get('Content-Length', '0'))
            if not 0 < length <= 64000:
                raise ValueError('Invalid request size.')
            payload = json.loads(self.rfile.read(length))
            if not isinstance(payload, dict) or set(payload) != {'timings', 'content'}:
                raise ValueError('Expected timing and text settings.')
            timings = validate(payload['timings'])
            content = validate_content(payload['content'])
            with LOCK:
                if STATE['running']:
                    return self.reply(409, {'error': 'Wait for the current render to finish.'})
                temporary = CONFIG.with_suffix('.tmp')
                temporary.write_text(json.dumps(timings, indent=2) + '\n', encoding='utf-8')
                temporary.replace(CONFIG)
                temporary = CONTENT.with_suffix('.tmp')
                temporary.write_text(json.dumps(content, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
                temporary.replace(CONTENT)
                if self.path == '/api/render':
                    STATE.update(running=True, message='Rendering… The existing video stays unchanged until the render completes.')
                    threading.Thread(target=render, daemon=True).start()
                else:
                    STATE['message'] = 'Text and timings saved. Render to update the exported video.'
            self.reply(200, {'ok': True})
        except (ValueError, OSError) as error:
            self.reply(400, {'error': str(error)})


if __name__ == '__main__':
    server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    url = f'http://127.0.0.1:{server.server_port}'
    print(f'Framegrid timing editor: {url}\nKeep this window open while editing or rendering. Press Ctrl+C to stop.', flush=True)
    if '--no-browser' not in sys.argv:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
