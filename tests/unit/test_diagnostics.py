import unittest

from dsrag.diagnostics import run_diagnostics


class TestDiagnostics(unittest.TestCase):
    def test_run_diagnostics_shape(self):
        report = run_diagnostics()

        self.assertIn("timestamp_utc", report)
        self.assertIn("python_version", report)
        self.assertIn("platform", report)
        self.assertIn("dependencies", report)
        self.assertIn("environment", report)
        self.assertIn("missing_dependency_features", report)
        self.assertIn("missing_env_vars", report)

        self.assertIsInstance(report["dependencies"], dict)
        self.assertIsInstance(report["environment"], dict)
        self.assertIsInstance(report["missing_dependency_features"], list)
        self.assertIsInstance(report["missing_env_vars"], list)

        for installed in report["dependencies"].values():
            self.assertIsInstance(installed, bool)
        for configured in report["environment"].values():
            self.assertIsInstance(configured, bool)


if __name__ == "__main__":
    unittest.main()
