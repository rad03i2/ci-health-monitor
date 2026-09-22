import json, tempfile, unittest
from pathlib import Path
from ci_health_monitor import analyze_runs, load_runs, parse_run

class CoreTests(unittest.TestCase):
    def run_obj(self, conclusion="success", created="2026-01-01T00:00:00Z", updated="2026-01-01T00:02:00Z", name="CI"):
        return parse_run({"workflowName": name, "status": "completed", "conclusion": conclusion, "createdAt": created, "updatedAt": updated})

    def test_health_metrics(self):
        runs = [self.run_obj("success"), self.run_obj("success"), self.run_obj("failure")]
        report = analyze_runs(runs, min_success_rate=60)
        self.assertTrue(report.healthy)
        self.assertEqual(report.failed, 1)
        self.assertAlmostEqual(report.success_rate, 66.67)
        self.assertEqual(report.average_duration_seconds, 120)

    def test_recent_failure_policy(self):
        runs = [self.run_obj("failure", "2026-01-03T00:00:00Z", "2026-01-03T00:01:00Z"), self.run_obj("failure", "2026-01-02T00:00:00Z", "2026-01-02T00:01:00Z"), self.run_obj("success")]
        report = analyze_runs(runs, min_success_rate=0, max_consecutive_failures=1)
        self.assertFalse(report.healthy); self.assertEqual(report.consecutive_failures, 2)

    def test_cancelled_excluded_from_rate(self):
        report = analyze_runs([self.run_obj("success"), self.run_obj("cancelled")])
        self.assertEqual(report.success_rate, 100.0)

    def test_workflow_filter(self):
        report = analyze_runs([self.run_obj(name="CI"), self.run_obj(name="Docs")], workflow="Docs")
        self.assertEqual(report.total, 1); self.assertIn("Docs", report.workflows)

    def test_load_wrapped_rest_payload(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)/"runs.json"; p.write_text(json.dumps({"workflow_runs":[{"name":"CI","status":"completed","conclusion":"success"}]}), encoding="utf-8")
            self.assertEqual(len(load_runs(p)), 1)

    def test_rejects_bad_timestamp(self):
        with self.assertRaises(ValueError): self.run_obj(created="yesterday")

    def test_rejects_bad_thresholds(self):
        with self.assertRaises(ValueError): analyze_runs([], min_success_rate=101)

if __name__ == "__main__": unittest.main()