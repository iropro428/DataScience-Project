import streamlit as st

from components.styles import apply_styles
from components.navbar import render_navbar
from components.glossary import apply_glossary_styles, tt, glossar_seite, TERMS

apply_glossary_styles()  # einmal pro Page aufrufen


st.set_page_config(
    page_title="Glossar",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="expanded",
)
apply_styles()
render_navbar()

st.markdown("""
<div class="page-header">
    <h1>📖 Glossary</h1>
    <p>All technical terms explained simply — no data science degree required</p>
</div>
""", unsafe_allow_html=True)

suche = st.text_input("🔍 Search term...", placeholder="e.g. p-value, Pearson, Median...")

if suche.strip():
    treffer = {t: v for t, v in TERMS.items()
               if suche.lower() in t.lower() or suche.lower() in v["kurz"].lower()}
    if treffer:
        st.markdown("**" + str(len(treffer)) + " results for: " + suche + "**")
        for term, t in treffer.items():
            with st.expander(t["emoji"] + " **" + term + "** — *" + t["kurz"] + "*", expanded=True):
                st.markdown(t["lang"])
    else:
        st.warning("No results for: " + suche)
    st.divider()

glossar_seite()
