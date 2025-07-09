import gspread
import pandas as pd
import streamlit as st
# O módulo json não é mais estritamente necessário aqui se st.secrets já entrega um dict ou se não estamos parseando string
# import json

# Carregar credenciais do Google Sheets
# Tenta carregar as credenciais dos segredos do Streamlit (st.secrets) primeiro
try:
    # Acessa as credenciais do TOML, usando a chave correta [google_credentials]
    gc = gspread.service_account_from_dict(st.secrets["google_credentials"])
    st.success("Credenciais carregadas do Streamlit Secrets!") # Mensagem de depuração
except Exception as e:
    st.warning(f"Não foi possível carregar credenciais do Streamlit Secrets: {e}") # Mensagem de depuração
    st.info("Tentando carregar credenciais de 'credentials.json' localmente...")
    try:
        # Para desenvolvimento local, carregue do arquivo credentials.json
        # Certifique-se de que credentials.json está no .gitignore!
        gc = gspread.service_account(filename='credentials.json')
        st.success("Credenciais carregadas de 'credentials.json' localmente!") # Mensagem de depuração
    except Exception as e_local:
        st.error(f"Erro ao carregar credenciais de 'credentials.json' localmente: {e_local}")
        st.stop() # Interrompe a execução do app se as credenciais não puderem ser carregadas

# Abra a planilha pelo nome
try:
    # Certifique-se que o nome da planilha e aba estão corretos
    spreadsheet = gc.open("Base Lovefintech") # O nome da sua planilha
    worksheet = spreadsheet.worksheet("Sheet1") # O nome da sua aba
except Exception as e:
    st.error(f"Erro ao abrir a planilha 'Base Lovefintech' ou a aba 'Sheet1': {e}") # Mensagem de erro atualizada para corresponder aos nomes da planilha e aba
    st.stop() # Interrompe a execução do app se a planilha não puder ser acessada

def salvar_dado(usuario, data, tipo, categoria, descricao, valor, forma_pgto):
    """
    Salva um novo lançamento financeiro na planilha Google Sheets.
    """
    try:
        # Formata a data para string para salvar na planilha
        data_str = data.strftime("%Y-%m-%d")
        
        # Adiciona uma nova linha com os dados
        worksheet.append_row([usuario, data_str, tipo, categoria, descricao, valor, forma_pgto])
    except Exception as e:
        st.error(f"Erro ao salvar dado na planilha: {e}")

@st.cache_data(ttl=600) # Cache os dados por 10 minutos
def carregar_dados():
    """
    Carrega todos os dados da planilha Google Sheets.
    """
    try:
        # Obtém todos os registros como uma lista de dicionários
        data = worksheet.get_all_records()
        # Converte para DataFrame do pandas
        df = pd.DataFrame(data)
        return df
    except Exception as e:
        st.error(f"Erro ao carregar dados da planilha: {e}")
        return pd.DataFrame() # Retorna um DataFrame vazio em caso de erro