import pandas as pd
import streamlit as st
import requests
import time



st.title('Dados Brutos')



@st.cache_data
def carregar_dados():
    url = 'https://labdados.com/produtos'
    response = requests.get(url)
    dados = pd.DataFrame.from_dict(response.json())

    # Converter data corretamente
    dados['Data da Compra'] = pd.to_datetime(
        dados['Data da Compra'],
        format='%d/%m/%Y'
    ).dt.date

    return dados

def converte_csv (df):
    return df.to_csv(index=False).encode('utf-8')
def mensagem_sucesso():
    sucesso = st.success("Arquivo baixado com sucesso!", icon = "✅")
    time.sleep(5)
    sucesso.empty()

dados = carregar_dados()


with st.expander('Colunas'):
    colunas = st.multiselect(
        'Selecione as colunas',
        list(dados.columns),
        list(dados.columns)
    )

st.sidebar.title('Filtros')

with st.sidebar.expander('Nome do produto'):
    produtos = st.multiselect(
        'Selecione os produtos',
        dados['Produto'].unique(),
        dados['Produto'].unique()
    )

with st.sidebar.expander('Categoria do produto'):
    categoria = st.multiselect(
        'Selecione as categorias',
        dados['Categoria do Produto'].unique(),
        dados['Categoria do Produto'].unique()
    )

with st.sidebar.expander('Preço do produto'):
    preco = st.slider('Selecione o preço', 0, 5000, (0, 5000))

with st.sidebar.expander('Frete da venda'):
    frete = st.slider('Frete', 0, 250, (0, 250))

with st.sidebar.expander('Data da compra'):
    data_compra = st.date_input(
        'Selecione a data',
        (dados['Data da Compra'].min(), dados['Data da Compra'].max())
    )

with st.sidebar.expander('Vendedor'):
    vendedores = st.multiselect(
        'Selecione os vendedores',
        dados['Vendedor'].unique(),
        dados['Vendedor'].unique()
    )

with st.sidebar.expander('Local da compra'):
    local_compra = st.multiselect(
        'Selecione o local da compra',
        dados['Local da compra'].unique(),
        dados['Local da compra'].unique()
    )

with st.sidebar.expander('Avaliação da compra'):
    avaliacao = st.slider('Selecione a avaliação da compra', 1, 5, (1, 5))

with st.sidebar.expander('Tipo de pagamento'):
    tipo_pagamento = st.multiselect(
        'Selecione o tipo de pagamento',
        dados['Tipo de pagamento'].unique(),
        dados['Tipo de pagamento'].unique()
    )

with st.sidebar.expander('Quantidade de parcelas'):
    qtd_parcelas = st.slider(
        'Selecione a quantidade de parcelas',
        1, 24, (1, 24)
    )


filtro = pd.Series(True, index=dados.index)

if produtos:
    filtro &= dados["Produto"].isin(produtos)

if categoria:
    filtro &= dados["Categoria do Produto"].isin(categoria)

filtro &= dados["Preço"].between(preco[0], preco[1])
filtro &= dados["Frete"].between(frete[0], frete[1])
filtro &= dados["Data da Compra"].between(data_compra[0], data_compra[1])

if vendedores:
    filtro &= dados["Vendedor"].isin(vendedores)

if local_compra:
    filtro &= dados["Local da compra"].isin(local_compra)

if tipo_pagamento:
    filtro &= dados["Tipo de pagamento"].isin(tipo_pagamento)

filtro &= dados["Avaliação da compra"].between(avaliacao[0], avaliacao[1])
filtro &= dados["Quantidade de parcelas"].between(qtd_parcelas[0], qtd_parcelas[1])

dados_filtrados = dados[filtro]


dados_filtrados = dados_filtrados[colunas]


st.dataframe(dados_filtrados, use_container_width=True)

st.markdown(
    f'A tabela possui :blue[{dados_filtrados.shape[0]}] linhas e '
    f':blue[{dados_filtrados.shape[1]}] colunas'
)

st.markdown('Escreva nome do arquivo')
col1, col2 = st.columns(2)

with col1:
  nome_arquivo = st.text_input('', label_visibility='collapsed', value = 'dados')
  nome_arquivo += '.csv'
with col2:
    st.download_button('Download em csv', data = converte_csv(dados_filtrados), file_name = nome_arquivo, mime = 'text/csv', on_click = mensagem_sucesso)