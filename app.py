import pandas as pd
import geopandas as gpd
import json
import plotly.express as px
import streamlit as st

st.set_page_config(layout='wide')

# Load the datasets
df = pd.read_csv('data/schools_geo_info.csv')
base_geral_df = pd.read_csv('data/base_geral_pagamentos.csv')

print(base_geral_df.head(5))

base_geral_df['ESCOLA'] = base_geral_df['ESCOLA'].str.upper()
# Clean and convert the VALOR column in base_geral_df
print(f'OLD VALORES {list(base_geral_df["VALOR"])}')

# Remove the 'R$' symbol and any spaces
base_geral_df['VALOR'] = base_geral_df['VALOR'].replace({'R\$': '', ' ': '', '-': ''}, regex=True)

# Remove dots used as thousand separators, replace the comma with a dot for decimal conversion
base_geral_df['VALOR'] = base_geral_df['VALOR'].str.replace('.', '', regex=False)
base_geral_df['VALOR'] = base_geral_df['VALOR'].str.replace(',', '.', regex=False)

# Convert to float, while preserving the negative sign
base_geral_df['VALOR'] = pd.to_numeric(base_geral_df['VALOR'], errors='coerce')

# Calculate the current balance
current_balance = base_geral_df[base_geral_df['CONTABILIDADE'] == 'Entrada']['VALOR'].sum() - \
                  base_geral_df[base_geral_df['CONTABILIDADE'] == 'Saída']['VALOR'].sum()

# Calculate total investments done for schools
total_investments = base_geral_df[base_geral_df['CONTABILIDADE'] == 'Saída']['VALOR'].sum()

# Aggregate investments by school
school_investments = base_geral_df[base_geral_df['CONTABILIDADE'] == 'Saída'].groupby('ESCOLA')['VALOR'].sum().reset_index()
school_investments.columns = ['Nome', 'Valor Investido']

# Merge the aggregated school investments data with the main dataset
df = pd.merge(df, school_investments, on='Nome', how='left')

# Treat NaN values in 'Valor Investido' as 0
df['Valor Investido'].fillna(0, inplace=True)

# Calculate the ratio of Valor Investido to Valor Estimado and convert to percentage
df['Investimento Percentual'] = (df['Valor Investido'] / df['Valor Estimado']) * 100

# Display the balance and total investments on the dashboard
st.title("Reconstrução do Ensino Infantil Impactado pela Enchente")

st.subheader(f"Saldo Atual: R$ {current_balance:,.2f}")
st.subheader(f"Investimentos Totais nas Escolas: R$ {total_investments:,.2f}")

# Create the scatter mapbox figure
fig_map = px.scatter_mapbox(
    df,
    lat="Latitude",
    lon="Longitude",
    color="Investimento Percentual",
    size="Num Alunos",
    hover_name="Nome",
    hover_data={
        "Bairro": True, 
        "Latitude": False, 
        "Longitude": False, 
        "Valor Estimado": True, 
        "Valor Investido": True, 
        "Investimento Percentual": ':.2f'
    },
    color_continuous_scale=px.colors.diverging.RdYlGn,
    size_max=15,
    zoom=11,
    mapbox_style="carto-positron",
    title="Valor Investido por Escola"
)

# Rename color bar
fig_map.update_coloraxes(colorbar_title="Investimento Percentual")

# Add the neighborhood boundaries to the figure
with open('./bairros.geojson') as f:
    neighbourhoods = json.load(f)

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

# Sort the dataframe by 'Valor Estimado'
df_sorted_by_valor_estimado = df.sort_values(by='Valor Estimado', ascending=True)

# Create the new DataFrame for the grouped bar chart
df_melted = df_sorted_by_valor_estimado.melt(id_vars=["Nome"], value_vars=["Valor Estimado", "Valor Investido"], 
                    var_name="Tipo", value_name="Valor")

# Create the grouped bar chart
fig_grouped_bar = px.bar(
    df_melted,
    x='Nome',
    y='Valor',
    color='Tipo',
    barmode='group',
    title='Valor Estimado de Prejuízo e Valor Investido por Escola',
    labels={'Valor': 'Valor (R$)', 'Nome': 'Nome da Escola'},
    color_discrete_map={"Valor Estimado": px.colors.sequential.Sunset[5], "Valor Investido": px.colors.sequential.Plasma[5]}
)
fig_grouped_bar.update_layout(
    title_x=0.5,
    xaxis_tickangle=-45,  # Rotate the x-axis labels
    xaxis_title=None,  # Remove x-axis title for better clarity
    yaxis_title=None,  # Remove y-axis title for better clarity
    margin=dict(l=20, r=20, t=30, b=200),  # Adjust margins to accommodate rotated labels
    height=700,  # Increase the height of the figure
    font=dict(size=10)  # Reduce the font size
)
fig_grouped_bar.update_traces(
    hovertemplate="<b>%{x}</b><br>%{fullData.name}: R$%{y}<extra></extra>"
)

