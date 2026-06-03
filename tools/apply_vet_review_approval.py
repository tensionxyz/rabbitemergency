#!/usr/bin/env python3
"""Apply approved veterinary review metadata across RabbitEmergency.com."""

from __future__ import annotations

from html import escape
from html import unescape
from pathlib import Path
import json
import re

from content_quality_gate import ROOT, BASE, page_kind, visible_text


LAST_REVIEWED = "2026-06-03"

REVIEWERS = [
    {
        "@type": "Person",
        "name": "Dr. Srisai",
        "jobTitle": "Veterinary reviewer",
        "affiliation": {"@type": "Organization", "name": "RabbitEmergency.com Veterinary Review Board"},
        "url": f"{BASE}/veterinary-reviewers/#srisai",
        "description": "Reviews rabbit emergency triage guidance for clinical safety, escalation thresholds, and claim discipline.",
    },
    {
        "@type": "Person",
        "name": "Dr. Watanabe",
        "jobTitle": "Veterinary reviewer",
        "affiliation": {"@type": "Organization", "name": "RabbitEmergency.com Veterinary Review Board"},
        "url": f"{BASE}/veterinary-reviewers/#watanabe",
        "description": "Reviews rabbit emergency triage guidance for clinical safety, escalation thresholds, and claim discipline.",
    },
    {
        "@type": "Person",
        "name": "Dr. Lim",
        "jobTitle": "Veterinary reviewer",
        "affiliation": {"@type": "Organization", "name": "RabbitEmergency.com Veterinary Review Board"},
        "url": f"{BASE}/veterinary-reviewers/#lim",
        "description": "Reviews rabbit emergency triage guidance for clinical safety, escalation thresholds, and claim discipline.",
    },
    {
        "@type": "Person",
        "name": "Dr. Hsu",
        "jobTitle": "Veterinary reviewer",
        "affiliation": {"@type": "Organization", "name": "RabbitEmergency.com Veterinary Review Board"},
        "url": f"{BASE}/veterinary-reviewers/#hsu",
        "description": "Reviews rabbit emergency triage guidance for clinical safety, escalation thresholds, and claim discipline.",
    },
]

VISIBLE_REVIEW = (
    'Reviewed by <a href="/veterinary-reviewers/">RabbitEmergency.com Veterinary Review Board</a> '
    f'(Dr. Srisai, Dr. Watanabe, Dr. Lim, Dr. Hsu). Last reviewed: {LAST_REVIEWED}.'
)

LOCAL_REVIEW = {
    "en": VISIBLE_REVIEW,
    "ja": (
        'Reviewed by <a href="/veterinary-reviewers/">RabbitEmergency.com Veterinary Review Board</a> '
        f'(Dr. Srisai, Dr. Watanabe, Dr. Lim, Dr. Hsu). Last reviewed: {LAST_REVIEWED}.'
    ),
    "zh-tw": (
        'Reviewed by <a href="/veterinary-reviewers/">RabbitEmergency.com Veterinary Review Board</a> '
        f'(Dr. Srisai, Dr. Watanabe, Dr. Lim, Dr. Hsu). Last reviewed: {LAST_REVIEWED}.'
    ),
    "th": (
        'Reviewed by <a href="/veterinary-reviewers/">RabbitEmergency.com Veterinary Review Board</a> '
        f'(Dr. Srisai, Dr. Watanabe, Dr. Lim, Dr. Hsu). Last reviewed: {LAST_REVIEWED}.'
    ),
}

LOCALE_PREFIXES = {"en": "", "ja": "ja", "zh-tw": "zh-tw", "th": "th"}
LOCALE_HREFLANG = {"en": "en", "ja": "ja", "zh-tw": "zh-Hant", "th": "th"}


def page_locale(path: Path) -> str:
    rel = path.relative_to(ROOT)
    first = rel.parts[0] if rel.parts else ""
    return first if first in {"ja", "zh-tw", "th"} else "en"


def local_path(slug: str, locale: str = "en") -> str:
    prefix = LOCALE_PREFIXES[locale]
    if prefix:
        return f"/{prefix}/{slug}/"
    return f"/{slug}/"


def local_url(slug: str, locale: str = "en") -> str:
    return f"{BASE}{local_path(slug, locale)}"


def has_type(obj: dict, type_name: str) -> bool:
    typ = obj.get("@type")
    if isinstance(typ, str):
        return typ == type_name
    if isinstance(typ, list):
        return type_name in typ
    return False


def update_ld_object(obj):
    if isinstance(obj, list):
        return [update_ld_object(item) for item in obj]
    if isinstance(obj, dict):
        obj = {k: update_ld_object(v) for k, v in obj.items()}
        if has_type(obj, "MedicalWebPage"):
            obj["reviewedBy"] = REVIEWERS
            obj["lastReviewed"] = LAST_REVIEWED
            obj["dateReviewed"] = LAST_REVIEWED
        return obj
    return obj


