import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline
from datasets import load_dataset

@st.cache_data
def load_model():
    dataset = load_dataset("sms_spam")
    X, y = dataset['train']['sms'], dataset['train']['label']
    model = make_pipeline(TfidfVectorizer(), MultinomialNB())
    model.fit(X, y)
    return model

model = load_model()

suspicious_keywords = [
    "account", "bank", "verify", "payment", "transaction", "wallet",
    "login", "credentials", "password", "electricity", "bill", 
    "customs", "link", "refund", "kyc", "failed", "urgent"
]

st.set_page_config(page_title="ScamSniperAI", page_icon="📱")
st.title("📱 ScamSniperAI")
st.caption("Detect scammy or suspicious messages instantly using AI.")
st.markdown("Type or paste an SMS or WhatsApp message below:")

msg = st.text_area("📝 Message")

if st.button("Analyze"):
    if not msg.strip():
        st.warning("Please enter a message.")
    else:
        prediction = model.predict([msg])[0]
        confidence = model.predict_proba([msg])[0][prediction]
        msg_lower = msg.lower()
        is_suspicious = any(word in msg_lower for word in suspicious_keywords)

        if prediction == 1:
            st.error(f"⚠️ Scam Detected! ({confidence*100:.1f}% confidence)")
        else:
            st.success(f"✅ Looks Safe ({confidence*100:.1f}% confidence)")
            if is_suspicious:
                st.warning("⚠️ But this message mentions accounts or payments. Be cautious!")

        st.markdown("---")
        st.markdown("💡 *Always double-check messages asking for money or personal information.*")
