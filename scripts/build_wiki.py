from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from pathlib import Path
import re
from typing import Dict, List, Tuple

from wiki_utils import (
    Section,
    clean_heading,
    compact_text,
    ensure_dir,
    parse_markdown_sections,
    slugify,
    top_lines,
    write_text,
)


ROOT = Path(__file__).resolve().parents[1]
RAW_FILE = ROOT / "raw" / "hospital_disease.md"
WIKI_DIR = ROOT / "wiki"
MANAGED_FOLDERS = [
    "source-sections",
    "groups",
    "diseases",
    "symptoms",
    "warning-signs",
    "investigations",
    "departments",
    "overlaps",
]


EMERGENCY_NOTE = (
    "> ⚠️ **Educational reference only.** This wiki does not diagnose conditions and does not prescribe treatment. "
    "If severe warning signs are present (chest pain, stroke-like symptoms, severe breathing difficulty, fainting, "
    "severe allergic reaction, uncontrolled bleeding, seizure, or confusion with illness), seek urgent medical care."
)


def section_body_map_from_children(section: Section, child_sections: List[Section]) -> Dict[str, List[str]]:
    out: Dict[str, List[str]] = defaultdict(list)
    if child_sections:
        for child in child_sections:
            out[child.heading_clean] = [ln for ln in child.body.splitlines() if ln.strip()]
    else:
        out["Overview"] = [ln for ln in section.body.splitlines() if ln.strip()]
    return out


def bullet_items(lines: List[str]) -> List[str]:
    items: List[str] = []
    for line in lines:
        m = re.match(r"^\s*-\s+(.*)$", line)
        if m:
            items.append(m.group(1).strip())
    return items


def infer_title_alias_map(sections: List[Section]) -> Dict[str, str]:
    mapping: Dict[str, str] = {}
    for sec in sections:
        title = clean_heading(sec.heading_clean)
        canonical = title
        mapping[canonical] = canonical
        if " / " in canonical:
            mapping[canonical.split(" / ", 1)[0].strip()] = canonical
        if " and " in canonical:
            mapping[canonical.replace(" and ", " / ")] = canonical
        if " - " in canonical:
            mapping[canonical.split(" - ", 1)[0].strip()] = canonical
    return mapping


def linkify_term(term: str, title_map: Dict[str, str]) -> str:
    plain = term.strip().strip(".")
    plain = re.sub(r"\s+", " ", plain)
    if plain in title_map:
        return f"[[{title_map[plain]}]]"
    return plain


def classify_sections(sections: List[Section]) -> Dict[str, List[Section]]:
    by_type: Dict[str, List[Section]] = defaultdict(list)
    for sec in sections:
        path_text = " > ".join(sec.path)
        if sec.level == 2 and "Major Disease Groups" in path_text:
            by_type["groups"].append(sec)
        elif sec.level == 2 and "Disease Profiles" in path_text:
            by_type["diseases"].append(sec)
        elif sec.level == 2 and "Symptom Relationship Index" in path_text:
            by_type["symptoms"].append(sec)
        elif sec.level == 2 and "Emergency Warning Sign Index" in path_text:
            by_type["warning-signs"].append(sec)
        elif sec.level == 2 and "Investigation Index" in path_text:
            by_type["investigations"].append(sec)
        elif sec.level == 2 and "Department Routing Index" in path_text:
            by_type["departments"].append(sec)
        elif sec.level == 2 and "Cross-Disease Reasoning Notes" in path_text:
            by_type["overlaps"].append(sec)
    return by_type


def render_group_page(section: Section) -> str:
    return "\n\n".join(
        [
            f"# {section.heading_clean}",
            EMERGENCY_NOTE,
            "## Overview",
            compact_text(section.body, max_chars=2600),
            "## Source",
            f"`raw/hospital_disease.md § {' > '.join(section.path)}`",
        ]
    )


def render_disease_page(section: Section, child_sections: List[Section], title_map: Dict[str, str]) -> str:
    parts = section_body_map_from_children(section, child_sections)
    lines: List[str] = [f"# {section.heading_clean}", "", EMERGENCY_NOTE, ""]
    order = [
        "Overview",
        "Common Symptoms",
        "Risk Factors",
        "Warning Signs",
        "Common Investigations",
        "Commonly Involved Departments",
        "Related or Overlapping Conditions",
        "Typical Hospital Flow",
    ]
    for title in order:
        lines.append(f"## {title}")
        raw = parts.get(title, [])
        if raw:
            for item in bullet_items(raw):
                lines.append(f"- {linkify_term(item, title_map)}")
            if not bullet_items(raw):
                lines.append(compact_text("\n".join(raw), max_chars=1800))
        else:
            lines.append("_Not specified in source section._")
        lines.append("")
    lines.append("## Source")
    lines.append(f"`raw/hospital_disease.md § {' > '.join(section.path)}`")
    return "\n".join(lines).strip()


def render_simple_page(section: Section, title_map: Dict[str, str], heading: str) -> str:
    lines: List[str] = [f"# {section.heading_clean}", "", EMERGENCY_NOTE, "", f"## {heading}", ""]
    summary = top_lines(section.body, count=22)
    lines.append(compact_text(summary, max_chars=2200))
    lines.append("")
    all_items = bullet_items(section.body.splitlines())
    if all_items:
        lines.append("## Linked Concepts")
        for item in all_items:
            lines.append(f"- {linkify_term(item, title_map)}")
        lines.append("")
    lines.append("## Source")
    lines.append(f"`raw/hospital_disease.md § {' > '.join(section.path)}`")
    return "\n".join(lines).strip()


