import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline
import pandas as pd
import numpy as np
import os
from datetime import datetime

# 🌐 Language support
LANGUAGES = {
    "English": {
        "title": "📱 ScamSniperAI",
        "caption_1": "Your local AI-powered scam message detector.",
        "caption_2": "Made for the elderly by the youth",
        "input_label": "📩 Paste the SMS or WhatsApp message below",
        "analyze_button": "🔍 Analyze",
        "empty_warning": "Please enter a message.",
        "scam_meter": "📊 Scam Risk Meter",
        "high_risk": "### 🔴 HIGH RISK: Definitely a SCAM!",
        "likely_scam": "### 🟠 Likely a scam. Be cautious.",
        "suspicious": "### ⚠️ Suspicious. Double-check manually.",
        "safe": "### 🟢 Safe Message",
        "likely_safe": "### 🟡 Likely safe. Still verify.",
        "unclear": "### ⚠️ Unclear. Use caution.",
        "prediction_correct": "#### 🤖 Was this prediction correct?",
        "yes": "👍 Yes",
        "no": "👎 No",
        "thanks": "Thanks for confirming!",
        "logged": "Logged! We'll learn from this.",
        "footer_1": "⚠️ ALWAYS VERIFY SUSPICIOUS MESSAGES DIRECTLY WITH YOUR SERVICE PROVIDER.",
        "footer_2": "🔍 ScamSniperAI IS NOT PROFESSIONAL ADVICE. ALWAYS SEEK SECOND OPINIONS.",
        "footer_3": "🛡️ *ScamSniperAI uses AI + keyword suspicion logic to help detect risky messages.*",
        "scam_msg": "⚠️ This message looks like a SCAM!",
        "safe_msg": "✅ This message looks SAFE.",
        "why": "💬 **Why?**"
    },
    "Malayalam": {
        "title": "📱 സ്കാംസ്നൈപ്പർAI",
        "caption_1": "നിങ്ങളുടെ AI-അധികാരപ്രാപ്തിയുള്ള തട്ടിപ്പ് സന്ദേശ നിരീക്ഷകന്‍.",
        "caption_2": "വൃദ്ധര്ക്കായി യുവാക്കള്‍ ഒരുക്കിയത്",
        "input_label": "📩 നിങ്ങളുടെ SMS അല്ലെങ്കിൽ WhatsApp സന്ദേശം ഇവിടെ പതിച്ചുക",
        "analyze_button": "🔍 വിശകലനം ചെയ്യുക",
        "empty_warning": "ദയവായി സന്ദേശം നൽകുക.",
        "scam_meter": "📊 തട്ടിപ്പ് റിസ്‌ക് മീറ്റർ",
        "high_risk": "### 🔴 ഉയര്‍ന്ന അപകടം: തട്ടിപ്പാണ്!",
        "likely_scam": "### 🟠 തട്ടിപ്പാകാം. ജാഗ്രത പാലിക്കുക.",
        "suspicious": "### ⚠️ സംശയാസ്പദം. വീണ്ടും പരിശോധിക്കുക.",
        "safe": "### 🟢 സുരക്ഷിത സന്ദേശം",
        "likely_safe": "### 🟡 സുരക്ഷിതമാകാം. ഉറപ്പുവരുത്തുക.",
        "unclear": "### ⚠️ വ്യക്തമല്ല. ജാഗ്രത പാലിക്കുക.",
        "prediction_correct": "#### 🤖 ഈ പ്രവചനം ശരിയായിരുന്നു?",
        "yes": "👍 ശരിയാണ്",
        "no": "👎 തെറ്റാണ്",
        "thanks": "ധന്യവാദം!",
        "logged": "ലോഗ് ചെയ്തു! ഞങ്ങൾ പഠിക്കുമെന്ന് ഉറപ്പാണ്.",
        "footer_1": "⚠️ സംശയാസ്പദമായ സന്ദേശങ്ങൾ നിങ്ങളുടേതായ സേവനദായകരെ ബന്ധപ്പെടി സ്ഥിരീകരിക്കുക.",
        "footer_2": "🔍 ScamSniperAI ഒരു വിദഗ്ധ ഉപദേശം അല്ല. രണ്ടാമതൊരു അഭിപ്രായം നേടുക.",
        "footer_3": "🛡️ *ScamSniperAI എഐയും കീവേഡ് ലോജിക്‌ഉം ഉപയോഗിച്ച് സംശയാസ്പദ സന്ദേശങ്ങൾ കണ്ടെത്താൻ സഹായിക്കുന്നു.*",
        "scam_msg": "⚠️ ഈ സന്ദേശം ഒരു തട്ടിപ്പായി തോന്നുന്നു!",
        "safe_msg": "✅ ഈ സന്ദേശം സുരക്ഷിതമാണെന്ന് തോന്നുന്നു.",
        "why": "💬 **എന്തുകൊണ്ട്?**"
    }
}

