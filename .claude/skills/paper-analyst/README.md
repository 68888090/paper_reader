# Paper Analyst - Deep Paper Analysis Skill

This skill focuses on deep reading and understanding of research papers,
generating comprehensive Chinese summaries and performing comparative analysis.

## Key Capabilities

1. **Read and Understand PDF Papers** - Directly read PDFs and extract content
2. **Generate Structured Summaries** - Follow write_summary.md format exactly
3. **Modify Existing Summaries** - Based on modify_summary.md rules
4. **Comparative Analysis** - Compare multiple papers for innovations

## File Location
- SKILL.md: .claude/skills/paper-analyst/SKILL.md
- Prompt: Direct LLM prompt (no separate script needed)

## Usage

Use this skill when user wants to:
1. Read and summarize a research paper from PDF
2. Modify existing paper summaries with new contributions
3. Compare multiple papers for innovative points

## Processing Flow

1. Read PDF content
2. Understand research problem and solution
3. Extract methodology step-by-step
4. Generate structured summary in Chinese
5. If modifying, add citations below original content
6. If comparing, output innovation comparison
