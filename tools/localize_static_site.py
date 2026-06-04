#!/usr/bin/env python3
"""Generate first-class JA/ZH-TW/TH static pages from the English site.

The rabbit site is deployed as static HTML. This utility treats English pages as
canonical, translates visible copy and selected metadata, then repairs URLs,
hreflang, JSON-LD language fields, sitemap, and llms.txt.
"""

from __future__ import annotations

import json
import re
import time
from copy import deepcopy
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any
from urllib.parse import urlparse
import xml.etree.ElementTree as ET

from bs4 import BeautifulSoup, NavigableString
from deep_translator import GoogleTranslator
from html_sanitizer import sanitize_html


ROOT = Path(__file__).resolve().parents[1]
SITE = "https://rabbitemergency.com"
TODAY = "2026-06-03"
CACHE_PATH = ROOT / "tools" / ".translation-cache.json"

LOCALES = {
    "ja": {
        "translator": "ja",
        "lang": "ja",
        "hreflang": "ja",
        "og": "ja_JP",
        "label": "日本語",
        "home": "ホーム",
    },
    "zh-tw": {
        "translator": "zh-TW",
        "lang": "zh-tw",
        "hreflang": "zh-Hant",
        "og": "zh_TW",
        "label": "繁體中文",
        "home": "首頁",
    },
    "th": {
        "translator": "th",
        "lang": "th",
        "hreflang": "th",
        "og": "th_TH",
        "label": "ไทย",
        "home": "หน้าแรก",
    },
}

PROTECT_TERMS = [
    "RabbitEmergency.com",
    "RodiCare",
    "WOOLY",
    "RWAF",
    "House Rabbit Society",
    "Merck Vet Manual",
    "Cornell Feline/Exotic",
    "VCA Hospitals",
    "E. cuniculi",
    "CCH Foundation",
]

NO_TRANSLATE_TEXT = {
    ".com",
    "RabbitEmergency.com",
    "DVM",
    "DVM, PhD",
    "BVMS",
}

PRESERVE_FIRST_CLASS_SLUGS = {
    "rabbit-not-eating-or-pooping",
    "rabbit-collapsed-in-heat",
    "rabbit-flystrike",
    "rabbit-head-tilt",
    "rabbit-difficulty-breathing",
    "rabbit-watery-diarrhea",
}

POST_REPLACEMENTS = {
    "ja": {
        "家": "ホーム",
        "うさぎ緊急事態": "RabbitEmergency",
        "回収棚": "回復サポート",
        "獣医のレビュー": "獣医監修",
        "頭の傾き": "斜頸",
        "珍しい救急獣医師": "エキゾチックアニマル対応の救急獣医師",
        "エキゾチックな獣医師": "エキゾチックアニマル対応の獣医師",
        "次の場合は今すぐ獣医に行ってください": "今すぐ受診すべき症状",
        "次の場合は今すぐ獣医に電話してください": "本日中に獣医師へ相談すべき症状",
        "ウサギの緊急ガイド": "うさぎ救急ガイド",
        "医薬品基準": "医学基準",
    },
    "zh-tw": {
        "兔子緊急情況": "RabbitEmergency",
        "恢復架": "復原支援",
    },
    "th": {
        "กระต่ายเหตุฉุกเฉิน": "RabbitEmergency",
        "ชั้นวางการกู้คืน": "การดูแลช่วงฟื้นตัว",
    },
}

JSON_KEYS_TO_TRANSLATE = {
    "name",
    "description",
    "headline",
    "text",
    "audienceType",
}

JSON_KEYS_NEVER_TRANSLATE = {
    "@context",
    "@type",
    "@id",
    "url",
    "item",
    "sameAs",
    "image",
    "telephone",
    "address",
    "dateModified",
    "datePublished",
    "honorificSuffix",
}


def load_cache() -> dict[str, str]:
    if CACHE_PATH.exists():
        return json.loads(CACHE_PATH.read_text(encoding="utf-8"))
    return {}


