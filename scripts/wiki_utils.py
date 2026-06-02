from __future__ import annotations

from dataclasses import dataclass, field
import re
from pathlib import Path
from typing import Dict, Iterable, List, Set


WIKILINK_RE = re.compile(r"\[\[([^\]|#]+?)(?:\|[^\]]+)?\]\]")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$", re.MULTILINE)


@dataclass
class Section:
    level: int
    heading_raw: str
    heading_clean: str
    body: str
    path: List[str] = field(default_factory=list)


def slugify(text: str) -> str:
    value = text.strip().lower()
    value = re.sub(r"[^\w\s-]", "", value)
    value = re.sub(r"[\s/]+", "-", value)
    value = re.sub(r"-{2,}", "-", value)
    return value.strip("-")


def clean_heading(heading: str) -> str:
    value = heading.strip()
    value = re.sub(r"^\d+(?:\.\d+)*\.\s*", "", value)
    return value.strip()


def parse_markdown_sections(text: str) -> List[Section]:
    matches = list(HEADING_RE.finditer(text))
    sections: List[Section] = []
    stack: List[str] = []
    stack_levels: List[int] = []

    for idx, match in enumerate(matches):
        level = len(match.group(1))
        heading_raw = match.group(2).strip()
        heading_clean = clean_heading(heading_raw)
        start = match.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
        body = text[start:end].strip()

        while stack_levels and stack_levels[-1] >= level:
            stack_levels.pop()
            stack.pop()

        stack_levels.append(level)
        stack.append(heading_clean)

        sections.append(
            Section(
                level=level,
                heading_raw=heading_raw,
                heading_clean=heading_clean,
                body=body,
                path=stack.copy(),
            )
        )
    return sections


def extract_wikilinks(text: str) -> List[str]:
    return [m.group(1).strip() for m in WIKILINK_RE.finditer(text)]


def load_markdown_pages(root: Path) -> Dict[str, str]:
    pages: Dict[str, str] = {}
    for path in sorted(root.rglob("*.md")):
        rel = path.relative_to(root).as_posix()
        pages[rel] = path.read_text(encoding="utf-8")
    return pages


def wikilink_title_to_slug(link_title: str) -> str:
    return slugify(link_title)


def title_from_markdown(markdown_text: str, fallback: str) -> str:
    for line in markdown_text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return fallback


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def write_text(path: Path, content: str) -> None:
    ensure_dir(path.parent)
    path.write_text(content.strip() + "\n", encoding="utf-8")


def to_title(path: str, content: str) -> str:
    fallback = Path(path).stem.replace("-", " ").title()
    return title_from_markdown(content, fallback)


def incoming_link_count(pages: Dict[str, str], title_targets: Set[str]) -> int:
    count = 0
    for content in pages.values():
        for link in extract_wikilinks(content):
            if link in title_targets:
                count += 1
    return count


def compact_text(text: str, max_chars: int = 1200) -> str:
    s = re.sub(r"\n{3,}", "\n\n", text).strip()
    if len(s) <= max_chars:
        return s
    return s[: max_chars - 3].rstrip() + "..."


def top_lines(text: str, count: int = 10) -> str:
    lines = [ln.rstrip() for ln in text.strip().splitlines() if ln.strip()]
    return "\n".join(lines[:count])


def tokenize(text: str) -> List[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


def token_set(text: str) -> Set[str]:
    return set(tokenize(text))


def jaccard(a: Iterable[str], b: Iterable[str]) -> float:
    sa, sb = set(a), set(b)
    if not sa or not sb:
        return 0.0
    inter = sa.intersection(sb)
    union = sa.union(sb)
    return len(inter) / len(union)
