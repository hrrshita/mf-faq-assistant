"""Routing: PII -> block, advice/performance -> refuse, else -> facts (RAG)."""
import re

PII = [
    (r"\b[A-Z]{5}[0-9]{4}[A-Z]\b", "PAN"),
    (r"\b\d{4}\s?\d{4}\s?\d{4}\b", "Aadhaar-like number"),
    (r"[\w.+-]+@[\w-]+\.[\w.-]+", "email"),
    (r"(?<!\d)(?:\+?91[\s-]?)?[6-9]\d{9}(?!\d)", "phone number"),
    (r"(?i)\botp\b.{0,15}\d{4,8}|\b\d{4,8}\b.{0,15}\botp\b", "OTP"),
    (r"(?i)\b(?:a/?c|account)\s*(?:no\.?|number)?\s*[:#-]?\s*\d{9,18}\b", "account number"),
    (r"\b\d{9,18}\b", "long numeric ID"),
]
ADVICE = re.compile(r"(?i)\b(should i|shall i|is it (good|safe|wise)|worth (it|investing)|"
    r"buy or sell|which (one )?is (better|best)|best (fund|scheme)|recommend|"
    r"good (fund|investment)|invest in|switch (to|from)|redeem now|portfolio|my holdings)\b")
PERF = re.compile(r"(?i)\b(returns?|cagr|xirr|performance|outperform|beat|profit|gain|"
    r"how much will|will .* grow|compare .* (vs|with|and))\b")

LINKS = {
    "advice": "https://investor.sebi.gov.in/",
    "perf": "https://www.hdfcfund.com/our-products/hdfc-flexi-cap-fund",
}

def route(q: str):
    for pat, name in PII:
        if re.search(pat, q):
            return "pii", (f"Please don't share personal information such as a {name}. "
                           "I can't accept or store it, and I only answer general facts about schemes.")
    if ADVICE.search(q):
        return "refuse", ("I can only share facts, not investment advice or recommendations. "
                          f"For neutral guidance on choosing funds, see SEBI's investor education: {LINKS['advice']}")
    if PERF.search(q):
        return "refuse", ("I don't compute or compare returns. Official performance is in the scheme's factsheet: "
                          f"{LINKS['perf']}")
    return "facts", None
