"""Package the skill and the standalone real-project natural-language product."""
import hashlib
import importlib.util
import json
from pathlib import Path
import runpy
import subprocess
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("narrator", ROOT / "code-narrator/scripts/narrator.py")
n = importlib.util.module_from_spec(spec)
spec.loader.exec_module(n)


def main():
    report = n.validate(ROOT / "examples/build-visprog")[0]
    if not report["passed"]:
        raise ValueError(report["errors"])
    product = ROOT / "examples/visprog自然语言仓库"
    if n.check_links(product):
        raise ValueError("成品链接未通过")
    test = n.read_json(ROOT / "docs/test-results.json")
    if not test["passed"] or test["skipped"]:
        raise ValueError("发布所需测试未全部执行通过")
    runpy.run_path(str(ROOT / "scripts/package_skill.py"), run_name="__main__")
    output = ROOT / "dist/visprog自然语言仓库.zip"
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(product.rglob("*")):
            if path.is_file():
                if path.suffix != ".md" and "许可原文" not in path.relative_to(product).parts:
                    raise ValueError("纯自然语言成品中出现意外文件：" + str(path))
                archive.write(path, Path(product.name) / path.relative_to(product))
    with tempfile.TemporaryDirectory(prefix="narrator-release-check-") as directory:
        folder = Path(directory)
        with zipfile.ZipFile(output) as archive:
            archive.extractall(folder)
        errors = n.check_links(folder / product.name)
        if errors:
            raise ValueError(errors)
        with zipfile.ZipFile(ROOT / "dist/code-narrator.zip") as archive:
            archive.extractall(folder)
        result = subprocess.run([sys.executable, str(folder / "code-narrator/scripts/narrator.py"), "--help"],
                                cwd=folder, capture_output=True)
        if result.returncode:
            raise ValueError("独立 Skill 启动失败：" + result.stderr.decode("utf-8", "replace"))
    artifacts = []
    for path in (ROOT / "dist/code-narrator.zip", output):
        artifacts.append({"file":path.name,"bytes":path.stat().st_size,"sha256":hashlib.sha256(path.read_bytes()).hexdigest()})
    release = {"version":"1.0.0","date":"2026-10-31","artifacts":artifacts,
               "input_snapshot":report["snapshot"],"source_files":report["files"],"units":report["units_total"],
               "tests":test,"portable_links_passed":True,"skill_standalone_start_passed":True}
    n.write_json(ROOT / "dist/release.json", release)
    print(json.dumps(release,ensure_ascii=False,indent=2))


if __name__ == "__main__":
    main()
