from pathlib import Path
import os

import streamlit as st


MODEL_DIR = Path(os.environ.get("TAKEMETER_MODEL_DIR", "takemeter-model"))
FALLBACK_LABELS = ["NTA", "YTA", "NAH", "ESH"]
LABEL_DESCRIPTIONS = {
    "NTA": "Not the Asshole",
    "YTA": "You're the Asshole",
    "NAH": "No Assholes Here",
    "ESH": "Everyone Sucks Here",
    "poster_not_blamed": "Poster not mainly blamed",
    "poster_blamed": "Poster mainly blamed",
}


@st.cache_resource
def load_model():
    sklearn_path = MODEL_DIR / "tfidf_logreg.joblib"
    if sklearn_path.exists():
        import joblib

        return "sklearn", joblib.load(sklearn_path)

    from transformers import AutoModelForSequenceClassification, AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_DIR)
    model.eval()
    return "transformers", (tokenizer, model)


def label_for(model, label_id):
    id2label = getattr(model.config, "id2label", {}) or {}
    return id2label.get(label_id) or id2label.get(str(label_id)) or (
        FALLBACK_LABELS[label_id] if label_id < len(FALLBACK_LABELS) else str(label_id)
    )


def predict(text):
    model_type, payload = load_model()
    if model_type == "sklearn":
        model = payload
        probs = model.predict_proba([text])[0]
        idx = int(probs.argmax())
        label = model.classes_[idx]
        return label, float(probs[idx]), list(zip(model.classes_, probs))

    import torch

    tokenizer, model = payload
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=256)
    with torch.no_grad():
        output = model(**inputs)
        probs = torch.softmax(output.logits, dim=-1)[0]
    pred_id = int(torch.argmax(probs).item())
    return label_for(model, pred_id), float(probs[pred_id]), list(enumerate(probs.tolist()))


st.set_page_config(page_title="AITA Verdict Compass", page_icon="A", layout="centered")

st.title("AITA Verdict Compass")
st.caption("Predicts the AITA community verdict from the original post text.")

if not MODEL_DIR.exists():
    st.error(
        "Model directory not found. Download or save the fine-tuned HuggingFace model "
        f"as `{MODEL_DIR}` before running this app."
    )
    st.stop()

post_text = st.text_area(
    "Post text",
    height=260,
    placeholder="AITA for ...",
)

if st.button("Classify", type="primary", disabled=not post_text.strip()):
    label, confidence, probs = predict(post_text)
    st.metric("Predicted verdict", f"{label} - {LABEL_DESCRIPTIONS.get(label, label)}", f"{confidence:.1%} confidence")

    st.subheader("Class probabilities")
    rows = []
    model_type, payload = load_model()
    for item, prob in probs:
        if model_type == "sklearn":
            row_label = item
        else:
            _, model = payload
            row_label = label_for(model, item)
        rows.append({
            "label": row_label,
            "meaning": LABEL_DESCRIPTIONS.get(row_label, ""),
            "confidence": round(prob, 4),
        })
    st.dataframe(rows, hide_index=True, use_container_width=True)
