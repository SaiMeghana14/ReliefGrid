import streamlit as st
import pandas as pd
import utils
import pydeck as pdk
from streamlit_lottie import st_lottie
import json

st.set_page_config(page_title="ReliefGrid - Board", layout="wide")
with open("app.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# load notify lottie
def load_lottie(path):
    try:
        with open(path, "r") as f:
            return json.load(f)
    except:
        return None

notify_anim = load_lottie("assets/notify.json")
if notify_anim:
    st_lottie(notify_anim, height=120, key="notify_small")

st.title("📌 Resource Exchange Board")

resources = utils.get_resources()
df = pd.DataFrame(resources)

# Filters panel
st.sidebar.header("Filters")
keyword = st.sidebar.text_input("Keyword")
category = st.sidebar.multiselect("Category", options=sorted(df['category'].dropna().unique().tolist()))
min_qty = st.sidebar.number_input("Min Quantity", min_value=0, value=0, step=1)
city = st.sidebar.text_input("City / State contains")

filtered = df.copy()
if keyword:
    filtered = filtered[filtered['description'].str.contains(keyword, case=False, na=False)]
if category:
    filtered = filtered[filtered['category'].isin(category)]
if min_qty > 0:
    filtered = filtered[filtered['quantity'].astype(float) >= float(min_qty)]
if city:
    filtered = filtered[filtered['description'].str.contains(city, case=False, na=False)]

st.markdown(f"**Showing {len(filtered)} resources**")
st.dataframe(filtered.reset_index(drop=True), height=300)

# Map visualization with pydeck or fallback
st.subheader("🗺 Map")
if not filtered.empty and 'lat' in filtered.columns and 'lon' in filtered.columns:
    try:
        # Layer toggles
        st.sidebar.header("Map Layers")
        show_scatter = st.sidebar.checkbox("Scatterplot (default)", True)
        show_heatmap = st.sidebar.checkbox("Heatmap", False)
        show_cluster = st.sidebar.checkbox("Cluster Grid", False)

        layers = []

        if show_scatter:
            layers.append(
                pdk.Layer(
                    "ScatterplotLayer",
                    data=filtered,
                    get_position='[lon, lat]',
                    get_color='[255, 120, 80, 160]',
                    get_radius=30000,
                    pickable=True,
                )
            )

        if show_heatmap:
            layers.append(
                pdk.Layer(
                    "HeatmapLayer",
                    data=filtered,
                    get_position='[lon, lat]',
                    aggregation=pdk.types.String("MEAN"),
                    opacity=0.6,
                )
            )

        if show_cluster:
            layers.append(
                pdk.Layer(
                    "ScreenGridLayer",
                    data=filtered,
                    get_position='[lon, lat]',
                    cell_size_pixels=40,
                    color_range=[[255, 180, 0, 200]],
                )
            )

        view = pdk.ViewState(
            latitude=filtered["lat"].mean() if "lat" in filtered else 20.5937,
            longitude=filtered["lon"].mean() if "lon" in filtered else 78.9629,
            zoom=4,
            pitch=30,
        )

        deck = pdk.Deck(map_style="ROAD", layers=layers, initial_view_state=view, tooltip={"text": "{category}: {quantity}"})
        st.pydeck_chart(deck, use_container_width=True)

    except Exception as e:
        # fallback to st.map
        try:
            st.map(filtered[['lat','lon']].dropna())
        except Exception:
            st.write("Map could not be rendered.")
else:
    st.info("No geo data available to render map.")

# Action per row (request / offer)
st.subheader("Take Action")
selected_id = st.selectbox("Select resource ID to Request / Offer", options=[""] + filtered['id'].astype(str).tolist())
action = st.radio("Action", ["Request", "Offer"])
contact = st.text_input("Contact details (phone/email)", placeholder="Optional - used for notifications")

if st.button("Submit Action"):
    if not selected_id:
        st.warning("Choose a resource ID first.")
    else:
        res = utils.get_resource_by_id(selected_id)
        if not res:
            st.error("Resource not found.")
        else:
            payload = {
                "action": action,
                "resource": res,
                "contact": contact
            }
            utils.record_exchange(payload)
            # notify via SNS (mock or real)
            message = f"{action} made for {res.get('category')} - {res.get('description')}"
            utils.send_sns_notification(message)
            st.success(f"{action} submitted & notification sent (mock).")
