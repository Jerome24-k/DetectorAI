import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline
from datasets import load_dataset
import numpy as np

# Load dataset
dataset = load_dataset("sms_spam")
X = dataset['train']['sms']
y = dataset['train']['label']

# Build model pipeline
model = make_pipeline(TfidfVectorizer(), MultinomialNB())
model.fit(X, y)

# Suspicious keyword triggers
suspicious_keywords = [
    "account", "bank", "verify", "payment", "transaction", "wallet",
    "login", "credentials", "password", "electricity", "bill", 
    "customs", "link", "refund", "kyc", "failed", "urgent"
]

# Streamlit UI
st.set_page_config(page_title="ScamSniperAI", page_icon="📱")
st.title("📱 ScamSniperAI")
st.caption("Your local AI-powered scam message detector.")
st.markdown("---")

msg = st.text_area("📩 Paste the SMS or WhatsApp message below")

if st.button("🔍 Analyze"):
    if not msg.strip():
        st.warning("Please enter a message.")
    else:
        prediction = model.predict([msg])[0]
        confidence = model.predict_proba([msg])[0][prediction]

        msg_lower = msg.lower()
        is_suspicious = any(word in msg_lower for word in suspicious_keywords)

        if prediction == 1:
            st.error(f"⚠️ This message looks like a SCAM! ({confidence*100:.1f}% confidence)")
        else:
            st.success(f"✅ This message looks SAFE. ({confidence*100:.1f}% confidence)")
            if is_suspicious:
                st.warning("⚠️ BUT this message mentions sensitive words like accounts, payments, or verification. Please double-check directly with your bank or service provider before responding.")
        st.markdown("---")
        st.markdown("⚠️ ALWAYS VERIFY SUSPICIOUS MESSAGES DIRECTLY WITH YOUR SERVICE PROVIDER.")
        st.markdown("🔍 ScamSniperAI IS NOT PROFESSIONAL ADVICE AND ALWAYS SEEK SECOND OPINIONS PREFERABLY FROM YOUR SERVICE PROVIDER")
        st.markdown("⚠️ ScamSniperAI is not responsible for any losses or issues arising from following its advice.")
        st.markdown("🛡️ *ScamSniperAI uses AI + keyword suspicion logic to help detect risky messages.*")
