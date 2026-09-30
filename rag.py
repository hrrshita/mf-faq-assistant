"""Small-corpus retrieval (TF-IDF) + extractive, cited answers. No LLM required."""
import json, re, os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from guardrails import route

SCHEMES = {"flexi": "HDFC Flexi Cap Fund", "large cap": "HDFC Large Cap Fund",
           "elss": "HDFC ELSS Tax Saver", "tax saver": "HDFC ELSS Tax Saver",
           "taxsaver": "HDFC ELSS Tax Saver", "mid cap": "HDFC Mid Cap Fund", "midcap": "HDFC Mid Cap Fund"}
TOPICS = [  # (question regex, preferred source types, sentence regex)
    (r"capital.?gain|tax (doc|statement)", ["capital_gains"], r"capital gain"),
    (r"statement|download|cas\b", ["statements"], r"statement"),
    (r"risk|benchmark", ["scheme_page", "riskometer"], r"risk|benchmark|nifty"),
    (r"expense", ["scheme_page", "factsheet"], r"expense"),
    (r"exit load", ["scheme_page"], r"exit load"),
    (r"sip|minimum|min\.? (invest|amount)", ["scheme_page"], r"sip|minimum|min\."),
    (r"lock.?in|80c", ["scheme_page", "factsheet"], r"lock.?in|80c"),
]
MIN_SCORE = 0.08
FALLBACK = "https://www.hdfcfund.com/"

class Assistant:
    def __init__(self, path="data/chunks.json"):
        self.chunks = json.load(open(path))
        self.vec = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), sublinear_tf=True)
        self.mat = self.vec.fit_transform([c["text"] for c in self.chunks])

    def _filter(self, q):
        ql = q.lower()
        scheme = next((v for k, v in SCHEMES.items() if k in ql), None)
        types, sent_re = None, None
        for pat, t, s in TOPICS:
            if re.search(pat, ql):
                types, sent_re = t, s; break
        idx = [i for i, c in enumerate(self.chunks)
               if (not scheme or c["scheme"] in (scheme, "All")) and (not types or c["type"] in types)]
        return idx or list(range(len(self.chunks))), sent_re

    def answer(self, q):
        kind, msg = route(q)
        if kind != "facts":
            return {"kind": kind, "text": msg}
        idx, sent_re = self._filter(q)
        sims = cosine_similarity(self.vec.transform([q]), self.mat[idx]).ravel()
        order = sims.argsort()[::-1][:3]
        if sims[order[0]] < MIN_SCORE:
            return {"kind": "low", "text": f"I couldn't find that in my official sources. Please check {FALLBACK}"}
        best = self.chunks[idx[order[0]]]
        qwords = set(re.findall(r"\w+", q.lower())) - {"the", "of", "is", "what", "for", "a", "in", "how", "do", "i"}
        cands = []
        for j in order:
            c = self.chunks[idx[j]]
            if c["url"] != best["url"]:
                continue
            for s in re.split(r"(?<=[.!?])\s+|\n+", c["text"]):
                s = s.strip()
                if 25 < len(s) < 300:
                    sc = len(qwords & set(re.findall(r"\w+", s.lower()))) + (2 if sent_re and re.search(sent_re, s, re.I) else 0)
                    cands.append((sc, s))
        cands.sort(key=lambda x: -x[0])
        sents, seen = [], set()
        for _, s in cands:
            if s not in seen and len(sents) < 3:
                sents.append(s); seen.add(s)
        body = " ".join(sents) or best["text"][:300]
        return {"kind": "fact", "text": body, "source": best["url"], "updated": best["fetched"]}

def format_answer(r):
    if r["kind"] == "fact":
        return f"{r['text']}\n\nSource: {r['source']}\nLast updated from sources: {r['updated']}"
    return r["text"]
