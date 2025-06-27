import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline
import pandas as pd
import numpy as np
import os
from datetime import datetime

# --- UI Customization ---
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #0f2027, #2c5364, #00c9a7);
        background-attachment: fixed;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins&display=swap');
    html, body, [class*="css"]  {
        font-family: 'Poppins', sans-serif;
    }
    </style>
""", unsafe_allow_html=True)

# --- Load Dataset & Train Model ---
df = pd.read_csv("scam_superdataset_10k.csv")
X = df['message']
y = df['label']

model = make_pipeline(TfidfVectorizer(), MultinomialNB())
model.fit(X, y)

# --- Keyword Logic ---
suspicious_keywords = [
    "account", "bank", "verify", "payment", "transaction", "wallet",
    "login", "credentials", "password", "electricity", "bill", 
    "customs", "link", "refund", "kyc", "failed", "urgent"
]

known_safe_phrases = [
    "how to protect", "guide to avoid", "scam awareness",
    "educate about scams", "help elderly", "protect seniors from scams",
    "tips to stay safe", "avoid getting scammed", "protecting elderly people from scams"
]

def is_known_safe(msg):
    msg_lower = msg.lower()
    return any(phrase in msg_lower for phrase in known_safe_phrases)

# --- Smarter Bait Detection ---
def is_bait_scam(message):
    message_lower = message.lower()
    safe_free_phrases = [
        "free education", "free books", "free seminar", "free event", 
        "free vaccine", "free course", "free guide", "free workshop"
    ]
    if any(phrase in message_lower for phrase in safe_free_phrases):
        return False

    custom_words = ["send", "receive", "$", "win", "money", "prize", "reward", "rich", "free"]
    word_spam = sum(word in message_lower for word in custom_words) >= 3
    dollar_count = message_lower.count("$") >= 2
    big_number = any(char.isdigit() and len(token) > 6 for token in message_lower.split() for char in token)

    return word_spam or dollar_count or big_number

def is_short_scam(msg):
    msg_lower = msg.lower().strip()
    short_red_flags = [
        "scam", "money now", "prize", "send money", "rich", "$$$", "lottery",
        "click", "verify", "account", "win", "otp", "bank", "reward"
    ]
    return len(msg_lower) <= 5 or any(flag in msg_lower for flag in short_red_flags)

# --- Feedback Logging ---
def log_feedback(message, prediction, confidence, correct_label):
    log_file = "feedback_log.csv"
    new_entry = {
        "timestamp": datetime.now().isoformat(),
        "message": message,
        "prediction": prediction,
        "confidence": round(confidence, 4),
        "correct_label": correct_label
    }
    if os.path.exists(log_file):
        pd.DataFrame([new_entry]).to_csv(log_file, mode='a', header=False, index=False)
    else:
        pd.DataFrame([new_entry]).to_csv(log_file, index=False)

# --- Streamlit UI ---
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
        if is_known_safe(msg):
            prediction = 0
            confidence = 0.99
        else:
            prediction = model.predict([msg])[0]
            confidence = model.predict_proba([msg])[0][prediction]

            msg_lower = msg.lower()
            is_suspicious = any(word in msg_lower for word in suspicious_keywords)
            forced_scam = is_bait_scam(msg) or is_short_scam(msg)

            if forced_scam:
                prediction = 1
                confidence = max(confidence, 0.97)

        # --- Scam Risk Meter ---
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

        # --- Result Output + Reasoning ---
        st.markdown("---")
        if prediction == 1:
            st.error(f"⚠️ This message looks like a SCAM! ({confidence*100:.1f}% confidence)")
            st.markdown("This message shows multiple red flags that are commonly seen in scam messages, like the use of financial words, vague language, or promises of rewards. Our model and logic-based checks identified patterns linked to phishing, fraud, or bait attempts. Please be extremely careful before responding to such messages.")
        else:
            st.success(f"✅ This message looks SAFE. ({confidence*100:.1f}% confidence)")
            st.markdown("This message does not contain strong indicators of scam activity based on our machine learning model. It doesn't include suspicious keywords or bait-style patterns. Still, it's always smart to stay alert and verify unknown sources.")
            if 'msg_lower' in locals() and is_suspicious:
                st.warning("⚠️ However, this message mentions sensitive terms like account, payment, or login. Even if it seems safe, contact your bank or service provider directly to confirm.")

        # --- Feedback System ---
        st.markdown("#### 🤖 Was this prediction correct?")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("👍 Yes"):
                st.success("Thanks for confirming!")
        with col2:
            if st.button("👎 No"):
                st.warning("Logged! We'll learn from this.")
                correct_label = 0 if prediction == 1 else 1
                log_feedback(msg, prediction, confidence, correct_label)

        # --- Footer ---
        st.markdown("---")
        st.markdown("⚠️ ALWAYS VERIFY SUSPICIOUS MESSAGES DIRECTLY WITH YOUR SERVICE PROVIDER.")
        st.markdown("🔍 ScamSniperAI IS NOT PROFESSIONAL ADVICE. ALWAYS SEEK SECOND OPINIONS.")
        st.markdown("⚠️ ScamSniperAI is not responsible for any losses or issues arising from following its advice.")
        st.markdown("🛡️ *ScamSniperAI uses AI + keyword suspicion logic to help detect risky messages.*")
