import streamlit as st
import uuid
import time
import utils
import json
from streamlit_lottie import st_lottie

st.set_page_config(page_title="ReliefGrid - Post Resource", layout="wide")
with open("app.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.title("➕ Post a Resource")

# load success animation
def load_lottie(path):
    try:
        with open(path, "r") as f:
            return json.load(f)
    except:
        return None

success_anim = load_lottie("assets/success.json")

with st.form("post_form"):
    col1, col2 = st.columns(2)
    with col1:
        category = st.selectbox("Category", ["Food", "Water", "Shelter", "Medicine", "Volunteers", "Other"])
        description = st.text_area("Description", help="Location, contact, details (e.g., 'Rice sacks, near MG Road, Hyderabad')")
        quantity = st.number_input("Quantity", min_value=1, value=1)
    with col2:
        lat = st.number_input("Latitude", format="%.6f", value=20.5937)
        lon = st.number_input("Longitude", format="%.6f", value=78.9629)
        contact = st.text_input("Contact (phone/email)")
        urgency = st.selectbox("Urgency", ["Normal", "High", "Urgent"])
    submit = st.form_submit_button("Post Resource")

if submit:
    item = {
        "id": str(uuid.uuid4()),
        "category": category,
        "description": f"{description} | Contact: {contact} | Urgency: {urgency}",
        "quantity": int(quantity),
        "lat": float(lat),
        "lon": float(lon),
        "timestamp": int(time.time())
    }
    utils.save_resource(item)
    utils.send_sns_notification(f"New resource posted: {category} | {description}")
    st.success("Resource posted successfully!")
    if success_anim:
        st_lottie(success_anim, height=180, key="success_post")
