#!/usr/bin/env python3
"""Publish Priority 50 SEO/LLM answer-source improvements from Markdown.

Usage:
  python3 tools/publish_priority50_improvements.py --batch 1 --batch-size 20
  python3 tools/publish_priority50_improvements.py --start 21 --limit 20
  python3 tools/publish_priority50_improvements.py --dry-run --batch 1

The Markdown manifest is the source of truth. The publisher only updates live
HTML owner pages, skips retired redirect stubs, keeps self-canonicals/hreflang
untouched, and sanitizes review-policy artifacts before writing.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import date
from html import escape
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET

from bs4 import BeautifulSoup, Tag

try:
    from html_sanitizer import sanitize_html
except ImportError:  # Allows importing as tools.publish_priority50_improvements.
    from tools.html_sanitizer import sanitize_html


ROOT = Path(__file__).resolve().parents[1]
BASE = "https://rabbitemergency.com"
MANIFEST = ROOT / "content" / "priority50-improvements.md"
REDIRECT_MANIFEST = ROOT / "tools" / "redirect_manifest.json"
TODAY = date.today().isoformat()
SCHEMA_TYPES = {"MedicalWebPage", "FAQPage", "BreadcrumbList"}
ROUTE_TARGETS = {
    "rabbit-not-eating": "rabbit-not-eating-or-pooping",
}
CLINIC_GROUP_PAGES = (
    "rabbit-emergency-vet-hong-kong",
    "rabbit-emergency-vet-bangkok",
    "rabbit-emergency-vet-taipei",
    "rabbit-emergency-vet-tokyo",
    "rabbit-emergency-vet-singapore",
)


@dataclass(frozen=True)
class Entry:
    priority: int
    slug: str
    hub: str
    cluster: str
    intent: str
    go_now: list[str]
    call_today: list[str]
    do_not: list[str]
    tell_vet: list[str]
    nuance: list[str]
    vet_checks: list[str]
    source_label: str
    source_url: str
    source_note: str
    siblings: list[str]
    faq: list[tuple[str, str]]

    @property
    def page_path(self) -> Path:
        return ROOT / self.slug / "index.html"


def split_table_row(line: str) -> list[str]:
    line = line.strip()
    if not line.startswith("|") or not line.endswith("|"):
        return []
    return [cell.strip() for cell in line.strip("|").split("|")]


def split_items(value: str) -> list[str]:
    return [item.strip() for item in value.split(";") if item.strip()]


def split_slugs(value: str) -> list[str]:
    return [item.strip().strip("/") for item in value.split(",") if item.strip()]


def split_faq(value: str) -> list[tuple[str, str]]:
    pairs: list[tuple[str, str]] = []
    for item in split_items(value):
        if "=>" not in item:
            continue
        q, a = item.split("=>", 1)
        pairs.append((q.strip(), a.strip()))
    return pairs


def parse_manifest(path: Path = MANIFEST) -> list[Entry]:
    rows: list[dict[str, str]] = []
    headers: list[str] | None = None
    for line in path.read_text(encoding="utf-8").splitlines():
        cells = split_table_row(line)
        if not cells:
            continue
        if cells[0] == "---:":
            continue
        if cells[0] == "#":
            headers = cells
            continue
        if headers and len(cells) == len(headers):
            rows.append(dict(zip(headers, cells)))
    entries: list[Entry] = []
    for row in rows:
        entries.append(
            Entry(
                priority=int(row["#"]),
                slug=row["slug"],
                hub=row["hub"],
                cluster=row["cluster"],
                intent=row["intent"],
                go_now=split_items(row["go_now"]),
                call_today=split_items(row["call_today"]),
                do_not=split_items(row["do_not"]),
                tell_vet=split_items(row["tell_vet"]),
                nuance=split_items(row["nuance"]),
                vet_checks=split_items(row["vet_checks"]),
                source_label=row["source_label"],
                source_url=row["source_url"],
                source_note=row["source_note"],
                siblings=split_slugs(row["siblings"]),
                faq=split_faq(row["faq"]),
            )
        )
    if len(entries) < 50:
        raise SystemExit(f"manifest parsed {len(entries)} entries, expected 50")
    return entries


def retired_slugs() -> set[str]:
    if not REDIRECT_MANIFEST.exists():
        return set()
    data = json.loads(REDIRECT_MANIFEST.read_text(encoding="utf-8"))
    return set(data)


def is_redirect_stub(path: Path) -> bool:
    if not path.exists():
        return False
    html = path.read_text(encoding="utf-8", errors="replace")
    return 'http-equiv="refresh"' in html and "noindex" in html.lower() and len(html) < 2500


def ensure_meta_last_updated(soup: BeautifulSoup) -> None:
    head = soup.head
    if head is None:
        return
    meta = head.find("meta", attrs={"name": "last-updated"})
    if meta is None:
        meta = soup.new_tag("meta")
        meta["name"] = "last-updated"
        head.append(meta)
    meta["content"] = TODAY


def list_html(items: list[str]) -> str:
    return "".join(f"<li>{escape(item)}</li>" for item in items)


def related_links(entry: Entry) -> str:
    seen: set[str] = set()
    links: list[str] = []
    for slug in [entry.hub, *entry.siblings]:
        if not slug or slug == entry.slug or slug in seen:
            continue
        if not (ROOT / slug / "index.html").exists() or is_redirect_stub(ROOT / slug / "index.html"):
            continue
        seen.add(slug)
        label = slug.replace("-", " ").replace("rabbit ", "Rabbit ")
        links.append(f'<a href="/{escape(slug)}/">{escape(label)}</a>')
    return "".join(links)


def answer_source_block(entry: Entry) -> str:
    go_now = "; ".join(entry.go_now[:3])
    call_today = "; ".join(entry.call_today[:2])
    do_not = "; ".join(entry.do_not[:3])
    tell_vet = "; ".join(entry.tell_vet[:4])
    return f"""
