import contextlib
import importlib.util
import io
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("narrator", ROOT / "code-narrator/scripts/narrator.py")
n = importlib.util.module_from_spec(spec)
spec.loader.exec_module(n)


class ToolTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Rebuild from committed source so a clean checkout needs no local artifacts.
        subprocess.run([sys.executable, str(ROOT / "examples/build_demo.py")],
                       cwd=ROOT, check=True, stdout=subprocess.DEVNULL)

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.source = self.base / "source"
        shutil.copytree(ROOT / "examples/record-report", self.source,
                        ignore=shutil.ignore_patterns("__pycache__"))
        self.work = self.base / "build"
        n.scan(self.source, self.work, [], "student")
        state, _ = n.load(self.work)
        original, _ = n.load(ROOT / "examples/build-record-report")
        by_path = {f["path"]: f for f in original["files"]}
        for item in state["files"]:
            packet = n.read_json(ROOT / "examples/build-record-report/translations" / by_path[item["path"]]["packet"])
            self.assertEqual(item["sha256"], packet["source_sha256"])
            n.write_json(self.work / "translations" / item["packet"], packet)
        project = n.read_json(ROOT / "examples/build-record-report/project.json")
        project["snapshot"] = state["snapshot"]
        n.write_json(self.work / "project.json", project)
        model = n.read_json(ROOT / "examples/build-record-report/model.json")
        model["snapshot"] = state["snapshot"]
        packets = [n.read_json(self.work / "translations" / f["packet"]) for f in state["files"] if f["status"] == "supported"]
        model["translation_sha256"] = n.content_hash(project, packets)
        n.write_json(self.work / "model.json", model)

    def test_complete_repository_and_portable_links(self):
        report = n.validate(self.work)[0]
        self.assertTrue(report["passed"], report["errors"])
        self.assertEqual(report["units_covered"], report["units_total"])
        out = self.base / "output"
        n.render(self.work, out)
        shutil.rmtree(self.source)
        shutil.rmtree(self.work)
        self.assertFalse(n.check_links(out))
        for path in out.rglob("*.md"):
            text = path.read_text(encoding="utf-8")
            self.assertNotIn("```", text)
            self.assertNotIn(str(self.source), text)
        with self.assertRaises(ValueError):
            # Existing products must not silently be overwritten.
            n.render(ROOT / "examples/build-record-report", out)

    def test_missing_unit_blocks_render(self):
        state, _ = n.load(self.work)
        packet_path = self.work / "translations" / state["files"][0]["packet"]
        packet = n.read_json(packet_path)
        packet["sections"][0]["unit_ids"].pop()
        n.write_json(packet_path, packet)
        report = n.validate(self.work)[0]
        self.assertFalse(report["passed"])
        self.assertTrue(report["missing_units"])
        with self.assertRaises(ValueError):
            n.render(self.work, self.base / "incomplete")
        self.assertFalse((self.base / "incomplete").exists())

    def test_added_modified_deleted_context_invalidates(self):
        state, _ = n.load(self.work)
        (self.source / "new.py").write_text("value = 1\n", encoding="utf-8")
        (self.source / "settings.py").write_text("value = 2\n", encoding="utf-8")
        (self.source / "report.py").unlink()
        self.assertEqual(n.freshness(self.work, state), ["new.py", "report.py", "settings.py"])
        self.assertFalse(n.validate(self.work)[0]["passed"])

    def test_rescan_preserves_work_and_requires_review(self):
        state, _ = n.load(self.work)
        packet_path = self.work / "translations" / state["files"][0]["packet"]
        before = packet_path.read_bytes()
        (self.source / state["files"][0]["path"]).write_text("changed = True\n", encoding="utf-8")
        n.scan(self.source, self.work, [], "student")
        self.assertEqual(packet_path.read_bytes(), before)
        report = n.validate(self.work)[0]
        self.assertFalse(report["passed"])
        self.assertTrue(any("哈希" in error or "内容" in error for error in report["errors"]))

    def test_unsupported_and_syntax_failure_are_not_hidden(self):
        (self.source / "page.js").write_text("let x = 1;", encoding="utf-8")
        (self.source / "broken.py").write_text("def !", encoding="utf-8")
        (self.source / ".env").write_text("TOKEN=private", encoding="utf-8")
        n.scan(self.source, self.work, [], "student")
        state, _ = n.load(self.work)
        statuses = {f["path"]: f["status"] for f in state["files"]}
        self.assertEqual(statuses["page.js"], "unsupported")
        self.assertEqual(statuses["broken.py"], "failed")
        self.assertEqual(statuses[".env"], "excluded")
        self.assertFalse(n.validate(self.work)[0]["passed"])

    def test_blocking_unknown_and_wrong_evidence_rejected(self):
        project = n.read_json(self.work / "project.json")
        project["unknowns"] = [{"description": "尚未确定关键目标", "blocking": True}]
        n.write_json(self.work / "project.json", project)
        self.assertFalse(n.validate(self.work)[0]["passed"])
        state, _ = n.load(self.work)
        packet_path = self.work / "translations" / state["files"][0]["packet"]
        packet = n.read_json(packet_path)
        packet["sections"][0]["evidence"] = ["invented"]
        n.write_json(packet_path, packet)
        self.assertTrue(any("evidence" in error for error in n.validate(self.work)[0]["errors"]))

    def test_nested_work_excluded_and_scan_is_stable(self):
        nested = self.source / "build-records"
        n.scan(self.source, nested, [], "student")
        state, _ = n.load(nested)
        self.assertEqual(n.freshness(nested, state), [])
        first = n.scan(self.source, nested, [], "student")["snapshot"]
        second = n.scan(self.source, nested, [], "student")["snapshot"]
        self.assertEqual(first, second)

    def test_unicode_nested_decorators_defaults_and_branches(self):
        text = '@wrap("中文")\ndef 外层(值=2):\n    try:\n        if 值:\n            return [str(x) for x in range(值)]\n        else:\n            return []\n    except TypeError:\n        raise\n    finally:\n        release()\n'
        units = n.extract("例.py", text)
        self.assertEqual(len({u["id"] for u in units}), len(units))
        kinds = {u["kind"] for u in units}
        self.assertTrue({"FunctionDef", "Try", "If", "Return", "ExceptHandler", "ListComp", "comprehension", "Call", "Constant"} <= kinds)
        self.assertTrue(any(u["start_line"] == 1 and u["kind"] == "Call" for u in units))
        self.assertTrue(all(u["start_line"] <= u["end_line"] for u in units))
        call = next(u for u in units if u["start_line"] == 5 and u["kind"] == "Call")
        self.assertEqual(text.splitlines()[4].encode()[call["start_byte"]:call["end_byte"]].decode(), "str(x)")

    def test_broken_links_and_escape_rejected(self):
        folder = self.base / "docs"
        folder.mkdir()
        (folder / "开始.md").write_text('[坏链接](missing.md)\n[越界](../source/report.py)\n[缺锚点](开始.md#missing)', encoding="utf-8")
        self.assertEqual(len(n.check_links(folder)), 3)

    def test_tampered_index_fails_and_cli_reports_exit_status(self):
        state, units = n.load(self.work)
        units[0]["start_line"] = 999
        n.write_json(self.work / "units.json", units)
        with contextlib.redirect_stdout(io.StringIO()) as stdout:
            code = n.main(["validate", "--work", str(self.work)])
        self.assertEqual(code, 1)
        self.assertFalse(json.loads(stdout.getvalue())["passed"])

    def test_review_method_must_be_text(self):
        state, _ = n.load(self.work)
        path = self.work / "translations" / state["files"][0]["packet"]
        packet = n.read_json(path)
        packet["review"]["method"] = ["not a string"]
        n.write_json(path, packet)
        report = n.validate(self.work)[0]
        self.assertFalse(report["passed"])
        self.assertTrue(any("review.method" in error for error in report["errors"]))

    def test_filename_with_hash_spaces_parentheses_and_percent(self):
        name = "说明 # (版本1)%.md"
        (self.source / name).write_text("这是项目说明。", encoding="utf-8")
        n.scan(self.source, self.work, [], "student")
        state, units = n.load(self.work)
        item = next(f for f in state["files"] if f["path"] == name)
        ids = [u["id"] for u in units if u["file"] == name]
        packet = {"schema_version": 1, "source_file": name, "source_sha256": item["sha256"],
                  "title": "项目说明", "overview": "说明项目用途。", "sections": [{
                      "title": "用途", "summary": "用于说明。", "body": "本文件用自然语言说明项目。",
                      "details": "", "unit_ids": ids, "evidence": ids, "links": [],
                  }], "review": {"status": "reviewed", "method": "测试固定资料"}}
        n.write_json(self.work / "translations" / item["packet"], packet)
        project = n.read_json(self.work / "project.json")
        project["snapshot"] = state["snapshot"]
        project["reading_order"].append(name)
        project["flows"][0]["unit_ids"].extend(ids)
        n.write_json(self.work / "project.json", project)
        old = next(f for f in state["files"] if f["path"] == "pipeline.py")
        old_packet = n.read_json(self.work / "translations" / old["packet"])
        old_packet["sections"][0]["links"].append({"target": ids[0], "label": "项目说明"})
        n.write_json(self.work / "translations" / old["packet"], old_packet)
        model = n.read_json(self.work / "model.json")
        model["snapshot"] = state["snapshot"]
        model["components"].append({"id": name, "title": "项目说明", "role": "提供项目用途说明。", "files": [name], "evidence": ids})
        packets = [n.read_json(self.work / "translations" / f["packet"]) for f in state["files"] if f["status"] == "supported"]
        model["translation_sha256"] = n.content_hash(project, packets)
        n.write_json(self.work / "model.json", model)
        output = self.base / "special-output"
        n.render(self.work, output)
        self.assertFalse(n.check_links(output))
        self.assertIn("%23", (output / "项目目录.md").read_text(encoding="utf-8"))


