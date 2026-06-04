#!/usr/bin/env python3
"""Repair schema and thin emergency pages for RabbitEmergency.com.

This does not apply or alter the veterinary approval system. It only adds
missing FAQ/Breadcrumb JSON-LD, visible FAQ blocks where needed, and useful
emergency prep content to pages under the content-length gate.
"""

from __future__ import annotations

from html import escape, unescape
from pathlib import Path
import json
import re

from content_quality_gate import ROOT, BASE, content_word_count, ld_types, page_kind, visible_text
from html_sanitizer import sanitize_html, scrub_review_schema

LAST_REVIEWED = "2026-06-03"

REVIEWERS = {
    "@type": "Organization",
    "name": "RabbitEmergency.com source-led veterinary review process",
    "url": f"{BASE}/veterinary-review/",
    "description": "Source-cited rabbit emergency guidance with veterinary review pending.",
}

VISIBLE_REVIEW = (
    'Source-cited guidance; <a href="/veterinary-review/">veterinary review pending</a>.'
)


LOCALES = {
    "en": {
        "prefix": "",
        "home": "Home",
        "faq_heading": "Emergency FAQ",
        "prep_heading": "Before you leave or call",
        "prep_body": [
            "Write down the exact time the sign started, the last normal meal, the last normal droppings, and whether your rabbit has urinated. These details help the clinic decide how urgent the case is and what equipment or staff may be needed when you arrive.",
            "Take clear photos of droppings, urine, wounds, discharge, packaging from anything eaten, and your rabbit's posture. Keep your rabbit warm or cool only in a gentle way that matches the problem, and avoid baths, force-feeding, human medicine, or leftover medication unless a veterinarian tells you to do it for this episode.",
            "Use a secure carrier with a towel, keep bonded companions together only if travel is safe, and call while preparing to travel. Ask the clinic whether a rabbit-savvy or exotic vet is on duty now, whether you should come immediately, and what they want you to bring.",
        ],
        "faq": [
            (
                "Can this wait until tomorrow?",
                "Do not wait overnight if your rabbit is not eating, not passing droppings, weak, collapsed, breathing abnormally, bleeding, bloated, exposed to toxins, or rapidly worsening. Call an exotic-capable or rabbit-savvy vet while preparing to travel.",
            ),
            (
                "What should I tell the clinic first?",
                "Start with the main sign, when it began, appetite, droppings, urine, breathing, posture, pain signs, recent surgery, heat exposure, trauma, and any possible toxin or medication exposure.",
            ),
            (
                "Should I use a product or home treatment first?",
                "No. Products, food changes, supplements, and home care should only be discussed after a veterinarian has assessed the emergency risk. They are not substitutes for urgent veterinary care.",
            ),
        ],
    },
    "ja": {
        "prefix": "ja",
        "home": "ホーム",
        "faq_heading": "救急FAQ",
        "prep_heading": "電話または移動前の準備",
        "prep_body": [
            "症状が始まった正確な時間、最後に普通に食べた時間、最後の正常な便、尿が出ているかをメモしてください。これらの情報は、病院が緊急度や到着時に必要な準備を判断する助けになります。",
            "便、尿、傷、分泌物、食べた可能性がある物の包装、姿勢が分かる写真を撮ってください。保温や冷却は問題に合う範囲で穏やかに行い、入浴、強制給餌、人間用の薬、以前の薬は、この症状について獣医師から指示がない限り使わないでください。",
            "安全なキャリーにタオルを敷き、移動準備をしながら電話してください。今うさぎまたはエキゾチックに対応できる獣医師がいるか、すぐ向かうべきか、何を持参すべきかを確認します。",
        ],
        "faq": [
            (
                "明日まで待ってもよいですか？",
                "食べない、便が出ない、弱っている、倒れる、呼吸がおかしい、出血、腹部膨満、中毒の疑い、急な悪化がある場合は一晩待たないでください。移動準備をしながら、うさぎ対応またはエキゾチック対応の病院へ電話してください。",
            ),
            (
                "病院へ最初に何を伝えますか？",
                "主な症状、始まった時間、食欲、便、尿、呼吸、姿勢、痛みのサイン、最近の手術、暑さ、外傷、中毒や薬の可能性を順番に伝えてください。",
            ),
            (
                "先に製品や家庭での処置を使うべきですか？",
                "いいえ。製品、食事変更、サプリメント、家庭でのケアは、緊急リスクを獣医師が評価した後に相談するものです。緊急診療の代わりにはなりません。",
            ),
        ],
    },
    "zh-tw": {
        "prefix": "zh-tw",
        "home": "首頁",
        "faq_heading": "急症FAQ",
        "prep_heading": "致電或出發前的準備",
        "prep_body": [
            "記下症狀開始的確切時間、最後一次正常進食、最後一次正常便便，以及是否有尿。這些資訊能幫助診所判斷緊急程度，以及你到達時可能需要哪些設備或人員。",
            "拍下便便、尿液、傷口、分泌物、可能吃下物品的包裝，以及兔子的姿勢。保暖或降溫只能以溫和方式進行，並符合目前問題；不要洗澡、強迫餵食、使用人用藥或舊藥，除非獸醫針對這次狀況指示。",
            "使用安全外出籠並鋪毛巾，一邊準備出門一邊致電。詢問當下是否有熟悉兔子或特殊寵物的獸醫值班、是否應立即前往，以及需要攜帶什麼。",
        ],
        "faq": [
            (
                "可以等到明天嗎？",
                "若兔子不進食、沒有便便、虛弱、倒下、呼吸異常、出血、腹部脹硬、疑似中毒或快速惡化，不要等過夜。請一邊準備出門一邊致電能處理兔子或特殊寵物的獸醫。",
            ),
            (
                "打給診所時先說什麼？",
                "先說主要症狀、何時開始、食慾、便便、尿液、呼吸、姿勢、疼痛表現、近期手術、熱暴露、外傷，以及任何可能的毒物或藥物接觸。",
            ),
            (
                "應先用產品或家庭處置嗎？",
                "不要。產品、飲食改變、補充品和居家照護，都應在獸醫評估急症風險後再討論。它們不能取代緊急獸醫照護。",
            ),
        ],
    },
    "th": {
        "prefix": "th",
        "home": "หน้าแรก",
        "faq_heading": "FAQ ฉุกเฉิน",
        "prep_heading": "ก่อนโทรหรือออกเดินทาง",
        "prep_body": [
            "จดเวลาที่อาการเริ่มขึ้นอย่างชัดเจน มื้ออาหารปกติครั้งล่าสุด อุจจาระปกติครั้งล่าสุด และกระต่ายปัสสาวะหรือไม่ ข้อมูลเหล่านี้ช่วยให้คลินิกประเมินความเร่งด่วนและเตรียมทีมเมื่อคุณไปถึง",
            "ถ่ายรูปอุจจาระ ปัสสาวะ แผล สิ่งคัดหลั่ง บรรจุภัณฑ์ของสิ่งที่อาจกินเข้าไป และท่าทางของกระต่าย รักษาอุณหภูมิอย่างนุ่มนวลตามปัญหาเท่านั้น และหลีกเลี่ยงการอาบน้ำ การป้อนบังคับ ยาคน หรือยาเก่า เว้นแต่สัตวแพทย์สั่งสำหรับเหตุการณ์นี้",
            "ใช้กรงเดินทางที่มั่นคงพร้อมผ้ารอง และโทรขณะเตรียมเดินทาง ถามว่ามีสัตวแพทย์ที่ดูแลกระต่ายหรือสัตว์พิเศษอยู่ตอนนี้หรือไม่ ควรไปทันทีไหม และต้องนำอะไรไปด้วย",
        ],
        "faq": [
            (
                "รอถึงพรุ่งนี้ได้ไหม",
                "อย่ารอข้ามคืนถ้ากระต่ายไม่กิน ไม่ถ่าย อ่อนแรง ล้ม หายใจผิดปกติ เลือดออก ท้องอืด สัมผัสสารพิษ หรืออาการแย่ลงเร็ว ให้โทรหาคลินิกที่ดูแลกระต่ายหรือสัตว์พิเศษได้ขณะเตรียมเดินทาง",
            ),
            (
                "ควรบอกคลินิกอะไรก่อน",
                "เริ่มจากอาการหลัก เวลาเริ่ม กินอาหาร อุจจาระ ปัสสาวะ การหายใจ ท่าทาง สัญญาณปวด การผ่าตัดล่าสุด ความร้อน บาดเจ็บ และสิ่งที่อาจเป็นพิษหรือยา",
            ),
            (
                "ควรใช้ผลิตภัณฑ์หรือดูแลเองก่อนไหม",
                "ไม่ควร ผลิตภัณฑ์ การเปลี่ยนอาหาร อาหารเสริม และการดูแลที่บ้านควรคุยหลังสัตวแพทย์ประเมินความเสี่ยงฉุกเฉินแล้วเท่านั้น ไม่ใช่สิ่งทดแทนการรักษาฉุกเฉิน",
            ),
        ],
    },
}


