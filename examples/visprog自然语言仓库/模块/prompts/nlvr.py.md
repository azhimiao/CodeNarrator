<a id="file-top"></a>

# 两图真假判断的提示与十二个示例

两图真假判断的提示与十二个示例。此模块只组织给模型的文字，不在导入时执行视觉任务。

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

<a id="section-1"></a>

## 保存的示例及其实际差异

### 概览

先引入标准库随机工具，保存十二段人工选择的示例，每段把一句陈述映射为多步视觉问答与逻辑组合。

### 完整过程

先引入标准库随机工具，保存十二段人工选择的示例，每段把一句陈述映射为多步视觉问答与逻辑组合。第一例分别问左右图是否有拇指在右的裸手举蟹、蟹是否腹部朝前头朝上、背景是否有水，先对每图的三条件取且，再对两图结论取异或。第二例问左右图是否有红色敞篷车，取异或。第三例分别问躺下的狗数，相加恰好等于一。第四例把两图蓝黄色鸟数相加，要求二。第五例每图问狼数以及是否对月嚎叫且呈剪影，分别要求一只并满足描述，再异或。第六例分别问是否有冰雪奇缘角色的包，再异或；但右图问答示例把图像参数首字母写成大写 Image，实际解释器读取小写 image，照搬会缺键。第七例只问左图酒瓶数，要求至少七。第八例两图分别问西兰花是否长在土里、花球是否被叶围住，分别取且再异或。第九例分别问海豹数量、是否直接接触、是否面对面，每图要求数量二且两条件成立，再异或。第十例只问右图鹦鹉数，要求至少二。第十一例问右图是否四人同乘独木舟，再把问答经表达式步骤处理。第十二例左右图狼数均要求恰好二。每例最终读取组合答案。

这些示例的“有一图”采用恰好一图为真的异或规则，不是两图皆真时也允许的普通或。示例是提供给生成模型的文本，不会在载入提示模块时执行，里面的错误也不会自动被修正。

冰雪奇缘示例的两行问题还包含未转义的 Disney's 单引号。用 CPython 三点十点十四官方词法实现核查，会把实际 question 截到 Disney，后面字符错配成多余参数；右图行另因 Image 大小写失败。当前 CPython 三点十二点十四运行时对这两行都产生 TokenError，报告字符串未结束。其他版本未逐一验证，不能仅凭“新版”一词判断。逐步展开中记录了这些确定版本及实际字段，不能把原模板看成合法无误的 Python 调用。

<a id="section-2"></a>

## 组装本次提示

### 概览

提示构造默认随机取八段、种子四十二，group 参数存在但未使用。

### 完整过程

提示构造默认随机取八段、种子四十二，group 参数存在但未使用。随机模式每次重设标准库的全局随机种子，再无放回抽样，请求数超过可选范围会失败；all 模式直接选全部十二段，不使用请求数。其他方式抛未实现错误。以换行拼接示例，前面加逐步判断陈述真假的英文要求，末尾用输入字典的 statement 字段填本次陈述，再留出程序生成位置。缺字段会格式化失败。Notebook 明确选择 all，因此实际不是默认随机八段。

<a id="section-3"></a>

## 逐步展开示例1

### 概览

这条示例给生成模型的输入原文为“An image shows one bare hand with the thumb on the right holding up a belly-first, head-up crab, with water in the background.”。

### 完整过程

这条示例给生成模型的输入原文为“An image shows one bare hand with the thumb on the right holding up a belly-first, head-up crab, with water in the background.”。以下完整说明其保存的各行，按顺序解释；它们是提示内的文字，不会在导入时执行。

第1步：向图像问答提供状态“LEFT”，问题原文为文字“Does the image shows one bare hand with the thumb on the right holding a crab?”；本行左侧输出名称为“ANSWER0”，成功时由该步骤按前文契约写入状态。

第2步：向图像问答提供状态“RIGHT”，问题原文为文字“Does the image shows one bare hand with the thumb on the right holding a crab?”；本行左侧输出名称为“ANSWER1”，成功时由该步骤按前文契约写入状态。

第3步：向图像问答提供状态“LEFT”，问题原文为文字“Is the crab belly-first and head-ups?”；本行左侧输出名称为“ANSWER2”，成功时由该步骤按前文契约写入状态。

第4步：向图像问答提供状态“RIGHT”，问题原文为文字“Is the crab belly-first and head-ups?”；本行左侧输出名称为“ANSWER3”，成功时由该步骤按前文契约写入状态。

