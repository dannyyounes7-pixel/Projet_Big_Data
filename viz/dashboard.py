"""
Streamlit Dashboard for IAR Platform
"""
import streamlit as st
import pandas as pd
import psycopg2
import yaml
from viz.charts import (
    create_top_communes_chart,
    create_scatter_plot,
    create_departmental_ranking_chart,
    create_regional_comparison_chart,
    create_service_categories_chart,
    create_price_distribution_chart
)


# Page configuration
st.set_page_config(
    page_title="IAR Platform Dashboard",
    page_icon="🏘️",
    layout="wide",
    initial_sidebar_state="expanded"
)


@st.cache_resource
def get_db_connection():
    """Create database connection"""
    with open('config/api.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    db_config = config['database']
    conn_str = db_config['url']
    
    # Parse connection string
    parts = conn_str.replace('postgresql://', '').split('@')
    user_pass = parts[0].split(':')
    host_port_db = parts[1].split('/')
    host_port = host_port_db[0].split(':')
    
    conn = psycopg2.connect(
        user=user_pass[0],
        password=user_pass[1],
        host=host_port[0],
        port=int(host_port[1]) if len(host_port) > 1 else 5432,
        database=host_port_db[1]
    )
    
    return conn


@st.cache_data(ttl=600)
def load_commune_data():
    """Load commune data from database"""
    conn = get_db_connection()
    query = "SELECT * FROM dm_commune_iar"
    df = pd.read_sql(query, conn)
    return df


@st.cache_data(ttl=600)
def load_department_data():
    """Load department statistics"""
    conn = get_db_connection()
    query = "SELECT * FROM dm_dep_stats"
    df = pd.read_sql(query, conn)
    return df


def main():
    """Main dashboard function"""
    
    # Title and description
    st.title("🏘️ IAR Platform - Indice d'Attractivité Rationnelle")
    st.markdown("""
    Analysez les communes françaises selon leur rapport **services de proximité / prix immobilier**.
    
    **Formule IAR** : `0.7 × services_normalisés + 0.3 × (1 - prix_normalisés)`
    """)
    
    # Load data
    with st.spinner("Chargement des données..."):
        df_communes = load_commune_data()
        df_departments = load_department_data()
    
    # Sidebar filters
    st.sidebar.header("🔍 Filtres")
    
    # Department filter
    departments = sorted(df_communes['dep'].dropna().unique())
    selected_dep = st.sidebar.selectbox(
        "Département",
        options=['Tous'] + list(departments),
        index=0
    )
    
    # IAR range filter
    iar_min, iar_max = st.sidebar.slider(
        "Plage IAR",
        min_value=float(df_communes['iar'].min()),
        max_value=float(df_communes['iar'].max()),
        value=(float(df_communes['iar'].min()), float(df_communes['iar'].max())),
        step=0.01
    )
    
    # Price range filter
    prix_min, prix_max = st.sidebar.slider(
        "Prix au m² (€)",
        min_value=float(df_communes['prix_m2'].min()),
        max_value=float(df_communes['prix_m2'].max()),
        value=(float(df_communes['prix_m2'].min()), float(df_communes['prix_m2'].max())),
        step=100.0
    )
    
    # Apply filters
    df_filtered = df_communes.copy()
    
    if selected_dep != 'Tous':
        df_filtered = df_filtered[df_filtered['dep'] == selected_dep]
    
    df_filtered = df_filtered[
        (df_filtered['iar'] >= iar_min) &
        (df_filtered['iar'] <= iar_max) &
        (df_filtered['prix_m2'] >= prix_min) &
        (df_filtered['prix_m2'] <= prix_max)
    ]
    
    # Key metrics
    st.header("📊 Indicateurs Clés")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Communes", f"{len(df_filtered):,}")
    
    with col2:
        st.metric("IAR Moyen", f"{df_filtered['iar'].mean():.3f}")
    
    with col3:
        st.metric("Prix m² Moyen", f"{df_filtered['prix_m2'].mean():.0f} €")
    
    with col4:
        st.metric("Score Services Moyen", f"{df_filtered['score_services_total'].mean():.1f}")
    
    # Tabs for different visualizations
    tab1, tab2, tab3, tab4 = st.tabs([
        "🏆 Top Communes",
        "📈 Corrélation Prix-Services",
        "🗺️ Analyse Départementale",
        "📊 Statistiques"
    ])
    
    # Tab 1: Top Communes
    with tab1:
        st.header("Top Communes par IAR")
        
        n_top = st.slider("Nombre de communes à afficher", 5, 50, 10)
        
        fig_top = create_top_communes_chart(df_filtered, n=n_top)
        st.plotly_chart(fig_top, use_container_width=True)
        
        # Data table
        st.subheader("Détails")
        top_communes = df_filtered.nlargest(n_top, 'iar')[
            ['code_commune', 'nom_commune', 'dep', 'iar', 'prix_m2', 
             'score_services_total', 'nb_ventes', 'rang_national']
        ]
        st.dataframe(top_communes, use_container_width=True)
    
    # Tab 2: Scatter Plot
    with tab2:
        st.header("Corrélation Prix vs Services")
        
        fig_scatter = create_scatter_plot(df_filtered)
        st.plotly_chart(fig_scatter, use_container_width=True)
        
        # Correlation coefficient
        corr = df_filtered[['prix_m2', 'score_services_total']].corr().iloc[0, 1]
        st.metric("Coefficient de corrélation", f"{corr:.3f}")
        
        if corr > 0:
            st.info("✅ Corrélation positive : les communes avec plus de services ont tendance à avoir des prix plus élevés.")
        else:
            st.info("⚠️ Corrélation négative : les communes avec plus de services ont tendance à avoir des prix plus bas.")
    
    # Tab 3: Departmental Analysis
    with tab3:
        st.header("Analyse Départementale")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Department selector
            dep_for_ranking = st.selectbox(
                "Sélectionner un département",
                options=departments
            )
            
            n_dep = st.slider("Nombre de communes", 5, 20, 10, key="dep_slider")
            
            fig_dep = create_departmental_ranking_chart(df_communes, dep_for_ranking, n=n_dep)
            st.plotly_chart(fig_dep, use_container_width=True)
        
        with col2:
            # Regional comparison
            if 'reg' in df_communes.columns:
                fig_regional = create_regional_comparison_chart(df_communes)
                st.plotly_chart(fig_regional, use_container_width=True)
        
        # Department statistics table
        st.subheader("Statistiques Départementales")
        st.dataframe(
            df_departments.sort_values('iar_moyen', ascending=False),
            use_container_width=True
        )
    
    # Tab 4: Statistics
    with tab4:
        st.header("Statistiques Globales")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Price distribution
            fig_prix = create_price_distribution_chart(df_filtered)
            st.plotly_chart(fig_prix, use_container_width=True)
        
        with col2:
            # IAR distribution
            fig_iar = create_price_distribution_chart(
                df_filtered.rename(columns={'iar': 'prix_m2'})
            )
            fig_iar.update_layout(
                title='Distribution IAR',
                xaxis_title='IAR'
            )
            st.plotly_chart(fig_iar, use_container_width=True)
        
        # Summary statistics
        st.subheader("Statistiques Descriptives")
        
        stats_df = df_filtered[['iar', 'prix_m2', 'score_services_total', 'nb_ventes']].describe()
        st.dataframe(stats_df, use_container_width=True)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    **IAR Platform** - Projet Big Data Framework  
    Sources : DVF 2024, BPE 2024 (INSEE), Référentiel Communes 2024
    """)


if __name__ == "__main__":
    main()
