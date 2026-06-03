from html import escape
from pathlib import Path
from datetime import date
import json
import re

ROOT = Path(__file__).parent
BASE = "https://rabbitemergency.com"
LASTMOD = date.today().isoformat()
REVIEW = "Veterinary review: pending. Add real reviewer name, credentials, affiliation, and review date before making a reviewed-by claim."
UNVERIFIED_REVIEWER_PATTERNS = (
    "veterinary-reviewers",
    "Dr. Apinya",
    "Dr. Kenji",
    "Dr. Sarah Lim",
    "Dr. Wei-Chen",
    "exotic veterinary advisory board",
)

LOCALES = {
    "en": {
        "prefix": "",
        "lang": "en",
        "hreflang": "en",
        "label": "English",
        "brand_tail": "rabbit-first emergency care",
        "home": "Home",
        "signs": "Signs",
        "not_eating": "Not eating",
        "heatstroke": "Heatstroke",
        "head_tilt": "Head tilt",
        "find_vet": "Find a vet",
        "hub_label": "Rabbit emergency signs",
        "guide_label": "Rabbit emergency sign guide",
        "hub_eyebrow": "Rabbit emergency signs hub",
        "hub_title": "Rabbit Emergency Signs: 100 Warning Signs and When to Go Now",
        "hub_meta": "A rabbit emergency signs hub with 100 sign-specific triage pages for not eating, no droppings, bloat, heatstroke, head tilt, flystrike, breathing trouble, trauma, pain, toxins, and more.",
        "hub_lede": "If a rabbit stops eating, stops pooping, breathes abnormally, collapses, overheats, has flystrike, shows severe pain, or has a bloated belly, treat it as urgent and call a rabbit-savvy vet.",
        "hub_answer": "Rabbits hide illness and can deteriorate fast. Use these 100 sign-specific pages to describe what you see, choose an urgency tier, and prepare the clinic call. Do not use supplements or recovery products instead of veterinary assessment.",
        "hub_cards": "100 rabbit emergency sign guides",
        "go_now_signs": "Go now signs",
        "go_now_bullets": [
            "No eating or no droppings for 6-12 hours.",
            "Hard or swollen belly, collapse, cold body, severe lethargy, or loud tooth grinding.",
            "Open-mouth breathing, blue lips, heatstroke, seizure, flystrike, severe bleeding, or trauma.",
            "Baby rabbit diarrhea, birth trouble, toxin exposure, or post-op not eating.",
        ],
        "title_pattern": "Rabbit {sign}: is this an emergency?",
        "meta_pattern": "Rabbit {sign} emergency triage: go-now signs, when to call today, what not to do, and what to tell a rabbit-savvy vet.",
        "lede": "Use this page to decide whether to go now, call today, or monitor only under veterinary guidance. It is not a diagnosis.",
        "disclaimer": "This page is not a substitute for a veterinarian. Rabbits can decline quickly. If your rabbit has go-now signs, call a rabbit-savvy or exotic vet while preparing to travel.",
        "short_answer": "Short answer",
        "product_warning": "Do not use online triage, RodiCare, WOOLY, food, supplements, or home remedies as a replacement for assessment when a rabbit may be in trouble.",
        "decision_table": "Emergency decision table",
        "tier": "Tier",
        "what_it_means": "What it means for rabbit {sign}",
        "action": "Action",
        "go_now": "Go now",
        "call_today": "Call today",
        "monitor": "Monitor with vet guidance",
        "go_action": "Call an emergency rabbit-savvy vet and travel when advised.",
        "call_meaning": "The sign is new, persistent, worsening, or paired with appetite, droppings, behavior, breathing, movement, urine, or pain changes.",
        "call_action": "Call your rabbit-savvy vet or an exotic-capable clinic today.",
        "monitor_meaning": "A vet has already assessed this episode and gave a specific monitoring plan.",
        "monitor_action": "Follow that plan and call back if anything worsens.",
        "go_now_if": "Go now if",
        "go_now_if_bullets": [
            "Not eating, no droppings, collapse, cold body, heatstroke signs, breathing trouble, seizures, flystrike, severe bleeding, bloated belly, or severe pain appear.",
            "The sign follows trauma, toxin exposure, surgery, birth trouble, or a known chronic illness.",
            "Your rabbit is a baby, senior, pregnant, very weak, or cannot stay upright.",
        ],
        "call_today_if": "Call today if",
        "call_today_bullets": [
            "The sign is mild but new or persistent.",
            "Droppings, appetite, water intake, urine, posture, or movement changed.",
            "You are considering any medication, force-feeding, supplement, or recovery product.",
        ],
        "what_not": "What not to do",
        "what_not_bullets": [
            "Do not force-feed a rabbit with a bloated belly, choking signs, severe weakness, or suspected blockage unless a vet instructs you.",
            "Do not give human medicine, leftover medication, gut stimulants, or pain relief unless prescribed for this episode.",
            "Do not wait overnight for go-now signs.",
        ],
        "tell_vet": "What to tell the vet",
        "tell_vet_bullets": [
            "When rabbit {sign} started and whether it is worsening.",
            "Last normal food, water, urine, and droppings.",
            "Posture, tooth grinding, belly feel, breathing, temperature, movement, and pain signs.",
            "Recent diet changes, heat, stress, moult, surgery, trauma, toxins, or medications.",
        ],
        "review_status": "Review status",
        "sources": "Sources & standards",
        "helpful": "Helpful next pages",
        "footer": "RabbitEmergency.com is an educational resource and does not provide veterinary diagnosis or treatment. In an emergency, contact a rabbit-savvy veterinarian immediately.",
        "review": REVIEW,
        "related": [
            ("Rabbit emergency signs hub", "/rabbit-emergency-signs/"),
            ("Rabbit not eating or pooping", "/rabbit-not-eating-or-pooping/"),
            ("Rabbit bloat / hard belly", "/rabbit-bloat-hard-belly/"),
            ("Find a rabbit emergency vet", "/rabbit-emergency-vet-hong-kong/"),
        ],
    },
    "ja": {
        "prefix": "ja",
        "lang": "ja",
        "hreflang": "ja",
        "label": "日本語",
        "brand_tail": "うさぎ優先の救急ケア",
        "home": "ホーム",
        "signs": "症状",
        "not_eating": "食べない",
        "heatstroke": "熱中症",
        "head_tilt": "斜頸",
        "find_vet": "獣医を探す",
        "hub_label": "うさぎの救急サイン",
        "guide_label": "うさぎ救急サインガイド",
        "hub_eyebrow": "うさぎ救急サイン集",
        "hub_title": "うさぎの救急サイン: 今すぐ受診すべき100の警告",
        "hub_meta": "食べない、便が出ない、膨満、熱中症、斜頸、ハエウジ症、呼吸異常、外傷、痛み、中毒など、100のうさぎ救急サイン別トリアージページ。",
        "hub_lede": "うさぎが食べない、便が出ない、呼吸がおかしい、倒れる、暑さでぐったりする、ハエウジ症、強い痛み、腹部膨満がある場合は緊急と考え、うさぎに詳しい獣医へ連絡してください。",
        "hub_answer": "うさぎは不調を隠し、急速に悪化することがあります。100のサイン別ページで見えている症状を整理し、緊急度を判断し、病院への電話に備えてください。サプリメントや回復補助品を診察の代わりにしないでください。",
        "hub_cards": "100のうさぎ救急サインガイド",
        "go_now_signs": "今すぐ受診すべきサイン",
        "go_now_bullets": [
            "6-12時間食べない、または便が出ない。",
            "硬い・腫れたお腹、倒れる、体が冷たい、強い元気消失、大きな歯ぎしり。",
            "口を開けた呼吸、青い唇、熱中症、発作、ハエウジ症、重い出血、外傷。",
            "子うさぎの下痢、出産トラブル、中毒、術後に食べない。",
        ],
        "title_pattern": "うさぎの{sign}: これは緊急ですか？",
        "meta_pattern": "うさぎの{sign}の救急トリアージ。今すぐ受診すべきサイン、本日中に連絡する目安、してはいけないこと、獣医へ伝える内容。",
        "lede": "今すぐ受診、本日中の相談、または獣医の指示下での観察かを判断するためのページです。診断ではありません。",
        "disclaimer": "このページは獣医師の代わりではありません。うさぎは急速に悪化することがあります。緊急サインがある場合は、移動準備をしながらうさぎに詳しい獣医またはエキゾチック対応病院へ連絡してください。",
        "short_answer": "短い答え",
        "product_warning": "オンラインの情報、RodiCare、WOOLY、食べ物、サプリメント、家庭療法を、異変があるうさぎの診察の代わりにしないでください。",
        "decision_table": "緊急度の判断表",
        "tier": "緊急度",
        "what_it_means": "うさぎの{sign}で見るポイント",
        "action": "行動",
        "go_now": "今すぐ",
        "call_today": "本日中に相談",
        "monitor": "獣医の指示で観察",
        "go_action": "うさぎ対応の救急獣医へ電話し、指示があれば受診してください。",
        "call_meaning": "新しい症状、続く症状、悪化する症状、または食欲・便・行動・呼吸・動き・尿・痛みの変化を伴う状態。",
        "call_action": "本日中にうさぎに詳しい獣医またはエキゾチック対応病院へ連絡してください。",
        "monitor_meaning": "この症状についてすでに獣医が診察し、具体的な観察計画を出している状態。",
        "monitor_action": "その計画に従い、悪化があればすぐ再連絡してください。",
        "go_now_if": "今すぐ受診する場合",
        "call_today_if": "本日中に相談する場合",
        "what_not": "してはいけないこと",
        "tell_vet": "獣医へ伝えること",
        "review_status": "レビュー状況",
        "sources": "出典と基準",
        "helpful": "関連ページ",
        "footer": "RabbitEmergency.comは教育目的の情報サイトであり、獣医師による診断や治療を提供するものではありません。緊急時はすぐにうさぎに詳しい獣医へ連絡してください。",
        "review": "獣医レビュー: 保留中。レビュー済みと表示する前に、実在するレビュアー名、資格、所属、レビュー日を追加してください。",
    },
    "zh-tw": {
        "prefix": "zh-tw",
        "lang": "zh-tw",
        "hreflang": "zh-Hant",
        "label": "繁體中文",
        "brand_tail": "兔子優先急症照護",
        "home": "首頁",
        "signs": "症狀",
        "not_eating": "不進食",
        "heatstroke": "中暑",
        "head_tilt": "歪頭",
        "find_vet": "找獸醫",
        "hub_label": "兔子急症警訊",
        "guide_label": "兔子急症警訊指南",
        "hub_eyebrow": "兔子急症警訊中心",
        "hub_title": "兔子急症警訊：100個需要立即就醫的警告",
        "hub_meta": "100個兔子急症警訊分頁，涵蓋不進食、無便便、脹氣、中暑、歪頭、蠅蛆症、呼吸困難、外傷、疼痛、中毒等。",
        "hub_lede": "如果兔子停止進食、沒有便便、呼吸異常、倒下、過熱、出現蠅蛆症、劇烈疼痛或腹部脹硬，請視為緊急並聯絡熟悉兔子的獸醫。",
        "hub_answer": "兔子會隱藏病痛，而且可能快速惡化。使用這100個症狀分頁描述你看到的狀況、判斷緊急程度，並準備打給診所。不要用補充品或復原產品取代獸醫評估。",
        "hub_cards": "100個兔子急症警訊指南",
        "go_now_signs": "需要立即就醫的警訊",
        "go_now_bullets": [
            "6-12小時不進食或沒有便便。",
            "腹部硬或腫脹、倒下、身體冰冷、嚴重嗜睡、明顯磨牙。",
            "張口呼吸、嘴唇發藍、中暑、癲癇、蠅蛆症、嚴重出血或外傷。",
            "幼兔腹瀉、生產困難、中毒暴露或術後不進食。",
        ],
        "title_pattern": "兔子{sign}：這是急症嗎？",
        "meta_pattern": "兔子{sign}急症分流：何時立即就醫、何時今天致電獸醫、不要做什麼，以及要告訴熟悉兔子的獸醫哪些資訊。",
        "lede": "用這頁判斷應立即就醫、今天致電，或只在獸醫指示下觀察。這不是診斷。",
        "disclaimer": "此頁不能取代獸醫。兔子可能快速惡化。若有立即就醫警訊，請一邊準備出門一邊致電熟悉兔子或特殊寵物的獸醫。",
        "short_answer": "簡短答案",
        "product_warning": "不要把網路分流、RodiCare、WOOLY、食物、補充品或家庭處置當成獸醫評估的替代品。",
        "decision_table": "急症判斷表",
        "tier": "等級",
        "what_it_means": "兔子{sign}代表什麼",
        "action": "行動",
        "go_now": "立即就醫",
        "call_today": "今天致電",
        "monitor": "依獸醫指示觀察",
        "go_action": "致電可看兔子的急症獸醫，並依指示前往。",
        "call_meaning": "症狀是新的、持續、惡化，或伴隨食慾、便便、行為、呼吸、活動、尿液或疼痛變化。",
        "call_action": "今天致電熟悉兔子的獸醫或可看特殊寵物的診所。",
        "monitor_meaning": "獸醫已評估這次狀況，並提供明確觀察計畫。",
        "monitor_action": "依照計畫，若惡化立即回電。",
        "go_now_if": "符合以下情況請立即就醫",
        "call_today_if": "符合以下情況請今天致電",
        "what_not": "不要做什麼",
        "tell_vet": "告訴獸醫的資訊",
        "review_status": "審閱狀態",
        "sources": "來源與標準",
        "helpful": "相關頁面",
        "footer": "RabbitEmergency.com是教育資源，不提供獸醫診斷或治療。緊急時請立即聯絡熟悉兔子的獸醫。",
        "review": "獸醫審閱：待定。在聲稱已由獸醫審閱前，需加入真實審閱者姓名、資格、所屬機構與審閱日期。",
    },
    "th": {
        "prefix": "th",
        "lang": "th",
        "hreflang": "th",
        "label": "ไทย",
        "brand_tail": "การดูแลฉุกเฉินสำหรับกระต่าย",
        "home": "หน้าแรก",
        "signs": "อาการ",
        "not_eating": "ไม่กินอาหาร",
        "heatstroke": "ฮีตสโตรก",
        "head_tilt": "หัวเอียง",
        "find_vet": "หาสัตวแพทย์",
        "hub_label": "สัญญาณฉุกเฉินของกระต่าย",
        "guide_label": "คู่มือสัญญาณฉุกเฉินของกระต่าย",
        "hub_eyebrow": "ศูนย์รวมสัญญาณฉุกเฉินของกระต่าย",
        "hub_title": "สัญญาณฉุกเฉินของกระต่าย: 100 อาการเตือนที่ควรไปพบสัตวแพทย์ทันที",
        "hub_meta": "หน้าคัดกรองสัญญาณฉุกเฉินของกระต่าย 100 รายการ ครอบคลุมไม่กินอาหาร ไม่ถ่าย ท้องอืด ฮีตสโตรก หัวเอียง หนอนแมลงวัน หายใจผิดปกติ บาดเจ็บ ปวด และพิษ",
        "hub_lede": "ถ้ากระต่ายหยุดกิน ไม่ถ่าย หายใจผิดปกติ ล้ม ร้อนเกิน มีหนอนแมลงวัน เจ็บมาก หรือท้องแข็งบวม ให้ถือว่าเร่งด่วนและโทรหาสัตวแพทย์ที่ดูแลกระต่ายได้",
        "hub_answer": "กระต่ายมักซ่อนอาการป่วยและอาจแย่ลงเร็ว ใช้หน้าอาการทั้ง 100 หน้าเพื่ออธิบายสิ่งที่เห็น เลือกระดับความเร่งด่วน และเตรียมข้อมูลสำหรับโทรหาคลินิก อย่าใช้ผลิตภัณฑ์เสริมหรือการดูแลฟื้นตัวแทนการประเมินของสัตวแพทย์",
        "hub_cards": "คู่มือสัญญาณฉุกเฉินของกระต่าย 100 รายการ",
        "go_now_signs": "สัญญาณที่ควรไปทันที",
        "go_now_bullets": [
            "ไม่กินอาหารหรือไม่ถ่ายนาน 6-12 ชั่วโมง",
            "ท้องแข็งหรือบวม ล้ม ตัวเย็น ซึมมาก หรือกัดฟันเสียงดัง",
            "อ้าปากหายใจ ริมฝีปากเขียว ฮีตสโตรก ชัก หนอนแมลงวัน เลือดออกมาก หรือบาดเจ็บ",
            "ลูกกระต่ายท้องเสีย คลอดผิดปกติ สัมผัสสารพิษ หรือหลังผ่าตัดแล้วไม่กิน",
        ],
        "title_pattern": "กระต่าย{sign}: เป็นเหตุฉุกเฉินไหม?",
        "meta_pattern": "การคัดกรองฉุกเฉินเมื่อกระต่าย{sign}: สัญญาณที่ควรไปทันที เมื่อใดควรโทรวันนี้ สิ่งที่ไม่ควรทำ และข้อมูลที่ควรบอกสัตวแพทย์",
        "lede": "ใช้หน้านี้เพื่อช่วยตัดสินใจว่าควรไปทันที โทรวันนี้ หรือเฝ้าดูตามคำแนะนำของสัตวแพทย์เท่านั้น ไม่ใช่การวินิจฉัย",
        "disclaimer": "หน้านี้ไม่สามารถแทนสัตวแพทย์ได้ กระต่ายอาจทรุดเร็ว หากมีสัญญาณฉุกเฉิน ให้โทรหาสัตวแพทย์ที่ดูแลกระต่ายหรือสัตว์พิเศษได้ขณะเตรียมเดินทาง",
        "short_answer": "คำตอบสั้น",
        "product_warning": "อย่าใช้การคัดกรองออนไลน์ RodiCare, WOOLY, อาหาร อาหารเสริม หรือการดูแลที่บ้านแทนการประเมินของสัตวแพทย์เมื่อกระต่ายอาจมีปัญหา",
        "decision_table": "ตารางตัดสินใจฉุกเฉิน",
        "tier": "ระดับ",
        "what_it_means": "ความหมายเมื่อกระต่าย{sign}",
        "action": "การทำทันที",
        "go_now": "ไปทันที",
        "call_today": "โทรวันนี้",
        "monitor": "เฝ้าดูตามคำแนะนำสัตวแพทย์",
        "go_action": "โทรหาสัตวแพทย์ฉุกเฉินที่ดูแลกระต่ายได้ และเดินทางเมื่อได้รับคำแนะนำ",
        "call_meaning": "อาการเป็นใหม่ เป็นต่อเนื่อง แย่ลง หรือมีการเปลี่ยนแปลงเรื่องการกิน อุจจาระ พฤติกรรม การหายใจ การเคลื่อนไหว ปัสสาวะ หรือความเจ็บปวด",
        "call_action": "โทรหาสัตวแพทย์ที่ดูแลกระต่ายหรือคลินิกสัตว์พิเศษภายในวันนี้",
        "monitor_meaning": "สัตวแพทย์ประเมินเหตุการณ์นี้แล้วและให้แผนเฝ้าดูเฉพาะไว้",
        "monitor_action": "ทำตามแผน และโทรกลับถ้าอาการแย่ลง",
        "go_now_if": "ไปทันทีถ้า",
        "call_today_if": "โทรวันนี้ถ้า",
        "what_not": "สิ่งที่ไม่ควรทำ",
        "tell_vet": "สิ่งที่ควรบอกสัตวแพทย์",
        "review_status": "สถานะการตรวจทาน",
        "sources": "แหล่งข้อมูลและมาตรฐาน",
        "helpful": "หน้าที่เกี่ยวข้อง",
        "footer": "RabbitEmergency.comเป็นแหล่งข้อมูลเพื่อการศึกษา ไม่ได้ให้การวินิจฉัยหรือรักษาโดยสัตวแพทย์ หากฉุกเฉินให้ติดต่อสัตวแพทย์ที่ดูแลกระต่ายได้ทันที",
        "review": "การตรวจทานโดยสัตวแพทย์: รอดำเนินการ ต้องเพิ่มชื่อผู้ตรวจทานจริง คุณวุฒิ สังกัด และวันที่ตรวจทานก่อนอ้างว่าได้รับการตรวจทานแล้ว",
    },
}

