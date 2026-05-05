#!/usr/bin/env python3
"""
Read PDF file and extract text content.
Output the raw text for downstream processing.

Usage: python -m scripts.read_pdf <path_to_pdf>
"""

import sys
import re
from pathlib import Path


def clean_text_for_llm(text: str) -> str:
    """Clean extracted text to make it more LLM-friendly.

    - Remove excessive whitespace and empty lines
    - Fix hyphenated word breaks
    - Normalize multiple spaces
    - Fix common text extraction artifacts
    - Preserve paragraph structure
    """
    # Fix hyphenated word breaks at end of lines (e.g., "gen-\nerate" -> "generate")
    text = re.sub(r'(\w+)-\n(\w+)', r'\1\2', text)

    # Normalize multiple spaces to single space
    text = re.sub(r' +', ' ', text)

    # Remove excessive blank lines (more than 2 consecutive newlines)
    text = re.sub(r'\n{3,}', '\n\n', text)

    # Remove excessive leading whitespace (indentation artifacts)
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        # Keep helpful indentation for lists
        stripped = line.strip()
        if len(stripped) == 0:
            cleaned_lines.append('')
            continue

        # Remove extreme left padding that's likely extraction artifact
        leading_spaces = len(line) - len(line.lstrip())
        if leading_spaces > 20:
            # This is likely a text artifact, strip it
            cleaned_lines.append(stripped)
        else:
            cleaned_lines.append(line)

    text = '\n'.join(cleaned_lines)

    # Remove standalone short lines that are likely elements (✓, ✗, page markers, etc)
    # but keep them if they're part of a table or list
    lines = text.split('\n')
    cleaned_lines = []

    i = 0
    while i < len(lines):
        line = lines[i].strip()
        next_line = lines[i + 1].strip() if i + 1 < len(lines) else ''

        # Keep standalone symbols if they appear to be in a table context
        if line in ['✓', '✗']:
            # Keep if next line is also a symbol or table-related
            if next_line in ['✓', '✗', 'GRES', 'RES', '']:
                cleaned_lines.append(line)
            # Otherwise skip (likely image annotation)
            i += 1
            continue

        # Keep list markers
        if re.match(r'^\d+\.', line) or re.match(r'^[A-D]\.', line) or line == '1':
            cleaned_lines.append(line)
        # Keep section headers (short but meaningful)
        elif len(line) < 100 and re.match(r'^[A-Z]', line):
            cleaned_lines.append(line)
        # Keep lines with substantial content
        elif len(line) >= 10:
            cleaned_lines.append(line)

        i += 1

    text = '\n'.join(cleaned_lines)

    # Final cleanup: remove very short lines surrounded by longer text
    lines = text.split('\n')
    final_lines = []
    for i, line in enumerate(lines):
        stripped = line.strip()
        if len(stripped) < 5 and stripped not in ['✓', '✗', '']:
            # Check if this is likely noise
            prev_line = lines[i-1].strip() if i > 0 else ''
            next_line = lines[i+1].strip() if i < len(lines)-1 else ''
            # Skip if surrounded by long text (likely artifact)
            if len(prev_line) > 50 and len(next_line) > 50:
                continue
        final_lines.append(line)

    return '\n'.join(final_lines)


def extract_text_simple(pdf_path: str) -> tuple[str, dict]:
    """Extract text using PyMuPDF with simple page-by-page projection.

    This projects all text from a page onto a single column, which helps
    with multi-column PDFs by reading top-to-bottom within each page.

    Returns:
        tuple: (text_content, metadata_dict)
    """
    import fitz  # PyMuPDF
    doc = fitz.open(pdf_path)

    # Extract metadata
    metadata = doc.metadata

    text_parts = []
    # Extract text from each page using blocks mode and sorting
    for page_num, page in enumerate(doc, 1):
        text_dict = page.get_text('blocks')
        # Sort blocks by position (top to bottom)
        text_dict.sort(key=lambda b: (b[1], b[0]))

        page_text = []
        for block in text_dict:
            # Block format: (x0, y0, x1, y1, "text", block_type, block_no)
            if len(block) >= 5:
                text = block[4].strip()
                if text:
                    page_text.append(text)

        if page_text:
            text_parts.append(f"--- Page {page_num} ---\n" + '\n'.join(page_text))

    doc.close()
    return '\n\n'.join(text_parts), metadata


