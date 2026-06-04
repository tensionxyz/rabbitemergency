from datetime import date
from html import escape
from pathlib import Path
import json

from generate_rabbit_sign_pages import BASE, LOCALES, STYLE, local_path, local_url, alternate_head_links, scrub_unverified_review_claims
from tools.html_sanitizer import sanitize_html

ROOT = Path(__file__).parent
LASTMOD = date.today().isoformat()

TEXT = {
    "en": {
        "home": "Home",
        "title": "Rabbit emergency vet in {city}: real clinics to call first",
        "meta": "Real rabbit-savvy, exotic, and emergency veterinary clinics in {city}, with source links and call-before-travel cautions.",
        "eyebrow": "Real clinic directory",
        "h1": "Rabbit emergency vet in {city}",
        "lede": "These are source-cited public clinic listings for emergency call planning. Call before travel to confirm address, emergency intake, and whether a rabbit-savvy or exotic vet is on duty now.",
        "verification": "Clinic verification",
        "verified": "Last verified",
        "method": "Verification method: public clinic or institution pages checked; third-party sources are used only where no official clinic page was found.",
        "travel": "Before travel: call ahead. A 24-hour hospital may still need to confirm whether rabbit/exotic coverage is available at that moment.",
        "emergency": "Go now if your rabbit has red-flag signs, but call while preparing to travel.",
        "clinics": "Clinics to call",
        "call": "What to say when you call",
        "call_items": [
            "I have a rabbit emergency. Do you treat rabbits or exotic small mammals right now?",
            "State the main sign and how long it has been happening.",
            "Ask whether to come immediately, what to bring, and whether another clinic is better if no rabbit vet is on duty.",
            "Confirm the address, phone number, after-hours fee, and intake process.",
        ],
        "sources": "Sources",
        "related": "Related city and region pages",
        "review": "Source-cited clinic directory; veterinary review pending.",
        "footer": "RabbitEmergency.com is educational and does not provide veterinary diagnosis or treatment.",
    },
    "ja": {
        "home": "ホーム",
        "title": "{city}のうさぎ救急動物病院: まず電話する実在クリニック",
        "meta": "{city}で連絡できる実在のうさぎ対応・エキゾチック対応・救急動物病院。出典リンクと事前電話の注意点つき。",
        "eyebrow": "実在クリニック一覧",
        "h1": "{city}のうさぎ救急動物病院",
        "lede": "公表情報と出典に基づく、救急時の電話確認用クリニック一覧です。移動前に必ず電話し、住所、救急受付、うさぎ・エキゾチック対応獣医の在院を確認してください。",
        "verification": "クリニック確認",
        "verified": "最終確認",
        "method": "確認方法: クリニックまたは機関の公開ページを確認。公式ページが見つからない場合のみ第三者情報を補助的に使用。",
        "travel": "移動前: 必ず電話してください。24時間病院でも、その時点でうさぎ・エキゾチック対応が可能か確認が必要です。",
        "emergency": "赤旗サインがある場合は急いで受診準備をしながら電話してください。",
        "clinics": "電話候補",
        "call": "電話で伝えること",
        "call_items": [
            "うさぎの救急です。今うさぎ、または小型エキゾチックを診られますか。",
            "主症状と、いつから続いているかを伝える。",
            "すぐ行くべきか、何を持参するか、対応獣医がいない場合の紹介先を聞く。",
            "住所、電話番号、時間外料金、受付方法を確認する。",
        ],
        "sources": "出典",
        "related": "関連する都市・地域ページ",
        "review": "出典つきのクリニック一覧。獣医師レビューは準備中です。",
        "footer": "RabbitEmergency.comは教育目的であり、獣医師による診断や治療を提供しません。",
    },
    "zh-tw": {
        "home": "首頁",
        "title": "{city}兔子急症獸醫：先致電確認的真實診所",
        "meta": "{city}真實兔子、特殊寵物與急症獸醫診所，附來源連結與出發前電話確認提醒。",
        "eyebrow": "真實診所目錄",
        "h1": "{city}兔子急症獸醫",
        "lede": "這些是附來源的公開診所資料，用於急症時先致電確認。出發前請先致電確認地址、急症收治，以及當下是否有熟悉兔子或特殊寵物的獸醫值班。",
        "verification": "診所查核",
        "verified": "最後查核",
        "method": "查核方式：檢查診所或機構公開頁面；只有找不到官方頁時才使用第三方來源補充。",
        "travel": "出發前：務必致電。即使是24小時醫院，也需要確認當下是否能處理兔子或特殊寵物。",
        "emergency": "若兔子有紅旗症狀，請一邊準備出門一邊致電。",
        "clinics": "可致電診所",
        "call": "電話中要說什麼",
        "call_items": [
            "我的兔子有急症。現在可以看兔子或特殊小型哺乳動物嗎？",
            "說明主要症狀和已經持續多久。",
            "詢問是否立即前往、要帶什麼，以及若沒有兔科獸醫值班應去哪裡。",
            "確認地址、電話、夜間費用與急症掛號流程。",
        ],
        "sources": "來源",
        "related": "相關城市與地區頁面",
        "review": "有來源引用的診所目錄；獸醫審閱待定。",
        "footer": "RabbitEmergency.com為教育資訊，不提供獸醫診斷或治療。",
    },
    "th": {
        "home": "หน้าแรก",
        "title": "สัตวแพทย์ฉุกเฉินสำหรับกระต่ายใน{city}: คลินิกจริงที่ควรโทรก่อน",
        "meta": "รายชื่อคลินิกสัตวแพทย์จริงใน{city}สำหรับกระต่าย สัตว์พิเศษ และกรณีฉุกเฉิน พร้อมแหล่งข้อมูลและคำเตือนให้โทรก่อนเดินทาง",
        "eyebrow": "รายชื่อคลินิกจริง",
        "h1": "สัตวแพทย์ฉุกเฉินสำหรับกระต่ายใน{city}",
        "lede": "รายชื่อนี้อ้างอิงข้อมูลคลินิกจากแหล่งสาธารณะเพื่อใช้โทรยืนยันในกรณีฉุกเฉิน ก่อนเดินทางให้โทรยืนยันที่อยู่ การรับเคสฉุกเฉิน และว่ามีสัตวแพทย์ที่ดูแลกระต่ายหรือสัตว์พิเศษอยู่ในเวลานั้นหรือไม่",
        "verification": "การตรวจสอบคลินิก",
        "verified": "ตรวจสอบล่าสุด",
        "method": "วิธีตรวจสอบ: ตรวจหน้าเว็บสาธารณะของคลินิกหรือสถาบัน ใช้แหล่งข้อมูลภายนอกเฉพาะเมื่อไม่พบหน้าเว็บทางการ",
        "travel": "ก่อนเดินทาง: โทรก่อนเสมอ โรงพยาบาล 24 ชั่วโมงก็อาจต้องยืนยันว่ามีทีมที่ดูแลกระต่ายหรือสัตว์พิเศษในเวลานั้น",
        "emergency": "ถ้ามีสัญญาณอันตราย ให้เตรียมเดินทางพร้อมโทรหาคลินิกทันที",
        "clinics": "คลินิกที่ควรโทร",
        "call": "สิ่งที่ควรพูดตอนโทร",
        "call_items": [
            "กระต่ายของฉันมีเหตุฉุกเฉิน ตอนนี้รับดูแลกระต่ายหรือสัตว์เลี้ยงพิเศษขนาดเล็กไหม",
            "บอกอาการหลักและเกิดมานานเท่าไร",
            "ถามว่าควรไปทันทีไหม ต้องนำอะไรไป และถ้าไม่มีสัตวแพทย์กระต่ายควรไปที่ไหน",
            "ยืนยันที่อยู่ เบอร์โทร ค่าบริการนอกเวลา และขั้นตอนรับเคสฉุกเฉิน",
        ],
        "sources": "แหล่งข้อมูล",
        "related": "หน้าเมืองและภูมิภาคที่เกี่ยวข้อง",
        "review": "รายชื่อคลินิกอ้างอิงแหล่งข้อมูล; การตรวจทานโดยสัตวแพทย์อยู่ระหว่างดำเนินการ",
        "footer": "RabbitEmergency.comเป็นข้อมูลเพื่อการศึกษา ไม่ใช่การวินิจฉัยหรือการรักษาโดยสัตวแพทย์",
    },
}

