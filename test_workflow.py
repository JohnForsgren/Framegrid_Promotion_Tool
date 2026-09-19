"""Run with the same Python runtime as the editor. No video is overwritten."""
import copy
import json
import tempfile
import threading
import unittest
import urllib.request
import urllib.error
from pathlib import Path
from unittest.mock import patch
import editor
import config


class WorkflowTests(unittest.TestCase):
    def test_reject_bad_timings(self):
        valid = json.loads(editor.CONFIG.read_text())
        for value in (False, -1, float('nan'), float('inf'), 999):
            invalid = copy.deepcopy(valid)
            invalid['opening'] = value
            with self.assertRaises(ValueError):
                editor.validate(invalid)
        invalid = copy.deepcopy(valid)
        invalid['chapters'].pop()
        with self.assertRaises(ValueError):
            editor.validate(invalid)

    def test_reject_unrenderable_copy(self):
        for key, value in [('generate', 'A' * 80), ('demo_prompt', 'two\nlines')]:
            invalid = dict(config.CONTENT_DEFAULTS, **{key: value})
            with self.assertRaises(ValueError):
                config.validate_content(invalid)

    def test_editor_save_and_access_boundaries(self):
        original_timing = editor.CONFIG.read_bytes()
        original_content = editor.CONTENT.read_bytes()
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            timing = root / 'timings.json'
            content = root / 'content.json'
            timing.write_bytes(original_timing)
            content.write_bytes(original_content)
            with patch.object(editor, 'CONFIG', timing), patch.object(editor, 'CONTENT', content):
                server = editor.ThreadingHTTPServer(('127.0.0.1', 0), editor.Handler)
                thread = threading.Thread(target=server.serve_forever, daemon=True)
                thread.start()
                url = f'http://127.0.0.1:{server.server_port}'
                body = {'timings': json.loads(original_timing), 'content': json.loads(original_content)}
                body['timings']['opening'] = 4.2
                body['content']['realise_your_ideas'] = 'Bring your ideas to life'
                headers = {'Origin': url, 'X-Editor-Token': editor.TOKEN, 'Content-Type': 'application/json'}
                try:
                    request = urllib.request.Request(url + '/api/save', json.dumps(body).encode(), headers)
                    with urllib.request.urlopen(request) as response:
                        self.assertEqual(response.status, 200)
                    self.assertEqual(json.loads(timing.read_text())['opening'], 4.2)
                    self.assertEqual(json.loads(content.read_text(encoding='utf-8'))['realise_your_ideas'], 'Bring your ideas to life')
                    before = timing.read_bytes(), content.read_bytes()
                    body['content']['generate'] = 'A' * 80
                    request = urllib.request.Request(url + '/api/save', json.dumps(body).encode(), headers)
                    with self.assertRaises(urllib.error.HTTPError) as error:
                        urllib.request.urlopen(request)
                    self.assertEqual(error.exception.code, 400)
                    self.assertEqual(before, (timing.read_bytes(), content.read_bytes()))
                    headers['Origin'] = 'https://unrelated.example'
                    request = urllib.request.Request(url + '/api/save', b'{}', headers)
                    with self.assertRaises(urllib.error.HTTPError) as error:
                        urllib.request.urlopen(request)
                    self.assertEqual(error.exception.code, 403)
                finally:
                    server.shutdown()
                    server.server_close()
                    thread.join()
        self.assertEqual(editor.CONFIG.read_bytes(), original_timing)
        self.assertEqual(editor.CONTENT.read_bytes(), original_content)


if __name__ == '__main__':
    unittest.main()

