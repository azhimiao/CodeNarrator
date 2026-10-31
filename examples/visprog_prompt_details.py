"""Natural-language rendering rules for the fixed VisProg prompt mini-language.

Only this fixture's declared step types are supported. No target code is run;
literal strings are read with AST, and every declarative example is expanded.
"""
import ast
import re


def value(node):
    if isinstance(node, ast.Name):
        return "状态“" + node.id + "”"
    if isinstance(node, ast.Constant):
        if node.value is None:
            return "专用空值 None"
        return "文字“" + str(node.value) + "”" if isinstance(node.value, str) else str(node.value)
    if isinstance(node, ast.Set) and len(node.elts) == 1 and isinstance(node.elts[0], ast.Name) and node.elts[0].id == "list_max":
        return "模板中的可变列表上限，标注入口填为二十"
    raise ValueError("固定提示中出现未解释的值：" + ast.dump(node))


def expression(text):
    replaced = re.sub(r"\{(\w+)\}", r"\1", text).replace(" xor ", " != ")
    try:
        tree = ast.parse(replaced, mode="eval").body
    except SyntaxError:
        if replaced == "'yes' if ANSWER0 > 0 and else 'no'":
            return "本想在 ANSWER0 大于零时选文字 yes，否则选文字 no，但大于零条件之后还写了英文 and，其后没有右侧条件就接 else，因此表达式语法无效，实际执行会失败"
        raise
    def explain(node):
        if isinstance(node, (ast.Name, ast.Constant)):
            return value(node)
        if isinstance(node, ast.Compare):
            words = {ast.Eq:"等于",ast.NotEq:"不等于",ast.Gt:"大于",ast.GtE:"大于或等于",ast.Lt:"小于",ast.LtE:"小于或等于"}
            return explain(node.left) + "，" + "，并且".join(words[type(op)] + explain(other) for op,other in zip(node.ops,node.comparators))
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
            return "把" + explain(node.left) + "与" + explain(node.right) + "相加"
        if isinstance(node, ast.BoolOp):
            return ("全部为真：" if isinstance(node.op, ast.And) else "至少一个为真：") + "；".join(explain(v) for v in node.values)
        if isinstance(node, ast.IfExp):
            return "如果" + explain(node.test) + "，则取" + explain(node.body) + "，否则取" + explain(node.orelse)
        raise ValueError("固定提示中出现未解释的表达式：" + ast.dump(node))
    result = explain(tree)
    if " xor " in text:
        result += "；模板原文使用 xor，表达式步骤会将其改成不等比较，用于两项真假异或"
    return result