PHRASE_REPLACEMENTS = {
    "ja": [
        ("not eating", "食べない"),
        ("not pooping", "便が出ない"),
        ("small droppings", "便が小さい"),
        ("watery diarrhea", "水様性下痢"),
        ("bloated belly", "お腹が膨れている"),
        ("belly pressed to floor", "お腹を床につける"),
        ("hunched posture", "背中を丸める"),
        ("loud tooth grinding", "大きな歯ぎしり"),
        ("lethargic", "ぐったりしている"),
        ("not moving", "動かない"),
        ("floppy", "力が抜けている"),
        ("collapsed", "倒れている"),
        ("cold ears", "耳が冷たい"),
        ("cold body", "体が冷たい"),
        ("heatstroke", "熱中症"),
        ("overheated", "暑さでぐったり"),
        ("panting", "パンティング"),
        ("difficulty breathing", "呼吸困難"),
        ("mouth breathing", "口呼吸"),
        ("blue lips", "唇が青い"),
        ("noisy breathing", "呼吸音が大きい"),
        ("sneezing with discharge", "鼻水を伴うくしゃみ"),
        ("runny nose", "鼻水"),
        ("choking", "窒息の疑い"),
        ("gagging", "えずく"),
        ("drooling", "よだれ"),
        ("wet chin", "あごが濡れている"),
        ("dropping food", "食べ物を落とす"),
        ("overgrown teeth", "歯の伸びすぎ"),
        ("face swelling", "顔の腫れ"),
        ("eye discharge", "目やに"),
        ("squinting eye", "目を細める"),
        ("cloudy eye", "目が濁る"),
        ("eye injury", "目のけが"),
        ("head tilt", "斜頸"),
        ("rolling", "転がる"),
        ("loss of balance", "バランス喪失"),
        ("seizure", "発作"),
        ("trembling", "震え"),
        ("back legs weak", "後ろ足が弱い"),
        ("dragging back legs", "後ろ足を引きずる"),
        ("paralysis", "麻痺"),
        ("limping", "足を引きずる"),
        ("fall", "落下"),
        ("dropped", "落とされた"),
        ("bleeding", "出血"),
        ("broken nail", "爪が折れた"),
        ("open wound", "開いた傷"),
        ("bite wound", "咬み傷"),
        ("abscess", "膿瘍"),
        ("sore hocks", "ソアホック"),
        ("flystrike", "ハエウジ症"),
        ("dirty bottom", "お尻が汚い"),
        ("maggots", "ウジ"),
        ("urine scald", "尿やけ"),
        ("straining to urinate", "排尿時にいきむ"),
        ("not peeing", "尿が出ない"),
        ("blood in urine", "血尿"),
        ("red urine", "赤い尿"),
        ("sludgy urine", "泥状尿"),
        ("not drinking", "水を飲まない"),
        ("dehydrated", "脱水"),
        ("weight loss", "体重減少"),
        ("hiding", "隠れる"),
        ("sudden behavior change", "急な行動変化"),
        ("screaming", "悲鳴"),
        ("grinding teeth", "歯ぎしり"),
        ("shaking head", "頭を振る"),
        ("ear scratching", "耳をかく"),
        ("ear discharge", "耳だれ"),
        ("toxic plant exposure", "有毒植物の摂取疑い"),
        ("ate chocolate", "チョコレートを食べた"),
        ("ate human medicine", "人間の薬を食べた"),
        ("ate rodenticide", "殺鼠剤を食べた"),
        ("ate onion or garlic", "玉ねぎやニンニクを食べた"),
        ("ate houseplant", "観葉植物を食べた"),
        ("ate carpet or fabric", "カーペットや布を食べた"),
        ("ate plastic", "プラスチックを食べた"),
        ("hair in gut", "胃腸内の毛"),
        ("moulting and not eating", "換毛中に食べない"),
        ("not eating after surgery", "術後に食べない"),
        ("not pooping after surgery", "術後に便が出ない"),
        ("swollen incision", "切開部の腫れ"),
        ("not eating after vet visit", "通院後に食べない"),
        ("baby rabbit not eating", "子うさぎが食べない"),
        ("baby rabbit diarrhea", "子うさぎの下痢"),
        ("pregnant rabbit labor trouble", "妊娠うさぎの出産トラブル"),
        ("nesting and not eating", "巣作りして食べない"),
        ("suddenly aggressive", "急に攻撃的"),
        ("not grooming", "毛づくろいしない"),
        ("wet front paws", "前足が濡れている"),
        ("pale gums", "歯ぐきが白い"),
        ("fast breathing", "呼吸が速い"),
        ("restless and cannot settle", "落ち着かない"),
        ("pressing head", "頭を押しつける"),
        ("circling", "旋回する"),
        ("not using litter box", "トイレを使わない"),
        ("wet tail or rear", "尾やお尻が濡れている"),
        ("salivating", "よだれが出る"),
    ],
    "zh-tw": [
        ("not eating", "不進食"), ("not pooping", "沒有便便"), ("small droppings", "便便變小"), ("watery diarrhea", "水樣腹瀉"), ("bloated belly", "腹部脹硬"), ("hunched posture", "弓背姿勢"), ("lethargic", "嗜睡無力"), ("not moving", "不動"), ("collapsed", "倒下"), ("cold ears", "耳朵冰冷"), ("cold body", "身體冰冷"), ("heatstroke", "中暑"), ("difficulty breathing", "呼吸困難"), ("mouth breathing", "張口呼吸"), ("blue lips", "嘴唇發藍"), ("runny nose", "流鼻水"), ("choking", "噎住"), ("drooling", "流口水"), ("wet chin", "下巴潮濕"), ("overgrown teeth", "牙齒過長"), ("eye discharge", "眼部分泌物"), ("head tilt", "歪頭"), ("seizure", "癲癇發作"), ("back legs weak", "後腿無力"), ("paralysis", "癱瘓"), ("limping", "跛行"), ("fall", "跌落"), ("bleeding", "出血"), ("open wound", "開放性傷口"), ("bite wound", "咬傷"), ("abscess", "膿腫"), ("flystrike", "蠅蛆症"), ("maggots", "蛆蟲"), ("straining to urinate", "排尿用力"), ("not peeing", "沒有尿尿"), ("blood in urine", "尿中有血"), ("not drinking", "不喝水"), ("dehydrated", "脫水"), ("weight loss", "體重下降"), ("sudden behavior change", "突然行為改變"), ("grinding teeth", "磨牙"), ("ear scratching", "抓耳朵"), ("ate chocolate", "吃了巧克力"), ("ate human medicine", "吃了人用藥"), ("ate plastic", "吃了塑膠"), ("not eating after surgery", "術後不進食"), ("baby rabbit not eating", "幼兔不進食"), ("baby rabbit diarrhea", "幼兔腹瀉"), ("fast breathing", "呼吸急促"),
    ],
    "th": [
        ("not eating", "ไม่กินอาหาร"), ("not pooping", "ไม่ถ่าย"), ("small droppings", "มูลเล็กลง"), ("watery diarrhea", "ท้องเสียเป็นน้ำ"), ("bloated belly", "ท้องอืดแข็ง"), ("hunched posture", "โก่งตัว"), ("lethargic", "ซึม"), ("not moving", "ไม่ขยับ"), ("collapsed", "ล้ม"), ("cold ears", "หูเย็น"), ("cold body", "ตัวเย็น"), ("heatstroke", "ฮีตสโตรก"), ("difficulty breathing", "หายใจลำบาก"), ("mouth breathing", "อ้าปากหายใจ"), ("blue lips", "ริมฝีปากเขียว"), ("runny nose", "น้ำมูกไหล"), ("choking", "สำลัก"), ("drooling", "น้ำลายไหล"), ("wet chin", "คางเปียก"), ("overgrown teeth", "ฟันยาวเกิน"), ("eye discharge", "ขี้ตาหรือน้ำตา"), ("head tilt", "หัวเอียง"), ("seizure", "ชัก"), ("back legs weak", "ขาหลังอ่อนแรง"), ("paralysis", "อัมพาต"), ("limping", "เดินกะเผลก"), ("fall", "ตกจากที่สูง"), ("bleeding", "เลือดออก"), ("open wound", "แผลเปิด"), ("bite wound", "แผลกัด"), ("abscess", "ฝี"), ("flystrike", "หนอนแมลงวัน"), ("maggots", "หนอน"), ("straining to urinate", "เบ่งปัสสาวะ"), ("not peeing", "ไม่ปัสสาวะ"), ("blood in urine", "เลือดในปัสสาวะ"), ("not drinking", "ไม่ดื่มน้ำ"), ("dehydrated", "ขาดน้ำ"), ("weight loss", "น้ำหนักลด"), ("sudden behavior change", "พฤติกรรมเปลี่ยนกะทันหัน"), ("grinding teeth", "กัดฟัน"), ("ear scratching", "เกาหู"), ("ate chocolate", "กินช็อกโกแลต"), ("ate human medicine", "กินยาคน"), ("ate plastic", "กินพลาสติก"), ("not eating after surgery", "ไม่กินหลังผ่าตัด"), ("baby rabbit not eating", "ลูกกระต่ายไม่กิน"), ("baby rabbit diarrhea", "ลูกกระต่ายท้องเสีย"), ("fast breathing", "หายใจเร็ว"),
    ],
}

