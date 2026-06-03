# RabbitEmergency.com Search + AI Monitoring

## Weekly checks

1. Google Search Console: submit `https://rabbitemergency.com/sitemap.xml`, inspect the top emergency hubs, and review indexing reasons for not-indexed pages.
2. Bing Webmaster Tools: import from Google Search Console, confirm sitemap success, and review Bing AI / Copilot citation visibility where available.
3. IndexNow: after each deploy, run `python3 tools/submit_indexnow.py` from the repo root. The key file is `https://rabbitemergency.com/dbc082bc9601440dac1a111ab4d647aa.txt`.
4. Clinic freshness: verify clinic source links monthly. Current verification date: 2026-06-03. Next scheduled date: 2026-07-03.
5. llms.txt: confirm it lists new hubs, printables, clinic pages, reviewer pages, and correction policy.

## Official references

- Google AI features and your website: https://developers.google.com/search/docs/appearance/ai-overviews
- Bing Webmaster Guidelines: https://www.bing.com/webmasters/help/bing-webmaster-guidelines-30fba23a
- IndexNow documentation: https://www.indexnow.org/documentation.html
