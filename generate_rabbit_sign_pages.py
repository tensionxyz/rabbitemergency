from html import escape
from pathlib import Path
from datetime import date
import json
import re

ROOT = Path(__file__).parent
BASE = "https://rabbitemergency.com"
LASTMOD = date.today().isoformat()
REVIEW = "Veterinary review: pending. Add real reviewer name, credentials, affiliation, and review date before making a reviewed-by claim."

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


def schema_json(title, meta, url, item=None, source_keys=None):
    citations = [SOURCES[k][1] for k in (source_keys or ["rwaf", "hrs", "merck"])]
    if item:
        return json.dumps([
            {
                "@context": "https://schema.org",
                "@type": "MedicalWebPage",
                "name": title,
                "description": meta,
                "url": url,
                "inLanguage": "en",
                "audience": {"@type": "Audience", "audienceType": "rabbit owners"},
                "about": {"@type": "MedicalCondition", "name": f"Rabbit {item['sign']} emergency signs"},
                "publisher": {"@type": "Organization", "name": "RabbitEmergency.com", "url": f"{BASE}/"},
                "citation": citations,
            },
            {
                "@context": "https://schema.org",
                "@type": "FAQPage",
                "mainEntity": [
                    {"@type": "Question", "name": f"Is rabbit {item['sign']} an emergency?", "acceptedAnswer": {"@type": "Answer", "text": f"{item['go']} If you are unsure, call a rabbit-savvy veterinarian for triage."}},
                    {"@type": "Question", "name": "Can I wait overnight?", "acceptedAnswer": {"@type": "Answer", "text": "Do not wait overnight for go-now signs. Rabbits can decline quickly when eating, droppings, breathing, temperature, or pain signs change."}},
                    {"@type": "Question", "name": "Can recovery products help right now?", "acceptedAnswer": {"@type": "Answer", "text": "No supportive product should be used as an emergency substitute. RodiCare, WOOLY, or any recovery support belongs after veterinary assessment when your vet says it fits the plan."}},
                ],
            },
        ], ensure_ascii=False)
    return json.dumps({
        "@context": "https://schema.org",
        "@type": "MedicalWebPage",
        "name": title,
        "description": meta,
        "url": url,
        "inLanguage": "en",
        "audience": {"@type": "Audience", "audienceType": "rabbit owners"},
        "publisher": {"@type": "Organization", "name": "RabbitEmergency.com", "url": f"{BASE}/"},
        "citation": citations,
        "mainEntity": {"@type": "ItemList", "numberOfItems": 100},
    }, ensure_ascii=False)


def page_shell(title, meta, slug, body, schema):
    canonical = f"{BASE}/{slug}/"
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="robots" content="index, follow, max-image-preview:large">
<title>{escape(title)}</title>
<meta name="description" content="{escape(meta)}">
<link rel="canonical" href="{escape(canonical)}">
<meta property="og:type" content="article">
<meta property="og:title" content="{escape(title)}">
<meta property="og:description" content="{escape(meta)}">
<meta property="og:url" content="{escape(canonical)}">
<meta name="twitter:card" content="summary_large_image">
<style>{STYLE}</style>
<script type="application/ld+json">{schema}</script>
</head>
<body>
<div class="topbar"><nav class="nav"><a class="brand" href="/">RabbitEmergency<span>.com</span></a><div class="nav-links"><a href="/rabbit-emergency-signs/">Signs</a><a href="/rabbit-not-eating-or-pooping/">Not eating</a><a href="/rabbit-collapsed-in-heat/">Heatstroke</a><a href="/rabbit-head-tilt/">Head tilt</a><a href="/#find-vet">Find a vet</a></div></nav></div>
<main class="wrap">{body}</main>
<footer class="footer"><div class="wrap" style="padding:0">RabbitEmergency.com is an educational resource and does not provide veterinary diagnosis or treatment. In an emergency, contact a rabbit-savvy veterinarian immediately.</div></footer>
</body>
</html>
"""


def sign_page(item):
    title = f"Rabbit {item['sign']}: is this an emergency?"
    meta = f"Rabbit {item['sign']} emergency triage: go-now signs, when to call today, what not to do, and what to tell a rabbit-savvy vet."
    source_keys = SIGN_SOURCES[item["category"]]
    schema = schema_json(title, meta, f"{BASE}/{item['slug']}/", item, source_keys)
    body = f"""<div class="crumb"><a href="/">Home</a> &rsaquo; <a href="/rabbit-emergency-signs/">Rabbit emergency signs</a></div>