CLINICS = {
    "hk_tai_wai": {
        "name": "Tai Wai Small Animal & Exotic Hospital",
        "area": "Tai Wai · Shop C-D, G/F, Lap Wo Building, 69-75 Chik Shun Street",
        "phone": "+852 2687 1030",
        "tags": ["24-hour", "exotic/rabbit", "New Territories"],
        "note": "Official site states 24-hour medical and surgical care for cats, dogs, and all exotic pets with a vet always on site.",
        "url": "https://www.taiwaiexotic.com/en-hk",
        "source": "taiwaiexotic.com",
    },
    "hk_concordia": {
        "name": "Concordia Pet Care",
        "area": "Happy Valley · 5-7 Blue Pool Road",
        "phone": "+852 2679 1000",
        "tags": ["24-hour", "exotic/rabbit", "Hong Kong Island"],
        "note": "Official site lists 24-hour services, exotic specialist services, and a dedicated exotic-animal contact path.",
        "url": "https://en.concordiapetcare.com/",
        "source": "concordiapetcare.com",
    },
    "hk_spca": {
        "name": "SPCA Hong Kong Centre 24 Hour Animal Hospital",
        "area": "Wan Chai · 5 Wan Shing Street",
        "phone": "+852 2802 0501 / emergency hotline +852 2711 1000",
        "tags": ["24-hour", "exotics ward", "Hong Kong Island"],
        "note": "SPCA lists a 24-hour animal hospital, 24-hour emergency service, an exotics ward, and rabbit/pocket-pet medicine pages.",
        "url": "https://www.spca.org.hk/contact/spca-centres/hong-kong-centre-hq/",
        "source": "spca.org.hk",
    },
    "hk_cityu": {
        "name": "CityU Veterinary Medical Centre",
        "area": "Sham Shui Po · 339 Lai Chi Kok Road",
        "phone": "+852 3650 3200",
        "tags": ["24-hour emergency", "referral", "Kowloon"],
        "note": "CityU VMC lists dedicated 24-hour emergency services. Call to confirm rabbit or exotic-pet coverage before travel.",
        "url": "https://cityuvmc.com.hk/en/services/",
        "source": "cityuvmc.com.hk",
    },
    "hk_cityvet": {
        "name": "CITYVET Small Animal and Exotics Hospital",
        "area": "Tsuen Wan / Yuen Long",
        "phone": "+852 2623 5500 / +852 2477 9990",
        "tags": ["exotic/rabbit", "24-hour phone", "New Territories"],
        "note": "Official site lists pet and exotic consultations, rabbits among exotic species, and 24-hour telephone service for Tsuen Wan and Yuen Long branches.",
        "url": "https://www.cityvet.com.hk/en/",
        "source": "cityvet.com.hk",
    },
    "tokyo_mitaka": {
        "name": "Mitaka Veterinary Medical Group / Japan Veterinary Medical Group",
        "area": "Musashino · 2-6-4 Nakamachi",
        "phone": "0422-54-5181 / night emergency 080-5487-6682",
        "tags": ["24-hour", "rabbits listed", "West Tokyo"],
        "note": "Official site states 24-hour emergency care, 365 days a year, and includes rabbit transport guidance.",
        "url": "https://www.pet-hospital.org/en/",
        "source": "pet-hospital.org",
    },
    "tokyo_daktari": {
        "name": "Daktari Animal Hospital Tokyo Medical Center",
        "area": "Shirokanedai, Minato-ku · 5-14-1 Shirokanedai Apartment 2F",
        "phone": "03-5420-0012",
        "tags": ["24/7 emergency", "general emergency", "Central Tokyo"],
        "note": "Official Japanese site states 24-hour, 365-day emergency outpatient care. Call to confirm rabbit/exotic handling.",
        "url": "https://www.daktari.gr.jp/",
        "source": "daktari.gr.jp",
    },
    "tokyo_miwa": {
        "name": "みわエキゾチック動物病院 / Japan Exotic Animal Medical Center",
        "area": "Komagome, Toshima-ku · 1-25-5 Komagome",
        "phone": "",
        "tags": ["exotic/rabbit", "specialist", "appointment"],
        "note": "Public professional sources identify Miwa Exotic Animal Hospital as a Tokyo exotic-animal hospital; use for specialist routing and call before travel.",
        "url": "https://www.jstage.jst.go.jp/article/jvma/76/11/76_e318/_pdf",
        "source": "jstage.jst.go.jp",
    },
    "taipei_lumos": {
        "name": "牧光特殊寵物專科醫院 (Lumos Exotic Animal Clinic)",
        "area": "Taipei",
        "phone": "",
        "tags": ["exotic/rabbit", "specialist", "appointment"],
        "note": "Official site describes Lumos as a special-pet specialist hospital offering specialty consultations, medical care, and hospitalization.",
        "url": "https://lumosvet.weebly.com/",
        "source": "lumosvet.weebly.com",
    },
    "taipei_mumu": {
        "name": "沐沐特寵動物醫院 (Mumu Exotic Animal Hospital)",
        "area": "Taipei · 中山區龍江路78號",
        "phone": "",
        "tags": ["exotic/rabbit", "appointment-only", "Zhongshan"],
        "note": "Public directory describes Mumu as a rodents/rabbits/birds/reptiles specialty hospital. It is not listed as 24-hour emergency.",
        "url": "https://pethealth.com.tw/tdcpt_directories/%E6%B2%90%E6%B2%90%E7%89%B9%E5%AF%B5%E5%8B%95%E7%89%A9%E9%86%AB%E9%99%A2/",
        "source": "pethealth.com.tw",
    },
    "taipei_daan": {
        "name": "大安動物醫院 (Da'an Animal Hospital)",
        "area": "Taipei · 新生南路一段162號1樓",
        "phone": "02-2363-2020",
        "tags": ["24-hour emergency", "general emergency", "Da'an"],
        "note": "Official site identifies the hospital as a 24-hour animal emergency hospital. Call first because rabbit/exotic coverage is not confirmed overnight.",
        "url": "https://daan-vet.com/",
        "source": "daan-vet.com",
    },
    "taipei_prospect": {
        "name": "展望動物醫院 (Prospect Veterinary Hospital)",
        "area": "Wanhua · 台北市萬華區中華路二段2號",
        "phone": "02-2388-0122",
        "tags": ["24-hour emergency", "general emergency", "Wanhua"],
        "note": "Official site lists 24-hour emergency and critical-care equipment. Call first because public rabbit/exotic coverage is not confirmed.",
        "url": "https://www.prospect-vet.com/",
        "source": "prospect-vet.com",
    },
    "taipei_national": {
        "name": "全國動物醫院 台北分院 (National Veterinary Hospital Taipei Branch)",
        "area": "Taipei",
        "phone": "",
        "tags": ["24-hour dog/cat ICU", "rabbit care article", "call first"],
        "note": "Official branch page lists 24H emergency for dogs and cats only; the chain publishes rabbit health information. Use only after calling to confirm rabbit intake.",
        "url": "https://www.vet.com.tw/store_detail.php?Key=3&Mode=Pre&cID=0",
        "source": "vet.com.tw",
    },
    "taipei_sensation": {
        "name": "上弦動物醫院 (Sensation Animal Hospital)",
        "area": "Linkou / New Taipei",
        "phone": "",
        "tags": ["24-hour emergency", "New Taipei", "call first"],
        "note": "Official site describes a 24-hour emergency and ICU service for the Linkou area. Call first because rabbit/exotic coverage is not confirmed.",
        "url": "https://www.sensationah.com/",
        "source": "sensationah.com",
    },
    "sg_beecroft": {
        "name": "Beecroft Animal Specialist & Emergency Hospital",
        "area": "Alexandra · 991E Alexandra Road #01-27",
        "phone": "+65 6996 1812",
        "tags": ["24-hour", "exotic/rabbit", "Central"],
        "note": "Official site lists 24-hour emergency care and small exotic pets including rabbits.",
        "url": "https://beecroft.com.sg/",
        "source": "beecroft.com.sg",
    },
    "sg_awrc": {
        "name": "Animal Wellness Referral Centre (AWRC)",
        "area": "Bukit Timah · 200 Bukit Timah Road",
        "phone": "+65 6530 3530 / +65 9370 3530",
        "tags": ["24-hour/on-call", "exotics", "Central"],
        "note": "Official exotics page states AWRC treats exotics and gives immediate-assistance contacts for 24-hour emergency veterinary support.",
        "url": "https://www.awrc.sg/service/exotic-animals/",
        "source": "awrc.sg",
    },
    "sg_advanced": {
        "name": "Advanced VetCare Veterinary Centre",
        "area": "Bedok / Balestier",
        "phone": "6636 1788",
        "tags": ["24/7 emergency", "rabbits listed", "East/Central"],
        "note": "Official site states 24/7 emergency and critical care; FAQ says the clinic treats rabbits, birds, and other small animals.",
        "url": "https://www.advancedvetcare.sg/",
        "source": "advancedvetcare.sg",
    },
    "sg_westside": {
        "name": "Westside Emergency & Referral Hospital",
        "area": "Serangoon · 86 Serangoon Garden Way",
        "phone": "6931 0095",
        "tags": ["24-hour", "rabbit ward", "North-East"],
        "note": "Official facilities page lists 24/7 operation and a Rabbit, Cat & Small Animal Ward.",
        "url": "https://www.westsideemergency.com.sg/facilities",
        "source": "westsideemergency.com.sg",
    },
    "sg_paws": {
        "name": "Paws N' Claws Veterinary Surgery",
        "area": "Upper Thomson / Yishun",
        "phone": "",
        "tags": ["extended hours", "rabbits listed", "North"],
        "note": "Official emergency page lists rabbits among animals treated and gives extended emergency hours. Not a 24-hour hospital.",
        "url": "https://pawsnclawsvet.sg/emergency-vet-care/",
        "source": "pawsnclawsvet.sg",
    },
    "sg_birdvet": {
        "name": "Birdvet Avian & Exotics Clinic",
        "area": "Singapore",
        "phone": "",
        "tags": ["exotic/rabbit", "specialist", "appointment"],
        "note": "Official site presents Birdvet as an avian and exotics clinic and lists specialized veterinary medicine for rabbits.",
        "url": "https://www.birdvet.com.sg/",
        "source": "birdvet.com.sg",
    },
    "sg_bloom": {
        "name": "Bloom Pets Clinic",
        "area": "Boon Teck · 12 Boon Teck Road",
        "phone": "",
        "tags": ["overnight vet on-site", "rabbit listed", "Central"],
        "note": "Official clinic page lists rabbit among accepted species and says 24-hour overnight vet on-site.",
        "url": "https://bloompets.com.sg/clinic/companion-animal-surgery",
        "source": "bloompets.com.sg",
    },
    "sg_vetaffinity": {
        "name": "Vet Affinity",
        "area": "West Singapore",
        "phone": "",
        "tags": ["exotic pets", "hospitalisation", "West"],
        "note": "Official site identifies Vet Affinity as a small animal and exotic-pet clinic with hospitalisation and exotics wards. Call first for emergency intake.",
        "url": "https://www.vetaffinity.com.sg/",
        "source": "vetaffinity.com.sg",
    },
    "bkk_chula": {
        "name": "Chulalongkorn University Small Animal Teaching Hospital",
        "area": "Pathum Wan · Henry-Dunant Road",
        "phone": "+66 2218 9751 / +66 2218 9810",
        "tags": ["24-hour emergency", "exotic clinic", "Pathum Wan"],
        "note": "Chulalongkorn states the emergency clinic is open 24 hours every day and services include exotic animal medicine.",
        "url": "https://www.chula.ac.th/en/services/small-animal-teaching-hospital/",
        "source": "chula.ac.th",
    },
    "bkk_ivet": {
        "name": "iVET Animal Hospital",
        "area": "Rama 9 / West Centre",
        "phone": "085-244-7899 / 02-641-5525",
        "tags": ["24-hour", "exotic/rabbit", "Rama 9"],
        "note": "Official Exotic Pet Center page lists small mammals, rabbit surgery, and iVET Hospital 24 Hours.",
        "url": "https://www.ivethospital.com/en/content/6060/exotic-pet-center?v=1518505746",
        "source": "ivethospital.com",
    },
    "bkk_uvet": {
        "name": "UVET Animal Hospital",
        "area": "Bangkok",
        "phone": "",
        "tags": ["24-hour", "exotic pets", "Bangkok"],
        "note": "Official site states 24-hour emergency care and services for general and exotic pets.",
        "url": "https://www.uvethospital.com/",
        "source": "uvethospital.com",
    },
    "bkk_arak": {
        "name": "Arak Animal Hospital",
        "area": "Thonglor · 99 Sukhumvit Soi 55",
        "phone": "02-106-997",
        "tags": ["24-hour emergency", "Thonglor", "call first"],
        "note": "Public RBSC page for Arak states emergency services are available 24 hours for outpatient and inpatient animals. Call first to confirm rabbit/exotic coverage.",
        "url": "https://www.rbsc.org/member-benefits/arak-animal-hospital/",
        "source": "rbsc.org",
    },
    "bkk_grand": {
        "name": "Grand Avenue Pet Hospital",
        "area": "Bangkok",
        "phone": "",
        "tags": ["24-hour", "general emergency", "call first"],
        "note": "Official site describes Grand Avenue as a full-service 24/7 veterinary hospital in Bangkok. Call first to confirm rabbit/exotic coverage.",
        "url": "https://grandavenuepethospital.com/en/about-gaph/",
        "source": "grandavenuepethospital.com",
    },
    "bkk_happy": {
        "name": "Happy Pet Hospital",
        "area": "Sukhumvit / Rangsit",
        "phone": "",
        "tags": ["24-hour", "general emergency", "call first"],
        "note": "Official contact page lists Happy Pet Hospital Sukhumvit as open daily 24 hours. Call first to confirm rabbit/exotic coverage.",
        "url": "https://happypet-hospital.com/en/contact",
        "source": "happypet-hospital.com",
    },
    "bkk_setthakit": {
        "name": "Setthakit Animal Hospital",
        "area": "Bang Khae, Bangkok",
        "phone": "",
        "tags": ["24-hour", "night emergency", "call first"],
        "note": "Official site lists emergency hours and 24-hour veterinary care. Call first to confirm rabbit/exotic coverage.",
        "url": "https://www.setthakitanimalhospital.com/en/program",
        "source": "setthakitanimalhospital.com",
    },
    "bkk_vetazoo": {
        "name": "VetAzoo Exotic Pet Hospital",
        "area": "Pattaya / East-coast Thailand",
        "phone": "+66 82 662 7999",
        "tags": ["24-hour", "exotic/rabbit", "Thailand fallback"],
        "note": "Official site states exotic veterinary care for rabbits and other exotic pets is available 24 hours a day.",
        "url": "https://exoticpethospital.com/",
        "source": "exoticpethospital.com",
    },
}