def locale_for(path: Path) -> str:
    rel = path.relative_to(ROOT)
    return rel.parts[0] if rel.parts and rel.parts[0] in {"ja", "zh-tw", "th"} else "en"


def page_url(path: Path) -> str:
    rel = path.relative_to(ROOT)
    if rel == Path("index.html"):
        return f"{BASE}/"
    return f"{BASE}/{'/'.join(rel.parts[:-1])}/"


def title_for(html: str) -> str:
    match = re.search(r"<title>(.*?)</title>", html, flags=re.I | re.S)
    if match:
        return unescape(re.sub(r"\s+", " ", match.group(1))).strip()
    match = re.search(r"<h1[^>]*>(.*?)</h1>", html, flags=re.I | re.S)
    if match:
        return unescape(re.sub(r"<[^>]+>", " ", match.group(1))).strip()
    return "RabbitEmergency.com"


def description_for(html: str) -> str:
    patterns = [
        r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']*)["\']',
        r'<meta[^>]+content=["\']([^"\']*)["\'][^>]+name=["\']description["\']',
    ]
    for pattern in patterns:
        match = re.search(pattern, html, flags=re.I)
        if match:
            return unescape(match.group(1)).strip()
    return "Rabbit emergency guidance for deciding when to call or travel to a rabbit-savvy veterinarian."


