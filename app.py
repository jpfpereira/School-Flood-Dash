import pandas as pd
import json
import plotly.express as px
import streamlit as st

st.set_page_config(layout='wide')

df = pd.read_csv('data/schools_geo_info.csv')
base_geral_df = pd.read_csv('data/base_geral_pagamentos.csv')

base_geral_df['ESCOLA'] = base_geral_df['ESCOLA'].str.upper()
base_geral_df['VALOR'] = pd.to_numeric(
    base_geral_df['VALOR']
    .str.replace(r'R\$', '', regex=True)
    .str.replace(' ', '', regex=False)
    .str.replace('-', '', regex=False)
    .str.replace('.', '', regex=False)
    .str.replace(',', '.', regex=False),
    errors='coerce'
)

current_balance = base_geral_df[base_geral_df['CONTABILIDADE'] == 'Entrada']['VALOR'].sum() - \
                  base_geral_df[base_geral_df['CONTABILIDADE'] == 'Saída']['VALOR'].sum()

total_investments = base_geral_df[base_geral_df['CONTABILIDADE'] == 'Saída']['VALOR'].sum()

school_investments = base_geral_df[base_geral_df['CONTABILIDADE'] == 'Saída'].groupby('ESCOLA')['VALOR'].sum().reset_index()
school_investments.columns = ['Nome', 'Valor Investido']

df = pd.merge(df, school_investments, on='Nome', how='left')
df['Valor Investido'].fillna(0, inplace=True)
df['Investimento Percentual'] = (df['Valor Investido'] / df['Valor Estimado']) * 100

st.title("Reconstrução do Ensino Infantil Impactado pela Enchente")
st.subheader(f"Saldo Atual: R$ {current_balance:,.2f}")
st.subheader(f"Investimentos Totais nas Escolas: R$ {total_investments:,.2f}")

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
fig_map.update_coloraxes(colorbar_title="Investimento Percentual")

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

st.plotly_chart(fig_map, use_container_width=True)

df_melted = df.sort_values(by='Valor Estimado').melt(id_vars=["Nome"], value_vars=["Valor Estimado", "Valor Investido"], 
                    var_name="Tipo", value_name="Valor")

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
    xaxis_tickangle=-45,
    xaxis_title=None,
    yaxis_title=None,
    margin=dict(l=20, r=20, t=30, b=200),
    height=700,
    font=dict(size=10)
)
fig_grouped_bar.update_traces(
    hovertemplate="<b>%{x}</b><br>%{fullData.name}: R$%{y}<extra></extra>"
)

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

fig_investimento_percentual = px.bar(
    df.sort_values(by='Investimento Percentual'),
    x='Nome',
    y='Investimento Percentual',
    title='Investimento Percentual por Escola',
    labels={'Investimento Percentual': 'Investimento Percentual (%)', 'Nome': 'Nome da Escola'},
    color='Investimento Percentual',
    color_continuous_scale=px.colors.sequential.Blues
)
fig_investimento_percentual.update_layout(
    title_x=0.5,
    xaxis_tickangle=-45,
    xaxis_title=None,
    yaxis_title=None,
    margin=dict(l=20, r=20, t=30, b=200),
    height=700,
    font=dict(size=10)
)
fig_investimento_percentual.update_traces(
    hovertemplate="<b>%{x}</b><br>Investimento Percentual: %{y:.2f}%<extra></extra>"
)

investment_distribution = df.groupby('Bairro')['Valor Investido'].sum().reset_index()
fig_investment_distribution = px.pie(
    investment_distribution,
    names='Bairro',
    values='Valor Investido',
    title='Distribuição de Investimento por Bairro',
    color_discrete_sequence=px.colors.sequential.RdBu
)
fig_investment_distribution.update_layout(title_x=0.5)

st.plotly_chart(fig_grouped_bar, use_container_width=True)
st.plotly_chart(fig_valor_investido, use_container_width=True)
st.plotly_chart(fig_investimento_percentual, use_container_width=True)
st.plotly_chart(fig_investment_distribution, use_container_width=True)

base_geral_df['MÊS'] = base_geral_df['MÊS'].apply(lambda x: x.split('. ')[1] if pd.notnull(x) else x)
month_order = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
base_geral_df['MÊS'] = pd.Categorical(base_geral_df['MÊS'], categories=month_order, ordered=True)
recent_investments = base_geral_df[base_geral_df['CONTABILIDADE'] == 'Saída']
recent_investments = recent_investments.sort_values(by='MÊS', ascending=False).reset_index(drop=True)

st.header("Investimentos Recentes")
st.table(recent_investments[['MÊS', 'ESCOLA', 'ITEM', 'CATEGORIA', 'PRESTADOR', 'VALOR']].head(50))