PAGES = {
    "hong-kong": {
        "city": {"en": "Hong Kong", "ja": "香港", "zh-tw": "香港", "th": "ฮ่องกง"},
        "clinics": ["hk_tai_wai", "hk_concordia", "hk_spca", "hk_cityu", "hk_cityvet"],
    },
    "hong-kong-island": {
        "city": {"en": "Hong Kong Island", "ja": "香港島", "zh-tw": "香港島", "th": "เกาะฮ่องกง"},
        "clinics": ["hk_concordia", "hk_spca", "hk_cityu", "hk_tai_wai", "hk_cityvet"],
    },
    "kowloon": {
        "city": {"en": "Kowloon", "ja": "九龍", "zh-tw": "九龍", "th": "เกาลูน"},
        "clinics": ["hk_cityu", "hk_tai_wai", "hk_concordia", "hk_spca", "hk_cityvet"],
    },
    "new-territories": {
        "city": {"en": "New Territories", "ja": "新界", "zh-tw": "新界", "th": "นิวเทร์ริทอรีส์"},
        "clinics": ["hk_tai_wai", "hk_cityvet", "hk_cityu", "hk_concordia", "hk_spca"],
    },
    "tokyo": {
        "city": {"en": "Tokyo", "ja": "東京", "zh-tw": "東京", "th": "โตเกียว"},
        "clinics": ["tokyo_mitaka", "tokyo_daktari", "tokyo_miwa"],
    },
    "central-tokyo": {
        "city": {"en": "Central Tokyo", "ja": "東京都心", "zh-tw": "東京市中心", "th": "ใจกลางโตเกียว"},
        "clinics": ["tokyo_daktari", "tokyo_miwa", "tokyo_mitaka"],
    },
    "west-tokyo": {
        "city": {"en": "West Tokyo and Musashino", "ja": "東京西部・武蔵野", "zh-tw": "東京西部與武藏野", "th": "โตเกียวตะวันตกและมุซาชิโนะ"},
        "clinics": ["tokyo_mitaka", "tokyo_miwa", "tokyo_daktari"],
    },
    "taipei": {
        "city": {"en": "Taipei", "ja": "台北", "zh-tw": "台北", "th": "ไทเป"},
        "clinics": ["taipei_lumos", "taipei_mumu", "taipei_daan", "taipei_prospect", "taipei_national", "taipei_sensation"],
    },
    "taipei-daan": {
        "city": {"en": "Taipei Da'an", "ja": "台北・大安", "zh-tw": "台北大安", "th": "ไทเปต้าอัน"},
        "clinics": ["taipei_daan", "taipei_lumos", "taipei_mumu", "taipei_prospect", "taipei_national"],
    },
    "taipei-zhongshan": {
        "city": {"en": "Taipei Zhongshan", "ja": "台北・中山", "zh-tw": "台北中山", "th": "ไทเปจงซาน"},
        "clinics": ["taipei_mumu", "taipei_lumos", "taipei_daan", "taipei_prospect", "taipei_national"],
    },
    "new-taipei": {
        "city": {"en": "New Taipei", "ja": "新北", "zh-tw": "新北", "th": "นิวไทเป"},
        "clinics": ["taipei_sensation", "taipei_lumos", "taipei_mumu", "taipei_daan", "taipei_prospect"],
    },
    "singapore": {
        "city": {"en": "Singapore", "ja": "シンガポール", "zh-tw": "新加坡", "th": "สิงคโปร์"},
        "clinics": ["sg_beecroft", "sg_awrc", "sg_advanced", "sg_westside", "sg_paws", "sg_birdvet", "sg_bloom", "sg_vetaffinity"],
    },
    "central-singapore": {
        "city": {"en": "Central Singapore", "ja": "シンガポール中部", "zh-tw": "新加坡中部", "th": "สิงคโปร์ตอนกลาง"},
        "clinics": ["sg_beecroft", "sg_awrc", "sg_bloom", "sg_birdvet", "sg_advanced", "sg_westside"],
    },
    "east-singapore": {
        "city": {"en": "East Singapore", "ja": "シンガポール東部", "zh-tw": "新加坡東部", "th": "สิงคโปร์ตะวันออก"},
        "clinics": ["sg_advanced", "sg_beecroft", "sg_awrc", "sg_westside", "sg_birdvet", "sg_bloom"],
    },
    "north-singapore": {
        "city": {"en": "North Singapore", "ja": "シンガポール北部", "zh-tw": "新加坡北部", "th": "สิงคโปร์ตอนเหนือ"},
        "clinics": ["sg_paws", "sg_westside", "sg_advanced", "sg_beecroft", "sg_awrc", "sg_birdvet"],
    },
    "west-singapore": {
        "city": {"en": "West Singapore", "ja": "シンガポール西部", "zh-tw": "新加坡西部", "th": "สิงคโปร์ตะวันตก"},
        "clinics": ["sg_vetaffinity", "sg_beecroft", "sg_awrc", "sg_westside", "sg_advanced", "sg_birdvet"],
    },
    "bangkok": {
        "city": {"en": "Bangkok", "ja": "バンコク", "zh-tw": "曼谷", "th": "กรุงเทพฯ"},
        "clinics": ["bkk_chula", "bkk_ivet", "bkk_uvet", "bkk_arak", "bkk_grand", "bkk_happy", "bkk_setthakit", "bkk_vetazoo"],
    },
    "sukhumvit-bangkok": {
        "city": {"en": "Sukhumvit and Thonglor, Bangkok", "ja": "バンコク・スクンビット/トンロー", "zh-tw": "曼谷素坤逸與通羅", "th": "สุขุมวิทและทองหล่อ กรุงเทพฯ"},
        "clinics": ["bkk_arak", "bkk_happy", "bkk_ivet", "bkk_uvet", "bkk_chula", "bkk_grand"],
    },
    "rama-9-bangkok": {
        "city": {"en": "Rama 9, Bangkok", "ja": "バンコク・ラマ9", "zh-tw": "曼谷拉瑪九世", "th": "พระราม 9 กรุงเทพฯ"},
        "clinics": ["bkk_ivet", "bkk_uvet", "bkk_chula", "bkk_arak", "bkk_grand", "bkk_happy"],
    },
    "pathum-wan-bangkok": {
        "city": {"en": "Pathum Wan, Bangkok", "ja": "バンコク・パトゥムワン", "zh-tw": "曼谷巴吞旺", "th": "ปทุมวัน กรุงเทพฯ"},
        "clinics": ["bkk_chula", "bkk_arak", "bkk_ivet", "bkk_uvet", "bkk_happy", "bkk_grand"],
    },
    "west-bangkok": {
        "city": {"en": "West Bangkok", "ja": "バンコク西部", "zh-tw": "曼谷西部", "th": "กรุงเทพฯ ฝั่งตะวันตก"},
        "clinics": ["bkk_setthakit", "bkk_ivet", "bkk_chula", "bkk_uvet", "bkk_grand", "bkk_vetazoo"],
    },
    "pattaya-thailand": {
        "city": {"en": "Pattaya and East-coast Thailand", "ja": "パタヤ・タイ東部", "zh-tw": "芭達雅與泰國東部", "th": "พัทยาและภาคตะวันออกของไทย"},
        "clinics": ["bkk_vetazoo", "bkk_ivet", "bkk_uvet", "bkk_chula", "bkk_arak"],
    },
}