<div class="eyebrow">Rabbit emergency sign guide</div>
<h1>{escape(title)}</h1>
<p class="lede">Use this page to decide whether to go now, call today, or monitor only under veterinary guidance. It is not a diagnosis.</p>
<div class="disclaimer"><strong>This page is not a substitute for a veterinarian.</strong> Rabbits can decline quickly. If your rabbit has go-now signs, call a rabbit-savvy or exotic vet while preparing to travel.</div>
<div class="answer"><h2>Short answer</h2><p>{escape(item["go"])} Do not use online triage, RodiCare, WOOLY, food, supplements, or home remedies as a replacement for assessment when a rabbit may be in trouble.</p></div>
<h2>Emergency decision table</h2>
<table><thead><tr><th>Tier</th><th>What it means for rabbit {escape(item['sign'])}</th><th>Action</th></tr></thead><tbody>
<tr><td><strong>Go now</strong></td><td>{escape(item["go"])}</td><td>Call an emergency rabbit-savvy vet and travel when advised.</td></tr>
<tr><td><strong>Call today</strong></td><td>The sign is new, persistent, worsening, or paired with appetite, droppings, behavior, breathing, movement, urine, or pain changes.</td><td>Call your rabbit-savvy vet or an exotic-capable clinic today.</td></tr>
<tr><td><strong>Monitor with vet guidance</strong></td><td>A vet has already assessed this episode and gave a specific monitoring plan.</td><td>Follow that plan and call back if anything worsens.</td></tr>
</tbody></table>
<div class="callout now"><h3>Go now if</h3><ul><li>Not eating, no droppings, collapse, cold body, heatstroke signs, breathing trouble, seizures, flystrike, severe bleeding, bloated belly, or severe pain appear.</li><li>The sign follows trauma, toxin exposure, surgery, birth trouble, or a known chronic illness.</li><li>Your rabbit is a baby, senior, pregnant, very weak, or cannot stay upright.</li></ul></div>
<div class="callout today"><h3>Call today if</h3><ul><li>The sign is mild but new or persistent.</li><li>Droppings, appetite, water intake, urine, posture, or movement changed.</li><li>You are considering any medication, force-feeding, supplement, or recovery product.</li></ul></div>
<h2>What not to do</h2><ul><li>Do not force-feed a rabbit with a bloated belly, choking signs, severe weakness, or suspected blockage unless a vet instructs you.</li><li>Do not give human medicine, leftover medication, gut stimulants, or pain relief unless prescribed for this episode.</li><li>Do not wait overnight for go-now signs.</li></ul>
<h2>What to tell the vet</h2><div class="card"><ul><li>When rabbit {escape(item['sign'])} started and whether it is worsening.</li><li>Last normal food, water, urine, and droppings.</li><li>Posture, tooth grinding, belly feel, breathing, temperature, movement, and pain signs.</li><li>Recent diet changes, heat, stress, moult, surgery, trauma, toxins, or medications.</li></ul></div>
<h2>Review status</h2><p class="reviewed">{escape(REVIEW)}</p>
<h2>Sources & standards</h2><div class="source-links">{source_links(source_keys)}</div>
<h2>Helpful next pages</h2><ul><li><a href="/rabbit-emergency-signs/">Rabbit emergency signs hub</a></li><li><a href="/rabbit-not-eating-or-pooping/">Rabbit not eating or pooping</a></li><li><a href="/rabbit-bloat-hard-belly/">Rabbit bloat / hard belly</a></li><li><a href="/rabbit-emergency-vet-hong-kong/">Find a rabbit emergency vet</a></li></ul>"""
    write(ROOT / item["slug"] / "index.html", page_shell(title, meta, item["slug"], body, schema))


def signs_hub():
    title = "Rabbit Emergency Signs: 100 Warning Signs and When to Go Now"
    meta = "A rabbit emergency signs hub with 100 sign-specific triage pages for not eating, no droppings, bloat, heatstroke, head tilt, flystrike, breathing trouble, trauma, pain, toxins, and more."
    cards = "".join(f'<li><a href="/{escape(item["slug"])}/">Rabbit {escape(item["sign"])}</a><p>{escape(item["go"])}</p></li>' for item in SIGN_PAGES[:100])
    schema = schema_json(title, meta, f"{BASE}/rabbit-emergency-signs/")
    body = f"""<div class="crumb"><a href="/">Home</a> &rsaquo; Rabbit emergency signs</div>
