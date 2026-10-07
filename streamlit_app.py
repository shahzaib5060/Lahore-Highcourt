"""Streamlit wrapper for the LHCBA voter roll dashboard.

The dashboard itself is index.html. Streamlit shows it inside a frame, where
relative links like photos/sheet_0.jpg don't resolve, so this file reads the
photo sheets and puts them straight into the page before displaying it.
"""
import base64
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

HERE = Path(__file__).parent

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
    # Photo sheets can sit in a photos/ folder or directly next to this file.
    sheets = {p.name: p for p in sorted(HERE.rglob("sheet_*.jpg"))}.values()
    for sheet in sheets:
        data = base64.b64encode(sheet.read_bytes()).decode("ascii")
        html = html.replace(f'"photos/{sheet.name}"', f'"data:image/jpeg;base64,{data}"')
    return html


page = build_page()
if '"photos/sheet_' in page:
    st.warning("Some photo files (sheet_0.jpg to sheet_8.jpg) are missing from the repository, so a few members will show initials instead of photos.")

components.html(page, height=1600, scrolling=True)