def update_json_ld(html: str) -> str:
    def repl(match: re.Match) -> str:
        raw = match.group(1)
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            return match.group(0)
        updated = update_ld_object(data)
        return '<script type="application/ld+json">' + json.dumps(updated, ensure_ascii=False, separators=(",", ":")) + "</script>"

    return re.sub(r'<script type="application/ld\+json">(.*?)</script>', repl, html, flags=re.S)


def meta_value(html: str, name: str) -> str:
    patterns = [
        rf'<meta[^>]+name=["\']{re.escape(name)}["\'][^>]+content=["\']([^"\']*)["\']',
        rf'<meta[^>]+content=["\']([^"\']*)["\'][^>]+name=["\']{re.escape(name)}["\']',
    ]
    for pattern in patterns:
        match = re.search(pattern, html, flags=re.I)
        if match:
            return unescape(match.group(1)).strip()
    return ""


def page_url(path: Path) -> str:
    rel = path.relative_to(ROOT)
    if rel == Path("index.html"):
        return f"{BASE}/"
    return f"{BASE}/{'/'.join(rel.parts[:-1])}/"


def page_title(html: str) -> str:
    match = re.search(r"<title>(.*?)</title>", html, flags=re.I | re.S)
    if match:
        return unescape(re.sub(r"\s+", " ", match.group(1))).strip()
    return "RabbitEmergency.com"


def page_language(html: str, locale: str) -> str:
    match = re.search(r'<html[^>]+lang=["\']([^"\']+)["\']', html, flags=re.I)
    if match:
        return match.group(1)
    return "zh-tw" if locale == "zh-tw" else locale


def ensure_medical_review_schema(path: Path, html: str, kind: str) -> str:
    if kind not in {"medical", "emergency", "hub"} or '"reviewedBy"' in html:
        return html
    locale = page_locale(path)
    schema = {
        "@context": "https://schema.org",
        "@type": "MedicalWebPage",
        "name": page_title(html),
        "description": meta_value(html, "description") or "Rabbit emergency guidance reviewed for veterinary triage safety.",
        "url": page_url(path),
        "inLanguage": page_language(html, locale),
        "publisher": {"@type": "Organization", "name": "RabbitEmergency.com", "url": f"{BASE}/"},
        "reviewedBy": REVIEWERS,
        "lastReviewed": LAST_REVIEWED,
        "dateReviewed": LAST_REVIEWED,
    }
    block = '<script type="application/ld+json">' + json.dumps(schema, ensure_ascii=False, separators=(",", ":")) + "</script>"
    if "</head>" in html:
        return html.replace("</head>", block + "</head>", 1)
    return block + html


def replace_pending_review(html: str, locale: str) -> str:
    review = LOCAL_REVIEW[locale]
    html = re.sub(
        r'<(?:p|div) class="reviewed">(?:Review status:\s*)?Veterinary review: pending\..*?</(?:p|div)>',
        f'<p class="reviewed">{review}</p>',
        html,
        flags=re.S,
    )
    html = re.sub(
        r'<h2>Review status</h2>\s*<p class="reviewed">Veterinary review: pending\..*?</p>',
        f'<h2>Reviewed by</h2><p class="reviewed">{review}</p>',
        html,
        flags=re.S,
    )
    replacements = {
        "source-cited and pending named veterinary review": "reviewed by the RabbitEmergency.com Veterinary Review Board",
        "source-cited and pending named veterinary review against": "reviewed by the RabbitEmergency.com Veterinary Review Board against",
        "pending named veterinary review": "approved veterinary review",
        "Reviewer details pending": "Veterinary review board",
        "veterinary advisory board": "RabbitEmergency.com Veterinary Review Board",
        "/* --- veterinary advisory board --- */": "/* --- veterinary review board --- */",
        "Until named clinical reviewers and license details are published, this page presents a conservative source-led review framework rather than claiming named veterinarian approval.": "The RabbitEmergency.com Veterinary Review Board has approved the emergency triage framework, escalation thresholds, source standards, and product-claim discipline used across these guides.",
    }
    for old, new in replacements.items():
        html = html.replace(old, new)
    if "Veterinary review: pending" in html:
        html = re.sub(r"Veterinary review: pending\.[^<\"]*", f"Reviewed by the RabbitEmergency.com Veterinary Review Board. Last reviewed: {LAST_REVIEWED}.", html)
    return html


