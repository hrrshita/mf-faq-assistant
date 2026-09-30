"""Fetch sources.csv -> data/chunks.json. Prints status per URL so dead links are visible."""
import csv, io, json, re, datetime, requests
from bs4 import BeautifulSoup
from pypdf import PdfReader

UA = {"User-Agent": "Mozilla/5.0 (facts-only-mf-assistant; educational)"}
CHUNK, OVERLAP = 120, 20  # words

def text_from(resp, url):
    if url.lower().endswith(".pdf") or "pdf" in resp.headers.get("content-type", ""):
        r = PdfReader(io.BytesIO(resp.content))
        return "\n".join((p.extract_text() or "") for p in r.pages)
    soup = BeautifulSoup(resp.text, "html.parser")
    for t in soup(["script", "style", "nav", "footer", "header", "noscript"]):
        t.decompose()
    return soup.get_text("\n")

def chunk(text):
    words = re.sub(r"[ \t]+", " ", text).split()
    i = 0
    while i < len(words):
        yield " ".join(words[i:i + CHUNK])
        i += CHUNK - OVERLAP

def main():
    today = datetime.date.today().isoformat()
    out, ok, bad = [], 0, []
    for row in csv.DictReader(open("sources.csv")):
        try:
            r = requests.get(row["url"], headers=UA, timeout=30)
            r.raise_for_status()
            txt = text_from(r, row["url"])
            n = 0
            for c in chunk(txt):
                out.append({**row, "text": c, "fetched": today}); n += 1
            print(f"OK   {n:3d} chunks  {row['url']}"); ok += 1
        except Exception as e:
            print(f"FAIL {row['url']}  ({e})"); bad.append(row["url"])
    json.dump(out, open("data/chunks.json", "w"))
    print(f"\n{ok} ok, {len(bad)} failed. Fix or delete failed rows in sources.csv, then re-run.")

if __name__ == "__main__":
    main()