# Sort the dataframe by 'Valor Investido'
df_sorted_by_valor_investido = df.sort_values(by='Valor Investido', ascending=True)

# Create the bar chart for absolute 'Valor Investido'
fig_valor_investido = px.bar(
    df_sorted_by_valor_investido,
    x='Nome',
    y='Valor Investido',
    title='Valor Investido por Escola',
    labels={'Valor Investido': 'Valor Investido (R$)', 'Nome': 'Nome da Escola'},
    color='Valor Investido',
    color_continuous_scale=px.colors.sequential.Blues
)
fig_valor_investido.update_layout(
    title_x=0.5,
    xaxis_tickangle=-45,  # Rotate the x-axis labels
    xaxis_title=None,  # Remove x-axis title for better clarity
    yaxis_title=None,  # Remove y-axis title for better clarity
    margin=dict(l=20, r=20, t=30, b=200),  # Adjust margins to accommodate rotated labels
    height=700,  # Increase the height of the figure
    font=dict(size=10)  # Reduce the font size
)
fig_valor_investido.update_traces(
    hovertemplate="<b>%{x}</b><br>Valor Investido: R$%{y}<extra></extra>"
)

# Sort the dataframe by 'Investimento Percentual'
df_sorted_by_investimento = df.sort_values(by='Investimento Percentual', ascending=True)

# Create the new bar chart for 'Investimento Percentual'
fig_investimento_percentual = px.bar(
    df_sorted_by_investimento,
    x='Nome',
    y='Investimento Percentual',
    title='Investimento Percentual por Escola',
    labels={'Investimento Percentual': 'Investimento Percentual (%)', 'Nome': 'Nome da Escola'},
    color='Investimento Percentual',
    color_continuous_scale=px.colors.sequential.Blues
)
fig_investimento_percentual.update_layout(
    title_x=0.5,
    xaxis_tickangle=-45,  # Rotate the x-axis labels
    xaxis_title=None,  # Remove x-axis title for better clarity
    yaxis_title=None,  # Remove y-axis title for better clarity
    margin=dict(l=20, r=20, t=30, b=200),  # Adjust margins to accommodate rotated labels
    height=700,  # Increase the height of the figure
    font=dict(size=10)  # Reduce the font size
)
fig_investimento_percentual.update_traces(
    hovertemplate="<b>%{x}</b><br>Investimento Percentual: %{y:.2f}%<extra></extra>"
)

# Create the pie chart for investment distribution by neighborhood
investment_distribution = df.groupby('Bairro')['Valor Investido'].sum().reset_index()
fig_investment_distribution = px.pie(
    investment_distribution,
    names='Bairro',
    values='Valor Investido',
    title='Distribuição de Investimento por Bairro',
    color_discrete_sequence=px.colors.sequential.RdBu
)
fig_investment_distribution.update_layout(title_x=0.5)

# Display the plots below the map
st.plotly_chart(fig_grouped_bar, use_container_width=True)
st.plotly_chart(fig_valor_investido, use_container_width=True)
st.plotly_chart(fig_investimento_percentual, use_container_width=True)
st.plotly_chart(fig_investment_distribution, use_container_width=True)

# Parse and extract the month names from the 'MÊS' column, safely handling NaNs
base_geral_df['MÊS'] = base_geral_df['MÊS'].apply(lambda x: x.split('.')[1] if pd.notnull(x) else x)

# Convert 'Mês' column to a categorical type with a specific order
month_order = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
base_geral_df['MÊS'] = pd.Categorical(base_geral_df['MÊS'], categories=month_order, ordered=True)
base_geral_df['ESCOLA'] = base_geral_df['ESCOLA'].str.upper()

# Sort the dataframe by 'Mês'
recent_investments = base_geral_df.sort_values(by='MÊS', ascending=False)

# Drop unnecessary columns for displaying recent investments
columns_to_drop = ['ID', 'ANO', 'ITEM', 'CATEGORIA', 'DATA_VENCIMENTO', 'DATA_PAGAMENTO', 'TIPO_DE_PAGAMENTO']
recent_investments = recent_investments.drop(columns=columns_to_drop)

# Display the most recent investments as a table
st.header("Investimentos Recentes")
st.table(recent_investments[['MÊS', 'ESCOLA', 'VALOR', 'CONTABILIDADE']].head(50))
