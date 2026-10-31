"""Bounded reading slices with lexical ancestry and full structural coverage."""
import hashlib
from notebooks import cells


def build_chunks(root, records, units, decode, limit=160):
    result = []
    for item in records:
        if item["status"] != "supported":
            continue
        path = item["path"]
        text = decode((root / path).read_bytes(), path.endswith(".py"))
        local = [u for u in units if u["file"] == path]
        sources = [(c["index"], c["source"]) for c in cells(text)] if path.endswith(".ipynb") else [(None, text)]
        for cell, source in sources:
            count = max(1, len(source.splitlines()))
            # Prefer definition boundaries when they fit. A huge function is
            # sliced explicitly and its enclosing definitions accompany it.
            starts = {1, count + 1}
            starts.update(u["start_line"] for u in local if u.get("cell") == cell and
                          u["kind"] in {"FunctionDef", "AsyncFunctionDef", "ClassDef"})
            cursor = 1
            while cursor <= count:
                choices = [v for v in starts if cursor < v <= cursor + limit]
                end = max(choices) - 1 if choices else min(count, cursor + limit - 1)
                members = [u["id"] for u in local if u.get("cell") == cell and cursor <= u["start_line"] <= end]
                ancestors = [{k: u.get(k) for k in ("id", "kind", "name", "start_line", "end_line")}
                             for u in local if u.get("cell") == cell and u["kind"] in {"ClassDef", "FunctionDef", "AsyncFunctionDef"}
                             and u["start_line"] < cursor <= u["end_line"]]
                key = f"{path}:{cell}:{cursor}:{end}"
                result.append({"id": hashlib.sha256(key.encode()).hexdigest()[:20], "file": path,
                               "cell": cell, "start_line": cursor, "end_line": end,
                               "unit_ids": members, "enclosing_definitions": ancestors})
                cursor = end + 1
        if path.endswith(".ipynb"):
            # The Notebook container has no cell; keep it explicit in the index.
            result.append({"id": local[0]["id"], "file": path, "cell": None,
                           "start_line": 1, "end_line": 1, "unit_ids": [local[0]["id"]],
                           "enclosing_definitions": [], "container": True})
    return {"schema_version": 1, "max_lines": limit, "chunks": result}