def save_cache(cache: dict[str, str]) -> None:
    CACHE_PATH.write_text(
        json.dumps(cache, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )


def protect(text: str) -> tuple[str, dict[str, str]]:
    mapping = {}
    protected = text
    for idx, term in enumerate(PROTECT_TERMS):
        if term in protected:
            token = f"ZXQ{idx}QXZ"
            protected = protected.replace(term, token)
            mapping[token] = term
    return protected, mapping


def unprotect(text: str, mapping: dict[str, str]) -> str:
    out = text
    for token, term in mapping.items():
        out = out.replace(token, term)
    return out


def should_translate(text: str) -> bool:
    text = text.strip()
    if not text or text in NO_TRANSLATE_TEXT:
        return False
    if re.fullmatch(r"[\W\d_]+", text, flags=re.UNICODE):
        return False
    if text.startswith("http://") or text.startswith("https://"):
        return False
    return True


def translate_text(text: str, locale: str, cache: dict[str, str]) -> str:
    if not should_translate(text):
        return text
    key = f"{locale}|{text}"
    if key in cache:
        return cache[key]

    protected, mapping = protect(text)
    translator = GoogleTranslator(source="en", target=LOCALES[locale]["translator"])
    last_error = None
    for attempt in range(4):
        try:
            translated = translator.translate(protected)
            translated = unprotect(translated, mapping)
            translated = translated.replace("RabbitEmergency .com", "RabbitEmergency.com")
            cache[key] = translated
            if len(cache) % 50 == 0:
                save_cache(cache)
            return translated
        except Exception as exc:  # pragma: no cover - network retry path
            last_error = exc
            time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"Could not translate {text!r} to {locale}: {last_error}")


def translate_uncached(text: str, locale: str) -> str:
    protected, mapping = protect(text)
    translator = GoogleTranslator(source="en", target=LOCALES[locale]["translator"])
    last_error = None
    for attempt in range(4):
        try:
            translated = translator.translate(protected)
            translated = unprotect(translated, mapping)
            return translated.replace("RabbitEmergency .com", "RabbitEmergency.com")
        except Exception as exc:  # pragma: no cover - network retry path
            last_error = exc
            time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"Could not translate {text!r} to {locale}: {last_error}")


def english_pages() -> list[tuple[str, Path]]:
    pages = [("", ROOT / "index.html")]
    for path in sorted(ROOT.glob("*/index.html")):
        slug = path.parent.name
        if slug in LOCALES:
            continue
        pages.append((slug, path))
    return pages


def collect_json_strings(obj: Any, out: set[str]) -> None:
    if isinstance(obj, dict):
        for key, value in obj.items():
            if key in JSON_KEYS_NEVER_TRANSLATE:
                continue
            if key in JSON_KEYS_TO_TRANSLATE and isinstance(value, str) and should_translate(value):
                out.add(value)
            else:
                collect_json_strings(value, out)
    elif isinstance(obj, list):
        for item in obj:
            collect_json_strings(item, out)


def collect_strings(pages: list[tuple[str, Path]]) -> set[str]:
    strings: set[str] = set()
    skip_parent = {"script", "style", "code", "pre", "textarea"}
    for _, path in pages:
        soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")
        for old in soup.find_all("p", class_="mono"):
            if any(label in old.get_text(" ") for label in ["English", "日本語", "繁體中文", "ไทย"]):
                old.decompose()
        for node in soup.find_all(string=True):
            parent = node.parent
            if parent and parent.name in skip_parent:
                continue
            text = str(node).strip()
            if should_translate(text):
                strings.add(text)
        for meta in soup.find_all("meta"):
            prop = meta.get("property")
            name = meta.get("name")
            if prop in {"og:title", "og:description"} or name == "description":
                value = meta.get("content", "")
                if should_translate(value):
                    strings.add(value)
        for script in soup.find_all("script", type="application/ld+json"):
            try:
                collect_json_strings(json.loads(script.string or "{}"), strings)
            except json.JSONDecodeError:
                pass
    return strings