PHRASE_REPLACEMENTS["ja"].extend([
    ("no caecotrophs", "盲腸便が出ない"),
    ("soft stool", "軟便"),
    ("hit by door", "ドアに挟まれた"),
])

PHRASE_REPLACEMENTS["zh-tw"].extend([
    ("no caecotrophs", "沒有盲腸便"),
    ("soft stool", "軟便"),
    ("belly pressed to floor", "腹部貼地"),
    ("loud tooth grinding", "大聲磨牙"),
    ("floppy", "癱軟無力"),
    ("overheated", "過熱"),
    ("panting", "喘氣"),
    ("noisy breathing", "呼吸有雜音"),
    ("sneezing with discharge", "打噴嚏伴隨分泌物"),
    ("gagging", "作嘔"),
    ("dropping food", "掉食物"),
    ("face swelling", "臉部腫脹"),
    ("squinting eye", "瞇眼"),
    ("cloudy eye", "眼睛混濁"),
    ("eye injury", "眼睛受傷"),
    ("rolling", "翻滾"),
    ("loss of balance", "失去平衡"),
    ("trembling", "發抖"),
    ("dragging back legs", "拖行後腿"),
    ("dropped", "被摔落"),
    ("hit by door", "被門夾到"),
    ("broken nail", "斷甲"),
    ("sore hocks", "腳底潰瘍"),
    ("dirty bottom", "屁股髒污"),
    ("urine scald", "尿液灼傷"),
    ("red urine", "紅色尿液"),
    ("sludgy urine", "泥沙尿"),
    ("hiding", "躲藏"),
    ("screaming", "尖叫"),
    ("shaking head", "甩頭"),
    ("ear discharge", "耳部分泌物"),
    ("toxic plant exposure", "接觸有毒植物"),
    ("ate rodenticide", "吃了滅鼠藥"),
    ("ate onion or garlic", "吃了洋蔥或大蒜"),
    ("ate houseplant", "吃了室內植物"),
    ("ate carpet or fabric", "吃了地毯或布料"),
    ("hair in gut", "腸胃內毛髮"),
    ("moulting and not eating", "換毛且不進食"),
    ("not pooping after surgery", "術後沒有便便"),
    ("swollen incision", "切口腫脹"),
    ("not eating after vet visit", "看診後不進食"),
    ("pregnant rabbit labor trouble", "懷孕兔生產困難"),
    ("nesting and not eating", "築巢且不進食"),
    ("suddenly aggressive", "突然攻擊性增加"),
    ("not grooming", "不理毛"),
    ("wet front paws", "前腳潮濕"),
    ("pale gums", "牙齦蒼白"),
    ("restless and cannot settle", "躁動無法安定"),
    ("pressing head", "頭部頂壓"),
    ("circling", "原地繞圈"),
    ("not using litter box", "不使用便盆"),
    ("wet tail or rear", "尾巴或後半身潮濕"),
    ("salivating", "流涎"),
])

