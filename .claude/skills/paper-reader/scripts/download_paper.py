#!/usr/bin/env python3
"""
快速下载单篇论文的独立脚本。
Usage: python download_paper.py <arxiv_id_or_url>
"""
import sys
import re
import os
import requests
from pathlib import Path

def sanitize_filename(name: str) -> str:
    name = re.sub(r'[<>:"/\\|?*]', '', name)
    name = re.sub(r'\s+', '_', name)
    return name[:200]

def get_arxiv_id(url_or_id: str) -> str:
    match = re.search(r'(\d{4}\.\d{4,5})', url_or_id)
    if match:
        return match.group(1)
    return None

def main():
    if len(sys.argv) < 2:
        print("Usage: python download_paper.py <arxiv_id_or_url>")
        sys.exit(1)

    arxiv_id = get_arxiv_id(sys.argv[1])
    if not arxiv_id:
        print(f"Error: Cannot extract arXiv ID from: {sys.argv[1]}")
        sys.exit(1)

    # Find project root
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent.parent.parent.parent
    if not (project_root / '.claude').exists():
        for p in script_dir.parents:
            if (p / 'src').exists():
                project_root = p
                break

    output_dir = project_root / 'src' / 'tmp'
    output_dir.mkdir(parents=True, exist_ok=True)

    pdf_url = f'https://arxiv.org/pdf/{arxiv_id}.pdf'
    print(f"Downloading: {pdf_url}")

    try:
        r = requests.get(pdf_url, timeout=60)
        r.raise_for_status()
    except Exception as e:
        print(f"Download failed: {e}")
        sys.exit(1)

    # Get title
    title = f"paper_{arxiv_id}"
    try:
        api_r = requests.get(f'https://export.arxiv.org/api/query?id_list={arxiv_id}', timeout=15)
        if api_r.status_code == 200:
            title_match = re.search(r'<title>([^<]+)</title>', api_r.text)
            if title_match:
                raw_title = title_match.group(1).strip()
                # Skip the first <title> which is "ArXiv Query..."
                titles = re.findall(r'<title>([^<]+)</title>', api_r.text)
                for t in titles:
                    if t.strip() != 'ArXiv Query Results':
                        raw_title = t.strip()
                        break
                title = sanitize_filename(raw_title)
    except:
        pass

    output_path = output_dir / f"{title}.pdf"
    with open(output_path, 'wb') as f:
        f.write(r.content)
    print(f"Saved to: {output_path}")
    return str(output_path)

if __name__ == '__main__':
    result = main()
    if result:
        print(result)
