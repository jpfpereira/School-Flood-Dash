import pandas as pd
import plotly.express as px
import streamlit as st

# Set page configuration
st.set_page_config(layout='wide', page_title="Dashboard Financeiro", page_icon="💰")

# Load data
base_geral_df = pd.read_csv('data/Base_Geral_Pagamentos.csv')

# Data cleaning and processing
base_geral_df['ESCOLA'] = base_geral_df['ESCOLA'].str.strip().str.upper()
base_geral_df['VALOR'] = base_geral_df['VALOR'].abs()
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

# Function to highlight rows based on status
def highlight_paid(row):
    if row['STATUS'] == 'Pago':
        return ['background-color: #90EE90'] * len(row)  # Light green color
    return [''] * len(row)  # Default to no highlighting for other rows

# Apply the styling
styled_df = sorted_transactions.style.apply(highlight_paid, axis=1)

# Format the 'VALOR' column
styled_df = styled_df.format({'VALOR': 'R$ {:.2f}'})

# Display the styled dataframe
st.dataframe(styled_df, height=600, use_container_width=True)

# Add a legend for the table
st.markdown("""
<div style="background-color: #F0F2F6; padding: 10px; border-radius: 5px; margin-top: 20px;">
    <strong>Legenda:</strong><br>
    <span style="display: inline-block; width: 20px; height: 10px; background-color: #90EE90; margin-right: 5px;"></span> Transações Pagas<br>
    <span style="display: inline-block; width: 20px; height: 10px; background-color: white; border: 1px solid #ccc; margin-right: 5px;"></span> Transações Previstas
</div>
""", unsafe_allow_html=True)