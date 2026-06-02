from __future__ import annotations

from collections import defaultdict
from pathlib import Path
import re
from typing import Dict, List, Set, Tuple

from wiki_utils import extract_wikilinks, load_markdown_pages, slugify, to_title


ROOT = Path(__file__).resolve().parents[1]
WIKI_DIR = ROOT / "wiki"
REPORT_PATH = ROOT / "reports" / "wiki_lint_report.md"


DIAGNOSTIC_PATTERNS = [
    r"\byou have\b",
    r"\bdiagnosis is\b",
    r"\bthis means you have\b",
    r"\bthis confirms diagnosis\b",
    r"\bdefinitely have\b",
]


WARNING_PATTERNS = [
    r"warning sign",
    r"emergency",
    r"chest pain",
    r"stroke",
    r"severe breathing",
    r"faint",
    r"seizure",
    r"bleeding",
    r"confusion",
]


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


def lint() -> Dict[str, object]:
    issues: Dict[str, object] = {}
    pages = load_markdown_pages(WIKI_DIR)
    if "index.md" not in pages:
        issues["missing_index"] = True
    if "log.md" not in pages:
        issues["missing_log"] = True

    title_to_path: Dict[str, str] = {}
    for rel, content in pages.items():
        title = to_title(rel, content)
        title_to_path[title] = rel
    resolver = build_link_resolver(title_to_path)

    broken: List[Tuple[str, str]] = []
    incoming: Dict[str, int] = defaultdict(int)
    for rel, content in pages.items():
        if rel == "log.md":
            continue
        for link in extract_wikilinks(content):
            if rel == "index.md" and link.lower() == "wikilinks":
                continue
            target_title = resolver.get(link) or resolver.get(slugify(link))
            if target_title:
                incoming[target_title] += 1
            else:
                broken.append((rel, link))
    issues["broken_links"] = broken

    orphans: List[str] = []
    for title, rel in title_to_path.items():
        if rel in {"index.md", "log.md"}:
            continue
        if incoming.get(title, 0) == 0 and rel != "index.md":
            orphans.append(rel)
    issues["orphans"] = sorted(orphans)

    lower_names: Dict[str, List[str]] = defaultdict(list)
    for rel in pages.keys():
        lower_names[Path(rel).name.lower()].append(rel)
    duplicates = {k: v for k, v in lower_names.items() if len(v) > 1}
    issues["duplicate_page_names"] = duplicates

    missing_source = []
    for rel, content in pages.items():
        if rel in {"index.md", "log.md"}:
            continue
        if "## Source" not in content:
            missing_source.append(rel)
    issues["missing_source"] = sorted(missing_source)

    diagnostic = []
    for rel, content in pages.items():
        if rel == "log.md" or rel.startswith("source-sections/"):
            continue
        lc = content.lower()
        for pat in DIAGNOSTIC_PATTERNS:
            if re.search(pat, lc):
                diagnostic.append((rel, pat))
                break
    issues["diagnostic_language"] = diagnostic

    missing_safety = []
    for rel, content in pages.items():
        if rel.startswith("source-sections/"):
            continue
        lc = content.lower()
        if any(re.search(pat, lc) for pat in WARNING_PATTERNS):
            if "⚠️" not in content and "urgent medical care" not in lc:
                missing_safety.append(rel)
    issues["missing_safety_note"] = sorted(set(missing_safety))

    source_pages = [p for p in pages.keys() if p.startswith("source-sections/")]
    source_title_map = {to_title(rel, pages[rel]): rel for rel in source_pages}
    unlinked_source_sections = []
    for source_title, source_rel in source_title_map.items():
        if incoming.get(source_title, 0) == 0:
            unlinked_source_sections.append(source_rel)
    issues["source_sections_unlinked"] = sorted(unlinked_source_sections)

    return issues


def write_report(issues: Dict[str, object]) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    pass_fail = "PASS"
    failing = []
    for key in [
        "missing_index",
        "missing_log",
        "broken_links",
        "duplicate_page_names",
        "missing_source",
        "diagnostic_language",
        "missing_safety_note",
    ]:
        value = issues.get(key)
        if value:
            pass_fail = "FAIL"
            failing.append(key)

    lines = [
        "# Wiki Lint Report",
        "",
        f"Status: **{pass_fail}**",
        "",
        "## Summary",
        "",
        f"- Broken links: {len(issues.get('broken_links', []))}",
        f"- Orphan pages: {len(issues.get('orphans', []))}",
        f"- Duplicate page names: {len(issues.get('duplicate_page_names', {}))}",
        f"- Missing source sections: {len(issues.get('missing_source', []))}",
        f"- Diagnostic language pages: {len(issues.get('diagnostic_language', []))}",
        f"- Missing safety note pages: {len(issues.get('missing_safety_note', []))}",
        f"- Unlinked source-section pages: {len(issues.get('source_sections_unlinked', []))}",
        "",
        "## Details",
        "",
    ]

    if issues.get("missing_index"):
        lines.append("- Missing `wiki/index.md`")
    if issues.get("missing_log"):
        lines.append("- Missing `wiki/log.md`")

    for src, link in issues.get("broken_links", []):
        lines.append(f"- Broken link: `{src}` -> `[[{link}]]`")

    for rel in issues.get("orphans", []):
        lines.append(f"- Orphan page: `{rel}`")

    for name, rels in issues.get("duplicate_page_names", {}).items():
        lines.append(f"- Duplicate page name `{name}` in: {', '.join(f'`{x}`' for x in rels)}")

    for rel in issues.get("missing_source", []):
        lines.append(f"- Missing source reference: `{rel}`")

    for rel, pat in issues.get("diagnostic_language", []):
        lines.append(f"- Diagnostic wording pattern `{pat}` in `{rel}`")

    for rel in issues.get("missing_safety_note", []):
        lines.append(f"- Warning content without safety note: `{rel}`")

    for rel in issues.get("source_sections_unlinked", []):
        lines.append(f"- Source section not linked by generated pages: `{rel}`")

    if len(lines) <= 14:
        lines.append("- No issues found.")

    REPORT_PATH.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def main() -> None:
    issues = lint()
    write_report(issues)
    print(f"Lint report written: {REPORT_PATH.as_posix()}")
    print(f"Broken links: {len(issues.get('broken_links', []))}")
    print(f"Orphans: {len(issues.get('orphans', []))}")
    print(f"Missing source: {len(issues.get('missing_source', []))}")


if __name__ == "__main__":
    main()
