import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(layout='wide')

# Load data
df = pd.read_csv('data/schools_geo_info.csv')
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

# Calculate total investments per school (including both 'Pago' and 'Forecast')
school_investments = base_geral_df[base_geral_df['Tipo'] == 'Saída'].groupby('ESCOLA')['VALOR'].sum().reset_index()
school_investments.columns = ['Nome', 'Valor Investido']

# Merge data
df = pd.merge(df, school_investments, on='Nome', how='left')
df['Valor Investido'].fillna(0, inplace=True)

# Dashboard title and balance display
st.title("Dashboard Financeiro - Escolas Conveniadas POA")
st.subheader(f"Saldo Atual: R$ {current_balance:,.2f}")
st.subheader(f"Total Doado para Escolas: R$ {total_investments:,.2f}")

# Bar chart for total invested values per school
fig_valor_investido = px.bar(
    df.sort_values(by='Valor Investido', ascending=False),
    x='Nome',
    y='Valor Investido',
    title='Valor Doado por Escola',
    labels={'Valor Investido': 'Valor (R$)', 'Nome': 'Nome da Escola'},
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

def paginate_dataframe(df, page_size, page_num):
    start_index = page_num * page_size
    end_index = start_index + page_size
    return df[start_index:end_index]

# Number of rows per page
page_size = 20

# Number of pages available
total_pages = (len(all_transactions) + page_size - 1) // page_size

# Create a container for the pagination and table
with st.container():
    # User selects the page
    page_num = st.selectbox('Página', range(total_pages), format_func=lambda x: f'Página {x + 1}', key='page_selector')

    # Paginate the dataframe
    paginated_df = paginate_dataframe(all_transactions[['MÊS', 'ESCOLA', 'ITEM', 'CATEGORIA', 'PRESTADOR', 'VALOR', 'STATUS']], page_size, page_num)
    
    # Sort the paginated dataframe by month order
    paginated_df['MÊS'] = pd.Categorical(paginated_df['MÊS'], categories=month_order, ordered=True)
    paginated_df = paginated_df.sort_values('MÊS')

    # Display the paginated dataframe with increased height
    st.dataframe(paginated_df, height=600, use_container_width=True)