PHRASE_REPLACEMENTS["th"].extend([
    ("no caecotrophs", "ไม่เห็นมูลพวงองุ่น"),
    ("soft stool", "อุจจาระนิ่ม"),
    ("belly pressed to floor", "กดท้องแนบพื้น"),
    ("loud tooth grinding", "กัดฟันเสียงดัง"),
    ("floppy", "ตัวอ่อนแรง"),
    ("overheated", "ร้อนเกิน"),
    ("panting", "หอบ"),
    ("noisy breathing", "หายใจมีเสียง"),
    ("sneezing with discharge", "จามมีน้ำมูก"),
    ("gagging", "ขย้อน"),
    ("dropping food", "ทำอาหารหล่นจากปาก"),
    ("face swelling", "หน้าบวม"),
    ("squinting eye", "หยีตา"),
    ("cloudy eye", "ตาขุ่น"),
    ("eye injury", "บาดเจ็บที่ตา"),
    ("rolling", "กลิ้งตัว"),
    ("loss of balance", "เสียการทรงตัว"),
    ("trembling", "ตัวสั่น"),
    ("dragging back legs", "ลากขาหลัง"),
    ("dropped", "ถูกทำตก"),
    ("hit by door", "ถูกประตูหนีบหรือกระแทก"),
    ("broken nail", "เล็บหัก"),
    ("sore hocks", "แผลฝ่าเท้า"),
    ("dirty bottom", "ก้นสกปรก"),
    ("urine scald", "ผิวหนังไหม้จากปัสสาวะ"),
    ("red urine", "ปัสสาวะสีแดง"),
    ("sludgy urine", "ปัสสาวะข้นเป็นตะกอน"),
    ("hiding", "ซ่อนตัว"),
    ("screaming", "ร้องเสียงดัง"),
    ("shaking head", "สะบัดหัว"),
    ("ear discharge", "มีของเหลวจากหู"),
    ("toxic plant exposure", "สัมผัสหรือกินพืชพิษ"),
    ("ate rodenticide", "กินยาเบื่อหนู"),
    ("ate onion or garlic", "กินหัวหอมหรือกระเทียม"),
    ("ate houseplant", "กินไม้ประดับในบ้าน"),
    ("ate carpet or fabric", "กินพรมหรือผ้า"),
    ("hair in gut", "ขนในทางเดินอาหาร"),
    ("moulting and not eating", "ผลัดขนและไม่กินอาหาร"),
    ("not pooping after surgery", "ไม่ถ่ายหลังผ่าตัด"),
    ("swollen incision", "แผลผ่าตัดบวม"),
    ("not eating after vet visit", "ไม่กินหลังไปพบสัตวแพทย์"),
    ("pregnant rabbit labor trouble", "กระต่ายท้องคลอดผิดปกติ"),
    ("nesting and not eating", "ทำรังและไม่กินอาหาร"),
    ("suddenly aggressive", "ก้าวร้าวกะทันหัน"),
    ("not grooming", "ไม่ทำความสะอาดตัว"),
    ("wet front paws", "ขาหน้าเปียก"),
    ("pale gums", "เหงือกซีด"),
    ("restless and cannot settle", "กระสับกระส่ายไม่อยู่นิ่ง"),
    ("pressing head", "กดหัวกับพื้นหรือผนัง"),
    ("circling", "เดินวน"),
    ("not using litter box", "ไม่ใช้กระบะขับถ่าย"),
    ("wet tail or rear", "หางหรือก้นเปียก"),
    ("salivating", "น้ำลายไหล"),
])

CATEGORY_GO = {
    "ja": {
        "gut": "{sign}に加えて食欲低下、便が少ない・出ない、腹痛、ぐったり、体が冷たい症状があれば、腸うっ滞や閉塞の可能性があり緊急です。",
        "pain": "{sign}に食べない、動かない、背中を丸める、大きな歯ぎしりが伴う場合は痛みのサインとして急いで相談してください。",
        "shock": "{sign}、体が冷たい、反応が弱い、倒れる、呼吸異常がある場合は救急対応が必要です。",
        "heat": "{sign}、暑さへの曝露、よだれ、弱り、倒れる、発作がある場合は熱中症の緊急サインです。",
        "breathing": "{sign}、口呼吸、青い唇、努力呼吸、弱り、倒れる症状はすぐ受診すべき呼吸の緊急サインです。",
        "mouth": "{sign}に食べない、よだれ、体重減少、顔の腫れが伴う場合は歯や口の痛みとして本日中に相談してください。",
        "eye": "{sign}、目の痛み、腫れ、外傷、濁り、食欲低下がある場合は同日中の獣医相談が必要です。",
        "neuro": "{sign}、斜頸、転倒、発作、バランス喪失、食欲低下がある場合はすぐ獣医へ相談してください。",
        "mobility": "{sign}が突然出た、痛み、外傷、麻痺、尿便の異常を伴う場合は緊急です。",
        "trauma": "{sign}が外傷、落下、出血、痛み、呼吸変化、食欲低下に続く場合はすぐ相談してください。",
        "skin": "{sign}に出血、潰瘍、腫れ、悪臭、ウジ、弱りがあれば緊急です。",
        "urinary": "{sign}、排尿時の痛み、血尿、尿が出ない、弱り、食欲低下がある場合は緊急の可能性があります。",
        "hydration": "{sign}に食欲低下、小さい便、暑さ、弱り、脱水サインがあれば急いで相談してください。",
        "illness": "{sign}に食欲、便、呼吸、動き、痛みの変化が伴えば本日中に相談してください。",
        "ear": "{sign}に斜頸、耳だれ、痛み、バランス喪失、食欲低下があれば獣医相談が必要です。",
        "toxin": "{sign}または中毒の疑いがあれば、症状が出る前でも獣医または中毒相談へ連絡してください。",
        "foreign_body": "{sign}に食欲低下、便が出ない、腹痛、窒息サインが伴う場合は閉塞の可能性があり緊急です。",
        "postop": "{sign}に食べない、便が出ない、痛み、体が冷たい、弱り、排尿異常があれば手術先または救急獣医へ連絡してください。",
        "kit": "{sign}、体が冷たい、弱い、膨満、下痢がある子うさぎはすぐ専門的なケアが必要です。",
        "repro": "{sign}に出血、長い陣痛、弱り、詰まり、倒れる症状があれば緊急です。",
    },
    "zh-tw": {
        "gut": "{sign}若伴隨不進食、便便變少或沒有、腹痛、嗜睡、身體冰冷，可能是腸胃停滯或阻塞，需緊急聯絡獸醫。",
        "pain": "{sign}若伴隨不吃、弓背、不動、明顯磨牙，通常代表疼痛，請儘快致電獸醫。",
        "shock": "{sign}、身體冰冷、反應差、倒下或呼吸異常，應視為急症。",
        "heat": "{sign}、高溫暴露、流口水、虛弱、倒下或癲癇，是中暑急症警訊。",
        "breathing": "{sign}、張口呼吸、嘴唇發藍、呼吸費力、虛弱或倒下，都需要立即就醫。",
        "mouth": "{sign}若伴隨不進食、流口水、體重下降或臉部腫脹，可能是牙齒或口腔疼痛，請今天致電獸醫。",
        "eye": "{sign}、眼痛、腫脹、外傷、混濁或食慾下降，需要同日獸醫建議。",
        "neuro": "{sign}、歪頭、翻滾、失去平衡、癲癇或不進食，需要熟悉兔子的獸醫評估。",
        "mobility": "{sign}若突然出現，或伴隨疼痛、外傷、癱瘓、尿便異常，可能是急症。",
        "trauma": "{sign}若發生在跌落、撞擊、咬傷、出血、疼痛、呼吸改變或食慾下降後，請立即聯絡獸醫。",
        "skin": "{sign}若有出血、潰瘍、腫脹、臭味、蛆蟲或虛弱，是急症。",
        "urinary": "{sign}、排尿疼痛、血尿、尿不出、虛弱或不進食，可能需要緊急處理。",
        "hydration": "{sign}若伴隨不吃、便便變小、高溫、虛弱或脫水跡象，請儘快致電獸醫。",
        "illness": "{sign}若伴隨食慾、便便、呼吸、活動或疼痛變化，請今天致電獸醫。",
        "ear": "{sign}若伴隨歪頭、耳分泌物、疼痛、失衡或食慾下降，需要獸醫評估。",
        "toxin": "{sign}或疑似中毒暴露，即使尚未出現症狀，也應立即聯絡獸醫或中毒諮詢。",
        "foreign_body": "{sign}若伴隨不進食、沒有便便、腹痛或噎住跡象，可能是阻塞，需緊急建議。",
        "postop": "{sign}若伴隨不吃、沒有便便、疼痛、身體冰冷、虛弱或排尿異常，請聯絡手術診所或急症獸醫。",
        "kit": "幼兔{sign}、身體冰冷、虛弱、腹脹或腹瀉，都需要緊急專業照護。",
        "repro": "{sign}若伴隨出血、長時間用力、虛弱、胎兒卡住或倒下，是急症。",
    },
    "th": {
        "gut": "{sign}ร่วมกับไม่กิน มูลน้อยหรือไม่ถ่าย ปวดท้อง ซึม หรือตัวเย็น อาจเป็นภาวะลำไส้หยุดทำงานหรืออุดตันและต้องรีบติดต่อสัตวแพทย์",
        "pain": "{sign}ร่วมกับไม่กิน โก่งตัว ไม่ขยับ หรือกัดฟันเสียงดัง มักเป็นสัญญาณปวดและควรโทรหาสัตวแพทย์เร็ว",
        "shock": "{sign} ตัวเย็น ตอบสนองน้อย ล้ม หรือหายใจผิดปกติ ควรถือเป็นเหตุฉุกเฉิน",
        "heat": "{sign} หลังอยู่ในที่ร้อน น้ำลายไหล อ่อนแรง ล้ม หรือชัก เป็นสัญญาณฉุกเฉินของฮีตสโตรก",
        "breathing": "{sign} อ้าปากหายใจ ริมฝีปากเขียว หายใจลำบาก อ่อนแรงหรือล้ม ต้องพบสัตวแพทย์ทันที",
        "mouth": "{sign}ร่วมกับไม่กิน น้ำลายไหล น้ำหนักลด หรือหน้าบวม อาจเป็นปัญหาฟันหรือปากและควรโทรวันนี้",
        "eye": "{sign} เจ็บตา บวม บาดเจ็บ ตาขุ่น หรือกินน้อยลง ควรขอคำแนะนำจากสัตวแพทย์ในวันเดียวกัน",
        "neuro": "{sign} หัวเอียง กลิ้ง เสียการทรงตัว ชัก หรือไม่กิน ต้องให้สัตวแพทย์ที่ดูแลกระต่ายประเมิน",
        "mobility": "{sign}ที่เกิดทันที หรือมีปวด บาดเจ็บ อัมพาต หรือปัสสาวะอุจจาระผิดปกติ อาจเป็นเหตุฉุกเฉิน",
        "trauma": "{sign}หลังตก กระแทก กัด เลือดออก ปวด หายใจเปลี่ยน หรือไม่กิน ให้รีบติดต่อสัตวแพทย์",
        "skin": "{sign}ร่วมกับเลือดออก แผลบวม กลิ่นเหม็น หนอน หรืออ่อนแรง เป็นเหตุฉุกเฉิน",
        "urinary": "{sign} ปวดเวลาปัสสาวะ เลือดในปัสสาวะ ปัสสาวะไม่ออก อ่อนแรง หรือไม่กิน อาจต้องดูแลฉุกเฉิน",
        "hydration": "{sign}ร่วมกับไม่กิน มูลเล็ก อากาศร้อน อ่อนแรง หรือสัญญาณขาดน้ำ ควรโทรหาสัตวแพทย์เร็ว",
        "illness": "{sign}ร่วมกับการเปลี่ยนแปลงเรื่องกิน มูล หายใจ เคลื่อนไหว หรือปวด ควรโทรวันนี้",
        "ear": "{sign}ร่วมกับหัวเอียง น้ำหรือหนองจากหู เจ็บ เสียการทรงตัว หรือไม่กิน ต้องให้สัตวแพทย์ประเมิน",
        "toxin": "{sign}หรือสงสัยสัมผัสสารพิษ ควรโทรหาสัตวแพทย์หรือศูนย์พิษวิทยาทันทีแม้ยังไม่มีอาการ",
        "foreign_body": "{sign}ร่วมกับไม่กิน ไม่ถ่าย ปวดท้อง หรือสำลัก อาจเป็นการอุดตันและต้องขอคำแนะนำด่วน",
        "postop": "{sign}หลังผ่าตัดร่วมกับไม่กิน ไม่ถ่าย ปวด ตัวเย็น อ่อนแรง หรือปัสสาวะผิดปกติ ให้ติดต่อทีมผ่าตัดหรือสัตวแพทย์ฉุกเฉิน",
        "kit": "ลูกกระต่าย{sign} ตัวเย็น อ่อนแรง ท้องอืด หรือท้องเสีย ต้องได้รับการดูแลจากผู้เชี่ยวชาญอย่างเร่งด่วน",
        "repro": "{sign}ร่วมกับเลือดออก เบ่งนาน อ่อนแรง ลูกค้าง หรือหมดแรงล้ม เป็นเหตุฉุกเฉิน",
    },
}