<section class="card" id="answer-source-block">
<h2>Fast answer for owners</h2>
<ul>
<li><strong>Go now if:</strong> {escape(go_now)}</li>
<li><strong>Call today if:</strong> {escape(call_today)}</li>
<li><strong>Do not:</strong> {escape(do_not)}</li>
<li><strong>Tell the vet:</strong> {escape(tell_vet)}</li>
</ul>
</section>"""


def priority_depth_block(entry: Entry) -> str:
    faq_html = "".join(
        f"<details><summary>{escape(q)}</summary><p>{escape(a)}</p></details>"
        for q, a in entry.faq[:3]
    )
    links = related_links(entry)
    related = (
        f'<section id="priority-related-links"><h2>Related pages in this emergency cluster</h2><div class="related">{links}</div></section>'
        if links
        else ""
    )
    return f"""
<section id="priority-depth-block">
<h2>What changes urgency for this page</h2>
<div class="card"><ul>{list_html(entry.nuance)}</ul></div>
<h2>What the vet is trying to rule out</h2>
<div class="card"><ul>{list_html(entry.vet_checks)}</ul></div>
<h2>Source-tied safety note</h2>
<p><a href="{escape(entry.source_url)}" rel="noreferrer" target="_blank">{escape(entry.source_label)}</a>: {escape(entry.source_note)}</p>
<section id="priority-owner-faq"><h2>Page-specific owner FAQ</h2>{faq_html}</section>
{related}
</section>"""


def remove_existing_block(soup: BeautifulSoup, block_id: str) -> None:
    existing = soup.find(id=block_id)
    if existing is not None:
        existing.decompose()


def insert_after_answer(soup: BeautifulSoup, html: str) -> None:
    fragment = BeautifulSoup(html, "html.parser")
    anchor = soup.find("div", class_="answer") or soup.find("h1")
    if anchor is None:
        main = soup.find("main")
        if isinstance(main, Tag):
            main.insert(0, fragment)
        return
    anchor.insert_after(fragment)


def insert_before_sources(soup: BeautifulSoup, html: str) -> None:
    fragment = BeautifulSoup(html, "html.parser")
    target = soup.find(id="sources")
    if target is None:
        for heading in soup.find_all(["h2", "h3"]):
            if "sources" in heading.get_text(" ", strip=True).lower():
                target = heading
                break
    if target is None:
        reviewed = soup.find("p", class_="reviewed")
        target = reviewed if isinstance(reviewed, Tag) else None
    if target is None:
        main = soup.find("main")
        if isinstance(main, Tag):
            main.append(fragment)
        return
    target.insert_before(fragment)


def schema_type(data: object) -> set[str]:
    found: set[str] = set()
    if isinstance(data, dict):
        t = data.get("@type")
        if isinstance(t, str):
            found.add(t)
        elif isinstance(t, list):
            found.update(str(x) for x in t)
        for value in data.values():
            found.update(schema_type(value))
    elif isinstance(data, list):
        for value in data:
            found.update(schema_type(value))
    return found


def jsonld_scripts(soup: BeautifulSoup) -> list[tuple[Tag, object]]:
    scripts: list[tuple[Tag, object]] = []
    for script in soup.find_all("script", type="application/ld+json"):
        raw = script.string or script.get_text() or ""
        try:
            scripts.append((script, json.loads(raw)))
        except json.JSONDecodeError:
            continue
    return scripts


def update_jsonld(soup: BeautifulSoup, entry: Entry) -> None:
    for script, data in jsonld_scripts(soup):
        types = schema_type(data)
        if "MedicalWebPage" in types and isinstance(data, dict):
            data["dateModified"] = TODAY
            citation = data.get("citation")
            citations = citation if isinstance(citation, list) else ([citation] if isinstance(citation, dict) else [])
            new_citation = {"@type": "CreativeWork", "name": entry.source_label, "url": entry.source_url}
            if not any(isinstance(item, dict) and item.get("url") == entry.source_url for item in citations):
                citations.append(new_citation)
            data["citation"] = citations
            script.string = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
        if "FAQPage" in types and isinstance(data, dict):
            entities = data.get("mainEntity")
            if not isinstance(entities, list):
                entities = []
            existing_questions = {
                item.get("name")
                for item in entities
                if isinstance(item, dict)
            }
            for question, answer in entry.faq:
                if question in existing_questions:
                    continue
                entities.append(
                    {
                        "@type": "Question",
                        "name": question,
                        "acceptedAnswer": {"@type": "Answer", "text": answer},
                    }
                )
            data["mainEntity"] = entities
            data["dateModified"] = TODAY
            script.string = json.dumps(data, ensure_ascii=False, separators=(",", ":"))


def validate_required_schema(soup: BeautifulSoup, slug: str) -> list[str]:
    found: set[str] = set()
    for _, data in jsonld_scripts(soup):
        found.update(schema_type(data))
    return [f"{slug} missing {schema}" for schema in sorted(SCHEMA_TYPES - found)]


def update_page(entry: Entry, dry_run: bool = False) -> tuple[bool, list[str]]:
    if entry.slug in ROUTE_TARGETS:
        return update_route_stub(entry, dry_run=dry_run)
    if entry.slug == "rabbit-clinic-directory-pages":
        return update_clinic_group(entry, dry_run=dry_run)

    path = entry.page_path
    warnings: list[str] = []
    if not path.exists():
        return False, [f"{entry.slug}: missing live page"]
    if entry.slug in retired_slugs() or is_redirect_stub(path):
        return False, [f"{entry.slug}: skipped retired redirect stub"]

    original = path.read_text(encoding="utf-8")
    soup = BeautifulSoup(original, "html.parser")
    remove_existing_block(soup, "answer-source-block")
    remove_existing_block(soup, "priority-depth-block")
    remove_existing_block(soup, "priority-owner-faq")
    remove_existing_block(soup, "priority-related-links")
    insert_after_answer(soup, answer_source_block(entry))
    insert_before_sources(soup, priority_depth_block(entry))
    ensure_meta_last_updated(soup)
    update_jsonld(soup, entry)
    warnings.extend(validate_required_schema(soup, entry.slug))

    html = sanitize_html(str(soup), path)
    changed = html != original
    if changed and not dry_run:
        path.write_text(html, encoding="utf-8")
    return changed, warnings


def redirect_stub_html(slug: str, target_slug: str) -> str:
    target = f"/{target_slug}/"
    target_abs = f"{BASE}/{target_slug}/"
    title = slug.replace("-", " ").title()
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="robots" content="noindex, follow">
<meta http-equiv="refresh" content="0; url={target}">
<link rel="canonical" href="{target_abs}">
<title>{escape(title)} | RabbitEmergency.com</title>
</head>
<body>
<p>This page has moved to <a href="{target}">{escape(target_abs)}</a>.</p>
</body>
</html>
"""


