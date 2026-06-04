#!/usr/bin/env python3
"""Shared HTML policy sanitizer for RabbitEmergency.com.

Keeps generator/localizer output aligned with the current review policy:
source-cited guidance only, no named reviewer claims until real reviewers are
approved and documented.
"""

from __future__ import annotations

from pathlib import Path
import json
import re

from bs4 import BeautifulSoup, Doctype
from bs4.element import NavigableString, Tag


ROOT = Path(__file__).resolve().parents[1]
BAD_SCHEMA_KEYS = {"reviewedBy", "lastReviewed", "dateReviewed"}
BAD_TEXT_PATTERNS = (
    "pending named veterinary review",
    "pending named clinical reviewer",
    "source-cited, pending",
    "named-reviewer",
    "named reviewer",
)
REVIEW_TEXT = {
    "en": "Source-cited guidance; veterinary review pending.",
    "ja": "出典に基づくガイダンス。獣医師レビューは準備中です。",
    "zh-tw": "有來源引用的指引；獸醫審閱待定。",
    "th": "คำแนะนำอ้างอิงแหล่งข้อมูล; การตรวจทานโดยสัตวแพทย์อยู่ระหว่างดำเนินการ",
}


def locale_for_path(path: Path | None) -> str:
    if path is None:
        return "en"
    try:
        rel = path.resolve().relative_to(ROOT)
    except ValueError:
        return "en"
    if rel.parts and rel.parts[0] in {"ja", "zh-tw", "th"}:
        return rel.parts[0]
    return "en"


def normalize_review_text(text: str) -> str:
    replacements = {
        "source-cited and pending named veterinary review": "source-cited; veterinary review pending",
        "source-cited, pending named veterinary review": "source-cited; veterinary review pending",
        "pending named veterinary review": "veterinary review pending",
        "pending named clinical reviewer publication": "veterinary review pending",
        "pending named clinical reviewer": "veterinary review pending",
        "named-reviewer": "source-cited",
        "named reviewer": "source-cited",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


def scrub_review_schema(obj: object) -> object:
    if isinstance(obj, list):
        return [scrub_review_schema(item) for item in obj]
    if isinstance(obj, dict):
        return {
            key: scrub_review_schema(normalize_review_text(value) if isinstance(value, str) else value)
            for key, value in obj.items()
            if key not in BAD_SCHEMA_KEYS
        }
    if isinstance(obj, str):
        return normalize_review_text(obj)
    return obj


def _ensure_doctype(html: str) -> str:
    html = re.sub(r"^\s*<!DOCTYPE html>\s*html\s*(?=<html\b)", "<!DOCTYPE html>\n", html, flags=re.I)
    html = re.sub(r"^\s*html\s*(?=<html\b)", "", html, flags=re.I)
    if not html.lstrip().lower().startswith("<!doctype html>"):
        html = "<!DOCTYPE html>\n" + html.lstrip()
    return html


def _remove_review_status_headings(soup: BeautifulSoup) -> None:
    for heading in list(soup.find_all(["h2", "h3"])):
        if heading.get_text(" ", strip=True).lower() != "review status":
            continue
        sibling = heading.find_next_sibling()
        if isinstance(sibling, Tag) and sibling.name == "p" and "reviewed" in (sibling.get("class") or []):
            sibling.decompose()
        heading.decompose()


def _remove_literal_html_nodes(soup: BeautifulSoup) -> None:
    for node in list(soup.find_all(string=True)):
        if isinstance(node, Doctype):
            continue
        if isinstance(node, NavigableString) and node.strip().lower() == "html":
            node.extract()


def _scrub_json_ld(soup: BeautifulSoup) -> None:
    for script in soup.find_all("script", type="application/ld+json"):
        raw = script.string or script.get_text() or ""
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            continue
        data = scrub_review_schema(data)
        script.string = json.dumps(data, ensure_ascii=False, separators=(",", ":"))


def _normalize_visible_review_copy(soup: BeautifulSoup, locale: str) -> None:
    for node in soup.find_all("p", class_="reviewed"):
        text = node.get_text(" ", strip=True).lower()
        if any(token in text for token in ("review", "source-cited", "source cited", "pending", "審閱", "レビュー", "ตรวจทาน")):
            node.string = REVIEW_TEXT[locale]
    for node in soup.find_all(["p", "div"], string=True):
        if isinstance(node.string, NavigableString):
            clean = normalize_review_text(str(node.string))
            if clean != str(node.string):
                node.string.replace_with(clean)


def sanitize_html(html: str, path: Path | None = None) -> str:
    """Return policy-clean HTML.

    Safe to call on generated full pages. Redirect stubs are intentionally left
    mostly untouched except for the accidental literal ``html`` line fix.
    """
    path = Path(path) if path is not None else None
    html = _ensure_doctype(html)
    if 'http-equiv="refresh"' in html and "noindex" in html.lower() and len(html) < 2500:
        return html

    soup = BeautifulSoup(html, "html.parser")
    _remove_literal_html_nodes(soup)
    _remove_review_status_headings(soup)
    _scrub_json_ld(soup)
    _normalize_visible_review_copy(soup, locale_for_path(path))
    cleaned = _ensure_doctype(str(soup))

    if path is not None:
        try:
            rel = path.resolve().relative_to(ROOT)
        except ValueError:
            rel = None
        if rel is not None and rel.parts in {("ja", "index.html"), ("zh-tw", "index.html"), ("th", "index.html")}:
            cleaned = cleaned.replace('src="assets/', 'src="/assets/')
            cleaned = cleaned.replace("src='assets/", "src='/assets/")

    return cleaned


def policy_violations_for_html(html: str) -> list[str]:
    violations: list[str] = []
    lines = html.splitlines()
    if len(lines) > 1 and lines[1].strip().lower() == "html":
        violations.append("literal html line after doctype")
    if re.search(r"<h[23][^>]*>\s*Review status\s*</h[23]>", html, flags=re.I):
        violations.append("visible Review status heading")
    for key in BAD_SCHEMA_KEYS:
        if f'"{key}"' in html or key in html:
            violations.append(f"banned review schema key: {key}")
    lower = html.lower()
    for phrase in BAD_TEXT_PATTERNS:
        if phrase in lower:
            violations.append(f"banned review phrase: {phrase}")
    return violations


def find_policy_violations(root: Path = ROOT) -> list[str]:
    problems: list[str] = []
    for path in sorted(root.glob("**/*.html")):
        if ".git" in path.parts:
            continue
        html = path.read_text(encoding="utf-8", errors="replace")
        for violation in policy_violations_for_html(html):
            problems.append(f"{path.relative_to(root)}: {violation}")
    return problems
