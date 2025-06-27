import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline
import pandas as pd
import numpy as np
import os
from datetime import datetime

# 🌈 Sleek modern background + font
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #fdfbfb, #ebedee);
        font-family: 'Segoe UI', sans-serif;
    }
    .risk-bar {
        height: 25px;
        width: 100%;
        border-radius: 10px;
        background: #ddd;
        overflow: hidden;
    }
    .risk-fill {
        height: 100%;
        text-align: center;
        color: white;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# Load custom dataset
df = pd.read_csv("scam_superdataset_10k.csv")
X = df['message']
y = df['label']

# Build model pipeline
model = make_pipeline(TfidfVectorizer(), MultinomialNB())
model.fit(X, y)

# Keyword & logic systems
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

def is_bait_scam(message):
    message_lower = message.lower()
    custom_words = ["send", "receive", "$", "win", "money", "prize", "reward", "rich"]
    word_spam = sum(word in message_lower for word in custom_words) >= 3
    dollar_count = message.count("$") >= 2
    big_number = any(char.isdigit() and len(token) > 6 for token in message.split() for char in token)
    return word_spam or dollar_count or big_number

def is_short_scam(msg):
    msg_lower = msg.lower().strip()
    short_red_flags = [
        "scam", "money now", "prize", "send money", "rich", "$$$", "lottery",
        "click", "verify", "account", "win", "otp", "bank", "reward"
    ]
    return len(msg_lower) <= 5 or any(flag in msg_lower for flag in short_red_flags)

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

# UI
st.set_page_config(page_title="ScamSniperAI", page_icon="📱")
st.title("📱 ScamSniperAI")
st.caption("Made for the elderly by the youth")
st.markdown("---")

msg = st.text_area("📩 Paste the SMS or WhatsApp message below")

if st.button("🔍 Analyze"):
    if not msg.strip():
        st.warning("Please enter a message.")
    else:
        # Prediction
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

        # 🎯 Risk Meter
        st.subheader("📊 Scam Risk Meter")
        risk_level = (1 - confidence) * 100 if prediction == 1 else (100 - confidence * 100)
        risk_color = "#d32f2f" if risk_level >= 75 else "#f57c00" if risk_level >= 50 else "#388e3c"

        # Custom bar
        st.markdown(f"""
            <div class='risk-bar'>
                <div class='risk-fill' style='width: {int(risk_level)}%; background-color: {risk_color};'>
                    {int(risk_level)}% Risk
                </div>
            </div>
        """, unsafe_allow_html=True)

        # Classification summary
        st.markdown("### 🔍 Result:")
        if prediction == 1:
            if confidence >= 0.9:
                st.error(f"⚠️ High Confidence: This message is a SCAM! ({confidence*100:.1f}%)")
            elif confidence >= 0.7:
                st.warning(f"⚠️ Likely Scam ({confidence*100:.1f}%)")
            else:
                st.warning(f"⚠️ Suspicious Message ({confidence*100:.1f}%)")
        else:
            if confidence >= 0.9:
                st.success(f"✅ This message looks SAFE. ({confidence*100:.1f}%)")
            else:
                st.info(f"🟡 Message likely safe, but double-check. ({confidence*100:.1f}%)")
            if 'msg_lower' in locals() and is_suspicious:
                st.warning("⚠️ Mentions sensitive keywords. Stay alert.")

        # Feedback
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

        # Footer
        st.markdown("---")
        st.markdown("⚠️ Always verify suspicious messages directly with your provider.")
        st.markdown("🛡️ ScamSniperAI uses AI + logic to help spot scam threats.")
