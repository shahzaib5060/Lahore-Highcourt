"""Streamlit wrapper for the LHCBA voter roll dashboard.

The dashboard itself is index.html. Its photos are 9 image sheets
(sheet_0.jpg to sheet_8.jpg). Sending them through Streamlit made the
page too heavy to load, so the browser fetches them straight from this
GitHub repository instead.
"""
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

HERE = Path(__file__).parent

# Where the browser loads the photo sheets from. This works while the
# repository is public. If you make it private, the photos will stop
# showing and this needs to change.
PHOTO_BASE_URL = "https://raw.githubusercontent.com/shahzaib5060/Lahore-Highcourt/main/"

st.set_page_config(page_title="LHCBA Voter Roll 2022-23", page_icon="⚖️", layout="wide")

# Remove Streamlit's own padding and header so the dashboard fills the window.
st.markdown(
    """
    <style>
      .block-container {padding: 0 !important; max-width: 100% !important;}
      header[data-testid="stHeader"] {display: none;}
      iframe {display: block;}
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_resource(show_spinner="Loading dashboard…")
def build_page() -> str:
    html = (HERE / "index.html").read_text(encoding="utf-8")
    for k in range(9):
        name = f"sheet_{k}.jpg"
        html = html.replace(f'"photos/{name}"', f'"{PHOTO_BASE_URL}{name}"')
    return html


components.html(build_page(), height=1600, scrolling=True)
