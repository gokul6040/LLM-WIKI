from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

from wiki_utils import extract_wikilinks, load_markdown_pages, to_title


ROOT = Path(__file__).resolve().parents[1]
WIKI_DIR = ROOT / "wiki"
GRAPH_PATH = ROOT / "knowledge" / "graph.json"
GRAPH_FULL_PATH = ROOT / "knowledge" / "graph_full.json"
GRAPH_VISUAL_PATH = ROOT / "knowledge" / "graph_visual.json"


def build_graph(title_to_path: Dict[str, str], pages: Dict[str, str], include_source_sections: bool) -> Dict[str, object]:
    nodes: List[Dict[str, str]] = []
    edges: List[Dict[str, str]] = []
    allowed_titles = set()

    for title, rel in sorted(title_to_path.items()):
        if not include_source_sections and rel.startswith("source-sections/"):
            continue
        nodes.append({"id": title, "path": rel})
        allowed_titles.add(title)

    for rel, content in pages.items():
        src_title = to_title(rel, content)
        if src_title not in allowed_titles:
            continue
        for link in extract_wikilinks(content):
            if link in allowed_titles:
                edges.append({"source": src_title, "target": link, "type": "wikilink"})

    return {
        "meta": {
            "source_of_truth": "wiki/*.md",
            "includes_source_sections": include_source_sections,
            "node_count": len(nodes),
            "edge_count": len(edges),
        },
        "nodes": nodes,
        "edges": edges,
    }


def main() -> None:
    pages = load_markdown_pages(WIKI_DIR)
    title_to_path: Dict[str, str] = {}
    for rel, content in pages.items():
        title_to_path[to_title(rel, content)] = rel

    graph_full = build_graph(title_to_path, pages, include_source_sections=True)
    graph_visual = build_graph(title_to_path, pages, include_source_sections=False)

    GRAPH_PATH.parent.mkdir(parents=True, exist_ok=True)
    # Keep graph.json as backward-compatible full graph.
    GRAPH_PATH.write_text(json.dumps(graph_full, indent=2), encoding="utf-8")
    GRAPH_FULL_PATH.write_text(json.dumps(graph_full, indent=2), encoding="utf-8")
    GRAPH_VISUAL_PATH.write_text(json.dumps(graph_visual, indent=2), encoding="utf-8")
    print(f"Graph written: {GRAPH_PATH.as_posix()}")
    print(f"Graph full written: {GRAPH_FULL_PATH.as_posix()}")
    print(f"Graph visual written: {GRAPH_VISUAL_PATH.as_posix()}")
    print(f"Full -> Nodes: {graph_full['meta']['node_count']}, Edges: {graph_full['meta']['edge_count']}")
    print(f"Visual -> Nodes: {graph_visual['meta']['node_count']}, Edges: {graph_visual['meta']['edge_count']}")


if __name__ == "__main__":
    main()
