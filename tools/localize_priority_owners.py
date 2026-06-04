#!/usr/bin/env python3
"""Scoped localization for thickened priority owner pages.

This intentionally avoids the broad all-site localizer. It rewrites only the
Tier 1/Tier 2 owner pages, locale homepages, and requested market clinic pages.
Redirect stubs are never touched.
"""

from __future__ import annotations

import argparse
import json
import re
import signal
import time
import xml.etree.ElementTree as ET
from copy import deepcopy
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from bs4 import BeautifulSoup, NavigableString
from deep_translator import GoogleTranslator


ROOT = Path(__file__).resolve().parents[1]
SITE = "https://rabbitemergency.com"
TODAY = "2026-06-04"
CACHE_PATH = ROOT / "tools" / ".translation-cache.json"
REDIRECT_MANIFEST = ROOT / "tools" / "redirect_manifest.json"

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

TIER1_OWNERS = [
    "rabbit-not-eating-or-pooping",
    "rabbit-gut-stasis-emergency-hub",
    "rabbit-collapsed-in-heat",
    "rabbit-flystrike",
    "rabbit-head-tilt",
    "rabbit-bloat-hard-belly",
    "rabbit-difficulty-breathing",
    "rabbit-watery-diarrhea",
    "rabbit-soft-stool-no-caecotrophs",
    "rabbit-not-drinking-dehydrated",
    "rabbit-overgrown-teeth-drooling",
    "rabbit-seizure",
    "rabbit-blood-in-urine",
    "rabbit-straining-to-urinate",
    "rabbit-post-op-not-eating",
]

TIER2_OWNERS = [
    "rabbit-urinary-emergency-hub",
    "rabbit-breathing-emergency-hub",
    "rabbit-poisoning-emergency-hub",
    "rabbit-injury-trauma-emergency-hub",
    "rabbit-ate-something-toxic",
    "rabbit-lethargic-not-moving",
    "rabbit-pale-gums-emergency-signs",
    "rabbit-abscess-or-lump",
    "rabbit-hind-leg-weakness",
    "rabbit-fall-or-trauma",
    "rabbit-bleeding-nail-or-wound",
    "rabbit-snuffles-runny-nose",
    "rabbit-eye-injury-discharge",
    "rabbit-ear-infection-scratching",
    "rabbit-grinding-teeth",
    "rabbit-pain-signs",
    "rabbit-cold-hypothermia",
    "rabbit-moulting-hairball-gut",
    "rabbit-choking-or-gagging",
    "baby-rabbit-not-eating",
]

OWNER_SLUGS = TIER1_OWNERS + TIER2_OWNERS
HUB_SLUGS = [
    "rabbit-gut-stasis-emergency-hub",
    "rabbit-urinary-emergency-hub",
    "rabbit-breathing-emergency-hub",
    "rabbit-poisoning-emergency-hub",
    "rabbit-injury-trauma-emergency-hub",
]

MARKET_CITY_SLUGS = {
    "ja": ["rabbit-emergency-vet-tokyo"],
    "zh-tw": ["rabbit-emergency-vet-taipei", "rabbit-emergency-vet-hong-kong"],
    "th": ["rabbit-emergency-vet-bangkok"],
}

CITY_SLUGS = sorted({slug for slugs in MARKET_CITY_SLUGS.values() for slug in slugs} | {"rabbit-emergency-vet-singapore"})

PROTECT_TERMS = [
    "RabbitEmergency.com",
    "RabbitEmergency",
    "RodiCare",
    "WOOLY",
    "RWAF",
    "House Rabbit Society",
    "Merck Vet Manual",
    "Cornell Feline/Exotic",
    "VCA Hospitals",
    "E. cuniculi",
    "CCH Foundation",
    "Mitaka Veterinary Medical Group / Japan Veterinary Medical Group",
    "Daktari Animal Hospital Tokyo Medical Center",
    "みわエキゾチック動物病院 / Japan Exotic Animal Medical Center",
    "The Ark Veterinary Hospital",
    "CityU Veterinary Medical Centre",
    "Taipei",
    "Tokyo",
    "Bangkok",
    "Hong Kong",
    "Singapore",
]