def cfg(locale):
    merged = dict(TEXT["en"])
    merged.update(TEXT[locale])
    return merged


def tags(items):
    return " ".join(f'<span class="city-tag">{escape(tag)}</span>' for tag in items)


def clinics_for(page_def):
    return [CLINICS[clinic_id] for clinic_id in page_def["clinics"]]


def clinic_cards(clinics):
    cards = []
    for clinic in clinics:
        phone = f' · <strong>☎ {escape(clinic["phone"])}</strong>' if clinic["phone"] else ""
        cards.append(
            f'<div class="card"><h3 style="margin-top:0">{escape(clinic["name"])}</h3>'
            f'<p style="margin-bottom:6px;color:var(--muted)">{escape(clinic["area"])}{phone}</p>'
            f'<p style="margin-bottom:8px">{tags(clinic["tags"])}</p>'
            f'<p>{escape(clinic["note"])}</p>'
            f'<p style="margin-bottom:0"><a class="source-link" href="{escape(clinic["url"])}" rel="noreferrer" target="_blank">Source: {escape(clinic["source"])}</a></p></div>'
        )
    return "".join(cards)


def schema(slug, city, clinics, locale):
    return json.dumps([
        {
            "@context": "https://schema.org",
            "@type": "WebPage",
            "name": cfg(locale)["title"].format(city=city),
            "description": cfg(locale)["meta"].format(city=city),
            "url": local_url(slug, locale),
            "inLanguage": LOCALES[locale]["lang"],
            "dateModified": LASTMOD,
            "publisher": {"@type": "Organization", "name": "RabbitEmergency.com", "url": BASE},
        },
        {
            "@context": "https://schema.org",
            "@type": "ItemList",
            "name": f"Real rabbit/exotic emergency clinics in {city}",
            "itemListElement": [
                {
                    "@type": "ListItem",
                    "position": idx + 1,
                    "item": {
                        "@type": "VeterinaryCare",
                        "name": clinic["name"],
                        "areaServed": city,
                        **({"telephone": clinic["phone"]} if clinic["phone"] else {}),
                        "url": clinic["url"],
                    },
                }
                for idx, clinic in enumerate(clinics)
            ],
        },
    ], ensure_ascii=False)


