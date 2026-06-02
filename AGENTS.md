# AGENTS.md - Hospital Wiki LLM Rules

## Purpose

This project turns `raw/hospital_disease.md` into a linked Markdown wiki and uses that wiki as the only retrieval layer for Q&A.

- Educational reference only.
- Not diagnosis.
- Not a substitute for medical care.
- Do not prescribe treatment.
- Use wording like "possible related conditions".
- For severe warning signs (chest pain, stroke-like symptoms, severe breathing difficulty, fainting, severe allergic reaction, uncontrolled bleeding, seizure, confusion with illness), advise urgent medical attention.

## Source of Truth

- `raw/hospital_disease.md` is immutable source truth.
- Do not invent diseases, symptoms, warning signs, investigations, departments, or relationships.
- Preserve exact warning signs, investigation names, disease names, department names, and relationships from source.
- Every generated page must have `## Source` linking to the raw section path.

## Wiki Layer Rules

- Generated wiki lives under `wiki/`.
- Use Obsidian wikilinks (`[[Page Title]]`) heavily.
- `wiki/index.md` is the main navigation page and query entry point.
- `wiki/log.md` is append-only change history.
- Avoid copy-pasting entire raw file into one giant page.
- Split by source sections and concept pages.

## Ingestion Workflow

Use `python scripts/build_wiki.py`.

Required behavior:
1. Read `raw/hospital_disease.md`.
2. Split by headings.
3. Create source-section pages.
4. Identify important concepts automatically.
5. Create concept pages and add wikilinks.
6. Rebuild `wiki/index.md`.
7. Append build summary to `wiki/log.md`.

## Maintenance Workflow

- Keep pages aligned with source text.
- Update links when adding/removing pages.
- Keep titles stable for reliable wikilinks.
- Keep safety framing on pages that discuss warning signs or emergency patterns.

## Q&A Workflow

Use `python scripts/ask_wiki.py --question "<question>"` or `--interactive`.

Rules:
1. Read `wiki/index.md` first.
2. Select relevant pages by title/headings/content.
3. Follow wikilinks up to depth 2.
4. Build compact context from selected pages only.
5. Answer with Azure OpenAI using wiki context only.
6. If not in wiki, explicitly say wiki does not contain enough information.
7. Include selected page list in output.
8. Include urgent-care safety note when emergency signs are discussed.

## Lint Workflow

Use `python scripts/lint_wiki.py`.

Checks:
- Broken wikilinks
- Orphan pages
- Duplicate page names
- Missing source references
- Missing `index.md` / `log.md`
- Diagnostic wording
- Warning content without safety note
- Source-section pages not linked by generated pages

Output:
- `reports/wiki_lint_report.md`

## Update Workflow for Source Changes

When `raw/hospital_disease.md` changes:
1. Re-run `scripts/build_wiki.py`.
2. Re-run `scripts/lint_wiki.py`.
3. Re-run `scripts/compile_wiki_to_graph.py`.
4. Review `wiki/log.md` append entry and lint report.

## Prohibited

- Do not use vector DB or embeddings for retrieval in this project.
- Do not use Chroma, FAISS, Pinecone, or similar.
- Do not answer from outside knowledge when wiki context is insufficient.
