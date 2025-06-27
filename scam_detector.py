import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline
import pandas as pd
import numpy as np

# === Load Dataset ===
df = pd.read_csv("scam_superdataset_10k.csv")
X = df['message']
y = df['label']

model = make_pipeline(TfidfVectorizer(), MultinomialNB())
model.fit(X, y)

# === Keyword Flags ===
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
    return any(phrase in msg.lower() for phrase in known_safe_phrases)

def is_bait_scam(message):
    message = message.lower()
    custom_words = ["send", "receive", "$", "win", "money", "prize", "reward", "rich"]
    word_spam = sum(word in message for word in custom_words) >= 3
    dollar_count = message.count("$") >= 2
    big_number = any(char.isdigit() and len(token) > 6 for token in message.split() for char in token)
    return word_spam or dollar_count or big_number

def is_short_scam(msg):
    msg = msg.lower().strip()
    short_flags = [
        "scam", "money now", "prize", "send money", "rich", "$$$", "lottery",
        "click", "verify", "account", "win", "otp", "bank", "reward"
    ]
    return len(msg) <= 5 or any(flag in msg for flag in short_flags)

# === Page Config ===
st.set_page_config(page_title="ScamSniperAI", page_icon="📱", layout="centered")

# === Sleek UI Styling ===
st.markdown("""
    <style>
        html, body, [class*="css"]  {
            background: linear-gradient(135deg, #f0f4f8 0%, #e8f0ff 100%) !important;
            color: #1c1c1e;
            font-family: 'Segoe UI', sans-serif;
        }
        .stTextArea > label {
            font-size: 1.2rem;
            font-weight: 500;
        }
        .result-card {
            background: #ffffff;
            padding: 1.5rem;
            border-radius: 1.5rem;
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.08);
        }
        .risk-meter {
            height: 18px;
            background: linear-gradient(to right, #4CAF50, #FFC107, #F44336);
            border-radius: 10px;
            margin-top: 10px;
        }
        .stButton button {
            border-radius: 10px;
            font-weight: bold;
            background: linear-gradient(90deg, #0072ff, #00c6ff);
            color: white;
            padding: 0.5rem 1rem;
            border: none;
        }
    </style>
""", unsafe_allow_html=True)

# === UI ===
st.title("📱 ScamSniperAI")
st.caption("Made for the elderly. Powered by youth.")
st.markdown("---")

msg = st.text_area("📩 Paste the SMS or WhatsApp message below")

if st.button("🔍 Analyze Message"):
    if not msg.strip():
        st.warning("Please enter a message.")
    else:
        if is_known_safe(msg):
            prediction, confidence = 0, 0.99
        else:
            prediction = model.predict([msg])[0]
            confidence = model.predict_proba([msg])[0][prediction]
            if is_bait_scam(msg) or is_short_scam(msg):
                prediction = 1
                confidence = max(confidence, 0.97)

        # === Risk Meter ===
        st.markdown("<div class='result-card'>", unsafe_allow_html=True)

        if prediction == 1:
            st.error(f"⚠️ This message looks like a SCAM! ({confidence*100:.1f}% confidence)")
        else:
            st.success(f"✅ This message looks SAFE. ({confidence*100:.1f}% confidence)")
            if any(word in msg.lower() for word in suspicious_keywords):
                st.warning("⚠️ BUT this message mentions sensitive words like accounts, payments, or verification. Please double-check with your bank or provider.")

        st.markdown("<div class='risk-meter'></div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # === Feedback Buttons ===
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("👍 Mark as Correct"):
                st.success("Thanks! Feedback noted.")
        with col2:
            if st.button("👎 Suggest Correction"):
                st.info("We'll use this to improve ScamSniperAI.")

        # === Footer ===
        st.markdown("---")
        st.markdown("⚠️ ALWAYS VERIFY SUSPICIOUS MESSAGES DIRECTLY WITH YOUR SERVICE PROVIDER.")
        st.caption("ScamSniperAI is not professional advice. It’s a learning AI tool.")