def related_links(active_slug, locale):
    items = []
    for page_key, page_def in PAGES.items():
        slug = f"rabbit-emergency-vet-{page_key}"
        if slug == active_slug:
            continue
        city = page_def["city"][locale]
        items.append(f'<a class="source-link" href="{escape(local_path(slug, locale))}">{escape(city)}</a>')
    return "".join(items)


def page(slug, page_key, locale):
    t = cfg(locale)
    page_def = PAGES[page_key]
    city = page_def["city"][locale]
    clinics = clinics_for(page_def)
    title = t["title"].format(city=city)
    meta = t["meta"].format(city=city)
    call_items = "".join(f"<li>{escape(item)}</li>" for item in t["call_items"])
    source_links = "".join(f'<a class="source-link" href="{escape(c["url"])}" rel="noreferrer" target="_blank">{escape(c["source"])}</a>' for c in clinics)
    body = f"""<div class="crumb"><a href="{escape(local_path('', locale))}">{escape(t['home'])}</a> &rsaquo; {escape(title)}</div>
<div class="eyebrow">{escape(t['eyebrow'])}</div>
<h1>{escape(t['h1'].format(city=city))}</h1>
<p class="lede">{escape(t['lede'])}</p>
<section class="card" id="clinic-verification"><h2 style="margin-top:0">{escape(t['verification'])}</h2><ul><li><strong>{escape(t['verified'])}:</strong> {LASTMOD}</li><li>{escape(t['method'])}</li><li>{escape(t['travel'])}</li><li>{escape(t['emergency'])}</li></ul></section>
<h2>{escape(t['clinics'])}</h2>
{clinic_cards(clinics)}
<h2>{escape(t['call'])}</h2><div class="card"><ul>{call_items}</ul></div>
<h2>{escape(t['sources'])}</h2><div class="source-links">{source_links}</div>
<h2>{escape(t['related'])}</h2><div class="source-links">{related_links(slug, locale)}</div>
<p class="reviewed">{escape(t['review'])}</p>"""
    return f"""<!DOCTYPE html>
<html lang="{escape(LOCALES[locale]['lang'])}">
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
<style>{STYLE}</style>
<script type="application/ld+json">{schema(slug, city, clinics, locale)}</script>
</head>
<body>
<div class="topbar"><nav class="nav"><a class="brand" href="{escape(local_path('', locale))}">RabbitEmergency<span>.com</span></a><div class="nav-links"><a href="{escape(local_path('rabbit-emergency-signs', locale))}">Signs</a><a href="{escape(local_path('rabbit-not-eating-or-pooping', locale))}">Not eating</a><a href="{escape(local_path('rabbit-emergency-vet-hong-kong', locale))}">Find a vet</a></div></nav></div>
<main class="wrap">{body}</main>
<footer class="footer"><div class="wrap" style="padding:0">{escape(t['footer'])}</div></footer>
</body>
</html>
"""


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(sanitize_html(text, path), encoding="utf-8")


def main():
    for page_key in PAGES:
        slug = f"rabbit-emergency-vet-{page_key}"
        for locale in LOCALES:
            out = ROOT / LOCALES[locale]["prefix"] / slug / "index.html" if locale != "en" else ROOT / slug / "index.html"
            write(out, page(slug, page_key, locale))
    scrub_unverified_review_claims()


if __name__ == "__main__":
    main()
