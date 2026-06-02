# Hospital Wiki LLM

Karpathy-style single-source wiki Q&A project:

- Source truth: `raw/hospital_disease.md`
- Generated knowledge layer: `wiki/*.md`
- Retrieval layer: `wiki/index.md` + linked wiki pages
- LLM answering: Azure OpenAI
- No vector DB / embeddings / Chroma / FAISS / Pinecone

## Project Flow

1. Build wiki from raw markdown headings and concept sections.
2. Lint wiki quality and link integrity.
3. Ask questions using only wiki context and wikilink traversal.
4. Optionally compile wiki links into `knowledge/graph.json`.

## Setup

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Place Raw Source

Ensure this file exists:

- `raw/hospital_disease.md`

The source file is immutable truth. Do not edit it from scripts.

## Azure OpenAI Configuration

Copy values to `.env`:

- `AZURE_OPENAI_ENDPOINT`
- `AZURE_OPENAI_API_KEY`
- `AZURE_OPENAI_DEPLOYMENT`
- `AZURE_OPENAI_API_VERSION`

Template is already included in `.env.example`.

## Build Wiki

```powershell
python scripts/build_wiki.py
```

What build does:

- Splits raw markdown by headings
- Creates source-section pages
- Auto-detects concept types (diseases, symptoms, warning signs, investigations, departments, overlaps, groups)
- Generates wiki pages with `[[wikilinks]]`
- Rebuilds `wiki/index.md`
- Appends `wiki/log.md`

## Lint Wiki

```powershell
python scripts/lint_wiki.py
```

Writes report:

- `reports/wiki_lint_report.md`

## Compile Graph Helper

```powershell
python scripts/compile_wiki_to_graph.py
```

Writes:

- `knowledge/graph.json`

## Ask Questions

Single question:

```powershell
python scripts/ask_wiki.py --question "What diseases are connected to chest pain?"
```

Interactive:

```powershell
python scripts/ask_wiki.py --interactive
```

With saved retrieval context:

```powershell
python scripts/ask_wiki.py --question "What diseases are connected to chest pain?" --show-context
```

## Safety Limitation

This system is educational only:

- not diagnosis
- not treatment advice
- not a substitute for medical care
- never prescribe medicines
- use "possible related conditions"
- for emergency warning signs, advise urgent medical attention