NO_TRANSLATE_TEXT = {".com", "RabbitEmergency.com", "DVM", "BVMS", "DVM, PhD"}

JSON_KEYS_TO_TRANSLATE = {"name", "description", "headline", "text", "audienceType"}
JSON_KEYS_NEVER_TRANSLATE = {
    "@context",
    "@type",
    "@id",
    "sameAs",
    "image",
    "telephone",
    "address",
    "dateModified",
    "datePublished",
    "honorificSuffix",
}

POST_REPLACEMENTS = {
    "ja": {
        "家": "ホーム",
        "ウサギの緊急事態": "RabbitEmergency",
        "うさぎ緊急事態": "RabbitEmergency",
        "珍しい": "エキゾチック",
        "次の場合は今すぐ獣医に行ってください": "今すぐ受診すべき症状",
    },
    "zh-tw": {
        "兔子緊急情況": "RabbitEmergency",
        "兔子緊急": "RabbitEmergency",
    },
    "th": {
        "กระต่ายเหตุฉุกเฉิน": "RabbitEmergency",
        "เหตุฉุกเฉินกระต่าย": "RabbitEmergency",
    },
}


def load_cache() -> dict[str, str]:
    if CACHE_PATH.exists():
        return json.loads(CACHE_PATH.read_text(encoding="utf-8"))
    return {}