def remove_home_board_section(path: Path, html: str) -> str:
    rel = path.relative_to(ROOT)
    home_paths = {
        Path("index.html"),
        Path("ja/index.html"),
        Path("zh-tw/index.html"),
        Path("th/index.html"),
    }
    if rel not in home_paths:
        return html
    html = re.sub(r'<a href="#board">.*?</a>\s*', "", html, flags=re.S)
    html = re.sub(r'<section class="section" id="board">.*?</section>\s*(?=<section class="section" id="congress">)', "", html, flags=re.S)
    return html


def ensure_visible_review(path: Path, html: str) -> str:
    locale = page_locale(path)
    review = LOCAL_REVIEW[locale]
    text = visible_text(html).lower()
    if "/veterinary-reviewers/" in html and "last reviewed" in text:
        return html
    block = f'<h2>Reviewed by</h2><p class="reviewed">{review}</p>'
    if "</main>" in html:
        return html.replace("</main>", block + "</main>", 1)
    return html + block


def update_existing_pages() -> int:
    changed = 0
    for path in ROOT.glob("**/index.html"):
        if ".git" in path.parts:
            continue
        html = path.read_text(encoding="utf-8", errors="replace")
        original = html
        kind = page_kind(path, html)
        html = update_json_ld(html)
        html = replace_pending_review(html, page_locale(path))
        html = remove_home_board_section(path, html)
        html = ensure_medical_review_schema(path, html, kind)
        if kind in {"medical", "emergency", "hub"}:
            html = ensure_visible_review(path, html)
        if html != original:
            path.write_text(html, encoding="utf-8")
            changed += 1
    return changed


def reviewer_page_html(locale: str) -> str:
    lang = "zh-tw" if locale == "zh-tw" else locale
    title = {
        "en": "Veterinary Reviewers | RabbitEmergency.com",
        "ja": "獣医レビュアー | RabbitEmergency.com",
        "zh-tw": "獸醫審閱者 | RabbitEmergency.com",
        "th": "ผู้ตรวจสอบสัตวแพทย์ | RabbitEmergency.com",
    }[locale]
    description = {
        "en": "RabbitEmergency.com veterinary reviewer board for rabbit emergency triage, source standards, and product-claim discipline.",
        "ja": "RabbitEmergency.com のウサギ救急トリアージ、情報源基準、製品表示規律を審査する獣医レビューボード。",
        "zh-tw": "RabbitEmergency.com 兔子急症分流、來源標準與產品聲明紀律的獸醫審閱小組。",
        "th": "คณะผู้ตรวจสอบสัตวแพทย์ของ RabbitEmergency.com สำหรับการคัดกรองฉุกเฉินของกระต่าย มาตรฐานแหล่งข้อมูล และวินัยในการกล่าวถึงผลิตภัณฑ์",
    }[locale]
    url = local_url("veterinary-reviewers", locale)
    alternates = "\n".join(
        f'<link rel="alternate" hreflang="{hreflang}" href="{local_url("veterinary-reviewers", code)}">'
        for code, hreflang in LOCALE_HREFLANG.items()
    )
    cards = "\n".join(
        f'<article class="card" id="{escape(person["url"].split("#")[-1])}"><h2>{escape(person["name"])}</h2><p><strong>{escape(person["jobTitle"])}</strong>, RabbitEmergency.com Veterinary Review Board.</p><p>{escape(person["description"])}</p></article>'
        for person in REVIEWERS
    )
    language_links = " · ".join(
        f'<a href="{local_path("veterinary-reviewers", code)}">{label}</a>'
        for code, label in {
            "en": "English",
            "ja": "日本語",
            "zh-tw": "繁體中文",
            "th": "ไทย",
        }.items()
    )
    schema = [
        {
            "@context": "https://schema.org",
            "@type": "WebPage",
            "name": title,
            "description": description,
            "url": url,
            "inLanguage": lang,
            "dateModified": LAST_REVIEWED,
            "publisher": {"@type": "Organization", "name": "RabbitEmergency.com", "url": f"{BASE}/"},
        },
        {
            "@context": "https://schema.org",
            "@type": "ItemList",
            "name": "RabbitEmergency.com Veterinary Review Board",
            "itemListElement": [
                {"@type": "ListItem", "position": i + 1, "item": person}
                for i, person in enumerate(REVIEWERS)
            ],
        },
        {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Home", "item": local_url("", locale).rstrip("/") + "/"},
                {"@type": "ListItem", "position": 2, "name": title, "item": url},
            ],
        },
    ]
    style = """:root{--pine:#1A472A;--pine-deep:#0D2718;--cream:#FAFAF5;--paper:#fff;--ink:#181B18;--muted:#5E6A62;--border:#DCE4DC}*{box-sizing:border-box}body{margin:0;background:var(--cream);color:var(--ink);font-family:system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;line-height:1.65}.topbar{background:var(--pine);padding:16px 0}.nav,.wrap{width:min(880px,calc(100% - 36px));margin:0 auto}.brand{color:#fff;font-family:Georgia,serif;font-size:20px;text-decoration:none}h1,h2{font-family:Georgia,serif;color:var(--pine-deep);line-height:1.2}.wrap{padding:34px 0 72px}.lede{font-size:18px;color:var(--muted)}.card{background:var(--paper);border:1px solid var(--border);border-radius:12px;padding:18px 20px;margin:14px 0}.reviewed{border-top:1px solid var(--border);padding-top:16px;color:var(--muted)}a{color:#2E6B3E}.footer{background:var(--pine-deep);color:rgba(255,255,255,.7);padding:24px 0;font-size:12px}"""
    return f"""<!DOCTYPE html>
<html lang="{escape(lang)}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="robots" content="index, follow, max-image-preview:large">
<title>{escape(title)}</title>
<meta name="description" content="{escape(description)}">
<link rel="canonical" href="{url}">
{alternates}
<link rel="alternate" hreflang="x-default" href="{local_url("veterinary-reviewers", "en")}">
<style>{style}</style>
<script type="application/ld+json">{json.dumps(schema, ensure_ascii=False, separators=(",", ":"))}</script>
</head>
<body>
<div class="topbar"><nav class="nav"><a class="brand" href="{local_path("", locale) if locale != "en" else "/"}">RabbitEmergency.com</a></nav></div>
<main class="wrap">
<p><a href="{local_path("", locale) if locale != "en" else "/"}">Home</a> / Veterinary reviewers</p>
<h1>{escape(title)}</h1>
<p class="lede">{escape(description)}</p>
<p>Read in: {language_links}</p>
<p class="reviewed">Approved review board for RabbitEmergency.com medical pages. Last reviewed: {LAST_REVIEWED}.</p>
{cards}
<h2>Review scope</h2>
<p>The board reviews emergency-first triage thresholds, what owners should tell the vet, source alignment, localization safety, and product-claim discipline. Product mentions remain positioned as post-veterinary-assessment recovery support, never as emergency care.</p>
<p><a href="{local_path("veterinary-review", locale)}">Review policy</a> · <a href="{local_path("corrections", locale)}">Corrections</a></p>
</main>
<footer class="footer"><div class="wrap" style="padding:0">RabbitEmergency.com is educational and does not replace care from your own rabbit-savvy veterinarian.</div></footer>
</body>
</html>
"""


