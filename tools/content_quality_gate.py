#!/usr/bin/env python3
"""RabbitEmergency.com batch quality gate.

Run before marking any content batch done. The checks mirror
CODEX-HOUSE-RULES.md and intentionally fail closed.
"""

from __future__ import annotations

from collections import defaultdict
from html.parser import HTMLParser
from pathlib import Path
import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
BASE = "https://rabbitemergency.com"
LOCALES = ("", "ja", "zh-tw", "th")
REVIEWER_PAGE = "/veterinary-review/"
CANONICAL_GUIDES = {
    "gut": "/rabbit-not-eating-or-pooping/",
    "poisoning": "/rabbit-ate-something-toxic/",
    "breathing": "/rabbit-difficulty-breathing/",
    "urinary": "/rabbit-straining-to-urinate/",
    "injury": "/rabbit-fall-or-trauma/",
    "heat": "/rabbit-collapsed-in-heat/",
}
HUB_SLUGS = {
    "rabbit-gut-stasis-emergency-hub",
    "rabbit-poisoning-emergency-hub",
    "rabbit-breathing-emergency-hub",
    "rabbit-urinary-emergency-hub",
    "rabbit-injury-trauma-emergency-hub",
    "rabbit-emergency-signs",
}
PRODUCT_CONTEXT_RE = re.compile(
    r"\b(product|products|supplement|supplements|rodicare|wooly|recovery support|powder|formula|paste)\b",
    re.I,
)
PRODUCT_CLAIM_RE = re.compile(r"\b(treats?|cures?|heals?)\b", re.I)
GLOBAL_BANNED_RE = re.compile(
    r"\b(guaranteed|replaces?\s+(?:the\s+)?vet(?:erinarian)?|emergency\s+medicine)\b",
    re.I,
)
RED_FLAG_TERMS = (
    "go now",
    "go to a vet now",
    "今すぐ",
    "立即就醫",
    "ไปทันที",
)
TELL_VET_TERMS = (
    "what to tell the vet",
    "獣医へ伝える",
    "告訴獸醫",
    "บอกสัตวแพทย์",
)
STALE_REVIEWER_TERMS = (
    "Dr. Apinya",
    "Dr. Sato",
    "Dr. Lin",
    "Dr. Mei",
    "reviewedBy",
    "lastReviewed",
    "dateReviewed",
    "pending named veterinary review",
    "pending named clinical reviewer",
    "source-cited, pending",
    "named-reviewer",
    "named reviewer",
)


class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []
        self.canonicals: list[str] = []
        self.hreflang: dict[str, str] = {}
        self.robots: list[str] = []
        self.ld_json: list[str] = []
        self.titles: list[str] = []
        self.descriptions: list[str] = []
        self._ld_depth = 0
        self._ld_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        data = {k.lower(): v or "" for k, v in attrs}
        if tag == "a" and data.get("href"):
            self.links.append(data["href"])
        if tag == "link" and data.get("rel") == "canonical":
            self.canonicals.append(data.get("href", ""))
        if tag == "link" and data.get("rel") == "alternate" and data.get("hreflang"):
            self.hreflang[data["hreflang"]] = data.get("href", "")
        if tag == "meta" and data.get("name", "").lower() == "robots":
            self.robots.append(data.get("content", ""))
        if tag == "meta" and data.get("name", "").lower() == "description":
            self.descriptions.append(data.get("content", ""))
        if tag == "script" and data.get("type") == "application/ld+json":
            self._ld_depth = 1
            self._ld_parts = []

    def handle_endtag(self, tag: str) -> None:
        if tag == "script" and self._ld_depth:
            self.ld_json.append("".join(self._ld_parts).strip())
            self._ld_depth = 0

    def handle_data(self, data: str) -> None:
        if self._ld_depth:
            self._ld_parts.append(data)
        elif self.lasttag == "title":
            self.titles.append(data.strip())


def url_for_page(path: Path) -> str:
    rel = path.relative_to(ROOT)
    if rel == Path("index.html"):
        return f"{BASE}/"
    slug = str(rel.parent).strip(".")
    return f"{BASE}/{slug}/"


def local_path_from_url(url: str) -> Path | None:
    if not url.startswith(BASE):
        return None
    suffix = url[len(BASE):].strip("/")
    return ROOT / suffix / "index.html" if suffix else ROOT / "index.html"


def visible_text(html: str) -> str:
    html = re.sub(r"<script\b.*?</script>", " ", html, flags=re.I | re.S)
    html = re.sub(r"<style\b.*?</style>", " ", html, flags=re.I | re.S)
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).strip()