def save_cache(cache: dict[str, str]) -> None:
    CACHE_PATH.write_text(json.dumps(cache, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")


CACHE = load_cache()


class TranslationTimeout(Exception):
    pass


def _translation_timeout(_signum: int, _frame: Any) -> None:
    raise TranslationTimeout("translation request timed out")


def manifest_redirects() -> set[str]:
    data = json.loads(REDIRECT_MANIFEST.read_text(encoding="utf-8"))
    return set(data.get("redirects", {}).keys())


REDIRECT_SLUGS = manifest_redirects()


def path_for(slug: str, locale: str | None = None) -> Path:
    if locale:
        return ROOT / locale / slug / "index.html" if slug else ROOT / locale / "index.html"
    return ROOT / slug / "index.html" if slug else ROOT / "index.html"


def url_for(slug: str, locale: str | None = None) -> str:
    if locale:
        return f"{SITE}/{locale}/{slug}/" if slug else f"{SITE}/{locale}/"
    return f"{SITE}/{slug}/" if slug else f"{SITE}/"


def slug_from_url(url: str) -> tuple[str | None, str | None]:
    parsed = urlparse(url)
    if parsed.netloc and parsed.netloc != "rabbitemergency.com":
        return None, None
    path = parsed.path.strip("/")
    if not path:
        return "", None
    bits = path.split("/")
    if bits[0] in LOCALES:
        return "/".join(bits[1:]), bits[0]
    return bits[0], None


def is_stub(path: Path) -> bool:
    if not path.exists():
        return False
    text = path.read_text(encoding="utf-8")
    return "noindex" in text.lower() or "http-equiv=\"refresh\"" in text.lower() or "http-equiv='refresh'" in text.lower()


def is_live(slug: str, locale: str | None = None) -> bool:
    if slug in REDIRECT_SLUGS:
        return False
    path = path_for(slug, locale)
    return path.exists() and not is_stub(path)


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
    stripped = text.strip()
    if not stripped or stripped in NO_TRANSLATE_TEXT:
        return False
    if re.fullmatch(r"[\W\d_]+", stripped, flags=re.UNICODE):
        return False
    if stripped.startswith(("http://", "https://", "mailto:", "tel:")):
        return False
    return True


def translate_text(text: str, locale: str) -> str:
    if not should_translate(text):
        return text
    key = f"{locale}|{text}"
    if key in CACHE:
        return CACHE[key]
    protected, mapping = protect(text)
    translator = GoogleTranslator(source="en", target=LOCALES[locale]["translator"])
    last_error = None
    for attempt in range(4):
        try:
            signal.signal(signal.SIGALRM, _translation_timeout)
            signal.alarm(18)
            try:
                translated = translator.translate(protected)
            finally:
                signal.alarm(0)
            translated = unprotect(translated, mapping).replace("RabbitEmergency .com", "RabbitEmergency.com")
            CACHE[key] = translated
            if len(CACHE) % 100 == 0:
                save_cache(CACHE)
            return translated
        except Exception as exc:
            last_error = exc
            time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"Could not translate {text!r} to {locale}: {last_error}")


def cluster_locales(slug: str) -> list[tuple[str, str | None, str]]:
    cluster = [("en", None, url_for(slug))]
    for locale, cfg in LOCALES.items():
        if is_live(slug, locale):
            cluster.append((cfg["hreflang"], locale, url_for(slug, locale)))
    cluster.append(("x-default", None, url_for(slug)))
    return cluster


def set_head_links(soup: BeautifulSoup, slug: str, locale: str | None) -> None:
    head = soup.head
    if not head:
        return
    for tag in list(head.find_all("link")):
        if tag.attrs is None:
            continue
        rel = tag.get("rel") or []
        if "canonical" in rel or "alternate" in rel:
            tag.decompose()
    canonical = soup.new_tag("link", rel="canonical", href=url_for(slug, locale))
    head.append(canonical)
    for hreflang, _, href in cluster_locales(slug):
        alt = soup.new_tag("link", rel="alternate", hreflang=hreflang, href=href)
        head.append(alt)


def localize_href(href: str, locale: str) -> str:
    if not href or href.startswith(("#", "mailto:", "tel:")):
        return href
    if href.startswith(("http://", "https://")):
        slug, href_locale = slug_from_url(href)
        if slug is None or href_locale:
            return href
        return url_for(slug, locale) if is_live(slug, locale) else href
    if href == "/":
        return f"/{locale}/"
    if href.startswith("/#"):
        return f"/{locale}/{href[1:]}"
    match = re.fullmatch(r"/([^?#/]+)/?(#[^?]*)?(\?.*)?", href)
    if match:
        slug = match.group(1)
        suffix = (match.group(2) or "") + (match.group(3) or "")
        if is_live(slug, locale):
            return f"/{locale}/{slug}/{suffix}"
    return href


def localize_url_string(value: str, locale: str) -> str:
    slug, href_locale = slug_from_url(value)
    if slug is None or href_locale:
        return value
    return url_for(slug, locale) if is_live(slug, locale) else value


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
        node.replace_with(leading + translate_text(text.strip(), locale) + trailing)


def translate_json_obj(obj: Any, locale: str) -> Any:
    if isinstance(obj, dict):
        out: dict[str, Any] = {}
        for key, value in obj.items():
            if key in JSON_KEYS_NEVER_TRANSLATE:
                out[key] = value
            elif key in {"url", "item"} and isinstance(value, str):
                out[key] = localize_url_string(value, locale)
            elif key == "inLanguage":
                out[key] = LOCALES[locale]["lang"]
            elif key in JSON_KEYS_TO_TRANSLATE and isinstance(value, str):
                out[key] = translate_text(value, locale)
            else:
                out[key] = translate_json_obj(value, locale)
        return out
    if isinstance(obj, list):
        return [translate_json_obj(item, locale) for item in obj]
    return obj


def jsonld_blocks(soup: BeautifulSoup) -> list[Any]:
    blocks = []
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            blocks.append(json.loads(script.string or "{}"))
        except json.JSONDecodeError:
            continue
    return blocks


def iter_schema_items(data: Any) -> list[dict[str, Any]]:
    if isinstance(data, dict):
        if "@graph" in data:
            return [item for item in data["@graph"] if isinstance(item, dict)]
        return [data]
    if isinstance(data, list):
        return [item for item in data if isinstance(item, dict)]
    return []


def has_schema_type(soup: BeautifulSoup, schema_type: str) -> bool:
    for block in jsonld_blocks(soup):
        for item in iter_schema_items(block):
            types = item.get("@type")
            if types == schema_type or (isinstance(types, list) and schema_type in types):
                return True
    return False


def page_title(soup: BeautifulSoup) -> str:
    h1 = soup.find("h1")
    if h1:
        return h1.get_text(" ", strip=True)
    if soup.title:
        return soup.title.get_text(" ", strip=True)
    return "Rabbit emergency guidance"


def page_description(soup: BeautifulSoup) -> str:
    meta = soup.find("meta", attrs={"name": "description"})
    if meta and meta.get("content"):
        return meta["content"]
    lede = soup.find(class_="lede")
    if lede:
        return lede.get_text(" ", strip=True)
    return "Source-cited rabbit emergency guidance for owners."


def append_jsonld(soup: BeautifulSoup, data: Any) -> None:
    script = soup.new_tag("script", type="application/ld+json")
    script.string = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    (soup.head or soup).append(script)


def ensure_required_schema(soup: BeautifulSoup, slug: str, locale: str | None) -> None:
    lang = "en" if locale is None else LOCALES[locale]["lang"]
    title = page_title(soup)
    desc = page_description(soup)
    target = url_for(slug, locale)
    if not has_schema_type(soup, "MedicalWebPage"):
        append_jsonld(
            soup,
            {
                "@context": "https://schema.org",
                "@type": "MedicalWebPage",
                "name": title,
                "description": desc,
                "url": target,
                "inLanguage": lang,
                "dateModified": TODAY,
                "publisher": {"@type": "Organization", "name": "RabbitEmergency.com", "url": SITE},
            },
        )
    if not has_schema_type(soup, "BreadcrumbList"):
        home_name = "Home" if locale is None else LOCALES[locale]["home"]
        append_jsonld(
            soup,
            {
                "@context": "https://schema.org",
                "@type": "BreadcrumbList",
                "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": home_name, "item": url_for("", locale)},
                    {"@type": "ListItem", "position": 2, "name": title, "item": target},
                ],
            },
        )
    if not has_schema_type(soup, "FAQPage"):
        q1 = "Can this wait until tomorrow?"
        a1 = "Do not wait overnight if your rabbit is not eating, not passing droppings, weak, collapsed, breathing abnormally, bleeding, bloated, exposed to toxins, or rapidly worsening. Call an exotic-capable or rabbit-savvy vet while preparing to travel."
        q2 = "What should I tell the clinic first?"
        a2 = "Start with the main sign, when it began, appetite, droppings, urine, breathing, posture, pain signs, recent surgery, heat exposure, trauma, and possible toxin or medication exposure."
        if locale:
            q1, a1, q2, a2 = [translate_text(x, locale) for x in (q1, a1, q2, a2)]
        append_jsonld(
            soup,
            {
                "@context": "https://schema.org",
                "@type": "FAQPage",
                "mainEntity": [
                    {"@type": "Question", "name": q1, "acceptedAnswer": {"@type": "Answer", "text": a1}},
                    {"@type": "Question", "name": q2, "acceptedAnswer": {"@type": "Answer", "text": a2}},
                ],
            },
        )