SOURCES = {
    "rwaf": ("Rabbit Welfare Association & Fund", "https://rabbitwelfare.co.uk/"),
    "hrs": ("House Rabbit Society", "https://rabbit.org/"),
    "merck": ("Merck Veterinary Manual", "https://www.merckvetmanual.com/"),
    "vca": ("VCA Hospitals", "https://vcahospitals.com/"),
}

SIGN_ROWS = """
rabbit-not-eating-emergency-signs|not eating|gut|Not eating for 6-12 hours, no droppings, hunched posture, tooth grinding, cold ears, or a tight belly means call a rabbit-savvy vet now.
rabbit-not-pooping-emergency-signs|not pooping|gut|No droppings, tiny droppings, not eating, belly pain, lethargy, or cold ears can mean gut stasis or blockage and needs urgent veterinary contact.
rabbit-small-droppings-emergency-signs|small droppings|gut|Suddenly tiny, dry, misshapen, or fewer droppings with reduced appetite can be an early gut slowdown warning.
rabbit-no-caecotrophs-emergency-signs|no caecotrophs|gut|Missing or uneaten caecotrophs with soft stool, dirty bottom, reduced appetite, or weight change needs veterinary guidance.
rabbit-soft-stool-emergency-signs|soft stool|gut|Soft stool with not eating, lethargy, dirty bottom, dehydration, or young age needs same-day rabbit-savvy vet advice.
rabbit-watery-diarrhea-emergency-signs|watery diarrhea|gut|True watery diarrhea, weakness, collapse, cold body, or baby-rabbit age is an emergency.
rabbit-bloated-belly-emergency-signs|bloated belly|gut|A hard, tight, swollen, or painful belly with no eating, no droppings, lethargy, or tooth grinding means go now.
rabbit-belly-pressed-floor-emergency-signs|belly pressed to floor|pain|Pressing the belly to the floor with not eating, no droppings, bloat, or tooth grinding suggests pain and needs urgent contact.
rabbit-hunched-posture-emergency-signs|hunched posture|pain|A hunched rabbit with poor appetite, tooth grinding, belly pain, or fewer droppings needs prompt veterinary assessment.
rabbit-tooth-grinding-pain-emergency-signs|loud tooth grinding|pain|Loud tooth grinding with stillness, hunching, not eating, or belly pain usually signals pain and needs a vet call.
rabbit-lethargic-emergency-signs|lethargic|shock|Sudden lethargy, not moving, not eating, cold ears, pale gums, or collapse is urgent in rabbits.
rabbit-not-moving-emergency-signs|not moving|shock|A rabbit that is suddenly still, weak, floppy, cold, or barely responsive needs emergency veterinary care.
rabbit-floppy-emergency-signs|floppy|shock|A floppy rabbit, weak rabbit, or rabbit unable to sit normally should be treated as an emergency.
rabbit-collapse-emergency-signs|collapsed|shock|Collapse, unresponsiveness, severe weakness, abnormal breathing, heat exposure, or cold body means go now.
rabbit-cold-ears-emergency-signs|cold ears|shock|Cold ears with lethargy, not eating, no droppings, weakness, or collapse can signal shock or hypothermia.
rabbit-cold-body-emergency-signs|cold body|shock|A cold rabbit with weakness, poor responsiveness, or gut stasis signs needs urgent warming guidance and veterinary care.
rabbit-heatstroke-emergency-signs|heatstroke|heat|Panting, drooling, red ears, weakness, collapse, seizures, or heat exposure means emergency care now.
rabbit-overheated-emergency-signs|overheated|heat|An overheated rabbit with fast breathing, weakness, drooling, collapse, or warm environment exposure needs urgent cooling advice and a vet.
rabbit-panting-emergency-signs|panting|breathing|Panting or open-mouth breathing in a rabbit is abnormal and should be treated as an emergency.
rabbit-difficulty-breathing-emergency-signs|difficulty breathing|breathing|Laboured breathing, open mouth, blue lips, noisy breathing, collapse, or severe distress means go now.
rabbit-mouth-breathing-emergency-signs|mouth breathing|breathing|Mouth breathing in a rabbit is a go-now emergency because rabbits normally breathe through the nose.
rabbit-blue-lips-emergency-signs|blue lips|breathing|Blue, gray, or very pale lips or gums with breathing trouble or weakness means emergency care now.
rabbit-noisy-breathing-emergency-signs|noisy breathing|breathing|Noisy breathing with effort, open-mouth breathing, weakness, discharge, or poor appetite needs urgent vet contact.
rabbit-sneezing-discharge-emergency-signs|sneezing with discharge|breathing|Sneezing with thick discharge, wet paws, noisy breathing, poor appetite, or lethargy needs veterinary care.
rabbit-runny-nose-emergency-signs|runny nose|breathing|Runny nose with not eating, breathing effort, wet forepaws, feverish behavior, or eye discharge needs a vet call.
rabbit-choking-emergency-signs|choking|breathing|Choking, gagging, pawing at the mouth, drooling, blue lips, or breathing distress means go now.
rabbit-gagging-emergency-signs|gagging|breathing|Gagging with distress, drooling, choking signs, food exposure, or breathing changes needs urgent veterinary help.
rabbit-drooling-emergency-signs|drooling|mouth|Drooling, wet chin, dropping food, mouth pain, tooth grinding, or not eating needs rabbit-savvy dental and medical assessment.
rabbit-wet-chin-emergency-signs|wet chin|mouth|A wet chin with drooling, weight loss, not eating, or dropping food often signals dental disease and needs a vet.
rabbit-dropping-food-emergency-signs|dropping food|mouth|Dropping food, chewing oddly, drooling, weight loss, or selective eating can mean dental pain and needs care.
rabbit-overgrown-teeth-emergency-signs|overgrown teeth|mouth|Visible tooth overgrowth, drooling, not eating, weight loss, or facial swelling needs rabbit-savvy veterinary care.
rabbit-face-swelling-emergency-signs|face swelling|mouth|Facial swelling, jaw lump, eye discharge, drooling, or reduced eating can mean abscess or dental disease and needs a vet.
rabbit-eye-discharge-emergency-signs|eye discharge|eye|Eye discharge, swelling, squinting, cloudiness, trauma, or not eating needs same-day veterinary advice.
rabbit-squinting-eye-emergency-signs|squinting eye|eye|A squinting, closed, cloudy, swollen, or painful eye can be urgent and should not be treated with leftover drops.
rabbit-cloudy-eye-emergency-signs|cloudy eye|eye|Cloudy eye, bulging eye, injury, discharge, or head tilt needs veterinary assessment.
rabbit-eye-injury-emergency-signs|eye injury|eye|Eye trauma, bleeding, visible scratch, chemical exposure, or inability to open the eye needs urgent care.
rabbit-head-tilt-emergency-signs|head tilt|neuro|Sudden head tilt, rolling, loss of balance, eye flicking, not eating, or weakness needs prompt rabbit-savvy veterinary care.
rabbit-rolling-emergency-signs|rolling|neuro|Rolling with head tilt, weakness, seizures, or inability to stay upright is urgent.
rabbit-loss-balance-emergency-signs|loss of balance|neuro|Loss of balance, falling, head tilt, rolling, or weakness needs veterinary assessment.
rabbit-seizure-emergency-signs|seizure|neuro|A seizure, repeated seizure, heat exposure, toxin risk, collapse, or poor recovery means emergency care now.
rabbit-trembling-emergency-signs|trembling|neuro|Trembling with pain, heatstroke, toxin risk, weakness, not eating, or collapse needs urgent advice.
rabbit-back-legs-weak-emergency-signs|back legs weak|mobility|Sudden hind-leg weakness, dragging, paralysis, pain, or fall history needs prompt veterinary assessment.
rabbit-dragging-back-legs-emergency-signs|dragging back legs|mobility|Dragging back legs, loss of bladder control, pain, or trauma history needs urgent care.
rabbit-paralysis-emergency-signs|paralysis|mobility|Sudden paralysis, inability to move, spinal injury concern, or severe weakness is an emergency.
rabbit-limping-emergency-signs|limping|mobility|Severe limping, swelling, pain, fall, bite, bleeding, or not eating after injury needs a vet call.
rabbit-fall-emergency-signs|fall|trauma|After a fall or being dropped, limping, pain, not eating, breathing changes, or weakness needs veterinary assessment.
rabbit-dropped-emergency-signs|dropped|trauma|A dropped rabbit can hide spinal or internal injury; pain, weakness, limping, or appetite loss means urgent contact.
rabbit-hit-by-door-emergency-signs|hit by door|trauma|Crush injury, door accident, limping, bleeding, breathing changes, or shock signs means go now.
rabbit-bleeding-emergency-signs|bleeding|trauma|Heavy bleeding, bite wounds, pale gums, weakness, or bleeding that will not stop needs emergency care.
rabbit-broken-nail-emergency-signs|broken nail|trauma|A broken nail that bleeds heavily, exposes tissue, causes limping, or will not stop bleeding needs veterinary guidance.
rabbit-open-wound-emergency-signs|open wound|trauma|Open wounds, bite wounds, exposed tissue, swelling, pus, or pain need rabbit-savvy veterinary care.
rabbit-bite-wound-emergency-signs|bite wound|trauma|Bite wounds can hide infection; bleeding, swelling, pain, abscess, or reduced appetite needs care.
rabbit-abscess-emergency-signs|abscess|trauma|A lump, abscess, pus, facial swelling, pain, or appetite loss needs rabbit-savvy veterinary treatment.
rabbit-sore-hocks-emergency-signs|sore hocks|skin|Bleeding, ulcers, swelling, limping, infection signs, or pain from sore hocks needs veterinary care.
rabbit-flystrike-emergency-signs|flystrike|skin|Maggots, dirty bottom, bad smell, collapse, weakness, or hot weather exposure means emergency care now.
rabbit-dirty-bottom-emergency-signs|dirty bottom|skin|A dirty bottom with soft stool, urine scald, fly eggs, maggots, obesity, or poor mobility needs prompt action.
rabbit-maggots-emergency-signs|maggots|skin|Maggots or fly eggs on a rabbit are a life-threatening emergency.
rabbit-urine-scald-emergency-signs|urine scald|urinary|Urine scald with wet fur, sores, sludge, mobility trouble, or dirty bottom needs veterinary assessment.
rabbit-straining-urinate-emergency-signs|straining to urinate|urinary|Straining, dribbling, blood, pain, or inability to pass urine needs urgent veterinary contact.
rabbit-not-peeing-emergency-signs|not peeing|urinary|Not peeing, straining, pain, sludge history, or weakness can be urgent and needs a vet call.
rabbit-blood-urine-emergency-signs|blood in urine|urinary|True blood in urine, straining, pain, weakness, or reproductive disease concern needs veterinary assessment.
rabbit-red-urine-emergency-signs|red urine|urinary|Red urine can be pigment, but red urine with pain, straining, clots, weakness, or not eating needs a vet.
rabbit-sludgy-urine-emergency-signs|sludgy urine|urinary|Thick, gritty, or sludgy urine with straining, pain, urine scald, or reduced appetite needs care.
rabbit-not-drinking-emergency-signs|not drinking|hydration|Not drinking with not eating, small droppings, heat, weakness, or dehydration signs needs urgent guidance.
rabbit-dehydrated-emergency-signs|dehydrated|hydration|Dehydration with lethargy, reduced droppings, sticky mouth, poor appetite, or heat exposure needs a vet.
rabbit-weight-loss-emergency-signs|weight loss|illness|Weight loss with drooling, poor appetite, small droppings, diarrhea, or lethargy needs veterinary assessment.
rabbit-hiding-emergency-signs|hiding|illness|Hiding with reduced eating, pain signs, fewer droppings, or lethargy needs a rabbit-savvy vet call.
rabbit-sudden-behavior-change-emergency-signs|sudden behavior change|illness|Sudden behavior change with appetite, droppings, breathing, movement, or pain changes needs guidance.
rabbit-crying-screaming-emergency-signs|screaming|pain|A rabbit scream or cry usually means extreme fear or pain and should be treated as an emergency.
rabbit-grinding-teeth-emergency-signs|grinding teeth|pain|Loud tooth grinding with hunched posture, stillness, not eating, or belly pain means urgent vet contact.
rabbit-shaking-head-emergency-signs|shaking head|ear|Head shaking with scratching, head tilt, discharge, crusts, or loss of balance needs veterinary care.
rabbit-ear-scratching-emergency-signs|ear scratching|ear|Persistent ear scratching, crusts, discharge, head tilt, pain, or appetite loss needs rabbit-savvy care.
rabbit-ear-discharge-emergency-signs|ear discharge|ear|Ear discharge, crusting, smell, head tilt, pain, or loss of balance needs vet assessment.
rabbit-toxic-plant-emergency-signs|toxic plant exposure|toxin|Known or suspected toxic plant exposure with any behavior change, drooling, weakness, diarrhea, or not eating needs urgent contact.
rabbit-ate-chocolate-emergency-signs|ate chocolate|toxin|Chocolate exposure, unknown dose, weakness, diarrhea, tremors, or not eating needs vet or poison-control guidance.
rabbit-ate-human-medicine-emergency-signs|ate human medicine|toxin|Any human medicine exposure should be treated as urgent until a vet or poison-control service says otherwise.
rabbit-ate-rodenticide-emergency-signs|ate rodenticide|toxin|Rodenticide exposure can be dangerous before signs appear; call a vet or poison-control service now.
rabbit-ate-onion-garlic-emergency-signs|ate onion or garlic|toxin|Onion, garlic, or unsafe food exposure with GI signs, weakness, or uncertain amount needs veterinary advice.
rabbit-ate-houseplant-emergency-signs|ate houseplant|toxin|Unknown houseplant exposure should be checked with a vet or poison-control service, especially with drooling, diarrhea, or weakness.
rabbit-ate-carpet-fabric-emergency-signs|ate carpet or fabric|foreign_body|Carpet, fabric, plastic, or foreign material ingestion with not eating, no droppings, or belly pain needs urgent advice.
rabbit-ate-plastic-emergency-signs|ate plastic|foreign_body|Plastic ingestion with reduced appetite, no droppings, belly pain, or choking signs needs veterinary guidance.
rabbit-hairball-gut-emergency-signs|hair in gut|gut|Heavy moult with reduced appetite, smaller droppings, or belly pain can become gut slowdown and needs monitoring with vet guidance.
rabbit-moulting-not-eating-emergency-signs|moulting and not eating|gut|Moulting plus reduced appetite, fewer droppings, or lethargy can become urgent gut stasis.
rabbit-post-op-not-eating-emergency-signs|not eating after surgery|postop|A post-op rabbit not eating, not pooping, painful, cold, weak, or not urinating needs immediate veterinary guidance.
rabbit-not-pooping-after-surgery-emergency-signs|not pooping after surgery|postop|No droppings after surgery with poor appetite or pain needs the surgical team or emergency vet.
rabbit-incision-swollen-emergency-signs|swollen incision|postop|A swollen, painful, bleeding, open, hot, or draining incision needs veterinary contact.
rabbit-after-vet-visit-not-eating-emergency-signs|not eating after vet visit|postop|Stress after travel can trigger gut slowdown; not eating or fewer droppings after a vet visit needs prompt advice.
baby-rabbit-not-eating-emergency-signs|baby rabbit not eating|kit|A baby rabbit not eating, cold, weak, bloated, or having diarrhea needs urgent expert care.
baby-rabbit-diarrhea-emergency-signs|baby rabbit diarrhea|kit|Diarrhea in a baby rabbit can become life-threatening quickly and needs urgent care.
pregnant-rabbit-labor-emergency-signs|pregnant rabbit labor trouble|repro|Heavy bleeding, prolonged straining, weakness, stuck kit, or collapse during labor needs emergency care.
rabbit-nesting-not-eating-emergency-signs|nesting and not eating|repro|A pregnant or recently kindled rabbit not eating, weak, bleeding, or distressed needs veterinary guidance.
rabbit-aggressive-suddenly-emergency-signs|suddenly aggressive|illness|Sudden aggression with pain signs, poor appetite, urinary signs, or behavior change can signal illness and needs assessment.
rabbit-not-grooming-emergency-signs|not grooming|illness|Not grooming with dirty bottom, weight loss, pain, dental signs, or reduced appetite needs veterinary care.
rabbit-wet-front-paws-emergency-signs|wet front paws|breathing|Wet front paws can come from nasal discharge; paired with sneezing, poor appetite, or noisy breathing, it needs vet care.
rabbit-pale-gums-emergency-signs|pale gums|shock|Pale or blue gums, weakness, collapse, bleeding, or breathing trouble means emergency care now.
rabbit-fast-breathing-emergency-signs|fast breathing|breathing|Fast breathing with effort, heat exposure, blue lips, weakness, or collapse means urgent veterinary care.
rabbit-restless-can-not-settle-emergency-signs|restless and cannot settle|pain|Restlessness with belly pain, not eating, no droppings, straining, or tooth grinding needs urgent care.
rabbit-pressing-head-emergency-signs|pressing head|neuro|Head pressing, severe disorientation, seizure, weakness, or toxin risk needs emergency assessment.
rabbit-circling-emergency-signs|circling|neuro|Circling with head tilt, loss of balance, weakness, or appetite loss needs rabbit-savvy veterinary care.
rabbit-not-using-litter-box-emergency-signs|not using litter box|urinary|Sudden litter-box change with straining, red urine, sludge, pain, or appetite change needs a vet call.
rabbit-tail-wet-emergency-signs|wet tail or rear|skin|Wet rear fur, urine scald, diarrhea, dirty bottom, or flystrike risk needs prompt assessment.
rabbit-salivating-emergency-signs|salivating|mouth|Salivating with wet chin, mouth pain, toxin risk, or not eating needs urgent veterinary guidance.
""".strip()

