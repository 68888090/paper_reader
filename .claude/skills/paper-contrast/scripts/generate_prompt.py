#!/usr/bin/env python3
"""
 Contrast Paper Agent Prompt

 This prompts an LLM to generate a comprehensive paper summary with comparative analysis.
"""

import os
import sys
from pathlib import Path


def get_prompt(paper_name: str, theme: str, pdf_content: str,
               comparison_papers: list, comparative_content: str,
               theme_papers: list) -> str:
    """Generate the prompt for the LLM to generate paper summary."""

    # Check if this is the first paper in theme
    is_first_paper = len([p for p in theme_papers if p != paper_name]) == 0

    prompt = f"""你是一个专业的论文分析专家。请分析以下论文并生成中文总结。

=== 论文信息 ===
- 论文名称: {paper_name}
- 主题: {theme}

=== 论文内容 (PDF 提取的文本) ===
{pdf_content[:8000]}

=== 写作要求 ===

**步骤 1: 生成基础总结 (所有情况下都需要)**

根据 write_summary.md 的规则，生成中文总结：

# {paper_name}

## 创作时间与刊物
- 观察 PDF 元数据中的创建日期和生成器来推断

## 面向的问题与方法
- 论文解决了什么问题？
- 提出了什么方法？

## 方法流程
### 数据集创建
- 数据集来源
- 数据集规模
- 数据集构建方法

### 前处理
- 数据预处理步骤
- 数据增强方法

### 前向传播
- 模型结构
- 前向计算过程

### 反向传播
- 损失函数设计
- 反向传播过程

### 后处理
- 结果后处理方法

---

**步骤 2: 对比分析 (仅在有其他论文时需要)**

当前主题下的其他论文:
{"无其他论文 (这是第一篇)" if is_first_paper else ', '.join(comparison_papers)}

{'无需对比分析' if is_first_paper else '''
请执行以下对比分析：

1. 首先在基础总结下方，以引用格式添加对比分析
2. 对比这篇文章与其它论文的异同点
3. 重点突出本文的创新点
4. 如果 Comparative.md 已存在，请在文章末尾添加与 Comparative.md 的对比分析

格式示例：
---
## 与其它论文的对比

本文相较于 [论文A] 的创新点：
- 创新点 1
- 创新点 2

本文相较于 [论文B] 的改进：
- 改进 1
- 改进 2

*(请基于具体的论文内容进行对比)*
'''}

"""
    return prompt


def main():
    if len(sys.argv) < 6:
        print("Usage: python generate_prompt.py <paper_name> <theme> <pdf_content_path> <comparison_papers> <comparative_path>")
        sys.exit(1)

    paper_name = sys.argv[1]
    theme = sys.argv[2]
    pdf_content_path = sys.argv[3]
    comparative_path = sys.argv[5]

    # Parse comparison papers (comma-separated)
    comparison_papers = sys.argv[4].split(',') if sys.argv[4] else []

    # Read PDF content
    with open(pdf_content_path, 'r', encoding='utf-8') as f:
        pdf_content = f.read()

    # Read comparative
    comparative_content = ''
    if os.path.exists(comparative_path):
        with open(comparative_path, 'r', encoding='utf-8') as f:
            comparative_content = f.read()

    # Get theme papers
    theme_dir = Path(comparative_path).parent
    theme_papers = []
    if theme_dir.exists():
        for item in theme_dir.iterdir():
            if item.is_file() and item.suffix == '.md':
                if item.stem not in ['Comparative', 'Metrics']:
                    theme_papers.append(item.stem)

    # Generate prompt
    prompt = get_prompt(
        paper_name=paper_name,
        theme=theme,
        pdf_content=pdf_content,
        comparison_papers=comparison_papers,
        comparative_content=comparative_content,
        theme_papers=theme_papers
    )

    print(prompt)


if __name__ == '__main__':
    main()