def repair_jsonld(soup: BeautifulSoup, slug: str, locale: str | None) -> None:
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.string or "{}")
        except json.JSONDecodeError:
            script.decompose()
            continue
        if locale:
            data = translate_json_obj(data, locale)
        for item in iter_schema_items(data):
            if item.get("@type") in {"MedicalWebPage", "WebPage", "Article"}:
                item["url"] = url_for(slug, locale)
                item["inLanguage"] = "en" if locale is None else LOCALES[locale]["lang"]
                item["dateModified"] = TODAY
        script.string = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    ensure_required_schema(soup, slug, locale)


def remove_language_switchers(soup: BeautifulSoup) -> None:
    for old in soup.find_all("p", class_="mono"):
        text = old.get_text(" ")
        if any(label in text for label in ["English", "日本語", "繁體中文", "ไทย"]):
            old.decompose()


def language_switcher(soup: BeautifulSoup, slug: str, locale: str | None) -> BeautifulSoup:
    p = soup.new_tag("p")
    p["class"] = "mono"
    entries = []
    for hreflang, loc, href in cluster_locales(slug):
        if hreflang == "x-default":
            continue
        label = "English" if loc is None else LOCALES[loc]["label"]
        entries.append((loc, label, href.replace(SITE, "")))
    for idx, (loc, label, href) in enumerate(entries):
        if idx:
            p.append(NavigableString(" · "))
        active = (locale is None and loc is None) or locale == loc
        if active:
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
    remove_language_switchers(soup)
    switcher = language_switcher(soup, slug, locale)
    crumb = main.find("div", class_="crumb")
    if crumb:
        crumb.insert_after(switcher)
        return
    h1 = main.find("h1")
    if h1:
        h1.insert_before(switcher)


