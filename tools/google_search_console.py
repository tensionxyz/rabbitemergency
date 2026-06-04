#!/usr/bin/env python3
"""Local Google Search Console helper.

Uses OAuth with the human Search Console owner account. This avoids the
Search Console UI issue where service-account emails can show "email not
found" when added as users.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


ROOT = Path(__file__).resolve().parents[1]
SECRETS = ROOT / ".secrets"
CLIENT_FILE = SECRETS / "google-oauth-client.json"
TOKEN_FILE = SECRETS / "google-search-console-token.json"
SCOPES = ["https://www.googleapis.com/auth/webmasters"]
DEFAULT_SITE = "sc-domain:rabbitemergency.com"
DEFAULT_SITEMAP = "https://rabbitemergency.com/sitemap.xml"


def load_credentials() -> Credentials:
    SECRETS.mkdir(exist_ok=True)
    creds = None
    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
    if creds and creds.valid:
        return creds
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        TOKEN_FILE.write_text(creds.to_json(), encoding="utf-8")
        return creds
    if not CLIENT_FILE.exists():
        raise SystemExit(
            "Missing OAuth client file:\n"
            f"  {CLIENT_FILE}\n\n"
            "Create Google Cloud credentials: OAuth client ID -> Desktop app, "
            "download the JSON, and save it at that path."
        )
    flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT_FILE), SCOPES)
    creds = flow.run_local_server(port=0, prompt="consent")
    TOKEN_FILE.write_text(creds.to_json(), encoding="utf-8")
    return creds


def service():
    return build("searchconsole", "v1", credentials=load_credentials(), cache_discovery=False)


def list_sites() -> None:
    svc = service()
    result = svc.sites().list().execute()
    sites = result.get("siteEntry", [])
    if not sites:
        print("No Search Console properties visible to this Google account.")
        return
    for item in sites:
        print(f"{item.get('siteUrl')}  permission={item.get('permissionLevel')}")


def submit_sitemap(site_url: str, sitemap_url: str) -> None:
    svc = service()
    svc.sitemaps().submit(siteUrl=site_url, feedpath=sitemap_url).execute()
    print(f"submitted sitemap: {sitemap_url} for {site_url}")


def inspect_url(site_url: str, url: str) -> None:
    svc = service()
    result = (
        svc.urlInspection()
        .index()
        .inspect(body={"siteUrl": site_url, "inspectionUrl": url})
        .execute()
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--site", default=DEFAULT_SITE)
    parser.add_argument("--sitemap", default=DEFAULT_SITEMAP)
    parser.add_argument("--list-sites", action="store_true")
    parser.add_argument("--submit-sitemap", action="store_true")
    parser.add_argument("--inspect-url")
    args = parser.parse_args()

    try:
        if args.list_sites:
            list_sites()
        if args.submit_sitemap:
            submit_sitemap(args.site, args.sitemap)
        if args.inspect_url:
            inspect_url(args.site, args.inspect_url)
        if not (args.list_sites or args.submit_sitemap or args.inspect_url):
            parser.print_help()
        return 0
    except HttpError as exc:
        print(f"Google API error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
