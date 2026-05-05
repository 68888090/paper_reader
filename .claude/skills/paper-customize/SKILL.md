---
name: paper-customize
description: Customize and localize paper summaries based on user's specific research interests. Supports multiple reading angles per theme, each with independent perspective files. Interactive questioning to establish reading perspective, accept user reading notes, and apply personalized focus dimensions to paper analysis and comparison.
context: inline
---

# Paper Customize - 个性化论文阅读视角（多角度）

## ⚠️ 重要：inline 模式

本 skill 使用 `context: inline`，在主对话中运行。

## 核心设计

一个主题下可以有**多个阅读角度**，每个角度有独立的 `perspective_<angle>.md` 文件。

- **Comparative.md** = 全局简化对比（地图）
- **perspective_<angle>.md** = 地方性深度对比（放大镜）

同一篇论文可以属于多个角度，在不同视角下有独立分析。

## 数据文件

```
src/items/<theme>/
├── paper_<id>.md
├── Comparative.md                  # 全局简化对比
├── Metrics.md
├── perspective_supervision.md      # 角度: 监督方式
├── perspective_granularity.md      # 角度: 对比粒度
└── perspective_optimization.md     # 角度: 优化目标
```

## perspective_<angle>.md 结构

```markdown
# 阅读视角: <角度名>

## 关注维度
- 维度1
- 维度2

## 核心问题
<!-- 用户在该角度下最关心的核心问题 -->

## 相关论文与角度分析
### paper_2011.10566 (CLIP)
- 该论文在此角度的表现/定位

## 角度内对比
| 论文 | 维度1 | 维度2 | 综合评价 |
|------|-------|-------|----------|

## 读书笔记
### 笔记标题
<用户读后感>
```

## 工作模式

### Mode 1: 视角管理

当用户对某个 theme 开始处理论文时：

1. 运行 `python3 .claude/skills/paper-customize/scripts/init_perspective.py <theme>` 列出已有角度
2. 运行 `python3 .claude/skills/paper-customize/scripts/apply_perspective.py <theme> --list` 确认
3. 用 AskUserQuestion 询问用户：
   - 选择已有角度来阅读本论文（可多选）
   - 或创建新角度
4. 创建新角度时：`python3 .claude/skills/paper-customize/scripts/init_perspective.py <theme> --new <angle_name>`
   - 给出预设维度候选，让用户选择关注哪些维度
   - 询问用户在该角度下的核心问题
   - 写入 perspective_<angle>.md

### Mode 2: 注入视角到总结

对用户选中的每个角度：

1. 运行 `python3 .claude/skills/paper-customize/scripts/apply_perspective.py <theme> <angle>` 获取个性化提示词片段
2. 在 paper-analyst 生成总结后，追加「个性化关注 — 角度「xxx」」引用条
3. 追加格式（遵守 modify_summary.md 规则）：
   ```
   > **个性化关注 — 角度「监督方式」**: 该论文采用了...作为监督信号，在此维度上...
   ```
4. 总结完成后，更新对应 perspective 文件的"相关论文与角度分析"部分

### Mode 3: 追加读书笔记

用户指定角度 + 笔记内容：
1. 读取 `perspective_<angle>.md`
2. 在"读书笔记"区域追加新笔记
3. 如笔记关联特定论文，同时在该论文总结的个性化关注部分添加引用

### Mode 4: 角度驱动的地方性对比

1. 读取对应 `perspective_<angle>.md`
2. 在该文件"角度内对比"表格中更新/追加论文对比
3. 对比维度来自该角度的"关注维度"
4. 标注每篇论文在该角度下的优劣，指出最符合用户关注重点的论文

## 预设关注维度映射

| 主题 | 预设维度 |
|------|----------|
| contrastive-learning | 监督方式, 对比粒度, 增强策略, 编码器架构, 优化目标 |
| object-detection | 检测范式, 标签分配, NMS方式, 特征金字塔 |
| segmentation | 分割粒度, 解码器架构, 边界处理 |
| nlp | 预训练目标, 序列建模方式, 位置编码 |

## 关键规则

- **使用中文**
- **多角度独立管理** — 一个角度一个文件，互不干扰
- **论文可跨角度** — 同一论文可在不同角度有独立分析
- **追加不覆盖** — 个性化关注作为引用条追加到总结末尾
- **角度内对比自维护** — 每个 perspective 文件维护自己的对比表
- **使用 python3** — macOS 上 python 可能不可用
