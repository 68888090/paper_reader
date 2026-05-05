#!/usr/bin/env python3
"""Apply reading perspective to generate customized prompt fragments.

Usage:
    python3 apply_perspective.py <theme> <angle>   # Read specific perspective
    python3 apply_perspective.py <theme> --list     # List all angles
    python3 apply_perspective.py <theme> --all      # Read all perspectives
"""

import sys
import json
from pathlib import Path
from typing import Optional


SRC_DIR = Path("src/items")


def load_perspective(theme: str, angle: str) -> Optional[str]:
    path = SRC_DIR / theme / f"perspective_{angle}.md"
    if path.exists():
        return path.read_text(encoding="utf-8")
    return None


def list_angles(theme: str) -> list[str]:
    theme_dir = SRC_DIR / theme
    if not theme_dir.exists():
        return []
    angles = []
    for f in sorted(theme_dir.glob("perspective_*.md")):
        name = f.stem[len("perspective_"):]
        angles.append(name)
    return angles


def parse_section(content: str, section_name: str) -> list[str]:
    """Extract bullet points from a ## section."""
    items = []
    in_section = False
    for line in content.split("\n"):
        stripped = line.strip()
        if stripped.startswith(f"## {section_name}"):
            in_section = True
            continue
        if in_section:
            if stripped.startswith("##") and section_name not in stripped:
                break
            if stripped.startswith("- ") or stripped.startswith("* "):
                item = stripped[2:].strip()
                if item and not item.startswith("<!--"):
                    items.append(item)
    return items


def parse_paper_references(content: str) -> list[dict]:
    """Extract paper references and angle analysis."""
    papers = []
    in_section = False
    current_id = None
    current_lines = []
    for line in content.split("\n"):
        stripped = line.strip()
        if stripped.startswith("## 相关论文与角度分析"):
            in_section = True
            continue
        if in_section:
            if stripped.startswith("##") and "相关论文" not in stripped:
                if current_id:
                    papers.append({"paper_id": current_id, "analysis": "\n".join(current_lines).strip()})
                break
            if stripped.startswith("### "):
                if current_id:
                    papers.append({"paper_id": current_id, "analysis": "\n".join(current_lines).strip()})
                    current_lines = []
                current_id = stripped[4:].strip()
                continue
            if current_id is not None:
                current_lines.append(line.rstrip())
    if current_id:
        papers.append({"paper_id": current_id, "analysis": "\n".join(current_lines).strip()})
    return papers


def parse_notes(content: str) -> list[dict]:
    """Extract reading notes from perspective content."""
    notes = []
    in_notes = False
    current_title = None
    current_body = []
    for line in content.split("\n"):
        stripped = line.strip()
        if stripped.startswith("## 读书笔记"):
            in_notes = True
            continue
        if in_notes:
            if stripped.startswith("##") and "读书笔记" not in stripped:
                break
            if stripped.startswith("### "):
                if current_title:
                    notes.append({"title": current_title, "body": "\n".join(current_body).strip()})
                    current_body = []
                current_title = stripped[4:].strip()
                continue
            if current_title is not None and stripped and not stripped.startswith("<!--"):
                current_body.append(line.rstrip())
    if current_title:
        notes.append({"title": current_title, "body": "\n".join(current_body).strip()})
    return notes


def parse_core_questions(content: str) -> str:
    """Extract core questions from the perspective."""
    in_section = False
    lines = []
    for line in content.split("\n"):
        stripped = line.strip()
        if stripped.startswith("## 核心问题"):
            in_section = True
            continue
        if in_section:
            if stripped.startswith("##") and "核心问题" not in stripped:
                break
            if stripped and not stripped.startswith("<!--"):
                lines.append(stripped)
    return "\n".join(lines)