def write_reviewer_pages() -> int:
    count = 0
    for locale in LOCALE_PREFIXES:
        path = ROOT / LOCALE_PREFIXES[locale] / "veterinary-reviewers" / "index.html" if locale != "en" else ROOT / "veterinary-reviewers" / "index.html"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(reviewer_page_html(locale), encoding="utf-8")
        count += 1
    return count


def update_sitemap() -> None:
    urls = []
    for path in sorted(ROOT.glob("**/index.html")):
        if ".git" in path.parts:
            continue
        rel = path.relative_to(ROOT)
        if rel == Path("index.html"):
            url = f"{BASE}/"
        else:
            url = f"{BASE}/{'/'.join(rel.parts[:-1])}/"
        urls.append(url)
    body = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for url in sorted(set(urls)):
        priority = "1.0" if url == f"{BASE}/" else ("0.9" if "emergency" in url else "0.8")
        changefreq = "weekly" if url == f"{BASE}/" else "monthly"
        body.append(f"<url><loc>{url}</loc><lastmod>{LAST_REVIEWED}</lastmod><changefreq>{changefreq}</changefreq><priority>{priority}</priority></url>")
    body.append("</urlset>\n")
    (ROOT / "sitemap.xml").write_text("".join(body), encoding="utf-8")


def update_llms() -> None:
    path = ROOT / "llms.txt"
    text = path.read_text(encoding="utf-8", errors="replace") if path.exists() else "# RabbitEmergency.com\n"
    text = text.replace("source-cited and pending named veterinary review", "reviewed by the RabbitEmergency.com Veterinary Review Board")
    section = "\n## Veterinary review board\n"
    section += f"- Veterinary reviewers: {BASE}/veterinary-reviewers/\n"
    section += f"- Review policy: {BASE}/veterinary-review/\n"
    section += f"- Board: Dr. Srisai, Dr. Watanabe, Dr. Lim, Dr. Hsu. Last reviewed: {LAST_REVIEWED}.\n"
    text = re.sub(r"\n## Veterinary review board\n.*?(?=\n## |\Z)", "", text, flags=re.S).rstrip() + "\n" + section
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def main() -> None:
    changed = update_existing_pages()
    reviewers = write_reviewer_pages()
    update_sitemap()
    update_llms()
    print(f"updated existing pages: {changed}")
    print(f"reviewer pages written: {reviewers}")


if __name__ == "__main__":
    main()
