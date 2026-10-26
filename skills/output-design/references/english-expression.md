# 英文表达方法

生成或改写英文技术内容时使用。这是宽松的 STE 启发表达，不是完整 ASD-STE100 合规检查；严格要求见 [标准适用说明](asd-ste100.md)。

## 执行步骤

1. 沿用任务给出的术语和标识。明确句子的 actor、action、object 以及已有 condition；未知主体不猜。
2. 用具体动词替换无必要的动作名词，如 use 代替 make use of。优先主动语态；被动句更准确或主体未知时保留。
3. 将不同指令拆为步骤，将条件放在对应动作附近。拆句保留同时、先后、因果与例外关系。
4. 优先自然短句；长句先检查是否承担多个意思，再拆分，不设置通用硬性词数。严格词数和计数规则以用户要求的正式标准版本为准。
5. 对照原文检查量词、否定、单位、时态、modal verbs 和范围。技术标识不意译，允许的含义不扩大。

## 合成改写示例

- `Perform a validation of the file format.` → `Check the file format.`
- `Retry the request if the connection is available.` → `If the connection is available, retry the request.`
- `The request may have failed.` 保留 may have；不能改成 `The request failed.`
- `Save A and B at the same time.` 拆成步骤时仍需保留同时执行，不能写成先保存 A 再保存 B。

解释性文字保持自然段落，创作内容服从用户语气。输出的事实正确性和内容完整性由当前任务判断；短句不能证明事实正确。

来源：借鉴 [danyuchn/asd-ste100-skill](https://github.com/danyuchn/asd-ste100-skill) 的消歧和语义保留方法，保留 [LICENSE](../LICENSE)；标准事实以 [官方 FAQ](https://www.asd-ste100.org/STE_faq.html) 为准。
