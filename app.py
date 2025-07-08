import streamlit as st
import pandas as pd
from datetime import date
import plotly.express as px
from sheets_connector import salvar_dado, carregar_dados
from gpt_insights import gerar_insight
import os # Importe o módulo os para depuração, se necessário

st.set_page_config(page_title="Finanças do casal Carol e Marcio", layout="wide")



st.title("Finanças do casal Carol e Marcio")

# --- Adicionado: Imagem e botões de visualização na Sidebar ---
st.sidebar.image("foto.jpg", use_container_width=True) # Logo com fundo azul e texto branco
st.sidebar.title("Configurações de Visualização")

if 'display_mode' not in st.session_state:
    st.session_state.display_mode = 'desktop'

col_mobile, col_desktop = st.sidebar.columns(2)
with col_mobile:
    if st.button("Mobile View", key="mobile_view_btn"):
        st.session_state.display_mode = 'mobile'
with col_desktop:
    if st.button("Desktop View", key="desktop_view_btn"):
        st.session_state.display_mode = 'desktop'

st.sidebar.info(f"Modo de exibição: **{st.session_state.display_mode.capitalize()}**")

# Sidebar com seleção de usuário (existente)
usuario = st.sidebar.selectbox("Quem está usando?", ["Carol", "Marcio", "Casal"])

# --- Adicionado: Texto "Desenvolvido por Marcio .V" na sidebar ---
st.sidebar.markdown("---") # Adiciona um separador visual
st.sidebar.markdown("Desenvolvido por **Marcio .V**")

# --- Lógica de exibição condicional ---
if st.session_state.display_mode == 'mobile':
    with st.form("form_lancamento_mobile"):
        st.subheader("Adicionar Receita ou Despesa")
        data = st.date_input("Data", value=date.today())
        tipo = st.radio("Tipo", ["Receita", "Despesa"], horizontal=True)
        categoria = st.selectbox("Categoria", ["Alimentação", "Transporte", "Lazer", "Moradia", "Salário", "Outros", "Investimento", "Educação", "Saúde"])
        descricao = st.text_input("Descrição")
        valor = st.number_input("Valor (R$)", min_value=0.0, step=0.01)
        forma_pgto = st.selectbox("Forma de pagamento", ["Pix", "Crédito", "Débito", "Dinheiro", "Transferência"])
        
        enviar = st.form_submit_button("Salvar Lançamento")

        if enviar:
            if usuario == "Casal":
                st.warning("Por favor, selecione 'Carol' ou 'Marcio' para adicionar um lançamento individual.")
            else:
                salvar_dado(usuario, data, tipo, categoria, descricao, valor, forma_pgto)
                st.success("Lançamento salvo com sucesso!")
    st.info("Alterne para 'Desktop View' para ver as análises e gráficos.")