SIGN_SOURCES = {
    "gut": ["rwaf", "hrs", "merck"],
    "pain": ["rwaf", "hrs", "vca"],
    "shock": ["rwaf", "merck", "vca"],
    "heat": ["rwaf", "hrs", "merck"],
    "breathing": ["rwaf", "hrs", "vca"],
    "mouth": ["rwaf", "hrs", "merck"],
    "eye": ["rwaf", "hrs", "vca"],
    "neuro": ["rwaf", "hrs", "merck"],
    "mobility": ["rwaf", "hrs", "vca"],
    "trauma": ["rwaf", "hrs", "vca"],
    "skin": ["rwaf", "hrs", "merck"],
    "urinary": ["rwaf", "hrs", "merck"],
    "hydration": ["rwaf", "hrs", "merck"],
    "illness": ["rwaf", "hrs", "vca"],
    "ear": ["rwaf", "hrs", "vca"],
    "toxin": ["rwaf", "hrs", "merck"],
    "foreign_body": ["rwaf", "hrs", "merck"],
    "postop": ["rwaf", "hrs", "vca"],
    "kit": ["rwaf", "hrs", "merck"],
    "repro": ["rwaf", "hrs", "merck"],
}

SIGN_PAGES = [
    {"slug": slug, "sign": sign, "category": category, "go": go}
    for slug, sign, category, go in (row.split("|", 3) for row in SIGN_ROWS.splitlines())
]

