#!/usr/bin/env python3
"""
Download paper from URL and save to src/tmp/ directory.

Usage: python -m scripts.get_paper <URL>
"""

from typing import Optional
import sys
import os
import re
import requests
from pathlib import Path


def sanitize_filename(name: str) -> str:
    """Sanitize string to be used as filename."""
    # Remove invalid characters
    name = re.sub(r'[<>:"/\\|?*]', '', name)
    # Replace multiple spaces with single underscore
    name = re.sub(r'\s+', '_', name)
    return name[:200]  # Limit length


def get_arxiv_id(url: str) -> Optional[str]:
    """Extract arXiv ID from URL."""
    # Match arXiv URLs: https://arxiv.org/abs/2306.00968 or https://arxiv.org/abs/2306.00968v1
    match = re.search(r'arxiv\.org/(?:abs|pdf)/(\d+\.\d+)', url)
    if match:
        return match.group(1)
    return None


def download_from_arxiv(url: str, output_dir: Path) -> Optional[Path]:
    """Download paper from arXiv."""
    arxiv_id = get_arxiv_id(url)
    if not arxiv_id:
        return None

    # Try PDF URL
    pdf_url = f'https://arxiv.org/pdf/{arxiv_id}.pdf'

    try:
        response = requests.get(pdf_url, timeout=30)
        response.raise_for_status()

        # Check if it's actually a PDF (not an error page)
        if response.headers.get('content-type') == 'application/pdf' or response.content[:4] == b'%PDF':
            # Try to get title from arXiv API
            title = f"paper_{arxiv_id}"
            try:
                api_url = f'https://export.arxiv.org/api/entry?id={arxiv_id}'
                api_response = requests.get(api_url, timeout=10)
                if api_response.status_code == 200:
                    title_match = re.search(r'<title>([^<]+)</title>', api_response.text)
                    if title_match:
                        title = sanitize_filename(title_match.group(1).strip())
            except:
                pass

            output_path = output_dir / f"{title}.pdf"
            with open(output_path, 'wb') as f:
                f.write(response.content)
            return output_path
    except Exception as e:
        print(f"Error downloading from arXiv: {e}")

    return None


def download_from_url(url: str, output_dir: Path) -> Optional[Path]:
    """Download paper from any URL."""
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        # Check if it's a PDF
        content_type = response.headers.get('content-type', '')
        if 'pdf' in content_type or response.content[:4] == b'%PDF':
            # Try to extract filename from URL
            filename = url.split('/')[-1]
            if not filename.endswith('.pdf'):
                filename = 'paper.pdf'

            # Sanitize
            filename = sanitize_filename(filename)
            if not filename.endswith('.pdf'):
                filename += '.pdf'

            output_path = output_dir / filename
            with open(output_path, 'wb') as f:
                f.write(response.content)
            return output_path
    except Exception as e:
        print(f"Error downloading from URL: {e}")

    return None


def get_project_root() -> Path:
    """Get project root directory (paper_Reader/)."""
    script_dir = Path(__file__).resolve().parent
    # Current structure: .../paper_Reader/.claude/skills/paper-reader/scripts/
    # We need to find the paper_Reader directory
    # Check if parent's parent's parent is '.claude' and go up from there
    potential_root = script_dir.parent.parent.parent.parent  # goes to paper_Reader/
    if (potential_root / '.claude').exists():
        return potential_root
    # Fallback: look for src/ directory in ancestors
    for parent in script_dir.parents:
        if (parent / 'src').exists():
            return parent
    # Last fallback: use current working directory
    return Path.cwd()


def main():
    if len(sys.argv) < 2:
        print("Usage: python -m scripts.get_paper <URL>")
        sys.exit(1)

    url = sys.argv[1]

    # Get project root and output directory
    project_root = get_project_root()
    output_dir = project_root / 'src' / 'tmp'

    # Create output directory if not exists
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Downloading paper from: {url}")

    # Try arXiv first (most common for academic papers)
    output_path = download_from_arxiv(url, output_dir)

    # Fall back to direct download
    if not output_path:
        output_path = download_from_url(url, output_dir)

    if output_path:
        print(f"Downloaded to: {output_path}")
    else:
        print("Failed to download paper. Please check the URL.")
        sys.exit(1)


if __name__ == '__main__':
    main()
