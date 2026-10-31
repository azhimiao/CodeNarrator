"""Demonstrate the difference between structural coverage and semantic review.

Writes only an isolated copy. Never modifies the working examples or product.
"""
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile

root = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("narrator", root / "code-narrator/scripts/narrator.py")
n = importlib.util.module_from_spec(spec)
spec.loader.exec_module(n)

with tempfile.TemporaryDirectory(prefix="coverage-audit-", dir=root / "research") as temp:
    work = Path(temp) / "work"
    shutil.copytree(root / "examples/build-record-report", work)
    state, _ = n.load(work)
    for item in state["files"]:
        if item["status"] != "supported":
            continue
        path = work / "translations" / item["packet"]
        packet = n.read_json(path)
        packet["overview"] = "这个模块负责处理项目中的信息。"
        for section in packet["sections"]:
            for field in ("summary", "body", "details"):
                section[field] = "这个部分负责处理项目中的信息。"
        packet["review"] = {"status": "reviewed", "method": "实验：该字段仅为声明，实际文本被替换为空泛描述。"}
        n.write_json(path, packet)
    report = n.validate(work)[0]
    project = n.read_json(work / "project.json")
    packets = [n.read_json(work / "translations" / f["packet"]) for f in state["files"] if f["status"] == "supported"]
    model = n.read_json(work / "model.json")
    model["translation_sha256"] = n.content_hash(project, packets)
    n.write_json(work / "model.json", model)
    forged_report = n.validate(work)[0]
    evidence = {
        "purpose": "反例：全部语义细节被空泛文字替代，但保留结构 ID 与源码依据引用。",
        "mechanical_check_passed": report["passed"],
        "units_total": report["units_total"], "units_covered": report["units_covered"],
        "errors": report["errors"],
        "forged_fresh_review_passed": forged_report["passed"],
        "conclusion": "新版拒绝沿用旧复核，但若生成者虚假刷新复核指纹，仍无法靠确定性检查识别所有语义错误。因此必须用具体行为契约与独立阅读检查，不能把一致性检查当语义准确率。",
    }
    n.write_json(root / "docs/coverage-regression-result.json", evidence)
    print(json.dumps(evidence, ensure_ascii=False, indent=2))