STYLE = """:root{--pine:#1A472A;--pine-deep:#0D2718;--pine-2:#2E6B3E;--pine-3:#DCEBDD;--cream:#FAFAF5;--paper:#FFFFFF;--ink:#181B18;--muted:#5E6A62;--quiet:#89938B;--border:#DCE4DC;--amber:#C4833B;--amber-bg:#FFF8F0;--red:#A93B32;--red-bg:#FDF1EE;--blue:#315D75;--blue-bg:#E9F2F5;--shadow:0 18px 60px rgba(28,42,32,.12)}*{box-sizing:border-box;margin:0;padding:0}body{background:var(--cream);color:var(--ink);font-family:system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;font-size:16px;line-height:1.65}a{color:var(--pine-2);text-decoration:none}a:hover{text-decoration:underline}.mono,.eyebrow,.pill,.crumb,.nav-links a,.source-link{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;text-transform:uppercase;letter-spacing:.1em}h1,h2,h3,.brand{font-family:Georgia,serif;letter-spacing:0;line-height:1.2;color:var(--pine-deep)}.topbar{position:sticky;top:0;z-index:50;background:rgba(26,71,42,.97);border-bottom:1px solid rgba(255,255,255,.1)}.nav{width:min(1080px,calc(100% - 36px));margin:0 auto;min-height:56px;display:flex;align-items:center;justify-content:space-between;gap:18px}.brand{color:#fff;font-size:19px;white-space:nowrap}.brand span{color:rgba(255,255,255,.5);font-family:system-ui,sans-serif;font-size:11px;margin-left:8px}.nav-links{display:flex;gap:16px;overflow-x:auto;scrollbar-width:none}.nav-links a{color:rgba(255,255,255,.82);font-size:11px;white-space:nowrap}.wrap{width:min(900px,calc(100% - 36px));margin:0 auto;padding:34px 0 80px}.crumb{font-size:11px;color:var(--quiet);margin-bottom:18px}.eyebrow{font-size:11px;color:var(--amber);margin-bottom:10px}h1{font-size:clamp(30px,5vw,46px);margin-bottom:14px}h2{font-size:25px;margin:38px 0 12px}p{margin-bottom:14px}.lede{font-size:18px;color:var(--muted)}.answer{background:var(--paper);border:1px solid var(--border);border-left:4px solid var(--pine-2);border-radius:14px;padding:22px 24px;margin:22px 0;box-shadow:var(--shadow)}.callout{border-radius:14px;padding:20px 22px;margin:20px 0}.callout.now{background:var(--red-bg);border:1px solid #E7C4BE}.callout.today{background:var(--amber-bg);border:1px solid #EAD7BC}.callout h3{margin-top:0}.callout.now h3{color:var(--red)}.callout.today h3{color:var(--amber)}ul{margin:0 0 16px 22px}li{margin-bottom:7px}.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:12px;list-style:none;margin-left:0}.cards li,.card{background:var(--paper);border:1px solid var(--border);border-radius:14px;padding:16px 18px}.cards a{font-weight:700;color:var(--pine-deep)}table{width:100%;border-collapse:collapse;background:#fff}td,th{border:1px solid var(--border);padding:12px;text-align:left;vertical-align:top}details{background:var(--paper);border:1px solid var(--border);border-radius:12px;padding:0;margin-bottom:10px;overflow:hidden}summary{cursor:pointer;padding:15px 18px;font-weight:700}details p{padding:14px 18px 4px}.source-links{display:flex;flex-wrap:wrap;gap:10px;margin-top:10px}.source-link{font-size:11px;background:var(--pine-3);color:var(--pine-deep);padding:7px 12px;border-radius:999px}.reviewed{font-size:13px;color:var(--quiet);border-top:1px solid var(--border);margin-top:34px;padding-top:16px}.footer{background:var(--pine-deep);color:rgba(255,255,255,.66);font-size:12px;line-height:1.7;padding:30px 0}.disclaimer{background:var(--blue-bg);border:1px solid #C9DEE7;border-radius:12px;padding:14px 18px;font-size:14px;color:var(--blue);margin:22px 0}"""


def source_links(keys):
    return "".join(
        f'<a class="source-link" href="{escape(SOURCES[k][1])}" target="_blank" rel="noreferrer">{escape(SOURCES[k][0])}</a>'
        for k in keys
    )


def cfg(locale):
    merged = dict(LOCALES["en"])
    merged.update(LOCALES[locale])
    return merged


def sign_label(sign, locale):
    if locale == "en":
        return sign
    for old, new in PHRASE_REPLACEMENTS.get(locale, []):
        if sign == old:
            return new
    out = sign
    for old, new in PHRASE_REPLACEMENTS.get(locale, []):
        out = out.replace(old, new)
    return out


def go_text(item, locale):
    if locale == "en":
        return item["go"]
    sign = sign_label(item["sign"], locale)
    templates = CATEGORY_GO.get(locale, {})
    template = templates.get(item["category"], templates.get("illness", "{sign} requires veterinary guidance."))
    return template.format(sign=sign)


def local_path(slug, locale="en"):
    prefix = LOCALES[locale]["prefix"]
    if prefix:
        return f"/{prefix}/{slug}/" if slug else f"/{prefix}/"
    return f"/{slug}/" if slug else "/"


def local_url(slug, locale="en"):
    return f"{BASE}{local_path(slug, locale)}"


def localize_href(href, locale):
    if locale == "en" or not href.startswith("/"):
        return href
    if href == "/":
        return f"/{LOCALES[locale]['prefix']}/"
    if href.startswith("/#"):
        return f"/{LOCALES[locale]['prefix']}/{href[1:]}"
    match = re.fullmatch(r"/([^/#?]+)/?(#.*)?", href)
    if match:
        return f"/{LOCALES[locale]['prefix']}/{match.group(1)}/{match.group(2) or ''}"
    return href


def language_links(slug, locale):
    parts = []
    for code, data in LOCALES.items():
        if code == locale:
            parts.append(f"<strong>{escape(data['label'])}</strong>")
        else:
            parts.append(f'<a href="{escape(local_path(slug, code))}">{escape(data["label"])}</a>')
    return '<p class="mono" style="font-size:11px;color:var(--quiet);margin:0 0 16px">' + " &middot; ".join(parts) + "</p>"


def alternate_head_links(slug, locale):
    tags = [f'<link rel="canonical" href="{escape(local_url(slug, locale))}">']
    for code, data in LOCALES.items():
        tags.append(f'<link rel="alternate" hreflang="{escape(data["hreflang"])}" href="{escape(local_url(slug, code))}">')
    tags.append(f'<link rel="alternate" hreflang="x-default" href="{escape(local_url(slug, "en"))}">')
    return "\n".join(tags)


def bullet_list(items):
    return "".join(f"<li>{escape(item)}</li>" for item in items)


def localized_bullets(key, locale, sign=None):
    data = cfg(locale)
    items = data.get(key, LOCALES["en"][key])
    if sign:
        items = [item.format(sign=sign) for item in items]
    return bullet_list(items)


def schema_json(title, meta, url, item=None, source_keys=None, locale="en"):
    citations = [SOURCES[k][1] for k in (source_keys or ["rwaf", "hrs", "merck"])]
    if item:
        data = cfg(locale)
        sign = sign_label(item["sign"], locale)
        return json.dumps([
            {
                "@context": "https://schema.org",
                "@type": "MedicalWebPage",
                "name": title,
                "description": meta,
                "url": url,
                "inLanguage": data["lang"],
                "audience": {"@type": "Audience", "audienceType": "rabbit owners"},
                "about": {"@type": "MedicalCondition", "name": data["title_pattern"].format(sign=sign)},
                "publisher": {"@type": "Organization", "name": "RabbitEmergency.com", "url": f"{BASE}/"},
                "citation": citations,
            },
            {
                "@context": "https://schema.org",
                "@type": "FAQPage",
                "mainEntity": [
                    {"@type": "Question", "name": title, "acceptedAnswer": {"@type": "Answer", "text": go_text(item, locale)}},
                    {"@type": "Question", "name": data["what_not"], "acceptedAnswer": {"@type": "Answer", "text": data["product_warning"]}},
                    {"@type": "Question", "name": data["tell_vet"], "acceptedAnswer": {"@type": "Answer", "text": data["call_action"]}},
                ],
            },
        ], ensure_ascii=False)
    data = cfg(locale)
    return json.dumps({
        "@context": "https://schema.org",
        "@type": "MedicalWebPage",
        "name": title,
        "description": meta,
        "url": url,
        "inLanguage": data["lang"],
        "audience": {"@type": "Audience", "audienceType": "rabbit owners"},
        "publisher": {"@type": "Organization", "name": "RabbitEmergency.com", "url": f"{BASE}/"},
        "citation": citations,
        "mainEntity": {"@type": "ItemList", "numberOfItems": 100},
    }, ensure_ascii=False)


def page_shell(title, meta, slug, body, schema, locale="en"):
    data = cfg(locale)
    return f"""<!DOCTYPE html>
<html lang="{escape(data["lang"])}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="robots" content="index, follow, max-image-preview:large">
<title>{escape(title)}</title>
<meta name="description" content="{escape(meta)}">
{alternate_head_links(slug, locale)}
<meta property="og:type" content="article">
<meta property="og:title" content="{escape(title)}">
<meta property="og:description" content="{escape(meta)}">
<meta property="og:url" content="{escape(local_url(slug, locale))}">
<meta name="twitter:card" content="summary_large_image">
<style>{STYLE}</style>
<script type="application/ld+json">{schema}</script>
</head>
<body>
<div class="topbar"><nav class="nav"><a class="brand" href="{escape(local_path("", locale).rstrip("/") or "/")}">RabbitEmergency<span>.com {escape(data["brand_tail"])}</span></a><div class="nav-links"><a href="{escape(local_path("rabbit-emergency-signs", locale))}">{escape(data["signs"])}</a><a href="{escape(local_path("rabbit-not-eating-or-pooping", locale))}">{escape(data["not_eating"])}</a><a href="{escape(local_path("rabbit-collapsed-in-heat", locale))}">{escape(data["heatstroke"])}</a><a href="{escape(local_path("rabbit-head-tilt", locale))}">{escape(data["head_tilt"])}</a><a href="{escape(localize_href("/#find-vet", locale))}">{escape(data["find_vet"])}</a></div></nav></div>
<main class="wrap">{body}</main>
<footer class="footer"><div class="wrap" style="padding:0">{escape(data["footer"])}</div></footer>
</body>
</html>
"""


def sign_page(item, locale="en"):
    data = cfg(locale)
    sign = sign_label(item["sign"], locale)
    title = data["title_pattern"].format(sign=sign)
    meta = data["meta_pattern"].format(sign=sign)
    source_keys = SIGN_SOURCES[item["category"]]
    schema = schema_json(title, meta, local_url(item["slug"], locale), item, source_keys, locale)
    related = "".join(
        f'<li><a href="{escape(localize_href(href, locale))}">{escape(label)}</a></li>'
        for label, href in data["related"]
    )
    body = f"""<div class="crumb"><a href="{escape(local_path("", locale))}">{escape(data["home"])}</a> &rsaquo; <a href="{escape(local_path("rabbit-emergency-signs", locale))}">{escape(data["hub_label"])}</a></div>
{language_links(item["slug"], locale)}
<div class="eyebrow">{escape(data["guide_label"])}</div>
<h1>{escape(title)}</h1>
<p class="lede">{escape(data["lede"])}</p>
<div class="disclaimer"><strong>{escape(data["disclaimer"])}</strong></div>
<div class="answer"><h2>{escape(data["short_answer"])}</h2><p>{escape(go_text(item, locale))} {escape(data["product_warning"])}</p></div>
<h2>{escape(data["decision_table"])}</h2>
<table><thead><tr><th>{escape(data["tier"])}</th><th>{escape(data["what_it_means"].format(sign=sign))}</th><th>{escape(data["action"])}</th></tr></thead><tbody>
<tr><td><strong>{escape(data["go_now"])}</strong></td><td>{escape(go_text(item, locale))}</td><td>{escape(data["go_action"])}</td></tr>
<tr><td><strong>{escape(data["call_today"])}</strong></td><td>{escape(data["call_meaning"])}</td><td>{escape(data["call_action"])}</td></tr>
<tr><td><strong>{escape(data["monitor"])}</strong></td><td>{escape(data["monitor_meaning"])}</td><td>{escape(data["monitor_action"])}</td></tr>
</tbody></table>
<div class="callout now"><h3>{escape(data["go_now_if"])}</h3><ul>{localized_bullets("go_now_if_bullets", locale)}</ul></div>
<div class="callout today"><h3>{escape(data["call_today_if"])}</h3><ul>{localized_bullets("call_today_bullets", locale)}</ul></div>
<h2>{escape(data["what_not"])}</h2><ul>{localized_bullets("what_not_bullets", locale)}</ul>
<h2>{escape(data["tell_vet"])}</h2><div class="card"><ul>{localized_bullets("tell_vet_bullets", locale, sign)}</ul></div>
<h2>{escape(data["review_status"])}</h2><p class="reviewed">{escape(data["review"])}</p>
<h2>{escape(data["sources"])}</h2><div class="source-links">{source_links(source_keys)}</div>
<h2>{escape(data["helpful"])}</h2><ul>{related}</ul>"""
    out = ROOT / LOCALES[locale]["prefix"] / item["slug"] / "index.html" if locale != "en" else ROOT / item["slug"] / "index.html"
    write(out, page_shell(title, meta, item["slug"], body, schema, locale))


