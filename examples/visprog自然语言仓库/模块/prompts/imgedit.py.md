<a id="file-top"></a>

# 图像编辑的十段示例提示

图像编辑的十段示例提示。此模块只组织给模型的文字，不在导入时执行视觉任务。

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

- [表情缩写的精确对应](#section-12)

<a id="section-1"></a>

## 保存的示例及其实际差异

### 概览

本文件只定义一份多行提示文字，没有提示函数或模型调用。

### 完整过程

本文件只定义一份多行提示文字，没有提示函数或模型调用。开头要求逐步执行指令，并把四种表情缩写分别对应吐舌、墨镜微笑、微笑、眨眼的素材名。十段示例依次是：检测人脸，按 Nicole Kidman 名称选脸并贴吐舌表情；检测同一批脸，先给 Nicole 贴眨眼再想给 Brad Pitt 贴墨镜；分割后选择 Amy 与 Daphne 做局部保色；选择女孩与伞做保色；选择狗、飞盘、草做保色；按 person 类别选择红衣男子做保色；选择红巴士后模糊背景；选红巴士换成蓝巴士；先换红巴士，再对新图重新分割并选择道路换成土路；按 bus 类别选择红巴士，再请求替换。各例通过结果读取返回图像。末尾为本次 instruction 留出文字插入位置。

第二例虽产生 Brad 的对象列表，第二次贴表情实际仍引用 Nicole 的列表，因此不会按描述贴到另一人。第十例自然语言说换成卡车，程序里的修补提示实际仍是蓝巴士。多对象查询用逗号分开，分类筛选在步骤内部另有子串成员规则。这些都是示例本身的真实差异；提示只是引导生成，不保证新程序正确。

<a id="section-2"></a>

## 逐步展开示例1

### 概览

这条示例给生成模型的输入原文为“Hide the face of Nicole Kidman with :p”。

### 完整过程

这条示例给生成模型的输入原文为“Hide the face of Nicole Kidman with :p”。以下完整说明其保存的各行，按顺序解释；它们是提示内的文字，不会在导入时执行。

第1步：对状态“IMAGE”做人脸检测，产生带框、类别与掩膜的对象列表；本行左侧输出名称为“OBJ0”，成功时由该步骤按前文契约写入状态。

第2步：从状态“OBJ0”选择对象，图像取状态“IMAGE”，查询参数为文字“Nicole Kidman”，类别参数为专用空值 None；保留原对象引用；本行左侧输出名称为“OBJ1”，成功时由该步骤按前文契约写入状态。

第3步：在状态“IMAGE”上，按状态“OBJ1”中的框覆盖表情素材文字“face_with_tongue”；本行左侧输出名称为“IMAGE0”，成功时由该步骤按前文契约写入状态。

第4步：读取状态“IMAGE0”作为本行结果；本行虽给出左侧名称“FINAL_RESULT”，结果步骤不将它写入状态，也不令执行器提前停止。

[在选中对象中心覆盖表情图](../engine/step_interpreters.py.md#section-28)

[检测并扩大人脸为带掩膜的对象](../engine/step_interpreters.py.md#section-27)

[读取指定状态作为步骤结果](../engine/step_interpreters.py.md#section-8)

[按类别匹配或图文相似度选择对象](../engine/step_interpreters.py.md#section-24)

<a id="section-3"></a>

## 逐步展开示例2

### 概览

这条示例给生成模型的输入原文为“Hide the faces of Nicole Kidman and Brad Pitt with ;) and 8)”。

### 完整过程

这条示例给生成模型的输入原文为“Hide the faces of Nicole Kidman and Brad Pitt with ;) and 8)”。以下完整说明其保存的各行，按顺序解释；它们是提示内的文字，不会在导入时执行。

第1步：对状态“IMAGE”做人脸检测，产生带框、类别与掩膜的对象列表；本行左侧输出名称为“OBJ0”，成功时由该步骤按前文契约写入状态。

第2步：从状态“OBJ0”选择对象，图像取状态“IMAGE”，查询参数为文字“Nicole Kidman”，类别参数为专用空值 None；保留原对象引用；本行左侧输出名称为“OBJ1”，成功时由该步骤按前文契约写入状态。

第3步：在状态“IMAGE”上，按状态“OBJ1”中的框覆盖表情素材文字“winking_face”；本行左侧输出名称为“IMAGE0”，成功时由该步骤按前文契约写入状态。

第4步：从状态“OBJ0”选择对象，图像取状态“IMAGE”，查询参数为文字“Brad Pitt”，类别参数为专用空值 None；保留原对象引用；本行左侧输出名称为“OBJ2”，成功时由该步骤按前文契约写入状态。

第5步：在状态“IMAGE0”上，按状态“OBJ1”中的框覆盖表情素材文字“smiling_face_with_sunglasses”；本行左侧输出名称为“IMAGE1”，成功时由该步骤按前文契约写入状态。

第6步：读取状态“IMAGE1”作为本行结果；本行虽给出左侧名称“FINAL_RESULT”，结果步骤不将它写入状态，也不令执行器提前停止。

[在选中对象中心覆盖表情图](../engine/step_interpreters.py.md#section-28)

[检测并扩大人脸为带掩膜的对象](../engine/step_interpreters.py.md#section-27)

[读取指定状态作为步骤结果](../engine/step_interpreters.py.md#section-8)

[按类别匹配或图文相似度选择对象](../engine/step_interpreters.py.md#section-24)

<a id="section-4"></a>

## 逐步展开示例3

### 概览

这条示例给生成模型的输入原文为“Create a color pop of Amy and Daphne”。

### 完整过程

这条示例给生成模型的输入原文为“Create a color pop of Amy and Daphne”。以下完整说明其保存的各行，按顺序解释；它们是提示内的文字，不会在导入时执行。

第1步：对状态“IMAGE”做全景分割，产生带框、类别与掩膜的对象列表；本行左侧输出名称为“OBJ0”，成功时由该步骤按前文契约写入状态。

第2步：从状态“OBJ0”选择对象，图像取状态“IMAGE”，查询参数为文字“Amy,Daphne”，类别参数为专用空值 None；保留原对象引用；本行左侧输出名称为“OBJ1”，成功时由该步骤按前文契约写入状态。

第3步：以状态“IMAGE”和对象状态“OBJ1”制作局部保色图；本行左侧输出名称为“IMAGE0”，成功时由该步骤按前文契约写入状态。

第4步：读取状态“IMAGE0”作为本行结果；本行虽给出左侧名称“FINAL_RESULT”，结果步骤不将它写入状态，也不令执行器提前停止。

[保留选中对象颜色并把其他区域变灰](../engine/step_interpreters.py.md#section-25)

[读取指定状态作为步骤结果](../engine/step_interpreters.py.md#section-8)

[把图像分成带类别和掩膜的对象](../engine/step_interpreters.py.md#section-23)

[按类别匹配或图文相似度选择对象](../engine/step_interpreters.py.md#section-24)

<a id="section-5"></a>

## 逐步展开示例4

### 概览

这条示例给生成模型的输入原文为“Create a color pop of the girl and the umbrella”。

### 完整过程

这条示例给生成模型的输入原文为“Create a color pop of the girl and the umbrella”。以下完整说明其保存的各行，按顺序解释；它们是提示内的文字，不会在导入时执行。

第1步：对状态“IMAGE”做全景分割，产生带框、类别与掩膜的对象列表；本行左侧输出名称为“OBJ0”，成功时由该步骤按前文契约写入状态。

第2步：从状态“OBJ0”选择对象，图像取状态“IMAGE”，查询参数为文字“girl,umbrella”，类别参数为专用空值 None；保留原对象引用；本行左侧输出名称为“OBJ1”，成功时由该步骤按前文契约写入状态。

第3步：以状态“IMAGE”和对象状态“OBJ1”制作局部保色图；本行左侧输出名称为“IMAGE0”，成功时由该步骤按前文契约写入状态。

第4步：读取状态“IMAGE0”作为本行结果；本行虽给出左侧名称“FINAL_RESULT”，结果步骤不将它写入状态，也不令执行器提前停止。

[保留选中对象颜色并把其他区域变灰](../engine/step_interpreters.py.md#section-25)

[读取指定状态作为步骤结果](../engine/step_interpreters.py.md#section-8)

[把图像分成带类别和掩膜的对象](../engine/step_interpreters.py.md#section-23)

[按类别匹配或图文相似度选择对象](../engine/step_interpreters.py.md#section-24)

<a id="section-6"></a>

## 逐步展开示例5

### 概览

这条示例给生成模型的输入原文为“Create a color pop of the dog, frisbee, and grass”。

### 完整过程

这条示例给生成模型的输入原文为“Create a color pop of the dog, frisbee, and grass”。以下完整说明其保存的各行，按顺序解释；它们是提示内的文字，不会在导入时执行。

第1步：对状态“IMAGE”做全景分割，产生带框、类别与掩膜的对象列表；本行左侧输出名称为“OBJ0”，成功时由该步骤按前文契约写入状态。

第2步：从状态“OBJ0”选择对象，图像取状态“IMAGE”，查询参数为文字“dog,frisbee,grass”，类别参数为专用空值 None；保留原对象引用；本行左侧输出名称为“OBJ1”，成功时由该步骤按前文契约写入状态。

第3步：以状态“IMAGE”和对象状态“OBJ1”制作局部保色图；本行左侧输出名称为“IMAGE0”，成功时由该步骤按前文契约写入状态。

第4步：读取状态“IMAGE0”作为本行结果；本行虽给出左侧名称“FINAL_RESULT”，结果步骤不将它写入状态，也不令执行器提前停止。

[保留选中对象颜色并把其他区域变灰](../engine/step_interpreters.py.md#section-25)

[读取指定状态作为步骤结果](../engine/step_interpreters.py.md#section-8)

[把图像分成带类别和掩膜的对象](../engine/step_interpreters.py.md#section-23)

[按类别匹配或图文相似度选择对象](../engine/step_interpreters.py.md#section-24)

<a id="section-7"></a>

## 逐步展开示例6

### 概览

这条示例给生成模型的输入原文为“Create a color pop of the man wearing a red suit (person)”。

### 完整过程

这条示例给生成模型的输入原文为“Create a color pop of the man wearing a red suit (person)”。以下完整说明其保存的各行，按顺序解释；它们是提示内的文字，不会在导入时执行。

第1步：对状态“IMAGE”做全景分割，产生带框、类别与掩膜的对象列表；本行左侧输出名称为“OBJ0”，成功时由该步骤按前文契约写入状态。

第2步：从状态“OBJ0”选择对象，图像取状态“IMAGE”，查询参数为文字“man wearing a red suit”，类别参数为文字“person”；保留原对象引用；本行左侧输出名称为“OBJ1”，成功时由该步骤按前文契约写入状态。

第3步：以状态“IMAGE”和对象状态“OBJ1”制作局部保色图；本行左侧输出名称为“IMAGE0”，成功时由该步骤按前文契约写入状态。

第4步：读取状态“IMAGE0”作为本行结果；本行虽给出左侧名称“FINAL_RESULT”，结果步骤不将它写入状态，也不令执行器提前停止。

[保留选中对象颜色并把其他区域变灰](../engine/step_interpreters.py.md#section-25)

[读取指定状态作为步骤结果](../engine/step_interpreters.py.md#section-8)

[把图像分成带类别和掩膜的对象](../engine/step_interpreters.py.md#section-23)

[按类别匹配或图文相似度选择对象](../engine/step_interpreters.py.md#section-24)

<a id="section-8"></a>

## 逐步展开示例7

### 概览

这条示例给生成模型的输入原文为“Select the red bus and blur the background”。

### 完整过程

这条示例给生成模型的输入原文为“Select the red bus and blur the background”。以下完整说明其保存的各行，按顺序解释；它们是提示内的文字，不会在导入时执行。

第1步：对状态“IMAGE”做全景分割，产生带框、类别与掩膜的对象列表；本行左侧输出名称为“OBJ0”，成功时由该步骤按前文契约写入状态。

第2步：从状态“OBJ0”选择对象，图像取状态“IMAGE”，查询参数为文字“red bus”，类别参数为专用空值 None；保留原对象引用；本行左侧输出名称为“OBJ1”，成功时由该步骤按前文契约写入状态。

第3步：以状态“IMAGE”和对象状态“OBJ1”制作背景模糊图；本行左侧输出名称为“IMAGE0”，成功时由该步骤按前文契约写入状态。

第4步：读取状态“IMAGE0”作为本行结果；本行虽给出左侧名称“FINAL_RESULT”，结果步骤不将它写入状态，也不令执行器提前停止。

[模糊背景并尝试保留目标清晰](../engine/step_interpreters.py.md#section-26)

[读取指定状态作为步骤结果](../engine/step_interpreters.py.md#section-8)

[把图像分成带类别和掩膜的对象](../engine/step_interpreters.py.md#section-23)

[按类别匹配或图文相似度选择对象](../engine/step_interpreters.py.md#section-24)

<a id="section-9"></a>

## 逐步展开示例8

### 概览

这条示例给生成模型的输入原文为“Replace the red bus with a blue bus”。

### 完整过程

这条示例给生成模型的输入原文为“Replace the red bus with a blue bus”。以下完整说明其保存的各行，按顺序解释；它们是提示内的文字，不会在导入时执行。

第1步：对状态“IMAGE”做全景分割，产生带框、类别与掩膜的对象列表；本行左侧输出名称为“OBJ0”，成功时由该步骤按前文契约写入状态。

第2步：从状态“OBJ0”选择对象，图像取状态“IMAGE”，查询参数为文字“red bus”，类别参数为专用空值 None；保留原对象引用；本行左侧输出名称为“OBJ1”，成功时由该步骤按前文契约写入状态。

第3步：以状态“IMAGE”为原图，只用状态“OBJ1”的第一个对象掩膜修补，修补文字为文字“blue bus”；该掩膜会被原地阈值化；本行左侧输出名称为“IMAGE0”，成功时由该步骤按前文契约写入状态。

第4步：读取状态“IMAGE0”作为本行结果；本行虽给出左侧名称“FINAL_RESULT”，结果步骤不将它写入状态，也不令执行器提前停止。

[用文字引导修补第一个选中对象](../engine/step_interpreters.py.md#section-33)

[读取指定状态作为步骤结果](../engine/step_interpreters.py.md#section-8)

[把图像分成带类别和掩膜的对象](../engine/step_interpreters.py.md#section-23)

[按类别匹配或图文相似度选择对象](../engine/step_interpreters.py.md#section-24)

<a id="section-10"></a>

## 逐步展开示例9

### 概览

这条示例给生成模型的输入原文为“Replace the red bus with blue bus and the road with dirt road”。

### 完整过程

这条示例给生成模型的输入原文为“Replace the red bus with blue bus and the road with dirt road”。以下完整说明其保存的各行，按顺序解释；它们是提示内的文字，不会在导入时执行。

第1步：对状态“IMAGE”做全景分割，产生带框、类别与掩膜的对象列表；本行左侧输出名称为“OBJ0”，成功时由该步骤按前文契约写入状态。

第2步：从状态“OBJ0”选择对象，图像取状态“IMAGE”，查询参数为文字“red bus”，类别参数为专用空值 None；保留原对象引用；本行左侧输出名称为“OBJ1”，成功时由该步骤按前文契约写入状态。

第3步：以状态“IMAGE”为原图，只用状态“OBJ1”的第一个对象掩膜修补，修补文字为文字“blue bus”；该掩膜会被原地阈值化；本行左侧输出名称为“IMAGE0”，成功时由该步骤按前文契约写入状态。

第4步：对状态“IMAGE0”做全景分割，产生带框、类别与掩膜的对象列表；本行左侧输出名称为“OBJ2”，成功时由该步骤按前文契约写入状态。

第5步：从状态“OBJ2”选择对象，图像取状态“IMAGE0”，查询参数为文字“road”，类别参数为专用空值 None；保留原对象引用；本行左侧输出名称为“OBJ3”，成功时由该步骤按前文契约写入状态。

第6步：以状态“IMAGE0”为原图，只用状态“OBJ3”的第一个对象掩膜修补，修补文字为文字“dirt road”；该掩膜会被原地阈值化；本行左侧输出名称为“IMAGE1”，成功时由该步骤按前文契约写入状态。

第7步：读取状态“IMAGE1”作为本行结果；本行虽给出左侧名称“FINAL_RESULT”，结果步骤不将它写入状态，也不令执行器提前停止。

[用文字引导修补第一个选中对象](../engine/step_interpreters.py.md#section-33)

[读取指定状态作为步骤结果](../engine/step_interpreters.py.md#section-8)

[把图像分成带类别和掩膜的对象](../engine/step_interpreters.py.md#section-23)

[按类别匹配或图文相似度选择对象](../engine/step_interpreters.py.md#section-24)

<a id="section-11"></a>

## 逐步展开示例10

### 概览

这条示例给生成模型的输入原文为“Replace the red bus (bus) with a truck”。

### 完整过程

这条示例给生成模型的输入原文为“Replace the red bus (bus) with a truck”。以下完整说明其保存的各行，按顺序解释；它们是提示内的文字，不会在导入时执行。

第1步：对状态“IMAGE”做全景分割，产生带框、类别与掩膜的对象列表；本行左侧输出名称为“OBJ0”，成功时由该步骤按前文契约写入状态。

第2步：从状态“OBJ0”选择对象，图像取状态“IMAGE”，查询参数为文字“red bus”，类别参数为文字“bus”；保留原对象引用；本行左侧输出名称为“OBJ1”，成功时由该步骤按前文契约写入状态。

第3步：以状态“IMAGE”为原图，只用状态“OBJ1”的第一个对象掩膜修补，修补文字为文字“blue bus”；该掩膜会被原地阈值化；本行左侧输出名称为“IMAGE0”，成功时由该步骤按前文契约写入状态。

第4步：读取状态“IMAGE0”作为本行结果；本行虽给出左侧名称“FINAL_RESULT”，结果步骤不将它写入状态，也不令执行器提前停止。

[用文字引导修补第一个选中对象](../engine/step_interpreters.py.md#section-33)

[读取指定状态作为步骤结果](../engine/step_interpreters.py.md#section-8)

[把图像分成带类别和掩膜的对象](../engine/step_interpreters.py.md#section-23)

[按类别匹配或图文相似度选择对象](../engine/step_interpreters.py.md#section-24)

<a id="section-12"></a>

## 表情缩写的精确对应

### 概览

提示开头把 :p 对应 face_with_tongue，把 8) 对应 smiling_face_with_sunglasses，把 :) 对应 smiling_face，把 ;) 对应 winking_face。

### 完整过程

提示开头把 :p 对应 face_with_tongue，把 8) 对应 smiling_face_with_sunglasses，把 :) 对应 smiling_face，把 ;) 对应 winking_face。这里左边是用户指令中的文字，右边是 AugLy 的 smileys 目录下素材名，不带 PNG 扩展名；提示示例据此选素材。它没有实现额外的缩写解析器，而是把对应关系交给生成模型理解。

[返回本文件目录](#file-top)

[返回项目目录](../../%E9%A1%B9%E7%9B%AE%E7%9B%AE%E5%BD%95.md)
