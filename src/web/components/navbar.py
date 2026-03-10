"""
components/navbar.py  —  Horizontale Navigation
Ersetzt die vertikale Sidebar komplett.
"""
import streamlit as st

PAGES = [
    {"label": "Streaming & Ticket", "page": "pages/2_Streaming_Ticket.py", "icon": "🎟️"},
]

NAV_CSS = """
<style>
/* Sidebar komplett ausblenden */
[data-testid="stSidebar"]        { display: none !important; }
[data-testid="collapsedControl"] { display: none !important; }

/* Hauptinhalt nimmt volle Breite */
.main .block-container {
    padding-top: 0.5rem !important;
    max-width: 1400px !important;
}

/* Navbar-Wrapper */
.navbar-wrapper {
    display: flex;
    align-items: center;
    gap: 0;
    background: #0f1320;
    border-bottom: 1px solid #232840;
    padding: 0 24px;
    height: 56px;
    margin: -0.5rem -2.5rem 1.5rem -2.5rem;
    position: sticky;
    top: 0;
    z-index: 999;
}
.navbar-brand {
    font-size: 1rem;
    font-weight: 800;
    background: linear-gradient(90deg, #818cf8, #fbbf24);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    white-space: nowrap;
    cursor: pointer;
    padding: 0 20px 0 0;
    margin-right: 12px;
    border-right: 1px solid #232840;
    text-decoration: none;
    line-height: 56px;
}
.navbar-brand:hover { opacity: 0.85; }

/* page_link Items in Navbar */
div[data-testid="stHorizontalBlock"] [data-testid="stPageLink"] a {
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    height: 56px !important;
    padding: 0 16px !important;
    border-radius: 0 !important;
    border: none !important;
    background: transparent !important;
    color: #94a3b8 !important;
    font-size: 0.875rem !important;
    font-weight: 500 !important;
    white-space: nowrap;
    transition: all 0.15s ease !important;
    border-bottom: 2px solid transparent !important;
    text-decoration: none !important;
}
div[data-testid="stHorizontalBlock"] [data-testid="stPageLink"] a:hover {
    color: #f1f5f9 !important;
    background: rgba(99,102,241,0.06) !important;
    border-bottom: 2px solid #6366f1 !important;
}
div[data-testid="stHorizontalBlock"] [data-testid="stPageLink"] a[aria-current="page"] {
    color: #818cf8 !important;
    border-bottom: 2px solid #6366f1 !important;
    font-weight: 600 !important;
    background: rgba(99,102,241,0.06) !important;
}
/* About Us extra Styling (letzter Punkt) */
div[data-testid="stHorizontalBlock"] [data-testid="stPageLink"]:last-child a {
    color: #818cf8 !important;
    margin-left: 8px;
}
div[data-testid="stHorizontalBlock"] [data-testid="stPageLink"]:last-child a:hover {
    color: #a5b4fc !important;
}
</style>
"""


def render_navbar():
    """Rendert die horizontale Navbar. Ersetzt render_nav()."""
    st.markdown(NAV_CSS, unsafe_allow_html=True)

    cols = st.columns([2] + [1] * len(PAGES) + [4])
    with cols[0]:
        st.page_link("pages/1_Home.py", label="🎵 From Streams to Stages")
    for i, page in enumerate(PAGES):
        with cols[i+1]:
            st.page_link(page["page"], label=f"{page['icon']} {page['label']}")

    st.markdown('<hr style="margin: 0 0 1.5rem 0; border-color: #232840;">', unsafe_allow_html=True)
