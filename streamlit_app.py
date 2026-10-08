"""Punjab Lawyers Directory - Justice Dashboard (Streamlit).

Login and data
--------------
Put these in the app's secrets (Streamlit Cloud: Manage app -> Settings -> Secrets):

    [passwords]                  # who can open the dashboard
    shahzaib = "choose-a-strong-password"

    [supabase]                   # optional: read the data from Supabase
    url = "https://YOUR-PROJECT-ID.supabase.co"
    key = "YOUR-SECRET-KEY"      # secret / service_role key (stays on the server)
    table = "lawyers"            # optional

Without [supabase], the data comes from lawyers.csv.

Photos
------
Member photos come from 9 image sheets (sheet_0.jpg ... sheet_8.jpg), each a
40-column grid of 72x72 px photos. photo_sheet and photo_pos say where each
lawyer's photo sits (-1 means no photo). A photo_url column, if present and
filled, is used instead.
"""
from __future__ import annotations

import base64
import hmac
import html
import io
import math
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from PIL import Image

# Lock the light theme so the dashboard looks the same in every browser,
# including ones set to dark mode, even if .streamlit/config.toml is missing.
from streamlit import config as _stconfig

_THEME = {
    "theme.base": "light",
    "theme.primaryColor": "#1B2A6B",
    "theme.backgroundColor": "#F4F6FB",
    "theme.secondaryBackgroundColor": "#FFFFFF",
    "theme.textColor": "#141B33",
}
if any(_stconfig.get_option(k) != v for k, v in _THEME.items()):
    for _k, _v in _THEME.items():
        _stconfig.set_option(_k, _v)
    st.rerun()

HERE = Path(__file__).parent
CSV_PATH = HERE / "lawyers.csv"
SHEET_COLS = 40
PHOTO_PX = 72

# Colours (checked for colour-blind readers against a white background).
NAVY = "#1B2A6B"   # brand navy: header block, selected controls
GOLD = "#F0B429"   # brand gold: highlights
BG, LINE = "#F4F6FB", "#E1E6F0"
S1, S2, S3 = "#3A57B8", "#D4980F", "#23A08C"
INK, MUTED, GRID = "#141B33", "#7A839E", "#E6EAF3"

