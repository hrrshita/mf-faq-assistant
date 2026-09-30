import streamlit as st
from rag import Assistant, format_answer

st.set_page_config(page_title="Facts-Only MF Assistant", page_icon="📄")
st.title("Facts-Only MF Assistant")
st.caption("Groww-style FAQ helper · HDFC Mutual Fund · Facts-only. No investment advice.")
st.write("Hi! Ask me factual questions about selected HDFC Mutual Fund schemes. I answer from official AMC, SEBI and AMFI pages and always show one source.")

@st.cache_resource
def load():
    return Assistant()
bot = load()

examples = ["What is the exit load of HDFC Flexi Cap Fund?",
            "What is the lock-in period of HDFC ELSS Tax Saver?",
            "How do I download my capital gains statement?"]
cols = st.columns(3)
for i, ex in enumerate(examples):
    if cols[i].button(ex, use_container_width=True):
        st.session_state["q"] = ex

q = st.text_input("Your question", key="q", placeholder="e.g. What is the riskometer of HDFC Mid Cap Fund?")
if q:
    r = bot.answer(q)   # question is never stored or logged
    (st.info if r["kind"] in ("refuse", "pii") else st.success)(format_answer(r))

st.divider()
st.caption("Facts-only. No investment advice. Do not enter PAN, Aadhaar, account numbers, OTPs, emails or phone numbers.")
