import pandas as pd
import streamlit as st
import plotly.express as px
import requests

st.set_page_config(page_title="Análise de Vendas", layout="wide")

dark_theme = """
<style>
    body, .css-18e3th9 {
        background-color: #0e1e2f;
        color: #cbd5e1;
    }
    [data-testid="stSidebar"] {
        background-color: #152f4a;
        color: #cbd5e1;
    }
    .css-1d391kg h1, h2, h3, h4, h5 {
        color: #f1f5f9;
        font-weight: 700;
    }
    .stPlotlyChart > div {
        background-color: transparent !important;
        padding: 0 !important;
        border-radius: 0 !important;
    }
    button[kind="primary"] {
        background-color: #1e40af !important;
        color: white !important;
        border-radius: 8px;
        border: none;
    }
    .stTextInput>div>div>input {
        background-color: #1e293b;
        color: #cbd5e1;
        border-radius: 6px;
        border: 1px solid #334155;
    }
    div[data-baseweb="select"] {
        background-color: #1e293b !important;
        color: #cbd5e1 !important;
        border-radius: 6px;
        border: 1px solid #334155;
    }
    .css-18e3th9 h1 {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        color: #3b82f6;
        font-weight: 800;
    }
    div[role="tab"] {
        font-weight: 600;
        color: #cbd5e1 !important;
    }
    div[role="tab"][aria-selected="true"] {
        background-color: #3b82f6 !important;
        color: white !important;
        border-radius: 6px 6px 0 0;
    }
</style>
"""

st.markdown(dark_theme, unsafe_allow_html=True)

def painel_metrica(titulo, valor):
    st.markdown(f"""
    <div style="
        background-color:#1e293b; 
        padding:15px; 
        border-radius:10px; 
        margin-bottom:15px;
        font-weight:600;
        font-size:18px;
        text-align:center;
    ">
        <div>{titulo}</div>
        <div style="font-size:24px; margin-top:5px;">{valor}</div>
    </div>""", unsafe_allow_html=True)

st.title('ANALISE DE VENDAS')

url = 'https://labdados.com/produtos'
regioes = ['Brasil', 'Centro-Oeste', 'Nordeste', 'Norte', 'Sudeste', 'Sul']
st.sidebar.title('Filtros')
regiao = st.sidebar.selectbox('Região', regioes)

if regiao == 'Brasil':
    regiao = ''

todos_anos = st.sidebar.checkbox('Filtrar dados de todos os anos', value=True)

if todos_anos:
    ano = ''
else:
    ano = st.sidebar.slider('Ano', 2020, 2023)

query_string = {'regiao': regiao.lower(), 'ano': ano}
response = requests.get(url, params=query_string)
dados = pd.DataFrame.from_dict(response.json())
dados['Data da Compra'] = pd.to_datetime(dados['Data da Compra'], format='%d/%m/%Y')

filtro_vendedores = st.sidebar.multiselect('Vendedores', dados['Vendedor'].unique())
if filtro_vendedores:
    dados = dados[dados['Vendedor'].isin(filtro_vendedores)]

def formata_numero(valor, prefixo=''):
    for unidade in ['', 'mil']:
        if valor < 1000:
            return f'{prefixo}{valor:.2f}{unidade}'
        valor /= 1000
    return f'{prefixo}{valor:.2f}milhões'

receita_estados = dados.groupby('Local da compra')[['Preço']].sum()
receita_estados = dados.drop_duplicates(subset='Local da compra')[['Local da compra','lat', 'lon']].merge(receita_estados, left_on='Local da compra', right_index=True).sort_values('Preço', ascending=False)

receita_mensal = dados.set_index('Data da Compra').groupby(pd.Grouper(freq='M'))['Preço'].sum().reset_index()
receita_mensal['Ano'] = receita_mensal['Data da Compra'].dt.year
receita_mensal['Mes_num'] = receita_mensal['Data da Compra'].dt.month
receita_mensal['Mes'] = receita_mensal['Data da Compra'].dt.strftime('%b')

receita_categoria = dados.groupby('Categoria do Produto')[['Preço']].sum().sort_values('Preço', ascending=False)

vendas_estados = pd.DataFrame(dados.groupby('Local da compra')['Preço'].count())
vendas_estados = dados.drop_duplicates(subset='Local da compra')[['Local da compra','lat', 'lon']].merge(vendas_estados, left_on='Local da compra', right_index=True).sort_values('Preço', ascending=False)

vendas_mensal = pd.DataFrame(dados.set_index('Data da Compra').groupby(pd.Grouper(freq='M'))['Preço'].count()).reset_index()
vendas_mensal['Ano'] = vendas_mensal['Data da Compra'].dt.year
vendas_mensal['Mes_num'] = vendas_mensal['Data da Compra'].dt.month
vendas_mensal['Mes'] = vendas_mensal['Data da Compra'].dt.strftime('%b')

vendas_categorias = pd.DataFrame(dados.groupby('Categoria do Produto')['Preço'].count().sort_values(ascending=False))
vendedores = pd.DataFrame(dados.groupby('Vendedor')['Preço'].agg(['sum', 'count']))

