"""Notebook source indexing, without executing cells or trusting stored outputs."""
import hashlib
import io
import json
import tokenize


def cells(text):
    book = json.loads(text)
    if book.get("nbformat") != 4 or not isinstance(book.get("cells"), list):
        raise ValueError("仅支持 nbformat 4 Notebook")
    metadata = book.get("metadata", {})
    language = metadata.get("language_info", {}).get("name") or metadata.get("kernelspec", {}).get("language")
    if language and language.lower() not in {"python", "python3"}:
        raise ValueError("Notebook 内核语言不受支持：" + str(language))
    result = []
    for index, cell in enumerate(book["cells"]):
        kind = cell.get("cell_type")
        if kind not in {"code", "markdown", "raw"}:
            raise ValueError(f"单元格 {index} 的类型不支持")
        source = cell.get("source", "")
        if isinstance(source, list) and all(isinstance(x, str) for x in source):
            source = "".join(source)
        if not isinstance(source, str):
            raise ValueError(f"单元格 {index} 的 source 不是文本")
        result.append({"index": index, "kind": kind, "source": source,
                       "execution_count": cell.get("execution_count"),
                       "stored_output_types": [x.get("output_type") for x in cell.get("outputs", [])]})
    return result


def python_source(source):
    """Replace standalone IPython directives with pass, retaining source lines.

    Cell magics own the whole cell. They are retained as an opaque directive,
    never parsed as Python. Multiline string contents must stay untouched.
    """
    lines = source.splitlines(keepends=True)
    protected = set()
    try:
        for token in tokenize.generate_tokens(io.StringIO(source).readline):
            if token.type == tokenize.STRING:
                protected.update(range(token.start[0], token.end[0] + 1))
    except (tokenize.TokenError, IndentationError):
        # AST parsing below still rejects malformed Python, rather than skipping it.
        pass
    directives = []
    for i, line in enumerate(lines, 1):
        stripped = line.lstrip()
        if i in protected or not stripped.startswith(("%", "!", "?")):
            continue
        if stripped.startswith("%%"):
            return "", [{"line": i, "end_line": len(lines), "text": source, "cell_magic": True}]
        directives.append({"line": i, "end_line": i, "text": line.rstrip(), "cell_magic": False})
        lines[i - 1] = line[:len(line) - len(stripped)] + "pass\n"
    return "".join(lines), directives


def extract_notebook(path, text, extract):
    root_id = hashlib.sha256((path + ":notebook").encode()).hexdigest()[:20]
    units = [{"id": root_id, "file": path, "kind": "Notebook", "name": None,
              "parent": None, "cell": None, "start_line": 1, "end_line": 1,
              "start_byte": 0, "end_byte": None}]
    for cell in cells(text):
        virtual = path + "::cell-" + str(cell["index"])
        normalized, directives = python_source(cell["source"]) if cell["kind"] == "code" else ("", [])
        found = extract(virtual, normalized if cell["kind"] == "code" else cell["source"], cell["kind"] == "code")
        found[0]["kind"] = "NotebookCell"
        found[0]["parent"] = root_id
        for unit in found:
            unit.update(file=path, cell=cell["index"])
            if unit["kind"] == "Pass" and any(d["line"] == unit["start_line"] for d in directives):
                unit["kind"] = "NotebookDirective"
        if directives and directives[0]["cell_magic"]:
            found[0]["end_line"] = max(1, len(cell["source"].splitlines()))
        units.extend(found)
    return units


def graph_source(text):
    return "\n".join(python_source(c["source"])[0] for c in cells(text) if c["kind"] == "code")