def repair_urls_and_meta(soup: BeautifulSoup, slug: str, locale: str | None) -> None:
    if soup.html:
        soup.html["lang"] = "en" if locale is None else LOCALES[locale]["lang"]
    target_url = url_for(slug, locale)
    for meta in soup.find_all("meta"):
        prop = meta.get("property")
        name = meta.get("name")
        if prop == "og:url":
            meta["content"] = target_url
        elif prop == "og:locale":
            meta["content"] = "en_US" if locale is None else LOCALES[locale]["og"]
        elif locale and (prop in {"og:title", "og:description"} or name == "description") and meta.get("content"):
            meta["content"] = translate_text(meta["content"], locale)
    if locale:
        if soup.title and soup.title.string:
            soup.title.string = translate_text(soup.title.string, locale)
        for a in soup.find_all("a", href=True):
            a["href"] = localize_href(a["href"], locale)
        brand = soup.select_one(".brand")
        if brand:
            brand["href"] = f"/{locale}/"


def render_html(soup: BeautifulSoup, locale: str | None) -> str:
    html = str(soup)
    if not html.startswith("<!DOCTYPE html>"):
        html = "<!DOCTYPE html>\n" + html
    if locale:
        for old, new in POST_REPLACEMENTS.get(locale, {}).items():
            html = html.replace(old, new)
    return html


def localize_page(slug: str, locale: str) -> None:
    if not is_live(slug):
        raise SystemExit(f"Refusing to localize non-live source: {slug or '/'}")
    out_path = path_for(slug, locale)
    if is_stub(out_path):
        raise SystemExit(f"Refusing to overwrite redirect stub: {out_path}")
    source = path_for(slug)
    soup = BeautifulSoup(source.read_text(encoding="utf-8"), "html.parser")
    set_head_links(soup, slug, locale)
    translate_visible_text(soup, locale)
    repair_urls_and_meta(soup, slug, locale)
    repair_jsonld(soup, slug, locale)
    insert_language_switcher(soup, slug, locale)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(render_html(soup, locale), encoding="utf-8")


def repair_english_page(slug: str) -> None:
    if not is_live(slug):
        raise SystemExit(f"Refusing to repair non-live English source: {slug or '/'}")
    path = path_for(slug)
    soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")
    set_head_links(soup, slug, None)
    repair_urls_and_meta(soup, slug, None)
    repair_jsonld(soup, slug, None)
    insert_language_switcher(soup, slug, None)
    path.write_text(render_html(soup, None), encoding="utf-8")


def scoped_slugs_for_locale(locale: str) -> list[str]:
    return [""] + OWNER_SLUGS + MARKET_CITY_SLUGS.get(locale, [])


def collect_live_sitemap_urls() -> list[str]:
    urls = [url_for("")]
    for path in sorted(ROOT.glob("*/index.html")):
        slug = path.parent.name
        if slug in LOCALES or slug in REDIRECT_SLUGS or is_stub(path):
            continue
        urls.append(url_for(slug))
    for locale in LOCALES:
        home = path_for("", locale)
        if home.exists() and not is_stub(home):
            urls.append(url_for("", locale))
        for path in sorted((ROOT / locale).glob("*/index.html")):
            slug = path.parent.name
            if slug in REDIRECT_SLUGS or is_stub(path):
                continue
            urls.append(url_for(slug, locale))
    return sorted(dict.fromkeys(urls), key=lambda x: (x.count("/"), x))


