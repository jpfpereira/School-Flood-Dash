import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(layout='wide')

# Load data
df = pd.read_csv('data/schools_geo_info.csv')
base_geral_df = pd.read_csv('data/base_geral_pagamentos.csv')

# Data cleaning and processing
base_geral_df['ESCOLA'] = base_geral_df['ESCOLA'].str.strip().str.upper()
base_geral_df['VALOR'] = pd.to_numeric(
    base_geral_df['VALOR']
    .str.replace(r'R\$', '', regex=True)
    .str.replace(' ', '', regex=False)
    .str.replace('-', '', regex=False)
    .str.replace('.', '', regex=False)
    .str.replace(',', '.', regex=False),
    errors='coerce'
)

# Handle date format variations in 'DATA_VENCIMENTO'
base_geral_df['DATA_VENCIMENTO'] = pd.to_datetime(base_geral_df['DATA_VENCIMENTO'], dayfirst=True, errors='coerce')

# Calculate current balance and total investments
current_balance = base_geral_df[base_geral_df['Tipo'] == 'Entrada']['VALOR'].sum() - \
                  base_geral_df[base_geral_df['Tipo'] == 'Saída']['VALOR'].sum()

total_investments = base_geral_df[base_geral_df['Tipo'] == 'Saída']['VALOR'].sum()

# Calculate investments per school
school_investments = base_geral_df[base_geral_df['Tipo'] == 'Saída'].groupby('ESCOLA')['VALOR'].sum().reset_index()
school_investments.columns = ['Nome', 'Valor Investido']

# Merge data
df = pd.merge(df, school_investments, on='Nome', how='left')
df['Valor Investido'].fillna(0, inplace=True)

# Dashboard title and balance display
st.title("Dashboard Financeiro - Escolas Conveniadas POA")
st.subheader(f"Saldo Atual: R$ {current_balance:,.2f}")
st.subheader(f"Investimentos Totais nas Escolas: R$ {total_investments:,.2f}")

# Bar chart for invested values per school
fig_valor_investido = px.bar(
    df.sort_values(by='Valor Investido'),
    x='Nome',
    y='Valor Investido',
    title='Valor Investido por Escola',
    labels={'Valor Investido': 'Valor Investido (R$)', 'Nome': 'Nome da Escola'},
    color='Valor Investido',
    color_continuous_scale=px.colors.sequential.Blues
)
fig_valor_investido.update_layout(
    title_x=0.5,
    xaxis_tickangle=-45,
    xaxis_title=None,
    yaxis_title=None,
    margin=dict(l=20, r=20, t=30, b=200),
    height=700,
    font=dict(size=10)
)
fig_valor_investido.update_traces(
    hovertemplate="<b>%{x}</b><br>Valor Investido: R$%{y}<extra></extra>"
)

st.plotly_chart(fig_valor_investido, use_container_width=True)

# Calculate the Balanço (balance) for each date
balanco_df = base_geral_df[['DATA_VENCIMENTO', 'VALOR', 'Tipo']]

balanco_df['VALOR'] = balanco_df.apply(
    lambda x: x['VALOR'] if x['Tipo'] == 'Entrada' else -x['VALOR'],
    axis=1
)

# Group by 'DATA_VENCIMENTO' and sum the 'VALOR'
aggregated_balanco_df = balanco_df.groupby('DATA_VENCIMENTO')['VALOR'].sum().reset_index()

# Convert 'DATA_VENCIMENTO' to datetime format, handle different formats
aggregated_balanco_df['DATA_VENCIMENTO'] = pd.to_datetime(aggregated_balanco_df['DATA_VENCIMENTO'], dayfirst=True, errors='coerce')

# Sort the dataframe by 'DATA_VENCIMENTO'
aggregated_balanco_df = aggregated_balanco_df.sort_values(by='DATA_VENCIMENTO')

# Calculate the running total (cumulative sum) of 'VALOR'
aggregated_balanco_df['TOTAL_CASH'] = aggregated_balanco_df['VALOR'].cumsum()

# Plot the Balanço over time
fig_balanco = px.line(
    aggregated_balanco_df,
    x='DATA_VENCIMENTO',
    y='TOTAL_CASH',
    title='Evolução do Balanço ao Longo do Tempo',
    labels={'TOTAL_CASH': 'Balanço (R$)', 'DATA_VENCIMENTO': 'Data de Vencimento'},
    markers=True
)
fig_balanco.update_layout(
    title_x=0.5,
    xaxis_tickangle=-45,
    xaxis_title=None,
    yaxis_title=None,
    height=600,
    font=dict(size=12)
)
fig_balanco.update_traces(
    hovertemplate="<b>%{x|%d/%m/%Y}</b><br>Balanço: R$%{y}<extra></extra>"
)

st.plotly_chart(fig_balanco, use_container_width=True)

# Process months for recent investments
base_geral_df['MÊS'] = base_geral_df['MÊS'].apply(lambda x: x.split('. ')[1] if pd.notnull(x) else x)
month_order = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
base_geral_df['MÊS'] = pd.Categorical(base_geral_df['MÊS'], categories=month_order, ordered=True)
recent_investments = base_geral_df[base_geral_df['Tipo'] == 'Saída']
recent_investments = recent_investments.sort_values(by='MÊS', ascending=False).reset_index(drop=True)

def paginate_dataframe(df, page_size, page_num):
    start_index = page_num * page_size
    end_index = start_index + page_size
    return df[start_index:end_index]

# Number of rows per page
page_size = 20

# Number of pages available
total_pages = (len(recent_investments) + page_size - 1) // page_size

# Create a container for the pagination and table
with st.container():
    # User selects the page
    page_num = st.selectbox('Página', range(total_pages), format_func=lambda x: f'Página {x + 1}', key='page_selector')

    # Paginate the dataframe
    paginated_df = paginate_dataframe(recent_investments[['MÊS', 'ESCOLA', 'ITEM', 'CATEGORIA', 'PRESTADOR', 'VALOR']], page_size, page_num)

    # Display the paginated dataframe
    st.dataframe(paginated_df, height=400, use_container_width=True)