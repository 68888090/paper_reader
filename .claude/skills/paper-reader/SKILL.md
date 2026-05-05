---
name: paper-reader
description: Read academic papers from URLs. Use this skill when the user provides a paper URL (e.g., from arXiv). Run the scripts/get_paper.py script with the URL to download the paper to src/tmp/, then run scripts/read_pdf.py to extract text and output the raw paper content for downstream processing. Do not analyze, summarize, or modify - just pass the raw paper content to the next skill.
context: inline
---

# Paper Reader

This skill reads academic papers from URLs using helper scripts. 

## ⚠️ 重要：inline 模式

本 skill 使用 `context: inline`，在主对话中运行，确保下载和提取的论文原文对后续 skill 可见。

## When to Use

Use this skill when the user provides a paper URL:
- arXiv URL (e.g., https://arxiv.org/abs/2306.12495)
- Direct PDF link (e.g., https://arxiv.org/pdf/2603.17110)
- Any direct paper link

## Workflow

1. **Download paper** — 执行 `python3 .claude/skills/paper-reader/scripts/get_paper.py <URL>` 下载到 `src/tmp/`
2. **Extract text** — 执行 `python3 .claude/skills/paper-reader/scripts/read_pdf.py src/tmp/paper_<id>.pdf` 提取全文
3. **Output** — 将提取的论文原文留在对话上下文中，供下游 skill 使用

## Key Rules

- **DO NOT summarize** — 原样输出论文全文
- **DO NOT analyze** — 不做任何解释或分析
- **DO NOT modify** — 保持原始格式
- **Pass raw content** — 下游 skill 会处理
- **使用 python3** — macOS 上 python 可能不可用，使用 python3

