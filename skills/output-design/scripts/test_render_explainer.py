import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest

from render_explainer import render


class ExplainerTests(unittest.TestCase):
    def fixture(self):
        return {'title': '说明', 'question': '如何理解？', 'sources': ['示例'],
                'scenarios': [{'name': '未知', 'steps': [{'title': '观察', 'explanation': '未验证，不等于通过。'}]}]}

    def test_input_preserved_in_payload(self):
        data = self.fixture()
        data['title'] = '__DATA__ & 中文'
        page = render(data)
        payload = re.search(r'<script type="application/json" id="explanation-data">(.*?)</script>', page, re.S)[1]
        self.assertEqual(json.loads(payload), data)
        self.assertIn('未验证，不等于通过。', page.split('<script')[0])

    def test_input_cannot_close_script_or_create_html(self):
        data = self.fixture()
        attack = '</script><script>alert(1)</script><img src=x onerror=alert(1)>'
        data['title'] = attack
        data['scenarios'][0]['steps'][0]['explanation'] = attack
        page = render(data)
        self.assertNotIn(attack, page)
        self.assertNotIn('<img src=x', page)
        payload = re.search(r'<script type="application/json" id="explanation-data">(.*?)</script>', page, re.S)[1]
        self.assertEqual(json.loads(payload), data)

    def test_missing_steps_rejected_instead_of_invented(self):
        data = self.fixture()
        data['scenarios'][0]['steps'] = []
        with self.assertRaises(ValueError):
            render(data)

    def test_cli_creates_new_file_and_preserves_existing(self):
        with tempfile.TemporaryDirectory() as folder:
            source, target = Path(folder) / 'input.json', Path(folder) / 'output.html'
            source.write_text(json.dumps(self.fixture(), ensure_ascii=False), encoding='utf-8-sig')
            cmd = [sys.executable, '-X', 'utf8', str(Path(__file__).with_name('render_explainer.py')), str(source), str(target)]
            first = subprocess.run(cmd, capture_output=True)
            self.assertEqual(first.returncode, 0, first.stderr)
            before = target.read_bytes()
            second = subprocess.run(cmd, capture_output=True)
            self.assertNotEqual(second.returncode, 0)
            self.assertEqual(target.read_bytes(), before)


if __name__ == '__main__':
    unittest.main()
