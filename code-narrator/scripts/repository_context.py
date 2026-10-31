"""Conservative Python import candidates and bounded cross-file context.

Design reference: Understand Anything's pre-resolved importMap and neighborMap.
Implemented independently with the stdlib AST; no upstream source copied.
This indexes syntax, not Python's runtime import path, call graph or data flow.
"""
from __future__ import annotations

import ast
from collections import defaultdict, deque
from pathlib import Path, PurePosixPath
from notebooks import graph_source


def build_context(root: Path, files: list[dict], decode, max_batch_lines=600) -> dict:
    sources = {}
    for item in files:
        if item["status"] != "supported" or not item["path"].endswith((".py", ".ipynb")):
            continue
        text = decode((root / item["path"]).read_bytes(), item["path"].endswith(".py"))
        if item["path"].endswith(".ipynb"):
            text = graph_source(text)
        sources[item["path"]] = (text, ast.parse(text, filename=item["path"]))
    names = defaultdict(set)
    for path in sources:
        if path.endswith(".ipynb"):
            continue
        parts = list(PurePosixPath(path).with_suffix("").parts)
        if parts[-1] == "__init__":
            parts.pop()
        if parts:
            names[".".join(parts)].add(path)
        if parts and parts[0] == "src":
            names[".".join(parts[1:])].add(path)

    dependencies = {path: set() for path in sources}
    imports, exported, calls = {}, {}, {}
    for path, (text, tree) in sources.items():
        imports[path], calls[path] = [], []
        exported[path] = [
            {"name": node.name, "kind": type(node).__name__, "line": node.lineno}
            for node in tree.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
        ]
        package = list(PurePosixPath(path).parent.parts)
        if package and package[0] == "src":
            package = package[1:]
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                calls[path].append({"expression": ast.unparse(node.func), "line": node.lineno,
                                    "status": "unresolved"})
            if not isinstance(node, (ast.Import, ast.ImportFrom)):
                continue
            if isinstance(node, ast.Import):
                queries = [(alias.name, alias.asname or alias.name.split(".")[0], None) for alias in node.names]
            else:
                base = node.module or ""
                if node.level:
                    # Relative imports cannot climb above the containing package.
                    if not package or node.level > len(package):
                        imports[path].append({"line": node.lineno, "module": base, "status": "unresolved_relative",
                                              "candidates": [], "bindings": [a.asname or a.name for a in node.names]})
                        continue
                    prefix = package[:len(package) - node.level + 1]
                    base = ".".join(prefix + ([base] if base else []))
                queries = [(base, alias.asname or alias.name, alias.name) for alias in node.names]
            for module, binding, symbol in queries:
                candidates = set(names.get(module, set()))
                # `from pkg import child` can refer to a submodule or a re-export.
                if symbol and symbol != "*":
                    candidates.update(names.get(module + "." + symbol, set()))
                status = "internal_candidate" if candidates else "external_or_unresolved"
                imports[path].append({"line": node.lineno, "module": module, "binding": binding,
                                      "symbol": symbol, "status": status, "candidates": sorted(candidates)})
                dependencies[path].update(candidates - {path})

    reverse = {path: set() for path in sources}
    for path, targets in dependencies.items():
        for target in targets:
            reverse[target].add(path)
    groups = defaultdict(list)
    for item in files:
        if item["status"] == "supported":
            path = PurePosixPath(item["path"])
            groups[str(path.parent)].append(item["path"])
    # Connected neighborhoods keep related files together, bounded by source lines.
    # They are work scheduling suggestions, not inferred architectural layers.
    remaining, batches = set(sources), []
    while remaining:
        queue = deque([min(remaining)])
        batch, lines = [], 0
        while queue:
            path = queue.popleft()
            if path not in remaining:
                continue
            count = len(sources[path][0].splitlines())
            if batch and lines + count > max_batch_lines:
                continue
            remaining.remove(path)
            batch.append(path)
            lines += count
            queue.extend(sorted((dependencies[path] | reverse[path]) & remaining))
        batches.append({"files": batch, "source_lines": lines, "oversized": lines > max_batch_lines})

    entry_candidates = []
    for path, (_, tree) in sources.items():
        if path.endswith(".ipynb"):
            entry_candidates.append({"file": path, "line": 1, "reason": "notebook_saved_cell_order"})
        for node in tree.body:
            if isinstance(node, ast.If) and isinstance(node.test, ast.Compare):
                test = node.test
                if (isinstance(test.left, ast.Name) and test.left.id == "__name__" and
                        len(test.ops) == 1 and isinstance(test.ops[0], ast.Eq) and
                        len(test.comparators) == 1 and isinstance(test.comparators[0], ast.Constant) and
                        test.comparators[0].value == "__main__"):
                    entry_candidates.append({"file": path, "line": node.lineno, "reason": "main_guard"})
    return {
        "schema_version": 1,
        "basis": "Python AST syntax and repository-relative/root-src module candidates",
        "limitations": ["不等于运行时导入解析；未执行目标代码", "不解析修改 sys.path、动态导入、重导出与插件注册",
                        "call_sites 只是调用位置，不是已解析调用图", "目录组和分析批次不代表语义架构层",
                        "Notebook 图中行号为拼接代码视图；精确源码映射请用带 cell 的 units 和 chunks"],
        "imports": imports,
        "dependencies": {p: sorted(v) for p, v in sorted(dependencies.items())},
        "dependents": {p: sorted(v) for p, v in sorted(reverse.items())},
        "symbols": exported, "call_sites": calls,
        "directory_groups": dict(sorted(groups.items())), "batches": batches,
        "entry_candidates": entry_candidates,
    }


def neighborhood(graph: dict, path: str) -> dict:
    neighbors = set(graph["dependencies"].get(path, [])) | set(graph["dependents"].get(path, []))
    return {
        "imports": graph["imports"].get(path, []),
        "imports_from": graph["dependencies"].get(path, []),
        "imported_by": graph["dependents"].get(path, []),
        "neighbors": [{"file": p, "symbols": graph["symbols"].get(p, [])} for p in sorted(neighbors)],
        "call_sites": graph["call_sites"].get(path, []),
        "limitations": graph["limitations"],
    }
