import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline
import pandas as pd
import numpy as np
import os
from datetime import datetime

# UI Styling
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #0f2027, #2c5364, #00c9a7);
        background-attachment: fixed;
    }
    html, body, [class*="css"]  {
        font-family: 'Poppins', sans-serif;
    }
    </style>
""", unsafe_allow_html=True)

# Load dataset
df = pd.read_csv("scam_superdataset_10k.csv")
X = df['message']
y = df['label']

# Build model pipeline
model = make_pipeline(TfidfVectorizer(), MultinomialNB())
model.fit(X, y)

# Keyword lists
suspicious_keywords = ["account", "bank", "verify", "payment", "transaction", "wallet",
    "login", "credentials", "password", "electricity", "bill", 
    "customs", "link", "refund", "kyc", "failed", "urgent"]

bait_words = ["send", "receive", "$", "win", "money", "prize", "reward", "rich"]
short_red_flags = ["scam", "money now", "prize", "send money", "rich", "$$$", "lottery",
    "click", "verify", "account", "win", "otp", "bank", "reward"]

known_safe_phrases = ["how to protect", "guide to avoid", "scam awareness",
    "educate about scams", "help elderly", "protect seniors from scams",
    "tips to stay safe", "avoid getting scammed", "protecting elderly people from scams"]

# Logic functions
def is_known_safe(msg):
    msg_lower = msg.lower()
    return any(phrase in msg_lower for phrase in known_safe_phrases)

def is_bait_scam(msg):
    msg_lower = msg.lower()
    word_spam = sum(word in msg_lower for word in bait_words) >= 3
    dollar_count = msg.count("$") >= 2
    big_number = any(char.isdigit() and len(token) > 6 for token in msg.split() for char in token)
    return word_spam or dollar_count or big_number

def is_short_scam(msg):
    msg_lower = msg.lower().strip()
    return len(msg_lower) <= 5 or any(flag in msg_lower for flag in short_red_flags)

# Explanation generator
def generate_explanation(msg):
    msg_lower = msg.lower()
    reasons = []
    if any(k in msg_lower for k in suspicious_keywords):
        reasons.append("The message contains keywords like 'account', 'verify', or 'refund', which are commonly used in phishing and scam messages.")
    if is_bait_scam(msg):
        reasons.append("It includes words like 'win', 'prize', or '$', and may be trying to bait you with fake rewards or money scams.")
    if is_short_scam(msg):
        reasons.append("The message is short and vague with suspicious language like 'money now' or 'click', which is a common trait of spam or scams.")
    if not reasons:
        reasons.append("The language and tone of the message matched patterns found in known scam messages in the training data.")
    return " ".join(reasons[:2])  # Limit to 2 explanations

# Feedback logger
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

# Streamlit UI
st.set_page_config(page_title="ScamSniperAI", page_icon="\ud83d\udcf1")
st.title("\ud83d\udcf1 ScamSniperAI")
st.caption("Your local AI-powered scam message detector.")
st.caption("Made for the elderly by the youth")
st.markdown("---")

msg = st.text_area("\ud83d\udce9 Paste the SMS or WhatsApp message below")

if st.button("\ud83d\udd0d Analyze"):
    if not msg.strip():
        st.warning("Please enter a message.")
    else:
        if is_known_safe(msg):
            prediction = 0
            confidence = 0.99
        else:
            prediction = model.predict([msg])[0]
            confidence = model.predict_proba([msg])[0][prediction]
            if is_bait_scam(msg) or is_short_scam(msg):
                prediction = 1
                confidence = max(confidence, 0.97)

        # Scam Risk Meter
        st.subheader("\ud83d\udcca Scam Risk Meter")
        risk_percent = (1 - confidence) * 100 if prediction == 1 else (100 - confidence * 100)
        if prediction == 1:
            if confidence >= 0.9:
                st.markdown("### \ud83d\udd34 HIGH RISK: Definitely a SCAM!")
            elif confidence >= 0.7:
                st.markdown("### \ud83d\udea0 Likely a scam. Be cautious.")
            else:
                st.markdown("### \u26a0\ufe0f Suspicious. Double-check manually.")
        else:
            if confidence >= 0.9:
                st.markdown("### \ud83d\udfe2 Safe Message")
            elif confidence >= 0.7:
                st.markdown("### \ud83d\udfe1 Likely safe. Still verify.")
            else:
                st.markdown("### \u26a0\ufe0f Unclear. Use caution.")

        st.progress(int(risk_percent))

        # Final result
        st.markdown("---")
        if prediction == 1:
            st.error(f"\u26a0\ufe0f This message looks like a SCAM! ({confidence*100:.1f}% confidence)")
            explanation = generate_explanation(msg)
            st.markdown(f"#### \ud83e\uddd0 Why?")
            st.info(explanation)
        else:
            st.success(f"\u2705 This message looks SAFE. ({confidence*100:.1f}% confidence)")

        # Feedback Buttons
        st.markdown("#### \ud83e\udd16 Was this prediction correct?")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("\ud83d\udc4d Yes"):
                st.success("Thanks for confirming!")
        with col2:
            if st.button("\ud83d\udc4e No"):
                st.warning("Logged! We'll learn from this.")
                correct_label = 0 if prediction == 1 else 1
                log_feedback(msg, prediction, confidence, correct_label)

        # Footer
        st.markdown("---")
        st.markdown("\u26a0\ufe0f ALWAYS VERIFY SUSPICIOUS MESSAGES DIRECTLY WITH YOUR SERVICE PROVIDER.")
        st.markdown("\ud83d\udd0d ScamSniperAI IS NOT PROFESSIONAL ADVICE. ALWAYS SEEK SECOND OPINIONS.")
        st.markdown("\u26a0\ufe0f ScamSniperAI is not responsible for any losses or issues arising from following its advice.")
        st.markdown("\ud83d\udee1\ufe0f *ScamSniperAI uses AI + keyword suspicion logic to help detect risky messages.*")


