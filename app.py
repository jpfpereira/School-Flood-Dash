import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(layout='wide')

# Load data
base_geral_df = pd.read_csv('data/base-geral-pagamentos.csv')

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

# Calculate current balance and total investments (only for 'Pago' status)
paid_transactions = base_geral_df[base_geral_df['STATUS'] == 'Pago']
current_balance = paid_transactions[paid_transactions['Tipo'] == 'Entrada']['VALOR'].sum() - \
                  paid_transactions[paid_transactions['Tipo'] == 'Saída']['VALOR'].sum()

total_investments = paid_transactions[paid_transactions['Tipo'] == 'Saída']['VALOR'].sum()

# Calculate investments per school
school_investments_paid = base_geral_df[(base_geral_df['Tipo'] == 'Saída') & (base_geral_df['STATUS'] == 'Pago')].groupby('ESCOLA')['VALOR'].sum().reset_index()
school_investments_paid.columns = ['Nome', 'Valor Pago']

school_investments_forecast = base_geral_df[base_geral_df['Tipo'] == 'Saída'].groupby('ESCOLA')['VALOR'].sum().reset_index()
school_investments_forecast.columns = ['Nome', 'Valor Previsto']

# Merge the two dataframes
df = pd.merge(school_investments_paid, school_investments_forecast, on='Nome', how='outer')
df['Valor Pago'].fillna(0, inplace=True)
df['Valor Previsto'].fillna(0, inplace=True)

# Dashboard title and balance display
st.title("Dashboard Financeiro - Escolas Conveniadas POA")
st.subheader(f"Saldo Atual: R$ {current_balance:,.2f}")
st.subheader(f"Total Doado para Escolas: R$ {total_investments:,.2f}")

# Grouped bar chart for paid and forecasted values per school
df_melted = df.melt(id_vars=['Nome'], value_vars=['Valor Pago', 'Valor Previsto'], var_name='Tipo', value_name='Valor')
fig_valor_investido = px.bar(
    df_melted.sort_values(by=['Nome', 'Tipo']),
    x='Nome',
    y='Valor',
    color='Tipo',
    barmode='group',
    title='Valor Doado por Escola (Pago e Previsto)',
    labels={'Valor': 'Valor (R$)', 'Nome': 'Nome da Escola'},
    color_discrete_map={'Valor Pago': '#636EFA', 'Valor Previsto': '#EF553B'}
)
fig_valor_investido.update_layout(
    title_x=0.5,
    xaxis_tickangle=-45,
    xaxis_title=None,
    yaxis_title=None,
    margin=dict(l=20, r=20, t=30, b=200),
    height=700,
    font=dict(size=10),
    legend_title_text='Status'
)
fig_valor_investido.update_traces(
    hovertemplate="<b>%{x}</b><br>R$ %{y:.2f}"
)

st.plotly_chart(fig_valor_investido, use_container_width=True)

# Process months for all transactions
month_order = ['Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
base_geral_df['MÊS'] = base_geral_df['MÊS'].apply(lambda x: x.split('. ')[1] if pd.notnull(x) else x)
base_geral_df['MÊS'] = pd.Categorical(base_geral_df['MÊS'], categories=month_order, ordered=True)

# Create a month-year column for correct sorting
base_geral_df['MÊS_ANO'] = pd.to_datetime(base_geral_df['DATA_VENCIMENTO']).dt.to_period('M')

# Sort all transactions from oldest to most recent
all_transactions = base_geral_df[base_geral_df['Tipo'] == 'Saída'].sort_values(by=['MÊS_ANO', 'DATA_VENCIMENTO'])

# Select and sort the columns for display
display_columns = ['MÊS', 'ESCOLA', 'ITEM', 'CATEGORIA', 'PRESTADOR', 'VALOR', 'STATUS']
sorted_transactions = all_transactions[display_columns]
sorted_transactions = sorted_transactions.sort_values('MÊS')

# Add a title for the table
st.subheader("Detalhamento de Transações")

# Display the scrollable dataframe with increased height
st.dataframe(sorted_transactions, height=600, use_container_width=True)