def read_pdf_pymupdf(pdf_path: str) -> tuple[str, dict]:
    """Read PDF using PyMuPDF (fitz).

    Returns:
        tuple: (text_content, metadata_dict)
    """
    import fitz  # PyMuPDF
    doc = fitz.open(pdf_path)

    # Extract metadata
    metadata = doc.metadata

    text_parts = []
    # Extract text from each page
    for page_num, page in enumerate(doc, 1):
        text = page.get_text()
        if text:
            # Clean text for LLM readability
            cleaned = clean_text_for_llm(text)
            text_parts.append(f"--- Page {page_num} ---\n{cleaned}")

    doc.close()
    return '\n\n'.join(text_parts), metadata


def read_pdf_pypdf(pdf_path: str) -> tuple[str, dict]:
    """Read PDF using pypdf.

    Returns:
        tuple: (text_content, metadata_dict)
    """
    import pypdf
    reader = pypdf.PdfReader(pdf_path)

    # Extract metadata
    metadata = reader.metadata if reader.metadata else {}

    text_parts = []
    for page_num, page in enumerate(reader.pages, 1):
        text = page.extract_text() or ""
        if text.strip():
            text_parts.append(f"--- Page {page_num} ---\n{text}")

    return '\n\n'.join(text_parts), metadata


def read_pdf_pdfminer(pdf_path: str) -> tuple[str, dict]:
    """Read PDF using pdfminer.six.

    Returns:
        tuple: (text_content, metadata_dict)
    """
    from pdfminer.high_level import extract_text, extract_metadata
    text = extract_text(pdf_path)

    # Extract basic metadata from file
    metadata = {}
    try:
        from pdfminer.pdfparser import PDFParser
        from pdfminer.pdfdocument import PDFDocument
        with open(pdf_path, 'rb') as f:
            parser = PDFParser(f)
            doc = PDFDocument(parser)
            metadata.update(doc.info)
    except:
        pass

    return text, metadata


def read_pdf(pdf_path: str) -> tuple[str, dict]:
    """Read PDF file and extract text content.

    Tries multiple methods in priority order:
    1. PyMuPDF (fitz) - fastest and most reliable
    2. pypdf - good alternative
    3. pdfminer.six - for complex PDFs

    Returns:
        tuple: (text_content, metadata_dict)
    """
    errors = []
    methods = ['PyMuPDF', 'pypdf', 'pdfminer.six']

    # Try PyMuPDF first (recommended)
    try:
        content, metadata = read_pdf_pymupdf(pdf_path)
        return content, metadata
    except ImportError:
        errors.append("PyMuPDF (fitz) not installed")
    except Exception as e:
        errors.append(f"PyMuPDF failed: {e}")

    # Try pypdf
    try:
        content, metadata = read_pdf_pypdf(pdf_path)
        return content, metadata
    except ImportError:
        errors.append("pypdf not installed")
    except Exception as e:
        errors.append(f"pypdf failed: {e}")

    # Try pdfminer.six
    try:
        content, metadata = read_pdf_pdfminer(pdf_path)
        return content, metadata
    except ImportError:
        errors.append("pdfminer.six not installed")
    except Exception as e:
        errors.append(f"pdfminer.six failed: {e}")

    # All methods failed
    error_msg = "Error: All PDF reading methods failed.\n"
    error_msg += f"Methods tried: {', '.join(methods)}\n"
    error_msg += f"Errors: {'; '.join(errors)}\n"
    error_msg += "Please install PyMuPDF with: pip install PyMuPDF"
    return error_msg, {}


def main():
    if len(sys.argv) < 2:
        print("Usage: python -m scripts.read_pdf <path_to_pdf>")
        sys.exit(1)

    pdf_path = sys.argv[1]

    # Resolve to absolute path
    pdf_path = Path(pdf_path).resolve()

    if not pdf_path.exists():
        print(f"Error: File not found: {pdf_path}")
        sys.exit(1)

    # Get content and metadata
    content, metadata = read_pdf(str(pdf_path))

    # Handle error case
    if content.startswith("Error:"):
        print(content)
        sys.exit(1)

    # Output metadata first
    print("=== PDF Metadata ===")
    for key, value in metadata.items():
        print(f"{key}: {value}")
    print()

    # Output content with page markers preserved
    # Limit output to avoid token overflow (output first 10000 chars)
    max_output = 10000
    if len(content) > max_output:
        print(content[:max_output])
        print(f"\n... [content truncated, {len(content)} total chars]")
    else:
        print(content)


if __name__ == '__main__':
    main()
