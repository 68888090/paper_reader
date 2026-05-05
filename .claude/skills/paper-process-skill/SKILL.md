---
name: paper-process-skill
description: Complete paper processing workflow. Integrates paper-reader (download/raw text extraction), paper-customize (multi-perspective personalized reading angles), paper-analyst (deep summary generation), and paper-contrast (comparative analysis). Automatically cleans src/tmp/ before and after processing.
context: inline
---

# Paper Process Skill

Complete paper processing workflow that integrates multiple skills for a full paper analysis pipeline.

## ⚠️ 重要：inline 模式

本 skill 使用 `context: inline`，在主对话中运行。所有子步骤（下载、提取、总结、对比）的中间结果对后续步骤可见，避免 fork 导致的上下文丢失和幻觉问题。

## Workflow

1. **Clean src/tmp/** — 清理临时文件（仅清理 src/tmp/，不要清理其他目录）
2. **Download paper** — 调用 paper-reader 下载论文 PDF
3. **Extract content** — 调用 paper-reader 提取论文全文
4. **Manage perspectives** — 调用 paper-customize：
   - 运行 `init_perspective.py <theme>` 列出主题下已有角度
   - 用 AskUserQuestion 询问用户选择哪些角度阅读本论文（可多选），或创建新角度
   - 若创建新角度 → 运行 `init_perspective.py <theme> --new <name>`，询问用户关注维度
5. **Apply perspectives & generate summary** — 对每个选中角度：
   - 运行 `apply_perspective.py <theme> <angle>` 获取个性化提示词片段
   - 生成中文总结，在末尾用引用格式追加「个性化关注 — 角度「xxx」」
6. **Save summary** — 保存至 `src/items/<theme>/paper_<id>.md`
7. **Update perspective files** — 更新每个相关 `perspective_<angle>.md` 的"相关论文与角度分析"和"角度内对比"
8. **Update comparative** — 更新全局 `Comparative.md` 和 `Metrics.md`

## 主题文件夹结构

```
src/items/<theme>/
├── paper_<id>.md              # 每篇论文的独立总结
├── Comparative.md             # 全局简化对比（地图）
├── Metrics.md                 # 性能指标汇总
├── perspective_supervision.md # 角度: 监督方式（放大镜）
├── perspective_granularity.md # 角度: 对比粒度（放大镜）
└── perspective_*.md           # 更多自定义角度
```

## 与子 Skill 的集成

| Skill | 用途 | 模式 |
|-------|------|------|
| paper-reader | 下载 PDF + 提取全文 | inline |
| paper-customize | 管理多角度视角，注入个性化关注维度，维护地方性对比 | inline |
| paper-analyst | 生成结构化中文总结 | inline |
| paper-contrast | 更新全局 Comparative.md / Metrics.md | inline |

所有子 skill 均使用 inline 模式，确保论文原文在整个流程中可见。

## 关键规则

- 处理前清理 src/tmp/
- 按顺序处理（下载 → 提取 → 总结 → 对比 → 保存）
- 完成后清理 src/tmp/
- 使用中文生成总结
- **严禁幻觉**：总结必须基于论文原文

## 流程完成后

处理结束后，调用用户级 skill `skill-self-update`，向用户询问对本次流程的满意度（满意/一般/不满意），根据 `~/.claude/rules/skill_self_update.md` 规则决定是否将本次流程优化更新到 skill 中。
