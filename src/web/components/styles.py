"""
components/styles.py  —  Shared Design System
Import in jede Page:
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from components.styles import apply_styles
"""
import streamlit as st

COLORS = {
    "bg": "#080b14",
    "surface": "#0f1320",
    "surface2": "#161c2d",
    "surface3": "#1d2440",
    "border": "#232840",
    "border2": "#2e3557",
    "primary": "#6366f1",
    "primary_l": "#818cf8",
    "primary_d": "#4338ca",
    "accent": "#f59e0b",
    "accent_l": "#fbbf24",
    "green": "#10b981",
    "red": "#f43f5e",
    "cyan": "#22d3ee",
    "text": "#f1f5f9",
    "text_m": "#94a3b8",
    "text_d": "#475569",
}

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --bg:#080b14; --surface:#0f1320; --surface2:#161c2d; --surface3:#1d2440;
    --border:#232840; --border2:#2e3557;
    --primary:#6366f1; --primary-l:#818cf8; --primary-d:#4338ca;
    --accent:#f59e0b; --accent-l:#fbbf24;
    --green:#10b981; --red:#f43f5e; --cyan:#22d3ee;
    --text:#f1f5f9; --text-m:#94a3b8; --text-d:#475569;
    --r:10px; --r-lg:16px; --t:all 0.18s ease;
}

html, body, [data-testid="stApp"], .stApp {
    background-color: var(--bg) !important;
    font-family: 'Inter', -apple-system, sans-serif !important;
    -webkit-font-smoothing: antialiased;
    color: var(--text) !important;
}
::-webkit-scrollbar{width:5px;height:5px}
::-webkit-scrollbar-track{background:var(--bg)}
::-webkit-scrollbar-thumb{background:var(--border2);border-radius:3px}
::-webkit-scrollbar-thumb:hover{background:var(--primary-d)}

