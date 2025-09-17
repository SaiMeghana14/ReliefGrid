import streamlit as st
import utils
import json
from streamlit_lottie import st_lottie

st.set_page_config(page_title="ReliefGrid - Notifications", layout="wide")
with open("app.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.title("🔔 Notifications & Alerts")

# load lottie
def load_lottie(path):
    try:
        with open(path, "r") as f:
            return json.load(f)
    except:
        return None

anim = load_lottie("assets/notify.json")
if anim:
    st_lottie(anim, height=160, key="notify_main")

alerts = utils.get_alerts()
if not alerts:
    st.info("No active alerts.")
else:
    for a in alerts:
        st.warning(f"{a.get('title')} — {a.get('message')}")
        if a.get("resource_id"):
            if st.button(f"Mark resolved ({a.get('resource_id')})", key=f"res_{a.get('resource_id')}"):
                utils.resolve_alert(a.get('id'))
                st.experimental_rerun()

st.markdown("---")
st.write("You can enable SNS notifications by setting AWS creds and `USE_AWS=true` in your environment.")
