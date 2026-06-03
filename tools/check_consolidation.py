#!/usr/bin/env python3
"""Guard: retired -emergency-signs intents must stay redirect stubs.
Fails (exit 1) if any retired slug was regenerated as a full page or re-listed
in the sitemap, or if the shared stylesheets vanished. Fail-open on internal
errors (exit 0) so a script bug never locks out pushes."""
import json, os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://rabbitemergency.com"
try:
    man = json.load(open(os.path.join(ROOT, "tools", "redirect_manifest.json")))
    M, LANGS = man["redirects"], man["langs"]
    problems = []
    # a) every present retired page must be a stub
    for a, o in M.items():
        for l in LANGS:
            fp = os.path.join(ROOT, l, a, "index.html")
            if not os.path.isfile(fp):
                continue
            s = open(fp, encoding="utf-8").read()
            is_stub = ('http-equiv="refresh"' in s and "noindex" in s and len(s) < 2000)
            if not is_stub:
                problems.append(f"REGENERATED (not a stub): /{l}{a}/  -> must redirect to /{o}/")
    # b) sitemap must not list retired pages
    sm = os.path.join(ROOT, "sitemap.xml")
    if os.path.isfile(sm):
        smtxt = open(sm, encoding="utf-8").read()
        for a in M:
            for l in LANGS:
                if f"<loc>{SITE}/{l}{a}/</loc>" in smtxt:
                    problems.append(f"SITEMAP re-lists retired page: /{l}{a}/")
    # c) shared stylesheets must still exist
    for css in ("styles.css", "styles-b.css"):
        if not os.path.isfile(os.path.join(ROOT, css)):
            problems.append(f"MISSING shared stylesheet: /{css} (CSS extraction reverted)")
    if problems:
        print("\n*** CONSOLIDATION GUARD FAILED ***")
        for p in problems[:40]:
            print("  -", p)
        if len(problems) > 40:
            print(f"  ... +{len(problems)-40} more")
        print("\nFix: retired intents in tools/redirect_manifest.json must stay redirect")
        print("stubs (do NOT regenerate them). Re-run the consolidation or restore stubs.")
        sys.exit(1)
    print(f"consolidation guard OK: {len(M)} intents x {len(LANGS)} langs intact; stylesheets present.")
    sys.exit(0)
except SystemExit:
    raise
except Exception as e:
    print(f"[consolidation guard] internal error, allowing push: {e}")
    sys.exit(0)
