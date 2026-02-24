"""
Chart Generation Functions for IAR Dashboard
"""
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd


def create_top_communes_chart(df: pd.DataFrame, n: int = 10, title: str = "Top 10 Communes par IAR"):
    """
    Create horizontal bar chart for top communes by IAR
    
    Args:
        df: DataFrame with commune data
        n: Number of top communes to show
        title: Chart title
        
    Returns:
        Plotly figure
    """
    # Get top N communes
    df_top = df.nlargest(n, 'iar')
    
    # Create horizontal bar chart
    fig = px.bar(
        df_top,
        y='nom_commune',
        x='iar',
        orientation='h',
        title=title,
        labels={'iar': 'IAR', 'nom_commune': 'Commune'},
        color='iar',
        color_continuous_scale='viridis',
        text='iar'
    )
    
    fig.update_traces(texttemplate='%{text:.3f}', textposition='outside')
    fig.update_layout(
        height=500,
        showlegend=False,
        yaxis={'categoryorder': 'total ascending'}
    )
    
    return fig


def create_scatter_plot(df: pd.DataFrame, title: str = "Prix vs Services"):
    """
    Create scatter plot for price vs services correlation
    
    Args:
        df: DataFrame with commune data
        title: Chart title
        
    Returns:
        Plotly figure
    """
    fig = px.scatter(
        df,
        x='prix_m2_moyen',
        y='score_services_total',
        color='iar',
        size='nb_ventes',
        hover_data=['nom_commune', 'dep', 'iar'],
        title=title,
        labels={
            'prix_m2_moyen': 'Prix au m² (€)',
            'score_services_total': 'Score Services',
            'iar': 'IAR',
            'nb_ventes': 'Nombre de ventes'
        },
        color_continuous_scale='RdYlGn',
        opacity=0.7
    )
    
    # Add trend line
    fig.add_trace(
        go.Scatter(
            x=df['prix_m2_moyen'],
            y=df['score_services_total'],
            mode='lines',
            name='Tendance',
            line=dict(color='red', dash='dash'),
            showlegend=True
        )
    )
    
    fig.update_layout(height=600)
    
    return fig


def create_departmental_ranking_chart(df: pd.DataFrame, dep: str, n: int = 10):
    """
    Create bar chart for top communes in a department
    
    Args:
        df: DataFrame with commune data
        dep: Department code
        n: Number of communes to show
        
    Returns:
        Plotly figure
    """
    # Filter by department
    df_dep = df[df['dep'] == dep].nlargest(n, 'iar')
    
    # Create grouped bar chart showing IAR components
    fig = go.Figure()
    
    # IAR total
    fig.add_trace(go.Bar(
        name='IAR',
        x=df_dep['nom_commune'],
        y=df_dep['iar'],
        marker_color='lightblue'
    ))
    
    fig.update_layout(
        title=f'Top {n} Communes - Département {dep}',
        xaxis_title='Commune',
        yaxis_title='Score',
        barmode='group',
        height=500,
        xaxis={'tickangle': -45}
    )
    
    return fig


def create_regional_comparison_chart(df: pd.DataFrame):
    """
    Create box plot comparing IAR across regions
    
    Args:
        df: DataFrame with commune data
        
    Returns:
        Plotly figure
    """
    fig = px.box(
        df,
        x='reg',
        y='iar',
        title='Distribution IAR par Région',
        labels={'reg': 'Région', 'iar': 'IAR'},
        color='reg'
    )
    
    fig.update_layout(
        height=500,
        showlegend=False
    )
    
    return fig


def create_service_categories_chart(df: pd.DataFrame, commune_code: str):
    """
    Create radar chart for service categories of a commune
    
    Args:
        df: DataFrame with commune data
        commune_code: Commune code
        
    Returns:
        Plotly figure
    """
    commune = df[df['code_commune'] == commune_code].iloc[0]
    
    categories = ['Santé', 'Éducation', 'Transport', 'Commerce', 'Services Publics', 'Loisirs']
    values = [
        commune.get('score_sante', 0),
        commune.get('score_education', 0),
        commune.get('score_transport', 0),
        commune.get('score_commerce', 0),
        commune.get('score_services_publics', 0),
        commune.get('score_loisirs', 0)
    ]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name=commune['nom_commune']
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, max(values) * 1.2])
        ),
        showlegend=True,
        title=f"Profil Services - {commune['nom_commune']}"
    )
    
    return fig


def create_price_distribution_chart(df: pd.DataFrame):
    """
    Create histogram for price distribution
    
    Args:
        df: DataFrame with commune data
        
    Returns:
        Plotly figure
    """
    fig = px.histogram(
        df,
        x='prix_m2_moyen',
        nbins=50,
        title='Distribution des Prix au m²',
        labels={'prix_m2_moyen': 'Prix au m² (€)', 'count': 'Nombre de communes'},
        color_discrete_sequence=['steelblue']
    )
    
    fig.update_layout(height=400)
    
    return fig
def create_regional_analysis_chart(df):
    """
    Create an interactive scatter plot for regional analysis
    """
    fig = px.scatter(
        df,
        x="prix_m2_moyen",
        y="iar_moyen",
        size="nb_communes",
        color="reg",
        hover_name="reg",
        hover_data=["score_services_moyen", "iar_min", "iar_max"],
        title="Analyse Régionale : IAR vs Prix m² (Taille = Nb Communes)",
        labels={
            "prix_m2_moyen": "Prix Moyen (km²)",
            "iar_moyen": "IAR Moyen",
            "nb_communes": "Nombre de Communes",
            "reg": "Région"
        },
        template="plotly_dark"
    )
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        height=600
    )
    return fig

def create_correlation_heatmap(df):
    """
    Create a heatmap for price vs services correlation
    """
    # Pivot for heatmap: index=Price, columns=Services, values=IAR
    pivot_df = df.pivot(index='prix_categorie', columns='services_categorie', values='iar_moyen')
    
    # Ensure correct order
    price_order = ['Faible', 'Moyen', 'Élevé'] # Note: SQL query returned 'Bas', 'Moyen', 'Elevé' for price
    # Let's check the SQL query in stats.py again. 
    # It uses: WHEN prix_m2 < 2000 THEN 'Bas' ...
    
    # We should handle different potential labels or re-index if possible
    # For fail-safety, we just plot what we have
    
    fig = px.imshow(
        pivot_df,
        labels=dict(x="Niveau de Services", y="Catégorie de Prix", color="IAR Moyen"),
        x=pivot_df.columns,
        y=pivot_df.index,
        text_auto=".2f",
        aspect="auto",
        title="Corrélation Prix / Services (Valeur : IAR Moyen)",
        template="plotly_dark",
        color_continuous_scale="viridis"
    )
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)"
    )
    return fig

def create_commune_scorecard(commune_data):
    """
    Create a Radar Chart (Spider Plot) for commune scores
    """
    categories = ['Santé', 'Éducation', 'Transport', 'Commerce', 'Services Publics', 'Loisirs']
    
    # Extract scores, handling Nones
    values = [
        commune_data.get('score_sante', 0) or 0,
        commune_data.get('score_education', 0) or 0,
        commune_data.get('score_transport', 0) or 0,
        commune_data.get('score_commerce', 0) or 0,
        commune_data.get('score_services_publics', 0) or 0,
        commune_data.get('score_loisirs', 0) or 0
    ]
    
    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name=commune_data.get('nom_commune', 'Commune'),
        line_color='#00CC96'
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, max(max(values), 10)] # Dynamic range
            )
        ),
        showlegend=False,
        title=f"Profil des Services : {commune_data.get('nom_commune')}",
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )
    return fig