else: # desktop
    with st.form("form_lancamento_desktop"):
        st.subheader("Adicionar Receita ou Despesa")
        col_form1, col_form2 = st.columns(2)
        with col_form1:
            data = st.date_input("Data", value=date.today())
            tipo = st.radio("Tipo", ["Receita", "Despesa"], horizontal=True)
            categoria = st.selectbox("Categoria", ["Alimentação", "Transporte", "Lazer", "Moradia", "Salário", "Outros", "Investimento", "Educação", "Saúde"])
        with col_form2:
            descricao = st.text_input("Descrição")
            valor = st.number_input("Valor (R$)", min_value=0.0, step=0.01)
            forma_pgto = st.selectbox("Forma de pagamento", ["Pix", "Crédito", "Débito", "Dinheiro", "Transferência"])
        
        enviar = st.form_submit_button("Salvar Lançamento")

        if enviar:
            if usuario == "Casal":
                st.warning("Por favor, selecione 'Carol' ou 'Marcio' para adicionar um lançamento individual.")
            else:
                salvar_dado(usuario, data, tipo, categoria, descricao, valor, forma_pgto)
                st.success("Lançamento salvo com sucesso!")

    st.subheader("Resumo Financeiro e Análises")
    df = carregar_dados()

    # Verifica se o DataFrame está vazio OU se a coluna 'Valor' não existe
    if df.empty or 'Valor' not in df.columns:
        st.info("Não há dados financeiros para exibir ou as colunas necessárias estão faltando. Adicione alguns lançamentos para começar a análise!")
    else:
        # Garante que as colunas 'Valor' e 'Data' estão no formato correto
        df['Valor'] = pd.to_numeric(df['Valor'], errors='coerce')
        # CONVERSÃO DA COLUNA 'Data' PARA OBJETOS date, REMOVENDO O COMPONENTE DE TEMPO
        df['Data'] = pd.to_datetime(df['Data'], errors='coerce').dt.date
        
        # Remove linhas com valores nulos que podem ter surgido da conversão
        df.dropna(subset=['Valor', 'Data'], inplace=True)

        # Re-check if df became empty after dropping NaNs
        if df.empty:
            st.info("Não há dados financeiros válidos para exibir após a limpeza. Adicione ou corrija os lançamentos para começar a análise!")
        else:
            # Cria uma coluna 'Mês/Ano' para análises mensais
            # Converte 'Data' para datetime temporariamente para usar dt.to_period, depois para string
            df['Mes/Ano'] = pd.to_datetime(df['Data']).dt.to_period('M').astype(str)

            # --- Abas para Análise Individual e do Casal ---
            tab_individual, tab_casal = st.tabs(["Análise Individual", "Análise do Casal"])

            with tab_individual:
                st.header(f"Análise Individual de {usuario}")
                if usuario == "Casal":
                    st.warning("Selecione 'Carol' ou 'Marcio' na barra lateral para ver a análise individual.")
                else:
                    df_user = df[df['Usuario'] == usuario].copy()

                    if df_user.empty:
                        st.info(f"Não há lançamentos para {usuario}. Adicione dados para ver a análise individual.")
                    else:
                        col1_ind, col2_ind, col3_ind = st.columns(3)
                        with col1_ind:
                            receita_total_ind = df_user[df_user['Tipo'] == 'Receita']['Valor'].sum()
                            st.metric("Receita Total", f"R$ {receita_total_ind:,.2f}")
                        with col2_ind:
                            despesa_total_ind = df_user[df_user['Tipo'] == 'Despesa']['Valor'].sum()
                            st.metric("Despesa Total", f"R$ {despesa_total_ind:,.2f}")
                        with col3_ind:
                            saldo_ind = receita_total_ind - despesa_total_ind
                            st.metric("Saldo Atual", f"R$ {saldo_ind:,.2f}")

                        st.markdown("---")

                        st.subheader("Despesas por Categoria (Individual)")
                        df_despesas_ind = df_user[df_user['Tipo'] == 'Despesa']
                        if not df_despesas_ind.empty:
                            fig_pie_ind = px.pie(df_despesas_ind, values='Valor', names='Categoria', 
                                                 title=f'Despesas de {usuario} por Categoria',
                                                 hole=0.3,
                                                 color_discrete_sequence=px.colors.qualitative.Pastel) # Manter pastel para diversidade
                            st.plotly_chart(fig_pie_ind, use_container_width=True)
                        else:
                            st.info(f"Não há despesas para {usuario} para gerar o gráfico.")

                        st.markdown("---")

                        st.subheader("Evolução do Saldo (Individual)")
                        df_user_sorted = df_user.sort_values("Data")
                        df_user_sorted['Impacto'] = df_user_sorted.apply(lambda row: row['Valor'] if row['Tipo'] == 'Receita' else -row['Valor'], axis=1)
                        df_user_sorted['Saldo Diario'] = df_user_sorted['Impacto'].cumsum()
                        fig_line_ind = px.line(df_user_sorted, x='Data', y='Saldo Diario', 
                                               title=f'Evolução do Saldo de {usuario}',
                                               markers=True,
                                               line_shape='spline',
                                               color_discrete_sequence=["#0041BB"]) # Azul vibrante
                        fig_line_ind.update_xaxes(dtick="D1", tickformat="%d/%m/%Y")
                        st.plotly_chart(fig_line_ind, use_container_width=True)

                        st.markdown("---")

                        st.subheader("Despesas Mensais por Categoria (Individual)")
                        df_despesas_mensal_ind = df_despesas_ind.groupby(['Mes/Ano', 'Categoria'])['Valor'].sum().reset_index()
                        if not df_despesas_mensal_ind.empty:
                            fig_bar_ind = px.bar(df_despesas_mensal_ind, x='Mes/Ano', y='Valor', color='Categoria',
                                                 title=f'Despesas Mensais de {usuario} por Categoria',
                                                 barmode='group',
                                                 color_discrete_sequence=px.colors.qualitative.Set2) # Manter Set2 para diversidade
                            st.plotly_chart(fig_bar_ind, use_container_width=True)
                        else:
                            st.info(f"Não há despesas mensais para {usuario} para gerar o gráfico.")

                        st.markdown("---")

                        st.subheader("Receitas e Despesas Mensais (Individual)")
                        df_mensal_ind = df_user.groupby(['Mes/Ano', 'Tipo'])['Valor'].sum().unstack(fill_value=0).reset_index()
                        if 'Receita' not in df_mensal_ind.columns:
                            df_mensal_ind['Receita'] = 0
                        if 'Despesa' not in df_mensal_ind.columns:
                            df_mensal_ind['Despesa'] = 0
                        
                        df_mensal_ind['Mes/Ano_dt'] = pd.to_datetime(df_mensal_ind['Mes/Ano'])
                        df_mensal_ind = df_mensal_ind.sort_values('Mes/Ano_dt').drop(columns='Mes/Ano_dt')

                        if not df_mensal_ind.empty:
                            df_mensal_ind_long = df_mensal_ind.melt(id_vars=['Mes/Ano'], value_vars=['Receita', 'Despesa'], 
                                                                    var_name='Tipo de Lançamento', value_name='Valor Mensal')
                            
                            fig_mensal_ind = px.bar(df_mensal_ind_long, x='Mes/Ano', y='Valor Mensal', color='Tipo de Lançamento',
                                                    title=f'Receitas e Despesas Mensais de {usuario}',
                                                    barmode='group',
                                                    color_discrete_map={'Receita': '#007BFF', 'Despesa': '#DC3545'}) # Azul e Vermelho
                            st.plotly_chart(fig_mensal_ind, use_container_width=True)
                        else:
                            st.info(f"Não há dados mensais para {usuario} para gerar o gráfico de receitas e despesas.")

                        st.markdown("---")

                        st.subheader("Saldo Acumulado Mensal (Individual)")
                        df_saldo_mensal_ind = df_user.groupby('Mes/Ano').apply(
                            lambda x: x[x['Tipo'] == 'Receita']['Valor'].sum() - x[x['Tipo'] == 'Despesa']['Valor'].sum()
                        ).reset_index(name='Saldo Mensal')
                        df_saldo_mensal_ind['Saldo Acumulado Mensal'] = df_saldo_mensal_ind['Saldo Mensal'].cumsum()
                        if not df_saldo_mensal_ind.empty:
                            fig_saldo_acum_ind = px.line(df_saldo_mensal_ind, x='Mes/Ano', y='Saldo Acumulado Mensal',
                                                         title=f'Evolução do Saldo Acumulado Mensal de {usuario}',
                                                         markers=True,
                                                         line_shape='spline',
                                                         color_discrete_sequence=['#007BFF']) # Azul vibrante
                            st.plotly_chart(fig_saldo_acum_ind, use_container_width=True)
                        else:
                            st.info(f"Não há dados mensais para {usuario} para gerar o gráfico de saldo acumulado.")

                        st.markdown("---")

                        st.subheader("🧠 Insight Inteligente (Individual)")
                        if st.button(f"Gerar insight para {usuario}", key=f"insight_ind_{usuario}"):
                            with st.spinner('Gerando insight...'):
                                insight_ind = gerar_insight(df_user)
                                st.info(insight_ind)

            with tab_casal:
                st.header("Análise Financeira do Casal")

                col1_casal, col2_casal, col3_casal = st.columns(3)
                with col1_casal:
                    receita_total_casal = df[df['Tipo'] == 'Receita']['Valor'].sum()
                    st.metric("Receita Total do Casal", f"R$ {receita_total_casal:,.2f}")
                with col2_casal:
                    despesa_total_casal = df[df['Tipo'] == 'Despesa']['Valor'].sum()
                    st.metric("Despesa Total do Casal", f"R$ {despesa_total_casal:,.2f}")
                with col3_casal:
                    saldo_casal = receita_total_casal - despesa_total_casal
                    st.metric("Saldo Atual do Casal", f"R$ {saldo_casal:,.2f}")

                st.markdown("---")

                st.subheader("Despesas por Categoria (Casal)")
                df_despesas_casal = df[df['Tipo'] == 'Despesa']
                if not df_despesas_casal.empty:
                    fig_pie_casal = px.pie(df_despesas_casal, values='Valor', names='Categoria', 
                                           title='Despesas do Casal por Categoria',
                                           hole=0.3,
                                           color_discrete_sequence=px.colors.qualitative.Pastel) # Manter pastel para diversidade
                    st.plotly_chart(fig_pie_casal, use_container_width=True)
                else:
                    st.info("Não há despesas para o casal para gerar o gráfico.")

                st.markdown("---")

                st.subheader("Evolução do Saldo (Casal)")
                df_casal_sorted = df.sort_values("Data")
                df_casal_sorted['Impacto'] = df_casal_sorted.apply(lambda row: row['Valor'] if row['Tipo'] == 'Receita' else -row['Valor'], axis=1)
                df_casal_sorted['Saldo Diario'] = df_casal_sorted['Impacto'].cumsum()
                fig_line_casal = px.line(df_casal_sorted, x='Data', y='Saldo Diario', 
                                         title='Evolução do Saldo do Casal',
                                         markers=True,
                                         line_shape='spline',
                                         color_discrete_sequence=['#007BFF']) # Azul vibrante
                fig_line_casal.update_xaxes(dtick="D1", tickformat="%d/%m/%Y")
                st.plotly_chart(fig_line_casal, use_container_width=True)

                st.markdown("---")

                st.subheader("Comparativo de Despesas por Usuário")
                df_despesas_por_usuario = df_despesas_casal.groupby('Usuario')['Valor'].sum().reset_index()
                if not df_despesas_por_usuario.empty:
                    fig_bar_user = px.bar(df_despesas_por_usuario, x='Usuario', y='Valor', 
                                          title='Total de Despesas por Usuário',
                                          color='Usuario',
                                          color_discrete_map={'Carol': '#007BFF', 'Marcio': '#DC3545'}) # Azul e Vermelho
                    st.plotly_chart(fig_bar_user, use_container_width=True)
                else:
                    st.info("Não há despesas para comparar entre os usuários.")

                st.markdown("---")

                st.subheader("Receitas e Despesas Mensais (Casal)")
                df_mensal_casal = df.groupby(['Mes/Ano', 'Tipo'])['Valor'].sum().unstack(fill_value=0).reset_index()
                if 'Receita' not in df_mensal_casal.columns:
                    df_mensal_casal['Receita'] = 0
                if 'Despesa' not in df_mensal_casal.columns:
                    df_mensal_casal['Despesa'] = 0

                df_mensal_casal['Mes/Ano_dt'] = pd.to_datetime(df_mensal_casal['Mes/Ano'])
                df_mensal_casal = df_mensal_casal.sort_values('Mes/Ano_dt').drop(columns='Mes/Ano_dt')

                if not df_mensal_casal.empty:
                    df_mensal_casal_long = df_mensal_casal.melt(id_vars=['Mes/Ano'], value_vars=['Receita', 'Despesa'],
                                                                var_name='Tipo de Lançamento', value_name='Valor Mensal')

                    fig_mensal_casal = px.bar(df_mensal_casal_long, x='Mes/Ano', y='Valor Mensal', color='Tipo de Lançamento',
                                              title='Receitas e Despesas Mensais do Casal',
                                              barmode='group',
                                              color_discrete_map={'Receita': '#007BFF', 'Despesa': "#C5C5C5"}) # Azul e Cinza
                    st.plotly_chart(fig_mensal_casal, use_container_width=True)
                else:
                    st.info("Não há dados mensais para o casal para gerar o gráfico de receitas e despesas.")

                st.markdown("---")

                st.subheader("Saldo Acumulado Mensal (Casal)")
                df_saldo_mensal_casal = df.groupby('Mes/Ano').apply(
                    lambda x: x[x['Tipo'] == 'Receita']['Valor'].sum() - x[x['Tipo'] == 'Despesa']['Valor'].sum()
                ).reset_index(name='Saldo Mensal')
                df_saldo_mensal_casal['Saldo Acumulado Mensal'] = df_saldo_mensal_casal['Saldo Mensal'].cumsum()
                if not df_saldo_mensal_casal.empty:
                    fig_saldo_acum_casal = px.line(df_saldo_mensal_casal, x='Mes/Ano', y='Saldo Acumulado Mensal',
                                              title='Evolução do Saldo Acumulado Mensal do Casal',
                                              markers=True,
                                              line_shape='spline',
                                              color_discrete_sequence=['#007BFF']) # Azul vibrante
                    st.plotly_chart(fig_saldo_acum_casal, use_container_width=True)
                else:
                    st.info("Não há dados mensais para o casal para gerar o gráfico de saldo acumulado.")

                st.markdown("---")

                st.subheader("🧠 Insight Inteligente (Casal)")
                if st.button("Gerar insight para o Casal", key="insight_casal"):
                    with st.spinner('Gerando insight...'):
                        insight_casal = gerar_insight(df)
                        st.info(insight_casal)

# --- Novo rodapé para a área de conteúdo principal ---
st.markdown("---") # Separador antes do rodapé
st.markdown("<p style='text-align: center; color: #E0E0E0; font-size: 0.9em;'>Desenvolvido com ❤️ por <strong>Marcio .V</strong></p>", unsafe_allow_html=True)
