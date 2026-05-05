---
name: paper-analyst
description: Deep read and analyze research papers. Generate comprehensive Chinese summaries following structured format. Supports summarization, modification of existing summaries, and comparative analysis based on user instructions.
context: inline
---

# Paper Analyst - 论文深度分析与总结

## ⚠️ 最高优先级规则：严禁幻觉

1. **必须基于论文原文生成总结**：所有总结内容必须来自对话中已提供的论文全文或从 src/tmp/ 中读取的论文原文。禁止编造任何论文中不存在的方法、实验、数据集或结论。
2. **若未获取论文原文**：如果对话中没有论文全文内容，必须先通过 Read 工具读取 src/tmp/ 下的对应 PDF 提取文本。
3. **验证机制**：生成总结前，自问——"这个方法、这个数据集、这个实验结果，是否确实出现在论文原文中？" 若不确定，只写论文中明确提到的内容。

## ⚠️ 生成总结前：读取用户画像

在执行任何总结操作前，先读取 `src/profiles/user_profile.md`（若存在），提取以下信息并应用到总结中：

1. **写作风格**：应用用户的常用表达、语气偏好、句式特征
2. **关注维度**：优先在用户高权重的关注维度上展开分析
3. **校正记录**：检查是否有与当前论文相关的校正记录，避免重复误解
4. **方法论偏好**：按用户偏好的分析方式组织总结（如偏好维度对比 → 多使用对比表格）

若 `user_profile.md` 不存在或内容为模板状态（"待填充"），跳过此步骤，按默认风格生成总结。

## 核心功能

这个 skill 专注于**论文的深度阅读、理解和总结**，提供以下能力：

1. **基础总结** - 阅读新论文，生成完整中文总结
2. **修改总结** - 根据新论文创新点，修改已有总结
3. **比较分析** - 对比多篇论文，提取创新点差异

## 工作模式

### Mode 1: 基础总结 (对新论文)
```
输入: 论文原文（从对话或 src/tmp/ 读取） + "请总结这篇论文"
输出: 结构化中文总结 → 保存至 src/items/<theme>/paper_<id>.md
```

### Mode 2: 修改总结 (根据新论文)
```
输入: 旧总结 + 新论文创新点 + "请修改原有总结"
输出: 修改后的总结（保留原文 + 新增引用）
```

### Mode 3: 比较分析
```
输入: 多篇论文内容 + "请对比"
输出: 创新点对比分析
```

### Mode 4: 多论文对比 + 透视文件生成
```
输入: 论文A 总结 + 论文B 总结 + 用户关注的对比维度
输出: .per.md 透视文件 + 更新 Comparative.md
```
- .per.md 命名：`<对比主题>.per.md`（如 `instance_vs_pixel_level.per.md`）
- .per.md 内容：按维度分表对比（设计哲学、架构、损失函数、正负样本、实验验证），最终给出总结性结论
- 同步更新 `Comparative.md`：新增论文对比为该主题下的独立章节
- 透视文件是用户后续反复阅读的核心参考，需足够深入但不冗余

## 输出格式规范

严格遵守 write_summary.md 规则，使用中文书写，按照数据集创建 → 前处理 → 前向传播 → 反向传播 → 后处理的流程逐步展开。

## 关键规则

1. **必须使用中文回答**
2. **必须基于论文原文**——禁止编造，禁止将其他论文的内容混入
3. **修改不覆盖**——modify_summary.md 规则：新增引用条，不删除原内容
4. **总结完成后保存**——将总结保存到 src/items/<theme>/paper_<id>.md

## ⚠️ 流程结束必须询问

每次完成 paper-analyst 流程后，必须使用 AskUserQuestion 询问用户满意度，遵照 skill_self_update 规则执行后续更新。
