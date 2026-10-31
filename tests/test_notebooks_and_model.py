import contextlib
import json
from pathlib import Path
import tempfile
import unittest

import test_narrator as fixture

n = fixture.n


class NotebookTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.root, self.work = self.base / "repo", self.base / "build"
        self.root.mkdir()

    def notebook(self, name, cells):
        path = self.root / name
        path.write_text(json.dumps({"nbformat": 4, "nbformat_minor": 5, "metadata": {}, "cells": cells}), encoding="utf-8")
        return path

    def test_cells_magic_markdown_and_stored_outputs_are_not_executed(self):
        self.notebook("entry.ipynb", [
            {"cell_type": "markdown", "source": ["说明"], "metadata": {}},
            {"cell_type": "code", "source": ["%env KEY=example\n", "import core\n", "raise RuntimeError('never execute')"], "execution_count": 8, "outputs": [{"output_type": "stream", "text": "old"}]},
            {"cell_type": "code", "source": "%%bash\necho test", "outputs": []},
        ])
        (self.root / "core.py").write_text("def run(): return 1\n", encoding="utf-8")
        n.scan(self.root, self.work, [], "student")
        state, units = n.load(self.work)
        self.assertTrue(all(f["status"] == "supported" for f in state["files"]))
        self.assertTrue(any(u["kind"] == "NotebookDirective" and u["cell"] == 1 and u["start_line"] == 1 for u in units))
        self.assertTrue(any(u["kind"] == "Raise" and u["cell"] == 1 for u in units))
        graph = n.read_json(self.work / "repository-context.json")
        self.assertEqual(graph["dependencies"]["entry.ipynb"], ["core.py"])
        self.assertTrue(any(x["reason"] == "notebook_saved_cell_order" for x in graph["entry_candidates"]))

    def test_multiline_string_is_not_mistaken_for_magic(self):
        source = 'text = """hello\n%not_a_magic\n"""\nprint(text)\n'
        units = n.extract_notebook("x.ipynb", json.dumps({"nbformat":4,"cells":[{"cell_type":"code","source":source}]}), n.extract)
        self.assertFalse(any(u["kind"] == "NotebookDirective" for u in units))
        self.assertTrue(any(u["kind"] == "Assign" for u in units))

    def test_other_kernel_language_is_explicitly_rejected(self):
        path = self.notebook("other.ipynb", [{"cell_type":"code", "source":"value = 1"}])
        data = json.loads(path.read_text(encoding="utf-8"))
        data["metadata"] = {"language_info": {"name": "julia"}}
        path.write_text(json.dumps(data), encoding="utf-8")
        n.scan(self.root, self.work, [], "student")
        state, _ = n.load(self.work)
        self.assertEqual(state["files"][0]["status"], "failed")
        self.assertIn("内核语言", state["files"][0]["reason"])

    def test_malformed_notebook_python_fails_instead_of_disappearing(self):
        self.notebook("bad.ipynb", [{"cell_type":"code","source":"def !","outputs":[]}])
        n.scan(self.root, self.work, [], "student")
        state, _ = n.load(self.work)
        self.assertEqual(state["files"][0]["status"], "failed")

    def test_long_function_chunks_preserve_coverage_and_context(self):
        (self.root / "huge.py").write_text("class Work:\n    def run(self):\n" + "        value = 1\n" * 500, encoding="utf-8")
        n.scan(self.root, self.work, [], "student")
        _, units = n.load(self.work)
        chunks = n.read_json(self.work / "analysis-chunks.json")["chunks"]
        self.assertEqual({u["id"] for u in units}, {i for c in chunks for i in c["unit_ids"]})
        self.assertTrue(all(c["end_line"] - c["start_line"] < 160 for c in chunks))
        self.assertTrue(any({a["name"] for a in c["enclosing_definitions"]} == {"Work","run"} for c in chunks))


class ModelTests(unittest.TestCase):
    setUp = fixture.ToolTests.setUp

    def test_changed_prose_invalidates_old_semantic_review(self):
        state, _ = n.load(self.work)
        path = self.work / "translations" / state["files"][0]["packet"]
        packet = n.read_json(path)
        for s in packet["sections"]:
            s["body"] = "这个部分负责处理项目中的信息。"
        n.write_json(path, packet)
        report = n.validate(self.work)[0]
        self.assertFalse(report["passed"])
        self.assertTrue(any("译文已变化" in e for e in report["errors"]))

    def test_missing_component_and_dangling_dispatch_are_rejected(self):
        path = self.work / "model.json"
        model = n.read_json(path)
        model["components"].pop()
        model["relations"][0]["to"] = "missing-component"
        n.write_json(path, model)
        errors = n.validate(self.work)[0]["errors"]
        self.assertTrue(any("恰好承接" in e for e in errors))
        self.assertTrue(any("不存在的组件" in e for e in errors))

    def test_missing_behavior_failure_case_blocks_delivery(self):
        path = self.work / "model.json"
        model = n.read_json(path)
        model["checks"] = [c for c in model["checks"] if c["kind"] != "failure"]
        n.write_json(path, model)
        self.assertFalse(n.validate(self.work)[0]["passed"])
        with self.assertRaises(ValueError):
            n.render(self.work, self.base / "incomplete")


if __name__ == "__main__":
    unittest.main()
