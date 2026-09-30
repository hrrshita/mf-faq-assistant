# Facts-Only MF Assistant (Groww context · HDFC Mutual Fund)

A small RAG chatbot that answers factual mutual-fund questions from official public pages, with exactly one source link per answer. No advice, no returns, no PII.

**Product chosen:** Groww (the user persona is a Groww investor asking a factual question).
**AMC:** HDFC Mutual Fund. **Schemes:** HDFC Flexi Cap, HDFC Large Cap, HDFC Mid Cap, HDFC ELSS Tax Saver.

## Setup
```bash
pip install -r requirements.txt
python ingest.py          # fetches sources.csv -> data/chunks.json, prints OK/FAIL per URL
streamlit run app.py
```
Deploy: push to GitHub, then Streamlit Community Cloud (run `ingest.py` locally and commit `data/chunks.json`).

## How it works
1. **Ingest** – fetch each URL/PDF, strip boilerplate, split into ~120-word chunks with URL + fetch date.
2. **Guardrail** (`guardrails.py`) – regex routes each question: PII → blocked (never stored); "should I / best / which is better" → advice refusal + SEBI investor-education link; returns/performance → refusal + official scheme page; otherwise → facts.
3. **Retrieve** – TF-IDF over chunks, filtered by detected scheme and topic (exit load, ELSS, statements…); top match must pass a confidence threshold.
4. **Answer** – up to 3 extracted sentences from the best source, one link, and "Last updated from sources: <fetch date>". Low confidence → "not found" + AMC link.
5. **UI** – welcome line, 3 example questions, "Facts-only. No investment advice." note.

## Source list
See `sources.csv` (20 URLs). `status=verified` means the page was seen in search results while building this; `pattern-derived` URLs follow the AMC's URL pattern and must pass `ingest.py` (fix or delete any FAIL rows).

## Known limits
- Scheme pages are JavaScript-heavy; if `ingest.py` returns thin text for a page, switch that row to the scheme's SID/KIM/Fund Facts PDF from its "Downloads" section.
- Factsheet PDF file names change monthly; update the URL in `sources.csv` each month.
- Extractive answers can include neighbouring sentences; keep the corpus small and clean.
- Regex guardrails can miss unusual phrasing. Riskometer and benchmark for a specific scheme need the scheme page or factsheet ingested successfully.
- Data is a snapshot from the fetch date shown in each answer.

## Files
`app.py` UI · `rag.py` retrieval/answers · `guardrails.py` routing · `ingest.py` crawler · `sources.csv` · `sample_qa.md` · `DISCLAIMER.md`
