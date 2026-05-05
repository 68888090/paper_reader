---
name: paper-contrast
description: Contrast and compare research papers within a theme. Read papers from src/tmp/, randomly select comparison papers from src/items/<theme>/, generate summaries, and update Comparative.md and Metrics.md. Useful for building a comprehensive comparison of papers in a research area.
context: inline
---

# Paper Contrast Skill

对比分析论文，更新 Comparative.md 和 Metrics.md。

## ⚠️ 重要：inline 模式

本 skill 使用 `context: inline`，在主对话中运行。可直接读取已生成的论文总结和已有的 Comparative.md / Metrics.md 进行对比。

## Workflow

1. **读取新论文总结** — 从 `src/items/<theme>/paper_<id>.md` 读取刚生成的总结
2. **读取已有对比文件** — 读取 `src/items/<theme>/Comparative.md` 和 `Metrics.md`
3. **读取视角文件** — 如存在 `src/items/<theme>/perspective.md`，读取用户关注维度
4. **选择对比论文** — 从同主题下随机选取最多 5 篇已有论文总结
5. **更新 Comparative.md** — 追加新论文的创新点对比章节，包含：
   - 论文对比列表（新论文与哪些已有论文对比）
   - 多维度对比表格（方法/数据/粒度/任务等，增加 perspective.md 中的用户关注维度列）
   - 核心创新点深度对比
   - 性能对比
   - 结论（与已有工作的关系定位）
6. **更新 Metrics.md** — 追加新论文的指标章节，包含：
   - 核心性能指标
   - 训练/推理配置
   - 与已有方法的指标对比总表

## 主题文件夹结构

```
src/items/<theme>/
├── paper_<id>.md          # 每篇论文的独立总结
├── Comparative.md         # 论文创新点对比（演进记录）
└── Metrics.md             # 性能指标汇总
```

## Contrast Strategy

### 第一篇论文（0→1）
- 只写总结，无需对比

### 第二篇论文（1→2）
- 创建 Comparative.md，对比论文 1 和论文 2

### 第 N 篇（N>2）
- 读取所有已有论文总结
- 按主题演进关系追加对比章节
- 更新对比粒度/增强策略等演进表格

## 关键规则

- **使用中文** 
- **先读取再更新** — 必须先 Read Comparative.md 和 Metrics.md 当前内容
- **追加不覆盖** — 在文件末尾追加新章节，保留所有历史对比内容
- **对比要有深度** — 不只是罗列差异，要分析演进关系和互补性
- **同时更新两个文件** — Comparative.md 和 Metrics.md 都需要更新

