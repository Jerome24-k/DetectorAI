import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline
import pandas as pd
import numpy as np
import os
from datetime import datetime

# 🌈 Modern background + font
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #0f2027, #2c5364, #00c9a7);
        background-attachment: fixed;
        color: #ffffff;
    }
    @import url('https://fonts.googleapis.com/css2?family=Poppins&display=swap');
    html, body, [class*="css"]  {
        font-family: 'Poppins', sans-serif;
    }
    </style>
""", unsafe_allow_html=True)

# 📂 Load custom dataset
df = pd.read_csv("scam_superdataset_10k.csv")
X = df['message']
y = df['label']
model = make_pipeline(TfidfVectorizer(), MultinomialNB())
model.fit(X, y)

# 🚨 Keyword logic
suspicious_keywords = [
    "account", "bank", "verify", "payment", "transaction", "wallet", "login",
    "credentials", "password", "electricity", "bill", "customs", "link", "refund", "kyc", "failed", "urgent"
]
safe_free_contexts = [
    "free books", "free food", "free course", "free resources", "free seminar", "free webinar",
    "free education", "free library", "free safety guide"
]
known_safe_phrases = [
    "how to protect", "guide to avoid", "scam awareness", "educate about scams", "help elderly",
    "tips to stay safe", "avoid getting scammed", "protecting elderly people from scams"
]

# ⚙️ Logic helpers
def is_known_safe(msg):
    msg_lower = msg.lower()
    return any(phrase in msg_lower for phrase in known_safe_phrases)

def is_safe_free_context(msg):
    msg_lower = msg.lower()
    return "free" in msg_lower and any(phrase in msg_lower for phrase in safe_free_contexts)

def is_bait_scam(msg):
    msg_lower = msg.lower()
    bait = ["send", "receive", "$", "win", "money", "prize", "reward", "rich"]
    word_spam = sum(word in msg_lower for word in bait) >= 3
    dollar_count = msg.count("$") >= 2
    big_number = any(char.isdigit() and len(token) > 6 for token in msg.split() for char in token)
    return word_spam or dollar_count or big_number

def is_short_scam(msg):
    msg_lower = msg.lower().strip()
    short_red_flags = [
        "scam", "money now", "prize", "send money", "rich", "$$$", "lottery",
        "click", "verify", "account", "win", "otp", "bank", "reward"
    ]
    return len(msg_lower) <= 5 or any(flag in msg_lower for flag in short_red_flags)

def is_scammy_free(msg):
    msg_lower = msg.lower()
    free_count = msg_lower.count("free")
    trigger_words = ["click", "win", "now", "limited", "offer", "guarantee", "urgent", "cash", "gift"]
    triggers = sum(word in msg_lower for word in trigger_words)
    if free_count >= 2 and triggers >= 1:
        return True
    if "free" in msg_lower and triggers >= 2:
        return True
    return False

def explain_reason(msg, prediction, logic_flags):
    msg = msg.lower()
    reasons = []

    if prediction == 1:
        if is_bait_scam(msg):
            reasons.append("The message contains multiple signs of a bait scam, like money promises or excessive dollar symbols.")
        if is_short_scam(msg):
            reasons.append("Very short messages with high-risk words like 'scam', 'prize', or 'win' are often fraudulent.")
        if "free" in msg and not is_safe_free_context(msg) and is_scammy_free(msg):
            reasons.append("The word 'free' was found in a context with suspicious trigger words like 'click', 'urgent', or 'gift'.")
        if any(k in msg for k in suspicious_keywords):
            matched = [k for k in suspicious_keywords if k in msg]
            reasons.append(f"Suspicious terms like {', '.join(matched)} were found in the message.")
        if not reasons:
            reasons.append("The message content appears to match patterns often associated with scams.")
    else:
        reasons.append("No strong scam patterns were detected, and the content appears informational or conversational.")
        if any(k in msg for k in suspicious_keywords):
            reasons.append("Still, sensitive words like 'account' or 'payment' were found, so caution is advised.")

    return " ".join(reasons[:3])

# 🧠 Feedback logger
def log_feedback(message, prediction, confidence, correct_label):
    log_file = "feedback_log.csv"
    entry = {
        "timestamp": datetime.now().isoformat(),
        "message": message,
        "prediction": prediction,
        "confidence": round(confidence, 4),
        "correct_label": correct_label
    }
    if os.path.exists(log_file):
        pd.DataFrame([entry]).to_csv(log_file, mode='a', header=False, index=False)
    else:
        pd.DataFrame([entry]).to_csv(log_file, index=False)

# 🚀 Streamlit UI
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
            prediction, confidence = 0, 0.99
        else:
            prediction = model.predict([msg])[0]
            confidence = model.predict_proba([msg])[0][prediction]

            if is_bait_scam(msg) or is_short_scam(msg) or ("free" in msg.lower() and not is_safe_free_context(msg) and is_scammy_free(msg)):
                prediction = 1
                confidence = max(confidence, 0.97)

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

        st.markdown("---")
        reason = explain_reason(msg, prediction, logic_flags=True)
        if prediction == 1:
            st.error(f"⚠️ This message looks like a SCAM! ({confidence*100:.1f}% confidence)\n\n💬 **Why?** {reason}")
        else:
            st.success(f"✅ This message looks SAFE. ({confidence*100:.1f}% confidence)\n\n💬 **Why?** {reason}")

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

        st.markdown("---")
        st.markdown("⚠️ ALWAYS VERIFY SUSPICIOUS MESSAGES DIRECTLY WITH YOUR SERVICE PROVIDER.")
        st.markdown("🔍 ScamSniperAI IS NOT PROFESSIONAL ADVICE. ALWAYS SEEK SECOND OPINIONS.")
        st.markdown("🛡️ *ScamSniperAI uses AI + keyword suspicion logic to help detect risky messages.*")