st.set_page_config(
    page_title="Punjab Lawyers Dashboard",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --------------------------------------------------------------------------
# Styling
# --------------------------------------------------------------------------
st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Libre+Caslon+Text:wght@700&family=Public+Sans:wght@400;600;700&display=swap');
    .stApp, .stMarkdown p, .stMarkdown li {{ font-family: 'Public Sans', sans-serif; }}
    .stMarkdown h1, .stMarkdown h1 *, .stMarkdown h3, .stMarkdown h3 * {{ font-family: 'Libre Caslon Text', Georgia, serif !important; color:{INK}; }}
    .stMarkdown h1 {{ font-size: 2.1rem !important; padding-bottom: .2rem !important; }}
    .stMarkdown h3 {{ font-size: 1.12rem !important; padding: .1rem 0 .5rem !important; }}
    .block-container {{ padding-top: 1.6rem; padding-bottom: 3rem; max-width: 1400px; }}
    .stApp {{ background:{BG}; }}
    [data-testid="stHeader"] {{ background:transparent; }}

    /* sidebar: white panel, navy brand block */
    [data-testid="stSidebar"] {{ background:#FFFFFF; border-right:1px solid {LINE}; }}
    [data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {{ color:{INK}; font-weight:600; font-size:13px; }}
    [data-testid="stSidebar"] label[data-baseweb="radio"] p {{ color:#4A5372; }}
    [data-testid="stSidebar"] [data-testid="stCaptionContainer"] p {{ color:{MUTED}; }}
    .brand {{ display:flex; gap:12px; align-items:center; background:{NAVY}; border-radius:14px;
             padding:14px; margin:0 0 10px; box-shadow:0 6px 18px rgba(27,42,107,.25); }}
    .brand .logo {{ width:42px; height:42px; border-radius:10px; background:{GOLD};
                   display:grid; place-items:center; font-size:22px; flex:0 0 42px; }}
    .brand b {{ display:block; color:#FFFFFF; font-family:'Libre Caslon Text',serif; font-size:18px; line-height:1.15; }}
    .brand span {{ color:#C9D0EA; font-size:12.5px; }}

    /* controls in brand navy, whether or not the theme file is present */
    [data-testid="stRadioOption"][data-selected="true"] > div > div:first-child {{ background-color:{NAVY} !important; border-color:{NAVY} !important; }}
    [data-testid="stMultiSelect"] span[data-tag] {{ background-color:{NAVY} !important; color:#FFFFFF !important; }}
    [data-focus-within="true"][role="group"], [data-testid="stTextInput"] [data-focus-within="true"],
    [data-testid="stNumberInput"] [data-focus-within="true"] {{ border-color:{NAVY} !important; }}
    [data-testid="stTab"][aria-selected="true"], [data-testid="stTab"][aria-selected="true"] p {{ color:{NAVY} !important; font-weight:700; }}
    .react-aria-SelectionIndicator {{ background-color:{GOLD} !important; }}
    label[data-selected="true"]:has(input[role="switch"]) > div:first-of-type {{ background-color:{NAVY} !important; }}

    /* panels */
    [data-testid="stVerticalBlockBorderWrapper"]:has(> div > [data-testid="stVerticalBlock"]) {{ background:#FFFFFF; }}
    [data-testid="stVerticalBlockBorderWrapper"] {{ border-radius:14px; border-color:{LINE} !important; }}
    .kpi {{ background:#fff; border-radius:14px; padding:16px 18px; border:1px solid {LINE}; border-top:3px solid {GOLD};
           box-shadow:0 1px 2px rgba(20,27,51,.06),0 4px 16px rgba(20,27,51,.06); height:100%; }}
    .kpi .h {{ color:#4A5372; font-size:13px; font-weight:600; }}
    .kpi .v {{ color:{INK}; font-size:30px; font-weight:700; line-height:1.15; margin:4px 0 6px; }}
    .kpi .d {{ color:{MUTED}; font-size:12.5px; }}
    .kpi .m {{ height:6px; background:{GRID}; border-radius:3px; overflow:hidden; margin:2px 0 6px; }}
    .kpi .m i {{ display:block; height:100%; background:{NAVY}; border-radius:3px; }}
    .stMarkdown p.sub, .sub {{ color:{MUTED}; font-size:13px !important; margin:-6px 0 6px; line-height:1.4; }}
    .cards {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(160px,1fr)); gap:14px; }}
    .card {{ background:#FFFFFF; border:1px solid {LINE}; border-radius:12px; padding:12px; text-align:center; }}
    .card .ph {{ width:92px; height:92px; border-radius:50%; margin:4px auto 10px; border:3px solid #fff;
                box-shadow:0 0 0 2px {GOLD}; background:{GRID}; object-fit:cover; display:block; }}
    .card .ini {{ display:flex; align-items:center; justify-content:center; font-family:'Libre Caslon Text',serif;
                 font-size:26px; color:{MUTED}; }}
    .card .n {{ font-weight:700; font-size:13.5px; line-height:1.3; color:{INK}; }}
    .card .p, .card .s {{ font-size:12px; color:{MUTED}; }}
    .tag {{ display:inline-block; margin-top:6px; font-size:12px; padding:2px 8px; border-radius:999px;
           background:#FFF4D6; color:#7A5600; font-weight:600; }}
    .tag.o {{ background:#EEF0F5; color:#4A5372; font-weight:400; }}
    </style>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------------------------------
# Data
# --------------------------------------------------------------------------
def _secret_section(name: str) -> dict | None:
    try:
        return dict(st.secrets[name])
    except Exception:
        return None


SUPABASE = _secret_section("supabase")    # url + key  -> data comes from Supabase
PASSWORDS = _secret_section("passwords")  # username = "password" lines -> who can open the dashboard


# --------------------------------------------------------------------------
# Login
# --------------------------------------------------------------------------
def login_screen() -> None:
    st.markdown(
        "<style>[data-testid='stSidebar'],[data-testid='stSidebarCollapsedControl']{display:none}"
        ".block-container{max-width:460px;padding-top:9vh}</style>",
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="brand"><div class="logo">⚖️</div><div><b>Justice Dashboard</b>'
        "<span>Punjab lawyers directory · sign in to continue</span></div></div>",
        unsafe_allow_html=True,
    )
    if not PASSWORDS:
        st.error("Login isn't set up yet. Add a [passwords] section to the app's secrets "
                 "(Manage app → Settings → Secrets). See README.md for the exact text.")
        st.stop()
    with st.form("login"):
        user = st.text_input("Username")
        pw = st.text_input("Password", type="password")
        ok = st.form_submit_button("Sign in", type="primary", use_container_width=True)
    if ok:
        expected = PASSWORDS.get(user.strip())
        if expected is not None and hmac.compare_digest(str(expected), pw):
            st.session_state.auth = {"user": user.strip()}
            st.rerun()
        else:
            st.error("Username or password is incorrect.")


if "auth" not in st.session_state:
    login_screen()
    st.stop()


# --------------------------------------------------------------------------
# Data
# --------------------------------------------------------------------------
@st.cache_data(ttl=600, show_spinner="Loading lawyers from Supabase…")
def load_supabase(url: str, key: str, table: str) -> pd.DataFrame:
    from supabase import create_client

    client = create_client(url, key)
    rows, start, step = [], 0, 1000  # Supabase returns at most 1,000 rows per request
    while True:
        batch = client.table(table).select("*").order("id").range(start, start + step - 1).execute().data
        rows.extend(batch)
        if len(batch) < step:
            break
        start += step
    return pd.DataFrame(rows)


@st.cache_data(show_spinner="Loading lawyers…")
def load_csv() -> pd.DataFrame:
    return pd.read_csv(CSV_PATH, dtype={"office_address": str, "parentage": str})


def prepare(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["parentage"] = df["parentage"].fillna("")
    df["office_address"] = df["office_address"].fillna("")
    df["life_member"] = df["life_member"].astype(str).str.lower().isin(["true", "1", "yes", "t"])
    df["photo_sheet"] = pd.to_numeric(df.get("photo_sheet"), errors="coerce").fillna(-1).astype(int)
    df["photo_pos"] = pd.to_numeric(df.get("photo_pos"), errors="coerce").fillna(-1).astype(int)
    if "photo_url" not in df:
        df["photo_url"] = None
    df["has_photo"] = (df["photo_sheet"] >= 0) | df["photo_url"].fillna("").astype(str).str.len().gt(0)
    df["sort_name"] = df["name"].str.replace(r"^(Mr|Ms|Mrs|Mst|Dr|Miss)\.\s*", "", regex=True)
    df.loc[df["sort_name"].str.startswith("("), "sort_name"] = "~"  # unnamed card goes last
    return df


if SUPABASE:
    try:
        raw = load_supabase(SUPABASE["url"], SUPABASE["key"], SUPABASE.get("table", "lawyers"))
    except Exception as exc:
        st.error(f"Couldn't read the lawyers table from Supabase. Check the url and key in Secrets. Details: {exc}")
        st.stop()
    if raw.empty:
        st.error("Supabase returned no rows. Import lawyers.csv into the lawyers table, and make sure the key in "
                 "Secrets is the secret (service_role) key, not the anon/publishable key.")
        st.stop()
    source = "Supabase"
else:
    raw, source = load_csv(), "lawyers.csv"
df = prepare(raw)


@st.cache_resource
def load_sheet(k: int) -> Image.Image | None:
    path = HERE / f"sheet_{k}.jpg"
    if not path.exists():
        path = HERE / "photos" / f"sheet_{k}.jpg"
    return Image.open(path).convert("RGB") if path.exists() else None


@st.cache_data(max_entries=5000)
def photo_data_uri(sheet: int, pos: int) -> str | None:
    if sheet < 0 or pos < 0:
        return None
    img = load_sheet(sheet)
    if img is None:
        return None
    col, row = pos % SHEET_COLS, pos // SHEET_COLS
    crop = img.crop((col * PHOTO_PX, row * PHOTO_PX, (col + 1) * PHOTO_PX, (row + 1) * PHOTO_PX))
    buf = io.BytesIO()
    crop.save(buf, "JPEG", quality=88)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()

# --------------------------------------------------------------------------
# Sidebar filters
# --------------------------------------------------------------------------
with st.sidebar:
    st.markdown(
        '<div class="brand"><div class="logo">⚖️</div><div><b>Justice Dashboard</b>'
        "<span>LHCBA voter roll 2022–23</span></div></div>",
        unsafe_allow_html=True,
    )
    station_order = df["station"].value_counts().index.tolist()
    stations = st.multiselect("Bar station", station_order, placeholder="All stations")
    membership = st.radio("Membership", ["All", "Life", "Ordinary"], horizontal=True)
    gender = st.radio("Gender", ["All", "Male", "Female"], horizontal=True)
    chambers = st.radio("Chambers", ["All", "Local courts", "Lahore", "Not listed"], horizontal=True)
    photo = st.radio("Photo", ["All", "With photo", "Without"], horizontal=True)
    st.caption(f"Data source: {source}. Phone numbers and home addresses are not included.")
    st.divider()
    st.caption(f"Signed in as {st.session_state.auth['user']}")
    if st.button("Sign out", use_container_width=True):
        del st.session_state["auth"]
        st.rerun()

f = df
if stations:
    f = f[f["station"].isin(stations)]
if membership != "All":
    f = f[f["life_member"] == (membership == "Life")]
if gender != "All":
    f = f[f["gender"] == gender]
if chambers != "All":
    f = f[f["chambers"] == chambers]
if photo != "All":
    f = f[f["has_photo"] == (photo == "With photo")]

n = len(f)


def pct(a: int, b: int) -> str:
    return f"{a / b:.0%}" if b else "–"


# --------------------------------------------------------------------------
# Header + KPIs
# --------------------------------------------------------------------------
st.markdown("# Punjab Lawyers Directory")
n_st = f["station"].nunique()
st.markdown(
    f'<p class="sub">{n:,} lawyers across {n_st} bar station{"s" if n_st != 1 else ""}'
    f'{" in Punjab, Lahore included" if n == len(df) else ""}</p>',
    unsafe_allow_html=True,
)

life, women, with_photo = int(f["life_member"].sum()), int((f["gender"] == "Female").sum()), int(f["has_photo"].sum())


def kpi(col, head, value, detail, meter=None):
    m = f'<div class="m"><i style="width:{meter:.1f}%"></i></div>' if meter is not None else ""
    col.markdown(
        f'<div class="kpi"><div class="h">{head}</div><div class="v">{value}</div>{m}<div class="d">{detail}</div></div>',
        unsafe_allow_html=True,
    )


k = st.columns(5)
kpi(k[0], "👥 Lawyers", f"{n:,}", "on the voter roll" if not stations else "in selected stations")
kpi(k[1], "🎖️ Life members", pct(life, n), f"{life:,} of {n:,}", life / n * 100 if n else 0)
kpi(k[2], "👩‍⚖️ Women", pct(women, n), f"{women:,} women lawyers", women / n * 100 if n else 0)
kpi(k[3], "🏛️ Bar stations", f"{n_st}", f"of {df['station'].nunique()} on the roll")
kpi(k[4], "📷 With photo", pct(with_photo, n), f"{with_photo:,} cards have a photo", with_photo / n * 100 if n else 0)
st.write("")

if n == 0:
    st.info("No lawyers match these filters. Change or clear a filter in the sidebar.")
    st.stop()


# --------------------------------------------------------------------------
# Charts
# --------------------------------------------------------------------------
def style(fig: go.Figure, height: int) -> go.Figure:
    fig.update_layout(
        height=height,
        margin=dict(l=8, r=8, t=8, b=8),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Public Sans, sans-serif", color="#4A5372", size=12),
        hoverlabel=dict(bgcolor=INK, font_color="#fff", bordercolor=INK),
        showlegend=False,
    )
    return fig


def donut(values: dict[str, int], colors: list[str], center: str) -> go.Figure:
    labels, counts = list(values), list(values.values())
    fig = go.Figure(
        go.Pie(
            labels=labels, values=counts, hole=0.64, sort=False, direction="clockwise",
            marker=dict(colors=colors, line=dict(color="#fff", width=2)),
            textinfo="none",
            hovertemplate="<b>%{label}</b><br>%{value:,} lawyers (%{percent})<extra></extra>",
        )
    )
    fig.add_annotation(text=f"<b>{center}</b><br><span style='font-size:11px;color:{MUTED}'>lawyers</span>",
                       showarrow=False, font=dict(size=20, color=INK))
    fig.update_traces(domain=dict(x=[0, 0.56], y=[0, 1]))
    fig.update_annotations(x=0.28, xref="paper", y=0.5, yref="paper", xanchor="center", yanchor="middle")
    style(fig, 200)
    fig.update_layout(showlegend=True, legend=dict(orientation="v", x=0.62, y=0.5, yanchor="middle", font=dict(size=13, color=INK)))
    return fig


c1, c2 = st.columns([1.7, 1])
with c1:
    with st.container(border=True):
        st.markdown("### Lawyers by bar station")
        st.markdown('<p class="sub">Hover for life-membership share. Use the sidebar to filter by station.</p>',
                    unsafe_allow_html=True)
        by_st = (f.groupby("station").agg(lawyers=("name", "size"), life=("life_member", "mean"))
                 .sort_values("lawyers", ascending=False))
        show_all = st.toggle(f"Show all {len(by_st)} stations", value=False) if len(by_st) > 12 else True
        top = by_st if show_all else by_st.head(12)
        top = top.iloc[::-1]
        fig = go.Figure(go.Bar(
            x=top["lawyers"], y=top.index, orientation="h", marker=dict(color=S1, cornerradius=4),
            text=[f"{v:,}" for v in top["lawyers"]], textposition="outside", cliponaxis=False,
            customdata=top["life"], hovertemplate="<b>%{y}</b><br>%{x:,} lawyers<br>%{customdata:.0%} life members<extra></extra>",
        ))
        fig.update_xaxes(range=[0, top["lawyers"].max() * 1.14], showgrid=False, zeroline=False, showticklabels=False)
        fig.update_yaxes(showgrid=False, tickfont=dict(size=12.5, color=INK))
        fig.update_traces(width=0.7)
        st.plotly_chart(style(fig, max(110, 28 * len(top) + 30)), use_container_width=True, config={"displayModeBar": False})

with c2:
    with st.container(border=True):
        st.markdown("### Membership type")
        st.plotly_chart(donut({"Life members": life, "Ordinary": n - life}, [S1, S2], f"{n:,}"),
                        use_container_width=True, config={"displayModeBar": False})
        st.markdown("### Gender")
        st.plotly_chart(donut({"Men": n - women, "Women": women}, [S1, S2], f"{n:,}"),
                        use_container_width=True, config={"displayModeBar": False})

c3, c4, c5 = st.columns(3)
with c3:
    with st.container(border=True):
        st.markdown("### Where they keep chambers")
        st.markdown('<p class="sub">Office address on the voter card.</p>', unsafe_allow_html=True)
        ch = f["chambers"].value_counts()
        st.plotly_chart(
            donut({k: int(ch.get(k, 0)) for k in ["Local courts", "Lahore", "Not listed"]}, [S1, S2, S3], f"{n:,}"),
            use_container_width=True, config={"displayModeBar": False},
        )
with c4:
    with st.container(border=True):
        st.markdown("### When they joined")
        st.markdown('<p class="sub">By membership number; lower joined earlier.</p>', unsafe_allow_html=True)
        bins = [0, 10_000, 20_000, 30_000, 40_000, math.inf]
        labels = ["Under 10k", "10k–20k", "20k–30k", "30k–40k", "40k+"]
        era = pd.cut(f["membership_no"], bins=bins, labels=labels, right=False).value_counts().reindex(labels)
        fig = go.Figure(go.Bar(
            x=labels, y=era.values, marker=dict(color=S1, cornerradius=4),
            text=[f"{v:,}" for v in era.values], textposition="outside", cliponaxis=False,
            hovertemplate="<b>Membership no. %{x}</b><br>%{y:,} lawyers<extra></extra>",
        ))
        fig.update_yaxes(showgrid=True, gridcolor=GRID, showticklabels=False, zeroline=False)
        st.plotly_chart(style(fig, 220), use_container_width=True, config={"displayModeBar": False})
with c5:
    with st.container(border=True):
        st.markdown("### Directory coverage")
        st.markdown('<p class="sub">How complete the printed cards are.</p>', unsafe_allow_html=True)
        cov = pd.Series({
            "Photo on card": f["has_photo"].mean(),
            "Office address": (f["chambers"] != "Not listed").mean(),
            "Parentage printed": (~f["parentage"].str.fullmatch(r"(S/o|D/o, W/o)?\s*\.?\s*")).mean(),
            "Life membership": f["life_member"].mean(),
        }).iloc[::-1]
        fig = go.Figure(go.Bar(
            x=cov.values, y=cov.index, orientation="h", marker=dict(color=S1, cornerradius=4),
            text=[f"{v:.0%}" for v in cov.values], textposition="outside", cliponaxis=False,
            hovertemplate="<b>%{y}</b><br>%{x:.0%}<extra></extra>",
        ))
        fig.update_xaxes(range=[0, 1.15], showgrid=False, showticklabels=False, zeroline=False)
        st.plotly_chart(style(fig, 220), use_container_width=True, config={"displayModeBar": False})

# --------------------------------------------------------------------------
# Station scorecard
# --------------------------------------------------------------------------
with st.container(border=True):
    st.markdown("### Station scorecard")
    st.markdown('<p class="sub">Every station side by side. Select a column heading to sort.</p>', unsafe_allow_html=True)
    sc = f.groupby("station").agg(
        lawyers=("name", "size"),
        life=("life_member", "mean"),
        women=("gender", lambda s: (s == "Female").mean()),
        lahore=("chambers", lambda s: (s == "Lahore").mean()),
        photo=("has_photo", "mean"),
    ).sort_values("lawyers", ascending=False)
    sc.loc[sc.index == "Lahore", "lahore"] = None  # Lahore is their home station
    sc[["life", "women", "lahore", "photo"]] *= 100
    pc = lambda label: st.column_config.ProgressColumn(label, format="%.0f%%", min_value=0, max_value=100)
    st.dataframe(
        sc.reset_index(),
        hide_index=True,
        use_container_width=True,
        height=min(460, 38 + 35 * len(sc)),
        column_config={
            "station": st.column_config.TextColumn("Station"),
            "lawyers": st.column_config.NumberColumn("Lawyers", format="localized"),
            "life": pc("Life members"),
            "women": pc("Women"),
            "lahore": pc("Lahore chambers"),
            "photo": pc("With photo"),
        },
    )

# --------------------------------------------------------------------------
# Member directory
# --------------------------------------------------------------------------
with st.container(border=True):
    st.markdown("### Member directory")
    q = st.text_input("Search", placeholder="Search by name, parentage, office or vote number", label_visibility="collapsed")
    d = f
    if q.strip():
        hay = d["name"] + " " + d["parentage"] + " " + d["office_address"] + " " + d["vote_no"].astype(str)
        d = d[hay.str.contains(q.strip(), case=False, regex=False)]
    d = d.sort_values(["sort_name", "vote_no"])
    st.markdown(f'<p class="sub">{len(d):,} lawyers match the current filters{" and search" if q.strip() else ""}.</p>',
                unsafe_allow_html=True)

    tab_cards, tab_table = st.tabs(["Photo cards", "Table"])
    with tab_cards:
        per_page = 36
        pages = max(1, math.ceil(len(d) / per_page))
        page = st.number_input(f"Page (1–{pages})", min_value=1, max_value=pages, value=1, step=1) if pages > 1 else 1
        chunk = d.iloc[(page - 1) * per_page: page * per_page]

        def card(r) -> str:
            name = html.escape(str(r["name"]))
            uri = r["photo_url"] if isinstance(r["photo_url"], str) and r["photo_url"] else None
            if uri is None and r["photo_sheet"] >= 0:
                uri = photo_data_uri(int(r["photo_sheet"]), int(r["photo_pos"]))
            if uri:
                pic = f'<img class="ph" src="{html.escape(uri)}" alt="Photo of {name}">'
            else:
                ini = "".join(w[0] for w in str(r["name"]).split(". ", 1)[-1].replace("(", "").split()[:2])
                pic = f'<div class="ph ini">{html.escape(ini)}</div>'
            tag = '<span class="tag">Life member</span>' if r["life_member"] else '<span class="tag o">Ordinary</span>'
            return (f'<div class="card">{pic}<div class="n">{name}</div><div class="p">{html.escape(r["parentage"])}</div>'
                    f'<div class="s">{html.escape(r["station"])} · Vote no. {int(r["vote_no"])}</div>{tag}</div>')

        if len(chunk):
            st.markdown('<div class="cards">' + "".join(card(r) for _, r in chunk.iterrows()) + "</div>",
                        unsafe_allow_html=True)
            st.caption(f"Showing {(page - 1) * per_page + 1:,}–{(page - 1) * per_page + len(chunk):,} of {len(d):,}")
        else:
            st.info("No lawyers match. Clear the search or a filter to see more.")

    with tab_table:
        table = d[["name", "parentage", "station", "vote_no", "membership_no", "life_member", "gender", "chambers", "office_address"]]
        st.dataframe(
            table, hide_index=True, use_container_width=True, height=480,
            column_config={
                "name": "Name", "parentage": "Parentage", "station": "Station",
                "vote_no": st.column_config.NumberColumn("Vote no.", format="%d"),
                "membership_no": st.column_config.NumberColumn("Membership no.", format="%d"),
                "life_member": st.column_config.CheckboxColumn("Life member"),
                "gender": "Gender", "chambers": "Chambers", "office_address": "Office address",
            },
        )
        st.download_button("Download these rows as CSV", table.to_csv(index=False).encode("utf-8"),
                           file_name="lawyers_filtered.csv", mime="text/csv")

st.caption(
    'Source: Lahore High Court Bar Association voter lists 2022–23. Women are counted from the "D/o, W/o" field and '
    "Ms./Mrs./Mst./Miss titles as printed. \"Lahore\" chambers counts outstation members with a Lahore office address."
)