def content_word_count(text: str, path: Path) -> int:
    """Count useful page length across languages.

    Japanese and Traditional Chinese do not use spaces between most words, so a
    whitespace-only word count under-reports localized pages. Count Latin/Thai
    style tokens normally and add a conservative CJK character allowance.
    """
    words = re.findall(r"\b[\w'-]+\b", text)
    rel = path.relative_to(ROOT)
    locale = rel.parts[0] if rel.parts and rel.parts[0] in {"ja", "zh-tw"} else ""
    if locale:
        cjk_chars = re.findall(r"[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff]", text)
        return len(words) + len(cjk_chars) // 2
    return len(words)


def page_kind(path: Path, html: str) -> str:
    slug = path.parent.name
    if slug in HUB_SLUGS:
        return "hub"
    if slug.endswith("-emergency-signs"):
        return "emergency"
    if any(token in slug for token in ("emergency", "bloat", "flystrike", "head-tilt", "not-eating", "watery-diarrhea")):
        return "medical"
    if "MedicalWebPage" in html:
        return "medical"
    return "other"


def issue(issues: dict[str, list[str]], key: str, message: str) -> None:
    issues[key].append(message)


def banned_claim_hits(text: str) -> list[str]:
    hits: list[str] = []
    for match in GLOBAL_BANNED_RE.finditer(text):
        hits.append(match.group(0))
    for sentence in re.split(r"(?<=[.!?])\s+", text):
        if PRODUCT_CONTEXT_RE.search(sentence):
            for match in PRODUCT_CLAIM_RE.finditer(sentence):
                hits.append(match.group(0))
    return hits


def parse_pages() -> dict[Path, tuple[str, LinkParser]]:
    pages: dict[Path, tuple[str, LinkParser]] = {}
    for path in sorted(ROOT.glob("**/index.html")):
        if ".git" in path.parts:
            continue
        html = path.read_text(encoding="utf-8", errors="replace")
        if is_redirect_stub(html):
            continue
        parser = LinkParser()
        parser.feed(html)
        pages[path] = (html, parser)
    return pages


def is_redirect_stub(html: str) -> bool:
    return 'http-equiv="refresh"' in html and "noindex" in html.lower() and len(html) < 2500


def ld_types(obj: object) -> list[str]:
    found: list[str] = []
    if isinstance(obj, list):
        for item in obj:
            found.extend(ld_types(item))
    elif isinstance(obj, dict):
        typ = obj.get("@type")
        if isinstance(typ, str):
            found.append(typ)
        elif isinstance(typ, list):
            found.extend(str(x) for x in typ)
        graph = obj.get("@graph")
        if graph:
            found.extend(ld_types(graph))
    return found


