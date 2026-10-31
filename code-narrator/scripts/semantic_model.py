"""Evidence-backed authoring records. Validation checks consistency, not truth."""
import hashlib
import json
from collections import Counter


def content_hash(project, packets):
    payload = {"project": project, "translations": sorted(packets, key=lambda p: p["source_file"])}
    return hashlib.sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


def validate_model(model, state, units, project, packets, prose):
    errors = []
    known = {u["id"]: u for u in units}
    paths = {f["path"] for f in state["files"] if f["status"] == "supported"}
    if not isinstance(model, dict):
        return ["语义模型必须是对象"]
    if model.get("snapshot") != state["snapshot"] or model.get("schema_version") != 1:
        errors.append("语义模型快照或版本不符")
    if model.get("translation_sha256") != content_hash(project, packets):
        errors.append("译文已变化或尚未完成语义复核；请重新核查 model.json，不能仅刷新指纹")

    def entries(key, required=False):
        value = model.get(key)
        if not isinstance(value, list) or (required and not value):
            errors.append(f"语义模型 {key} 需要{'非空' if required else ''}列表")
            return []
        if any(not isinstance(v, dict) for v in value):
            errors.append(f"语义模型 {key} 每项需要对象")
        return [v for v in value if isinstance(v, dict)]

    def fields(obj, names, label):
        for key in names:
            prose(obj.get(key), label + "." + key, errors)

    def evidence(obj, label):
        ids = obj.get("evidence")
        if not isinstance(ids, list) or not ids or any(not isinstance(i, str) or i not in known for i in ids):
            errors.append(label + " 缺少有效源码依据")

    components = entries("components", True)
    ids = [c.get("id") for c in components if isinstance(c.get("id"), str) and c["id"]]
    if len(set(ids)) != len(components):
        errors.append("架构组件标识缺失或重复")
    ownership = Counter()
    for component in components:
        fields(component, ("title", "role"), "组件")
        evidence(component, "组件")
        files = component.get("files")
        if not isinstance(files, list) or not files or any(not isinstance(f, str) or f not in paths for f in files):
            errors.append("组件需列出有效文件")
        else:
            ownership.update(files)
            ev_files = {known[e]["file"] for e in component.get("evidence", []) if e in known}
            if not set(files) <= ev_files:
                errors.append("组件的依据未涵盖其全部文件")
    if set(ownership) != paths or any(n != 1 for n in ownership.values()):
        errors.append("架构组件须恰好承接每个范围内文件一次")
    for relation in entries("relations"):
        fields(relation, ("kind", "behavior"), "关系")
        if relation.get("from") not in ids or relation.get("to") not in ids:
            errors.append("关系引用了不存在的组件")
        evidence(relation, "关系")
    for item in entries("state"):
        fields(item, ("name", "lifecycle", "aliasing"), "状态")
        for field in ("readers", "writers"):
            refs = item.get(field)
            if not isinstance(refs, list) or any(ref not in ids for ref in refs):
                errors.append("状态读写者必须引用组件")
        evidence(item, "状态")
    prose(model.get("state_policy"), "状态追踪结论", errors)
    for contract in entries("contracts"):
        fields(contract, ("name", "version", "behavior", "failure"), "依赖契约")
        evidence(contract, "依赖契约")
    for journey in entries("journeys", True):
        fields(journey, ("title",), "执行路线")
        steps = journey.get("steps")
        if not isinstance(steps, list) or not steps:
            errors.append("执行路线需包含步骤")
            continue
        for step in steps:
            if not isinstance(step, dict):
                errors.append("执行路线步骤需为对象")
                continue
            fields(step, ("behavior", "failure"), "执行步骤")
            if step.get("component") not in ids:
                errors.append("执行步骤引用了不存在的组件")
            evidence(step, "执行步骤")
    checks = entries("checks", True)
    if not {"normal", "boundary", "failure"} <= {c.get("kind") for c in checks}:
        errors.append("行为验收至少需要正常、边界和失败问题")
    for check in checks:
        fields(check, ("question", "expected", "observed", "method"), "行为验收")
        evidence(check, "行为验收")
        if check.get("status") != "passed":
            errors.append("仍有未通过的行为验收")
    review = model.get("review", {})
    if not isinstance(review, dict) or review.get("status") != "reviewed":
        errors.append("语义模型尚未复核")
    else:
        fields(review, ("method",), "模型复核")
    return errors


def render_model(model, link):
    lines = ["# 架构与状态", model["state_policy"]]
    for c in model["components"]:
        lines += ["## " + c["title"], c["role"]]
        lines += [link("深入阅读相关实现", e) for e in c["evidence"]]
    titles = {c["id"]: c["title"] for c in model["components"]}
    lines += ["## 组件关系"]
    for r in model["relations"]:
        lines += [titles[r["from"]] + " → " + titles[r["to"]] + "：" + r["behavior"]]
    for s in model["state"]:
        lines += ["## " + s["name"], s["lifecycle"], s["aliasing"],
                  "读取方：" + "、".join(titles[i] for i in s["readers"]),
                  "写入方：" + "、".join(titles[i] for i in s["writers"])]
    for j in model["journeys"]:
        lines += ["## " + j["title"]]
        for i, s in enumerate(j["steps"], 1):
            lines += [f"{i}. {s['behavior']}\n\n失败边界：{s['failure']}"]
    for c in model["contracts"]:
        lines += ["## " + c["name"] + "的使用契约", "版本依据：" + c["version"], c["behavior"], c["failure"]]
    return "\n\n".join(lines)


def render_checks(model):
    lines = ["# 行为验收", "这些是本版本实际记录的问题、预期和对照结果。复核方式如下，不代表已经开展人类理解实验。", model["review"]["method"]]
    for c in model["checks"]:
        lines += ["## " + c["question"], "源码行为预期：" + c["expected"],
                  "译文对照结果：" + c["observed"], "检查方式：" + c["method"]]
    return "\n\n".join(lines)
