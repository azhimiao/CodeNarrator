<a id="file-top"></a>

# 外部知识标注的十三段示例提示

外部知识标注的十三段示例提示。此模块只组织给模型的文字，不在导入时执行视觉任务。

## 本文件的处理过程

- [保存的示例及其实际差异](#section-1)

- [逐步展开示例1](#section-2)

- [逐步展开示例2](#section-3)

- [逐步展开示例3](#section-4)

- [逐步展开示例4](#section-5)

- [逐步展开示例5](#section-6)

- [逐步展开示例6](#section-7)

- [逐步展开示例7](#section-8)

- [逐步展开示例8](#section-9)

- [逐步展开示例9](#section-10)

- [逐步展开示例10](#section-11)

- [逐步展开示例11](#section-12)

- [逐步展开示例12](#section-13)

- [逐步展开示例13](#section-14)

<a id="section-1"></a>

## 保存的示例及其实际差异

### 概览

本文件只保存多行提示文字，要求逐步执行指令。

### 完整过程

本文件只保存多行提示文字，要求逐步执行指令。每例先取得对象，再让语言模型列候选类别，用图文分类选类，最后在图上画标签并读取结果。十三例依次标注美国总统的人脸、野生动物、鞋的颜色、鞋的类型、上限明确为四种的鞋类型、奥斯卡获奖好莱坞演员的人脸、菜肴的菜系、可饮水的器具、含蓝色的商标、上限明确为十种的此类商标、领导人人脸所代表的国家、哈利波特演员的人脸且列表上限一、白雪公主七个小矮人的人脸且上限七。人脸题使用人脸检测，其余题按野生动物、鞋、菜、器具、商标的文字目标做开放词汇检测。

未明确数字的示例都留有 list_max 插值位置，Notebook 将它填成二十；明确四、十、一、七的示例不被这个默认替换。末尾再填 instruction。列表数量只是提示请求，不是结果截断；分类每类最多保留一项且可能有空项，并不保证把所有目标逐一可靠标完。模板在导入时不联网，真正补全发生在生成器和列表步骤。

<a id="section-2"></a>

## 逐步展开示例1

### 概览

这条示例给生成模型的输入原文为“Tag the presidents of US”。

### 完整过程

这条示例给生成模型的输入原文为“Tag the presidents of US”。以下完整说明其保存的各行，按顺序解释；它们是提示内的文字，不会在导入时执行。

第1步：对状态“IMAGE”做人脸检测，产生带框、类别与掩膜的对象列表；本行左侧输出名称为“OBJ0”，成功时由该步骤按前文契约写入状态。

第2步：向列表补全服务请求主题文字“presidents of the US”，文字中的最多项数为模板中的可变列表上限，标注入口填为二十，没有硬性截断；本行左侧输出名称为“LIST0”，成功时由该步骤按前文契约写入状态。

第3步：以图像状态“IMAGE”、对象列表状态“OBJ0”和类别列表状态“LIST0”进行图文分类，会改写原对象的类别与分数；本行左侧输出名称为“OBJ1”，成功时由该步骤按前文契约写入状态。

第4步：复制状态“IMAGE”，按状态“OBJ1”的类别与分数画框和标签；本行左侧输出名称为“IMAGE0”，成功时由该步骤按前文契约写入状态。

第5步：读取状态“IMAGE0”作为本行结果；本行虽给出左侧名称“FINAL_RESULT”，结果步骤不将它写入状态，也不令执行器提前停止。

[给候选对象分配类别并每类取一项](../engine/step_interpreters.py.md#section-30)

[检测并扩大人脸为带掩膜的对象](../engine/step_interpreters.py.md#section-27)

[用语言模型列出外部知识候选](../engine/step_interpreters.py.md#section-29)

[读取指定状态作为步骤结果](../engine/step_interpreters.py.md#section-8)

[把分类标签和框画到图像副本](../engine/step_interpreters.py.md#section-31)

<a id="section-3"></a>

## 逐步展开示例2

### 概览

这条示例给生成模型的输入原文为“Tag the wild animals”。

### 完整过程

这条示例给生成模型的输入原文为“Tag the wild animals”。以下完整说明其保存的各行，按顺序解释；它们是提示内的文字，不会在导入时执行。

第1步：在状态“IMAGE”中定位目标文字“wild animal”；采用本任务登记的定位类型，几何保留词和对象包装差异见定位译文；本行左侧输出名称为“OBJ0”，成功时由该步骤按前文契约写入状态。

第2步：向列表补全服务请求主题文字“wild animals”，文字中的最多项数为模板中的可变列表上限，标注入口填为二十，没有硬性截断；本行左侧输出名称为“LIST0”，成功时由该步骤按前文契约写入状态。

第3步：以图像状态“IMAGE”、对象列表状态“OBJ0”和类别列表状态“LIST0”进行图文分类，会改写原对象的类别与分数；本行左侧输出名称为“OBJ1”，成功时由该步骤按前文契约写入状态。

第4步：复制状态“IMAGE”，按状态“OBJ1”的类别与分数画框和标签；本行左侧输出名称为“IMAGE0”，成功时由该步骤按前文契约写入状态。

第5步：读取状态“IMAGE0”作为本行结果；本行虽给出左侧名称“FINAL_RESULT”，结果步骤不将它写入状态，也不令执行器提前停止。

[给候选对象分配类别并每类取一项](../engine/step_interpreters.py.md#section-30)

[用语言模型列出外部知识候选](../engine/step_interpreters.py.md#section-29)

[为外部知识标注提供对象列表](../engine/step_interpreters.py.md#section-11)

[读取指定状态作为步骤结果](../engine/step_interpreters.py.md#section-8)

[把分类标签和框画到图像副本](../engine/step_interpreters.py.md#section-31)

<a id="section-4"></a>

## 逐步展开示例3

### 概览

这条示例给生成模型的输入原文为“Tag the shoes with their colors”。

### 完整过程

这条示例给生成模型的输入原文为“Tag the shoes with their colors”。以下完整说明其保存的各行，按顺序解释；它们是提示内的文字，不会在导入时执行。

第1步：在状态“IMAGE”中定位目标文字“shoe”；采用本任务登记的定位类型，几何保留词和对象包装差异见定位译文；本行左侧输出名称为“OBJ0”，成功时由该步骤按前文契约写入状态。

第2步：向列表补全服务请求主题文字“colors”，文字中的最多项数为模板中的可变列表上限，标注入口填为二十，没有硬性截断；本行左侧输出名称为“LIST0”，成功时由该步骤按前文契约写入状态。

第3步：以图像状态“IMAGE”、对象列表状态“OBJ0”和类别列表状态“LIST0”进行图文分类，会改写原对象的类别与分数；本行左侧输出名称为“OBJ1”，成功时由该步骤按前文契约写入状态。

第4步：复制状态“IMAGE”，按状态“OBJ1”的类别与分数画框和标签；本行左侧输出名称为“IMAGE0”，成功时由该步骤按前文契约写入状态。

第5步：读取状态“IMAGE0”作为本行结果；本行虽给出左侧名称“FINAL_RESULT”，结果步骤不将它写入状态，也不令执行器提前停止。

[给候选对象分配类别并每类取一项](../engine/step_interpreters.py.md#section-30)

[用语言模型列出外部知识候选](../engine/step_interpreters.py.md#section-29)

[为外部知识标注提供对象列表](../engine/step_interpreters.py.md#section-11)

[读取指定状态作为步骤结果](../engine/step_interpreters.py.md#section-8)

[把分类标签和框画到图像副本](../engine/step_interpreters.py.md#section-31)

<a id="section-5"></a>

## 逐步展开示例4

### 概览

这条示例给生成模型的输入原文为“Tag the shoes by their type”。

### 完整过程

这条示例给生成模型的输入原文为“Tag the shoes by their type”。以下完整说明其保存的各行，按顺序解释；它们是提示内的文字，不会在导入时执行。

第1步：在状态“IMAGE”中定位目标文字“shoe”；采用本任务登记的定位类型，几何保留词和对象包装差异见定位译文；本行左侧输出名称为“OBJ0”，成功时由该步骤按前文契约写入状态。

第2步：向列表补全服务请求主题文字“type of shoes”，文字中的最多项数为模板中的可变列表上限，标注入口填为二十，没有硬性截断；本行左侧输出名称为“LIST0”，成功时由该步骤按前文契约写入状态。

第3步：以图像状态“IMAGE”、对象列表状态“OBJ0”和类别列表状态“LIST0”进行图文分类，会改写原对象的类别与分数；本行左侧输出名称为“OBJ1”，成功时由该步骤按前文契约写入状态。

第4步：复制状态“IMAGE”，按状态“OBJ1”的类别与分数画框和标签；本行左侧输出名称为“IMAGE0”，成功时由该步骤按前文契约写入状态。

第5步：读取状态“IMAGE0”作为本行结果；本行虽给出左侧名称“FINAL_RESULT”，结果步骤不将它写入状态，也不令执行器提前停止。

[给候选对象分配类别并每类取一项](../engine/step_interpreters.py.md#section-30)

[用语言模型列出外部知识候选](../engine/step_interpreters.py.md#section-29)

[为外部知识标注提供对象列表](../engine/step_interpreters.py.md#section-11)

[读取指定状态作为步骤结果](../engine/step_interpreters.py.md#section-8)

[把分类标签和框画到图像副本](../engine/step_interpreters.py.md#section-31)

<a id="section-6"></a>

## 逐步展开示例5

### 概览

这条示例给生成模型的输入原文为“Tag the shoes (4) by their type”。

### 完整过程

这条示例给生成模型的输入原文为“Tag the shoes (4) by their type”。以下完整说明其保存的各行，按顺序解释；它们是提示内的文字，不会在导入时执行。

第1步：在状态“IMAGE”中定位目标文字“shoe”；采用本任务登记的定位类型，几何保留词和对象包装差异见定位译文；本行左侧输出名称为“OBJ0”，成功时由该步骤按前文契约写入状态。

第2步：向列表补全服务请求主题文字“type of shoes”，文字中的最多项数为4，没有硬性截断；本行左侧输出名称为“LIST0”，成功时由该步骤按前文契约写入状态。

第3步：以图像状态“IMAGE”、对象列表状态“OBJ0”和类别列表状态“LIST0”进行图文分类，会改写原对象的类别与分数；本行左侧输出名称为“OBJ1”，成功时由该步骤按前文契约写入状态。

第4步：复制状态“IMAGE”，按状态“OBJ1”的类别与分数画框和标签；本行左侧输出名称为“IMAGE0”，成功时由该步骤按前文契约写入状态。

第5步：读取状态“IMAGE0”作为本行结果；本行虽给出左侧名称“FINAL_RESULT”，结果步骤不将它写入状态，也不令执行器提前停止。

[给候选对象分配类别并每类取一项](../engine/step_interpreters.py.md#section-30)

[用语言模型列出外部知识候选](../engine/step_interpreters.py.md#section-29)

[为外部知识标注提供对象列表](../engine/step_interpreters.py.md#section-11)

[读取指定状态作为步骤结果](../engine/step_interpreters.py.md#section-8)

[把分类标签和框画到图像副本](../engine/step_interpreters.py.md#section-31)

<a id="section-7"></a>

## 逐步展开示例6

### 概览

这条示例给生成模型的输入原文为“Tag oscar winning hollywood actors”。

### 完整过程

这条示例给生成模型的输入原文为“Tag oscar winning hollywood actors”。以下完整说明其保存的各行，按顺序解释；它们是提示内的文字，不会在导入时执行。

第1步：对状态“IMAGE”做人脸检测，产生带框、类别与掩膜的对象列表；本行左侧输出名称为“OBJ0”，成功时由该步骤按前文契约写入状态。

第2步：向列表补全服务请求主题文字“oscar winning hollywood actors”，文字中的最多项数为模板中的可变列表上限，标注入口填为二十，没有硬性截断；本行左侧输出名称为“LIST0”，成功时由该步骤按前文契约写入状态。

第3步：以图像状态“IMAGE”、对象列表状态“OBJ0”和类别列表状态“LIST0”进行图文分类，会改写原对象的类别与分数；本行左侧输出名称为“OBJ1”，成功时由该步骤按前文契约写入状态。

第4步：复制状态“IMAGE”，按状态“OBJ1”的类别与分数画框和标签；本行左侧输出名称为“IMAGE0”，成功时由该步骤按前文契约写入状态。

第5步：读取状态“IMAGE0”作为本行结果；本行虽给出左侧名称“FINAL_RESULT”，结果步骤不将它写入状态，也不令执行器提前停止。

[给候选对象分配类别并每类取一项](../engine/step_interpreters.py.md#section-30)

[检测并扩大人脸为带掩膜的对象](../engine/step_interpreters.py.md#section-27)

[用语言模型列出外部知识候选](../engine/step_interpreters.py.md#section-29)

[读取指定状态作为步骤结果](../engine/step_interpreters.py.md#section-8)

[把分类标签和框画到图像副本](../engine/step_interpreters.py.md#section-31)

<a id="section-8"></a>

## 逐步展开示例7

### 概览

这条示例给生成模型的输入原文为“Tag these dishes with their cuisines”。

### 完整过程

这条示例给生成模型的输入原文为“Tag these dishes with their cuisines”。以下完整说明其保存的各行，按顺序解释；它们是提示内的文字，不会在导入时执行。

第1步：在状态“IMAGE”中定位目标文字“dish”；采用本任务登记的定位类型，几何保留词和对象包装差异见定位译文；本行左侧输出名称为“OBJ0”，成功时由该步骤按前文契约写入状态。

第2步：向列表补全服务请求主题文字“cuisines”，文字中的最多项数为模板中的可变列表上限，标注入口填为二十，没有硬性截断；本行左侧输出名称为“LIST0”，成功时由该步骤按前文契约写入状态。

第3步：以图像状态“IMAGE”、对象列表状态“OBJ0”和类别列表状态“LIST0”进行图文分类，会改写原对象的类别与分数；本行左侧输出名称为“OBJ1”，成功时由该步骤按前文契约写入状态。

第4步：复制状态“IMAGE”，按状态“OBJ1”的类别与分数画框和标签；本行左侧输出名称为“IMAGE0”，成功时由该步骤按前文契约写入状态。

第5步：读取状态“IMAGE0”作为本行结果；本行虽给出左侧名称“FINAL_RESULT”，结果步骤不将它写入状态，也不令执行器提前停止。

[给候选对象分配类别并每类取一项](../engine/step_interpreters.py.md#section-30)

[用语言模型列出外部知识候选](../engine/step_interpreters.py.md#section-29)

[为外部知识标注提供对象列表](../engine/step_interpreters.py.md#section-11)

[读取指定状态作为步骤结果](../engine/step_interpreters.py.md#section-8)

[把分类标签和框画到图像副本](../engine/step_interpreters.py.md#section-31)

<a id="section-9"></a>

## 逐步展开示例8

### 概览

这条示例给生成模型的输入原文为“Tag the utensils used for drinking”。

### 完整过程

这条示例给生成模型的输入原文为“Tag the utensils used for drinking”。以下完整说明其保存的各行，按顺序解释；它们是提示内的文字，不会在导入时执行。

第1步：在状态“IMAGE”中定位目标文字“utensil”；采用本任务登记的定位类型，几何保留词和对象包装差异见定位译文；本行左侧输出名称为“OBJ0”，成功时由该步骤按前文契约写入状态。

第2步：向列表补全服务请求主题文字“utensils used for drinking”，文字中的最多项数为模板中的可变列表上限，标注入口填为二十，没有硬性截断；本行左侧输出名称为“LIST0”，成功时由该步骤按前文契约写入状态。

第3步：以图像状态“IMAGE”、对象列表状态“OBJ0”和类别列表状态“LIST0”进行图文分类，会改写原对象的类别与分数；本行左侧输出名称为“OBJ1”，成功时由该步骤按前文契约写入状态。

第4步：复制状态“IMAGE”，按状态“OBJ1”的类别与分数画框和标签；本行左侧输出名称为“IMAGE0”，成功时由该步骤按前文契约写入状态。

第5步：读取状态“IMAGE0”作为本行结果；本行虽给出左侧名称“FINAL_RESULT”，结果步骤不将它写入状态，也不令执行器提前停止。

[给候选对象分配类别并每类取一项](../engine/step_interpreters.py.md#section-30)

[用语言模型列出外部知识候选](../engine/step_interpreters.py.md#section-29)

[为外部知识标注提供对象列表](../engine/step_interpreters.py.md#section-11)

[读取指定状态作为步骤结果](../engine/step_interpreters.py.md#section-8)

[把分类标签和框画到图像副本](../engine/step_interpreters.py.md#section-31)

<a id="section-10"></a>

## 逐步展开示例9

### 概览

这条示例给生成模型的输入原文为“Tag the logos that have a shade of blue”。

### 完整过程

这条示例给生成模型的输入原文为“Tag the logos that have a shade of blue”。以下完整说明其保存的各行，按顺序解释；它们是提示内的文字，不会在导入时执行。

第1步：在状态“IMAGE”中定位目标文字“logo”；采用本任务登记的定位类型，几何保留词和对象包装差异见定位译文；本行左侧输出名称为“OBJ0”，成功时由该步骤按前文契约写入状态。

第2步：向列表补全服务请求主题文字“logos that have a shade of blue”，文字中的最多项数为模板中的可变列表上限，标注入口填为二十，没有硬性截断；本行左侧输出名称为“LIST0”，成功时由该步骤按前文契约写入状态。

第3步：以图像状态“IMAGE”、对象列表状态“OBJ0”和类别列表状态“LIST0”进行图文分类，会改写原对象的类别与分数；本行左侧输出名称为“OBJ1”，成功时由该步骤按前文契约写入状态。

第4步：复制状态“IMAGE”，按状态“OBJ1”的类别与分数画框和标签；本行左侧输出名称为“IMAGE0”，成功时由该步骤按前文契约写入状态。

第5步：读取状态“IMAGE0”作为本行结果；本行虽给出左侧名称“FINAL_RESULT”，结果步骤不将它写入状态，也不令执行器提前停止。

[给候选对象分配类别并每类取一项](../engine/step_interpreters.py.md#section-30)

[用语言模型列出外部知识候选](../engine/step_interpreters.py.md#section-29)

[为外部知识标注提供对象列表](../engine/step_interpreters.py.md#section-11)

[读取指定状态作为步骤结果](../engine/step_interpreters.py.md#section-8)

[把分类标签和框画到图像副本](../engine/step_interpreters.py.md#section-31)

<a id="section-11"></a>

## 逐步展开示例10

### 概览

这条示例给生成模型的输入原文为“Tag the logos (10) that have a shade of blue”。

### 完整过程

这条示例给生成模型的输入原文为“Tag the logos (10) that have a shade of blue”。以下完整说明其保存的各行，按顺序解释；它们是提示内的文字，不会在导入时执行。

第1步：在状态“IMAGE”中定位目标文字“logo”；采用本任务登记的定位类型，几何保留词和对象包装差异见定位译文；本行左侧输出名称为“OBJ0”，成功时由该步骤按前文契约写入状态。

第2步：向列表补全服务请求主题文字“logos that have a shade of blue”，文字中的最多项数为10，没有硬性截断；本行左侧输出名称为“LIST0”，成功时由该步骤按前文契约写入状态。

第3步：以图像状态“IMAGE”、对象列表状态“OBJ0”和类别列表状态“LIST0”进行图文分类，会改写原对象的类别与分数；本行左侧输出名称为“OBJ1”，成功时由该步骤按前文契约写入状态。

第4步：复制状态“IMAGE”，按状态“OBJ1”的类别与分数画框和标签；本行左侧输出名称为“IMAGE0”，成功时由该步骤按前文契约写入状态。

第5步：读取状态“IMAGE0”作为本行结果；本行虽给出左侧名称“FINAL_RESULT”，结果步骤不将它写入状态，也不令执行器提前停止。

[给候选对象分配类别并每类取一项](../engine/step_interpreters.py.md#section-30)

[用语言模型列出外部知识候选](../engine/step_interpreters.py.md#section-29)

[为外部知识标注提供对象列表](../engine/step_interpreters.py.md#section-11)

[读取指定状态作为步骤结果](../engine/step_interpreters.py.md#section-8)

[把分类标签和框画到图像副本](../engine/step_interpreters.py.md#section-31)

<a id="section-12"></a>

## 逐步展开示例11

### 概览

这条示例给生成模型的输入原文为“Tag these leaders with the countries they represent”。

### 完整过程

这条示例给生成模型的输入原文为“Tag these leaders with the countries they represent”。以下完整说明其保存的各行，按顺序解释；它们是提示内的文字，不会在导入时执行。

第1步：对状态“IMAGE”做人脸检测，产生带框、类别与掩膜的对象列表；本行左侧输出名称为“OBJ0”，成功时由该步骤按前文契约写入状态。

第2步：向列表补全服务请求主题文字“countries”，文字中的最多项数为模板中的可变列表上限，标注入口填为二十，没有硬性截断；本行左侧输出名称为“LIST0”，成功时由该步骤按前文契约写入状态。

第3步：以图像状态“IMAGE”、对象列表状态“OBJ0”和类别列表状态“LIST0”进行图文分类，会改写原对象的类别与分数；本行左侧输出名称为“OBJ1”，成功时由该步骤按前文契约写入状态。

第4步：复制状态“IMAGE”，按状态“OBJ1”的类别与分数画框和标签；本行左侧输出名称为“IMAGE0”，成功时由该步骤按前文契约写入状态。

第5步：读取状态“IMAGE0”作为本行结果；本行虽给出左侧名称“FINAL_RESULT”，结果步骤不将它写入状态，也不令执行器提前停止。

[给候选对象分配类别并每类取一项](../engine/step_interpreters.py.md#section-30)

[检测并扩大人脸为带掩膜的对象](../engine/step_interpreters.py.md#section-27)

[用语言模型列出外部知识候选](../engine/step_interpreters.py.md#section-29)

[读取指定状态作为步骤结果](../engine/step_interpreters.py.md#section-8)

[把分类标签和框画到图像副本](../engine/step_interpreters.py.md#section-31)

<a id="section-13"></a>

## 逐步展开示例12

### 概览

这条示例给生成模型的输入原文为“Tag the actor who played Harry Potter”。

### 完整过程

这条示例给生成模型的输入原文为“Tag the actor who played Harry Potter”。以下完整说明其保存的各行，按顺序解释；它们是提示内的文字，不会在导入时执行。

第1步：对状态“IMAGE”做人脸检测，产生带框、类别与掩膜的对象列表；本行左侧输出名称为“OBJ0”，成功时由该步骤按前文契约写入状态。

第2步：向列表补全服务请求主题文字“actor who played Harry Potter”，文字中的最多项数为1，没有硬性截断；本行左侧输出名称为“LIST0”，成功时由该步骤按前文契约写入状态。

第3步：以图像状态“IMAGE”、对象列表状态“OBJ0”和类别列表状态“LIST0”进行图文分类，会改写原对象的类别与分数；本行左侧输出名称为“OBJ1”，成功时由该步骤按前文契约写入状态。

第4步：复制状态“IMAGE”，按状态“OBJ1”的类别与分数画框和标签；本行左侧输出名称为“IMAGE0”，成功时由该步骤按前文契约写入状态。

第5步：读取状态“IMAGE0”作为本行结果；本行虽给出左侧名称“FINAL_RESULT”，结果步骤不将它写入状态，也不令执行器提前停止。

[给候选对象分配类别并每类取一项](../engine/step_interpreters.py.md#section-30)

[检测并扩大人脸为带掩膜的对象](../engine/step_interpreters.py.md#section-27)

[用语言模型列出外部知识候选](../engine/step_interpreters.py.md#section-29)

[读取指定状态作为步骤结果](../engine/step_interpreters.py.md#section-8)

[把分类标签和框画到图像副本](../engine/step_interpreters.py.md#section-31)

<a id="section-14"></a>

## 逐步展开示例13

### 概览

这条示例给生成模型的输入原文为“Tag the 7 dwarfs in Snow White”。

### 完整过程

这条示例给生成模型的输入原文为“Tag the 7 dwarfs in Snow White”。以下完整说明其保存的各行，按顺序解释；它们是提示内的文字，不会在导入时执行。

第1步：对状态“IMAGE”做人脸检测，产生带框、类别与掩膜的对象列表；本行左侧输出名称为“OBJ0”，成功时由该步骤按前文契约写入状态。

第2步：向列表补全服务请求主题文字“dwarfs in snow white”，文字中的最多项数为7，没有硬性截断；本行左侧输出名称为“LIST0”，成功时由该步骤按前文契约写入状态。

第3步：以图像状态“IMAGE”、对象列表状态“OBJ0”和类别列表状态“LIST0”进行图文分类，会改写原对象的类别与分数；本行左侧输出名称为“OBJ1”，成功时由该步骤按前文契约写入状态。

第4步：复制状态“IMAGE”，按状态“OBJ1”的类别与分数画框和标签；本行左侧输出名称为“IMAGE0”，成功时由该步骤按前文契约写入状态。

第5步：读取状态“IMAGE0”作为本行结果；本行虽给出左侧名称“FINAL_RESULT”，结果步骤不将它写入状态，也不令执行器提前停止。

[给候选对象分配类别并每类取一项](../engine/step_interpreters.py.md#section-30)

[检测并扩大人脸为带掩膜的对象](../engine/step_interpreters.py.md#section-27)

[用语言模型列出外部知识候选](../engine/step_interpreters.py.md#section-29)

[读取指定状态作为步骤结果](../engine/step_interpreters.py.md#section-8)

[把分类标签和框画到图像副本](../engine/step_interpreters.py.md#section-31)

[返回本文件目录](#file-top)

[返回项目目录](../../%E9%A1%B9%E7%9B%AE%E7%9B%AE%E5%BD%95.md)
