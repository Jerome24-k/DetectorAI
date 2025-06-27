import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline
import pandas as pd
import numpy as np

# Load custom dataset
df = pd.read_csv("scam_superdataset_10k.csv")
X = df['message']
y = df['label']

# Build model pipeline
model = make_pipeline(TfidfVectorizer(), MultinomialNB())
model.fit(X, y)

# Suspicious keyword triggers
suspicious_keywords = [
    "account", "bank", "verify", "payment", "transaction", "wallet",
    "login", "credentials", "password", "electricity", "bill", 
    "customs", "link", "refund", "kyc", "failed", "urgent"
]

# Known-safe phrases to avoid false flags
known_safe_phrases = [
    "how to protect", "guide to avoid", "scam awareness",
    "educate about scams", "help elderly", "protect seniors from scams",
    "tips to stay safe", "avoid getting scammed", "protecting elderly people from scams"
]

def is_known_safe(msg):
    msg_lower = msg.lower()
    return any(phrase in msg_lower for phrase in known_safe_phrases)

# Logic: bait-style scam detector
def is_bait_scam(message):
    message_lower = message.lower()
    custom_words = ["send", "receive", "$", "win", "money", "prize", "reward", "rich"]
    word_spam = sum(word in message_lower for word in custom_words) >= 3
    dollar_count = message.count("$") >= 2
    big_number = any(char.isdigit() and len(token) > 6 for token in message.split() for char in token)
    return word_spam or dollar_count or big_number

# Short suspicious message detector
def is_short_scam(msg):
    msg_lower = msg.lower().strip()
    short_red_flags = [
        "scam", "money now", "prize", "send money", "rich", "$$$", "lottery",
        "click", "verify", "account", "win", "otp", "bank", "reward"
    ]
    return len(msg_lower) <= 5 or any(flag in msg_lower for flag in short_red_flags)

# Streamlit UI
st.set_page_config(page_title="ScamSniperAI", page_icon="📱")
st.title("📱 ScamSniperAI")
st.caption("Your local AI-powered scam message detector.")
st.caption("Made for the elderly by the youth")
st.markdown("---")

msg = st.text_area("📩 Paste the SMS or WhatsApp message below")

if st.button("🔍 Analyze"):
    if not msg.strip():
        st.warning("Please enter a message.")
    else:
        # First, skip AI if message is known safe
        if is_known_safe(msg):
            prediction = 0
            confidence = 0.99
        else:
            # AI prediction
            prediction = model.predict([msg])[0]
            confidence = model.predict_proba([msg])[0][prediction]

            # Logic flags
            msg_lower = msg.lower()
            is_suspicious = any(word in msg_lower for word in suspicious_keywords)
            forced_scam = is_bait_scam(msg) or is_short_scam(msg)

            if forced_scam:
                prediction = 1
                confidence = max(confidence, 0.97)

        # 📊 RISK METER
        st.subheader("📊 Scam Risk Meter")
        risk_percent = (1 - confidence) * 100 if prediction == 1 else (100 - confidence * 100)

        if prediction == 1:
            if confidence >= 0.9:
                st.markdown("### 🔴 HIGH RISK: Definitely a SCAM!")
            elif confidence >= 0.7:
                st.markdown("### 🟠 Likely a scam. Be cautious.")
            else:
                st.markdown("### ⚠️ Suspicious. Double-check manually.")
        else:
            if confidence >= 0.9:
                st.markdown("### 🟢 Safe Message")
            elif confidence >= 0.7:
                st.markdown("### 🟡 Likely safe. Still verify.")
            else:
                st.markdown("### ⚠️ Unclear. Use caution.")

        st.progress(int(risk_percent))

        # 🧠 Final result block
        st.markdown("---")
        if prediction == 1:
            st.error(f"⚠️ This message looks like a SCAM! ({confidence*100:.1f}% confidence)")
        else:
            st.success(f"✅ This message looks SAFE. ({confidence*100:.1f}% confidence)")
            if 'msg_lower' in locals() and is_suspicious:
                st.warning("⚠️ BUT this message mentions sensitive words like accounts, payments, or verification. Please double-check directly with your bank or service provider before responding.")

        # Footer disclaimers
        st.markdown("---")
        st.markdown("⚠️ ALWAYS VERIFY SUSPICIOUS MESSAGES DIRECTLY WITH YOUR SERVICE PROVIDER.")
        st.markdown("🔍 ScamSniperAI IS NOT PROFESSIONAL ADVICE. ALWAYS SEEK SECOND OPINIONS.")
        st.markdown("⚠️ ScamSniperAI is not responsible for any losses or issues arising from following its advice.")
        st.markdown("🛡️ *ScamSniperAI uses AI + keyword suspicion logic to help detect risky messages.*")