def has_bad_review_metadata(obj: object) -> bool:
    if isinstance(obj, list):
        return any(has_bad_review_metadata(x) for x in obj)
    if isinstance(obj, dict):
        if any(key in obj for key in ("reviewedBy", "lastReviewed", "dateReviewed")):
            return True
        return any(has_bad_review_metadata(v) for v in obj.values())
    return False


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true", help="Emit machine-readable summary.")
    args = parser.parse_args()

    issues: dict[str, list[str]] = defaultdict(list)
    pages = parse_pages()
    urls = {url_for_page(path): path for path in pages}

    sitemap_path = ROOT / "sitemap.xml"
    sitemap_urls: list[str] = []
    if not sitemap_path.exists():
        issue(issues, "sitemap", "missing sitemap.xml")
    else:
        sitemap_text = sitemap_path.read_text(encoding="utf-8", errors="replace")
        try:
            tree = ET.parse(sitemap_path)
            ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
            sitemap_urls = [el.text or "" for el in tree.findall(".//sm:loc", ns)]
        except ET.ParseError as exc:
            issue(issues, "sitemap_xml_invalid", str(exc))
            sitemap_urls = re.findall(r"<loc>(.*?)</loc>", sitemap_text)
        missing = sorted(url for url in sitemap_urls if local_path_from_url(url) not in pages)
        extra = sorted(url for url in urls if url not in sitemap_urls)
        if len(sitemap_urls) != len(pages):
            issue(issues, "sitemap", f"sitemap count {len(sitemap_urls)} != live page count {len(pages)}")
        for url in missing[:50]:
            issue(issues, "sitemap_missing_disk", url)
        for url in extra[:50]:
            issue(issues, "sitemap_missing_url", url)

    title_seen: dict[str, Path] = {}
    meta_seen: dict[str, Path] = {}
    inbound: dict[str, set[str]] = defaultdict(set)

    for path, (html, parsed) in pages.items():
        url = url_for_page(path)
        text = visible_text(html)
        kind = page_kind(path, html)

        if any("noindex" in robots.lower() for robots in parsed.robots):
            issue(issues, "noindex", str(path.relative_to(ROOT)))

        if parsed.canonicals != [url]:
            issue(issues, "canonical", f"{path.relative_to(ROOT)} canonical={parsed.canonicals!r}, expected {url}")

        title = parsed.titles[0] if parsed.titles else ""
        desc = parsed.descriptions[0] if parsed.descriptions else ""
        if not title:
            issue(issues, "title", f"{path.relative_to(ROOT)} missing title")
        elif title in title_seen:
            issue(issues, "title_duplicate", f"{path.relative_to(ROOT)} duplicates {title_seen[title].relative_to(ROOT)}: {title}")
        else:
            title_seen[title] = path
        if not desc:
            issue(issues, "meta", f"{path.relative_to(ROOT)} missing meta description")
        elif desc in meta_seen:
            issue(issues, "meta_duplicate", f"{path.relative_to(ROOT)} duplicates {meta_seen[desc].relative_to(ROOT)}")
        else:
            meta_seen[desc] = path

        for hit in banned_claim_hits(text):
            issue(issues, "banned_claim_terms", f"{path.relative_to(ROOT)}: {hit!r}")

        ld_objects: list[object] = []
        for block in parsed.ld_json:
            try:
                ld_objects.append(json.loads(block))
            except json.JSONDecodeError as exc:
                issue(issues, "invalid_json_ld", f"{path.relative_to(ROOT)}: {exc}")
        types = [typ for obj in ld_objects for typ in ld_types(obj)]

        if kind in {"medical", "emergency", "hub"}:
            for required in ("MedicalWebPage", "FAQPage", "BreadcrumbList"):
                if required not in types:
                    issue(issues, "schema_missing", f"{path.relative_to(ROOT)} missing {required}")
            lower_text = text.lower()
            if any(has_bad_review_metadata(obj) for obj in ld_objects):
                issue(issues, "review_metadata_banned", str(path.relative_to(ROOT)))
            for term in STALE_REVIEWER_TERMS:
                if term.lower() in lower_text or term in html:
                    issue(issues, "stale_reviewer_claim", f"{path.relative_to(ROOT)} contains {term!r}")
            if kind == "emergency":
                if not any(term.lower() in lower_text for term in RED_FLAG_TERMS):
                    issue(issues, "red_flag_missing", str(path.relative_to(ROOT)))
                words = content_word_count(text, path)
                if words < 600:
                    issue(issues, "thin_emergency_page", f"{path.relative_to(ROOT)}: {words} words")
                if not any(term.lower() in lower_text for term in TELL_VET_TERMS):
                    issue(issues, "tell_vet_missing", str(path.relative_to(ROOT)))

        if "Organization" in types and "sameAs" in html:
            pass

        for href in parsed.links:
            if not href.startswith("/") or href.startswith("//"):
                continue
            target = href.split("#", 1)[0].split("?", 1)[0]
            if not target:
                continue
            target_url = f"{BASE}{target if target.endswith('/') else target + '/'}"
            inbound[target_url].add(url)

        if parsed.hreflang:
            expected_default = f"{BASE}/{path.relative_to(ROOT).parent}/".replace("/./", "/")
            if path == ROOT / "index.html":
                expected_default = f"{BASE}/"
            if parsed.hreflang.get("x-default") is None:
                issue(issues, "hreflang", f"{path.relative_to(ROOT)} missing x-default")
            for lang, alt_url in parsed.hreflang.items():
                alt_path = local_path_from_url(alt_url)
                if alt_path and alt_path in pages:
                    alt_html, alt_parsed = pages[alt_path]
                    if url not in alt_parsed.hreflang.values() and url != alt_url:
                        issue(issues, "hreflang_reciprocal", f"{path.relative_to(ROOT)} -> {alt_path.relative_to(ROOT)} is not reciprocal")

    for url, path in urls.items():
        if url == f"{BASE}/":
            continue
        if not inbound.get(url):
            issue(issues, "orphans", str(path.relative_to(ROOT)))

    summary = {
        "pages": len(pages),
        "sitemap_urls": len(sitemap_urls),
        "invalid_json_ld": len(issues.get("invalid_json_ld", [])),
        "orphans": len(issues.get("orphans", [])),
        "banned_claim_terms": len(issues.get("banned_claim_terms", [])),
        "issue_counts": {k: len(v) for k, v in sorted(issues.items())},
    }

    if args.json:
        print(json.dumps({"summary": summary, "issues": issues}, indent=2, ensure_ascii=False))
    else:
        print("RabbitEmergency.com content quality gate")
        for key, value in summary.items():
            print(f"{key}: {value}")
        if issues:
            print("\nFailures:")
            for key in sorted(issues):
                print(f"- {key}: {len(issues[key])}")
                for item in issues[key][:10]:
                    print(f"  {item}")
                if len(issues[key]) > 10:
                    print(f"  ... {len(issues[key]) - 10} more")

    return 1 if issues else 0


if __name__ == "__main__":
    sys.exit(main())