def pretranslate(strings: set[str]) -> None:
    for locale in LOCALES:
        missing = sorted(s for s in strings if f"{locale}|{s}" not in CACHE)
        print(f"{locale}: {len(missing)} strings to translate")
        if not missing:
            continue
        completed = 0
        with ThreadPoolExecutor(max_workers=10) as pool:
            futures = {pool.submit(translate_uncached, text, locale): text for text in missing}
            for future in as_completed(futures):
                text = futures[future]
                CACHE[f"{locale}|{text}"] = future.result()
                completed += 1
                if completed % 100 == 0:
                    save_cache(CACHE)
                    print(f"{locale}: {completed}/{len(missing)}")
        save_cache(CACHE)


def localized_url(slug: str, locale: str) -> str:
    if slug:
        return f"{SITE}/{locale}/{slug}/"
    return f"{SITE}/{locale}/"


def english_url(slug: str) -> str:
    if slug:
        return f"{SITE}/{slug}/"
    return f"{SITE}/"


def alternate_links(slug: str) -> list[tuple[str, str]]:
    links = [("en", english_url(slug))]
    for locale, cfg in LOCALES.items():
        links.append((cfg["hreflang"], localized_url(slug, locale)))
    links.append(("x-default", english_url(slug)))
    return links


def set_head_links(soup: BeautifulSoup, slug: str, locale: str | None) -> None:
    head = soup.head
    if not head:
        return
    for tag in head.find_all("link", rel=lambda rel: rel and ("canonical" in rel or "alternate" in rel)):
        tag.decompose()

    canonical = soup.new_tag("link", rel="canonical")
    canonical["href"] = localized_url(slug, locale) if locale else english_url(slug)
    head.append(canonical)
    for hreflang, href in alternate_links(slug):
        alt = soup.new_tag("link", rel="alternate")
        alt["hreflang"] = hreflang
        alt["href"] = href
        head.append(alt)


def localize_href(href: str, locale: str, localized_slugs: set[str]) -> str:
    if not href or href.startswith(("#", "mailto:", "tel:", "http://", "https://")):
        return href
    if href == "/":
        return f"/{locale}/"
    if href.startswith("/#"):
        return f"/{locale}/{href[1:]}"
    match = re.fullmatch(r"/([^/#?]+)/?(#.*)?", href)
    if match and match.group(1) in localized_slugs:
        return f"/{locale}/{match.group(1)}/{match.group(2) or ''}"
    return href


def language_switcher(soup: BeautifulSoup, slug: str, locale: str | None) -> BeautifulSoup:
    p = soup.new_tag("p")
    p["class"] = "mono"
    p["style"] = "font-size:11px;color:var(--quiet);margin:0 0 16px"

    entries = [("en", "English", english_url(slug).replace(SITE, ""))]
    entries += [
        (loc, cfg["label"], localized_url(slug, loc).replace(SITE, ""))
        for loc, cfg in LOCALES.items()
    ]

    for idx, (code, label, href) in enumerate(entries):
        if idx:
            p.append(NavigableString(" · "))
        if (locale is None and code == "en") or locale == code:
            strong = soup.new_tag("strong")
            strong.string = label
            p.append(strong)
        else:
            a = soup.new_tag("a", href=href)
            a.string = label
            p.append(a)
    return p


def insert_language_switcher(soup: BeautifulSoup, slug: str, locale: str | None) -> None:
    main = soup.find("main")
    if not main:
        return
    for old in main.find_all("p", class_="mono"):
        if "English" in old.get_text(" "):
            old.decompose()
    crumb = main.find("div", class_="crumb")
    switcher = language_switcher(soup, slug, locale)
    if crumb:
        crumb.insert_after(switcher)
    else:
        h1 = main.find("h1")
        if h1:
            h1.insert_before(switcher)