def build_summary_fragment(angle_name: str, dimensions: list[str],
                           questions: str, notes: list[dict], papers: list[dict]) -> str:
    """Build prompt fragment for paper analyst summary customization."""
    parts = [f"## 个性化关注 — 角度「{angle_name}」"]
    parts.append(f"在生成总结后，请从「{angle_name}」角度追加个性化分析（引用格式）：\n")

    if questions:
        parts.append(f"**用户在意的核心问题**: {questions}\n")

    if dimensions:
        parts.append("**关注维度**:")
        for d in dimensions:
            parts.append(f"- {d}")

    if papers:
        parts.append(f"\n**该角度下已有论文分析**（参考已有定位，不强制关联）:")
        for p in papers:
            parts.append(f"- {p['paper_id']}: {p['analysis'][:150]}")

    if notes:
        parts.append(f"\n**用户笔记参考**:")
        for n in notes:
            parts.append(f"- {n['title']}: {n['body'][:200]}")

    return "\n".join(parts)


def build_contrast_fragment(angle_name: str, dimensions: list[str]) -> str:
    """Build prompt fragment for angle-specific contrast."""
    if not dimensions:
        return ""
    parts = [f"## 角度「{angle_name}」的地方性对比"]
    parts.append(f"在生成该角度的对比时，额外关注以下维度：\n")
    for d in dimensions:
        parts.append(f"- {d}")
    parts.append(f"\n标注每篇论文在「{angle_name}」角度下的优劣，指出最符合用户关注重点的论文。")
    return "\n".join(parts)


def process_single(theme: str, angle: str) -> dict:
    """Process a single perspective angle."""
    content = load_perspective(theme, angle)
    if content is None:
        return {
            "angle": angle,
            "found": False,
            "error": f"视角 '{angle}' 不存在于主题 '{theme}'",
        }

    dimensions = parse_section(content, "关注维度")
    questions = parse_core_questions(content)
    papers = parse_paper_references(content)
    notes = parse_notes(content)

    return {
        "angle": angle,
        "found": True,
        "dimensions": dimensions,
        "core_questions": questions,
        "related_papers": papers,
        "notes": notes,
        "prompt_fragment": build_summary_fragment(angle, dimensions, questions, notes, papers),
        "contrast_prompt_fragment": build_contrast_fragment(angle, dimensions),
    }


def cmd_list(theme: str):
    angles = list_angles(theme)
    result = {
        "theme": theme,
        "angles": angles,
        "count": len(angles),
    }
    json.dump(result, sys.stdout, ensure_ascii=False, indent=2)


def cmd_all(theme: str):
    angles = list_angles(theme)
    results = []
    for angle in angles:
        results.append(process_single(theme, angle))

    # Merge all dimensions across angles
    all_dimensions = []
    seen = set()
    for r in results:
        for d in r.get("dimensions", []):
            if d not in seen:
                all_dimensions.append(d)
                seen.add(d)

    merged_fragment = ""
    if results:
        parts = ["## 多角度个性化关注"]
        for r in results:
            if r["found"]:
                parts.append(f"\n### 角度「{r['angle']}」")
                parts.append(f"关注维度: {', '.join(r['dimensions'][:3])}")
                if r["core_questions"]:
                    parts.append(f"核心问题: {r['core_questions'][:100]}")
        merged_fragment = "\n".join(parts)

    output = {
        "theme": theme,
        "angles": angles,
        "results": results,
        "merged_dimensions": all_dimensions,
        "merged_prompt_fragment": merged_fragment,
    }
    json.dump(output, sys.stdout, ensure_ascii=False, indent=2)


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 apply_perspective.py <theme> [<angle> | --list | --all]", file=sys.stderr)
        sys.exit(1)

    theme = sys.argv[1]

    if len(sys.argv) >= 3:
        arg2 = sys.argv[2]
        if arg2 == "--list":
            cmd_list(theme)
        elif arg2 == "--all":
            cmd_all(theme)
        else:
            result = process_single(theme, arg2)
            json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
    else:
        # Default: list available angles
        cmd_list(theme)


if __name__ == "__main__":
    main()
