import json, tempfile, unittest
from contextlib import redirect_stdout, redirect_stderr
from io import StringIO
from pathlib import Path
from ci_health_monitor.cli import main

class CliTests(unittest.TestCase):
    def _file(self, payload):
        d=tempfile.TemporaryDirectory(); p=Path(d.name)/"runs.json"; p.write_text(json.dumps(payload), encoding="utf-8"); return d,p
    def test_json_output(self):
        d,p=self._file([{"name":"CI","status":"completed","conclusion":"success"}]); out=StringIO()
        with d, redirect_stdout(out): code=main([str(p),"--json"])
        self.assertEqual(code,0); self.assertTrue(json.loads(out.getvalue())["healthy"])
    def test_unhealthy_exit(self):
        d,p=self._file([{"name":"CI","status":"completed","conclusion":"failure"}]); out=StringIO()
        with d, redirect_stdout(out): code=main([str(p)])
        self.assertEqual(code,1)
    def test_invalid_json_exit(self):
        d=tempfile.TemporaryDirectory(); p=Path(d.name)/"bad.json"; p.write_text("{", encoding="utf-8"); err=StringIO()
        with d, redirect_stderr(err): code=main([str(p)])
        self.assertEqual(code,2); self.assertIn("invalid JSON",err.getvalue())

if __name__ == "__main__": unittest.main()