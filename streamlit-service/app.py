import os
import requests
import streamlit as st

GATEWAY_URL = os.getenv("GATEWAY_URL", "http://localhost:8080")

st.set_page_config(page_title="WikiMind", page_icon="🧠", layout="centered")
st.title("🧠 WikiMind")
st.caption("Ask anything about AI, Machine Learning, Neural Networks, NLP, or Transformers.")

# Sidebar health status
with st.sidebar:
    st.header("System Status")
    try:
        health = requests.get(f"{GATEWAY_URL}/health", timeout=5).json()
        if health.get("db_loaded"):
            st.success(f"Ready — {health['chunk_count']} chunks loaded")
        else:
            st.warning("ChromaDB not loaded. Run ingest.py first.")
    except Exception:
        st.error("Cannot reach the backend. Is it running?")

question = st.text_input("Your question", placeholder="What is a transformer model?")

if st.button("Ask", disabled=not question):
    with st.spinner("Thinking..."):
        try:
            resp = requests.post(
                f"{GATEWAY_URL}/ask",
                json={"question": question},
                timeout=120,
            )
            resp.raise_for_status()
            data = resp.json()

            st.markdown("### Answer")
            st.write(data["answer"])

            if data.get("sources"):
                st.markdown("### Sources")
                for src in data["sources"]:
                    st.markdown(f"- [{src}]({src})")

        except requests.HTTPError as e:
            st.error(f"Request failed: {e.response.status_code} — {e.response.text}")
        except Exception as e:
            st.error(f"Error: {e}")
