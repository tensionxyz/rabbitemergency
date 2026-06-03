#!/usr/bin/env python3
"""Submit RabbitEmergency.com URLs to IndexNow after deploy.
Uses the official IndexNow format: host a key file, then POST urlList to the global endpoint.
Docs: https://www.indexnow.org/documentation.html
"""
import json, re, time, urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
KEY='dbc082bc9601440dac1a111ab4d647aa'
ENDPOINT='https://api.indexnow.org/indexnow'
BATCH_SIZE=100
urls=re.findall(r'<loc>(.*?)</loc>', (ROOT/'sitemap.xml').read_text(encoding='utf-8'))
for start in range(0, len(urls), BATCH_SIZE):
    batch=urls[start:start+BATCH_SIZE]
    payload=json.dumps({"host":"rabbitemergency.com","key":KEY,"keyLocation":f"https://rabbitemergency.com/{KEY}.txt","urlList":batch}).encode('utf-8')
    req=urllib.request.Request(ENDPOINT, data=payload, headers={'Content-Type':'application/json; charset=utf-8'}, method='POST')
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            print(f"batch {start//BATCH_SIZE+1}: {resp.status} {len(batch)} urls")
    except Exception as exc:
        print(f"batch {start//BATCH_SIZE+1}: failed for {len(batch)} urls: {exc}")
        raise
    time.sleep(1)
