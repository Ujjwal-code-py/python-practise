import streamlit as st
import pandas as pd
import requests

OLLAMA_URL = "http://localhost:11434"

st.title("📊 AI Dataset Insights (Fast Version)")

# --- get available models from Ollama automatically ---
@st.cache_data
def get_ollama_models():
    try:
        resp = requests.get(f"{OLLAMA_URL}/api/tags", timeout=10)
        if resp.status_code == 200:
            tags = resp.json().get("models", [])
            return [m["name"] for m in tags]  # names like "llama2:7b"
    except Exception:
        return []
    return []

models = get_ollama_models()
if not models:
    st.warning("Could not fetch models from Ollama. Check if Ollama is running.")
MODEL_NAME = st.selectbox("Select a model to use", models)

uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.write("### Preview of your data")
    st.dataframe(df.head())

    if st.button("Generate AI Insights"):
        # ---- compute summaries in Python (fast) ----
        summary = {
            "columns_and_types": df.dtypes.astype(str).to_dict(),
            "missing_values": df.isnull().sum().to_dict(),
            "describe": df.describe(include='all').fillna("").to_dict(),
            "correlations": df.corr(numeric_only=True).fillna("").to_dict()
        }

        prompt = f"""You are a helpful data analyst.
Here is a summary of the dataset:

{summary}

Explain in plain English:
- What the data contains
- Key patterns or anomalies
- Interesting relationships between variables
- Any recommendations or insights
"""

        with st.spinner("Thinking..."):
            try:
                response = requests.post(
                    f"{OLLAMA_URL}/api/generate",
                    json={
                        "model": MODEL_NAME,
                        "prompt": prompt,
                        "stream": False
                    },
                    timeout=300
                )
                if response.status_code == 200:
                    result_json = response.json()
                    st.markdown("### 🧠 Insights from Ollama:")
                    st.write(result_json.get("response", "No response field"))
                else:
                    st.error(f"Ollama API error {response.status_code}: {response.text}")
            except Exception as e:
                st.error(f"Error contacting Ollama: {e}")
