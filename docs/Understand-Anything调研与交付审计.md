# Understand Anything 调研与 CodeNarrator 交付审计

本文件记录当时的真实缺口与参考研究。随后已补齐 Notebook、分块、结构化理解记录、VisProg 全文和行为验收，当前交付以 [V1 验收记录](V1验收记录.md) 为准。保留原审计内容用于追踪，不把历史判断伪装成当时已经完成。

日期：2026-10-31。

## 结论与交付更正

上一轮开发没有实际调研 Understand Anything。虽然文档列出了参考项目，交付中并没有它的源码分析、复用决策或与本项目目标的差异论证。

已有实现是一个可运行的 Skill 原型：扫描、AST 结构定位、翻译包、覆盖检查、Markdown 生成、快照和安装机制已实现；示例正文由 Agent 根据源码编写。它没有充分实现或验证全仓库理解、架构组织、跨模块数据流以及完整自然语言翻译的语义验收。

此前“项目完成”的结论撤回。15 项工具与示例测试通过是真实结果，但不能被扩大为已经实现产品目标。

## 本次实际查看的资料

Understand Anything 固定提交：`4e6d3299017a7432da15957874992837a315c5b4`。本地只读调研副本位于 research/understand-anything。本次查看源码与规范，没有运行其完整 Agent 流水线、安装其 Node 依赖或验证其宣传效果。

