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

# Extra logic-based scam traps (bait detection)
def is_bait_scam(message):
    message_lower = message.lower()
    custom_words = ["send", "receive", "$", "win", "money", "prize", "reward", "rich"]
    word_spam = sum(word in message_lower for word in custom_words) >= 3
    dollar_count = message.count("$") >= 2
    big_number = any(char.isdigit() and len(token) > 6 for token in message.split() for char in token)
    return word_spam or dollar_count or big_number

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
        # Initial AI prediction
        prediction = model.predict([msg])[0]
        confidence = model.predict_proba([msg])[0][prediction]

        # Logic flags
        msg_lower = msg.lower()
        is_suspicious = any(word in msg_lower for word in suspicious_keywords)
        forced_scam = is_bait_scam(msg)

        # Override model prediction if scammy pattern found
        if forced_scam:
            prediction = 1
            confidence = max(confidence, 0.97)

        # Display result
        if prediction == 1:
            st.error(f"⚠️ This message looks like a SCAM! ({confidence*100:.1f}% confidence)")
        else:
            st.success(f"✅ This message looks SAFE. ({confidence*100:.1f}% confidence)")
            if is_suspicious:
                st.warning("⚠️ BUT this message mentions sensitive words like accounts, payments, or verification. Please double-check directly with your bank or service provider before responding.")

        # Footer disclaimers
        st.markdown("---")
        st.markdown("⚠️ ALWAYS VERIFY SUSPICIOUS MESSAGES DIRECTLY WITH YOUR SERVICE PROVIDER.")
        st.markdown("🔍 ScamSniperAI IS NOT PROFESSIONAL ADVICE. ALWAYS SEEK SECOND OPINIONS.")
        st.markdown("⚠️ ScamSniperAI is not responsible for any losses or issues arising from following its advice.")
        st.markdown("🛡️ *ScamSniperAI uses AI + keyword suspicion logic to help detect risky messages.*")
