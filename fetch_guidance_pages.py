"""Re-capture web-only guidance pages as clean Markdown, without navigation junk."""
from datetime import date

import requests
import trafilatura

ACCESSED = date.today().isoformat()
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                         "(KHTML, like Gecko) Chrome/140.0 Safari/537.36"}  # some .gov.au sites block bots

PAGES = [
    {
        "file": "swa-working-in-heat-faq.md",
        "title": "Working in heat - frequently asked questions",
        "publisher": "Safe Work Australia",
        "authority": "National guidance, not law in Victoria",
        "url": "https://www.safeworkaustralia.gov.au/safety-topic/hazards/working-heat/frequently-asked-questions",
    },
    {
        "file": "swa-heat-checklist.md",
        "title": "Checklist for managing the risks of heat in the workplace",
        "publisher": "Safe Work Australia",
        "authority": "National guidance, not law in Victoria",
        "url": "https://www.safeworkaustralia.gov.au/safety-topic/hazards/working-heat/checklist-managing-risks-heat-workplace",
    },
    {
        "file": "worksafevic-prevention-heat-illness.md",
        "title": "Prevention and protection from heat illness",
        "publisher": "WorkSafe Victoria",
        "authority": "Victorian regulator",
        "url": "https://www.worksafe.vic.gov.au/prevention-and-protection-heat-illness",
    },
]


def get_text(html: str) -> tuple[str | None, str]:
    """Try strict extraction first, then looser settings, then a plain text dump."""
    attempts = [
        ("precise", dict(favor_precision=True, include_tables=True, include_links=False)),
        ("recall", dict(favor_recall=True, include_tables=True, include_links=False, no_fallback=False)),
        ("bare", dict(include_tables=True, include_comments=True, include_links=False)),
    ]
    for label, kwargs in attempts:
        text = trafilatura.extract(html, output_format="markdown", **kwargs)
        if text and len(text) > 500:
            return text, label
    dump = trafilatura.html2txt(html)  # last resort: everything, junk included
    return (dump, "html2txt") if dump and len(dump) > 500 else (None, "none")


for p in PAGES:
    r = requests.get(p["url"], headers=HEADERS, timeout=30)
    print(f"{p['file']}: HTTP {r.status_code}, {len(r.text):,} chars of HTML")
    if r.status_code != 200:
        print("  skipped - page did not load")
        continue

    text, how = get_text(r.text)
    if not text:
        print("  FAILED - extracted nothing, capture this one by hand")
        continue

    header = (f"# {p['title']}\n\n"
              f"Publisher: {p['publisher']}\n"
              f"Authority in Victoria: {p['authority']}\n"
              f"Source: {p['url']}\n"
              f"Accessed: {ACCESSED}\n\n---\n\n")

    with open(f"corpus/{p['file']}", "w", encoding="utf-8") as f:
        f.write(header + text + "\n")
    print(f"  saved via '{how}': {len(text):,} characters")