def repair_urls_and_meta(soup: BeautifulSoup, slug: str, locale: str | None, localized_slugs: set[str]) -> None:
    if soup.html:
        soup.html["lang"] = LOCALES[locale]["lang"] if locale else "en"
    target_url = localized_url(slug, locale) if locale else english_url(slug)
    og_locale = "en_US" if locale is None else LOCALES[locale]["og"]
    for meta in soup.find_all("meta"):
        prop = meta.get("property")
        name = meta.get("name")
        if prop == "og:url":
            meta["content"] = target_url
        elif prop == "og:locale":
            meta["content"] = og_locale
        elif locale and (prop in {"og:title", "og:description"} or name == "description"):
            meta["content"] = translate_text(meta.get("content", ""), locale, CACHE)
    if locale:
        for a in soup.find_all("a", href=True):
            a["href"] = localize_href(a["href"], locale, localized_slugs)
        brand = soup.select_one(".brand")
        if brand:
            brand["href"] = f"/{locale}/"


def translate_visible_text(soup: BeautifulSoup, locale: str) -> None:
    skip_parent = {"script", "style", "code", "pre", "textarea"}
    for node in list(soup.find_all(string=True)):
        parent = node.parent
        if parent and parent.name in skip_parent:
            continue
        text = str(node)
        if not text.strip():
            continue
        leading = text[: len(text) - len(text.lstrip())]
        trailing = text[len(text.rstrip()) :]
        compact = text.strip()
        node.replace_with(leading + translate_text(compact, locale, CACHE) + trailing)


def translate_json_obj(obj: Any, locale: str, source_url: str, target_url: str) -> Any:
    if isinstance(obj, dict):
        out = {}
        for key, value in obj.items():
            if key in JSON_KEYS_NEVER_TRANSLATE:
                out[key] = value
            elif key == "inLanguage":
                out[key] = LOCALES[locale]["lang"]
            elif key in JSON_KEYS_TO_TRANSLATE and isinstance(value, str):
                out[key] = translate_text(value, locale, CACHE)
            else:
                out[key] = translate_json_obj(value, locale, source_url, target_url)
        if out.get("@type") in {"MedicalWebPage", "WebPage", "Article"}:
            out["url"] = target_url
            out["translationOfWork"] = {"@id": source_url}
        return out
    if isinstance(obj, list):
        return [translate_json_obj(item, locale, source_url, target_url) for item in obj]
    return obj


def repair_jsonld(soup: BeautifulSoup, slug: str, locale: str | None) -> None:
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.string or "{}")
        except json.JSONDecodeError:
            continue
        if locale:
            data = translate_json_obj(data, locale, english_url(slug), localized_url(slug, locale))
        script.string = json.dumps(data, ensure_ascii=False, separators=(",", ": "))


def postprocess_locale_html(html: str, locale: str) -> str:
    for old, new in POST_REPLACEMENTS.get(locale, {}).items():
        html = html.replace(old, new)
    return html


def render_html(soup: BeautifulSoup, locale: str | None = None) -> str:
    html = str(soup)
    if locale:
        return postprocess_locale_html(html, locale)
    return html


def localize_page(slug: str, source: Path, locale: str, localized_slugs: set[str]) -> None:
    out_dir = ROOT / locale / slug if slug else ROOT / locale
    out_path = out_dir / "index.html"
    if slug in PRESERVE_FIRST_CLASS_SLUGS and out_path.exists():
        return
    soup = BeautifulSoup(source.read_text(encoding="utf-8"), "html.parser")
    for old in soup.find_all("p", class_="mono"):
        if any(label in old.get_text(" ") for label in ["English", "日本語", "繁體中文", "ไทย"]):
            old.decompose()
    set_head_links(soup, slug, locale)
    translate_visible_text(soup, locale)
    repair_urls_and_meta(soup, slug, locale, localized_slugs)
    repair_jsonld(soup, slug, locale)
    insert_language_switcher(soup, slug, locale)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path.write_text(sanitize_html(render_html(soup, locale), out_path), encoding="utf-8")


