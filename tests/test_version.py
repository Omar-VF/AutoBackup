import os
import re
import tempfile
import unittest
from pathlib import Path
from autobackup.version import get_version, write_version_file, _clean_version, DEFAULT_VERSION


class TestVersion(unittest.TestCase):
    def test_clean_version(self):
        self.assertEqual(_clean_version("v1.2.3"), "1.2.3")
        self.assertEqual(_clean_version("V2.0.0"), "2.0.0")
        self.assertEqual(_clean_version("refs/tags/v3.4.5"), "3.4.5")
        self.assertEqual(_clean_version("  1.0.1  \n"), "1.0.1")

    def test_git_or_default_version(self):
        # Without env vars, get_version should dynamically return the git tag or default
        old_env = {k: os.environ.pop(k, None) for k in ("TETHR_VERSION", "APP_VERSION", "GITHUB_REF_NAME")}
        try:
            ver = get_version(use_cache=False)
            self.assertTrue(re.match(r"^\d+\.\d+(\.\d+)?", ver), f"Version '{ver}' should match semver pattern")
        finally:
            for k, v in old_env.items():
                if v is not None:
                    os.environ[k] = v

    def test_env_override(self):
        old_env = os.environ.get("TETHR_VERSION")
        try:
            os.environ["TETHR_VERSION"] = "v2.8.4"
            ver = get_version(use_cache=False)
            self.assertEqual(ver, "2.8.4")

            os.environ["TETHR_VERSION"] = "3.1.0"
            ver = get_version(use_cache=False)
            self.assertEqual(ver, "3.1.0")
        finally:
            if old_env is not None:
                os.environ["TETHR_VERSION"] = old_env
            else:
                os.environ.pop("TETHR_VERSION", None)

    def test_github_ref_name_override(self):
        old_ref = os.environ.get("GITHUB_REF_NAME")
        try:
            os.environ["GITHUB_REF_NAME"] = "v1.9.9"
            ver = get_version(use_cache=False)
            self.assertEqual(ver, "1.9.9")
        finally:
            if old_ref is not None:
                os.environ["GITHUB_REF_NAME"] = old_ref
            else:
                os.environ.pop("GITHUB_REF_NAME", None)

    def test_write_version_file(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            target = Path(tmp_dir) / "_test_ver.py"
            write_version_file("v4.5.6", target)
            self.assertTrue(target.exists())
            content = target.read_text(encoding="utf-8")
            self.assertIn('VERSION = "4.5.6"', content)


if __name__ == "__main__":
    unittest.main()
