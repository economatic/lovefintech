# sheets_connector.py
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from datetime import datetime
import os # Importe o módulo 'os' para manipulação de caminhos de arquivo

# Autenticacao com Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# Constrói o caminho completo para credentials.json, sempre a partir do diretório deste arquivo
# Isso garante que o arquivo seja encontrado, independentemente do diretório de onde o script é executado.
caminho_credenciais = os.path.join(os.path.dirname(os.path.abspath(__file__)), "credentials.json")

# Autentica usando o caminho completo do arquivo de credenciais
creds = ServiceAccountCredentials.from_json_keyfile_name(caminho_credenciais, scope)
client = gspread.authorize(creds)

# Nome da planilha e da aba
NOME_PLANILHA = "Base Lovefintech"
ABA = "Sheet1"

# Acesso à planilha e aba
def get_sheet():
    """Retorna a aba específica da planilha do Google Sheets."""
    sheet = client.open(NOME_PLANILHA).worksheet(ABA)
    return sheet

# Salvar novo dado
def salvar_dado(usuario, data, tipo, categoria, descricao, valor, forma_pgto):
    """
    Salva um novo registro na planilha do Google Sheets.

    Args:
        usuario (str): Nome do usuário.
        data (datetime.date): Data do lançamento.
        tipo (str): Tipo do lançamento (ex: 'Receita', 'Despesa').
        categoria (str): Categoria do lançamento.
        descricao (str): Descrição detalhada.
        valor (float): Valor do lançamento.
        forma_pgto (str): Forma de pagamento.
    """
    sheet = get_sheet()
    nova_linha = [
        str(datetime.now()), # Timestamp do registro
        usuario,
        data.strftime("%Y-%m-%d"), # Formata a data para YYYY-MM-DD
        tipo,
        categoria,
        descricao,
        f"{valor:.2f}", # Formata o valor com 2 casas decimais
        forma_pgto
    ]
    sheet.append_row(nova_linha)

# Carregar dados do Google Sheets
def carregar_dados():
    """
    Carrega todos os dados da planilha e os retorna como um DataFrame do Pandas.
    Converte colunas 'Valor' e 'Data' para seus tipos corretos,
    tratando casos onde a planilha está vazia ou colunas essenciais não existem.
    """
    sheet = get_sheet()
    dados = sheet.get_all_records() # Obtém todos os dados como uma lista de dicionários

    # Se a lista de dicionários estiver vazia (planilha vazia), retorna um DataFrame vazio
    if not dados:
        return pd.DataFrame()

    df = pd.DataFrame(dados) # Converte para DataFrame

    # Verifica se a coluna 'Valor' existe antes de tentar acessá-la
    if 'Valor' not in df.columns:
        # Se a coluna 'Valor' não existir, retorna um DataFrame vazio
        return pd.DataFrame()

    # Converte 'Valor' para numérico, tratando erros (valores não numéricos se tornarão NaN)
    df['Valor'] = pd.to_numeric(df['Valor'], errors='coerce')

    # Verifica se a coluna 'Data' existe antes de tentar acessá-la
    if 'Data' not in df.columns:
        # Se a coluna 'Data' não existir, retorna um DataFrame vazio
        return pd.DataFrame()
        
    # Converte 'Data' para datetime, tratando erros (datas inválidas se tornarão NaT)
    df['Data'] = pd.to_datetime(df['Data'], errors='coerce')
    
    return df