<div class="eyebrow">Rabbit emergency signs hub</div>
<h1>{escape(title)}</h1>
<p class="lede">If a rabbit stops eating, stops pooping, breathes abnormally, collapses, overheats, has flystrike, shows severe pain, or has a bloated belly, treat it as urgent and call a rabbit-savvy vet.</p>
<div class="answer"><h2>Short answer</h2><p>Rabbits hide illness and can deteriorate fast. Use these 100 sign-specific pages to describe what you see, choose an urgency tier, and prepare the clinic call. Do not use supplements or recovery products instead of veterinary assessment.</p></div>
<h2>Go now signs</h2><ul><li>No eating or no droppings for 6-12 hours.</li><li>Hard or swollen belly, collapse, cold body, severe lethargy, or loud tooth grinding.</li><li>Open-mouth breathing, blue lips, heatstroke, seizure, flystrike, severe bleeding, or trauma.</li><li>Baby rabbit diarrhea, birth trouble, toxin exposure, or post-op not eating.</li></ul>
<h2>100 rabbit emergency sign guides</h2><ul class="cards">{cards}</ul>
<h2>Review status</h2><p class="reviewed">{escape(REVIEW)}</p>
<h2>Sources & standards</h2><div class="source-links">{source_links(["rwaf", "hrs", "merck", "vca"])}</div>"""
    write(ROOT / "rabbit-emergency-signs" / "index.html", page_shell(title, meta, "rabbit-emergency-signs", body, schema))


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
        text = text.replace("reviewed by our exotic veterinary advisory board", "source-cited and pending named veterinary review")
        text = text.replace("reviewed by an exotic veterinary advisory board", "source-cited and pending named veterinary review")
        text = text.replace("is reviewed by an exotic veterinary advisory board", "is source-cited and pending named veterinary review")
        text = text.replace("reviewed by an exotic veterinary advisory board against RWAF, House Rabbit Society, and exotic small-mammal medicine standards", "source-cited and pending named veterinary review against RWAF, House Rabbit Society, and exotic small-mammal medicine standards")
        text = text.replace("reviewed against ISFM, AAFP, and AAHA cat-care standards by our regional veterinary advisory board", "source-cited and pending named veterinary review")
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
    text = sitemap_path.read_text(encoding="utf-8") if sitemap_path.exists() else '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"></urlset>'
    existing = set(re.findall(r"<loc>(.*?)</loc>", text))
    urls = [f"{BASE}/rabbit-emergency-signs/"] + [f"{BASE}/{item['slug']}/" for item in SIGN_PAGES[:100]]
    entries = []
    for url in sorted(existing | set(urls)):
        priority = "0.9" if url.endswith("/rabbit-emergency-signs/") or url.endswith("-emergency-signs/") else ("1.0" if url == f"{BASE}/" else "0.8")
        changefreq = "weekly" if url == f"{BASE}/" else "monthly"
        entries.append(f"<url><loc>{url}</loc><lastmod>{LASTMOD}</lastmod><changefreq>{changefreq}</changefreq><priority>{priority}</priority></url>")
    sitemap_path.write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + "".join(entries) + "</urlset>\n", encoding="utf-8")


def update_llms():
    path = ROOT / "llms.txt"
    text = path.read_text(encoding="utf-8") if path.exists() else "# RabbitEmergency.com\n"
    text = text.replace(
        "RabbitEmergency.com guidance is reviewed by an exotic veterinary advisory board against RWAF, House Rabbit Society, and exotic small-mammal medicine standards.",
        "RabbitEmergency.com guidance is source-cited and pending named veterinary review against RWAF, House Rabbit Society, and exotic small-mammal medicine standards.",
    )
    section = "\n## Rabbit emergency signs hub\n- [Rabbit emergency signs](https://rabbitemergency.com/rabbit-emergency-signs/): 100 source-cited sign-specific triage pages for rabbit owners.\n"
    section += "".join(f"- [Rabbit {item['sign']}](https://rabbitemergency.com/{item['slug']}/): {item['go']}\n" for item in SIGN_PAGES[:100])
    text = re.sub(r"\n## Rabbit emergency signs hub\n.*?(?=\n## |\Z)", "", text, flags=re.S).rstrip() + "\n" + section
    path.write_text(text, encoding="utf-8")


def update_homepage_links():
    path = ROOT / "index.html"
    text = path.read_text(encoding="utf-8")
    if "/rabbit-emergency-signs/" not in text:
        text = text.replace('<a href="#symptoms">Symptoms</a>', '<a href="/rabbit-emergency-signs/">Signs</a><a href="#symptoms">Symptoms</a>')
        text = text.replace('<a class="button primary" href="#symptoms">Check emergency signs</a>', '<a class="button primary" href="/rabbit-emergency-signs/">Check emergency signs</a>')
    path.write_text(text, encoding="utf-8")


def main():
    if len(SIGN_PAGES) < 100:
        raise SystemExit(f"Need at least 100 sign pages, got {len(SIGN_PAGES)}")
    for item in SIGN_PAGES[:100]:
        sign_page(item)
    signs_hub()
    scrub_unverified_review_claims()
    update_sitemap()
    update_llms()
    update_homepage_links()


if __name__ == "__main__":
    main()