def update_route_stub(entry: Entry, dry_run: bool = False) -> tuple[bool, list[str]]:
    target_slug = ROUTE_TARGETS[entry.slug]
    target_path = ROOT / target_slug / "index.html"
    if not target_path.exists():
        return False, [f"{entry.slug}: route target missing: {target_slug}"]
    out = entry.page_path
    desired = redirect_stub_html(entry.slug, target_slug)
    original = out.read_text(encoding="utf-8") if out.exists() else ""
    changed = desired != original
    if changed and not dry_run:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(desired, encoding="utf-8")
    return changed, []


def clinic_quality_block(entry: Entry, slug: str) -> str:
    city_label = slug.replace("rabbit-emergency-vet-", "").replace("-", " ").title()
    return f"""
<section class="card" id="clinic-directory-quality-block">
<h2>Before travelling to a {escape(city_label)} clinic</h2>
<ul>
<li><strong>Call first:</strong> {escape(entry.do_not[0])}</li>
<li><strong>Confirm:</strong> emergency hours, rabbit/exotic capability, current vet availability, address, and whether oxygen or urgent stabilization is available.</li>
<li><strong>Tell the clinic:</strong> {escape('; '.join(entry.tell_vet[:4]))}</li>
<li><strong>Verification standard:</strong> each listing should keep a source link, visible caveat, last-verified date, and correction route.</li>
</ul>
<p><a href="{escape(entry.source_url)}" rel="noreferrer" target="_blank">{escape(entry.source_label)}</a>: {escape(entry.source_note)}</p>
</section>"""


