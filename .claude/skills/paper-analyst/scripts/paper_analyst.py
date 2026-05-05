#!/usr/bin/env python3
"""
Paper Analyst CLI - 命令行工具

支持功能:
1. 基础总结: 分析PDF并生成中文总结
2. 修改总结: 根据新论文修改已有总结
3. 比较分析: 对比多篇论文的创新点

Usage:
    python paper_analyst.py summarize <pdf_path> <theme>
    python paper_analyst.py modify <existing_summary> <new_paper_innovation>
    python paper_analyst.py compare <paper1> <paper2> ...
"""

import sys
import os
from pathlib import Path


def print_usage():
    print("""
Paper Analyst CLI 工具

Usage:
    python paper_analyst.py summarize <pdf_path> <theme>
    python paper_analyst.py modify <existing_summary> <new_paper_innovation>
    python paper_analyst.py compare <paper1> <paper2> ...

Examples:
    python paper_analyst.py summarize src/tmp/paper_2306.00968.pdf reffering-segmentation
    python paper_analyst.py compare src/items/reffering-segmentation/paper1.md src/items/reffering-segmentation/paper2.md
""")


def main():
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)

    command = sys.argv[1]

    if command == 'summarize':
        if len(sys.argv) < 4:
            print("Error: 需要 PDF 路径和主题名称")
            print_usage()
            sys.exit(1)
        pdf_path = sys.argv[2]
        theme = sys.argv[3]
        print(f"PDF 路径: {pdf_path}")
        print(f"主题: {theme}")
        print("注意: 详细分析需要通过 LLM agent 执行")

    elif command == 'modify':
        if len(sys.argv) < 4:
            print("Error: 需要已有总结和新论文创新点")
            print_usage()
            sys.exit(1)
        existing = sys.argv[2]
        innovation = sys.argv[3]
        print(f"已有总结: {existing}")
        print(f"新论文创新点: {innovation}")

    elif command == 'compare':
        if len(sys.argv) < 3:
            print("Error: 需要至少两篇论文")
            print_usage()
            sys.exit(1)
        papers = sys.argv[2:]
        print(f"待比较论文: {papers}")

    else:
        print(f"未知命令: {command}")
        print_usage()
        sys.exit(1)


if __name__ == '__main__':
    main()