第5步：向图像问答提供状态“LEFT”，问题原文为文字“Is there water in the background?”；本行左侧输出名称为“ANSWER4”，成功时由该步骤按前文契约写入状态。

第6步：向图像问答提供状态“RIGHT”，问题原文为文字“Is there water in the background?”；本行左侧输出名称为“ANSWER5”，成功时由该步骤按前文契约写入状态。

第7步：把表达式参数作为文字交给组合求值步骤：全部为真：状态“ANSWER0”；状态“ANSWER2”；状态“ANSWER4”；本行左侧输出名称为“ANSWER6”，成功时由该步骤按前文契约写入状态。

第8步：把表达式参数作为文字交给组合求值步骤：全部为真：状态“ANSWER1”；状态“ANSWER3”；状态“ANSWER5”；本行左侧输出名称为“ANSWER7”，成功时由该步骤按前文契约写入状态。

第9步：把表达式参数作为文字交给组合求值步骤：状态“ANSWER6”，不等于状态“ANSWER7”；模板原文使用 xor，表达式步骤会将其改成不等比较，用于两项真假异或；本行左侧输出名称为“ANSWER8”，成功时由该步骤按前文契约写入状态。

第10步：读取状态“ANSWER8”作为本行结果；本行虽给出左侧名称“FINAL_ANSWER”，结果步骤不将它写入状态，也不令执行器提前停止。

