import gspread
import pandas as pd
import streamlit as st
import json # Importar o módulo json para lidar com strings JSON

# Carregar credenciais do Google Sheets
# A forma como as credenciais são carregadas depende do ambiente:
# 1. No Streamlit Cloud, elas são carregadas dos segredos (st.secrets).
# 2. Localmente, elas podem ser carregadas de um arquivo .json (para desenvolvimento).

# Tenta carregar as credenciais dos segredos do Streamlit Cloud
# Se estiver no Streamlit Cloud, st.secrets["GOOGLE_SHEETS_CREDENTIALS"] estará disponível.
# Caso contrário, ele tentará carregar de um arquivo local.
try:
    # No Streamlit Cloud, st.secrets é a forma segura de acessar segredos.
    # O segredo é armazenado como uma string JSON, então precisamos fazer o parse.
    google_sheets_credentials = json.loads(st.secrets["GOOGLE_SHEETS_CREDENTIALS"])
    gc = gspread.service_account_from_dict(google_sheets_credentials)
    st.success("Credenciais carregadas do Streamlit Secrets!") # Mensagem de depuração
except Exception as e:
    st.warning(f"Não foi possível carregar credenciais do Streamlit Secrets: {e}") # Mensagem de depuração
    st.warning("Tentando carregar credenciais de 'credentials.json' localmente...")
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
    spreadsheet = gc.open("financas_casal")
    worksheet = spreadsheet.worksheet("dados")
except Exception as e:
    st.error(f"Erro ao abrir a planilha 'financas_casal' ou a aba 'dados': {e}")
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

