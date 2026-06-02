from __future__ import annotations

import argparse
from pathlib import Path
import re
from typing import Dict, List, Set, Tuple

from azure_llm import ask_azure_llm
from wiki_utils import (
    extract_wikilinks,
    load_markdown_pages,
    slugify,
    token_set,
    to_title,
)


ROOT = Path(__file__).resolve().parents[1]
WIKI_DIR = ROOT / "wiki"
REPORTS_DIR = ROOT / "reports"


SYSTEM_PROMPT = """
You answer strictly from supplied wiki context.
Rules:
- Educational only.
- Never diagnose.
- Never prescribe medication or treatment plans.
- Use wording like "possible related conditions".
- If context is insufficient, say the wiki does not contain enough information.
- If warning signs or emergency red flags are involved, include an urgent-care safety note.
""".strip()


EMERGENCY_RE = re.compile(
    r"(chest pain|stroke|weakness|speech|breathing|shortness of breath|faint|seizure|bleeding|allergic|confusion)",
    re.IGNORECASE,
)


def build_link_resolver(title_to_path: Dict[str, str]) -> Dict[str, str]:
    resolver: Dict[str, str] = {}
    for title in title_to_path:
        resolver[title] = title
        resolver[slugify(title)] = title
        if " / " in title:
            short = title.split(" / ", 1)[0].strip()
            resolver[short] = title
            resolver[slugify(short)] = title
        if " and " in title:
            alt = title.replace(" and ", " / ")
            resolver[alt] = title
            resolver[slugify(alt)] = title
    return resolver


def index_pages() -> Tuple[Dict[str, str], Dict[str, str], Dict[str, Set[str]]]:
    pages = load_markdown_pages(WIKI_DIR)
    title_to_path: Dict[str, str] = {}
    path_to_title: Dict[str, str] = {}
    graph: Dict[str, Set[str]] = {}

    for rel_path, content in pages.items():
        title = to_title(rel_path, content)
        title_to_path[title] = rel_path
        path_to_title[rel_path] = title
    resolver = build_link_resolver(title_to_path)

    for rel_path, content in pages.items():
        src_title = path_to_title[rel_path]
        graph[src_title] = set()
        for link in extract_wikilinks(content):
            target = resolver.get(link) or resolver.get(slugify(link))
            if target:
                graph[src_title].add(target)
    return pages, title_to_path, graph


def score_page(question: str, title: str, content: str) -> float:
    q_tokens = token_set(question)
    c_tokens = token_set(content)
    title_tokens = token_set(title)
    overlap = len(q_tokens.intersection(c_tokens))
    title_overlap = len(q_tokens.intersection(title_tokens))
    phrase_bonus = 2.5 if question.lower() in content.lower() else 0.0
    return overlap + (title_overlap * 2.0) + phrase_bonus


def select_seed_pages(question: str, pages: Dict[str, str], title_to_path: Dict[str, str], k: int = 5) -> List[str]:
    scored: List[Tuple[float, str]] = []
    for title, rel_path in title_to_path.items():
        content = pages[rel_path]
        s = score_page(question, title, content)
        if s > 0:
            scored.append((s, title))
    scored.sort(reverse=True)
    return [t for _, t in scored[:k]]


def expand_with_links(seed_titles: List[str], graph: Dict[str, Set[str]], max_depth: int = 2) -> List[str]:
    visited: Set[str] = set(seed_titles)
    frontier = list(seed_titles)
    for _ in range(max_depth):
        nxt: List[str] = []
        for title in frontier:
            for neighbor in graph.get(title, set()):
                if neighbor not in visited:
                    visited.add(neighbor)
                    nxt.append(neighbor)
        frontier = nxt
        if not frontier:
            break
    return list(visited)


def build_context(selected_titles: List[str], title_to_path: Dict[str, str], pages: Dict[str, str], max_chars: int = 14000) -> str:
    blocks: List[str] = []
    running = 0
    for title in selected_titles:
        rel_path = title_to_path.get(title)
        if not rel_path:
            continue
        content = pages[rel_path]
        block = f"## {title}\nPath: {rel_path}\n\n{content.strip()}\n"
        if running + len(block) > max_chars:
            break
        blocks.append(block)
        running += len(block)
    return "\n\n".join(blocks).strip()


def safety_footer_if_needed(question: str, answer: str, context: str) -> str:
    if EMERGENCY_RE.search(question) or EMERGENCY_RE.search(context):
        if "urgent" not in answer.lower() and "emergency" not in answer.lower():
            return (
                answer.rstrip()
                + "\n\n⚠️ If severe warning signs are present, seek urgent medical care immediately. "
                "This wiki is educational only and not a diagnostic tool."
            )
    return answer


def ask_once(question: str, show_context: bool) -> None:
    pages, title_to_path, graph = index_pages()
    if "index.md" not in pages:
        raise RuntimeError("wiki/index.md not found. Build wiki first.")

    seed = select_seed_pages(question, pages, title_to_path, k=6)
    selected = expand_with_links(seed, graph, max_depth=2)
    selected_sorted = sorted(selected, key=lambda x: x.lower())
    context = build_context(selected_sorted, title_to_path, pages)

    user_prompt = (
        f"Question: {question}\n\n"
        f"Selected wiki pages: {', '.join(selected_sorted) if selected_sorted else '(none)'}\n\n"
        f"Context (wiki-only):\n{context}\n\n"
        "Return:\n"
        "1) Selected page list\n"
        "2) Educational answer using only this context\n"
        "3) If not enough context, clearly say so\n"
    )

    answer = ask_azure_llm(SYSTEM_PROMPT, user_prompt)
    answer = safety_footer_if_needed(question, answer, context)

    print("\nSelected Pages:")
    for title in selected_sorted:
        print(f"- {title}")
    print("\nAnswer:\n")
    print(answer)

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    (REPORTS_DIR / "last_answer.md").write_text(answer + "\n", encoding="utf-8")
    if show_context:
        (REPORTS_DIR / "last_context.md").write_text(context + "\n", encoding="utf-8")
        print("\nContext written to reports/last_context.md")


def run_interactive(show_context: bool) -> None:
    print("Interactive mode. Type 'exit' to quit.")
    while True:
        question = input("\nquestion> ").strip()
        if not question:
            continue
        if question.lower() in {"exit", "quit"}:
            break
        ask_once(question, show_context=show_context)


def main() -> None:
    parser = argparse.ArgumentParser(description="Ask questions against wiki markdown pages.")
    parser.add_argument("--question", type=str, default="")
    parser.add_argument("--interactive", action="store_true")
    parser.add_argument("--show-context", action="store_true")
    args = parser.parse_args()

    if args.interactive:
        run_interactive(show_context=args.show_context)
        return
    if not args.question:
        raise SystemExit("Pass --question or use --interactive")
    ask_once(args.question, show_context=args.show_context)


if __name__ == "__main__":
    main()
