#!/usr/bin/env python3
"""
Paper Contrast Script

This script handles the paper contrast logic:
1. Read the new paper from src/tmp/
2. Randomly select comparison papers from src/items/<theme>/
3. Generate summary and update Comparative.md

Usage:
    python contrast_papers.py <pdf_path> <theme>
"""

import sys
import os
import re
import random
from pathlib import Path


def get_project_root() -> Path:
    """Get project root directory (paper_Reader/)."""
    script_dir = Path(__file__).resolve().parent
    # Current structure: .../paper_Reader/.claude/skills/paper-contrast/scripts/
    # We need to find the paper_Reader directory
    for parent in script_dir.parents:
        if (parent / 'src').exists() and (parent / '.claude').exists():
            return parent
    return Path.cwd()


def get_pdf_metadata(pdf_path: str) -> dict:
    """Extract metadata from PDF using PyMuPDF."""
    try:
        import fitz
        doc = fitz.open(pdf_path)
        metadata = doc.metadata
        doc.close()
        return metadata
    except Exception:
        return {}


def extract_paper_name(pdf_path: str, metadata: dict) -> str:
    """Extract a clean paper name from PDF path or metadata."""
    # Try to get title from metadata first
    if metadata.get('title'):
        title = metadata['title'].strip()
        if title:
            # Sanitize
            title = re.sub(r'[<>:"/\\|?*]', '', title)
            title = re.sub(r'\s+', '_', title)
            return title[:100]

    # Fallback to filename
    filename = os.path.basename(pdf_path)
    # Remove extension
    name = os.path.splitext(filename)[0]
    # Remove "paper_" prefix if present
    name = re.sub(r'^paper_', '', name)
    return name


def list_theme_papers(theme: str, project_root: Path) -> list:
    """List all papers in a theme folder."""
    theme_dir = project_root / 'src' / 'items' / theme
    if not theme_dir.exists():
        return []

    papers = []
    for item in theme_dir.iterdir():
        if item.is_file() and item.suffix == '.md':
            # Skip special files
            if item.stem in ['Comparative', 'Metrics']:
                continue
            papers.append(item.stem)

    return sorted(papers)


def select_comparison_papers(current_paper: str, theme: str, project_root: Path,
                             max_papers: int = 5) -> list:
    """Select up to max_papers comparison papers randomly."""
    theme_dir = project_root / 'src' / 'items' / theme
    if not theme_dir.exists():
        return []

    # Get all papers in theme
    all_papers = []
    for item in theme_dir.iterdir():
        if item.is_file() and item.suffix == '.md':
            if item.stem in ['Comparative', 'Metrics']:
                continue
            if item.stem != current_paper:  # Exclude current paper
                all_papers.append(item.stem)

    # Shuffle and select
    random.shuffle(all_papers)
    return all_papers[:max_papers]


def read_paper_summary(paper_name: str, theme: str, project_root: Path) -> str:
    """Read the summary of a paper from the theme folder."""
    summary_path = project_root / 'src' / 'items' / theme / f'{paper_name}.md'
    if not summary_path.exists():
        return ''

    try:
        with open(summary_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception:
        return ''


def read_comparative(theme: str, project_root: Path) -> str:
    """Read the Comparative.md file if it exists."""
    comparative_path = project_root / 'src' / 'items' / theme / 'Comparative.md'
    if not comparative_path.exists():
        return ''

    try:
        with open(comparative_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception:
        return ''


def write_paper_summary(paper_name: str, content: str, theme: str, project_root: Path):
    """Write a paper summary to the theme folder."""
    theme_dir = project_root / 'src' / 'items' / theme
    theme_dir.mkdir(parents=True, exist_ok=True)

    summary_path = theme_dir / f'{paper_name}.md'
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write(content)


def write_comparative(theme: str, content: str, project_root: Path):
    """Write the Comparative.md file."""
    theme_dir = project_root / 'src' / 'items' / theme
    theme_dir.mkdir(parents=True, exist_ok=True)

    comparative_path = theme_dir / 'Comparative.md'
    with open(comparative_path, 'w', encoding='utf-8') as f:
        f.write(content)


def read_pdf_content(pdf_path: str) -> tuple[str, dict]:
    """Read PDF content and extract text."""
    try:
        import fitz
        doc = fitz.open(pdf_path)

        text_parts = []
        metadata = doc.metadata

        for page_num, page in enumerate(doc, 1):
            text = page.get_text()
            if text:
                text_parts.append(f"--- Page {page_num} ---\n{text}")

        doc.close()
        return '\n\n'.join(text_parts), metadata
    except Exception as e:
        return f"Error reading PDF: {e}", {}


def main():
    if len(sys.argv) < 3:
        print("Usage: python contrast_papers.py <pdf_path> <theme>")
        print("Example: python contrast_papers.py src/tmp/paper_2306.00968.pdf reffering-segmentation")
        sys.exit(1)

    pdf_path = sys.argv[1]
    theme = sys.argv[2]

    # Get project root
    project_root = get_project_root()
    print(f"Project root: {project_root}")

    # Validate PDF path
    pdf_path = Path(pdf_path).resolve()
    if not pdf_path.exists():
        print(f"Error: PDF not found: {pdf_path}")
        sys.exit(1)

    print(f"Reading PDF: {pdf_path}")
    print(f"Theme: {theme}")

    # Extract paper information
    metadata = get_pdf_metadata(str(pdf_path))
    paper_name = extract_paper_name(str(pdf_path), metadata)
    print(f"Extracted paper name: {paper_name}")

    # List theme papers
    theme_papers = list_theme_papers(theme, project_root)
    print(f"Papers in theme '{theme}': {theme_papers}")

    # Select comparison papers
    comparison_papers = select_comparison_papers(paper_name, theme, project_root, max_papers=5)
    print(f"Selected comparison papers: {comparison_papers}")

    # Read PDF content
    pdf_content, pdf_metadata = read_pdf_content(str(pdf_path))
    print(f"PDF content length: {len(pdf_content)} chars")

    # Read existing comparative
    comparative_content = read_comparative(theme, project_root)

    # Summary structure
    summary = f"""# {paper_name}

## 创作时间与刊物
- 时间: {pdf_metadata.get('creationDate', 'Unknown')}
- 刊物: {pdf_metadata.get('producer', 'Unknown')}

## 面向的问题与方法
[Summary will be generated]

## 方法流程

### 数据集创建
[Summary will be generated]

### 前处理
[Summary will be generated]

### 前向传播
[Summary will be generated]

### 反向传播
[Summary will be generated]

### 后处理
[Summary will be generated]
"""

    print(f"\n=== Paper Contrast Summary ===")
    print(f"Paper: {paper_name}")
    print(f"Theme: {theme}")
    print(f"Comparison papers: {comparison_papers}")
    print(f"Comparative.md exists: {len(comparative_content) > 0}")
    print(f"\nSummary template:\n{summary}")


if __name__ == '__main__':
    main()
