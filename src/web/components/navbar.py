"""
components/navbar.py  —  Horizontale Navigation
Ersetzt die vertikale Sidebar komplett.
"""
import streamlit as st

PAGES = [
    {"label": "Home", "page": "pages/1_Home.py", "icon": "🏠"},
    {"label": "Streaming & Ticket Power", "page": "pages/2_Streaming_Ticket.py", "icon": "🎟️"},
    {"label": "Geographic Analysis", "page": "pages/3_Geographic.py", "icon": "🗺️"},
    {"label": "Market Time & Scheduling", "page": "pages/4_Scheduling.py", "icon": "📅"},
    {"label": "Data", "page": "pages/7_Data.py", "icon": "🗄️"},
    {"label": "Glossary", "page": "pages/5_Glossar.py", "icon": "📖"},
    {"label": "About Us", "page": "pages/6_About.py", "icon": "👥"},
]

NAV_CSS = """
<style>
[data-testid="stSidebar"]        { display: none !important; }
[data-testid="collapsedControl"] { display: none !important; }

.main .block-container {
    padding-top: 0.5rem !important;
    max-width: 1600px !important;
}

/* Große Überschrift oben */
.brand-header {
    margin: -0.5rem -2.5rem 0rem -2.5rem;
    padding: 26px 24px 16px 24px;
    background: transparent;
    border-bottom: none;
}

.brand-row {
    display: flex;
    align-items: center;
    gap: 16px;
}

.brand-icon {
    font-size: 3rem !important;
    line-height: 1 !important;
    flex-shrink: 0;
}

.brand-title {
    font-size: 3.6rem !important;
    font-weight: 800 !important;
    line-height: 1.05 !important;
    letter-spacing: -0.02em !important;
    white-space: nowrap !important;
    background: linear-gradient(90deg, #818cf8 0%, #fbbf24 100%) !important;
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    background-clip: text !important;
    color: transparent !important;
}

/* Navigation darunter */
.navbar-wrapper {
    display: flex;
    align-items: center;
    gap: 0;
    background: transparent;
    border-bottom: 1px solid #232840;
    padding: 0 24px;
    height: 56px;
    margin: 0rem -2.5rem 2rem -2.5rem;
    position: sticky;
    top: 0;
    z-index: 999;
}

/* Standard-Styling für die Nav-Zeile */
div[data-testid="stHorizontalBlock"] [data-testid="stPageLink"] a {
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    height: 56px !important;
    padding: 10px 12px !important;
    border-radius: 0 !important;
    border: none !important;
    background: transparent !important;
    color: #94a3b8 !important;
    font-size: 1rem !important;
    font-weight: 500 !important;
    white-space: nowrap !important;
    transition: all 0.15s ease !important;
    border-bottom: 2px solid transparent !important;
    text-decoration: none !important;
    box-shadow: none !important;
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
</style>
"""

def render_navbar():
    st.markdown(NAV_CSS, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="brand-header">
        <div class="brand-row">
            <span class="brand-icon">🎵</span>
            <span class="brand-title">From Streams to Stages</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="navbar-wrapper">', unsafe_allow_html=True)

    cols = st.columns([1.1, 2.3, 1.9, 2.5, 1.3, 1.3, 1.0], gap="small")
    for i, page in enumerate(PAGES):
        with cols[i]:
            st.page_link(page["page"], label=f"{page['icon']} {page['label']}")

    st.markdown('</div>', unsafe_allow_html=True)
