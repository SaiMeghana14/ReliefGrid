import streamlit as st
import pandas as pd
import json
import time
from streamlit_lottie import st_lottie
import utils
st.set_page_config(page_title="ReliefGrid", layout="wide", initial_sidebar_state="expanded")

import auth
if not auth.is_logged_in():
    st.warning("Please login first.")
    st.stop()

# styles
with open("app.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Load lottie safely
def load_lottie_file(path):
    try:
        with open(path, "r") as f:
            return json.load(f)
    except Exception:
        return None

lottie_banner = load_lottie_file("assets/banner.json")
if lottie_banner:
    st_lottie(lottie_banner, height=200, key="banner")

# Header row
col1, col2 = st.columns([0.8, 0.2])
with col1:
    st.title("🌍 ReliefGrid — Resource Exchange Dashboard")
    st.write("Find, offer, and request resources during emergencies. Demo mode: **Local JSON** or enable **AWS**.")
with col2:
    try:
        st.image("assets/logo.png", width=120)
    except Exception:
        st.write(" ")

# Fetch resources
resources = utils.get_resources()
df = pd.DataFrame(resources)

# summary metrics
total_resources = len(df)
exchanges_completed = utils.get_stats().get("exchanges_completed", 0)
active_alerts = utils.get_stats().get("active_alerts", 0)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Resources", total_resources)
c2.metric("Exchanges Completed", exchanges_completed)
c3.metric("Active Alerts", active_alerts)
c4.metric("Last Updated", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))

# quick filters
st.subheader("Quick Search")
q_col1, q_col2, q_col3 = st.columns([3,2,2])
with q_col1:
    keyword = st.text_input("Search descriptions / keywords")
with q_col2:
    category = st.selectbox("Category", ["All"] + sorted(df['category'].dropna().unique().tolist()))
with q_col3:
    location = st.text_input("Location (city/state)")

filtered = df.copy()
if keyword:
    filtered = filtered[filtered['description'].str.contains(keyword, case=False, na=False)]
if category and category != "All":
    filtered = filtered[filtered['category'] == category]
if location:
    filtered = filtered[filtered['description'].str.contains(location, case=False, na=False)]

st.markdown("### Recent Resources")
st.dataframe(filtered.sort_values("timestamp", ascending=False).reset_index(drop=True), height=350)

st.markdown("---")
st.markdown("Built for hackathons — switch between **Demo (local)** and **AWS** by changing environment variables.")