def render_source_section_page(section: Section) -> str:
    excerpt = compact_text(section.body, max_chars=4000)
    return "\n\n".join(
        [
            f"# Source Section: {' > '.join(section.path)}",
            "## Raw Heading",
            f"`{' > '.join(section.path)}`",
            "## Extract",
            excerpt if excerpt else "_No body text in this heading._",
            "## Source",
            f"`raw/hospital_disease.md § {' > '.join(section.path)}`",
        ]
    )


def build_index(concept_pages: Dict[str, List[Tuple[str, str]]]) -> str:
    lines = [
        "# Hospital Disease Wiki — Index",
        "",
        EMERGENCY_NOTE,
        "",
        "## Navigation by Concept Type",
        "",
    ]
    for folder, pages in concept_pages.items():
        lines.append(f"### {folder}")
        for title, rel_path in sorted(pages):
            lines.append(f"- [[{title}]] (`{rel_path}`)")
        lines.append("")
    lines.extend(
        [
            "## Query Workflow",
            "",
            "1. Start from this index.",
            "2. Open directly relevant pages.",
            "3. Follow `[[wikilinks]]` up to 2 hops for related context.",
            "4. Answer using only wiki content, as possible related conditions.",
            "",
            "## Safety Reminder",
            "",
            "Do not diagnose. Do not prescribe treatment. Use urgent-care note when emergency warning signs are discussed.",
        ]
    )
    return "\n".join(lines).strip() + "\n"


def append_log(created_counts: Dict[str, int]) -> None:
    log_path = WIKI_DIR / "log.md"
    ensure_dir(log_path.parent)
    if not log_path.exists():
        log_path.write_text("# Wiki Log\n\n", encoding="utf-8")
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    total = sum(created_counts.values())
    lines = [
        f"### [{ts}] BUILD",
        "",
        f"- Source: `raw/hospital_disease.md`",
        f"- Pages written: {total}",
    ]
    for key, value in sorted(created_counts.items()):
        lines.append(f"- {key}: {value}")
    lines.extend(["", "---", ""])
    with log_path.open("a", encoding="utf-8") as f:
        f.write("\n".join(lines))


def clean_managed_wiki_folders() -> None:
    for folder in MANAGED_FOLDERS:
        folder_path = WIKI_DIR / folder
        if not folder_path.exists():
            continue
        for md_file in folder_path.rglob("*.md"):
            md_file.unlink()


def main() -> None:
    if not RAW_FILE.exists():
        raise FileNotFoundError(f"Missing raw source: {RAW_FILE}")

    raw_text = RAW_FILE.read_text(encoding="utf-8")
    sections = parse_markdown_sections(raw_text)
    title_map = infer_title_alias_map(sections)
    typed = classify_sections(sections)
    clean_managed_wiki_folders()
    children_by_parent: Dict[Tuple[str, ...], List[Section]] = defaultdict(list)
    for sec in sections:
        if sec.level >= 3 and len(sec.path) >= 2:
            parent_key = tuple(sec.path[:-1])
            children_by_parent[parent_key].append(sec)

    concept_pages: Dict[str, List[Tuple[str, str]]] = defaultdict(list)
    created_counts: Dict[str, int] = defaultdict(int)

    source_dir = WIKI_DIR / "source-sections"
    ensure_dir(source_dir)
    for sec in sections:
        source_slug = slugify(" > ".join(sec.path))
        path = source_dir / f"{source_slug}.md"
        write_text(path, render_source_section_page(sec))
        created_counts["source-sections"] += 1
        concept_pages["source-sections"].append((f"Source Section: {' > '.join(sec.path)}", path.relative_to(ROOT).as_posix()))

    renderer_by_type = {
        "groups": lambda s: render_group_page(s),
        "diseases": lambda s: render_disease_page(s, children_by_parent.get(tuple(s.path), []), title_map),
        "symptoms": lambda s: render_simple_page(s, title_map, "Symptom Notes"),
        "warning-signs": lambda s: render_simple_page(s, title_map, "Warning Sign Notes"),
        "investigations": lambda s: render_simple_page(s, title_map, "Investigation Notes"),
        "departments": lambda s: render_simple_page(s, title_map, "Department Notes"),
        "overlaps": lambda s: render_simple_page(s, title_map, "Cross-Disease Reasoning"),
    }

    for folder, sec_list in typed.items():
        folder_dir = WIKI_DIR / folder
        ensure_dir(folder_dir)
        for sec in sec_list:
            slug = slugify(sec.heading_clean)
            out_path = folder_dir / f"{slug}.md"
            rendered = renderer_by_type[folder](sec)
            write_text(out_path, rendered)
            created_counts[folder] += 1
            concept_pages[folder].append((sec.heading_clean, out_path.relative_to(ROOT).as_posix()))

    write_text(WIKI_DIR / "index.md", build_index(concept_pages))
    append_log(created_counts)

    print("Build complete.")
    print(f"Folders created/updated: {', '.join(sorted(concept_pages.keys()))}")
    print(f"Pages created/updated: {sum(created_counts.values())}")
    for key, value in sorted(created_counts.items()):
        print(f"  - {key}: {value}")


if __name__ == "__main__":
    main()