[把中间答案组合成表达式结果](../engine/step_interpreters.py.md#section-7)

[读取指定状态作为步骤结果](../engine/step_interpreters.py.md#section-8)

[根据图像回答文字问题](../engine/step_interpreters.py.md#section-9)

<a id="section-4"></a>

## 逐步展开示例2

### 概览

这条示例给生成模型的输入原文为“There is a red convertible in one image.”。

### 完整过程

这条示例给生成模型的输入原文为“There is a red convertible in one image.”。以下完整说明其保存的各行，按顺序解释；它们是提示内的文字，不会在导入时执行。

第1步：向图像问答提供状态“LEFT”，问题原文为文字“Is there a red convertible in the image?”；本行左侧输出名称为“ANSWER0”，成功时由该步骤按前文契约写入状态。

第2步：向图像问答提供状态“RIGHT”，问题原文为文字“Is there a red convertible in the image?”；本行左侧输出名称为“ANSWER1”，成功时由该步骤按前文契约写入状态。

第3步：把表达式参数作为文字交给组合求值步骤：状态“ANSWER0”，不等于状态“ANSWER1”；模板原文使用 xor，表达式步骤会将其改成不等比较，用于两项真假异或；本行左侧输出名称为“ANSWER2”，成功时由该步骤按前文契约写入状态。

第4步：读取状态“ANSWER2”作为本行结果；本行虽给出左侧名称“FINAL_ANSWER”，结果步骤不将它写入状态，也不令执行器提前停止。

[把中间答案组合成表达式结果](../engine/step_interpreters.py.md#section-7)

[读取指定状态作为步骤结果](../engine/step_interpreters.py.md#section-8)

[根据图像回答文字问题](../engine/step_interpreters.py.md#section-9)

<a id="section-5"></a>

## 逐步展开示例3

### 概览

这条示例给生成模型的输入原文为“One dog is laying down.”。

### 完整过程

这条示例给生成模型的输入原文为“One dog is laying down.”。以下完整说明其保存的各行，按顺序解释；它们是提示内的文字，不会在导入时执行。

第1步：向图像问答提供状态“LEFT”，问题原文为文字“How many dogs are laying down?”；本行左侧输出名称为“ANSWER0”，成功时由该步骤按前文契约写入状态。

第2步：向图像问答提供状态“RIGHT”，问题原文为文字“How many dogs are laying down?”；本行左侧输出名称为“ANSWER1”，成功时由该步骤按前文契约写入状态。

第3步：把表达式参数作为文字交给组合求值步骤：把状态“ANSWER0”与状态“ANSWER1”相加，等于1；本行左侧输出名称为“ANSWER2”，成功时由该步骤按前文契约写入状态。

第4步：读取状态“ANSWER2”作为本行结果；本行虽给出左侧名称“FINAL_ANSWER”，结果步骤不将它写入状态，也不令执行器提前停止。

[把中间答案组合成表达式结果](../engine/step_interpreters.py.md#section-7)

[读取指定状态作为步骤结果](../engine/step_interpreters.py.md#section-8)

[根据图像回答文字问题](../engine/step_interpreters.py.md#section-9)

<a id="section-6"></a>

## 逐步展开示例4

### 概览

这条示例给生成模型的输入原文为“There are two blue and yellow birds”。

### 完整过程

这条示例给生成模型的输入原文为“There are two blue and yellow birds”。以下完整说明其保存的各行，按顺序解释；它们是提示内的文字，不会在导入时执行。

第1步：向图像问答提供状态“LEFT”，问题原文为文字“How many blue and yellow birds are in the image?”；本行左侧输出名称为“ANSWER0”，成功时由该步骤按前文契约写入状态。

第2步：向图像问答提供状态“RIGHT”，问题原文为文字“How many blue and yellow birds are in the image?”；本行左侧输出名称为“ANSWER1”，成功时由该步骤按前文契约写入状态。

第3步：把表达式参数作为文字交给组合求值步骤：把状态“ANSWER0”与状态“ANSWER1”相加，等于2；本行左侧输出名称为“ANSWER2”，成功时由该步骤按前文契约写入状态。

第4步：读取状态“ANSWER2”作为本行结果；本行虽给出左侧名称“FINAL_ANSWER”，结果步骤不将它写入状态，也不令执行器提前停止。

[把中间答案组合成表达式结果](../engine/step_interpreters.py.md#section-7)

[读取指定状态作为步骤结果](../engine/step_interpreters.py.md#section-8)

[根据图像回答文字问题](../engine/step_interpreters.py.md#section-9)

<a id="section-7"></a>

## 逐步展开示例5

### 概览

这条示例给生成模型的输入原文为“A single wolf is howling and silhouetted by the moon in one of the images.”。

### 完整过程

这条示例给生成模型的输入原文为“A single wolf is howling and silhouetted by the moon in one of the images.”。以下完整说明其保存的各行，按顺序解释；它们是提示内的文字，不会在导入时执行。

第1步：向图像问答提供状态“LEFT”，问题原文为文字“How many wolves are in the image?”；本行左侧输出名称为“ANSWER0”，成功时由该步骤按前文契约写入状态。

第2步：向图像问答提供状态“RIGHT”，问题原文为文字“How many wolves are in the image?”；本行左侧输出名称为“ANSWER1”，成功时由该步骤按前文契约写入状态。

第3步：向图像问答提供状态“LEFT”，问题原文为文字“Is the wolf howling and silhouetted by the moon?”；本行左侧输出名称为“ANSWER2”，成功时由该步骤按前文契约写入状态。

第4步：向图像问答提供状态“RIGHT”，问题原文为文字“Is the wolf howling and silhouetted by the moon?”；本行左侧输出名称为“ANSWER3”，成功时由该步骤按前文契约写入状态。

第5步：把表达式参数作为文字交给组合求值步骤：全部为真：状态“ANSWER0”，等于1；状态“ANSWER2”；本行左侧输出名称为“ANSWER4”，成功时由该步骤按前文契约写入状态。

第6步：把表达式参数作为文字交给组合求值步骤：全部为真：状态“ANSWER1”，等于1；状态“ANSWER3”；本行左侧输出名称为“ANSWER5”，成功时由该步骤按前文契约写入状态。

第7步：把表达式参数作为文字交给组合求值步骤：状态“ANSWER4”，不等于状态“ANSWER5”；模板原文使用 xor，表达式步骤会将其改成不等比较，用于两项真假异或；本行左侧输出名称为“ANSWER6”，成功时由该步骤按前文契约写入状态。

第8步：读取状态“ANSWER6”作为本行结果；本行虽给出左侧名称“FINAL_ANSWER”，结果步骤不将它写入状态，也不令执行器提前停止。

[把中间答案组合成表达式结果](../engine/step_interpreters.py.md#section-7)

[读取指定状态作为步骤结果](../engine/step_interpreters.py.md#section-8)

[根据图像回答文字问题](../engine/step_interpreters.py.md#section-9)

<a id="section-8"></a>

## 逐步展开示例6

### 概览

这条示例给生成模型的输入原文为“One of the two images has a bag with the characters from Disney's Frozen on it.”。

### 完整过程

这条示例给生成模型的输入原文为“One of the two images has a bag with the characters from Disney's Frozen on it.”。以下完整说明其保存的各行，按顺序解释；它们是提示内的文字，不会在导入时执行。

第1步：向图像问答提供状态“LEFT”，问题原文为文字“Does the image have a bag with the characters from Disney's Frozen on it?”；另一个独立问题是原始示例把 Disney's 的单引号直接放进单引号问题文字中，没有转义。使用 CPython 三点十点十四官方词法实现核查时，question 实际只取到英文 Does the image have a bag with the characters from Disney，其后的 s 与 Frozen、on 与 it、问号与单引号被错配为三个额外参数。左图步骤会把截短的问题交给模型，额外参数没有被本步骤读取；右图仍先因大写 Image 缺少小写 image 而失败。另在当前 CPython 三点十二点十四运行时逐行核查，这两行均直接产生 TokenError，报告字符串未结束。其他版本没有逐一验证，不能仅按“新旧”推断行为；以上分别说明实际核查过的两个版本，不影响声明三点十环境的解释。本段保留原始错误，没有替示例修正；本行左侧输出名称为“ANSWER0”，成功时由该步骤按前文契约写入状态。

第2步：向图像问答提供状态“RIGHT”，问题原文为文字“Does the image have a bag with the characters from Disney's Frozen on it?”；但此行图像参数写成大写 Image，读取器只读取小写 image，所以照此执行会发生缺参数键错误；另一个独立问题是原始示例把 Disney's 的单引号直接放进单引号问题文字中，没有转义。使用 CPython 三点十点十四官方词法实现核查时，question 实际只取到英文 Does the image have a bag with the characters from Disney，其后的 s 与 Frozen、on 与 it、问号与单引号被错配为三个额外参数。左图步骤会把截短的问题交给模型，额外参数没有被本步骤读取；右图仍先因大写 Image 缺少小写 image 而失败。另在当前 CPython 三点十二点十四运行时逐行核查，这两行均直接产生 TokenError，报告字符串未结束。其他版本没有逐一验证，不能仅按“新旧”推断行为；以上分别说明实际核查过的两个版本，不影响声明三点十环境的解释。本段保留原始错误，没有替示例修正；本行左侧输出名称为“ANSWER1”，成功时由该步骤按前文契约写入状态。

第3步：把表达式参数作为文字交给组合求值步骤：状态“ANSWER0”，不等于状态“ANSWER1”；模板原文使用 xor，表达式步骤会将其改成不等比较，用于两项真假异或；本行左侧输出名称为“ANSWER2”，成功时由该步骤按前文契约写入状态。

第4步：读取状态“ANSWER2”作为本行结果；本行虽给出左侧名称“FINAL_ANSWER”，结果步骤不将它写入状态，也不令执行器提前停止。

[把中间答案组合成表达式结果](../engine/step_interpreters.py.md#section-7)

[读取指定状态作为步骤结果](../engine/step_interpreters.py.md#section-8)

[根据图像回答文字问题](../engine/step_interpreters.py.md#section-9)

<a id="section-9"></a>

## 逐步展开示例7

### 概览

这条示例给生成模型的输入原文为“there are at least seven wine bottles in the image on the left”。

### 完整过程

这条示例给生成模型的输入原文为“there are at least seven wine bottles in the image on the left”。以下完整说明其保存的各行，按顺序解释；它们是提示内的文字，不会在导入时执行。

第1步：向图像问答提供状态“LEFT”，问题原文为文字“How many wine bottles are in the image?”；本行左侧输出名称为“ANSWER0”，成功时由该步骤按前文契约写入状态。

第2步：把表达式参数作为文字交给组合求值步骤：状态“ANSWER0”，大于或等于7；本行左侧输出名称为“ANSWER1”，成功时由该步骤按前文契约写入状态。

第3步：读取状态“ANSWER1”作为本行结果；本行虽给出左侧名称“FINAL_ANSWER”，结果步骤不将它写入状态，也不令执行器提前停止。

[把中间答案组合成表达式结果](../engine/step_interpreters.py.md#section-7)

[读取指定状态作为步骤结果](../engine/step_interpreters.py.md#section-8)

[根据图像回答文字问题](../engine/step_interpreters.py.md#section-9)

<a id="section-10"></a>

## 逐步展开示例8

### 概览

这条示例给生成模型的输入原文为“An image shows broccoli growing in soil, with leaves surrounding the florets.”。

### 完整过程

这条示例给生成模型的输入原文为“An image shows broccoli growing in soil, with leaves surrounding the florets.”。以下完整说明其保存的各行，按顺序解释；它们是提示内的文字，不会在导入时执行。

第1步：向图像问答提供状态“LEFT”，问题原文为文字“Does the image show broccoli growing in soil?”；本行左侧输出名称为“ANSWER0”，成功时由该步骤按前文契约写入状态。

第2步：向图像问答提供状态“RIGHT”，问题原文为文字“Does the image show broccoli growing in soil?”；本行左侧输出名称为“ANSWER1”，成功时由该步骤按前文契约写入状态。

第3步：向图像问答提供状态“LEFT”，问题原文为文字“Are leaves surrounding the floret?”；本行左侧输出名称为“ANSWER2”，成功时由该步骤按前文契约写入状态。

第4步：向图像问答提供状态“RIGHT”，问题原文为文字“Are leaves surrounding the floret?”；本行左侧输出名称为“ANSWER3”，成功时由该步骤按前文契约写入状态。

第5步：把表达式参数作为文字交给组合求值步骤：全部为真：状态“ANSWER0”；状态“ANSWER2”；本行左侧输出名称为“ANSWER4”，成功时由该步骤按前文契约写入状态。

第6步：把表达式参数作为文字交给组合求值步骤：全部为真：状态“ANSWER1”；状态“ANSWER3”；本行左侧输出名称为“ANSWER5”，成功时由该步骤按前文契约写入状态。

第7步：把表达式参数作为文字交给组合求值步骤：状态“ANSWER4”，不等于状态“ANSWER5”；模板原文使用 xor，表达式步骤会将其改成不等比较，用于两项真假异或；本行左侧输出名称为“ANSWER6”，成功时由该步骤按前文契约写入状态。

第8步：读取状态“ANSWER6”作为本行结果；本行虽给出左侧名称“FINAL_ANSWER”，结果步骤不将它写入状态，也不令执行器提前停止。

[把中间答案组合成表达式结果](../engine/step_interpreters.py.md#section-7)

[读取指定状态作为步骤结果](../engine/step_interpreters.py.md#section-8)

[根据图像回答文字问题](../engine/step_interpreters.py.md#section-9)

<a id="section-11"></a>

## 逐步展开示例9

### 概览

这条示例给生成模型的输入原文为“An image shows exactly two seals in direct contact, posed face to face.”。

### 完整过程

这条示例给生成模型的输入原文为“An image shows exactly two seals in direct contact, posed face to face.”。以下完整说明其保存的各行，按顺序解释；它们是提示内的文字，不会在导入时执行。

第1步：向图像问答提供状态“LEFT”，问题原文为文字“How many seals are in the image?”；本行左侧输出名称为“ANSWER0”，成功时由该步骤按前文契约写入状态。

第2步：向图像问答提供状态“RIGHT”，问题原文为文字“How many seals are in the image?”；本行左侧输出名称为“ANSWER1”，成功时由该步骤按前文契约写入状态。

第3步：向图像问答提供状态“LEFT”，问题原文为文字“Are the seals in direct contact?”；本行左侧输出名称为“ANSWER2”，成功时由该步骤按前文契约写入状态。

第4步：向图像问答提供状态“RIGHT”，问题原文为文字“Are the seals in direct contact?”；本行左侧输出名称为“ANSWER3”，成功时由该步骤按前文契约写入状态。

第5步：向图像问答提供状态“LEFT”，问题原文为文字“Are the seals posed face to face?”；本行左侧输出名称为“ANSWER4”，成功时由该步骤按前文契约写入状态。

第6步：向图像问答提供状态“RIGHT”，问题原文为文字“Are the seals posed face to face?”；本行左侧输出名称为“ANSWER5”，成功时由该步骤按前文契约写入状态。

第7步：把表达式参数作为文字交给组合求值步骤：全部为真：状态“ANSWER0”，等于2；状态“ANSWER2”；状态“ANSWER4”；本行左侧输出名称为“ANSWER6”，成功时由该步骤按前文契约写入状态。

第8步：把表达式参数作为文字交给组合求值步骤：全部为真：状态“ANSWER1”，等于2；状态“ANSWER3”；状态“ANSWER5”；本行左侧输出名称为“ANSWER7”，成功时由该步骤按前文契约写入状态。

第9步：把表达式参数作为文字交给组合求值步骤：状态“ANSWER6”，不等于状态“ANSWER7”；模板原文使用 xor，表达式步骤会将其改成不等比较，用于两项真假异或；本行左侧输出名称为“ANSWER8”，成功时由该步骤按前文契约写入状态。

第10步：读取状态“ANSWER8”作为本行结果；本行虽给出左侧名称“FINAL_ANSWER”，结果步骤不将它写入状态，也不令执行器提前停止。

[把中间答案组合成表达式结果](../engine/step_interpreters.py.md#section-7)

[读取指定状态作为步骤结果](../engine/step_interpreters.py.md#section-8)

[根据图像回答文字问题](../engine/step_interpreters.py.md#section-9)

<a id="section-12"></a>

## 逐步展开示例10

### 概览

这条示例给生成模型的输入原文为“There is at least two parrots in the right image.”。

### 完整过程

这条示例给生成模型的输入原文为“There is at least two parrots in the right image.”。以下完整说明其保存的各行，按顺序解释；它们是提示内的文字，不会在导入时执行。

第1步：向图像问答提供状态“RIGHT”，问题原文为文字“How many parrots are in the image?”；本行左侧输出名称为“ANSWER0”，成功时由该步骤按前文契约写入状态。

第2步：把表达式参数作为文字交给组合求值步骤：状态“ANSWER0”，大于或等于2；本行左侧输出名称为“ANSWER1”，成功时由该步骤按前文契约写入状态。

第3步：读取状态“ANSWER1”作为本行结果；本行虽给出左侧名称“FINAL_ANSWER”，结果步骤不将它写入状态，也不令执行器提前停止。

[把中间答案组合成表达式结果](../engine/step_interpreters.py.md#section-7)

[读取指定状态作为步骤结果](../engine/step_interpreters.py.md#section-8)

[根据图像回答文字问题](../engine/step_interpreters.py.md#section-9)

<a id="section-13"></a>

## 逐步展开示例11

### 概览

这条示例给生成模型的输入原文为“In the image on the right, four people are riding in one canoe.”。

### 完整过程

这条示例给生成模型的输入原文为“In the image on the right, four people are riding in one canoe.”。以下完整说明其保存的各行，按顺序解释；它们是提示内的文字，不会在导入时执行。

第1步：向图像问答提供状态“RIGHT”，问题原文为文字“Are there four people riding in one canoe?”；本行左侧输出名称为“ANSWER0”，成功时由该步骤按前文契约写入状态。

第2步：把表达式参数作为文字交给组合求值步骤：状态“ANSWER0”；本行左侧输出名称为“ANSWER1”，成功时由该步骤按前文契约写入状态。

第3步：读取状态“ANSWER1”作为本行结果；本行虽给出左侧名称“FINAL_ANSWER”，结果步骤不将它写入状态，也不令执行器提前停止。

[把中间答案组合成表达式结果](../engine/step_interpreters.py.md#section-7)

[读取指定状态作为步骤结果](../engine/step_interpreters.py.md#section-8)

[根据图像回答文字问题](../engine/step_interpreters.py.md#section-9)

<a id="section-14"></a>

## 逐步展开示例12

### 概览

这条示例给生成模型的输入原文为“There are two wolves in each image.”。

### 完整过程

这条示例给生成模型的输入原文为“There are two wolves in each image.”。以下完整说明其保存的各行，按顺序解释；它们是提示内的文字，不会在导入时执行。

第1步：向图像问答提供状态“LEFT”，问题原文为文字“How many wolves are in the image?”；本行左侧输出名称为“ANSWER0”，成功时由该步骤按前文契约写入状态。

第2步：向图像问答提供状态“RIGHT”，问题原文为文字“How many wolves are in the image?”；本行左侧输出名称为“ANSWER1”，成功时由该步骤按前文契约写入状态。

第3步：把表达式参数作为文字交给组合求值步骤：全部为真：状态“ANSWER0”，等于2；状态“ANSWER1”，等于2；本行左侧输出名称为“ANSWER2”，成功时由该步骤按前文契约写入状态。

第4步：读取状态“ANSWER2”作为本行结果；本行虽给出左侧名称“FINAL_ANSWER”，结果步骤不将它写入状态，也不令执行器提前停止。

[把中间答案组合成表达式结果](../engine/step_interpreters.py.md#section-7)

[读取指定状态作为步骤结果](../engine/step_interpreters.py.md#section-8)

[根据图像回答文字问题](../engine/step_interpreters.py.md#section-9)

[返回本文件目录](#file-top)

[返回项目目录](../../%E9%A1%B9%E7%9B%AE%E7%9B%AE%E5%BD%95.md)