def ld_blocks(html: str) -> list[object]:
    objects = []
    for raw in re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, flags=re.S):
        try:
            objects.append(json.loads(raw))
        except json.JSONDecodeError:
            pass
    return objects


def has_type(obj: object, schema_type: str) -> bool:
    if isinstance(obj, dict):
        typ = obj.get("@type")
        if typ == schema_type or (isinstance(typ, list) and schema_type in typ):
            return True
    return False


def update_ld_review(obj: object) -> object:
    return scrub_review_schema(obj)


def update_json_ld_review(html: str) -> str:
    def repl(match: re.Match) -> str:
        raw = match.group(1)
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            return match.group(0)
        data = update_ld_review(data)
        return '<script type="application/ld+json">' + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + "</script>"

    return re.sub(r'<script type="application/ld\+json">(.*?)</script>', repl, html, flags=re.S)


def has_schema(html: str, schema_type: str) -> bool:
    return schema_type in [typ for obj in ld_blocks(html) for typ in ld_types(obj)]


def insert_before_review_or_main(html: str, block: str) -> str:
    review = re.search(r'<p class="reviewed">', html)
    if review:
        return html[: review.start()] + block + html[review.start() :]
    if "</main>" in html:
        return html.replace("</main>", block + "</main>", 1)
    return html + block


def faq_block(locale: str) -> str:
    data = LOCALES[locale]
    details = "".join(
        f"<details><summary>{escape(question)}</summary><p>{escape(answer)}</p></details>"
        for question, answer in data["faq"]
    )
    return f'<section id="quality-faq"><h2>{escape(data["faq_heading"])}</h2>{details}</section>'


def prep_block(locale: str) -> str:
    data = LOCALES[locale]
    paras = "".join(f"<p>{escape(paragraph)}</p>" for paragraph in data["prep_body"])
    return f'<section id="vet-call-prep"><h2>{escape(data["prep_heading"])}</h2>{paras}</section>'


def faq_schema(locale: str) -> dict:
    return {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": question,
                "acceptedAnswer": {"@type": "Answer", "text": answer},
            }
            for question, answer in LOCALES[locale]["faq"]
        ],
    }