def write_sitemap() -> None:
    urls = collect_live_sitemap_urls()
    body = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for url in urls:
        priority = "1.0" if url.rstrip("/") == SITE else "0.8"
        changefreq = "weekly" if priority == "1.0" else "monthly"
        body.append(f"<url><loc>{url}</loc><lastmod>{TODAY}</lastmod><changefreq>{changefreq}</changefreq><priority>{priority}</priority></url>")
    body.append("</urlset>")
    (ROOT / "sitemap.xml").write_text("".join(body), encoding="utf-8")


def validate_jsonld(paths: list[Path]) -> list[str]:
    errors = []
    for path in paths:
        soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")
        for idx, script in enumerate(soup.find_all("script", type="application/ld+json"), 1):
            try:
                json.loads(script.string or "{}")
            except Exception as exc:
                errors.append(f"{path}: JSON-LD {idx}: {exc}")
    return errors


def validate_hreflang(slugs: list[str]) -> list[str]:
    errors = []
    for slug in slugs:
        live_paths = [(None, path_for(slug))]
        live_paths += [(loc, path_for(slug, loc)) for loc in LOCALES if is_live(slug, loc)]
        expected = {hreflang: href for hreflang, _, href in cluster_locales(slug)}
        for loc, path in live_paths:
            if not path.exists():
                errors.append(f"{path}: missing live cluster page")
                continue
            soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")
            canonical = soup.find("link", rel="canonical")
            if not canonical or canonical.get("href") != url_for(slug, loc):
                errors.append(f"{path}: bad canonical")
            actual = {tag.get("hreflang"): tag.get("href") for tag in soup.find_all("link", rel="alternate")}
            if actual != expected:
                errors.append(f"{path}: hreflang mismatch")
            for hreflang, href in actual.items():
                alt_slug, alt_locale = slug_from_url(href or "")
                if hreflang == "x-default":
                    if href != url_for(slug):
                        errors.append(f"{path}: x-default not EN")
                    continue
                if alt_slug is None or not is_live(alt_slug, alt_locale):
                    errors.append(f"{path}: hreflang points to non-live page {href}")
    return errors


def validate_sitemap() -> tuple[int, list[str]]:
    errors = []
    tree = ET.parse(ROOT / "sitemap.xml")
    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    urls = [node.text or "" for node in tree.findall(".//sm:loc", ns)]
    for url in urls:
        slug, locale = slug_from_url(url)
        if slug is None or not is_live(slug, locale):
            errors.append(f"sitemap contains non-live URL: {url}")
    return len(urls), errors


def run(locale: str | None) -> None:
    locales = [locale] if locale else list(LOCALES)
    changed_slugs = []
    for loc in locales:
        slugs = scoped_slugs_for_locale(loc)
        for idx, slug in enumerate(slugs, 1):
            print(f"{loc}: {idx}/{len(slugs)} {slug or 'home'}", flush=True)
            localize_page(slug, loc)
        changed_slugs.extend(slugs)
    for slug in sorted(set(changed_slugs + CITY_SLUGS)):
        if is_live(slug):
            repair_english_page(slug)
    write_sitemap()
    save_cache(CACHE)

    scoped = sorted(set(changed_slugs + CITY_SLUGS))
    json_errors = validate_jsonld([path_for(slug, loc) for slug in scoped for loc in [None, *LOCALES.keys()] if path_for(slug, loc).exists() and not is_stub(path_for(slug, loc))])
    hreflang_errors = validate_hreflang(scoped)
    sitemap_count, sitemap_errors = validate_sitemap()
    errors = json_errors + hreflang_errors + sitemap_errors
    if errors:
        raise SystemExit("\n".join(errors))
    for loc in locales:
        owners = len(OWNER_SLUGS)
        cities = len(MARKET_CITY_SLUGS.get(loc, []))
        print(f"{loc}: localized {owners} owners, homepage, {len(HUB_SLUGS)} hubs, {cities} market city page(s)")
    print(f"scoped localization OK; sitemap URLs: {sitemap_count}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--locale", choices=sorted(LOCALES))
    args = parser.parse_args()
    run(args.locale)


if __name__ == "__main__":
    main()
