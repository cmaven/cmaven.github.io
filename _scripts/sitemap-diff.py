#!/usr/bin/env python3
# ============================================================
# sitemap-diff.py: sitemap.xml vs 사용자 텍스트 비교 도구
# 상세: 시스템 클립보드 또는 stdin에서 사용자 텍스트(GSC URL 목록 등)를 읽고,
#       https://cmaven.github.io/sitemap.xml 과 비교하여
#       sitemap에는 있지만 사용자 텍스트에는 없는 URL 목록을 출력·저장.
# 사용법:
#   1) 대화형 (기본):
#        python3 _scripts/sitemap-diff.py
#      → GSC URL 텍스트 붙여넣고 → 빈 줄에 "EOF" 입력 후 Enter
#   2) 파일 리다이렉트:
#        python3 _scripts/sitemap-diff.py < paste.txt
# 출력: sitemap-missing.txt (스크립트 실행 디렉토리)
# 생성일: 2026-05-26 | 수정일: 2026-05-26
# ============================================================

import re
import sys
import urllib.request
from pathlib import Path
from xml.etree import ElementTree as ET

SITEMAP_URL = "https://cmaven.github.io/sitemap.xml"
OUT_FILE = "sitemap-missing.txt"
URL_RE = re.compile(r"https?://[^\s<>\"'\)]+")
EOF_SENTINEL = "EOF"


def fetch_sitemap(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "sitemap-diff/1.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8")


def parse_sitemap_locs(xml_text: str) -> set[str]:
    cleaned = re.sub(r'\sxmlns="[^"]+"', "", xml_text, count=1)
    root = ET.fromstring(cleaned)

    locs = {loc.text.strip() for loc in root.findall(".//loc") if loc.text}

    if root.tag.lower().endswith("sitemapindex"):
        child_urls: set[str] = set()
        for sitemap_loc in list(locs):
            try:
                child_urls |= parse_sitemap_locs(fetch_sitemap(sitemap_loc))
            except Exception as e:
                print(f"[warn] failed to fetch child sitemap {sitemap_loc}: {e}", file=sys.stderr)
        return child_urls
    return locs


def normalize(url: str) -> str:
    return url.split("#", 1)[0].rstrip("/")


def get_input_text() -> str | None:
    # If stdin is piped (not a TTY), read full stdin
    if not sys.stdin.isatty():
        return sys.stdin.read()

    # Interactive mode: read lines until user types EOF on its own line
    print(f"[1/3] Paste GSC URL list. When done, type {EOF_SENTINEL} on a new line and press ENTER:",
          file=sys.stderr)
    lines: list[str] = []
    try:
        while True:
            line = input()
            if line.strip().upper() == EOF_SENTINEL:
                break
            lines.append(line)
    except (EOFError, KeyboardInterrupt):
        # Allow Ctrl+D as a fallback for power users whose terminal supports it
        pass
    if not lines:
        print("[abort] no input.", file=sys.stderr)
        return None
    return "\n".join(lines)


def main() -> int:
    pasted = get_input_text()
    if pasted is None:
        return 1

    user_urls_raw = URL_RE.findall(pasted)
    user_urls = {normalize(u) for u in user_urls_raw}

    if not user_urls:
        print("[warn] no URLs found in input.", file=sys.stderr)

    print(f"[2/3] Fetching {SITEMAP_URL} ...", file=sys.stderr)
    try:
        xml_text = fetch_sitemap(SITEMAP_URL)
    except Exception as e:
        print(f"[error] failed to fetch sitemap: {e}", file=sys.stderr)
        return 1
    sitemap_urls = {normalize(u) for u in parse_sitemap_locs(xml_text)}

    missing = sorted(sitemap_urls - user_urls)
    extras = sorted(user_urls - sitemap_urls)

    print("[3/3] Writing output file ...", file=sys.stderr)
    Path(OUT_FILE).write_text(
        "\n".join(missing) + ("\n" if missing else ""), encoding="utf-8"
    )

    print("", file=sys.stderr)
    print("=== Summary ===", file=sys.stderr)
    print(f"  sitemap.xml URLs        : {len(sitemap_urls)}", file=sys.stderr)
    print(f"  pasted URLs             : {len(user_urls)} (raw matches: {len(user_urls_raw)})", file=sys.stderr)
    print(f"  in sitemap, NOT pasted  : {len(missing)}  <- saved to {OUT_FILE}", file=sys.stderr)
    print(f"  in pasted, NOT sitemap  : {len(extras)}", file=sys.stderr)

    print("", file=sys.stderr)
    print("=== Missing URLs (in sitemap, not in pasted text) ===")
    for u in missing:
        print(u)

    if extras:
        print("", file=sys.stderr)
        print("=== Extras (pasted but not in sitemap — possibly stale or filtered) ===", file=sys.stderr)
        for u in extras:
            print(u, file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