def repair_english_page(slug: str, source: Path) -> None:
    soup = BeautifulSoup(source.read_text(encoding="utf-8"), "html.parser")
    set_head_links(soup, slug, None)
    insert_language_switcher(soup, slug, None)
    source.write_text(sanitize_html(render_html(soup), source), encoding="utf-8")


def write_sitemap(pages: list[tuple[str, Path]]) -> None:
    urls = [english_url("")]
    urls += [english_url(slug) for slug, _ in pages if slug]
    for locale in LOCALES:
        urls.append(localized_url("", locale))
        urls += [localized_url(slug, locale) for slug, _ in pages if slug]

    body = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for idx, url in enumerate(urls):
        priority = "1.0" if url.rstrip("/") == SITE else "0.8"
        changefreq = "weekly" if priority == "1.0" else "monthly"
        body.append(
            f"<url><loc>{url}</loc><lastmod>{TODAY}</lastmod>"
            f"<changefreq>{changefreq}</changefreq><priority>{priority}</priority></url>"
        )
    body.append("</urlset>")
    (ROOT / "sitemap.xml").write_text("".join(body), encoding="utf-8")


def write_llms(pages: list[tuple[str, Path]]) -> None:
    soup_cache = {}
    lines = [
        "# RabbitEmergency.com",
        "",
        "> Educational rabbit-emergency triage for owners across Asia, now available in English, Japanese, Traditional Chinese, and Thai. Not a substitute for veterinary care.",
        "",
        "## Languages",
        "- English: https://rabbitemergency.com/",
        "- Japanese: https://rabbitemergency.com/ja/",
        "- Traditional Chinese: https://rabbitemergency.com/zh-tw/",
        "- Thai: https://rabbitemergency.com/th/",
        "",
        "## Sitemap",
        "- https://rabbitemergency.com/sitemap.xml",
        "",
        "## All localized pages",
    ]
    for slug, path in pages:
        soup_cache[slug] = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")
        title = soup_cache[slug].find("h1")
        label = title.get_text(" ", strip=True) if title else "Home"
        lines.append(f"- [{label}]({english_url(slug)})")
        for locale, cfg in LOCALES.items():
            lines.append(f"  - {cfg['label']}: {localized_url(slug, locale)}")
    (ROOT / "llms.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")


def validate(pages: list[tuple[str, Path]]) -> None:
    expected = 1 + len([p for p in pages if p[0]]) + len(LOCALES) * len(pages)
    sitemap = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
    count = sitemap.count("<loc>")
    if count != expected:
        raise SystemExit(f"sitemap URL count {count}, expected {expected}")

    missing = []
    bad_json = []
    for slug, _ in pages:
        paths = [ROOT / slug / "index.html"] if slug else [ROOT / "index.html"]
        paths += [(ROOT / loc / slug / "index.html") if slug else (ROOT / loc / "index.html") for loc in LOCALES]
        for path in paths:
            if not path.exists():
                missing.append(str(path))
                continue
            soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")
            for script in soup.find_all("script", type="application/ld+json"):
                try:
                    json.loads(script.string or "{}")
                except Exception as exc:
                    bad_json.append(f"{path}: {exc}")
            alt_count = len(soup.find_all("link", rel="alternate"))
            if alt_count != len(LOCALES) + 2:
                missing.append(f"{path}: alternate count {alt_count}")
    if missing or bad_json:
        raise SystemExit("\n".join(missing + bad_json))
    print(f"validated: {len(pages)} source pages, {count} sitemap URLs, {len(LOCALES)} locales")


CACHE = load_cache()


def main() -> None:
    pages = english_pages()
    pretranslate(collect_strings(pages))
    localized_slugs = {slug for slug, _ in pages if slug}
    for slug, path in pages:
        repair_english_page(slug, path)
        for locale in LOCALES:
            localize_page(slug, path, locale, localized_slugs)
    write_sitemap(pages)
    write_llms(pages)
    save_cache(CACHE)
    validate(pages)


if __name__ == "__main__":
    main()
