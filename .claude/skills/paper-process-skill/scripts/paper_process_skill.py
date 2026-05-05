#!/usr/bin/env python3
"""
Paper Process Skill CLI

Usage:
    python paper_process_skill.py download <theme> <url>
    python paper_process_skill.py process <theme> <url1> [url2] ...
    python paper_process_skill.py analyze <theme>
    python paper_process_skill.py cleanup
"""

import sys
import os
import subprocess
from pathlib import Path


def get_project_root() -> Path:
    """Get project root directory."""
    script_dir = Path(__file__).resolve().parent
    for parent in script_dir.parents:
        if (parent / 'src').exists() and (parent / '.claude').exists():
            return parent
    return Path.cwd()


def print_usage():
    print("""
Paper Process Skill CLI 工具

Usage:
    python paper_process_skill.py download <theme> <url>
    python paper_process_skill.py process <theme> <url1> [url2] ...
    python paper_process_skill.py analyze <theme>
    python paper_process_skill.py cleanup

Examples:
    python paper_process_skill.py download contrastive-learning https://arxiv.org/...
    python paper_process_skill.py process contrastive-learning https://arxiv.org/... https://arxiv.org/...
""")


def download_paper(theme: str, url: str, project_root: Path) -> str:
    """Download a single paper to src/tmp/."""
    tmp_dir = project_root / 'src' / 'tmp'
    tmp_dir.mkdir(parents=True, exist_ok=True)

    result = subprocess.run(
        ['python3', '.claude/skills/paper-reader/scripts/get_paper.py', url],
        cwd=project_root,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        return f"Error: {result.stderr}"

    # Find the downloaded PDF
    pdf_files = list(tmp_dir.glob('*.pdf'))
    if not pdf_files:
        return "Error: No PDF downloaded"

    return str(pdf_files[0])


def process_theme(theme: str, urls: list, project_root: Path):
    """Process multiple papers for a theme."""
    print(f"=== Paper Process Skill ===")
    print(f"Theme: {theme}")
    print(f"Papers to process: {len(urls)}")

    # Clean src/tmp/ before starting
    print("\n=== Step 1: Clean src/tmp/ ===")
    tmp_dir = project_root / 'src' / 'tmp'
    if tmp_dir.exists():
        for item in tmp_dir.iterdir():
            if item.is_file():
                item.unlink()
        print(f"Cleaned: {tmp_dir}")

    # Process each paper
    print("\n=== Step 2: Process papers ===")
    results = []

    for i, url in enumerate(urls, 1):
        print(f"\n--- Paper {i}/{len(urls)}: {url} ---")

        # Download
        print("Downloading...")
        pdf_path = download_paper(theme, url, project_root)
        if pdf_path.startswith("Error"):
            print(f"Error: {pdf_path}")
            results.append({"url": url, "status": "error", "error": pdf_path})
            continue

        print(f"Downloaded to: {pdf_path}")

        # Extract text
        print("Extracting text...")
        result = subprocess.run(
            ['python3', '.claude/skills/paper-reader/scripts/read_pdf.py', pdf_path],
            cwd=project_root,
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            print(f"Error extracting text: {result.stderr}")
            results.append({"url": url, "status": "error", "error": result.stderr})
            continue

        # Get content
        output = result.stdout
        content_start = output.find('--- Page 1 ---')
        if content_start > 0:
            content = output[content_start:]
        else:
            content = output

        print(f"Extracted content: {len(content)} chars")

        # Save to theme folder
        theme_dir = project_root / 'src' / 'items' / theme
        theme_dir.mkdir(parents=True, exist_ok=True)

        # Extract paper name from URL
        paper_name = url.split('/')[-1].replace('.pdf', '').replace('abs/', '').replace('pdf/', '')
        paper_name = paper_name.replace('_', ' ').title().replace(' ', '_')

        summary_path = theme_dir / f'{paper_name}.md'
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write(f"# {paper_name}\n\n## 创作时间与刊物\n- 时间: 处理中...\n\n## 面向的问题与方法\n- 待生成...\n\n## 方法流程\n\n### 数据集创建\n- 待生成...\n\n### 前处理\n- 待生成...\n\n### 前向传播\n- 待生成...\n\n### 反向传播\n- 待生成...\n\n### 后处理\n- 待生成...\n")

        print(f"Saved summary template: {summary_path}")
        results.append({"url": url, "paper_name": paper_name, "status": "success", "content_length": len(content)})

    # Clean src/tmp/ after completion
    print("\n=== Step 3: Clean src/tmp/ ===")
    for item in tmp_dir.iterdir():
        if item.is_file():
            item.unlink()
    print(f"Cleaned: {tmp_dir}")

    # Summary
    print("\n=== Processing Complete ===")
    success_count = sum(1 for r in results if r["status"] == "success")
    print(f"Success: {success_count}/{len(results)}")


def main():
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)

    command = sys.argv[1]
    project_root = get_project_root()

    if command == 'download':
        if len(sys.argv) < 4:
            print("Error: Need theme and URL")
            print_usage()
            sys.exit(1)
        theme = sys.argv[2]
        url = sys.argv[3]
        result = download_paper(theme, url, project_root)
        print(result)

    elif command == 'process':
        if len(sys.argv) < 4:
            print("Error: Need theme and at least one URL")
            print_usage()
            sys.exit(1)
        theme = sys.argv[2]
        urls = sys.argv[3:]
        process_theme(theme, urls, project_root)

    elif command == 'analyze':
        if len(sys.argv) < 3:
            print("Error: Need theme")
            print_usage()
            sys.exit(1)
        theme = sys.argv[2]
        print(f"Analyze theme: {theme}")

    elif command == 'cleanup':
        tmp_dir = project_root / 'src' / 'tmp'
        if tmp_dir.exists():
            for item in tmp_dir.iterdir():
                if item.is_file():
                    item.unlink()
            print(f"Cleaned: {tmp_dir}")
        else:
            print(f"Directory does not exist: {tmp_dir}")

    else:
        print(f"Unknown command: {command}")
        print_usage()
        sys.exit(1)


if __name__ == '__main__':
    main()
