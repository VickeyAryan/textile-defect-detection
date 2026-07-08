"""Streamlit demo: upload a fabric image, get a predicted defect class and confidence."""

import os
import sys

import streamlit as st
import torch
from PIL import Image

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from data_loader import build_transforms  # noqa: E402
from model import build_model  # noqa: E402

CHECKPOINT_PATH = os.path.join(os.path.dirname(__file__), "..", "models", "best_model.pt")


@st.cache_resource
def load_model():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    checkpoint = torch.load(CHECKPOINT_PATH, map_location=device, weights_only=False)
    model = build_model(checkpoint["arch"], num_classes=len(checkpoint["class_names"]))
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()
    return model.to(device), checkpoint["class_names"], checkpoint["img_size"], device


def predict(image: Image.Image, model, class_names, img_size, device):
    _, eval_tf = build_transforms(img_size)
    tensor = eval_tf(image.convert("RGB")).unsqueeze(0).to(device)
    with torch.no_grad():
        logits = model(tensor)
        probs = torch.softmax(logits, dim=1).squeeze(0).cpu()
    top_prob, top_idx = probs.max(0)
    ranked = sorted(zip(class_names, probs.tolist()), key=lambda x: x[1], reverse=True)
    return class_names[top_idx], top_prob.item(), ranked


def main():
    st.set_page_config(page_title="Fabric Defect Detector", page_icon="🧵")
    st.title("Fabric Defect Detector")
    st.write("Upload a fabric image to classify it as defect-free or a specific defect type.")

    if not os.path.exists(CHECKPOINT_PATH):
        st.error(
            f"No trained model found at `{CHECKPOINT_PATH}`. "
            "Train a model first (see notebooks/train_model.ipynb or src/train.py)."
        )
        return

    model, class_names, img_size, device = load_model()

    uploaded_file = st.file_uploader("Upload a fabric image", type=["jpg", "jpeg", "png", "bmp"])
    if uploaded_file is None:
        return

    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded image", use_container_width=True)

    predicted_class, confidence, ranked = predict(image, model, class_names, img_size, device)

    st.subheader(f"Prediction: **{predicted_class}**")
    st.write(f"Confidence: {confidence:.1%}")

    st.write("Class probabilities:")
    for name, prob in ranked:
        st.progress(prob, text=f"{name}: {prob:.1%}")


if __name__ == "__main__":
    main()
