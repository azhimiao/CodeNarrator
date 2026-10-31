# 可复核的架构、状态与行为记录

`scan` 创建空的 `model.json`。这是 Agent 的理解记录，不是静态分析器已经证明的结论；最终由渲染器转成自然语言“架构与状态”和“行为验收”。文件名、编号、依据保留在构建记录，读者沿自然语言内链阅读。

各对象的 `evidence` 均为非空真实单元 ID 列表，来自 `units.json` 或 context；可以跨文件。角色或组件关系要用具体定义支撑，不能凭名称编造。文件必须恰好归属一个组件；可把多个实现文件归为一个职责组件。文档、配置也须归属，可独立成组件。

| 字段 | 内容 |
|---|---|
| schema_version | 整数 1 |
| snapshot | 当前 manifest.snapshot |
| translation_sha256 | `review` 返回的本次项目包与全部文件包的内容指纹；完成真实复核之后填写 |
| components | 非空列表，每项含 id、title、files、role、evidence；files 为范围内相对路径 |
| relations | 列表，每项含 from、to、kind、behavior、evidence；前两项引用组件 id，明确调用、动态分派或数据关系 |
| state_policy | 状态流动与共享的总体结论；无运行状态时说明原因 |
| state | 列表，每项含 name、lifecycle、aliasing、readers、writers、evidence；读写方引用组件 id，外部调用者写入可在正文中说明 |
| contracts | 列表，每项含 name、version、behavior、failure、evidence；版本未锁定也应明确，而不是假定最新版行为 |
| journeys | 非空列表，每项有 title 和非空 steps；每步含 component、behavior、failure、evidence |
| checks | 非空列表，每项含 kind、question、expected、observed、method、evidence、status；至少含 normal、boundary、failure 三类，通过状态为 passed |
| review | status 为 reviewed，method 如实记录实际复核方法与范围 |

行为问题先依据源码确定预期，随后遮住源码，从完整译本中查出答案，记录具体自然语言章节与观察结果。适合的题目包括默认配置被入口如何覆盖、边界相等是否保留、返回值与状态是否一致、对象是否复制、异常后留下哪些写入、依赖是否在初始化时加载、展示失败是否改变结果状态。没有此类行为的资料仓库可根据其实际用途选择正常、边界与失败情景，不能编造运行过程。

每一步的失败边界要说明在哪里中断、哪些内容已改变、是否恢复。不能只写“可能报错”。组件归属与证据的检查防止漏项与悬空引用；内容指纹使修改后的正文不能继续沿用旧复核。它们无法判断 reviewer 的声明是否真实，更不能证明自然语言绝无误解。若问题答不出，修正文并重新复核后再获取新指纹。

Notebook 状态需要同时区分“保存顺序的一次运行”和“用户在内核中可重复、乱序运行”。`units.cell` 从零开始，行号在各自单元格内计数。特殊命令必须解释其实际作用；整单元格 magic 是不透明源内容，由 Agent 查明其契约，不冒充 Python AST 深度覆盖。原始输出仅供发现上下文，不能当作当前运行证据。

内容指纹不包含 model 自身，避免自引用；改动模型仍要按实际影响复核。最终 manifest、结构/分块/邻域指纹、来源文件哈希、项目快照和译文复核指纹分别检查不同的一致性边界。
