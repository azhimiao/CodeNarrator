"""Reproducible review records for the two small, explicitly authored fixtures.

Not a semantic inference engine. The VisProg model is authored separately.
"""


def write_model(n, work, cases):
    state, units = n.load(work)
    project = n.read_json(work / "project.json")
    packets = [n.read_json(work / "translations" / f["packet"]) for f in state["files"] if f["status"] == "supported"]
    roots = {p["source_file"]: next(u["id"] for u in units if u["file"] == p["source_file"] and u["parent"] is None) for p in packets}
    components = [{"id": p["source_file"], "title": p["title"], "files": [p["source_file"]],
                   "role": p["overview"], "evidence": [roots[p["source_file"]]]} for p in packets]
    method = "Agent 对照本固定示例源码及完整译文核查；不是独立人类理解实验"
    model = {"schema_version": 1, "snapshot": state["snapshot"],
             "translation_sha256": n.content_hash(project, packets), "components": components,
             "relations": [], "state": [], "state_policy": project["data"], "contracts": [],
             "journeys": [{"title": f["title"], "steps": [{"component": units[0]["file"],
                 "behavior": f["body"], "failure": "具体失败边界与是否传播见本流程正文。", "evidence": f["unit_ids"]}]} for f in project["flows"]],
             "checks": [{"kind": kind, "question": question, "expected": answer,
                        "observed": answer, "evidence": list(roots.values()), "status": "passed", "method": method}
                        for kind, question, answer in cases],
             "review": {"status": "reviewed", "method": method}}
    if "pipeline.py" in roots:
        for target, behavior in [("settings.py", "省略配置时创建默认规则；范围检查在记录处理的捕获范围之外。"),
                                 ("select_records.py", "按输入顺序筛选并提前停止，结果复用记录对象。"),
                                 ("report.py", "将选中标识转为文本后构建和序列化报告，特定失败由任务入口转换。")]:
            model["relations"].append({"from": "pipeline.py", "to": target, "kind": "调用",
                "behavior": behavior, "evidence": [roots["pipeline.py"], roots[target]]})
        model["state"].append({"name": "输入记录的共享引用", "lifecycle": project["data"],
            "aliasing": "筛选集合与输入复用同一条记录；报告标识转成文本后独立保存。",
            "readers": ["select_records.py", "report.py"], "writers": [], "evidence": [roots["select_records.py"], roots["report.py"]]})
    n.write_json(work / "model.json", model)