def step_sentence(node):
    if not isinstance(node, ast.Assign) or len(node.targets) != 1 or not isinstance(node.targets[0], ast.Name) or not isinstance(node.value, ast.Call):
        raise ValueError("固定提示中出现未解释的程序行")
    target = node.targets[0].id
    name = node.value.func.id
    args = {k.arg:k.value for k in node.value.keywords}
    read = lambda key: value(args[key])
    if name == "RESULT":
        return "读取" + read("var") + "作为本行结果；本行虽给出左侧名称“" + target + "”，结果步骤不将它写入状态，也不令执行器提前停止。"
    if name == "EVAL":
        action = "把表达式参数作为文字交给组合求值步骤：" + expression(ast.literal_eval(args["expr"]))
    elif name == "VQA":
        image_key = "image" if "image" in args else "Image"
        action = "向图像问答提供" + read(image_key) + "，问题原文为" + read("question")
        if image_key == "Image":
            action += "；但此行图像参数写成大写 Image，读取器只读取小写 image，所以照此执行会发生缺参数键错误"
        if "Disney's Frozen" in ast.literal_eval(args["question"]):
            action += "；另一个独立问题是原始示例把 Disney's 的单引号直接放进单引号问题文字中，没有转义。使用 CPython 三点十点十四官方词法实现核查时，question 实际只取到英文 Does the image have a bag with the characters from Disney，其后的 s 与 Frozen、on 与 it、问号与单引号被错配为三个额外参数。左图步骤会把截短的问题交给模型，额外参数没有被本步骤读取；右图仍先因大写 Image 缺少小写 image 而失败。另在当前 CPython 三点十二点十四运行时逐行核查，这两行均直接产生 TokenError，报告字符串未结束。其他版本没有逐一验证，不能仅按“新旧”推断行为；以上分别说明实际核查过的两个版本，不影响声明三点十环境的解释。本段保留原始错误，没有替示例修正"
    elif name == "LOC":
        action = "在" + read("image") + "中定位目标" + read("object") + "；采用本任务登记的定位类型，几何保留词和对象包装差异见定位译文"
    elif name == "COUNT":
        action = "统计" + read("box") + "的列表长度"
    elif name.startswith("CROP"):
        action = "以" + read("image") + "为图，使用" + read("box") + "按步骤“" + name + "”的实际裁剪规则取图；只处理首框，具体空框与别名行为见裁图译文"
    elif name in {"SEG", "FACEDET"}:
        action = ("对" + read("image") + ("做全景分割" if name == "SEG" else "做人脸检测") + "，产生带框、类别与掩膜的对象列表")
    elif name == "SELECT":
        action = "从" + read("object") + "选择对象，图像取" + read("image") + "，查询参数为" + read("query") + "，类别参数为" + read("category") + "；保留原对象引用"
    elif name in {"COLORPOP", "BGBLUR"}:
        action = "以" + read("image") + "和对象" + read("object") + ("制作局部保色图" if name == "COLORPOP" else "制作背景模糊图")
    elif name == "EMOJI":
        action = "在" + read("image") + "上，按" + read("object") + "中的框覆盖表情素材" + read("emoji")
    elif name == "REPLACE":
        action = "以" + read("image") + "为原图，只用" + read("object") + "的第一个对象掩膜修补，修补文字为" + read("prompt") + "；该掩膜会被原地阈值化"
    elif name == "LIST":
        action = "向列表补全服务请求主题" + read("query") + "，文字中的最多项数为" + read("max") + "，没有硬性截断"
    elif name == "CLASSIFY":
        action = "以图像" + read("image") + "、对象列表" + read("object") + "和类别列表" + read("categories") + "进行图文分类，会改写原对象的类别与分数"
    elif name == "TAG":
        action = "复制" + read("image") + "，按" + read("object") + "的类别与分数画框和标签"
    else:
        raise ValueError("固定提示中出现未解释的步骤：" + name)
    return action + "；本行左侧输出名称为“" + target + "”，成功时由该步骤按前文契约写入状态。"


def expanded_examples(path):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    literal = ast.literal_eval(next(node.value for node in tree.body if isinstance(node, ast.Assign)))
    texts = literal if isinstance(literal, list) else [literal]
    result = []
    for text in texts:
        # A missing comma in GQA joins two example blocks in one string.
        pieces = re.split(r"(?m)^(?:Statement|Question|Instruction):\s*", text)
        for piece in pieces[1:]:
            if "\nProgram:" not in piece:
                raise ValueError("固定提示缺少程序标记")
            request, program = piece.split("\nProgram:", 1)
            if not program.strip():
                continue  # final placeholder for the current user request
            # Decode the known broken literal solely to describe its intended
            # fields. step_sentence explicitly records the original lexical
            # failure/truncation, verified with CPython 3.10's own tokenizer.
            nodes = ast.parse(program.strip().replace("Disney's", "Disney\\'s")).body
            body = "这条示例给生成模型的输入原文为“" + request.strip() + "”。以下完整说明其保存的各行，按顺序解释；它们是提示内的文字，不会在导入时执行。"
            for i,node in enumerate(nodes, 1):
                body += "\n\n第" + str(i) + "步：" + step_sentence(node)
            result.append(("逐步展开示例" + str(len(result)+1), body, sorted({node.value.func.id for node in nodes})))
    return result
