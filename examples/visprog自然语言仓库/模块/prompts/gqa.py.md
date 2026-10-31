<a id="file-top"></a>

# 单图问答的提示与候选程序

单图问答的提示与候选程序。此模块只组织给模型的文字，不在导入时执行视觉任务。

## 本文件的处理过程

- [保存的示例及其实际差异](#section-1)

- [组装本次提示](#section-2)

- [逐步展开示例1](#section-3)

- [逐步展开示例2](#section-4)

- [逐步展开示例3](#section-5)

- [逐步展开示例4](#section-6)

- [逐步展开示例5](#section-7)

- [逐步展开示例6](#section-8)

- [逐步展开示例7](#section-9)

- [逐步展开示例8](#section-10)

- [逐步展开示例9](#section-11)

- [逐步展开示例10](#section-12)

- [逐步展开示例11](#section-13)

- [逐步展开示例12](#section-14)

- [逐步展开示例13](#section-15)

- [逐步展开示例14](#section-16)

- [逐步展开示例15](#section-17)

- [逐步展开示例16](#section-18)

- [逐步展开示例17](#section-19)

- [逐步展开示例18](#section-20)

- [逐步展开示例19](#section-21)

- [逐步展开示例20](#section-22)

<a id="section-1"></a>

## 保存的示例及其实际差异

### 概览

引入随机工具，保存人工示例文本。

### 完整过程

引入随机工具，保存人工示例文本。按意图依次是：取图上半并裁剪、检测车辆、计数，以数量大于零答有无；分别检测火车与栅栏并合计是否大于零；定位雨伞、裁图后问谁拿着；直接问所在地点；定位镜子取右侧后问窗帘颜色；检查上半是否有枕头，非空答顶部否则底部；先取左半、定位酒、取其右侧、检测瓶子并判有无；定位卡车、用名为后方的通用裁图再检测路灯；取右半查食物，据数量回答左右；直接问潜水服与天空的共同点；分别裁出柱与标志并问颜色，再比较不同；裁交通锥问颜色，是否白色；直接问动物是否不同物种；查右半的椅子以回答左右；裁盘子左侧查抽屉；分别裁天空与垫子并比较颜色；定位垫子裁上方查猫；定位猫裁下方查垫子；再次以垫子上方查猫来回答垫子是否在猫下；最后以猫下方查垫子。

必须区分意图与实际模板：第二段计算结果写到 ANSWER2，最终却读取不存在的 ANSWER。两段“猫下方查垫子”的判断文字都在大于零后多了 and，成为无效表达式。相邻的“猫在垫子上方”和“猫下方查垫子”两个字符串之间漏了逗号，Python 将它们拼成同一个列表元素，因此实际上十九个字符串承载二十个问答片段。使用全部示例时坏示例也一起进入模型提示。名为后方的裁图没有深度理解，上下裁剪的无框回退也不符合名称，细节以步骤译文为准。

<a id="section-2"></a>

## 组装本次提示

### 概览

默认随机取八条、种子四十二，group 未使用。

### 完整过程

默认随机取八条、种子四十二，group 未使用。all 使用十九个保存的字符串；random 重设全局随机种子后无放回抽样，数量非法会失败；其他模式抛未实现错误。以换行拼接，前缀要求逐步回答问题，再用输入字典的 question 字段补本次问题，并留下程序位置。Notebook 固定 all。此过程不执行示例，不判断示例引用是否定义，也不修复示例中的语法。

<a id="section-3"></a>

## 逐步展开示例1

### 概览

这条示例给生成模型的输入原文为“Is the vehicle in the top of the image?”。

### 完整过程

这条示例给生成模型的输入原文为“Is the vehicle in the top of the image?”。以下完整说明其保存的各行，按顺序解释；它们是提示内的文字，不会在导入时执行。

第1步：在状态“IMAGE”中定位目标文字“TOP”；采用本任务登记的定位类型，几何保留词和对象包装差异见定位译文；本行左侧输出名称为“BOX0”，成功时由该步骤按前文契约写入状态。

第2步：以状态“IMAGE”为图，使用状态“BOX0”按步骤“CROP”的实际裁剪规则取图；只处理首框，具体空框与别名行为见裁图译文；本行左侧输出名称为“IMAGE0”，成功时由该步骤按前文契约写入状态。

第3步：在状态“IMAGE0”中定位目标文字“vehicle”；采用本任务登记的定位类型，几何保留词和对象包装差异见定位译文；本行左侧输出名称为“BOX1”，成功时由该步骤按前文契约写入状态。

第4步：统计状态“BOX1”的列表长度；本行左侧输出名称为“ANSWER0”，成功时由该步骤按前文契约写入状态。

第5步：把表达式参数作为文字交给组合求值步骤：如果状态“ANSWER0”，大于0，则取文字“yes”，否则取文字“no”；本行左侧输出名称为“ANSWER1”，成功时由该步骤按前文契约写入状态。

第6步：读取状态“ANSWER1”作为本行结果；本行虽给出左侧名称“FINAL_RESULT”，结果步骤不将它写入状态，也不令执行器提前停止。

[统计已有候选框数量](../engine/step_interpreters.py.md#section-12)

[围绕第一个候选框裁出图像](../engine/step_interpreters.py.md#section-13)

[把中间答案组合成表达式结果](../engine/step_interpreters.py.md#section-7)

[定位文字描述的目标并保存候选框](../engine/step_interpreters.py.md#section-10)

[读取指定状态作为步骤结果](../engine/step_interpreters.py.md#section-8)

<a id="section-4"></a>

## 逐步展开示例2

### 概览

这条示例给生成模型的输入原文为“Are there trains or fences in this scene?”。

### 完整过程

这条示例给生成模型的输入原文为“Are there trains or fences in this scene?”。以下完整说明其保存的各行，按顺序解释；它们是提示内的文字，不会在导入时执行。

第1步：在状态“IMAGE”中定位目标文字“train”；采用本任务登记的定位类型，几何保留词和对象包装差异见定位译文；本行左侧输出名称为“BOX0”，成功时由该步骤按前文契约写入状态。

第2步：在状态“IMAGE”中定位目标文字“fence”；采用本任务登记的定位类型，几何保留词和对象包装差异见定位译文；本行左侧输出名称为“BOX1”，成功时由该步骤按前文契约写入状态。

第3步：统计状态“BOX0”的列表长度；本行左侧输出名称为“ANSWER0”，成功时由该步骤按前文契约写入状态。

第4步：统计状态“BOX1”的列表长度；本行左侧输出名称为“ANSWER1”，成功时由该步骤按前文契约写入状态。

第5步：把表达式参数作为文字交给组合求值步骤：如果把状态“ANSWER0”与状态“ANSWER1”相加，大于0，则取文字“yes”，否则取文字“no”；本行左侧输出名称为“ANSWER2”，成功时由该步骤按前文契约写入状态。

第6步：读取状态“ANSWER”作为本行结果；本行虽给出左侧名称“FINAL_RESULT”，结果步骤不将它写入状态，也不令执行器提前停止。

[统计已有候选框数量](../engine/step_interpreters.py.md#section-12)

[把中间答案组合成表达式结果](../engine/step_interpreters.py.md#section-7)

[定位文字描述的目标并保存候选框](../engine/step_interpreters.py.md#section-10)

[读取指定状态作为步骤结果](../engine/step_interpreters.py.md#section-8)

<a id="section-5"></a>

## 逐步展开示例3

### 概览

这条示例给生成模型的输入原文为“Who is carrying the umbrella?”。

### 完整过程

这条示例给生成模型的输入原文为“Who is carrying the umbrella?”。以下完整说明其保存的各行，按顺序解释；它们是提示内的文字，不会在导入时执行。

第1步：在状态“IMAGE”中定位目标文字“umbrella”；采用本任务登记的定位类型，几何保留词和对象包装差异见定位译文；本行左侧输出名称为“BOX0”，成功时由该步骤按前文契约写入状态。

第2步：以状态“IMAGE”为图，使用状态“BOX0”按步骤“CROP”的实际裁剪规则取图；只处理首框，具体空框与别名行为见裁图译文；本行左侧输出名称为“IMAGE0”，成功时由该步骤按前文契约写入状态。

第3步：向图像问答提供状态“IMAGE0”，问题原文为文字“Who is carrying the umbrella?”；本行左侧输出名称为“ANSWER0”，成功时由该步骤按前文契约写入状态。

第4步：读取状态“ANSWER0”作为本行结果；本行虽给出左侧名称“FINAL_RESULT”，结果步骤不将它写入状态，也不令执行器提前停止。

[围绕第一个候选框裁出图像](../engine/step_interpreters.py.md#section-13)

[定位文字描述的目标并保存候选框](../engine/step_interpreters.py.md#section-10)

[读取指定状态作为步骤结果](../engine/step_interpreters.py.md#section-8)

[根据图像回答文字问题](../engine/step_interpreters.py.md#section-9)

<a id="section-6"></a>

## 逐步展开示例4

### 概览

这条示例给生成模型的输入原文为“Which place is it?”。

### 完整过程

这条示例给生成模型的输入原文为“Which place is it?”。以下完整说明其保存的各行，按顺序解释；它们是提示内的文字，不会在导入时执行。

第1步：向图像问答提供状态“IMAGE”，问题原文为文字“Which place is it?”；本行左侧输出名称为“ANSWER0”，成功时由该步骤按前文契约写入状态。

第2步：读取状态“ANSWER0”作为本行结果；本行虽给出左侧名称“FINAL_RESULT”，结果步骤不将它写入状态，也不令执行器提前停止。

[读取指定状态作为步骤结果](../engine/step_interpreters.py.md#section-8)

[根据图像回答文字问题](../engine/step_interpreters.py.md#section-9)

<a id="section-7"></a>

## 逐步展开示例5

### 概览

这条示例给生成模型的输入原文为“What color is the curtain that is to the right of the mirror?”。

### 完整过程

这条示例给生成模型的输入原文为“What color is the curtain that is to the right of the mirror?”。以下完整说明其保存的各行，按顺序解释；它们是提示内的文字，不会在导入时执行。

第1步：在状态“IMAGE”中定位目标文字“mirror”；采用本任务登记的定位类型，几何保留词和对象包装差异见定位译文；本行左侧输出名称为“BOX0”，成功时由该步骤按前文契约写入状态。

第2步：以状态“IMAGE”为图，使用状态“BOX0”按步骤“CROP_RIGHTOF”的实际裁剪规则取图；只处理首框，具体空框与别名行为见裁图译文；本行左侧输出名称为“IMAGE0”，成功时由该步骤按前文契约写入状态。

第3步：向图像问答提供状态“IMAGE0”，问题原文为文字“What color is the curtain?”；本行左侧输出名称为“ANSWER0”，成功时由该步骤按前文契约写入状态。

第4步：读取状态“ANSWER0”作为本行结果；本行虽给出左侧名称“FINAL_RESULT”，结果步骤不将它写入状态，也不令执行器提前停止。

[裁出首个目标中心右侧](../engine/step_interpreters.py.md#section-14)

[定位文字描述的目标并保存候选框](../engine/step_interpreters.py.md#section-10)

[读取指定状态作为步骤结果](../engine/step_interpreters.py.md#section-8)

[根据图像回答文字问题](../engine/step_interpreters.py.md#section-9)

<a id="section-8"></a>

## 逐步展开示例6

### 概览

这条示例给生成模型的输入原文为“Is the pillow in the top part or in the bottom of the picture?”。

### 完整过程

这条示例给生成模型的输入原文为“Is the pillow in the top part or in the bottom of the picture?”。以下完整说明其保存的各行，按顺序解释；它们是提示内的文字，不会在导入时执行。

第1步：在状态“IMAGE”中定位目标文字“TOP”；采用本任务登记的定位类型，几何保留词和对象包装差异见定位译文；本行左侧输出名称为“BOX0”，成功时由该步骤按前文契约写入状态。

第2步：以状态“IMAGE”为图，使用状态“BOX0”按步骤“CROP”的实际裁剪规则取图；只处理首框，具体空框与别名行为见裁图译文；本行左侧输出名称为“IMAGE0”，成功时由该步骤按前文契约写入状态。

第3步：在状态“IMAGE0”中定位目标文字“pillow”；采用本任务登记的定位类型，几何保留词和对象包装差异见定位译文；本行左侧输出名称为“BOX1”，成功时由该步骤按前文契约写入状态。

第4步：统计状态“BOX1”的列表长度；本行左侧输出名称为“ANSWER0”，成功时由该步骤按前文契约写入状态。

第5步：把表达式参数作为文字交给组合求值步骤：如果状态“ANSWER0”，大于0，则取文字“top”，否则取文字“bottom”；本行左侧输出名称为“ANSWER1”，成功时由该步骤按前文契约写入状态。

第6步：读取状态“ANSWER1”作为本行结果；本行虽给出左侧名称“FINAL_RESULT”，结果步骤不将它写入状态，也不令执行器提前停止。

[统计已有候选框数量](../engine/step_interpreters.py.md#section-12)

[围绕第一个候选框裁出图像](../engine/step_interpreters.py.md#section-13)

[把中间答案组合成表达式结果](../engine/step_interpreters.py.md#section-7)

[定位文字描述的目标并保存候选框](../engine/step_interpreters.py.md#section-10)

[读取指定状态作为步骤结果](../engine/step_interpreters.py.md#section-8)

<a id="section-9"></a>

## 逐步展开示例7

### 概览

这条示例给生成模型的输入原文为“Question: Do you see bottles to the right of the wine on the left of the picture?”。

### 完整过程

这条示例给生成模型的输入原文为“Question: Do you see bottles to the right of the wine on the left of the picture?”。以下完整说明其保存的各行，按顺序解释；它们是提示内的文字，不会在导入时执行。

第1步：在状态“IMAGE”中定位目标文字“LEFT”；采用本任务登记的定位类型，几何保留词和对象包装差异见定位译文；本行左侧输出名称为“BOX0”，成功时由该步骤按前文契约写入状态。

第2步：以状态“IMAGE”为图，使用状态“BOX0”按步骤“CROP”的实际裁剪规则取图；只处理首框，具体空框与别名行为见裁图译文；本行左侧输出名称为“IMAGE0”，成功时由该步骤按前文契约写入状态。

第3步：在状态“IMAGE0”中定位目标文字“wine”；采用本任务登记的定位类型，几何保留词和对象包装差异见定位译文；本行左侧输出名称为“BOX1”，成功时由该步骤按前文契约写入状态。

第4步：以状态“IMAGE0”为图，使用状态“BOX1”按步骤“CROP_RIGHTOF”的实际裁剪规则取图；只处理首框，具体空框与别名行为见裁图译文；本行左侧输出名称为“IMAGE1”，成功时由该步骤按前文契约写入状态。

第5步：在状态“IMAGE1”中定位目标文字“bottles”；采用本任务登记的定位类型，几何保留词和对象包装差异见定位译文；本行左侧输出名称为“BOX2”，成功时由该步骤按前文契约写入状态。

第6步：统计状态“BOX2”的列表长度；本行左侧输出名称为“ANSWER0”，成功时由该步骤按前文契约写入状态。

第7步：把表达式参数作为文字交给组合求值步骤：如果状态“ANSWER0”，大于0，则取文字“yes”，否则取文字“no”；本行左侧输出名称为“ANSWER1”，成功时由该步骤按前文契约写入状态。

第8步：读取状态“ANSWER1”作为本行结果；本行虽给出左侧名称“FINAL_RESULT”，结果步骤不将它写入状态，也不令执行器提前停止。

[统计已有候选框数量](../engine/step_interpreters.py.md#section-12)

[围绕第一个候选框裁出图像](../engine/step_interpreters.py.md#section-13)

[裁出首个目标中心右侧](../engine/step_interpreters.py.md#section-14)

[把中间答案组合成表达式结果](../engine/step_interpreters.py.md#section-7)

[定位文字描述的目标并保存候选框](../engine/step_interpreters.py.md#section-10)

[读取指定状态作为步骤结果](../engine/step_interpreters.py.md#section-8)

<a id="section-10"></a>

## 逐步展开示例8

### 概览

这条示例给生成模型的输入原文为“Is the street light standing behind a truck?”。

### 完整过程

这条示例给生成模型的输入原文为“Is the street light standing behind a truck?”。以下完整说明其保存的各行，按顺序解释；它们是提示内的文字，不会在导入时执行。

第1步：在状态“IMAGE”中定位目标文字“truck”；采用本任务登记的定位类型，几何保留词和对象包装差异见定位译文；本行左侧输出名称为“BOX0”，成功时由该步骤按前文契约写入状态。

第2步：以状态“IMAGE”为图，使用状态“BOX0”按步骤“CROP_BEHIND”的实际裁剪规则取图；只处理首框，具体空框与别名行为见裁图译文；本行左侧输出名称为“IMAGE0”，成功时由该步骤按前文契约写入状态。

第3步：在状态“IMAGE0”中定位目标文字“street light”；采用本任务登记的定位类型，几何保留词和对象包装差异见定位译文；本行左侧输出名称为“BOX1”，成功时由该步骤按前文契约写入状态。

第4步：统计状态“BOX1”的列表长度；本行左侧输出名称为“ANSWER0”，成功时由该步骤按前文契约写入状态。

第5步：把表达式参数作为文字交给组合求值步骤：如果状态“ANSWER0”，大于0，则取文字“yes”，否则取文字“no”；本行左侧输出名称为“ANSWER1”，成功时由该步骤按前文契约写入状态。

第6步：读取状态“ANSWER1”作为本行结果；本行虽给出左侧名称“FINAL_RESULT”，结果步骤不将它写入状态，也不令执行器提前停止。

[统计已有候选框数量](../engine/step_interpreters.py.md#section-12)

[名为后方的通用裁图别名](../engine/step_interpreters.py.md#section-21)

[把中间答案组合成表达式结果](../engine/step_interpreters.py.md#section-7)

[定位文字描述的目标并保存候选框](../engine/step_interpreters.py.md#section-10)

[读取指定状态作为步骤结果](../engine/step_interpreters.py.md#section-8)

<a id="section-11"></a>

## 逐步展开示例9

### 概览

这条示例给生成模型的输入原文为“Which side is the food on?”。

### 完整过程

这条示例给生成模型的输入原文为“Which side is the food on?”。以下完整说明其保存的各行，按顺序解释；它们是提示内的文字，不会在导入时执行。

第1步：在状态“IMAGE”中定位目标文字“RIGHT”；采用本任务登记的定位类型，几何保留词和对象包装差异见定位译文；本行左侧输出名称为“BOX0”，成功时由该步骤按前文契约写入状态。

第2步：以状态“IMAGE”为图，使用状态“BOX0”按步骤“CROP”的实际裁剪规则取图；只处理首框，具体空框与别名行为见裁图译文；本行左侧输出名称为“IMAGE0”，成功时由该步骤按前文契约写入状态。

第3步：在状态“IMAGE0”中定位目标文字“food”；采用本任务登记的定位类型，几何保留词和对象包装差异见定位译文；本行左侧输出名称为“BOX1”，成功时由该步骤按前文契约写入状态。

第4步：统计状态“BOX1”的列表长度；本行左侧输出名称为“ANSWER0”，成功时由该步骤按前文契约写入状态。

第5步：把表达式参数作为文字交给组合求值步骤：如果状态“ANSWER0”，大于0，则取文字“right”，否则取文字“left”；本行左侧输出名称为“ANSWER1”，成功时由该步骤按前文契约写入状态。

第6步：读取状态“ANSWER1”作为本行结果；本行虽给出左侧名称“FINAL_RESULT”，结果步骤不将它写入状态，也不令执行器提前停止。

[统计已有候选框数量](../engine/step_interpreters.py.md#section-12)

[围绕第一个候选框裁出图像](../engine/step_interpreters.py.md#section-13)

[把中间答案组合成表达式结果](../engine/step_interpreters.py.md#section-7)

[定位文字描述的目标并保存候选框](../engine/step_interpreters.py.md#section-10)

[读取指定状态作为步骤结果](../engine/step_interpreters.py.md#section-8)

<a id="section-12"></a>

## 逐步展开示例10

### 概览

这条示例给生成模型的输入原文为“What do the wetsuit and the sky have in common?”。

### 完整过程

这条示例给生成模型的输入原文为“What do the wetsuit and the sky have in common?”。以下完整说明其保存的各行，按顺序解释；它们是提示内的文字，不会在导入时执行。

第1步：向图像问答提供状态“IMAGE”，问题原文为文字“What do the wetsuit and the sky have in common?”；本行左侧输出名称为“ANSWER0”，成功时由该步骤按前文契约写入状态。

第2步：读取状态“ANSWER0”作为本行结果；本行虽给出左侧名称“FINAL_RESULT”，结果步骤不将它写入状态，也不令执行器提前停止。

[读取指定状态作为步骤结果](../engine/step_interpreters.py.md#section-8)

[根据图像回答文字问题](../engine/step_interpreters.py.md#section-9)

<a id="section-13"></a>

## 逐步展开示例11

### 概览

这条示例给生成模型的输入原文为“Do the post and the sign have a different colors?”。

### 完整过程

这条示例给生成模型的输入原文为“Do the post and the sign have a different colors?”。以下完整说明其保存的各行，按顺序解释；它们是提示内的文字，不会在导入时执行。

第1步：在状态“IMAGE”中定位目标文字“post”；采用本任务登记的定位类型，几何保留词和对象包装差异见定位译文；本行左侧输出名称为“BOX0”，成功时由该步骤按前文契约写入状态。

第2步：以状态“IMAGE”为图，使用状态“BOX0”按步骤“CROP”的实际裁剪规则取图；只处理首框，具体空框与别名行为见裁图译文；本行左侧输出名称为“IMAGE0”，成功时由该步骤按前文契约写入状态。

第3步：在状态“IMAGE”中定位目标文字“sign”；采用本任务登记的定位类型，几何保留词和对象包装差异见定位译文；本行左侧输出名称为“BOX1”，成功时由该步骤按前文契约写入状态。

第4步：以状态“IMAGE”为图，使用状态“BOX1”按步骤“CROP”的实际裁剪规则取图；只处理首框，具体空框与别名行为见裁图译文；本行左侧输出名称为“IMAGE1”，成功时由该步骤按前文契约写入状态。

第5步：向图像问答提供状态“IMAGE0”，问题原文为文字“What color is the post?”；本行左侧输出名称为“ANSWER0”，成功时由该步骤按前文契约写入状态。

第6步：向图像问答提供状态“IMAGE1”，问题原文为文字“What color is the sign?”；本行左侧输出名称为“ANSWER1”，成功时由该步骤按前文契约写入状态。

第7步：把表达式参数作为文字交给组合求值步骤：如果状态“ANSWER0”，不等于状态“ANSWER1”，则取文字“yes”，否则取文字“no”；本行左侧输出名称为“ANSWER2”，成功时由该步骤按前文契约写入状态。

第8步：读取状态“ANSWER2”作为本行结果；本行虽给出左侧名称“FINAL_RESULT”，结果步骤不将它写入状态，也不令执行器提前停止。

[围绕第一个候选框裁出图像](../engine/step_interpreters.py.md#section-13)

[把中间答案组合成表达式结果](../engine/step_interpreters.py.md#section-7)

[定位文字描述的目标并保存候选框](../engine/step_interpreters.py.md#section-10)

[读取指定状态作为步骤结果](../engine/step_interpreters.py.md#section-8)

[根据图像回答文字问题](../engine/step_interpreters.py.md#section-9)

<a id="section-14"></a>

## 逐步展开示例12

### 概览

这条示例给生成模型的输入原文为“Does the traffic cone have white color?”。

### 完整过程

这条示例给生成模型的输入原文为“Does the traffic cone have white color?”。以下完整说明其保存的各行，按顺序解释；它们是提示内的文字，不会在导入时执行。

第1步：在状态“IMAGE”中定位目标文字“traffic cone”；采用本任务登记的定位类型，几何保留词和对象包装差异见定位译文；本行左侧输出名称为“BOX0”，成功时由该步骤按前文契约写入状态。

第2步：以状态“IMAGE”为图，使用状态“BOX0”按步骤“CROP”的实际裁剪规则取图；只处理首框，具体空框与别名行为见裁图译文；本行左侧输出名称为“IMAGE0”，成功时由该步骤按前文契约写入状态。

第3步：向图像问答提供状态“IMAGE0”，问题原文为文字“What color is the traffic cone?”；本行左侧输出名称为“ANSWER0”，成功时由该步骤按前文契约写入状态。

第4步：把表达式参数作为文字交给组合求值步骤：如果状态“ANSWER0”，等于文字“white”，则取文字“yes”，否则取文字“no”；本行左侧输出名称为“ANSWER1”，成功时由该步骤按前文契约写入状态。

第5步：读取状态“ANSWER1”作为本行结果；本行虽给出左侧名称“FINAL_RESULT”，结果步骤不将它写入状态，也不令执行器提前停止。

[围绕第一个候选框裁出图像](../engine/step_interpreters.py.md#section-13)

[把中间答案组合成表达式结果](../engine/step_interpreters.py.md#section-7)

[定位文字描述的目标并保存候选框](../engine/step_interpreters.py.md#section-10)

[读取指定状态作为步骤结果](../engine/step_interpreters.py.md#section-8)

[根据图像回答文字问题](../engine/step_interpreters.py.md#section-9)

<a id="section-15"></a>

## 逐步展开示例13

### 概览

这条示例给生成模型的输入原文为“Are these animals of different species?”。

### 完整过程

这条示例给生成模型的输入原文为“Are these animals of different species?”。以下完整说明其保存的各行，按顺序解释；它们是提示内的文字，不会在导入时执行。

第1步：向图像问答提供状态“IMAGE”，问题原文为文字“Are these animals of different species?”；本行左侧输出名称为“ANSWER0”，成功时由该步骤按前文契约写入状态。

第2步：读取状态“ANSWER0”作为本行结果；本行虽给出左侧名称“FINAL_RESULT”，结果步骤不将它写入状态，也不令执行器提前停止。

[读取指定状态作为步骤结果](../engine/step_interpreters.py.md#section-8)

[根据图像回答文字问题](../engine/step_interpreters.py.md#section-9)

<a id="section-16"></a>

## 逐步展开示例14

### 概览

这条示例给生成模型的输入原文为“Which side of the image is the chair on?”。

### 完整过程

这条示例给生成模型的输入原文为“Which side of the image is the chair on?”。以下完整说明其保存的各行，按顺序解释；它们是提示内的文字，不会在导入时执行。

第1步：在状态“IMAGE”中定位目标文字“RIGHT”；采用本任务登记的定位类型，几何保留词和对象包装差异见定位译文；本行左侧输出名称为“BOX0”，成功时由该步骤按前文契约写入状态。

第2步：以状态“IMAGE”为图，使用状态“BOX0”按步骤“CROP”的实际裁剪规则取图；只处理首框，具体空框与别名行为见裁图译文；本行左侧输出名称为“IMAGE0”，成功时由该步骤按前文契约写入状态。

第3步：在状态“IMAGE0”中定位目标文字“chair”；采用本任务登记的定位类型，几何保留词和对象包装差异见定位译文；本行左侧输出名称为“BOX1”，成功时由该步骤按前文契约写入状态。

第4步：统计状态“BOX1”的列表长度；本行左侧输出名称为“ANSWER0”，成功时由该步骤按前文契约写入状态。

第5步：把表达式参数作为文字交给组合求值步骤：如果状态“ANSWER0”，大于0，则取文字“right”，否则取文字“left”；本行左侧输出名称为“ANSWER1”，成功时由该步骤按前文契约写入状态。

第6步：读取状态“ANSWER1”作为本行结果；本行虽给出左侧名称“FINAL_RESULT”，结果步骤不将它写入状态，也不令执行器提前停止。

[统计已有候选框数量](../engine/step_interpreters.py.md#section-12)

[围绕第一个候选框裁出图像](../engine/step_interpreters.py.md#section-13)

[把中间答案组合成表达式结果](../engine/step_interpreters.py.md#section-7)

[定位文字描述的目标并保存候选框](../engine/step_interpreters.py.md#section-10)

[读取指定状态作为步骤结果](../engine/step_interpreters.py.md#section-8)

<a id="section-17"></a>

## 逐步展开示例15

### 概览

这条示例给生成模型的输入原文为“Do you see any drawers to the left of the plate?”。

### 完整过程

这条示例给生成模型的输入原文为“Do you see any drawers to the left of the plate?”。以下完整说明其保存的各行，按顺序解释；它们是提示内的文字，不会在导入时执行。

第1步：在状态“IMAGE”中定位目标文字“plate”；采用本任务登记的定位类型，几何保留词和对象包装差异见定位译文；本行左侧输出名称为“BOX0”，成功时由该步骤按前文契约写入状态。

第2步：以状态“IMAGE”为图，使用状态“BOX0”按步骤“CROP_LEFTOF”的实际裁剪规则取图；只处理首框，具体空框与别名行为见裁图译文；本行左侧输出名称为“IMAGE0”，成功时由该步骤按前文契约写入状态。

第3步：在状态“IMAGE0”中定位目标文字“drawers”；采用本任务登记的定位类型，几何保留词和对象包装差异见定位译文；本行左侧输出名称为“BOX1”，成功时由该步骤按前文契约写入状态。

第4步：统计状态“BOX1”的列表长度；本行左侧输出名称为“ANSWER0”，成功时由该步骤按前文契约写入状态。

第5步：把表达式参数作为文字交给组合求值步骤：如果状态“ANSWER0”，大于0，则取文字“yes”，否则取文字“no”；本行左侧输出名称为“ANSWER1”，成功时由该步骤按前文契约写入状态。

第6步：读取状态“ANSWER1”作为本行结果；本行虽给出左侧名称“FINAL_RESULT”，结果步骤不将它写入状态，也不令执行器提前停止。

[统计已有候选框数量](../engine/step_interpreters.py.md#section-12)

[裁出首个目标中心左侧](../engine/step_interpreters.py.md#section-15)

[把中间答案组合成表达式结果](../engine/step_interpreters.py.md#section-7)

[定位文字描述的目标并保存候选框](../engine/step_interpreters.py.md#section-10)

[读取指定状态作为步骤结果](../engine/step_interpreters.py.md#section-8)

<a id="section-18"></a>

## 逐步展开示例16

### 概览

这条示例给生成模型的输入原文为“Does the mat have the same color as the sky?”。

### 完整过程

这条示例给生成模型的输入原文为“Does the mat have the same color as the sky?”。以下完整说明其保存的各行，按顺序解释；它们是提示内的文字，不会在导入时执行。

第1步：在状态“IMAGE”中定位目标文字“sky”；采用本任务登记的定位类型，几何保留词和对象包装差异见定位译文；本行左侧输出名称为“BOX0”，成功时由该步骤按前文契约写入状态。

第2步：以状态“IMAGE”为图，使用状态“BOX0”按步骤“CROP”的实际裁剪规则取图；只处理首框，具体空框与别名行为见裁图译文；本行左侧输出名称为“IMAGE0”，成功时由该步骤按前文契约写入状态。

第3步：在状态“IMAGE”中定位目标文字“mat”；采用本任务登记的定位类型，几何保留词和对象包装差异见定位译文；本行左侧输出名称为“BOX1”，成功时由该步骤按前文契约写入状态。

第4步：以状态“IMAGE”为图，使用状态“BOX1”按步骤“CROP”的实际裁剪规则取图；只处理首框，具体空框与别名行为见裁图译文；本行左侧输出名称为“IMAGE1”，成功时由该步骤按前文契约写入状态。

第5步：向图像问答提供状态“IMAGE0”，问题原文为文字“What color is the sky?”；本行左侧输出名称为“ANSWER0”，成功时由该步骤按前文契约写入状态。

第6步：向图像问答提供状态“IMAGE1”，问题原文为文字“What color is the mat?”；本行左侧输出名称为“ANSWER1”，成功时由该步骤按前文契约写入状态。

第7步：把表达式参数作为文字交给组合求值步骤：如果状态“ANSWER0”，等于状态“ANSWER1”，则取文字“yes”，否则取文字“no”；本行左侧输出名称为“ANSWER2”，成功时由该步骤按前文契约写入状态。

第8步：读取状态“ANSWER2”作为本行结果；本行虽给出左侧名称“FINAL_RESULT”，结果步骤不将它写入状态，也不令执行器提前停止。

[围绕第一个候选框裁出图像](../engine/step_interpreters.py.md#section-13)

[把中间答案组合成表达式结果](../engine/step_interpreters.py.md#section-7)

[定位文字描述的目标并保存候选框](../engine/step_interpreters.py.md#section-10)

[读取指定状态作为步骤结果](../engine/step_interpreters.py.md#section-8)

[根据图像回答文字问题](../engine/step_interpreters.py.md#section-9)

<a id="section-19"></a>

## 逐步展开示例17

### 概览

这条示例给生成模型的输入原文为“Is a cat above the mat?”。

### 完整过程

这条示例给生成模型的输入原文为“Is a cat above the mat?”。以下完整说明其保存的各行，按顺序解释；它们是提示内的文字，不会在导入时执行。

第1步：在状态“IMAGE”中定位目标文字“mat”；采用本任务登记的定位类型，几何保留词和对象包装差异见定位译文；本行左侧输出名称为“BOX0”，成功时由该步骤按前文契约写入状态。

第2步：以状态“IMAGE”为图，使用状态“BOX0”按步骤“CROP_ABOVE”的实际裁剪规则取图；只处理首框，具体空框与别名行为见裁图译文；本行左侧输出名称为“IMAGE0”，成功时由该步骤按前文契约写入状态。

第3步：在状态“IMAGE0”中定位目标文字“cat”；采用本任务登记的定位类型，几何保留词和对象包装差异见定位译文；本行左侧输出名称为“BOX1”，成功时由该步骤按前文契约写入状态。

第4步：统计状态“BOX1”的列表长度；本行左侧输出名称为“ANSWER0”，成功时由该步骤按前文契约写入状态。

第5步：把表达式参数作为文字交给组合求值步骤：如果状态“ANSWER0”，大于0，则取文字“yes”，否则取文字“no”；本行左侧输出名称为“ANSWER1”，成功时由该步骤按前文契约写入状态。

第6步：读取状态“ANSWER1”作为本行结果；本行虽给出左侧名称“FINAL_RESULT”，结果步骤不将它写入状态，也不令执行器提前停止。

[统计已有候选框数量](../engine/step_interpreters.py.md#section-12)

[裁出首个目标中心上方](../engine/step_interpreters.py.md#section-16)

[把中间答案组合成表达式结果](../engine/step_interpreters.py.md#section-7)

[定位文字描述的目标并保存候选框](../engine/step_interpreters.py.md#section-10)

[读取指定状态作为步骤结果](../engine/step_interpreters.py.md#section-8)

<a id="section-20"></a>

## 逐步展开示例18

### 概览

这条示例给生成模型的输入原文为“Is the cat above a mat?”。

### 完整过程

这条示例给生成模型的输入原文为“Is the cat above a mat?”。以下完整说明其保存的各行，按顺序解释；它们是提示内的文字，不会在导入时执行。

第1步：在状态“IMAGE”中定位目标文字“cat”；采用本任务登记的定位类型，几何保留词和对象包装差异见定位译文；本行左侧输出名称为“BOX0”，成功时由该步骤按前文契约写入状态。

第2步：以状态“IMAGE”为图，使用状态“BOX0”按步骤“CROP_BELOW”的实际裁剪规则取图；只处理首框，具体空框与别名行为见裁图译文；本行左侧输出名称为“IMAGE0”，成功时由该步骤按前文契约写入状态。

第3步：在状态“IMAGE0”中定位目标文字“mat”；采用本任务登记的定位类型，几何保留词和对象包装差异见定位译文；本行左侧输出名称为“BOX1”，成功时由该步骤按前文契约写入状态。

第4步：统计状态“BOX1”的列表长度；本行左侧输出名称为“ANSWER0”，成功时由该步骤按前文契约写入状态。

第5步：把表达式参数作为文字交给组合求值步骤：本想在 ANSWER0 大于零时选文字 yes，否则选文字 no，但大于零条件之后还写了英文 and，其后没有右侧条件就接 else，因此表达式语法无效，实际执行会失败；本行左侧输出名称为“ANSWER1”，成功时由该步骤按前文契约写入状态。

第6步：读取状态“ANSWER1”作为本行结果；本行虽给出左侧名称“FINAL_RESULT”，结果步骤不将它写入状态，也不令执行器提前停止。

[统计已有候选框数量](../engine/step_interpreters.py.md#section-12)

[裁出首个目标中心下方](../engine/step_interpreters.py.md#section-17)

[把中间答案组合成表达式结果](../engine/step_interpreters.py.md#section-7)

[定位文字描述的目标并保存候选框](../engine/step_interpreters.py.md#section-10)

[读取指定状态作为步骤结果](../engine/step_interpreters.py.md#section-8)

<a id="section-21"></a>

## 逐步展开示例19

### 概览

这条示例给生成模型的输入原文为“Is the mat below a cat?”。

### 完整过程

这条示例给生成模型的输入原文为“Is the mat below a cat?”。以下完整说明其保存的各行，按顺序解释；它们是提示内的文字，不会在导入时执行。

第1步：在状态“IMAGE”中定位目标文字“mat”；采用本任务登记的定位类型，几何保留词和对象包装差异见定位译文；本行左侧输出名称为“BOX0”，成功时由该步骤按前文契约写入状态。

第2步：以状态“IMAGE”为图，使用状态“BOX0”按步骤“CROP_ABOVE”的实际裁剪规则取图；只处理首框，具体空框与别名行为见裁图译文；本行左侧输出名称为“IMAGE0”，成功时由该步骤按前文契约写入状态。

第3步：在状态“IMAGE0”中定位目标文字“cat”；采用本任务登记的定位类型，几何保留词和对象包装差异见定位译文；本行左侧输出名称为“BOX1”，成功时由该步骤按前文契约写入状态。

第4步：统计状态“BOX1”的列表长度；本行左侧输出名称为“ANSWER0”，成功时由该步骤按前文契约写入状态。

第5步：把表达式参数作为文字交给组合求值步骤：如果状态“ANSWER0”，大于0，则取文字“yes”，否则取文字“no”；本行左侧输出名称为“ANSWER1”，成功时由该步骤按前文契约写入状态。

第6步：读取状态“ANSWER1”作为本行结果；本行虽给出左侧名称“FINAL_RESULT”，结果步骤不将它写入状态，也不令执行器提前停止。

[统计已有候选框数量](../engine/step_interpreters.py.md#section-12)

[裁出首个目标中心上方](../engine/step_interpreters.py.md#section-16)

[把中间答案组合成表达式结果](../engine/step_interpreters.py.md#section-7)

[定位文字描述的目标并保存候选框](../engine/step_interpreters.py.md#section-10)

[读取指定状态作为步骤结果](../engine/step_interpreters.py.md#section-8)

<a id="section-22"></a>

## 逐步展开示例20

### 概览

这条示例给生成模型的输入原文为“Is a mat below the cat?”。

### 完整过程

这条示例给生成模型的输入原文为“Is a mat below the cat?”。以下完整说明其保存的各行，按顺序解释；它们是提示内的文字，不会在导入时执行。

第1步：在状态“IMAGE”中定位目标文字“cat”；采用本任务登记的定位类型，几何保留词和对象包装差异见定位译文；本行左侧输出名称为“BOX0”，成功时由该步骤按前文契约写入状态。

第2步：以状态“IMAGE”为图，使用状态“BOX0”按步骤“CROP_BELOW”的实际裁剪规则取图；只处理首框，具体空框与别名行为见裁图译文；本行左侧输出名称为“IMAGE0”，成功时由该步骤按前文契约写入状态。

第3步：在状态“IMAGE0”中定位目标文字“mat”；采用本任务登记的定位类型，几何保留词和对象包装差异见定位译文；本行左侧输出名称为“BOX1”，成功时由该步骤按前文契约写入状态。

第4步：统计状态“BOX1”的列表长度；本行左侧输出名称为“ANSWER0”，成功时由该步骤按前文契约写入状态。

第5步：把表达式参数作为文字交给组合求值步骤：本想在 ANSWER0 大于零时选文字 yes，否则选文字 no，但大于零条件之后还写了英文 and，其后没有右侧条件就接 else，因此表达式语法无效，实际执行会失败；本行左侧输出名称为“ANSWER1”，成功时由该步骤按前文契约写入状态。

第6步：读取状态“ANSWER1”作为本行结果；本行虽给出左侧名称“FINAL_RESULT”，结果步骤不将它写入状态，也不令执行器提前停止。

[统计已有候选框数量](../engine/step_interpreters.py.md#section-12)

[裁出首个目标中心下方](../engine/step_interpreters.py.md#section-17)

[把中间答案组合成表达式结果](../engine/step_interpreters.py.md#section-7)

[定位文字描述的目标并保存候选框](../engine/step_interpreters.py.md#section-10)

[读取指定状态作为步骤结果](../engine/step_interpreters.py.md#section-8)

[返回本文件目录](#file-top)

[返回项目目录](../../%E9%A1%B9%E7%9B%AE%E7%9B%AE%E5%BD%95.md)