def breadcrumb_schema(path: Path, html: str, locale: str) -> dict:
    data = LOCALES[locale]
    home = f"{BASE}/{data['prefix']}/" if data["prefix"] else f"{BASE}/"
    crumb_links = re.findall(r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>(.*?)</a>', html, flags=re.I | re.S)
    items = [{"@type": "ListItem", "position": 1, "name": data["home"], "item": home}]
    for href, label in crumb_links[:3]:
        if not href.startswith("/"):
            continue
        clean_label = unescape(re.sub(r"<[^>]+>", " ", label)).strip()
        if not clean_label or clean_label.lower() == data["home"].lower():
            continue
        item_url = f"{BASE}{href if href.endswith('/') else href + '/'}"
        if item_url == home or item_url == page_url(path):
            continue
        items.append({"@type": "ListItem", "position": len(items) + 1, "name": clean_label, "item": item_url})
        if len(items) >= 3:
            break
    items.append({"@type": "ListItem", "position": len(items) + 1, "name": title_for(html), "item": page_url(path)})
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": items}


def add_schema(html: str, schema: dict) -> str:
    block = '<script type="application/ld+json">' + json.dumps(schema, ensure_ascii=False, separators=(",", ":")) + "</script>"
    if "</head>" in html:
        return html.replace("</head>", block + "</head>", 1)
    return block + html


def medical_schema(path: Path, html: str, locale: str) -> dict:
    return {
        "@context": "https://schema.org",
        "@type": "MedicalWebPage",
        "name": title_for(html),
        "description": description_for(html),
        "url": page_url(path),
        "inLanguage": "zh-tw" if locale == "zh-tw" else locale,
        "publisher": {"@type": "Organization", "name": "RabbitEmergency.com", "url": f"{BASE}/"},
    }


def ensure_visible_review(html: str) -> str:
    html = re.sub(
        r'<p class="reviewed">.*?(?:pending named veterinary review|source-cited and pending named veterinary review|source-cited, pending named veterinary review).*?</p>',
        f'<p class="reviewed">{VISIBLE_REVIEW}</p>',
        html,
        flags=re.I | re.S,
    )
    text = visible_text(html).lower()
    if "/veterinary-review/" in html and "veterinary review pending" in text:
        return html
    return insert_before_review_or_main(html, f'<p class="reviewed">{VISIBLE_REVIEW}</p>')


def repair_page(path: Path) -> bool:
    html = path.read_text(encoding="utf-8", errors="replace")
    original = html
    if 'http-equiv="refresh"' in html and "noindex" in html.lower() and len(html) < 2500:
        return False
    kind = page_kind(path, html)
    if kind not in {"medical", "emergency", "hub"}:
        return False

    locale = locale_for(path)

    html = update_json_ld_review(html)

    if not has_schema(html, "MedicalWebPage"):
        html = add_schema(html, medical_schema(path, html, locale))

    html = ensure_visible_review(html)

    if not has_schema(html, "FAQPage"):
        if 'id="quality-faq"' not in html and 'id="faq"' not in html:
            html = insert_before_review_or_main(html, faq_block(locale))
        html = add_schema(html, faq_schema(locale))

    if not has_schema(html, "BreadcrumbList"):
        html = add_schema(html, breadcrumb_schema(path, html, locale))

    if kind == "emergency" and content_word_count(visible_text(html), path) < 600 and 'id="vet-call-prep"' not in html:
        html = insert_before_review_or_main(html, prep_block(locale))

    if html != original:
        path.write_text(sanitize_html(html, path), encoding="utf-8")
        return True
    return False


def update_sitemap() -> None:
    urls = []
    for path in sorted(ROOT.glob("**/index.html")):
        if ".git" in path.parts:
            continue
        html = path.read_text(encoding="utf-8", errors="replace")
        if 'http-equiv="refresh"' in html and "noindex" in html.lower() and len(html) < 2500:
            continue
        urls.append(page_url(path))
    body = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for url in sorted(set(urls)):
        priority = "1.0" if url == f"{BASE}/" else ("0.9" if "emergency" in url else "0.8")
        changefreq = "weekly" if url == f"{BASE}/" else "monthly"
        body.append(f"<url><loc>{url}</loc><lastmod>{LAST_REVIEWED}</lastmod><changefreq>{changefreq}</changefreq><priority>{priority}</priority></url>")
    body.append("</urlset>\n")
    (ROOT / "sitemap.xml").write_text("".join(body), encoding="utf-8")


def repair_reviewer_pages() -> int:
    changed = 0
    language_links = (
        '<p>Read in: <a href="/veterinary-review/">English</a> · '
        '<a href="/ja/veterinary-review/">日本語</a> · '
        '<a href="/zh-tw/veterinary-review/">繁體中文</a> · '
        '<a href="/th/veterinary-review/">ไทย</a></p>'
    )
    for rel in (
        "veterinary-review/index.html",
        "ja/veterinary-review/index.html",
        "zh-tw/veterinary-review/index.html",
        "th/veterinary-review/index.html",
    ):
        path = ROOT / rel
        if not path.exists():
            continue
        html = path.read_text(encoding="utf-8", errors="replace")
        original = html
        html = re.sub(r"<p>Read in: .*?</p>", language_links, html, count=1, flags=re.S)
        html = html.replace('href="/ja//"', 'href="/ja/"')
        html = html.replace('href="/zh-tw//"', 'href="/zh-tw/"')
        html = html.replace('href="/th//"', 'href="/th/"')
        if html != original:
            path.write_text(sanitize_html(html, path), encoding="utf-8")
            changed += 1
    return changed


def main() -> None:
    changed = 0
    for path in sorted(ROOT.glob("**/index.html")):
        if ".git" in path.parts:
            continue
        if repair_page(path):
            changed += 1
    changed += repair_reviewer_pages()
    update_sitemap()
    print(f"content quality pages changed: {changed}")


if __name__ == "__main__":
    main()
