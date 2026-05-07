import streamlit as st

from config.constants import APP_NAME
from config.settings import settings

st.set_page_config(
    page_title=APP_NAME,
    page_icon="📺",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title(f"📺 {APP_NAME}")
st.caption(f"API: `{settings.api_base_url}`")
st.info("Selecciona una sección en el menú lateral.")