| 来源 | 实际核查内容 |
|---|---|
| [项目扫描规范](https://github.com/Egonex-AI/Understand-Anything/blob/4e6d3299017a7432da15957874992837a315c5b4/understand-anything-plugin/agents/project-scanner.md) | 确定性扫描、语言与类别、内部导入映射，与模型生成项目描述的职责分工 |
| [导入提取实现](https://github.com/Egonex-AI/Understand-Anything/blob/4e6d3299017a7432da15957874992837a315c5b4/understand-anything-plugin/skills/understand/extract-import-map.mjs) | Tree-sitter 与分语言路径候选解析；为输入文件生成内部 importMap |
| [分批实现](https://github.com/Egonex-AI/Understand-Anything/blob/4e6d3299017a7432da15957874992837a315c5b4/understand-anything-plugin/skills/understand/compute-batches.mjs) | 基于关联组织批次、提取外部邻居符号、文件读取及失败处理 |
| [文件分析规范](https://github.com/Egonex-AI/Understand-Anything/blob/4e6d3299017a7432da15957874992837a315c5b4/understand-anything-plugin/agents/file-analyzer.md) | 先提取结构，再结合 neighborMap 生成摘要与关系；摘要粒度通常为一到两句 |
| [架构分析规范](https://github.com/Egonex-AI/Understand-Anything/blob/4e6d3299017a7432da15957874992837a315c5b4/understand-anything-plugin/agents/architecture-analyzer.md) | 目录分组、依赖方向、入出度、非代码关系，之后再做语义架构划分 |
| [阅读路线规范](https://github.com/Egonex-AI/Understand-Anything/blob/4e6d3299017a7432da15957874992837a315c5b4/understand-anything-plugin/agents/tour-builder.md) | 从入口候选、依赖链与关键节点设计学习顺序 |
| [领域分析规范](https://github.com/Egonex-AI/Understand-Anything/blob/4e6d3299017a7432da15957874992837a315c5b4/understand-anything-plugin/agents/domain-analyzer.md) | 领域、流程、步骤三个层次及实现位置对应 |
| [图审查规范](https://github.com/Egonex-AI/Understand-Anything/blob/4e6d3299017a7432da15957874992837a315c5b4/understand-anything-plugin/agents/graph-reviewer.md) | 节点与边格式、引用完整性、分层覆盖、重复与孤立节点检查 |
| [指纹实现](https://github.com/Egonex-AI/Understand-Anything/blob/4e6d3299017a7432da15957874992837a315c5b4/understand-anything-plugin/packages/core/src/fingerprint.ts) | 内容哈希、函数与类结构指纹，以及用于图更新的变化分类 |
| [增量准备](https://github.com/Egonex-AI/Understand-Anything/blob/4e6d3299017a7432da15957874992837a315c5b4/understand-anything-plugin/skills/understand/prepare-incremental.mjs) | 更新计划、变更文件、基线与增量符号记录 |
| [主流程](https://github.com/Egonex-AI/Understand-Anything/blob/4e6d3299017a7432da15957874992837a315c5b4/understand-anything-plugin/skills/understand/SKILL.md) | 扫描、分批、分析、合并、架构、路线、校验与保存之间如何传递上下文 |

上游采用 MIT 许可证。本次没有复制其代码；独立实现了下面列明的 Python 有限范围机制。以后如直接引入其代码，需要保留相应版权与许可。

## 真正值得借鉴的内容

最重要的是建立可以复用、审查和持续修正的项目模型，再组织语义内容。

1. 文件分析前提供项目内部导入关系，避免每次从零猜测。
2. 文件所在批次之外仍保留关联文件与符号，减少局部分析丢失全局上下文。
3. 架构分层以实际关系、结构信号和局部语义为依据，不仅按目录名称写介绍。
4. 阅读顺序有入口和依赖链依据，不只是把文件名排成列表。
5. 配置、部署、数据和测试也进入项目模型。
6. 合并与复核检查关系引用和范围，不只检查每个文件有没有摘要。

这些机制与最终是否绘图无关。CodeNarrator 可以在内部使用结构模型，最终仍输出独立的纯自然语言仓库。

## 不能直接等同的能力

Understand Anything 的节点摘要、知识图和导览提供架构理解基础；其文件分析规范要求的简短摘要不等于本项目要求的完整实现翻译。不能直接导出这些摘要，就声称用户无需源码也能理解所有条件、数据变化与失败路径。

上游图更新的结构指纹着重记录签名、导入、定义等结构，其目的与语句级自然语言维护不同。例如仅修改比较阈值或异常处理，即使函数签名不变，也可能让译文失效。CodeNarrator 必须保留内容级变化检查，不能照搬“结构未变便无需重译”的思路。

同样，内部导入边不等于实际调用边，调用边不等于数据流，目录群组不等于架构层，图引用完整也不等于语义正确。这些概念在工具与报告中必须区分。

## 对现有实现的逐项审计

| 能力 | 上一轮实际情况 | 本次修正 | 仍未完成 |
|---|---|---|---|
| 项目导入模型 | 只有 AST 单元，没有跨文件解析 | 增加 Python 根目录与常见 src 布局的导入候选、相对导入、别名与反向引用 | 完整运行时路径、动态导入与重导出解析 |
| 文件上下文 | context 返回当前文件和单元 | 现在提供导入记录、邻居顶层符号、反向引用和未解析调用位置 | 参数来源、共享状态与返回值消费的结构化模型 |
| 分批组织 | 依靠 Agent 自行组织 | 增加按关联邻域和源码行数预算组织批次，超大文件显式标记 | 大文件按逻辑单元分块、跨块状态衔接 |
| 语义架构 | project.architecture 为自由文本 | 新增结构证据查询及明确的架构分析规范 | 可校验的模块职责、分层与证据模型 |
| 跨模块执行 | 自由文本 flows 与单元列表 | 现在要求先核查正常与异常路径并回查局部说明 | 调用候选、分派条件、数据与状态的完整追踪和验证 |
| 阅读路线 | 文件路径列表 | 增加真实入口语法线索、依赖关系和人工语义判断规范 | 路线依据和学习依赖的结构化验收 |
| 完整性 | 有编号即计覆盖 | 明确其只是机械统计，并增加语义反例审计 | 对正文是否实际表达完整行为的可靠验收 |
| 科研项目验证 | 自编示例和极小 sampleproject | 实际扫描原定 VisProg 并读取 NLVR 关键路径 | VisProg 全仓库自然语言译本与独立阅读验收 |

本次没有把这些未完成项重新包装为“新版本已完成”。

## 可重复的覆盖率反例

执行 `python research/audit_coverage.py`：在隔离副本中把示例的全部章节内容替换为“这个部分负责处理项目中的信息”，保留真实单元 ID、哈希和依据引用。

实际结果：机械验证仍通过，62/62 个结构被计为覆盖。完整结果保存在 [coverage-audit-result.json](coverage-audit-result.json)。

这不是用另一个更复杂的正则规则就能解决的问题。它证明当前验证器检查了记录的结构，尚未证明正文承接了相应语义；review.method 也是复核声明，不能代替独立检查。不能再拿这些百分比作为“完整自然语言仓库已实现”的结论。

## 原定 VisProg 上的实际核查

固定提交：`9626868c0d1007c41d8f210fe99f5c1facc3325f`，来源 [allenai/visprog](https://github.com/allenai/visprog/tree/9626868c0d1007c41d8f210fe99f5c1facc3325f)。只读代码与 Notebook 的源单元，没有运行模型、安装依赖或请求 API。

扫描记录 24 项，其中 12 个受支持文件，4 个不支持的 Notebook，其余为排除项。受支持内容提取 1,903 个结构；核心解释器文件 1,380 行。以上是范围与规模记录，不是已翻译数量。

新增导入分析识别出执行器工具到解释器集合、解释器集合到抑制算法与可视化工具的关系。但关键任务由 Notebook 进入，且处理步骤按注册表动态分派，单纯 import 图无法表达完整执行路径。

已实际核查 NLVR 路径：

- Notebook 创建任务解释器，并把 NLVR 的全部示例绑定为提示生成方式；不能只按提示函数本身的默认“随机八个”来解释此处行为。
- 创建 NLVR 解释器时就建立 VQA、表达式计算和结果提取三个处理器；其中视觉问答处理器的初始化会准备模型。不能解释成某个步骤第一次运行时才创建全部处理器。
- 两张图像进入初始共享状态。生成器先生成程序文本；执行器按行建立步骤对象，各步骤共享同一个状态对象，后续步骤能够读取前面写入的结果。
- 每一步先解析操作名，再从任务注册表选择处理器。实际方法必须结合注册表和任务类型确定，不能只说“执行 execute”。
- 检查模式改变处理器返回内容，并把各步可视化片段串起来；程序执行返回最后一步输出及状态，检查模式另返回可视化内容。
- 表达式处理器会转换部分字符串值、替换异或文本并代入状态，然后使用求值机制；它不是一个可随意概括为“安全表达式计算”的实现。

这几项事实需要把 Notebook、提示函数、执行器、注册表和具体处理器合起来读。当前工具仍不支持把 Notebook 作为结构化翻译输入，也未解析注册表、状态写入和动态调用链，因此尚未满足原定科研项目验收。

## 本次代码变化与验证

新增 scripts/repository_context.py：独立实现导入候选、反向引用、邻居符号、调用位置、目录组、入口语法线索和关联批次。scan 保存该模型及其哈希；context 检查整个快照，避免仅当前文件未变时返回已过期的邻居信息。architecture 命令提供结构证据，明确不声称自动得出语义架构。

新增六项真实行为测试，覆盖相对导入、src 布局、别名、反向关系、多候选、外部未知、动态调用边界、分批、邻居变化失效与入口语法。累计 21 项测试通过。它们验证新增机制，不证明完整仓库语义翻译已完成。

## 接下来的实现依据

优先补可检查的架构、流程和状态模型，以及 Notebook 和大文件分块；然后以 VisProg 的 NLVR 实际链路逐层展开为自然语言，检验读者能否独立回答涉及参数覆盖、分派、共享状态和错误路径的问题。

Skill 仍保持轻量，确定性部分组织结构证据，宿主 Agent 承担语义理解。验收需要真实科研仓库的正文与行为问题，不能再用安装成功、导出成功或工具测试数量替代。