def update_clinic_group(entry: Entry, dry_run: bool = False) -> tuple[bool, list[str]]:
    changed_any = False
    warnings: list[str] = []
    for slug in CLINIC_GROUP_PAGES:
        path = ROOT / slug / "index.html"
        if not path.exists():
            warnings.append(f"{slug}: missing clinic page")
            continue
        original = path.read_text(encoding="utf-8")
        soup = BeautifulSoup(original, "html.parser")
        remove_existing_block(soup, "clinic-directory-quality-block")
        insert_before_sources(soup, clinic_quality_block(entry, slug))
        ensure_meta_last_updated(soup)
        for script, data in jsonld_scripts(soup):
            if isinstance(data, dict) and any(t in schema_type(data) for t in {"WebPage", "ItemList", "VeterinaryCare"}):
                data["dateModified"] = TODAY
                script.string = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
        html = sanitize_html(str(soup), path)
        changed = html != original
        changed_any = changed_any or changed
        if changed and not dry_run:
            path.write_text(html, encoding="utf-8")
    return changed_any, warnings


def update_sitemap(dry_run: bool = False) -> int:
    sitemap = ROOT / "sitemap.xml"
    if not sitemap.exists():
        return 0
    tree = ET.parse(sitemap)
    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    count = 0
    for url in tree.findall(".//sm:url", ns):
        lastmod = url.find("sm:lastmod", ns)
        if lastmod is not None:
            lastmod.text = TODAY
        count += 1
    if not dry_run:
        ET.register_namespace("", "http://www.sitemaps.org/schemas/sitemap/0.9")
        tree.write(sitemap, encoding="utf-8", xml_declaration=True)
    return count


def selected_entries(entries: list[Entry], args: argparse.Namespace) -> list[Entry]:
    if args.batch is not None:
        start = ((args.batch - 1) * args.batch_size) + 1
        end = start + args.batch_size - 1
    else:
        start = args.start
        end = args.start + args.limit - 1
    return [entry for entry in entries if start <= entry.priority <= end]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=MANIFEST)
    parser.add_argument("--batch", type=int)
    parser.add_argument("--batch-size", type=int, default=20)
    parser.add_argument("--start", type=int, default=1)
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    entries = parse_manifest(args.manifest)
    chosen = selected_entries(entries, args)
    if not chosen:
        raise SystemExit("no entries selected")

    changed: list[str] = []
    warnings: list[str] = []
    for entry in chosen:
        did_change, entry_warnings = update_page(entry, dry_run=args.dry_run)
        if did_change:
            changed.append(entry.slug)
        warnings.extend(entry_warnings)

    sitemap_count = update_sitemap(dry_run=args.dry_run)
    mode = "dry run" if args.dry_run else "published"
    print(f"priority50 improvements {mode}: selected {len(chosen)}, changed {len(changed)}, sitemap URLs {sitemap_count}")
    for slug in changed:
        print(f"changed: {slug}")
    for warning in warnings:
        print(f"warning: {warning}")
    return 0 if not warnings else 1


if __name__ == "__main__":
    raise SystemExit(main())
