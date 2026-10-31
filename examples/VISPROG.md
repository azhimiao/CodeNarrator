# VisProg 的来源与复现

上游：[allenai/visprog](https://github.com/allenai/visprog/tree/9626868c0d1007c41d8f210fe99f5c1facc3325f)。固定提交：9626868c0d1007c41d8f210fe99f5c1facc3325f。许可：Apache-2.0；原文保留在 third_party/visprog-LICENSE.txt 和独立成品的许可原文目录。

在项目根目录准备输入，检出固定版本后构建：

```powershell
git clone https://github.com/allenai/visprog.git research/visprog
git -C research/visprog checkout 9626868c0d1007c41d8f210fe99f5c1facc3325f
python examples/build_visprog.py
python examples/build_visprog.py --out F:/VisProg自然语言仓库新版本
python -m unittest discover -s tests -v
```

build 首先核对 visprog-source-lock.json 的每个源文件哈希和全部支持范围。固定文件哈希使用 LF 规范化策略，只消除 Git 在不同系统检出时产生的 CRLF 差异，其余字节必须完全匹配固定上游；构建快照仍绑定实际输入字节。上游内容变化时直接拒绝复用固定译文，不能只改提交号或哈希假装重新翻译。未带 --out 时只复现构建资料和验证；成品目录已存在时不会覆盖。

此次输入包含 16 份文本文件：4 份核心/展示 Python、4 份提示 Python、4 份 Notebook 和 4 份项目文本。7 张图片作为输入和说明素材登记，Git 目录排除。提取 2105 个结构，划分 68 个阅读片段，最终生成 28 份 Markdown，另保留上游许可原文。全部步骤类型及其方法、4 个任务注册分支、41 个 Notebook 保存单元格、55 段提示示例的逐行自然语言过程与实际错例均有对应说明。

固定编写资料在 visprog_prose.py、visprog_inputs.py 与 build_visprog.py。这些是针对上述提交由 Agent 对照实际源码编写的自然语言资料，不是通用模型输出器；真正使用 Skill 翻译新项目时，Agent 要重新读取其全部实现并编写新资料。

tests/test_visprog_contracts.py 隔离抽取上游的一小组定义，验证共享状态、结果步骤、错误后写入、无框裁图、分类、概率和坏示例等可离线验证的行为。不导入原项目顶层视觉依赖，不下载权重，不触发模型推理或远端补全。它不能代替整套模型端到端测试。
