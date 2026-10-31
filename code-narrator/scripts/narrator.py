#!/usr/bin/env python3
"""Deterministic support for an agent-authored natural-language repository.

Python 3.10+, standard library only. This tool never executes target code.
"""
from __future__ import annotations

import argparse
import ast
import fnmatch
import hashlib
import io
import json
import os
from pathlib import Path
import re
import sys
import tempfile
import tokenize
from urllib.parse import quote, unquote, urlsplit

# Also support callers loading this script through importlib rather than the CLI.
if str(Path(__file__).resolve().parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
from repository_context import build_context, neighborhood
from notebooks import cells, extract_notebook
from chunks import build_chunks
from semantic_model import content_hash, validate_model, render_model, render_checks

VERSION = 1
SKIP_DIRS = {".git", ".hg", ".svn", "__pycache__", ".venv", "venv", "node_modules"}
TEXT_SUFFIXES = {".json", ".toml", ".yaml", ".yml", ".ini", ".cfg", ".md", ".txt", ".dat"}
TEXT_NAMES = {".gitignore", ".gitattributes", "LICENSE", "NOTICE", "Dockerfile", "Makefile"}
BINARY_SUFFIXES = {".pyc", ".png", ".jpg", ".jpeg", ".gif", ".pdf", ".zip", ".exe", ".dll"}
SPECIAL = (ast.Call, ast.Lambda, ast.Await, ast.Yield, ast.YieldFrom,
           ast.NamedExpr, ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp,
           ast.ExceptHandler, ast.comprehension)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    # Replace in the same filesystem, so interruption cannot leave half a JSON file.
    fd, temp = tempfile.mkstemp(dir=path.parent, prefix=".narrator-", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(value, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
        os.replace(temp, path)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)


def inside(path: Path, parent: Path) -> bool:
    return path == parent or parent in path.parents


def decode(raw: bytes, python=False) -> str:
    encoding = tokenize.detect_encoding(io.BytesIO(raw).readline)[0] if python else "utf-8-sig"
    return raw.decode(encoding)


def extract(path: str, text: str, python=True) -> list[dict]:
    """Index statements plus behavior-bearing expressions, using AST byte columns."""
    units = []
    line_count = max(1, len(text.splitlines()))

    def add(kind, route, node=None, parent=None, name=None):
        descendants = list(ast.walk(node)) if node is not None else []
        starts = [n.lineno for n in descendants if hasattr(n, "lineno")]
        ends = [getattr(n, "end_lineno", n.lineno) for n in descendants if hasattr(n, "lineno")]
        unit = {
            "id": digest((path + ":" + route).encode())[:20], "file": path,
            "kind": kind, "name": name, "parent": parent,
            "start_line": getattr(node, "lineno", min(starts, default=1)),
            "end_line": getattr(node, "end_lineno", max(ends, default=line_count)),
            "start_byte": getattr(node, "col_offset", 0),
            "end_byte": getattr(node, "end_col_offset", None),
        }
        units.append(unit)
        return unit["id"]

    root = add("Module" if python else "Document", "root")
    if not python:
        return units
    tree = ast.parse(text, filename=path, type_comments=True)

    def walk(node, route, parent, forced=False):
        selected = isinstance(node, (ast.stmt,) + SPECIAL) or forced
        if hasattr(ast, "match_case") and isinstance(node, ast.match_case):
            selected = True
        current = parent
        if selected:
            current = add(type(node).__name__, route, node, parent, getattr(node, "name", None))
        for field, value in ast.iter_fields(node):
            if isinstance(value, list):
                for index, child in enumerate(value):
                    if isinstance(child, ast.AST):
                        walk(child, f"{route}.{field}.{index}", current,
                             field in {"decorator_list", "defaults", "kw_defaults"})
            elif isinstance(value, ast.AST):
                walk(value, f"{route}.{field}", current)

    walk(tree, "ast", root)
    return units


def packet_name(path: str) -> str:
    return digest(path.encode())[:20] + ".json"


def load(work: Path):
    state = read_json(work / "manifest.json")
    if not isinstance(state, dict) or state.get("schema_version") != VERSION:
        raise ValueError("不支持此构建记录版本")
    units = read_json(work / "units.json")
    if not isinstance(units, list) or any(not isinstance(u, dict) for u in units):
        raise ValueError("结构索引必须是对象列表")
    return state, units


def verified_index(work, state, filename, hash_field):
    value = read_json(work / filename)
    if (value.get("snapshot") != state["snapshot"] or
            digest(json.dumps(value, ensure_ascii=False, sort_keys=True).encode()) != state.get(hash_field)):
        raise ValueError("索引与扫描记录不一致，请重新 scan：" + filename)
    return value


def scan(root: Path, work: Path, patterns: list[str], profile: str):
    root, work = root.resolve(), work.resolve()
    if not root.is_dir() or inside(root, work):
        raise ValueError("输入必须是目录，构建目录不能等于或包含输入目录")
    previous, previous_graph = None, {}
    if (work / "manifest.json").exists():
        previous, _ = load(work)
        if Path(previous["root"]) != root:
            raise ValueError("构建目录已绑定另一个仓库，请使用新目录")
        try:
            previous_graph = read_json(work / "repository-context.json")
        except (OSError, ValueError):
            pass
    records, units = [], []

    def excluded(rel):
        return any(fnmatch.fnmatchcase(rel, pattern) for pattern in patterns)

    def record(path, status, reason=None):
        item = {"path": path.relative_to(root).as_posix(), "status": status}
        if reason:
            item["reason"] = reason
        records.append(item)
        return item

    def walk_error(error):
        record(Path(error.filename), "failed", str(error))

    for directory, dirs, files in os.walk(root, followlinks=False, onerror=walk_error):
        base = Path(directory)
        for name in sorted(dirs.copy()):
            path = base / name
            rel = path.relative_to(root).as_posix()
            reason = None
            is_link = path.is_symlink() or (hasattr(path, "is_junction") and path.is_junction())
            if is_link:
                reason = "不跟随目录链接"
            elif inside(path.resolve(), work):
                reason = "构建产物"
            elif name in SKIP_DIRS:
                reason = "缓存、版本记录或依赖目录"
            elif excluded(rel) or excluded(rel + "/"):
                reason = "用户排除规则"
            if reason:
                record(path, "excluded", reason)
                dirs.remove(name)
        dirs.sort()
        for name in sorted(files):
            path = base / name
            rel = path.relative_to(root).as_posix()
            if path.is_symlink():
                record(path, "excluded", "不跟随文件链接")
                continue
            if excluded(rel) or name == ".env" or name.startswith(".env."):
                record(path, "excluded", "用户规则或环境凭据文件")
                continue
            if path.suffix.lower() in BINARY_SUFFIXES:
                record(path, "excluded", "二进制或编译产物")
                continue
            item = record(path, "pending")
            try:
                raw = path.read_bytes()
                item["sha256"] = digest(raw)
                if path.suffix.lower() not in TEXT_SUFFIXES | {".py", ".ipynb"} and path.name not in TEXT_NAMES:
                    item.update(status="unsupported", reason="未支持的文件类型；尚未翻译")
                    continue
                text = decode(raw, path.suffix.lower() == ".py")
                found = extract_notebook(rel, text, extract) if path.suffix.lower() == ".ipynb" else extract(rel, text, path.suffix.lower() == ".py")
                item.update(status="supported", unit_count=len(found), packet=packet_name(rel))
                units.extend(found)
            except (OSError, UnicodeError, SyntaxError, LookupError, ValueError, TypeError, AttributeError) as error:
                item.update(status="failed", reason=str(error))
    records.sort(key=lambda item: item["path"])
    snapshot = digest(json.dumps(records, ensure_ascii=False, sort_keys=True).encode())
    state = {"schema_version": VERSION, "root": str(root), "snapshot": snapshot,
             "units_sha256": digest(json.dumps(units, ensure_ascii=False, sort_keys=True).encode()),
             "profile": profile, "exclude": patterns, "files": records}
    work.mkdir(parents=True, exist_ok=True)
    # The manifest is written last; validation also checks every unit count.
    write_json(work / "units.json", units)
    graph = build_context(root, records, decode)
    graph["snapshot"] = snapshot
    state["context_sha256"] = digest(json.dumps(graph, ensure_ascii=False, sort_keys=True).encode())
    write_json(work / "repository-context.json", graph)
    chunks = build_chunks(root, records, units, decode)
    chunks["snapshot"] = snapshot
    state["chunks_sha256"] = digest(json.dumps(chunks, ensure_ascii=False, sort_keys=True).encode())
    write_json(work / "analysis-chunks.json", chunks)
    if previous:
        before = {f["path"]: (f["status"], f.get("sha256")) for f in previous["files"] if f["status"] != "excluded"}
        after = {f["path"]: (f["status"], f.get("sha256")) for f in records if f["status"] != "excluded"}
        changed = sorted(p for p in before.keys() | after.keys() if before.get(p) != after.get(p))
        impacted, queue = set(changed), list(changed)
        while queue:
            path = queue.pop()
            for g in (previous_graph, graph):
                for dependent in g.get("dependents", {}).get(path, []):
                    if dependent not in impacted:
                        impacted.add(dependent)
                        queue.append(dependent)
        state["update_review"] = {"changed_files": changed, "import_dependents": sorted(impacted - set(changed)),
            "instruction": "导入反向影响只是候选；还要复核 model 中的动态分派、共享状态、配置和跨文件译文。"}
        # Repeated scans of the same snapshot retain outstanding review hints.
        if not changed and previous.get("snapshot") == snapshot and previous.get("update_review"):
            state["update_review"] = previous["update_review"]
    for item in records:
        if item["status"] == "supported" and digest((root / item["path"]).read_bytes()) != item["sha256"]:
            raise ValueError("扫描期间源码变化，请重试：" + item["path"])
    write_json(work / "manifest.json", state)
    packets = work / "translations"
    for item in records:
        if item["status"] != "supported":
            continue
        packet = packets / item["packet"]
        if not packet.exists():
            write_json(packet, {"schema_version": VERSION, "source_file": item["path"],
                                "source_sha256": item["sha256"], "title": "", "overview": "",
                                "sections": [], "review": {"status": "unreviewed", "method": ""}})
    if not (work / "project.json").exists():
        write_json(work / "project.json", {
            "schema_version": VERSION, "snapshot": snapshot, "title": "", "overview": "",
            "architecture": "", "reading_order": [], "flows": [], "data": "",
            "dependencies": "", "glossary": "", "unknowns": [],
        })
    if not (work / "model.json").exists():
        write_json(work / "model.json", {"schema_version": 1, "snapshot": snapshot,
                   "translation_sha256": "", "components": [], "relations": [],
                   "state": [], "state_policy": "", "contracts": [], "journeys": [], "checks": [],
                   "review": {"status": "unreviewed", "method": ""}})
    return {"snapshot": snapshot, "files": len(records), "units": len(units),
            "supported": sum(f["status"] == "supported" for f in records), "work": str(work)}


def freshness(work: Path, state: dict) -> list[str]:
    """Rescan to detect added files as well as changed/deleted source and context."""
    with tempfile.TemporaryDirectory(prefix="narrator-check-") as temp:
        # Exclude the original work path if it is inside the source tree.
        patterns = state["exclude"].copy()
        root = Path(state["root"])
        if inside(work.resolve(), root):
            patterns.append(work.resolve().relative_to(root).as_posix())
        scan(root, Path(temp), patterns, state["profile"])
        other, _ = load(Path(temp))
    before = {f["path"]: (f["status"], f.get("sha256")) for f in state["files"]
              if f["status"] != "excluded"}
    after = {f["path"]: (f["status"], f.get("sha256")) for f in other["files"]
             if f["status"] != "excluded"}
    return sorted(path for path in before.keys() | after.keys() if before.get(path) != after.get(path))


def prose(value, where, errors, required=True):
    if not isinstance(value, str) or (required and not value.strip()):
        errors.append(f"{where}：缺少自然语言正文")
        return
    if re.search(r"```|~~~|\bTODO\b|\bTBD\b|待补充|占位符", value, re.I):
        errors.append(f"{where}：包含代码围栏或未完成占位文字")
    if re.search(r"(?m)^\s*(?:def \w+\(|class \w+[:(]|from \w[\w.]* import |import \w|return\s+|\w+\s*=\s*[^=])", value):
        errors.append(f"{where}：疑似源码或伪代码，请转换为完整自然语言")


def validate(work: Path, check_fresh=True):
    state, units = load(work)
    errors, warnings, covered, packets = [], [], set(), []
    known = {u["id"]: u for u in units}
    supported = [f for f in state["files"] if f["status"] == "supported"]
    if not supported:
        errors.append("没有可翻译的输入文件")
    if len(known) != len(units):
        errors.append("结构单元 ID 重复")
    if digest(json.dumps(units, ensure_ascii=False, sort_keys=True).encode()) != state.get("units_sha256"):
        errors.append("结构索引与扫描记录不一致，请重新扫描")
    try:
        graph = read_json(work / "repository-context.json")
        if (graph.get("snapshot") != state["snapshot"] or
                digest(json.dumps(graph, ensure_ascii=False, sort_keys=True).encode()) != state.get("context_sha256")):
            errors.append("跨文件上下文与扫描记录不一致，请重新扫描")
    except (OSError, ValueError, AttributeError):
        errors.append("缺少有效的跨文件上下文，请重新扫描")
    try:
        chunk_index = read_json(work / "analysis-chunks.json")
        if (chunk_index.get("snapshot") != state["snapshot"] or
                digest(json.dumps(chunk_index, ensure_ascii=False, sort_keys=True).encode()) != state.get("chunks_sha256")):
            errors.append("分块索引与扫描记录不一致，请重新扫描")
        indexed = {uid for c in chunk_index["chunks"] for uid in c["unit_ids"]}
        if indexed != set(known):
            errors.append("分块索引未承接全部结构")
    except (OSError, ValueError, TypeError, KeyError, AttributeError):
        errors.append("缺少有效的分块索引，请重新扫描")
    changed = freshness(work, state) if check_fresh else []
    if changed:
        errors.append("源码快照已变化，需重新扫描并复核：" + "、".join(changed))
    for item in state["files"]:
        if item["status"] in {"failed", "unsupported"}:
            errors.append(f"{item['path']}：{item['status']}，{item['reason']}；需支持或明确排除")
    for item in supported:
        file_units = {u["id"] for u in units if u["file"] == item["path"]}
        if len(file_units) != item["unit_count"] or not file_units:
            errors.append(f"{item['path']}：索引与清单不一致，请重新扫描")
        try:
            packet = read_json(work / "translations" / item["packet"])
            if not isinstance(packet, dict):
                raise ValueError("文件包必须是对象")
            if packet.get("schema_version") != VERSION:
                errors.append(f"{item['path']}：翻译包格式版本不符")
            if packet.get("source_file") != item["path"] or packet.get("source_sha256") != item["sha256"]:
                errors.append(f"{item['path']}：翻译未绑定当前文件内容，需复核后更新哈希")
            for field in ("title", "overview"):
                prose(packet.get(field), f"{item['path']}.{field}", errors)
            sections = packet.get("sections")
            if not isinstance(sections, list):
                raise ValueError("sections 必须是列表")
            for index, section in enumerate(sections):
                where = f"{item['path']} 第 {index + 1} 节"
                if not isinstance(section, dict):
                    errors.append(where + "：章节必须是对象")
                    continue
                for field in ("title", "summary", "body", "details"):
                    prose(section.get(field), where + "." + field, errors, field != "details")
                ids = section.get("unit_ids")
                if not isinstance(ids, list) or not ids or any(not isinstance(x, str) for x in ids):
                    errors.append(where + "：需要非空 unit_ids 列表")
                    ids = []
                wrong = [x for x in ids if x not in file_units]
                if wrong:
                    errors.append(where + "：映射不属于当前文件：" + ", ".join(wrong))
                covered.update(x for x in ids if x in file_units)
                evidence = section.get("evidence", [])
                if not isinstance(evidence, list) or any(not isinstance(x, str) or x not in known for x in evidence):
                    errors.append(where + "：evidence 必须引用真实单元")
                elif not evidence:
                    errors.append(where + "：缺少事实依据 evidence")
                links = section.get("links", [])
                if not isinstance(links, list):
                    errors.append(where + "：links 必须是列表")
                else:
                    for link in links:
                        if not isinstance(link, dict) or link.get("target") not in known:
                            errors.append(where + "：无效的关系目标")
                        else:
                            prose(link.get("label"), where + ".links.label", errors)
            review = packet.get("review", {})
            if not isinstance(review, dict) or review.get("status") != "reviewed":
                errors.append(f"{item['path']}：尚未记录语义复核方式")
            else:
                prose(review.get("method"), f"{item['path']}.review.method", errors)
            packets.append(packet)
        except (OSError, ValueError, TypeError, KeyError) as error:
            errors.append(f"{item['path']}：翻译包无效：{error}")
    missing = sorted(set(known) - covered)
    if missing:
        errors.append(f"尚有 {len(missing)} 个结构未被正文承接")
    project = {}
    try:
        project = read_json(work / "project.json")
        if not isinstance(project, dict):
            raise ValueError("项目包必须是对象")
        if project.get("schema_version") != VERSION or project.get("snapshot") != state["snapshot"]:
            errors.append("项目说明的格式或快照不符，需复核后更新")
        for field in ("title", "overview", "architecture", "data", "dependencies", "glossary"):
            prose(project.get(field), "项目." + field, errors)
        order = project.get("reading_order")
        paths = {f["path"] for f in supported}
        if not isinstance(order, list) or not order or any(not isinstance(x, str) or x not in paths for x in order):
            errors.append("reading_order 必须包含有效的文件路径")
        flows = project.get("flows")
        if not isinstance(flows, list) or not flows:
            errors.append("至少需要一条完整的自然语言流程")
        else:
            for flow in flows:
                if not isinstance(flow, dict):
                    errors.append("流程必须是对象")
                    continue
                prose(flow.get("title"), "流程标题", errors)
                prose(flow.get("body"), "流程正文", errors)
                ids = flow.get("unit_ids")
                if not isinstance(ids, list) or not ids or any(not isinstance(x, str) or x not in known for x in ids):
                    errors.append("流程缺少有效的单元依据")
        unknowns = project.get("unknowns")
        if not isinstance(unknowns, list):
            errors.append("unknowns 必须是列表")
        else:
            for unknown in unknowns:
                if not isinstance(unknown, dict) or not isinstance(unknown.get("blocking"), bool):
                    errors.append("未知事项需要 description 和布尔值 blocking")
                    continue
                prose(unknown.get("description"), "未知事项", errors)
                (errors if unknown["blocking"] else warnings).append("未确定：" + str(unknown.get("description")))
    except (OSError, ValueError, TypeError) as error:
        errors.append("项目说明无效：" + str(error))
    try:
        errors.extend(validate_model(read_json(work / "model.json"), state, units, project, packets, prose))
    except (OSError, ValueError, TypeError, KeyError, AttributeError) as error:
        errors.append("语义模型无效：" + str(error))
    report = {"schema_version": VERSION, "snapshot": state["snapshot"], "passed": not errors,
              "files": len(supported), "units_total": len(known), "units_covered": len(covered),
              "missing_units": missing, "changed_files": changed, "errors": errors, "warnings": warnings,
              "limitation": "结构检查不证明语义正确或用户理解效果；复核方式由生成者记录。"}
    write_json(work / "validation-report.json", report)
    return report, state, packets, project


def markdown_link(label, target, anchor=None):
    encoded = quote(target, safe="/")
    if anchor:
        encoded += "#" + quote(anchor, safe="")
    return "[" + label.replace("[", "\\[").replace("]", "\\]") + "](" + encoded + ")"


def check_links(folder: Path):
    errors = []
    for path in folder.rglob("*.md"):
        text = path.read_text(encoding="utf-8")
        for target in re.findall(r"(?<!!)\[[^\]\n]+\]\(([^\s)]+)\)", text):
            parts = urlsplit(target)
            if parts.scheme or parts.netloc:
                errors.append(f"{path.name}：阅读正文不应依赖外部链接：{target}")
                continue
            dest = (path.parent / unquote(parts.path)).resolve() if parts.path else path.resolve()
            if not inside(dest, folder.resolve()) or not dest.is_file():
                errors.append(f"{path.name}：内部链接不存在或越界：{target}")
            elif parts.fragment:
                contents = dest.read_text(encoding="utf-8")
                if f'id="{unquote(parts.fragment)}"' not in contents:
                    errors.append(f"{path.name}：章节锚点不存在：{target}")
    return errors


def render(work: Path, out: Path):
    report, state, packets, project = validate(work)
    if not report["passed"]:
        raise ValueError("验证未通过，未生成成品；请查看 validation-report.json")
    out = out.resolve()
    source = Path(state["root"])
    if inside(out, source) or inside(out, work.resolve()) or inside(work.resolve(), out):
        raise ValueError("成品目录必须独立于输入仓库和构建记录")
    if out.exists():
        raise ValueError("成品目录已存在；为避免覆盖，请选一个新版本目录")
    out.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".narrator-render-", dir=out.parent) as temp:
        folder = Path(temp) / "repository"
        folder.mkdir()
        locations, docpaths = {}, {}
        for packet in packets:
            doc = "模块/" + packet["source_file"] + ".md"
            docpaths[packet["source_file"]] = doc
            for index, section in enumerate(packet["sections"]):
                for unit in section["unit_ids"]:
                    locations.setdefault(unit, (doc, f"section-{index + 1}"))

        def write(name, text):
            target = folder / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(text.rstrip() + "\n", encoding="utf-8")

        for packet in packets:
            doc = docpaths[packet["source_file"]]
            lines = ['<a id="file-top"></a>', "# " + packet["title"], packet["overview"], "## 本文件的处理过程"]
            lines += ["- " + markdown_link(s["title"], "", f"section-{i + 1}") for i,s in enumerate(packet["sections"])]
            for index, section in enumerate(packet["sections"]):
                lines += [f'<a id="section-{index + 1}"></a>', "## " + section["title"],
                          "### 概览", section["summary"], "### 完整过程", section["body"]]
                if section.get("details", "").strip():
                    lines += ["### 进一步理解", section["details"]]
                for link in section.get("links", []):
                    target_file, anchor = locations[link["target"]]
                    rel = os.path.relpath(folder / target_file, (folder / doc).parent).replace("\\", "/")
                    lines.append(markdown_link(link["label"], rel, anchor))
            lines += [markdown_link("返回本文件目录", "", "file-top"), markdown_link("返回项目目录", os.path.relpath(folder / "项目目录.md", (folder / doc).parent).replace("\\", "/"))]
            write(doc, "\n\n".join(lines))
        index = ["# 项目目录"] + ["- " + markdown_link(p["title"], docpaths[p["source_file"]]) for p in packets]
        write("项目目录.md", "\n\n".join(index))
        by_path = {p["source_file"]: p for p in packets}
        route = ["# 阅读路线"] + [f"{i + 1}. " + markdown_link(by_path[p]["title"], docpaths[p]) for i, p in enumerate(project["reading_order"])]
        write("阅读路线.md", "\n\n".join(route))
        write("项目总览.md", "# " + project["title"] + "\n\n" + project["overview"] + "\n\n## 项目组成\n\n" + project["architecture"])
        for field, name in (("data", "数据说明"), ("dependencies", "依赖说明"), ("glossary", "术语说明")):
            write(name + ".md", "# " + name + "\n\n" + project[field])
        flow_lines = ["# 跨模块流程"]
        for flow in project["flows"]:
            flow_lines += ["## " + flow["title"], flow["body"]]
            seen = set()
            for unit in flow["unit_ids"]:
                dest = locations[unit]
                if dest not in seen:
                    flow_lines.append(markdown_link("深入阅读相关过程", dest[0], dest[1]))
                    seen.add(dest)
        write("跨模块流程.md", "\n\n".join(flow_lines))
        model = read_json(work / "model.json")
        write("架构与状态.md", render_model(model, lambda label, uid: markdown_link(label, *locations[uid])))
        write("行为验收.md", render_checks(model))
        write("未确定事项.md", "# 未确定事项\n\n" + ("\n\n".join(u["description"] for u in project["unknowns"]) or "本次生成没有记录尚未解决的行为问题。这不构成对程序正确性的证明。"))
        for item in state["files"]:
            if item["status"] == "supported" and Path(item["path"]).stem.upper() in {"LICENSE", "LICENCE", "COPYING", "NOTICE"}:
                raw = (source / item["path"]).read_bytes()
                if digest(raw) != item["sha256"]:
                    raise ValueError("许可原文在生成期间变化，请重新扫描")
                target = folder / "许可原文" / item["path"]
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(raw)
        exclusions = [f for f in state["files"] if f["status"] == "excluded"]
        scope = "\n\n".join("- " + f["path"] + "：" + f["reason"] for f in exclusions) or "无排除项。"
        methods = sorted({p["review"]["method"] for p in packets})
        write("版本与完整性说明.md", f"# 版本与完整性说明\n\n对应快照：{state['snapshot']}\n\n已处理 {report['files']} 个文件，正文承接 {report['units_covered']} 个结构。一致性检查已通过，不代表所有语义都已由人核实。\n\n复核方式：{'；'.join(methods)}。\n\n如输入含许可与通知原文，已同时保留在许可原文目录，中文说明不替代原文。\n\n## 排除范围\n\n{scope}\n\n输入变化后需要重新生成和复核；此版本不是实时工作区。")
        write("开始阅读.md", "# " + project["title"] + "\n\n这是一份可独立阅读的自然语言仓库。理解正文不需要查看源代码。\n\n" + "\n\n".join(markdown_link(name, name + ".md") for name in ("项目总览", "阅读路线", "项目目录", "架构与状态", "跨模块流程", "数据说明", "依赖说明", "术语说明", "行为验收", "未确定事项", "版本与完整性说明")) + "\n\n每个过程先给出概览，再给出完整过程和可选的进一步解释。只读概览不能替代对全部实现的理解。")
        link_errors = check_links(folder)
        if link_errors:
            raise ValueError("\n".join(link_errors))
        folder.rename(out)
    return {"output": str(out), "files": len(list(out.rglob("*.md"))), "snapshot": state["snapshot"]}


def main(argv=None):
    # The CLI emits machine-readable JSON, including Chinese paths, on Windows too.
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    init = sub.add_parser("scan", help="索引仓库，创建可续作的空翻译包")
    init.add_argument("root", type=Path)
    init.add_argument("--work", required=True, type=Path)
    init.add_argument("--exclude", action="append", default=[], help="相对路径 glob，可重复")
    init.add_argument("--profile", default="student", choices=["student", "developer", "domain"])
    for name in ("pending", "context", "architecture", "chunks", "review", "validate", "freshness", "render"):
        child = sub.add_parser(name)
        child.add_argument("--work", required=True, type=Path)
        if name == "context":
            child.add_argument("--file", required=True)
            child.add_argument("--chunk", help="仅返回指定分析分块的正文及所在定义")
        if name == "render":
            child.add_argument("--out", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        if args.command == "scan":
            result = scan(args.root, args.work, args.exclude, args.profile)
        elif args.command == "validate":
            result = validate(args.work)[0]
        elif args.command == "render":
            result = render(args.work, args.out)
        else:
            state, units = load(args.work)
            if args.command == "freshness":
                changed = freshness(args.work, state)
                result = {"passed": not changed, "changed_files": changed}
            elif args.command == "context":
                item = next((f for f in state["files"] if f["path"] == args.file and f["status"] == "supported"), None)
                if item is None:
                    raise ValueError("文件不在受支持清单内")
                path = Path(state["root"]) / args.file
                raw = path.read_bytes()
                if digest(raw) != item["sha256"]:
                    raise ValueError("文件已变化，请重新扫描")
                result = {"file": args.file, "sha256": item["sha256"], "packet": item["packet"],
                          "source": decode(raw, path.suffix.lower() == ".py"),
                          "units": [u for u in units if u["file"] == args.file]}
                graph_path = args.work / "repository-context.json"
                if not graph_path.exists():
                    raise ValueError("缺少跨文件上下文索引，请重新 scan")
                graph = verified_index(args.work, state, "repository-context.json", "context_sha256")
                changed = freshness(args.work, state)
                if graph.get("snapshot") != state["snapshot"] or changed:
                    raise ValueError("跨文件上下文已失效，请重新 scan：" + "、".join(changed))
                result["repository_context"] = neighborhood(graph, args.file)
                if args.file.endswith(".ipynb"):
                    result["cells"] = cells(result["source"])
                    result["notebook_policy"] = "按保存的单元格顺序理解；执行计数和历史输出不证明当前运行结果，未执行任何单元格。"
                    del result["source"]
                if args.chunk:
                    index = verified_index(args.work, state, "analysis-chunks.json", "chunks_sha256")
                    chunk = next((c for c in index["chunks"] if c["id"] == args.chunk and c["file"] == args.file), None)
                    if chunk is None:
                        raise ValueError("指定分块不存在或不属于当前文件")
                    result["chunk"] = chunk
                    source = result.get("source", "")
                    if "cells" in result:
                        source = next((c["source"] for c in result["cells"] if c["index"] == chunk["cell"]), "")
                        del result["cells"]
                    result["source"] = "\n".join(source.splitlines()[chunk["start_line"] - 1:chunk["end_line"]])
                    result["units"] = [u for u in result["units"] if u["id"] in chunk["unit_ids"]]
            elif args.command == "chunks":
                if freshness(args.work, state):
                    raise ValueError("源码已变化，请重新 scan")
                result = verified_index(args.work, state, "analysis-chunks.json", "chunks_sha256")
            elif args.command == "review":
                if freshness(args.work, state):
                    raise ValueError("源码已变化，请先重新 scan 并复核")
                project = read_json(args.work / "project.json")
                packets = [read_json(args.work / "translations" / f["packet"]) for f in state["files"] if f["status"] == "supported"]
                result = {"snapshot": state["snapshot"], "translation_sha256": content_hash(project, packets),
                          "model": read_json(args.work / "model.json"),
                          "instruction": "逐条核对架构、状态、依赖契约及正常/边界/失败问题。完成真实复核后才将指纹写入 model；本命令没有代替语义复核。"}
            elif args.command == "architecture":
                graph_path = args.work / "repository-context.json"
                if not graph_path.exists():
                    raise ValueError("缺少跨文件上下文索引，请重新 scan")
                graph = verified_index(args.work, state, "repository-context.json", "context_sha256")
                changed = freshness(args.work, state)
                if graph.get("snapshot") != state["snapshot"] or changed:
                    raise ValueError("跨文件上下文已失效，请重新 scan：" + "、".join(changed))
                result = graph
            else:
                result = {"snapshot": state["snapshot"], "profile": state["profile"], "files": state["files"],
                          "update_review": state.get("update_review"),
                          "report": validate(args.work)[0]}
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 1 if result.get("passed") is False else 0
    except (OSError, ValueError, TypeError, KeyError) as error:
        print(json.dumps({"error": str(error)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