fig_mapa_receita = px.scatter_geo(receita_estados,
                                  lat='lat',
                                  lon='lon',
                                  scope='south america',
                                  hover_name='Local da compra',
                                  hover_data={'lat': False, 'lon': False},
                                  size='Preço',
                                  template='plotly_dark',
                                  title='Receita por estado')

fig_receita_mensal = px.line(receita_mensal.sort_values('Mes_num'),
                             x='Mes',
                             y='Preço',
                             markers=True,
                             color='Ano',
                             line_dash='Ano',
                             template='plotly_dark',
                             title='Receita mensal')
fig_receita_mensal.update_layout(yaxis_title='Receita')

fig_receita_estado = px.bar(receita_estados.head(),
                            x='Local da compra',
                            y='Preço',
                            text_auto=True,
                            template='plotly_dark',
                            title='Top Estados com maior receita')
fig_receita_estado.update_layout(yaxis_title='Receita')

fig_receita_categoria = px.bar(receita_categoria,
                               text_auto=True,
                               template='plotly_dark',
                               title='Receita por categoria')
fig_receita_categoria.update_layout(yaxis_title='Receita')

fig_mapa_vendas = px.scatter_geo(vendas_estados,
                                 lat='lat',
                                 lon='lon',
                                 scope='south america',
                                 template='plotly_dark',
                                 size='Preço',
                                 hover_name='Local da compra',
                                 hover_data={'lat': False, 'lon': False},
                                 title='Vendas por estado')

fig_vendas_mensal = px.line(vendas_mensal.sort_values('Mes_num'),
                            x='Mes',
                            y='Preço',
                            markers=True,
                            color='Ano',
                            line_dash='Ano',
                            template='plotly_dark',
                            title='Quantidade de vendas mensal')
fig_vendas_mensal.update_layout(yaxis_title='Quantidade de vendas')

fig_vendas_estados = px.bar(vendas_estados.head(),
                           x='Local da compra',
                           y='Preço',
                           text_auto=True,
                           template='plotly_dark',
                           title='Top 5 estados')
fig_vendas_estados.update_layout(yaxis_title='Quantidade de vendas')

fig_vendas_categorias = px.bar(vendas_categorias,
                              text_auto=True,
                              template='plotly_dark',
                              title='Vendas por categoria')
fig_vendas_categorias.update_layout(showlegend=False, yaxis_title='Quantidade de vendas')

aba1, aba2, aba3 = st.tabs(['Receita', 'Quantidade de vendas', 'Vendedores'])

with aba1:
    col1, col2 = st.columns(2)
    with col1:
        painel_metrica('Receita', formata_numero(dados['Preço'].sum(), 'R$'))
        st.plotly_chart(fig_mapa_receita, use_container_width=True)
        st.plotly_chart(fig_receita_estado, use_container_width=True)
    with col2:
        painel_metrica('Quantidade de vendas', formata_numero(dados.shape[0]))
        st.plotly_chart(fig_receita_mensal, use_container_width=True)
        st.plotly_chart(fig_receita_categoria, use_container_width=True)

with aba2:
    col1, col2 = st.columns(2)
    with col1:
        painel_metrica('Receita', formata_numero(dados['Preço'].sum(), 'R$'))
        st.plotly_chart(fig_mapa_vendas, use_container_width=True)
        st.plotly_chart(fig_vendas_estados, use_container_width=True)
    with col2:
        painel_metrica('Quantidade de vendas', formata_numero(dados.shape[0]))
        st.plotly_chart(fig_vendas_mensal, use_container_width=True)
        st.plotly_chart(fig_vendas_categorias, use_container_width=True)

with aba3:
    qtd_vendedores = st.number_input('Quantidade de vendedores', 2, 10, 5)
    col1, col2 = st.columns(2)
    with col1:
        painel_metrica('Receita', formata_numero(dados['Preço'].sum(), 'R$'))
        fig_receita_vendedores = px.bar(vendedores[['sum']].sort_values('sum', ascending=False).head(qtd_vendedores),
                                        x='sum',
                                        y=vendedores[['sum']].sort_values('sum', ascending=False).head(qtd_vendedores).index,
                                        text_auto=True,
                                        template='plotly_dark',
                                        title=f'Top{qtd_vendedores} vendedores (receita)')
        st.plotly_chart(fig_receita_vendedores, use_container_width=True)
    with col2:
        painel_metrica('Quantidade de vendas', formata_numero(dados.shape[0]))
        fig_vendas_vendedores = px.bar(vendedores[['count']].sort_values('count', ascending=False).head(qtd_vendedores),
                                      x='count',
                                      y=vendedores[['count']].sort_values('count', ascending=False).head(qtd_vendedores).index,
                                      text_auto=True,
                                      template='plotly_dark',
                                      title=f'Top{qtd_vendedores} vendedores (quantidade de vendas)')
        st.plotly_chart(fig_vendas_vendedores, use_container_width=True)