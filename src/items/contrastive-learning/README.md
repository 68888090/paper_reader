# Contrastive Learning 论文总结

## 文件列表

| 文件名 | 论文标题 | arXiv ID |
|--------|----------|----------|
| `CLIP_Learning_Transferable_Visual_Models.md` | Learning Transferable Visual Models From Natural Language Supervision | 2011.10566 |
| `GroupViT_Semantic_Segmentation_from_Text.md` | GroupViT: Semantic Segmentation Emerges from Text Supervision | 2202.11094 |
| `Difficult_Examples_Hurt_Contrastive_Learning.md` | Difficult Examples Hurt Unsupervised Contrastive Learning | 2501.01317 |
| `DIA-CLIP_Zero-shot_Proteomics.md` | DIA-CLIP: universal representation learning for zero-shot DIA proteomics | 2602.01772 |
| `Pixel-level_Counterfactual_Contrastive_Learning.md` | Pixel-level Counterfactual Contrastive Learning for Medical Image Segmentation | 2603.17110 |
| `Comparative.md` | 论文创新点对比（演进记录） | — |
| `Metrics.md` | 性能指标汇总 | — |

## 主题演进

CLIP（跨模态对齐）→ GroupViT（区域级分割）→ DIA-CLIP（领域迁移：蛋白质组学）→ Difficult Examples（理论分析）→ Counterfactual Dense CL（像素级反事实增强）

对比学习在 2020-2026 年的演进：**图像级 → 区域级 → 像素级**，**标准增强 → 反事实生成**，**视觉 → 生命科学**。

## 更新记录
- 2026/05/04: 重命名所有文件为论文标题，修复 DIA-CLIP 摘要（原为错误的 DT-CL 幻觉内容）
- 2026/05/01: 创建初步总结文件
