# 真实仓库验证输入

上游：PyPA sampleproject，来源 https://github.com/pypa/sampleproject ，提交 621e4974ca25ce531773def586ba3ed8e736b3fc，分发版本 4.0.0，MIT 许可证。

本次完整扫描 12 个仓库文件，另记录版本控制目录为排除项。范围包括运行代码、测试、构建配置、说明文档、许可、忽略规则、数据和两项自动化定义，不仅是核心函数。

准备输入后可以复现翻译：

```powershell
git clone https://github.com/pypa/sampleproject.git examples/real-sampleproject
git -C examples/real-sampleproject checkout 621e4974ca25ce531773def586ba3ed8e736b3fc
python examples/build_real_demo.py
python code-narrator/scripts/narrator.py render --work examples/build-sampleproject --out examples/sampleproject自然语言仓库新版本
```

如果输出已存在，换用新版本目录。固定译文由 Agent 根据此提交编写，未使用模板自动推断实现语义。

实际仅运行上游标准库测试，不安装上游的运行依赖，不运行 nox、不触发 GitHub 工作流、不发布包。自动化章节翻译其声明、步骤和已知边界，不宣称远端执行成功。

原始上游文件和许可仍保留。许可原文另存于第三方归属目录，和纯自然语言阅读产物分离。