/* SIDEBAR */
[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"]>div:first-child { padding:0 !important; }
[data-testid="stSidebarNavItems"] { display:none !important; }

/* NAV BOXES — page_link items */
[data-testid="stSidebar"] [data-testid="stPageLink"] {
    display:block !important;
    margin:3px 12px !important;
}
[data-testid="stSidebar"] [data-testid="stPageLink"] a {
    display:flex !important;
    align-items:center !important;
    gap:10px !important;
    padding:10px 14px !important;
    border-radius:var(--r) !important;
    border:1px solid var(--border) !important;
    background:var(--surface2) !important;
    color:var(--text-m) !important;
    font-size:.875rem !important;
    font-weight:500 !important;
    text-decoration:none !important;
    transition:var(--t) !important;
}
[data-testid="stSidebar"] [data-testid="stPageLink"] a:hover {
    background:var(--surface3) !important;
    border-color:var(--primary-d) !important;
    color:var(--text) !important;
    transform:translateX(3px);
}
[data-testid="stSidebar"] [data-testid="stPageLink"] a[aria-current="page"] {
    background:linear-gradient(135deg,var(--primary-d),#312e81) !important;
    border-color:var(--primary) !important;
    color:#fff !important;
    font-weight:600 !important;
    box-shadow:0 0 0 1px var(--primary-d),0 4px 16px rgba(99,102,241,.35) !important;
}

/* MAIN */
.main .block-container { padding:2rem 2.5rem 4rem !important; max-width:1380px !important; }

/* TYPOGRAPHY */
h1,h2,h3,h4,h5 { font-family:'Inter',sans-serif !important; color:var(--text) !important; letter-spacing:-.02em; }
p,li,span,label,div { color:var(--text-m) !important; }
strong { color:var(--text) !important; }

/* WIDGETS */
[data-testid="stSelectbox"]>div>div,
[data-testid="stMultiSelect"]>div>div {
    background:var(--surface2) !important;
    border:1px solid var(--border2) !important;
    border-radius:var(--r) !important;
}
.stRadio label {
    background:var(--surface2) !important;
    border:1px solid var(--border) !important;
    border-radius:8px !important;
    padding:5px 13px !important;
    transition:var(--t) !important;
    color:var(--text-m) !important;
    font-size:.84rem !important;
}
.stRadio label:hover { border-color:var(--primary) !important; color:var(--text) !important; }

/* METRICS */
[data-testid="stMetric"] {
    background:var(--surface2) !important;
    border:1px solid var(--border) !important;
    border-radius:var(--r) !important;
    padding:14px 18px !important;
    transition:var(--t);
}
[data-testid="stMetric"]:hover { border-color:var(--border2) !important; transform:translateY(-1px); }
[data-testid="stMetricLabel"]>div { color:var(--text-d) !important; font-size:.72rem !important; text-transform:uppercase !important; letter-spacing:.08em !important; font-weight:600 !important; }
[data-testid="stMetricValue"]>div { color:var(--text) !important; font-size:1.5rem !important; font-weight:700 !important; }

/* HR */
hr { border:none !important; border-top:1px solid var(--border) !important; margin:2rem 0 !important; }

/* TABLES */
table { width:100%; border-collapse:collapse; background:var(--surface); border-radius:var(--r); overflow:hidden; }
thead tr { background:var(--surface2); }
th { padding:10px 14px; font-size:.72rem; text-transform:uppercase; letter-spacing:.06em; color:var(--text-d) !important; font-weight:600; border-bottom:1px solid var(--border2); text-align:left; }
td { padding:10px 14px; font-size:.85rem; color:var(--text-m) !important; border-bottom:1px solid var(--border); }
tbody tr:last-child td { border-bottom:none; }
tbody tr:hover { background:var(--surface2); }

/* ALERTS */
[data-testid="stAlert"] { background:var(--surface2) !important; border:1px solid var(--border2) !important; border-radius:var(--r) !important; }

/* EXPANDER */
[data-testid="stExpander"] { background:var(--surface2) !important; border:1px solid var(--border) !important; border-radius:var(--r) !important; }

/* CODE */
code { background:var(--surface2) !important; color:var(--primary-l) !important; padding:2px 6px !important; border-radius:4px !important; font-family:'JetBrains Mono',monospace !important; font-size:.84em !important; }

/* CUSTOM COMPONENTS */
.page-header {
    background:linear-gradient(135deg,var(--surface) 0%,var(--surface3) 100%);
    border:1px solid var(--border2); border-radius:var(--r-lg);
    padding:30px 34px; margin-bottom:26px; position:relative; overflow:hidden;
}
.page-header::before { content:''; position:absolute; top:0; left:0; width:4px; height:100%; background:linear-gradient(180deg,var(--primary),var(--accent)); }
.page-header::after  { content:''; position:absolute; top:-50px; right:-50px; width:200px; height:200px; background:radial-gradient(circle,rgba(99,102,241,.07) 0%,transparent 70%); pointer-events:none; }
.page-header h1 { color:var(--text) !important; font-size:1.7rem !important; font-weight:800 !important; margin:0 0 6px 0 !important; background:linear-gradient(90deg,var(--primary-l) 0%,var(--accent-l) 100%); -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text; }
.page-header p { color:var(--text-m) !important; margin:0 !important; font-size:.93rem !important; }

.rq-box { background:linear-gradient(135deg,#4f58b0 0%,#bbc0c9 100%); border:1px solid var(--primary-d); border-radius:var(--r); padding:16px 20px; margin-bottom:22px; }
.rq-box h3 { color:var(--primary-l) !important; margin:0 0 6px 0 !important; font-size:1.2rem !important; text-transform:uppercase !important; letter-spacing:.12em !important; font-weight:700 !important; }
.rq-box p { color:var(--text) !important; margin:0 !important; font-size:1rem !important; font-weight:500 !important; line-height:1.5 !important; }

.section-title { font-size:1.1rem !important; font-weight:700 !important; color:var(--text) !important; margin:26px 0 10px 0 !important; padding-bottom:8px !important; border-bottom:1px solid var(--border) !important; }

.insight-card { background:var(--surface2); border:1px solid var(--border); border-radius:var(--r); padding:14px 18px; margin-bottom:10px; border-left:3px solid var(--primary); transition:var(--t); }
.insight-card:hover { border-color:var(--border2); }
.insight-card h4 { color:var(--primary-l) !important; margin:0 0 6px 0 !important; font-size:.7rem !important; text-transform:uppercase !important; letter-spacing:.08em !important; font-weight:700 !important; }
.insight-card p { color:var(--text-m) !important; margin:0 !important; font-size:.88rem !important; line-height:1.65 !important; }

.methodology-note { background:var(--surface); border:1px solid var(--border); border-radius:var(--r); padding:12px 16px; margin-top:12px; }
.methodology-note p { color:var(--text-d) !important; font-size:.79rem !important; margin:0 !important; font-style:italic; line-height:1.6 !important; }
"""


def apply_styles():
    st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)

    # rgb(141 92 168);
