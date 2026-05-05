#!/usr/bin/env python3
"""Manage reading perspectives for a given theme. Supports multiple angles per theme.

Usage:
    python3 init_perspective.py <theme>                 # List existing angles + dimension candidates
    python3 init_perspective.py <theme> --new <name>    # Create a new perspective_<name>.md
    python3 init_perspective.py <theme> --delete <name> # Delete a perspective file
"""

import sys
import json
from pathlib import Path
from typing import Optional


SRC_DIR = Path("src/items")

PRESET_DIMENSIONS = {
    "contrastive-learning": [
        "监督方式（无监督对比 / 正负样本 / 全正样本 / 专家系统 / 文本监督）",
        "对比粒度（实例级 / 像素级 / 模态级 / 区域级）",
        "增强策略（数据增强类型 / 增强强度 / 是否需要负样本）",
        "编码器架构（单编码器 / 双编码器 / 多编码器 / 是否共享权重）",
        "优化目标（InfoNCE / 排序损失 / 聚类损失 / BYOL风格）",
        "下游任务迁移（零样本 / 少样本 / 全微调 / 线性探测）",
    ],
    "object-detection": [
        "检测范式（anchor-based / anchor-free / DETR风格）",
        "标签分配策略（IoU阈值 / 动态分配 / 匈牙利匹配）",
        "NMS方式（传统NMS / Soft-NMS / NMS-free）",
        "特征融合（FPN / PANet / BiFPN）",
        "训练策略（数据增强 / 损失函数设计 / 正负样本比例）",
    ],
    "segmentation": [
        "分割粒度（语义 / 实例 / 全景）",
        "解码器架构（FCN / U-Net / Transformer解码器）",
        "边界处理（CRF / 边界损失 / 边缘细化）",
        "特征分辨率（下采样倍数 / 多尺度特征利用）",
        "开放词汇能力（是否支持文本引导 / 零样本类别）",
    ],
    "nlp": [
        "预训练目标（MLM / CLM / Seq2Seq / 对比学习）",
        "序列建模方式（RNN / Transformer / SSM / 混合）",
        "位置编码（绝对 / 相对 / RoPE / ALiBi）",
        "token化方式（BPE / WordPiece / SentencePiece / byte-level）",
        "训练效率（稀疏注意力 / 并行策略 / 推理优化）",
    ],
}

GENERIC_DIMENSIONS = [
    "方法范式（端到端 / 多阶段 / 模块化）",
    "训练策略（数据需求 / 增强方式 / 优化器选择 / 学习率调度）",
    "监督信号（全监督 / 半监督 / 弱监督 / 无监督 / 自监督）",
    "评估指标（准确性 / 效率 / 鲁棒性 / 泛化性）",
    "可扩展性（模型规模 / 数据规模 / 计算资源需求）",
    "创新来源（新架构 / 新损失函数 / 新数据策略 / 新训练范式）",
]

PERSPECTIVE_TEMPLATE = """# 阅读视角: {angle_name}

## 关注维度
{dimensions}

## 核心问题
<!-- 用户在该角度下最关心的核心问题，可在此补充 -->

## 相关论文与角度分析
<!-- 每篇论文在该角度下的表现、定位、优势与不足 -->

## 角度内对比
<!-- 该角度下相关论文之间的深度对比表 -->

## 读书笔记
<!-- 用户对该角度的阅读笔记和思考 -->
"""


def get_theme_dir(theme: str) -> Path:
    return SRC_DIR / theme


def list_perspectives(theme: str) -> list[dict]:
    """List all perspective files in the theme directory."""
    theme_dir = get_theme_dir(theme)
    if not theme_dir.exists():
        return []
    results = []
    for f in sorted(theme_dir.glob("perspective_*.md")):
        # Extract angle name: perspective_<name>.md -> <name>
        stem = f.stem  # perspective_<name>
        name = stem[len("perspective_"):]
        results.append({
            "angle": name,
            "path": str(f),
            "file": f.name,
        })
    return results


def create_perspective(theme: str, angle_name: str, dimensions: Optional[list[str]] = None) -> str:
    """Create a new perspective file. Returns the file path."""
    theme_dir = get_theme_dir(theme)
    theme_dir.mkdir(parents=True, exist_ok=True)

    if dimensions is None:
        dimensions = PRESET_DIMENSIONS.get(theme, GENERIC_DIMENSIONS)

    dim_text = "\n".join(f"- {d}" for d in dimensions)
    content = PERSPECTIVE_TEMPLATE.format(angle_name=angle_name, dimensions=dim_text)

    filepath = theme_dir / f"perspective_{angle_name}.md"
    filepath.write_text(content, encoding="utf-8")
    return str(filepath)


def delete_perspective(theme: str, angle_name: str) -> bool:
    """Delete a perspective file. Returns True if deleted."""
    filepath = get_theme_dir(theme) / f"perspective_{angle_name}.md"
    if filepath.exists():
        filepath.unlink()
        return True
    return False


def cmd_list(theme: str):
    """List existing angles and candidates."""
    existing = list_perspectives(theme)
    candidates = PRESET_DIMENSIONS.get(theme, GENERIC_DIMENSIONS)

    result = {
        "theme": theme,
        "existing_angles": [e["angle"] for e in existing],
        "existing_files": existing,
        "candidates": candidates,
        "theme_dir": str(get_theme_dir(theme)),
    }
    json.dump(result, sys.stdout, ensure_ascii=False, indent=2)


def cmd_create(theme: str, angle_name: str):
    """Create a new perspective file."""
    existing = list_perspectives(theme)
    existing_names = [e["angle"] for e in existing]
    if angle_name in existing_names:
        result = {
            "ok": False,
            "error": f"角度 '{angle_name}' 已存在",
            "existing_angles": existing_names,
        }
    else:
        path = create_perspective(theme, angle_name)
        result = {
            "ok": True,
            "angle": angle_name,
            "path": path,
            "existing_angles": existing_names + [angle_name],
            "message": f"已创建视角文件: {path}",
        }
    json.dump(result, sys.stdout, ensure_ascii=False, indent=2)


def cmd_delete(theme: str, angle_name: str):
    """Delete a perspective file."""
    ok = delete_perspective(theme, angle_name)
    result = {
        "ok": ok,
        "angle": angle_name,
        "message": f"已删除视角 '{angle_name}'" if ok else f"视角 '{angle_name}' 不存在",
    }
    json.dump(result, sys.stdout, ensure_ascii=False, indent=2)


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 init_perspective.py <theme> [--new <name> | --delete <name>]", file=sys.stderr)
        sys.exit(1)

    theme = sys.argv[1]

    if len(sys.argv) >= 4 and sys.argv[2] == "--new":
        angle_name = sys.argv[3]
        cmd_create(theme, angle_name)
    elif len(sys.argv) >= 4 and sys.argv[2] == "--delete":
        angle_name = sys.argv[3]
        cmd_delete(theme, angle_name)
    else:
        cmd_list(theme)


if __name__ == "__main__":
    main()
