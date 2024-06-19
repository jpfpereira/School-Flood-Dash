import pandas as pd
import geopandas as gpd
import json
import plotly.express as px
import streamlit as st

# Load the dataset
df = pd.read_csv('./final_dataset.csv')

# Clean 'VALOR ESTIMADO' column: remove 'R$', handle non-numeric values, convert to float
df['VALOR ESTIMADO'] = df['VALOR ESTIMADO'].str.replace('R$', '', regex=False).str.replace(',', '').str.strip()
df['VALOR ESTIMADO'] = pd.to_numeric(df['VALOR ESTIMADO'].replace(' -', pd.NA), errors='coerce')

# Replace NaN values with the mean of the column
df['VALOR ESTIMADO'].fillna(df['VALOR ESTIMADO'].mean(), inplace=True)

# Convert 'VALOR ESTIMADO' to integers
df['VALOR ESTIMADO'] = df['VALOR ESTIMADO'].astype(int)

# Convert 'NUM ALUNOS' to numeric, errors='coerce' will replace non-numeric values with NaN
df['NUM ALUNOS'] = pd.to_numeric(df['NUM ALUNOS'], errors='coerce')

# Replace NaN values with the mean of the column
df['NUM ALUNOS'].fillna(df['NUM ALUNOS'].mean(), inplace=True)

# Convert 'NUM ALUNOS' to integers
df['NUM ALUNOS'] = df['NUM ALUNOS'].astype(int)

# Load the GeoJSON file
with open('./bairros.geojson') as f:
    neighbourhoods = json.load(f)

# Calculate additional metrics
average_renda = df['renda_media_domicilio_sm'].mean()

# Set up the Streamlit interface
st.title("Impacto das Enchentes no Ensino Infantil de Porto Alegre")
st.subheader(f"Média de renda domiciliar: {average_renda:.2f} salários mínimos")

# Create the scatter mapbox figure
fig_map = px.scatter_mapbox(
    df,
    lat="Latitude",
    lon="Longitude",
    color="VALOR ESTIMADO",
    size="NUM ALUNOS",
    hover_name="NOME",
    hover_data={"Bairro": True, "Latitude": False, "Longitude": False},
    color_continuous_scale=px.colors.sequential.Viridis,
    size_max=15,
    zoom=11,
    mapbox_style="carto-positron",
    title="Prejuízo Estimado Por Escola Com Ensino Infantil"
)

# Add the neighborhood boundaries to the figure
fig_map.update_layout(
    mapbox={
        "layers": [{
            "source": neighbourhoods,
            "type": "line",
            "below": "traces",
            "color": "green",
            "line": {"width": 1}
        }]
    },
    title_x=0.5
)

# Adjust the layout to make the map wider
st.plotly_chart(fig_map, use_container_width=True)

# Create the bar chart for top schools by 'VALOR ESTIMADO'
top_schools = df.nlargest(10, 'VALOR ESTIMADO')
fig_top_schools = px.bar(
    top_schools,
    x='NOME',
    y='VALOR ESTIMADO',
    title='Top 10 Escolas por Valor Estimado de Prejuízo',
    labels={'VALOR ESTIMADO': 'Valor Estimado de Prejuízo (R$)', 'NOME': 'Nome da Escola'},
    color='VALOR ESTIMADO',
    color_continuous_scale=px.colors.sequential.Sunset
)
fig_top_schools.update_layout(title_x=0.5)

# Create the pie chart for student distribution by neighborhood
students_distribution = df.groupby('Bairro')['NUM ALUNOS'].sum().reset_index()
fig_students_distribution = px.pie(
    students_distribution,
    names='Bairro',
    values='NUM ALUNOS',
    title='Distribuição de Alunos por Bairro',
    color_discrete_sequence=px.colors.sequential.RdBu
)
fig_students_distribution.update_layout(title_x=0.5)

# Create the bar chart for average 'renda_media_domicilio_sm' by neighborhood
average_renda_neighborhood = df.groupby('Bairro')['renda_media_domicilio_sm'].mean().reset_index()
fig_average_renda = px.bar(
    average_renda_neighborhood,
    x='Bairro',
    y='renda_media_domicilio_sm',
    title='Média de Renda Domiciliar por Bairro',
    labels={'renda_media_domicilio_sm': 'Renda Média (Salários Mínimos)', 'Bairro': 'Bairro'},
    color='renda_media_domicilio_sm',
    color_continuous_scale=px.colors.sequential.Blues
)
fig_average_renda.update_layout(title_x=0.5)

# Display the other plots below the map
st.plotly_chart(fig_top_schools, use_container_width=True)
st.plotly_chart(fig_students_distribution, use_container_width=True)
st.plotly_chart(fig_average_renda, use_container_width=True)
