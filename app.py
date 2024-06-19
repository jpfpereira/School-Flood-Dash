import pandas as pd
import geopandas as gpd
import json
import plotly.express as px
import streamlit as st

st.set_page_config(layout='wide')

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

# Sort the dataframe by 'VALOR ESTIMADO'
df_sorted = df.sort_values(by='VALOR ESTIMADO', ascending=True)

# Create the bar chart ranking all schools by 'VALOR ESTIMADO'
fig_all_schools = px.bar(
    df_sorted,
    x='NOME',
    y='VALOR ESTIMADO',
    title='Escolas por Valor Estimado de Prejuízo',
    labels={'VALOR ESTIMADO': 'Valor Estimado de Prejuízo (R$)', 'NOME': 'Nome da Escola'},
    color='VALOR ESTIMADO',
    color_continuous_scale=px.colors.sequential.Sunset
)
fig_all_schools.update_layout(
    title_x=0.5,
    xaxis_tickangle=-45,  # Rotate the x-axis labels
    xaxis_title=None,  # Remove x-axis title for better clarity
    yaxis_title=None,  # Remove y-axis title for better clarity
    margin=dict(l=20, r=20, t=30, b=200),  # Adjust margins to accommodate rotated labels
    height=700,  # Increase the height of the figure
    font=dict(size=10)  # Reduce the font size
)
fig_all_schools.update_traces(
    hovertemplate="<b>%{x}</b><br>Valor Estimado de Prejuízo: R$%{y}<extra></extra>"
)

# Create the new column for 'Prejuízo estimado por aluno'
df['PREJUIZO_POR_ALUNO'] = (df['VALOR ESTIMADO'] / df['NUM ALUNOS']).astype(int)

# Sort the dataframe by 'PREJUIZO_POR_ALUNO'
df_sorted_by_prejuizo_por_aluno = df.sort_values(by='PREJUIZO_POR_ALUNO', ascending=True)

# Create the new bar chart for 'Prejuízo estimado por aluno'
fig_prejuizo_por_aluno = px.bar(
    df_sorted_by_prejuizo_por_aluno,
    x='NOME',
    y='PREJUIZO_POR_ALUNO',
    title='Prejuízo Estimado por Aluno em Cada Escola',
    labels={'PREJUIZO_POR_ALUNO': 'Prejuízo Estimado por Aluno (R$)', 'NOME': 'Nome da Escola'},
    color='PREJUIZO_POR_ALUNO',
    color_continuous_scale=px.colors.sequential.Plasma
)
fig_prejuizo_por_aluno.update_layout(
    title_x=0.5,
    xaxis_tickangle=-45,  # Rotate the x-axis labels
    xaxis_title=None,  # Remove x-axis title for better clarity
    yaxis_title=None,  # Remove y-axis title for better clarity
    margin=dict(l=20, r=20, t=30, b=200),  # Adjust margins to accommodate rotated labels
    height=700,  # Increase the height of the figure
    font=dict(size=10)  # Reduce the font size
)
fig_prejuizo_por_aluno.update_traces(
    hovertemplate="<b>%{x}</b><br>Prejuízo Estimado por Aluno: R$%{y}<extra></extra>"
)

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

# Display the plots below the map
st.plotly_chart(fig_all_schools, use_container_width=True)
st.plotly_chart(fig_prejuizo_por_aluno, use_container_width=True)
st.plotly_chart(fig_students_distribution, use_container_width=True)
st.plotly_chart(fig_average_renda, use_container_width=True)