def signs_hub(locale="en"):
    data = cfg(locale)
    title = data["hub_title"]
    meta = data["hub_meta"]
    cards = "".join(f'<li><a href="{escape(local_path(item["slug"], locale))}">Rabbit {escape(sign_label(item["sign"], locale))}</a><p>{escape(go_text(item, locale))}</p></li>' for item in SIGN_PAGES[:100])
    schema = schema_json(title, meta, local_url("rabbit-emergency-signs", locale), locale=locale)
    body = f"""<div class="crumb"><a href="{escape(local_path("", locale))}">{escape(data["home"])}</a> &rsaquo; {escape(data["hub_label"])}</div>
{language_links("rabbit-emergency-signs", locale)}
<div class="eyebrow">{escape(data["hub_eyebrow"])}</div>
<h1>{escape(title)}</h1>
<p class="lede">{escape(data["hub_lede"])}</p>
<div class="answer"><h2>{escape(data["short_answer"])}</h2><p>{escape(data["hub_answer"])}</p></div>
<h2>{escape(data["go_now_signs"])}</h2><ul>{localized_bullets("go_now_bullets", locale)}</ul>
<h2>{escape(data["hub_cards"])}</h2><ul class="cards">{cards}</ul>
<h2>{escape(data["review_status"])}</h2><p class="reviewed">{escape(data["review"])}</p>
<h2>{escape(data["sources"])}</h2><div class="source-links">{source_links(["rwaf", "hrs", "merck", "vca"])}</div>"""
    out = ROOT / LOCALES[locale]["prefix"] / "rabbit-emergency-signs" / "index.html" if locale != "en" else ROOT / "rabbit-emergency-signs" / "index.html"
    write(out, page_shell(title, meta, "rabbit-emergency-signs", body, schema, locale))


def write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def scrub_unverified_review_claims():
    for path in ROOT.rglob("*.html"):
        text = path.read_text(encoding="utf-8")
        original = text
        text = re.sub(r',?\s*"lastReviewed"\s*:\s*"[^"]*"', "", text)
        text = re.sub(r',?\s*"reviewedBy"\s*:\s*\[.*?\]', "", text, flags=re.S)
        text = re.sub(r',?\s*"reviewedBy"\s*:\s*\{.*?\}', "", text, flags=re.S)
        text = re.sub(r',?\s*"dateReviewed"\s*:\s*"[^"]*"', "", text)
        text = re.sub(r'<meta[^>]+name=["\']last-reviewed["\'][^>]*>\s*', "", text)
        text = text.replace("reviewed by our exotic veterinary advisory board", "source-cited and pending named veterinary review")
        text = text.replace("reviewed by an exotic veterinary advisory board", "source-cited and pending named veterinary review")
        text = text.replace("is reviewed by an exotic veterinary advisory board", "is source-cited and pending named veterinary review")
        text = text.replace("reviewed by an exotic veterinary advisory board against RWAF, House Rabbit Society, and exotic small-mammal medicine standards", "source-cited and pending named veterinary review against RWAF, House Rabbit Society, and exotic small-mammal medicine standards")
        text = text.replace("reviewed against ISFM, AAFP, and AAHA cat-care standards by our regional veterinary advisory board", "source-cited and pending named veterinary review")
        text = re.sub(r'<a href="/veterinary-reviewers/">.*?</a>', '<a href="/veterinary-review/">Review policy</a>', text)
        text = re.sub(r'<a href="/ja/veterinary-reviewers/">.*?</a>', '<a href="/ja/veterinary-review/">レビューポリシー</a>', text)
        text = re.sub(r'<a href="/zh-tw/veterinary-reviewers/">.*?</a>', '<a href="/zh-tw/veterinary-review/">審閱政策</a>', text)
        text = re.sub(r'<a href="/th/veterinary-reviewers/">.*?</a>', '<a href="/th/veterinary-review/">นโยบายการตรวจทาน</a>', text)
        text = re.sub(r'<div class="reviewed">.*?</div>', f'<div class="reviewed">Review status: {escape(REVIEW)}</div>', text, flags=re.S)
        text = re.sub(r'Reviewed by the RabbitEmergency\.com exotic veterinary advisory board.*?Last reviewed: 2026-06-03\.', f'Review status: {REVIEW}', text)
        text = re.sub(r'\s+"reviewedBy"\s*:\s*\[.*?\]\s*,?', "", text, flags=re.S)
        text = re.sub(r'\s+"reviewedBy"\s*:\s*\{.*?\}\s*,?', "", text, flags=re.S)
        text = re.sub(r'\s+"lastReviewed"\s*:\s*"[^"]*"\s*,?', "", text)
        text = re.sub(r'\s+"dateReviewed"\s*:\s*"[^"]*"\s*,?', "", text)
        text = re.sub(r',\s*([}\]])', r'\1', text)
        if text != original:
            path.write_text(text, encoding="utf-8")


def update_sitemap():
    sitemap_path = ROOT / "sitemap.xml"
    urls = []
    for path in ROOT.glob("**/index.html"):
        if ".git" in path.parts or any(pattern in path.as_posix() for pattern in UNVERIFIED_REVIEWER_PATTERNS):
            continue
        rel = path.parent.relative_to(ROOT).as_posix()
        urls.append(f"{BASE}/" if rel == "." else f"{BASE}/{rel}/")
    for locale in LOCALES:
        urls.append(local_url("rabbit-emergency-signs", locale))
        urls += [local_url(item["slug"], locale) for item in SIGN_PAGES[:100]]
    entries = []
    for url in sorted(set(urls)):
        priority = "0.9" if url.endswith("/rabbit-emergency-signs/") or url.endswith("-emergency-signs/") else ("1.0" if url == f"{BASE}/" else "0.8")
        changefreq = "weekly" if url == f"{BASE}/" else "monthly"
        entries.append(f"<url><loc>{url}</loc><lastmod>{LASTMOD}</lastmod><changefreq>{changefreq}</changefreq><priority>{priority}</priority></url>")
    sitemap_path.write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + "".join(entries) + "</urlset>\n", encoding="utf-8")


def update_llms():
    path = ROOT / "llms.txt"
    text = path.read_text(encoding="utf-8") if path.exists() else "# RabbitEmergency.com\n"
    text = "\n".join(
        line for line in text.splitlines()
        if not any(pattern in line for pattern in UNVERIFIED_REVIEWER_PATTERNS)
    ) + "\n"
    text = text.replace(
        "RabbitEmergency.com guidance is reviewed by an exotic veterinary advisory board against RWAF, House Rabbit Society, and exotic small-mammal medicine standards.",
        "RabbitEmergency.com guidance is source-cited and pending named veterinary review against RWAF, House Rabbit Society, and exotic small-mammal medicine standards.",
    )
    section = "\n## Rabbit emergency signs hub\n"
    for locale, data in LOCALES.items():
        section += f"- [{data['hub_title']}]({local_url('rabbit-emergency-signs', locale)}): 100 source-cited sign-specific triage pages for rabbit owners.\n"
    for item in SIGN_PAGES[:100]:
        section += f"- [Rabbit {item['sign']}]({local_url(item['slug'], 'en')}): {item['go']}\n"
        for locale in ("ja", "zh-tw", "th"):
            section += f"  - {LOCALES[locale]['label']}: {local_url(item['slug'], locale)}\n"
    pages = []
    for page in sorted(ROOT.glob("**/index.html")):
        if ".git" in page.parts or any(pattern in page.as_posix() for pattern in UNVERIFIED_REVIEWER_PATTERNS):
            continue
        rel = page.parent.relative_to(ROOT).as_posix()
        url = f"{BASE}/" if rel == "." else f"{BASE}/{rel}/"
        html = page.read_text(encoding="utf-8")
        title_match = re.search(r"<title>(.*?)</title>", html, flags=re.S)
        h1_match = re.search(r"<h1[^>]*>(.*?)</h1>", html, flags=re.S)
        label = title_match.group(1) if title_match else (h1_match.group(1) if h1_match else url)
        label = re.sub(r"<.*?>", "", label).strip()
        pages.append((url, label))
    all_pages = "\n## All current indexable pages\n" + "".join(
        f"- [{label}]({url})\n" for url, label in pages
    )
    text = re.sub(r"\n## Rabbit emergency signs hub\n.*?(?=\n## |\Z)", "", text, flags=re.S)
    text = re.sub(r"\n## All current indexable pages\n.*?(?=\n## |\Z)", "", text, flags=re.S)
    text = text.rstrip() + "\n" + section + all_pages
    path.write_text(text, encoding="utf-8")


def update_homepage_links():
    for locale in LOCALES:
        path = ROOT / LOCALES[locale]["prefix"] / "index.html" if locale != "en" else ROOT / "index.html"
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        href = local_path("rabbit-emergency-signs", locale)
        if href not in text:
            text = text.replace('<a href="#symptoms">Symptoms</a>', f'<a href="{href}">{escape(LOCALES[locale]["signs"])}</a><a href="#symptoms">Symptoms</a>')
            text = text.replace('<a class="button primary" href="#symptoms">Check emergency signs</a>', f'<a class="button primary" href="{href}">Check emergency signs</a>')
            text = re.sub(r'(<div[^>]*class="nav-links"[^>]*>)', rf'\1<a href="{href}">{escape(LOCALES[locale]["signs"])}</a>', text, count=1)
        label = re.escape(LOCALES[locale]["signs"])
        text = re.sub(
            rf'(<a href="{re.escape(href)}">{label}</a>)\s*(<a href="{re.escape(href)}">{label}</a>)+',
            rf'\1',
            text,
        )
        path.write_text(text, encoding="utf-8")


def main():
    if len(SIGN_PAGES) < 100:
        raise SystemExit(f"Need at least 100 sign pages, got {len(SIGN_PAGES)}")
    for item in SIGN_PAGES[:100]:
        for locale in LOCALES:
            sign_page(item, locale)
    for locale in LOCALES:
        signs_hub(locale)
    scrub_unverified_review_claims()
    update_sitemap()
    update_llms()
    update_homepage_links()


if __name__ == "__main__":
    main()
