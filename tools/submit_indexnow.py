#!/usr/bin/env python3
"""Submit RabbitEmergency.com URLs to IndexNow after deploy.
Uses the official IndexNow format: host a key file, then POST urlList to the global endpoint.
Docs: https://www.indexnow.org/documentation.html
"""
import json, re, sys, urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
KEY='dbc082bc9601440dac1a111ab4d647aa'
ENDPOINT='https://api.indexnow.org/indexnow'
urls=re.findall(r'<loc>(.*?)</loc>', (ROOT/'sitemap.xml').read_text(encoding='utf-8'))
payload=json.dumps({"host":"rabbitemergency.com","key":KEY,"keyLocation":f"https://rabbitemergency.com/{KEY}.txt","urlList":urls}).encode('utf-8')
req=urllib.request.Request(ENDPOINT, data=payload, headers={'Content-Type':'application/json; charset=utf-8'}, method='POST')
with urllib.request.urlopen(req, timeout=30) as resp:
    print(resp.status, resp.read().decode('utf-8','replace'))
