"""Rebuild the fully authored VisProg translation; never runs its ML code.

Requires upstream 9626868c0d1007c41d8f210fe99f5c1facc3325f at research/visprog.
This file assembles fixed prose written from that version, not arbitrary repos.
"""
import argparse
import ast
import importlib.util
from pathlib import Path

from visprog_prose import STEPS, UTILS, VIS, NMS, COMMON, GLOSSARY_EXTRA
from visprog_inputs import PROMPTS, DOCUMENTS, notebook_sections
from visprog_prompt_details import expanded_examples

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent
spec = importlib.util.spec_from_file_location("narrator", ROOT / "code-narrator/scripts/narrator.py")
n = importlib.util.module_from_spec(spec)
spec.loader.exec_module(n)


def build(out=None):
    source, work = ROOT / "research/visprog", BASE / "build-visprog"
    lock = n.read_json(BASE / "visprog-source-lock.json")
    if lock.get("hash_policy") != "sha256-lf-normalized":
        raise ValueError("无法识别固定样例哈希策略")
    for path, sha in lock["files"].items():
        # Git may convert LF to CRLF at checkout; preserve every other byte.
        if n.digest((source / path).read_bytes().replace(b"\r\n", b"\n")) != sha:
            raise ValueError("固定样例源码不符：" + path)
    n.scan(source, work, [], "student")
    state, units = n.load(work)
    supported_paths = {f["path"] for f in state["files"] if f["status"] == "supported"}
    if supported_paths != set(lock["files"]):
        raise ValueError("固定样例范围变化，需重新理解，不能复用固定译文")
    roots = {p: next(u["id"] for u in units if u["file"] == p and u["parent"] is None) for p in supported_paths}
    uidmap = {u["id"]: u for u in units}
    packets = []
    for item in state["files"]:
        if item["status"] != "supported":
            continue
        path = item["path"]
        own = [u for u in units if u["file"] == path]
        sections = []
        def section(title, body, members, details=""):
            if not members:
                raise ValueError("没有实际映射的章节：" + title)
            sections.append({"title": title, "summary": body.split("。", 1)[0] + "。", "body": body,
                             "details": details, "unit_ids": list(members), "evidence": list(members), "links": []})
        if path.endswith(".ipynb"):
            title, bodies = notebook_sections(Path(path).name)
            overview = "本入口按保存的单元格顺序描述一次完整任务，包括路径、凭据、模型、提示、图像、生成、执行和显示。单元格可被人在内核中另行乱序执行；保存的执行计数和输出不构成当前运行保证。"
            section("入口的阅读与执行顺序", overview, [roots[path]])
            for cell in n.cells((source / path).read_text(encoding="utf-8")):
                section("第" + str(cell["index"] + 1) + "个单元格", bodies[cell["index"]],
                        [u["id"] for u in own if u.get("cell") == cell["index"]])
        elif path in DOCUMENTS:
            title, overview = DOCUMENTS[path]
            section(title, overview, [u["id"] for u in own])
        else:
            data = STEPS if path == "engine/step_interpreters.py" else UTILS if path == "engine/utils.py" else VIS if path == "vis_utils.py" else None
            if data is None and path == "engine/nms.py":
                title, overview = "按置信度去掉重叠候选框", NMS
                section(title, overview, [u["id"] for u in own])
            elif path.startswith("prompts/"):
                key = Path(path).stem
                title, body, function = PROMPTS[key]
                overview = title + "。此模块只组织给模型的文字，不在导入时执行视觉任务。"
                def is_prompt_function(u):
                    while u.get("parent"):
                        if u.get("name") == "create_prompt":
                            return True
                        u = uidmap[u["parent"]]
                    return False
                section("保存的示例及其实际差异", body, [u["id"] for u in own if not is_prompt_function(u)])
                if function:
                    section("组装本次提示", function, [u["id"] for u in own if is_prompt_function(u)])
                data_ids = [u["id"] for u in own if u["kind"] == "Assign" and u["parent"] == roots[path]]
                step_classes = {"VQA":"VQAInterpreter","EVAL":"EvalInterpreter","RESULT":"ResultInterpreter",
                    "LOC":"Loc2Interpreter" if key == "knowtag" else "LocInterpreter", "COUNT":"CountInterpreter",
                    "CROP":"CropInterpreter","CROP_RIGHTOF":"CropRightOfInterpreter","CROP_LEFTOF":"CropLeftOfInterpreter",
                    "CROP_ABOVE":"CropAboveInterpreter","CROP_BELOW":"CropBelowInterpreter","CROP_BEHIND":"CropBehindInterpreter",
                    "SEG":"SegmentInterpreter","FACEDET":"FaceDetInterpreter","SELECT":"SelectInterpreter",
                    "COLORPOP":"ColorpopInterpreter","BGBLUR":"BgBlurInterpreter","REPLACE":"ReplaceInterpreter",
                    "EMOJI":"EmojiInterpreter","LIST":"ListInterpreter","CLASSIFY":"ClassifyInterpreter","TAG":"TagInterpreter"}
                for example_title, example_body, step_names in expanded_examples(source / path):
                    section(example_title, example_body, data_ids)
                    for step_name in step_names:
                        class_name = step_classes[step_name]
                        target = next(u["id"] for u in units if u["file"] == "engine/step_interpreters.py" and u.get("name") == class_name)
                        sections[-1]["links"].append({"target":target,"label":STEPS[class_name][0]})
                        sections[-1]["evidence"].append(target)
                if key == "imgedit":
                    section("表情缩写的精确对应", "提示开头把 :p 对应 face_with_tongue，把 8) 对应 smiling_face_with_sunglasses，把 :) 对应 smiling_face，把 ;) 对应 winking_face。这里左边是用户指令中的文字，右边是 AugLy 的 smileys 目录下素材名，不带 PNG 扩展名；提示示例据此选素材。它没有实现额外的缩写解析器，而是把对应关系交给生成模型理解。", data_ids)
            else:
                title = {"engine/step_interpreters.py": "全部视觉步骤与任务注册", "engine/utils.py": "程序生成、状态容器与逐行执行", "vis_utils.py": "图像、掩膜与推理过程展示"}[path]
                overview = data["__module__"][1]
                if path == "engine/step_interpreters.py":
                    overview += COMMON
                grouped = {}
                for u in own:
                    top = u
                    while top.get("parent") and uidmap[top["parent"]].get("parent") is not None:
                        top = uidmap[top["parent"]]
                    key = top.get("name") or "__module__"
                    grouped.setdefault(key, []).append(u["id"])
                if set(grouped) != set(data):
                    raise ValueError("定义与译文不符：" + path + repr(set(grouped) ^ set(data)))
                for key, ids in grouped.items():
                    name, body = data[key]
                    section(name, body, ids, COMMON if path == "engine/step_interpreters.py" and key.endswith("Interpreter") else "")
        packet = {"schema_version": 1, "source_file": path, "source_sha256": item["sha256"],
                  "title": title, "overview": overview, "sections": sections,
                  "review": {"status": "reviewed", "method": "Agent 对照固定提交的源码、全部 Notebook 保存单元格与提示逐项复核；未运行模型或远端服务"}}
        packets.append(packet)
    by_path = {p["source_file"]: p for p in packets}
    for packet in packets:
        path = packet["source_file"]
        related = (["engine/utils.py", "engine/step_interpreters.py"] if path.startswith("notebooks/") else
                   ["engine/utils.py", "vis_utils.py", "engine/nms.py"] if path == "engine/step_interpreters.py" else
                   ["engine/step_interpreters.py"] if path == "engine/utils.py" else [])
        if path.startswith("notebooks/"):
            related.append("prompts/" + {"gqa.ipynb": "gqa", "nlvr.ipynb": "nlvr", "image_editing.ipynb": "imgedit", "ok_det.ipynb": "knowtag"}[Path(path).name] + ".py")
        packet["sections"][0]["links"] = [{"target": roots[p], "label": by_path[p]["title"]} for p in related]
        packet["sections"][0]["evidence"] += [roots[p] for p in related]
        if path == "engine/step_interpreters.py":
            named = {u["name"]:u["id"] for u in units if u["file"] == path and u.get("name") and u["parent"] == roots[path]}
            pairs = {"Loc2Interpreter":["CountInterpreter","register_step_interpreters"],
                     "CountInterpreter":["LocInterpreter","Loc2Interpreter","register_step_interpreters"],
                     "register_step_interpreters":["LocInterpreter","Loc2Interpreter","CountInterpreter"],
                     "SelectInterpreter":["SegmentInterpreter","FaceDetInterpreter","ClassifyInterpreter"],
                     "ReplaceInterpreter":["SelectInterpreter","SegmentInterpreter"]}
            for section_data in packet["sections"]:
                for name, targets in pairs.items():
                    if named[name] in section_data["unit_ids"]:
                        section_data["links"] += [{"target":named[t],"label":STEPS[t][0]} for t in targets]
        n.write_json(work / "translations" / n.packet_name(path), packet)
    flows = [
        ("双图判断的一次完整任务", "两图入口先使仓库可导入、设置环境凭据，创建 nlvr 的三类步骤，固定使用全部十二条示例的提示。将两张骆驼图片缩略并转 RGB，放入共享状态。陈述被填到提示末尾，补全服务一次生成完整程序；概率指标被入口丢弃。执行器逐行解析步骤名并动态分派，问答写文字答案，表达式把 yes/no、数字与逻辑组合成结果，结果步骤只读状态。入口最后显示最终值和检查展示。任一加载、网络、格式、缺变量或展示失败都会中止，已写入的初始状态不会回滚。", ["notebooks/nlvr.ipynb", "prompts/nlvr.py", "engine/utils.py", "engine/step_interpreters.py"]),
        ("单图组合问答", "单图入口选 gqa，全部提示描述定位、计数、裁图、问答和表达式的组合。默认问题是图中人或动物总数。定位保存候选框以及伴随画框图，计数从框取长度，裁图只看首框并可能直接复用原图，问答读取当前图像；表达式组合中间答案。所有状态按变量名在同一字典流动，坐标相对于当时被裁的图，而不是自动映回原图。示例中部分变量名和表达式有错误，生成器没有验证修复。", ["notebooks/gqa.ipynb", "prompts/gqa.py", "engine/step_interpreters.py", "engine/nms.py"]),
        ("按指令编辑图像", "编辑入口选 imageEdit，注册时即加载分割、图文选择、人脸及修补能力，包括固定 CUDA 修补管线。把静态提示填入本次换砖墙指令，生成程序。分割或人脸检测形成带框和掩膜对象，选择保留原对象引用，保色与模糊按掩膜混图，表情按框叠图，修补只取第一对象并原地阈值化其掩膜。修改结果以新状态名保存，可再被后续分割和编辑使用。结果步骤读取最终图，检查展示失败也可能发生在状态写入后。", ["notebooks/image_editing.ipynb", "prompts/imgedit.py", "engine/step_interpreters.py", "vis_utils.py"]),
        ("外部知识目标标注", "标注入口选 okDet，将模板默认列表上限填成二十。默认要标注宝莱坞演员。生成程序通常通过人脸检测或对象定位形成候选，由列表步骤再调用另一旧补全模型列知识类别，分类按图文余弦相似度原地附加类别与分数，每类挑一个对象，然后在图像副本画框和文字。单类别先追加 other，零或负分可能留下空项，字体路径也可能使绘图失败。列表的请求上限没有作为硬性截断。", ["notebooks/ok_det.ipynb", "prompts/knowtag.py", "engine/step_interpreters.py", "engine/utils.py"]),
    ]
    project = {"schema_version": 1, "snapshot": state["snapshot"], "title": "VisProg 完整自然语言仓库",
        "overview": "对应 allenai/visprog 提交 9626868c0d1007c41d8f210fe99f5c1facc3325f。这是通过语言模型编排视觉工具的研究系统：输入图片与一句问题或指令，生成整段小程序，再逐行执行得到答案或编辑图，并显示中间过程。此译本涵盖全部 Python、四个 Notebook、提示、环境与项目文本，不需阅读源码来理解已保存实现。二进制示例图片只作为输入或说明素材登记，不把画面内容当算法。本次没有下载模型、安装此研究环境或调用远端服务，具体运行边界在各过程说明。",
        "architecture": "四个 Notebook 是真实入口，不存在自动启动的统一命令。它们负责准备路径、凭据、图像、任务与提示。提示层给出少量示例或静态模板；核心层保存程序与共享状态、请求补全、逐行调度；步骤层实现任务登记和每个视觉或普通运算；底层小工具做框去重和图像展示。登记表是动态分派的关键：任务名决定可用步骤，程序每行的名字再决定调用哪个对象。导入关系不能替代这个执行关系。",
        "reading_order": ["README.md", "notebooks/nlvr.ipynb", "engine/utils.py", "prompts/nlvr.py", "engine/step_interpreters.py", "engine/nms.py", "vis_utils.py", "notebooks/gqa.ipynb", "prompts/gqa.py", "notebooks/image_editing.ipynb", "prompts/imgedit.py", "notebooks/ok_det.ipynb", "prompts/knowtag.py", "environment.yaml", ".gitignore", "LICENSE"],
        "flows": [{"title": t, "body": b, "unit_ids": [roots[p] for p in paths]} for t,b,paths in flows],
        "data": "初始状态是由入口创建的字典，图像存于 IMAGE 或 LEFT、RIGHT。Program 和每行小程序都引用它，解释器对它逐步增加文字答案、计数、框、对象和图像；失败不恢复旧值。普通定位的框伴随 _IMAGE 展示图，Loc2 却只存带 box、category 的对象。分割与人脸对象还含 mask 和实例编号。选择后的列表复用原对象，分类添加 class 与 class_score 会反映到源列表；修补阈值化 mask 会改写源数组。RESULT 只读指定项，不建立左侧输出名。最终返回最后一行结果和整个状态。表达式的格式化字典是另建的，但不构成执行隔离。图像框坐标有闭区间计算与 Pillow 排他裁剪的混用，具体边界见各过程。",
        "dependencies": "环境声明 Python 三点十、OpenAI 客户端零点二十三点零、Transformers 四点二十七点二、Diffusers 零点十四点零、Pillow 九点二点零等，详见环境译文。生成器请求 text-davinci-003，列表步骤请求 text-davinci-002；这些是固定代码中的旧补全调用，不能承诺今天服务仍可用。视觉处理分别依赖 BLIP 问答、OWL-ViT 开放词汇框检测、MaskFormer 分割、CLIP 图文特征、人脸检测与 Stable Diffusion 图像修补。处理器负责将输入转换成张量，模型从预训练标识加载并可能联网取权重；设评估模式与关闭梯度不会保证预测正确。CLIP 这里用自己归一化特征后的点积作为余弦分数，不是校准概率。修补中的白掩膜指需要生成替换的区域、黑色表示保留的区域，项目另有阈值和缩放处理。torch、NumPy 未独立锁定；修补无 CPU 回退、展示有 Linux 字体路径，都是运行条件。本文已经展开项目实际如何调用依赖，权重内部训练细节不属于此仓库实现。",
        "glossary": "状态是按名字保存中间对象的共享字典，引用表示多个位置指向同一对象。动态分派是先读步骤名称，再查登记表决定用哪个处理对象。候选框描述目标矩形，掩膜为每个像素提供区域权重。交并比是两框交叠面积占联合面积的比例；非极大值抑制优先留高分、去掉重叠候选。图文特征是模型生成的数值表示，归一化点积用于衡量匹配，但并非正确概率。提示示例通过上下文引导生成，不会在导入时自动执行。token 是模型分割文字的单位。梯度用于学习，本项目关闭它进行推理，不训练这些模型。Notebook 内核保存变量，乱序或重复执行会影响状态；本译本按保存顺序说明。",
        "unknowns": []}
    project["glossary"] += GLOSSARY_EXTRA
    n.write_json(work / "project.json", project)
    model = create_model(n, state, units, packets, project, roots)
    n.write_json(work / "model.json", model)
    report = n.validate(work)[0]
    n.write_json(ROOT / "docs/visprog-final-validation.json", report)
    if not report["passed"]:
        raise ValueError(report["errors"])
    if out:
        print(n.render(work, out))
    else:
        print(report)


