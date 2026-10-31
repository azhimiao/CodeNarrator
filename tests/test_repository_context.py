import contextlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("context_narrator", ROOT / "code-narrator/scripts/narrator.py")
n = importlib.util.module_from_spec(spec)
spec.loader.exec_module(n)


class RepositoryContextTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.root, self.work = self.base / "input", self.base / "work"
        self.root.mkdir()

    def source(self, name, text):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def scan(self):
        n.scan(self.root, self.work, [], "student")
        return n.read_json(self.work / "repository-context.json")

    def test_relative_src_import_alias_and_reverse_neighbors(self):
        self.source("src/app/__init__.py", "")
        self.source("src/app/tools.py", "def check(value):\n    return bool(value)\n")
        self.source("src/app/main.py", "from .tools import check as verify\nfrom app import tools\ndef run(x):\n    return verify(x)\n")
        graph = self.scan()
        self.assertEqual(graph["dependencies"]["src/app/main.py"], ["src/app/__init__.py", "src/app/tools.py"])
        self.assertIn("src/app/main.py", graph["dependents"]["src/app/tools.py"])
        detail = n.neighborhood(graph, "src/app/main.py")
        self.assertEqual(detail["imports"][0]["binding"], "verify")
        self.assertEqual(next(x for x in detail["neighbors"] if x["file"].endswith("tools.py"))["symbols"][0]["name"], "check")

    def test_external_dynamic_and_ambiguous_imports_stay_uncertain(self):
        self.source("utils.py", "def run(): pass\n")
        self.source("src/utils.py", "def run(): pass\n")
        self.source("main.py", "import utils\nimport remote_library\nhandler.execute()\n__import__('runtime_plugin')\n")
        graph = self.scan()
        records = graph["imports"]["main.py"]
        self.assertEqual(records[0]["candidates"], ["src/utils.py", "utils.py"])
        self.assertEqual(records[0]["status"], "internal_candidate")
        self.assertEqual(records[1]["status"], "external_or_unresolved")
        self.assertTrue(all(x["status"] == "unresolved" for x in graph["call_sites"]["main.py"]))
        self.assertNotIn("runtime_plugin", graph["dependencies"]["main.py"])

    def test_relative_parent_boundaries(self):
        self.source("pkg/__init__.py", "")
        self.source("pkg/core.py", "value = 1\n")
        self.source("pkg/sub/__init__.py", "")
        self.source("pkg/sub/main.py", "from ..core import value\nfrom ....outside import missing\n")
        graph = self.scan()
        self.assertEqual(graph["dependencies"]["pkg/sub/main.py"], ["pkg/core.py"])
        self.assertEqual(graph["imports"]["pkg/sub/main.py"][1]["status"], "unresolved_relative")

    def test_connected_batches_cover_once_with_line_budget(self):
        self.source("a.py", "import b\n")
        self.source("b.py", "import c\n")
        self.source("c.py", "value = 1\n")
        self.scan()
        state, _ = n.load(self.work)
        graph = n.build_context(self.root, state["files"], n.decode, max_batch_lines=2)
        paths = [path for batch in graph["batches"] for path in batch["files"]]
        self.assertEqual(sorted(paths), ["a.py", "b.py", "c.py"])
        self.assertTrue(all(b["source_lines"] <= 2 for b in graph["batches"]))

    def test_context_rejects_changed_neighbor_not_just_current_file(self):
        self.source("a.py", "import b\n")
        self.source("b.py", "value = 1\n")
        self.scan()
        self.source("b.py", "value = 2\n")
        with contextlib.redirect_stderr(io.StringIO()) as stderr:
            code = n.main(["context", "--work", str(self.work), "--file", "a.py"])
        self.assertEqual(code, 2)
        self.assertIn("跨文件上下文已失效", json.loads(stderr.getvalue())["error"])

    def test_entry_guard_is_syntax_evidence_not_name_guess(self):
        self.source("main.py", "def run(): pass\n")
        self.source("cli.py", "if __name__ == '__main__':\n    print('hello')\n")
        graph = self.scan()
        self.assertEqual(graph["entry_candidates"], [{"file": "cli.py", "line": 1, "reason": "main_guard"}])

    def test_rescan_reports_transitive_import_impact_including_removed_edges(self):
        self.source("entry.py", "import middle\n")
        self.source("middle.py", "import leaf\n")
        self.source("leaf.py", "value = 1\n")
        self.scan()
        (self.root / "leaf.py").unlink()
        self.source("middle.py", "value = 2\n")
        self.scan()
        state, _ = n.load(self.work)
        self.assertEqual(state["update_review"]["changed_files"], ["leaf.py", "middle.py"])
        self.assertEqual(state["update_review"]["import_dependents"], ["entry.py"])


if __name__ == "__main__":
    unittest.main()
