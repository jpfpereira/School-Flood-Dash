import pandas as pd
import geopandas as gpd
import json
import plotly.express as px
import streamlit as st

st.set_page_config(layout='wide')

# Load the datasets
df = pd.read_csv('data/schools_geo_info.csv')
cashflow_df = pd.read_csv('data/aggregated_cashflow.csv')
recent_investments = pd.read_csv('data/cashflow.csv')

# Load the GeoJSON file
with open('./bairros.geojson') as f:
    neighbourhoods = json.load(f)

# Merge the aggregated cashflow data with the main dataset
df = pd.merge(df, cashflow_df, left_on='Nome', right_on='Escola', how='left')
df.rename(columns={'Valor': 'Valor Investido'}, inplace=True)

# Treat NaN values in 'Valor Investido' as 0
df['Valor Investido'].fillna(0, inplace=True)

# Calculate additional metrics
average_renda = df['Renda_Media_Domicilio_Sm'].mean()

# Calculate the ratio of Valor Investido to Valor Estimado and convert to percentage
df['Investimento Percentual'] = (df['Valor Investido'] / df['Valor Estimado']) * 100

# Set up the Streamlit interface
st.title("Reconstrução do Ensino Infantil Impactado pela Enchente")

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
    title='Escolas por Valor Estimado de Prejuízo e Valor Investido',
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

# Transform 'Mês' column
recent_investments['Mês'] = recent_investments['Mês'].apply(lambda x: x.split('.')[1])

# Convert 'Mês' column to a categorical type with a specific order
month_order = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
recent_investments['Mês'] = pd.Categorical(recent_investments['Mês'], categories=month_order, ordered=True)

# Sort the dataframe by 'Mês'
recent_investments = recent_investments.sort_values(by='Mês', ascending=False)

# Drop unnecessary columns
columns_to_drop = ['ID', 'Ano', 'Item', 'Categoria', 'Data de Vencimento', 'Data de Pagamento', 'Método de Pagameto']
recent_investments = recent_investments.drop(columns=columns_to_drop)

# Display the most recent investments as a table
st.header("Investimentos Recentes")
st.table(recent_investments.head(50))
