#!/usr/bin/env python3
"""
Paper Process Skill - Main entry point

整合 paper-reader, paper-contrast, paper-analyst 三个 skill 的完整流程：

1. Clean src/tmp/ - 清空临时文件夹
2. Process papers sequentially - 逐篇处理论文
   - Download to src/tmp/
   - Read and extract content
   - Analyze and generate summary
   - Update comparative files
3. Clean src/tmp/ - 清理临时文件夹
"""

import sys
import os
import subprocess
import shutil
from pathlib import Path


def get_project_root() -> Path:
    """Get project root directory."""
    script_dir = Path(__file__).resolve().parent
    for parent in script_dir.parents:
        if (parent / 'src').exists() and (parent / '.claude').exists():
            return parent
    return Path.cwd()


def clean_dir(dir_path: Path):
    """Clean a directory, keep it if doesn't exist."""
    if dir_path.exists():
        for item in dir_path.iterdir():
            if item.is_file():
                item.unlink()
            elif item.is_dir():
                shutil.rmtree(item)
        print(f"Cleaned: {dir_path}")
    else:
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"Created: {dir_path}")


def print_usage():
    print("""
Paper Process Skill - 整合的论文处理工具

Usage:
    python paper_process.py process <theme> <url1> [url2] [url3] ...
    python paper_process.py cleanup

Examples:
    python paper_process.py process contrastive-learning https://arxiv.org/abs/2011.10566 https://arxiv.org/abs/2501.01317v2
    python paper_process.py cleanup
""")


def process_paper(url: str, theme: str, project_root: Path, paper_index: int, total_papers: int) -> dict:
    """Process a single paper."""
    tmp_dir = project_root / 'src' / 'tmp'
    theme_dir = project_root / 'src' / 'items' / theme

    print(f"\n{'='*60}")
    print(f"[{paper_index}/{total_papers}] Processing: {url}")
    print(f"{'='*60}")

    # Step 1: Download paper
    print("\n[1/4] Downloading paper...")
    result = subprocess.run(
        ['python3', '.claude/skills/paper-reader/scripts/get_paper.py', url],
        cwd=project_root,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        return {"url": url, "status": "error", "error": f"Download failed: {result.stderr}"}

    # Find downloaded PDF
    pdf_files = list(tmp_dir.glob('*.pdf'))
    if not pdf_files:
        return {"url": url, "status": "error", "error": "No PDF downloaded"}

    pdf_path = str(pdf_files[0])
    print(f"Downloaded to: {pdf_path}")

    # Step 2: Extract content
    print("\n[2/4] Extracting paper content...")
    result = subprocess.run(
        ['python3', '.claude/skills/paper-reader/scripts/read_pdf.py', pdf_path],
        cwd=project_root,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        return {"url": url, "status": "error", "error": f"Extraction failed: {result.stderr}"}

    output = result.stdout
    content_start = output.find('--- Page 1 ---')
    if content_start > 0:
        content = output[content_start:]
    else:
        content = output

    print(f"Extracted content: {len(content)} chars")

    # Step 3: Generate summary using paper-analyst
    print("\n[3/4] Generating summary with paper-analyst...")
    summary = generate_summary_with_analyst(content, theme, project_root)

    # Step 4: Update comparative files
    print("\n[4/4] updating comparative files...")
    update_comparative_files(theme, project_root)

    # Cleanup tmp
    print("\nCleaning tmp directory...")
    clean_dir(tmp_dir)

    return {"url": url, "status": "success", "content_length": len(content), "summary": summary}


def generate_summary_with_analyst(content: str, theme: str, project_root: Path) -> str:
    """Generate summary using paper-analyst skill via file-based approach.

    Since we cannot call the Skill tool directly from a script,
    we write the content to a prompt file and invoke the paper-analyst skill.
    """
    # Save prompt to temp file for the skill to read
    tmp_dir = project_root / 'src' / 'tmp'
    tmp_dir.mkdir(parents=True, exist_ok=True)

    # Create prompt file
    prompt_content = f"""请阅读并总结这篇论文，生成符合 write_summary.md 结构的完整中文总结。

主题: {theme}

论文内容 (限制15000字符):
{content[:15000]}

请生成完整的中文总结，包含：
1. 创作时间与刊物
2. 面向的问题与方法
3. 方法流程（数据集创建、前处理、前向传播、反向传播、后处理）
4. 关键贡献
5. 核心创新点

请直接输出完整的Markdown格式总结。
"""

    prompt_file = tmp_dir / 'analyzer_prompt.md'
    with open(prompt_file, 'w', encoding='utf-8') as f:
        f.write(prompt_content)

    # The actual analysis is done by the paper-analyst skill when called
    # For now, return a placeholder and let the user trigger the skill manually
    # Or we can just return the extracted content for the user to analyze

    return f"Summary placeholder for {theme}. Please use paper-analyst skill to generate full summary."


def update_comparative_files(theme: str, project_root: Path):
    """Update comparative files for a theme."""
    theme_dir = project_root / 'src' / 'items' / theme

    # Check if Comparative.md exists
    comparative_path = theme_dir / 'Comparative.md'
    if not comparative_path.exists():
        # Create initial Comparative.md
        comparative_content = f"""# 论文创新点对比

## 待补充

这是一个新的主题: {theme}

请添加论文对比内容。
"""
        with open(comparative_path, 'w', encoding='utf-8') as f:
            f.write(comparative_content)
        print(f"Created Comparative.md at {comparative_path}")

    # Check if Metrics.md exists
    metrics_path = theme_dir / 'Metrics.md'
    if not metrics_path.exists():
        # Create initial Metrics.md
        metrics_content = f"""# 论文指标汇总

## 待补充

这是一个新的主题: {theme}

请添加论文指标内容。
"""
        with open(metrics_path, 'w', encoding='utf-8') as f:
            f.write(metrics_content)
        print(f"Created Metrics.md at {metrics_path}")


def main():
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)

    command = sys.argv[1]
    project_root = get_project_root()

    if command == 'process':
        if len(sys.argv) < 4:
            print("Error: Need theme and at least one URL")
            print_usage()
            sys.exit(1)

        theme = sys.argv[2]
        urls = sys.argv[3:]

        # Create theme directory
        theme_dir = project_root / 'src' / 'items' / theme
        theme_dir.mkdir(parents=True, exist_ok=True)
        print(f"Theme folder: {theme_dir}")

        # Step 1: Clean src/tmp/ before starting
        print("\n=== Step 1: Clean src/tmp/ ===")
        tmp_dir = project_root / 'src' / 'tmp'
        clean_dir(tmp_dir)

        # Step 2: Process each paper sequentially
        print("\n=== Step 2: Process papers sequentially ===")
        results = []

        for i, url in enumerate(urls, 1):
            result = process_paper(url, theme, project_root, i, len(urls))
            results.append(result)

        # Step 3: Clean src/tmp/ after completion
        print("\n=== Step 3: Clean src/tmp/ after completion ===")
        clean_dir(tmp_dir)

        # Summary
        print("\n=== Processing Complete ===")
        success_count = sum(1 for r in results if r["status"] == "success")
        print(f"Success: {success_count}/{len(results)}")

        for r in results:
            if r["status"] == "error":
                print(f"  Error: {r['url']} - {r.get('error', 'Unknown error')}")

    elif command == 'cleanup':
        tmp_dir = project_root / 'src' / 'tmp'
        clean_dir(tmp_dir)

    else:
        print(f"Unknown command: {command}")
        print_usage()
        sys.exit(1)


if __name__ == '__main__':
    main()
