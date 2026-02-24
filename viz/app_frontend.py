"""
Streamlit Frontend for IAR Platform API
"""
import streamlit as st
import pandas as pd
import requests
import json
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from viz.charts import (
    create_top_communes_chart,
    create_scatter_plot,
    create_departmental_ranking_chart,
    create_regional_comparison_chart,
    create_price_distribution_chart,
    create_regional_analysis_chart,
    create_correlation_heatmap,
    create_commune_scorecard
)

# Configuration
API_URL = "http://localhost:8000"

# Page configuration
st.set_page_config(
    page_title="IAR Platform - Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

def local_css():
    st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(to bottom right, #0e1117, #131720);
    }
    .stMetric {
        background-color: #262730;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #363945;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    div[data-testid="stExpander"] {
        background-color: #262730;
        border-radius: 10px;
    }
    h1 {
        background: -webkit-linear-gradient(45deg, #00CC96, #3366FF);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800 !important;
    }
    .highlight {
        color: #00CC96;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# Session State Initialization
if 'token' not in st.session_state:
    st.session_state.token = None
if 'user' not in st.session_state:
    st.session_state.user = None

def api_request(method, endpoint, params=None, data=None):
    """Make an API request and return response object"""
    headers = {}
    if st.session_state.token:
        headers["Authorization"] = f"Bearer {st.session_state.token}"
    
    url = f"{API_URL}{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url, params=params, headers=headers)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers)
        return response
    except requests.exceptions.ConnectionError:
        st.error("Impossible de se connecter à l'API. Vérifiez qu'elle est bien lancée sur http://localhost:8000")
        return None

def login():
    """Handle login"""
    st.sidebar.header("Authentification")
    
    if st.session_state.token:
        st.sidebar.success(f"Connecté en tant que **{st.session_state.user}**")
        if st.sidebar.button("Déconnexion"):
            st.session_state.token = None
            st.session_state.user = None
            st.rerun()
    else:
        username = st.sidebar.text_input("Utilisateur", value="admin")
        password = st.sidebar.text_input("Mot de passe", type="password", value="admin123")
        
        if st.sidebar.button("Se connecter"):
            # Note: The API expects form data usually for OAuth2, but let's check the docs provided in conversation
            # The docs say: POST /auth/login with JSON body
            response = requests.post(f"{API_URL}/auth/login", json={"username": username, "password": password})
            
            if response.status_code == 200:
                data = response.json()
                st.session_state.token = data.get("access_token")
                st.session_state.user = username
                st.success("Connexion réussie !")
                st.rerun()
            else:
                st.sidebar.error(f"Erreur: {response.status_code}")
                # Display raw error for debugging
                with st.sidebar.expander("Détails de l'erreur"):
                    st.json(response.json())

def display_raw_json(response, title="Réponse API (JSON)"):
    """Helper to display raw JSON from response"""
    if response is not None:
        with st.expander(title):
            st.markdown(f"**Status Code:** `{response.status_code}`")
            st.markdown(f"**URL:** `{response.url}`")
            try:
                st.json(response.json())
            except:
                st.text(response.text)

def main():
    local_css() # Apply custom CSS
    
    st.title("IAR Platform - Analytics Dashboard")
    st.markdown("""
    <div style='background-color: #262730; padding: 10px; border-radius: 5px; border-left: 5px solid #00CC96;'>
    Bienvenue sur la plateforme d'analyse d'attractivité territoriale.
    Cette interface explore les données <b>DVF</b> et <b>BPE</b> via l'API REST.
    </div>
    """, unsafe_allow_html=True)
    
    # Login Sidebar
    login()
    
    # Check API Health
    with st.sidebar:
        st.divider()
        try:
            health_response = requests.get(f"{API_URL}/health", timeout=2)
            if health_response.status_code == 200:
                st.success("API Connectée")
            else:
                st.error("Erreur API")
        except:
             st.error("API Hors Ligne")
    
    # Main Tabs
    tab_home, tab_communes, tab_regions, tab_stats, tab_corr = st.tabs([
        "Accueil", 
        "Communes", 
        "Régions", 
        "Départements",
        "Corrélations"
    ])
    
    # --- PROJET ACCUEIL ---
    with tab_home:
        st.header("Vue d'ensemble")
        
        if st.session_state.token:
            if st.button("Actualiser les données"):
                st.rerun()
                
            with st.spinner("Chargement du tableau de bord..."):
                response = api_request("GET", "/stats/summary")
                if response and response.status_code == 200:
                    data = response.json()
                    
                    # KPIs Row 1
                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("Communes Analysées", f"{data.get('total_communes'):,}".replace(",", " "))
                    col2.metric("Ventes Immobilières", f"{data.get('total_ventes'):,}".replace(",", " "))
                    col3.metric("Équipements Recensés", f"{data.get('total_equipements'):,}".replace(",", " "))
                    col4.metric("IAR Moyen National", f"{data.get('iar_moyen_national', 0):.3f}")
                    
                    st.divider()
                    
                    # KPIs Row 2
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Prix m² Moyen", f"{data.get('prix_m2_moyen_national', 0):,.0f} €".replace(",", " "))
                    c2.metric("Score Services Moyen", f"{data.get('score_services_moyen_national', 0):.1f}")
                    
                    top_c = data.get('top_commune', {})
                    if top_c:
                        c3.metric("Top Commune Nationale", f"{top_c.get('nom_commune')} ({top_c.get('iar'):.3f})")
                    
                    display_raw_json(response)
        else:
            st.info("Veuillez vous connecter via le menu latéral pour accéder au tableau de bord.")
            st.image("https://images.unsplash.com/photo-1477959858617-67f85cf4f1df?q=80&w=2000&auto=format&fit=crop", caption="Analyse Territoriale Avancée")

    # --- COMMUNES ---
    with tab_communes:
        st.header("Exploration Detaillée")
        
        if not st.session_state.token:
            st.warning("Authentification requise.")
        else:
            col_search, col_res = st.columns([1, 3])
            
            with col_search:
                st.subheader("Filtres")
                with st.form("search_form"):
                    page = st.number_input("Page", min_value=1, value=1)
                    size = st.number_input("Taille", min_value=10, max_value=100, value=20)
                    sort_key = st.selectbox("Tri", [
                        "iar_desc", "iar_asc", 
                        "prix_asc", "prix_desc",
                        "services_desc", "services_asc"
                    ])
                    dep_filter = st.text_input("Département (opt)", placeholder="Ex: 75")
                    submitted = st.form_submit_button("Lancer la recherche")
            
            with col_res:
                if submitted:
                    params = {"page": page, "size": size, "sort": sort_key}
                    if dep_filter:
                        params["dep"] = dep_filter
                        
                    with st.spinner("Interrogation du Big Data..."):
                        response = api_request("GET", "/communes", params=params)
                        
                        if response and response.status_code == 200:
                            data = response.json()
                            items = data.get("data", [])
                            
                            if items:
                                df = pd.DataFrame(items)
                                st.dataframe(
                                    df[['code_commune', 'nom_commune', 'dep', 'iar', 'prix_m2_moyen', 'score_services_total']]
                                    .style.background_gradient(subset=['iar'], cmap='viridis')
                                    .format({'prix_m2_moyen': "{:,.0f} €"}),
                                    use_container_width=True
                                )
                                
                                # Visualization Row
                                st.subheader("Top Communes de la page")
                                fig = create_top_communes_chart(df, n=len(df), title="")
                                st.plotly_chart(fig, use_container_width=True)
                                
                                # --- DETAIL SECTION ---
                                st.divider()
                                st.subheader("Focus Commune")
                                selected_commune = st.selectbox(
                                    "Sélectionnez une commune pour voir le détail :",
                                    items,
                                    format_func=lambda x: f"{x['nom_commune']} ({x['code_commune']})"
                                )
                                
                                if selected_commune:
                                    # Fetch full details
                                    with st.spinner(f"Analyse de {selected_commune['nom_commune']}..."):
                                        detail_resp = api_request("GET", f"/communes/{selected_commune['code_commune']}")
                                        if detail_resp and detail_resp.status_code == 200:
                                            detail = detail_resp.json()
                                            
                                            # Scorecard Layout
                                            sc1, sc2 = st.columns([1, 1])
                                            
                                            with sc1:
                                                st.metric("IAR Score", f"{detail.get('iar'):.3f}")
                                                st.metric("Prix m²", f"{detail.get('prix_m2_median', detail.get('prix_m2_moyen')):,.0f} €".replace(",", " "))
                                                st.metric("Rangs (Nat/Dep)", f"{detail.get('rang_national')} / {detail.get('rang_dep')}")
                                            
                                            with sc2:
                                                # Radar Chart
                                                fig_radar = create_commune_scorecard(detail)
                                                st.plotly_chart(fig_radar, use_container_width=True)
                                            
                                            display_raw_json(detail_resp, "JSON Détail")
                            else:
                                st.info("Aucun résultat trouvé.")
                            
                            st.caption(f"Page {data.get('page')} / {data.get('pages')}")
                            display_raw_json(response)
                        else:
                             st.error("Erreur lors de la récupération des données.")

    # --- REGIONS ---
    with tab_regions:
        st.header("Analyse Régionale Macroscopique")
        
        if not st.session_state.token:
            st.warning("Authentification requise.")
        else:
            if st.button("Charger l'analyse régionale"):
                with st.spinner("Agrégation des données régionales..."):
                    resp = api_request("GET", "/stats/regions")
                    if resp and resp.status_code == 200:
                        regions_data = resp.json().get("regions", [])
                        df_reg = pd.DataFrame(regions_data)
                        
                        st.subheader("Comparaison IAR / Prix / Services")
                        fig_reg = create_regional_analysis_chart(df_reg)
                        st.plotly_chart(fig_reg, use_container_width=True)
                        
                        with st.expander("Voir les données brutes"):
                            st.dataframe(df_reg)
                            display_raw_json(resp)
                    else:
                        st.error("Impossible de charger les données régionales.")

    # --- DEPARTEMENTS ---
    with tab_stats:
        st.header("Focus Départemental")
        
        if not st.session_state.token:
            st.warning("Authentification requise.")
        else:
            c_input, c_btn = st.columns([3, 1])
            with c_input:
                dep_code = st.text_input("Code Département", value="75")
            with c_btn:
                analyze_btn = st.button("Analyser")
            
            if analyze_btn:
                with st.spinner(f"Analyse du département {dep_code}..."):
                    resp_stats = api_request("GET", f"/departements/{dep_code}/stats")
                    
                    if resp_stats and resp_stats.status_code == 200:
                        stats = resp_stats.json()
                        st.success(f"Département : {stats.get('nom_departement')}")
                        
                        m1, m2, m3 = st.columns(3)
                        m1.metric("Nb Communes", stats.get("nb_communes"))
                        m2.metric("IAR Moyen", f"{stats.get('iar_moyen', 0):.3f}")
                        m3.metric("Prix Moyen", f"{stats.get('prix_m2_moyen', 0):,.0f} €".replace(",", " "))
                        
                        # Top 10 Chart
                        resp_top = api_request("GET", f"/departements/{dep_code}/top", params={"n": 10})
                        if resp_top:
                            top_data = resp_top.json()
                            if top_data:
                                df_top = pd.DataFrame(top_data)
                                # Fix numeric conversion
                                if 'iar' in df_top.columns:
                                    df_top['iar'] = pd.to_numeric(df_top['iar'], errors='coerce')
                                
                                st.subheader(f"Top 10 Communes ({stats.get('nom_departement')})")
                                fig = create_departmental_ranking_chart(df_top, dep_code, n=10)
                                st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.error("Données indisponibles.")

    # --- CORRELATIONS ---
    with tab_corr:
        st.header("Analyse des Corrélations (Prix vs Services)")
        st.info("Cette matrice permet d'identifier les segments de marché (ex: Prix Faible / Services Élevés = Opportunité).")
        
        if not st.session_state.token:
            st.warning("Authentification requise.")
        else:
            if st.button("Générer la Matrice de Corrélation"):
                with st.spinner("Calcul des corrélations..."):
                    resp = api_request("GET", "/stats/correlation")
                    if resp and resp.status_code == 200:
                        corr_data = resp.json().get("correlation", [])
                        df_corr = pd.DataFrame(corr_data)
                        
                        fig_heat = create_correlation_heatmap(df_corr)
                        st.plotly_chart(fig_heat, use_container_width=True)
                        
                        display_raw_json(resp)
                    else:
                        st.error("Erreur lors du calcul des corrélations.")

if __name__ == "__main__":
    main()