def create_model(n, state, units, packets, project, roots):
    def ev(path, name=None):
        return next(u["id"] for u in units if u["file"] == path and (u.get("name") == name if name else u["parent"] is None))
    step = "engine/step_interpreters.py"
    definitions = [
        ("entry", "四类任务入口", [p for p in roots if p.startswith("notebooks/")], "准备路径、环境、图像、任务和提示，生成与执行程序，再显示结果。"),
        ("prompt", "任务提示", [p for p in roots if p.startswith("prompts/")], "保存全部示例与模板，按入口参数组装本次提示；不执行示例。"),
        ("core", "程序与执行核心", ["engine/utils.py"], "请求旧补全接口、统计生成指标，持有共享状态，按程序行动态分派。"),
        ("steps", "任务登记和实际步骤", [step], "登记任务可用能力，解析参数，做视觉推理、图像编辑、表达式和状态读写。"),
        ("nms", "框去重", ["engine/nms.py"], "按分数优先级和严格交并比条件去除重叠框。"),
        ("display", "展示工具", ["vis_utils.py"], "缩图、编码图像、绘掩膜、排网格及拼接展示文字。"),
        ("meta", "环境与项目文本", ["README.md", "environment.yaml", "LICENSE", ".gitignore"], "说明安装、用法、扩展、依赖、版本规则与上游许可。"),
    ]
    components = [{"id": i,"title":t,"files":sorted(files),"role":b,"evidence":[roots[p] for p in sorted(files)]} for i,t,files,b in definitions]
    relation_data = [("entry","prompt","调用","问答入口固定 all；编辑和标注入口插入指令，标注默认上限二十。"),
        ("entry","core","调用","创建生成器与任务解释器，传入同一初始状态并开启检查执行。"),
        ("core","steps","动态分派","任务名先决定登记表，行中的步骤名再查表调用；未知任务无最终错误分支，未知步骤引发键错误。"),
        ("steps","nms","调用","普通对象检测按阈值筛候选后用交并比去重；Loc2 调低两项阈值。"),
        ("steps","display","调用","制作检查图文；部分图片即使关闭检查仍会制作，展示失败可能在写状态后发生。")]
    comp_ev = {c["id"]:c["evidence"] for c in components}
    relations = [{"from":a,"to":b,"kind":k,"behavior":v,"evidence":comp_ev[a]+comp_ev[b]} for a,b,k,v in relation_data]
    checks_data = [
        ("normal","NLVR 入口用几条示例？","使用全部十二条；入口覆盖了默认随机八条。","两图入口与提示译文明确区分默认和实际参数。",[ev("notebooks/nlvr.ipynb"),ev("prompts/nlvr.py","create_prompt")]),
        ("normal","程序经过 RESULT 后还有指令，会不会停止？","继续执行，返回最后一行结果；RESULT 不保存左侧名。","执行器与结果步骤译文均明确这两项行为。",[ev("engine/utils.py","ProgramInterpreter"),ev(step,"ResultInterpreter")]),
        ("boundary","定位框的交并比恰好等于阈值会保留吗？","不会，只有严格小于阈值才留到下一轮。","框去重译文给出严格条件和闭区间面积。",[ev("engine/nms.py","nms")]),
        ("boundary","上下裁图在没有框时取哪部分？","两者实际都取左半图。","两种裁图译文保留实现差异，没有按名称补写上下半图。",[ev(step,"CropAboveInterpreter"),ev(step,"CropBelowInterpreter")]),
        ("boundary","只给分类一个候选类别会怎样？","局部查询先加 other；后面的单类别特例通常不可达。","分类译文说明新增候选、不可达分支和无固定类顺序。",[ev(step,"ClassifyInterpreter")]),
        ("state","分类和修补是否只改新结果？","分类原地加类名与分数；修补原地改第一对象 mask；共享引用能观察这些修改。","数据说明和两个步骤译文均说明引用与写入。",[ev(step,"ClassifyInterpreter"),ev(step,"ReplaceInterpreter")]),
        ("failure","中途失败是否恢复初始字典？","不恢复；已写状态仍在，后续行不执行。","程序容器和执行核心说明同一引用与无回滚。",[ev("engine/utils.py","Program"),ev("engine/utils.py","ProgramInterpreter")]),
        ("failure","COUNT 开检查却缺伴随图会怎样？","先保存数量，读取 _IMAGE 时键错误。","计数译文按实际写入和展示顺序说明失败。",[ev(step,"CountInterpreter")]),
        ("failure","只做表情编辑，注册时可以完全不加载修补吗？","不可以；imageEdit 全部立即实例化，修补固定 CUDA 可能先失败。","注册和修补初始化译文揭示任务级加载成本。",[ev(step,"register_step_interpreters"),ev(step,"ReplaceInterpreter")]),
        ("boundary","没有结束符时生成概率统计包含最后一个 token 吗？","不包含，切片终点取最后下标，漏掉该项。","生成器译文说明这个边界及空列表失败。",[ev("engine/utils.py","ProgramGenerator")]),
        ("dependency","列表上限是否保证最终列表不超长？","不保证，只有文字提示且按逗号空格拆分，没有截断。","列表译文明确模型请求与确定性限制的区别。",[ev(step,"ListInterpreter")]),
        ("failure","提示示例是否完全正确？","不是；有错变量、错参数大小写、拼接字符串、无效表达式和目标替换不符。","四个提示译文逐一说明这些差异。",[roots[p] for p in roots if p.startswith("prompts/")]),
    ]
    method = "同一 Agent 对照固定源码与全文完成静态行为问答核查；另用隔离的算法契约测试验证可离线执行的边界；未作独立人类研究或视觉模型端到端测试"
    journeys = []
    for f in project["flows"]:
        journeys.append({"title":f["title"], "steps":[
            {"component":"entry","behavior":"入口选择任务、准备图像状态和提示参数。","failure":"路径、凭据、导入或注册模型失败时中止。","evidence":f["unit_ids"]},
            {"component":"core","behavior":"生成整段程序，再以共享状态按行执行。具体路径："+f["body"],"failure":"没有自动程序修复或回滚，异常中止后续步骤。","evidence":f["unit_ids"]},
            {"component":"steps","behavior":"登记步骤读取并写入共享状态，按需产生检查展示。","failure":"格式、缺字段、推理或展示失败向外传播。","evidence":[ev(step,"register_step_interpreters")]}]})
    return {"schema_version":1,"snapshot":state["snapshot"],"translation_sha256":n.content_hash(project,packets),
        "components":components,"relations":relations,"state_policy":project["data"],
        "state":[{"name":"跨行共享状态","lifecycle":project["data"],"aliasing":"入口字典、整段程序和每行小程序为同一引用，失败不会回滚。","readers":["entry","core","steps"],"writers":["entry","steps"],"evidence":[ev("engine/utils.py","Program"),ev("engine/utils.py","ProgramInterpreter")]},
                 {"name":"候选对象与掩膜的共享内容","lifecycle":"分割或人脸检测创建对象，选择与分类沿用对象；执行完仍保留在状态。","aliasing":"选择不复制字典，分类原地写字段，修补直接修改 mask 数组。","readers":["steps"],"writers":["steps"],"evidence":[ev(step,"SelectInterpreter"),ev(step,"ClassifyInterpreter"),ev(step,"ReplaceInterpreter")]}],
        "contracts":[{"name":"图文模型与预训练加载","version":"Transformers 四点二十七点二，权重标识见各步骤。","behavior":"处理器准备图像和文字张量；预训练载入可能联网；项目按余弦分数选择，不是正确概率。","failure":"下载、设备、内存与推理失败没有自动恢复。","evidence":[ev(step,"VQAInterpreter"),ev(step,"LocInterpreter"),ev(step,"SelectInterpreter")]},
                     {"name":"图像修补","version":"Diffusers 零点十四点零与 fp16 模型修订。","behavior":"白色掩膜对应重绘区域，使用五十步、引导尺度七点五；项目先缩放填充，未固定随机种子。","failure":"固定 CUDA 无 CPU 回退，空对象、尺寸与模型失败传播。","evidence":[ev(step,"ReplaceInterpreter")]},
                     {"name":"远端补全","version":"仓库锁 OpenAI 零点二十三点零客户端，属于旧接口调用。","behavior":"生成器和列表步骤一次请求第一条补全，不验证或自动修错。","failure":"不能保证现时远端模型可用，网络和接口失败传播。","evidence":[ev("engine/utils.py","ProgramGenerator"),ev(step,"ListInterpreter")]}],
        "journeys":journeys,"checks":[{"kind":k,"question":q,"expected":e,"observed":o,"evidence":v,"method":method,"status":"passed"} for k,q,e,o,v in checks_data],
        "review":{"status":"reviewed","method":method}}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path)
    build(parser.parse_args().out)
