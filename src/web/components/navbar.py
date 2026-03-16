"""
components/navbar.py  —  Horizontale Navigation
Ersetzt die vertikale Sidebar komplett.
"""
import streamlit as st

PAGES = [
    {"label": "Streaming & Ticket Power", "page": "pages/2_Streaming_Ticket.py", "icon": "🎟️"},
    {"label": "Geographic Analysis", "page": "pages/3_Geographic.py", "icon": "🗺️"},
    {"label": "Market Time & Scheduling", "page": "pages/4_Scheduling.py", "icon": "📅"},
    {"label": "Glossar", "page": "pages/5_Glossar.py", "icon": "📖"},
    {"label": "About Us", "page": "pages/6_About.py", "icon": "👥"},
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
    height: 72px;
    margin: -0.5rem -2.5rem 2rem -2.5rem;
    position: sticky;
    top: 0;
    z-index: 999;
}

.navbar-brand {
    font-size: 1.2rem;
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
    line-height: 72px;
}
.navbar-brand:hover { opacity: 0.85; }

/* page_link Items in Navbar */
div[data-testid="stHorizontalBlock"] [data-testid="stPageLink"] a {
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    height: 72px !important;
    padding: 10px 20px !important;
    border-radius: 0 !important;
    border: none !important;
    background: transparent !important;
    color: #94a3b8 !important;
    font-size: 1.6rem !important;
    font-weight: 800 !important;
    white-space: nowrap !important;
    transition: all 0.15s ease !important;
    border-bottom: 2px solid transparent !important;
    text-decoration: none !important;
}

/* Erzwinge fett auf alle inneren Elemente */
div[data-testid="stHorizontalBlock"] [data-testid="stPageLink"] a p,
div[data-testid="stHorizontalBlock"] [data-testid="stPageLink"] a span,
div[data-testid="stHorizontalBlock"] [data-testid="stPageLink"] p {
    font-weight: 800 !important;
    font-size: 1.6rem !important;
}

div[data-testid="stHorizontalBlock"] [data-testid="stPageLink"] a:hover {
    color: #f1f5f9 !important;
    background: rgba(99,102,241,0.06) !important;
    border-bottom: 2px solid #6366f1 !important;
}

div[data-testid="stHorizontalBlock"] [data-testid="stPageLink"] a[aria-current="page"] {
    color: #818cf8 !important;
    border-bottom: 2px solid #6366f1 !important;
    font-weight: 800 !important;
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

/* Navbar Items volle Breite verteilen */
div[data-testid="stHorizontalBlock"] {
    gap: 0 !important;
    width: 100% !important;
}

div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] {
    flex: 1 1 auto !important;
    min-width: fit-content !important;
}
</style>
"""

def render_navbar():
    """Rendert die horizontale Navbar. Ersetzt render_nav()."""
    st.markdown(NAV_CSS, unsafe_allow_html=True)

    st.markdown("""
    <div class="navbar-wrapper">
        <a class="navbar-brand" href="/">&#127925; From Streams to Stages</a>
    </div>
    """, unsafe_allow_html=True)

    nav_container = st.container()
    with nav_container:
        cols = st.columns([2, 2, 2, 1, 1, 3])
        for i, page in enumerate(PAGES):
            with cols[i]:
                st.page_link(page["page"], label=f"{page['icon']} {page['label']}")

    st.markdown('<hr style="margin: 0 0 1.5rem 0; border-color: #232840;">', unsafe_allow_html=True)