# 🌐 Language selector
lang_choice = st.sidebar.selectbox("🌍 Language / ഭാഷ", list(LANGUAGES.keys()))
T = LANGUAGES[lang_choice]

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

# 📂 Load dataset + model
df = pd.read_csv("scam_superdataset_10k.csv")
X = df['message']
y = df['label']
model = make_pipeline(TfidfVectorizer(), MultinomialNB())
model.fit(X, y)

# 💡 Logic
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

def explain_reason(msg, prediction):
    msg = msg.lower()
    reasons = []

    if prediction == 1:
        if is_bait_scam(msg):
            reasons.append("Contains bait words like money, win, or prize.")
        if is_short_scam(msg):
            reasons.append("Message is short with red flags.")
        if "free" in msg and not is_safe_free_context(msg) and is_scammy_free(msg):
            reasons.append("‘Free’ used in suspicious context.")
        if any(k in msg for k in suspicious_keywords):
            matched = [k for k in suspicious_keywords if k in msg]
            reasons.append(f"Suspicious terms: {', '.join(matched)}")
        if not reasons:
            reasons.append("Message matches scam-like patterns.")
    else:
        reasons.append("No strong scam patterns were found.")
        if any(k in msg for k in suspicious_keywords):
            reasons.append("Still contains sensitive words like ‘account’, ‘payment’, etc.")
    return " ".join(reasons[:3])

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

# 🚀 UI
st.set_page_config(page_title="ScamSniperAI", page_icon="📱")
st.title(T["title"])
st.caption(T["caption_1"])
st.caption(T["caption_2"])
st.markdown("---")

msg = st.text_area(T["input_label"])

if st.button(T["analyze_button"]):
    if not msg.strip():
        st.warning(T["empty_warning"])
    else:
        if is_known_safe(msg):
            prediction, confidence = 0, 0.99
        else:
            prediction = model.predict([msg])[0]
            confidence = model.predict_proba([msg])[0][prediction]

            bait_flag = is_bait_scam(msg)
            short_flag = is_short_scam(msg)
            scammy_free_flag = "free" in msg.lower() and not is_safe_free_context(msg) and is_scammy_free(msg)
            safe_free_flag = "free" in msg.lower() and is_safe_free_context(msg)

            if bait_flag or short_flag or scammy_free_flag:
                prediction = 1
                confidence = max(confidence, 0.97)

            if safe_free_flag and not bait_flag and not short_flag:
                prediction = 0
                confidence = 0.95

        st.subheader(T["scam_meter"])
        risk_percent = (1 - confidence) * 100 if prediction == 1 else (100 - confidence * 100)

        if prediction == 1:
            if confidence >= 0.9:
                st.markdown(T["high_risk"])
            elif confidence >= 0.7:
                st.markdown(T["likely_scam"])
            else:
                st.markdown(T["suspicious"])
        else:
            if confidence >= 0.9:
                st.markdown(T["safe"])
            elif confidence >= 0.7:
                st.markdown(T["likely_safe"])
            else:
                st.markdown(T["unclear"])

        st.progress(int(risk_percent))
        st.markdown("---")

        reason = explain_reason(msg, prediction)
        if prediction == 1:
            st.error(f"{T['scam_msg']} ({confidence*100:.1f}%)\n\n{T['why']} {reason}")
        else:
            st.success(f"{T['safe_msg']} ({confidence*100:.1f}%)\n\n{T['why']} {reason}")

        st.markdown(T["prediction_correct"])
        col1, col2 = st.columns(2)
        with col1:
            if st.button(T["yes"]):
                st.success(T["thanks"])
        with col2:
            if st.button(T["no"]):
                st.warning(T["logged"])
                correct_label = 0 if prediction == 1 else 1
                log_feedback(msg, prediction, confidence, correct_label)

        st.markdown("---")
        st.markdown(T["footer_1"])
        st.markdown(T["footer_2"])
        st.markdown(T["footer_3"])
