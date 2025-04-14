import dash
import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html
from dash.dependencies import Input, Output, State

# Étape 1 : Charger le fichier brut
df = pd.read_csv("../tunisie_annonce_listings.csv")

# Étape 2 : Nettoyage des données
# Nettoyage minimal : enlever les valeurs manquantes
df.dropna(subset=["title", "location", "price"], inplace=True)

# Nettoyer la colonne 'price' : supprimer les espaces et convertir en entier
def clean_price(price):
    if isinstance(price, str):
        # Supprimer les espaces
        price = price.replace(" ", "")
        try:
            return int(price)  # Convertir en entier
        except ValueError:
            return None
    return int(price)

df["price"] = df["price"].apply(clean_price)
df.dropna(subset=["price"], inplace=True)  # Supprimer les prix non convertibles

# Extraire la ville depuis 'location'
df["city"] = df["location"].apply(
    lambda x: str(x).split(",")[-1].strip() if isinstance(x, str) else "Inconnu"
)

# Déduire le type de bien depuis 'title' (remplace la colonne 'property_type' si nécessaire)
def extraire_type_bien(titre):
    titre = titre.lower()
    if "appart" in titre or "app." in titre or "s1" in titre or "s2" in titre or "s3" in titre:
        return "Appartement"
    elif "villa" in titre:
        return "Villa"
    elif "terrain" in titre:
        return "Terrain"
    elif "maison" in titre:
        return "Maison"
    else:
        return "Autre"

df["property_type"] = df["title"].apply(extraire_type_bien)

# Vérification des prix pour détecter les anomalies
print("Statistiques des prix après nettoyage :", df["price"].describe())

# Étape 3 : Sauvegarder les données nettoyées dans un nouveau fichier CSV
df.to_csv("annonces_nettoyees_nouveau.csv", index=False)
print("Données nettoyées sauvegardées dans 'annonces_nettoyees_nouveau.csv'")

# Étape 4 : Création des figures pour le dashboard
def create_figures(filtered_df):
    # Top 10 villes
    top_cities = filtered_df["city"].value_counts().head(10).reset_index()
    top_cities.columns = ["City", "Number of Listings"]

    fig_top_cities = px.bar(
        top_cities, x="City", y="Number of Listings",
        labels={"City": "Ville", "Number of Listings": "Nombre d'annonces"},
        title="🏙️ Top 10 Villes par Nombre d'Annonces"
    )

    # Distribution des prix
    fig_price_distribution = px.histogram(
        filtered_df, x="price",
        nbins=30,
        title="📈 Distribution des Prix"
    )
    fig_price_distribution.update_layout(
        xaxis_title="Prix (DT)",
        yaxis_title="Nombre d'annonces"
    )

    # Répartition des types de biens
    fig_property_type = px.pie(
        filtered_df, names="property_type",
        title="🏡 Répartition des Types de Biens"
    )
    
    return fig_top_cities, fig_price_distribution, fig_property_type

# Étape 5 : Application Dash
app = Dash(__name__)

app.layout = html.Div(children=[ 
    html.H1("📊 Tableau de Bord Immobilier", style={'textAlign': 'center'}), 

    # Filtres
    html.Div([ 
        html.Label("Filtrer par Ville"), 
        dcc.Dropdown( 
            id='city-filter', 
            options=[{'label': city, 'value': city} for city in df['city'].unique()], 
            value=[], 
            multi=True 
        ), 
    ], style={'padding': '20px'}), 

    html.Div([ 
        html.Label("Filtrer par Type de Bien"), 
        dcc.Dropdown( 
            id='type-filter', 
            options=[{'label': type_, 'value': type_} for type_ in df['property_type'].unique()], 
            value=[], 
            multi=True 
        ), 
    ], style={'padding': '20px'}), 

    html.Div([ 
        html.Label("Filtrer par Plage de Prix"), 
        dcc.RangeSlider( 
            id='price-filter', 
            min=df['price'].min(), 
            max=df['price'].max(), 
            step=1000, 
            marks={i: f"{i:,.0f} DT".replace(",", " ") for i in range(int(df['price'].min()), int(df['price'].max()) + 10000, 20000)}, 
            value=[df['price'].min(), df['price'].max()], 
        ), 
        html.Div([ 
            html.Span(id='price-min-label', style={'marginRight': '20px'}), 
            html.Span(id='price-max-label') 
        ], style={'marginTop': '10px'}) 
    ], style={'padding': '20px', 'backgroundColor': '#f4f4f4', 'borderRadius': '8px'}), 

    # Graphiques
    html.Div([ 
        dcc.Graph(id='type-bien-graph') 
    ], style={'margin': '50px'}), 

    html.Div([ 
        dcc.Graph(id='top-villes-graph') 
    ], style={'margin': '50px'}), 

    html.Div([ 
        dcc.Graph(id='price-distribution-graph') 
    ], style={'margin': '50px'}) 
]) 

# Callback de mise à jour des graphiques
@app.callback(
    [Output('type-bien-graph', 'figure'),
     Output('top-villes-graph', 'figure'),
     Output('price-distribution-graph', 'figure'),
     Output('price-min-label', 'children'),
     Output('price-max-label', 'children')],
    [Input('city-filter', 'value'),
     Input('type-filter', 'value'),
     Input('price-filter', 'value')]
)
def update_graphs(selected_cities, selected_types, price_range):
    if not selected_cities:
        selected_cities = df['city'].unique().tolist()
    if not selected_types:
        selected_types = df['property_type'].unique().tolist()

    filtered_df = df[df['city'].isin(selected_cities)]
    filtered_df = filtered_df[filtered_df['property_type'].isin(selected_types)]
    filtered_df = filtered_df[(
        filtered_df['price'] >= price_range[0]) & 
        (filtered_df['price'] <= price_range[1])
    ]
    
    fig_top_cities, fig_price_distribution, fig_property_type = create_figures(filtered_df)
    
    # Formater les étiquettes min/max avec espaces
    price_min_label = f"Min: {price_range[0]:,.0f} DT".replace(",", " ")
    price_max_label = f"Max: {price_range[1]:,.0f} DT".replace(",", " ")
    
    return fig_property_type, fig_top_cities, fig_price_distribution, price_min_label, price_max_label

# Callback pour réinitialiser les filtres
@app.callback(
    [Output('city-filter', 'value'),
     Output('type-filter', 'value')],
    [Input('clear-city-filter', 'n_clicks'),
     Input('clear-type-filter', 'n_clicks')],
    [State('city-filter', 'value'),
     State('type-filter', 'value')]
)
def reset_filters(clear_city, clear_type, city_value, type_value):
    ctx = dash.callback_context
    if not ctx.triggered:
        return city_value, type_value
    else:
        triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
        if triggered_id == "clear-city-filter":
            return [], type_value
        elif triggered_id == "clear-type-filter":
            return city_value, []

# Lancer le dashboard
if __name__ == "__main__":
    app.run(debug=True)