class ExampleBehavior(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, str(ROOT / "examples/record-report"))
        import pipeline
        import settings
        import select_records
        cls.run_task = staticmethod(pipeline.run)
        cls.Settings = settings.Settings
        cls.choose = staticmethod(select_records.select_records)

    @classmethod
    def tearDownClass(cls):
        sys.path.remove(str(ROOT / "examples/record-report"))

    def test_threshold_order_early_stop_and_unicode(self):
        result = self.run_task([{"id": "甲", "score": .8}, {"id": "乙", "score": .9}, {"id": "丙", "score": .85}, None])
        self.assertTrue(result["ok"])
        self.assertEqual(result["report"]["identifiers"], ["甲", "乙", "丙"])
        self.assertIn("甲", result["text"])

    def test_empty_missing_and_error_boundaries(self):
        self.assertEqual(self.run_task([{}, {"score": None}])["report"]["count"], 0)
        self.assertEqual(self.run_task([{"score": .9}]), {"ok": False, "reason": "KeyError"})
        self.assertEqual(self.run_task([{"score": "bad"}]), {"ok": False, "reason": "TypeError"})
        with self.assertRaises(AttributeError):
            self.run_task([None])
        with self.assertRaises(ValueError):
            self.Settings(minimum=2)

    def test_fractional_limit_and_shared_references(self):
        config = self.Settings(limit=1.5)
        row = {"id": "original", "score": .8}
        chosen = self.choose([row, row, row], config.minimum, config.limit)
        self.assertEqual(len(chosen), 2)
        self.assertIs(chosen[0], row)
        chosen[0]["id"] = "changed"
        self.assertEqual(row["id"], "changed")


if __name__ == "__main__":
    unittest.main()
