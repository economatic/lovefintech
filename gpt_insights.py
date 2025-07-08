# gpt_insights.py
import openai
import pandas as pd
from dotenv import load_dotenv, find_dotenv # Importe find_dotenv também
import os

# Carregar variáveis de ambiente do arquivo .env
# Adicione um print para ver se load_dotenv está encontrando o arquivo
dotenv_path = find_dotenv()
print(f"DEBUG: Caminho do .env encontrado por find_dotenv: {dotenv_path}")
load_dotenv(dotenv_path) # Passe o caminho explícito para load_dotenv

# Obtém a chave da API da OpenAI da variável de ambiente
# AQUI ESTÁ A CORREÇÃO CRÍTICA: os.getenv() deve receber o NOME da variável.
api_key = os.getenv("OPENAI_API_KEY")

# Verifica se a chave da API foi carregada corretamente
if not api_key:
    raise ValueError("A chave da API da OpenAI (OPENAI_API_KEY) não foi encontrada nas variáveis de ambiente. Certifique-se de que está definida no seu arquivo .env")

# Crie uma instância do cliente OpenAI, passando a chave diretamente
client = openai.OpenAI(api_key=api_key)

def gerar_insight(df_user):
    """
    Gera insights financeiros baseados nos dados do usuário usando a API da OpenAI.
    """
    if df_user.empty:
        return "Não há dados suficientes para gerar insights. Por favor, adicione alguns lançamentos."

    # Prepara os dados para o prompt
    # Seleciona apenas as colunas relevantes para a IA
    dados_para_ia = df_user[['Data', 'Tipo', 'Categoria', 'Descricao', 'Valor', 'Forma_pgto']].to_string(index=False)

    prompt = f"""
    Com base nos seguintes dados financeiros de um casal (Carol e Marcio), gere um insight inteligente e acionável.
    Analise tendências, padrões de gastos, e o saldo geral. Aponte áreas de melhoria ou pontos positivos.
    Os dados são:

    {dados_para_ia}

    Insight:
    """

    try:
        # Nova forma de chamar a API no openai>=1.0.0
        resposta = client.chat.completions.create(
            model="gpt-3.5-turbo", # Você pode experimentar outros modelos como "gpt-4" se tiver acesso
            messages=[
                {"role": "system", "content": "Você é um assistente financeiro inteligente para casais. Forneça insights concisos e acionáveis."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7, # Controla a criatividade da resposta (0.0 a 1.0)
            max_tokens=200 # Limita o tamanho da resposta em tokens
        )
        return resposta.choices[0].message.content.strip()

    except Exception as e:
        # Retorna uma mensagem de erro mais útil se a IA falhar
        return f"Erro ao gerar insight com IA: {e}. Verifique sua conexão e chave da API."

