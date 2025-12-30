import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import json
import time
from datetime import datetime

# --- 1. CONFIGURAÇÃO ---
st.set_page_config(page_title="Team Sofistas | Analytics", layout="wide", page_icon="🦁")

# --- 2. CSS PREMIUM (LOGIN + DASHBOARD) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;600;800&family=Roboto:wght@300;400;700&display=swap');
    
    html, body, [class*="css"] { font-family: 'Roboto', sans-serif; }
    
    /* --- ESTILO GERAL --- */
    .stApp { 
        background: linear-gradient(135deg, #002b55 0%, #004e92 50%, #F37021 100%);
        background-attachment: fixed;
    }
    
    /* --- LOGIN CARD (Centralizado e Moderno) --- */
    [data-testid="stForm"] {
        background-color: rgba(255, 255, 255, 0.95);
        padding: 50px;
        border-radius: 20px;
        box-shadow: 0 15px 35px rgba(0,0,0,0.3);
        border-top: 5px solid #F37021;
        max-width: 450px;
        margin: 0 auto; /* Centraliza horizontalmente */
    }
    
    /* Título do Login */
    .login-title {
        font-family: 'Montserrat', sans-serif;
        font-weight: 800;
        font-size: 2.5em;
        color: #003366;
        text-align: center;
        margin-bottom: 0;
        letter-spacing: -1px;
    }
    .login-subtitle {
        font-family: 'Montserrat', sans-serif;
        font-size: 1.1em;
        color: #F37021;
        text-align: center;
        margin-bottom: 30px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 2px;
    }
    
    /* Botões */
    div.stButton > button {
        background: linear-gradient(90deg, #003366 0%, #00528b 100%);
        color: white; border: none;
        padding: 0.6rem 1.2rem; border-radius: 8px; 
        font-weight: bold; transition: 0.3s;
        width: 100%; /* Botão full width no login */
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    div.stButton > button:hover { 
        transform: scale(1.02); 
        box-shadow: 0 4px 12px rgba(0, 51, 102, 0.4); 
        background: linear-gradient(90deg, #F37021 0%, #d35400 100%);
    }

    /* Ajustes para quando logado (Fundo mais limpo) */
    .main-container {
        background-color: #f4f7f6; 
        border-radius: 15px; 
        padding: 20px;
        margin-top: 20px;
    }
    
    /* Metrics */
    div.stMetric {
        background-color: white; 
        border: 1px solid #e0e0e0; 
        padding: 15px 20px;
        border-radius: 12px; 
        border-left: 5px solid #F37021;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
</style>
""", unsafe_allow_html=True)

# --- 3. FUNÇÕES DE BACKEND (MANTIDAS) ---

def formatar_nome_visual(nome_cru):
    nome = str(nome_cru).strip().upper()
    if "ADER" in nome: return "Aderência"
    if "CONFORM" in nome: return "Conformidade"
    if "INTERA" in nome: return "Interações"
    if "PONTUAL" in nome: return "Pontualidade"
    if "CSAT" in nome: return "CSAT"
    if "RESOLU" in nome or nome == "IR": return "IR (Resolução)"
    if "TPC" in nome: return "TPC"
    if "QUALIDADE" in nome: return "Qualidade"
    return nome_cru 

def tentar_extrair_data_csv(df):
    colunas_possiveis = ['data', 'date', 'periodo', 'mês', 'mes', 'competencia', 'ref']
    for col in df.columns:
        if any(x in col.lower() for x in colunas_possiveis):
            try:
                data = pd.to_datetime(df[col], dayfirst=True, errors='coerce').dropna().max()
                if pd.notnull(data): return data.strftime("%m/%Y")
            except: continue
    return None

def obter_data_hoje():
    return datetime.now().strftime("%m/%Y")

def salvar_config(data_texto):
    try:
        with open('config.json', 'w') as f:
            json.dump({'periodo': data_texto}, f)
    except Exception as e: st.error(f"Erro config: {e}")

def ler_config():
    if os.path.exists('config.json'):
        with open('config.json', 'r') as f:
            return json.load(f).get('periodo', 'Não informado')
    return "Aguardando atualização"

def limpar_base_dados_completa():
    arquivos = [f for f in os.listdir('.') if f.endswith('.csv')]
    for f in arquivos:
        os.remove(f)

def faxina_arquivos_temporarios():
    arquivos = [f for f in os.listdir('.') if f.endswith('.csv')]
    protegidos = ['historico_consolidado.csv', 'usuarios.csv']
    removidos = 0
    for f in arquivos:
        if f not in protegidos:
            try:
                os.remove(f)
                removidos += 1
            except: pass
    return removidos

def atualizar_historico(df_atual, periodo):
    ARQUIVO_HIST = 'historico_consolidado.csv'
    df_save = df_atual.copy()
    df_save['Periodo'] = str(periodo).strip()
    df_save['Colaborador'] = df_save['Colaborador'].astype(str).str.strip().str.upper()
    
    if os.path.exists(ARQUIVO_HIST):
        try:
            df_hist = pd.read_csv(ARQUIVO_HIST)
            df_hist['Periodo'] = df_hist['Periodo'].astype(str).str.strip()
            df_hist = df_hist[df_hist['Periodo'] != str(periodo).strip()]
            df_final = pd.concat([df_hist, df_save], ignore_index=True)
        except: df_final = df_save
    else: df_final = df_save
    
    cols_order = ['Periodo', 'Colaborador', 'Indicador', '% Atingimento']
    if 'Diamantes' in df_final.columns: cols_order.append('Diamantes')
    if 'Max. Diamantes' in df_final.columns: cols_order.append('Max. Diamantes')
    existing_cols = [c for c in cols_order if c in df_final.columns]
    df_final = df_final[existing_cols]
    df_final.to_csv(ARQUIVO_HIST, index=False)
    return True

def excluir_periodo_historico(periodo_alvo):
    ARQUIVO_HIST = 'historico_consolidado.csv'
    if os.path.exists(ARQUIVO_HIST):
        try:
            df_hist = pd.read_csv(ARQUIVO_HIST)
            df_hist['Periodo'] = df_hist['Periodo'].astype(str).str.strip()
            df_novo = df_hist[df_hist['Periodo'] != str(periodo_alvo).strip()]
            df_novo.to_csv(ARQUIVO_HIST, index=False)
            return True
        except Exception as e:
            st.error(f"Erro ao excluir: {e}")
            return False
    return False

def carregar_historico_completo():
    if os.path.exists('historico_consolidado.csv'):
        try: 
            df = pd.read_csv('historico_consolidado.csv')
            df['Colaborador'] = df['Colaborador'].astype(str).str.strip().str.upper()
            return df
        except: return None
    return None

def listar_periodos_disponiveis():
    df = carregar_historico_completo()
    if df is not None and 'Periodo' in df.columns:
        periodos = df['Periodo'].unique().tolist()
        try: periodos.sort(key=lambda x: datetime.strptime(x, "%m/%Y"), reverse=True)
        except: periodos.sort(reverse=True)
        return periodos
    return []

def salvar_arquivos_padronizados(files):
    arquivos_salvos = []
    for f in files:
        try:
            with open(f.name, "wb") as w: w.write(f.getbuffer())
            arquivos_salvos.append(f.name)
        except Exception as e: st.error(f"Erro salvar {f.name}: {e}")
    return arquivos_salvos

def processar_porcentagem_br(valor):
    if isinstance(valor, str):
        v = valor.replace('%', '').replace(',', '.').strip()
        try: return float(v) / 100
        except: return 0.0
    if isinstance(valor, (int, float)):
        if valor > 1.1: return valor / 100
        return valor
    return 0.0

def ler_csv_inteligente(arquivo_ou_caminho):
    separadores = [',', ';']
    encodings = ['utf-8-sig', 'latin1', 'cp1252']
    for sep in separadores:
        for enc in encodings:
            try:
                if hasattr(arquivo_ou_caminho, 'seek'): arquivo_ou_caminho.seek(0)
                df = pd.read_csv(arquivo_ou_caminho, sep=sep, encoding=enc)
                if len(df.columns) > 1: return df
            except: continue
    return None

def normalizar_nome_indicador(nome_arquivo):
    nome = nome_arquivo.upper()
    if 'ADER' in nome: return 'ADERENCIA'
    if 'CONFORM' in nome: return 'CONFORMIDADE'
    if 'INTERA' in nome: return 'INTERACOES'
    if 'PONTUAL' in nome: return 'PONTUALIDADE'
    if 'CSAT' in nome: return 'CSAT'
    if 'IR' in nome or 'RESOLU' in nome: return 'IR'
    if 'TPC' in nome: return 'TPC'
    return nome.split('.')[0].upper()

def tratar_arquivo_especial(df, nome_arquivo):
    df.columns = [str(c).strip().lower() for c in df.columns]
    col_agente = None
    possiveis_nomes = ['colaborador', 'agente', 'nome', 'employee', 'funcionario', 'operador']
    for c in df.columns:
        if any(p == c or p in c for p in possiveis_nomes):
            col_agente = c
            break
    if not col_agente: return None, "Coluna de Nome não encontrada"
    
    df.rename(columns={col_agente: 'Colaborador'}, inplace=True)
    df['Colaborador'] = df['Colaborador'].astype(str).str.strip().str.upper()

    col_ad = next((c for c in df.columns if 'ader' in c and ('%' in c or 'perc' in c or 'aderencia' in c)), None)
    col_conf = next((c for c in df.columns if 'conform' in c and ('%' in c or 'perc' in c or 'conformidade' in c)), None)

    if col_ad and col_conf:
        lista_retorno = []
        df_ad = df[['Colaborador', col_ad]].copy()
        df_ad['% Atingimento'] = df_ad[col_ad].apply(processar_porcentagem_br)
        df_ad['Indicador'] = 'ADERENCIA'
        lista_retorno.append(df_ad[['Colaborador', 'Indicador', '% Atingimento']])
        
        df_conf = df[['Colaborador', col_conf]].copy()
        df_conf['% Atingimento'] = df_conf[col_conf].apply(processar_porcentagem_br)
        df_conf['Indicador'] = 'CONFORMIDADE'
        lista_retorno.append(df_conf[['Colaborador', 'Indicador', '% Atingimento']])
        return pd.concat(lista_retorno), "Arquivo Combinado"

    col_valor = None
    nome_kpi_limpo = nome_arquivo.split('.')[0].lower()
    possiveis_valores = [nome_kpi_limpo, 'atingimento', 'resultado', 'nota', 'final', 'pontos', 'valor', 'score']
    if 'ader' in nome_kpi_limpo: possiveis_valores.extend(['aderência', 'aderencia'])
    if 'conform' in nome_kpi_limpo: possiveis_valores.extend(['conformidade'])
    if 'intera' in nome_kpi_limpo: possiveis_valores.extend(['interações', 'interacoes'])

    for c in df.columns:
        if c == 'colaborador': continue
        if any(pv in c for pv in possiveis_valores):
            col_valor = c
            break
    if col_valor: df.rename(columns={col_valor: '% Atingimento'}, inplace=True)
    else: return None, f"Coluna de Valor não encontrada"

    for c in df.columns:
        if 'diamantes' in c and 'max' not in c: df.rename(columns={c: 'Diamantes'}, inplace=True)
        if 'max' in c and 'diamantes' in c: df.rename(columns={c: 'Max. Diamantes'}, inplace=True)

    df['% Atingimento'] = df['% Atingimento'].apply(processar_porcentagem_br)
    df['Indicador'] = normalizar_nome_indicador(nome_arquivo)
    
    cols_to_keep = ['Colaborador', 'Indicador', '% Atingimento']
    if 'Diamantes' in df.columns: cols_to_keep.append('Diamantes')
    if 'Max. Diamantes' in df.columns: cols_to_keep.append('Max. Diamantes')
    return df[cols_to_keep], "OK"

def carregar_dados_completo():
    lista_final = []
    arquivos_ignorar = ['usuarios.csv', 'historico_consolidado.csv', 'config.json']
    arquivos = [f for f in os.listdir('.') if f.endswith('.csv') and f.lower() not in arquivos_ignorar]
    for arquivo in arquivos:
        try:
            df_bruto = ler_csv_inteligente(arquivo)
            if df_bruto is not None:
                df_tratado, msg = tratar_arquivo_especial(df_bruto, arquivo)
                if df_tratado is not None:
                    lista_final.append(df_tratado)
        except: pass
    if lista_final: 
        df_concat = pd.concat(lista_final, ignore_index=True)
        agg_rules = {'% Atingimento': 'mean'}
        if 'Diamantes' in df_concat.columns: agg_rules['Diamantes'] = 'sum'
        if 'Max. Diamantes' in df_concat.columns: agg_rules['Max. Diamantes'] = 'sum'
        df_final = df_concat.groupby(['Colaborador', 'Indicador'], as_index=False).agg(agg_rules)
        return df_final
    return None

def carregar_usuarios():
    arquivos = [f for f in os.listdir('.') if f.endswith('.csv') and 'usuario' in f.lower()]
    if arquivos:
        df = ler_csv_inteligente(arquivos[0])
        if df is not None:
            df.columns = df.columns.str.lower()
            col_email = next((c for c in df.columns if 'mail' in c), None)
            col_nome = next((c for c in df.columns if 'colaborador' in c or 'nome' in c), None)
            if col_email and col_nome:
                df.rename(columns={col_email: 'email', col_nome: 'nome'}, inplace=True)
                df['email'] = df['email'].astype(str).str.strip().str.lower()
                df['nome'] = df['nome'].astype(str).str.strip().str.upper()
                return df
    return None

def filtrar_por_usuarios_cadastrados(df_dados, df_users):
    if df_dados is None or df_dados.empty: return df_dados
    if df_users is None or df_users.empty: return df_dados
    lista_vip = df_users['nome'].unique()
    return df_dados[df_dados['Colaborador'].isin(lista_vip)].copy()

def classificar_farol(val):
    if val >= 0.90: return '💎 Excelência' 
    elif val >= 0.80: return '🟢 Meta Batida'
    else: return '🔴 Crítico'

# --- 4. LOGIN RENOVADO ---
if 'logado' not in st.session_state:
    st.session_state.update({'logado': False, 'usuario_nome': '', 'perfil': ''})

if not st.session_state['logado']:
    # Layout de colunas para centralizar o cartão
    c1, c2, c3 = st.columns([1, 2, 1]) # O meio é maior
    
    with c2:
        # Espaçador vertical
        st.markdown("<br><br>", unsafe_allow_html=True)
        
        # Início do formulário que foi estilizado pelo CSS [data-testid="stForm"]
        with st.form("form_login"):
            # Cabeçalho dentro do card
            st.markdown('<p class="login-title">Team Sofistas</p>', unsafe_allow_html=True)
            st.markdown('<p class="login-subtitle">Analytics & Performance</p>', unsafe_allow_html=True)
            
            email = st.text_input("E-mail Corporativo", placeholder="seu.email@brisanet.com.br").strip().lower()
            senha = st.text_input("Senha", type="password", placeholder="Apenas para Gestores")
            
            st.markdown("<br>", unsafe_allow_html=True)
            submit = st.form_submit_button("ACESSAR SISTEMA")
            
            if submit:
                if email in ['gestor', 'admin'] and senha == 'admin':
                    st.session_state.update({'logado': True, 'usuario_nome': 'Gestor', 'perfil': 'admin'})
                    st.rerun()
                else:
                    df_users = carregar_usuarios()
                    if df_users is not None:
                        user = df_users[df_users['email'] == email]
                        if not user.empty:
                            nome_upper = user.iloc[0]['nome']
                            st.session_state.update({'logado': True, 'usuario_nome': nome_upper, 'perfil': 'user'})
                            st.rerun()
                        else: st.error("Acesso negado: E-mail não encontrado na base de usuários.")
                    else: st.error("Erro: Base de usuários não carregada. Contate o suporte.")
    
    # Rodapé simples
    st.markdown('<div style="text-align: center; margin-top: 50px; color: rgba(255,255,255,0.7); font-size: 0.8em;">© 2025 Brisanet | Desenvolvido por Team Sofistas</div>', unsafe_allow_html=True)
    st.stop()

# --- 5. SISTEMA LOGADO (BACKGROUND BRANCO PARA DADOS) ---
# Aqui mudamos o estilo para quem já logou, para facilitar a leitura dos gráficos
st.markdown("""
<style>
    /* Remove o gradiente quando logado e volta para fundo claro */
    .stApp { background: #f4f7f6; }
</style>
""", unsafe_allow_html=True)

# --- 6. SIDEBAR E NAVEGAÇÃO ---
lista_periodos = listar_periodos_disponiveis()
opcoes_periodo = lista_periodos if lista_periodos else ["Nenhum histórico disponível"]

with st.sidebar:
    st.title("🦁 Team Sofistas")
    st.caption("Performance Analytics")
    st.markdown("---")
    
    periodo_selecionado = st.selectbox("📅 Mês de Referência:", opcoes_periodo)
    
    if periodo_selecionado == "Nenhum histórico disponível":
        df_raw = None
        periodo_label = "Aguardando Upload"
    else:
        df_hist_full = carregar_historico_completo()
        if df_hist_full is not None:
            df_raw = df_hist_full[df_hist_full['Periodo'] == periodo_selecionado].copy()
        else: df_raw = None
        periodo_label = periodo_selecionado
    
    df_users_cadastrados = carregar_usuarios()
    df_dados = filtrar_por_usuarios_cadastrados(df_raw, df_users_cadastrados)
    
    if df_dados is not None and not df_dados.empty:
        df_dados['Colaborador'] = df_dados['Colaborador'].str.title()

    st.markdown("---")
    nome_logado = st.session_state['usuario_nome'].title() if st.session_state['usuario_nome'] != 'Gestor' else 'Gestor'
    st.markdown(f"### 👤 {nome_logado.split()[0]}")
    if st.button("Sair"):
        st.session_state.update({'logado': False})
        st.rerun()

perfil = st.session_state['perfil']

if df_dados is None and perfil == 'user':
    st.info(f"👋 Olá, **{nome_logado}**! Os dados de **{periodo_label}** ainda não estão disponíveis ou você não possui métricas neste mês.")
    st.stop()

# --- CONTEÚDO PRINCIPAL (GESTOR OU USER) ---
if perfil == 'admin':
    st.title(f"📊 Painel do Gestor")
    
    tabs = st.tabs(["🚦 Visão Geral", "⏳ Evolução", "🔍 Indicadores", "💰 Comissões", "📋 Tabela Detalhada", "⚙️ Admin"])
    
    with tabs[0]: 
        if df_dados is not None and not df_dados.empty:
            st.markdown(f"### Resumo de Saúde: **{periodo_label}**")
            df_media_pessoas = df_dados.groupby('Colaborador')['% Atingimento'].mean().reset_index()
            
            qtd_verde = len(df_media_pessoas[df_media_pessoas['% Atingimento'] >= 0.90]) 
            qtd_amarelo = len(df_media_pessoas[(df_media_pessoas['% Atingimento'] >= 0.80) & (df_media_pessoas['% Atingimento'] < 0.90)]) 
            qtd_vermelho = len(df_media_pessoas[df_media_pessoas['% Atingimento'] < 0.80]) 
            
            c1, c2, c3 = st.columns(3)
            c1.metric("💎 Excelência", f"{qtd_verde}", delta=">=90%")
            c2.metric("🟢 Meta Batida", f"{qtd_amarelo}", delta="80-90%", delta_color="off")
            c3.metric("🔴 Crítico", f"{qtd_vermelho}", delta="<80%", delta_color="inverse")
            
            st.markdown("---")
            st.subheader("📋 Atenção Prioritária")
            df_atencao = df_media_pessoas[df_media_pessoas['% Atingimento'] < 0.80].sort_values(by='% Atingimento')
            
            if not df_atencao.empty:
                lista_detalhada = []
                for colab in df_atencao['Colaborador']:
                    dados_pessoa = df_dados[df_dados['Colaborador'] == colab]
                    media_pessoa = dados_pessoa['% Atingimento'].mean()
                    pior_kpi_row = dados_pessoa.loc[dados_pessoa['% Atingimento'].idxmin()]
                    lista_detalhada.append({
                        'Colaborador': colab,
                        'Média Geral': media_pessoa,
                        'Pior KPI': f"{formatar_nome_visual(pior_kpi_row['Indicador'])} ({pior_kpi_row['% Atingimento']:.1%})"
                    })
                st.dataframe(pd.DataFrame(lista_detalhada).style.format({'Média Geral': '{:.1%}'}), use_container_width=True)
            else: st.success("🎉 Equipe performando bem! Ninguém abaixo de 80%.")

    with tabs[1]:
        st.markdown("### ⏳ Evolução Temporal")
        df_hist = carregar_historico_completo()
        df_hist = filtrar_por_usuarios_cadastrados(df_hist, df_users_cadastrados)
        if df_hist is not None:
            df_hist['Colaborador'] = df_hist['Colaborador'].str.title()
            colab_sel = st.selectbox("Selecione:", sorted(df_hist['Colaborador'].unique()))
            df_user_hist = df_hist[df_hist['Colaborador'] == colab_sel]
            fig = px.line(df_user_hist, x='Periodo', y='% Atingimento', color='Indicador', markers=True)
            st.plotly_chart(fig, use_container_width=True)

    with tabs[2]:
        st.markdown("### 🔍 Detalhe por Indicador")
        if df_dados is not None:
            df_dados['Status'] = df_dados['% Atingimento'].apply(classificar_farol)
            fig = px.bar(df_dados, x='Indicador', y='% Atingimento', color='Status', 
                         color_discrete_map={'💎 Excelência': '#003366', '🟢 Meta Batida': '#2ecc71', '🔴 Crítico': '#e74c3c'},
                         hover_data=['Colaborador'])
            st.plotly_chart(fig, use_container_width=True)

    with tabs[3]:
        st.markdown(f"### 💰 Relatório de Comissões")
        if df_dados is not None:
            st.info("Regra: R$ 0,50/Diamante. Trava: Conformidade >= 92%.")
            lista_pgto = []
            df_upper = df_dados.copy()
            df_upper['Colaborador_Key'] = df_upper['Colaborador'].str.upper()
            
            for colab_key in df_upper['Colaborador_Key'].unique():
                d_user = df_upper[df_upper['Colaborador_Key'] == colab_key]
                total_dia = d_user['Diamantes'].sum() if 'Diamantes' in d_user.columns else 0
                
                # Checa Conformidade
                row_conf = d_user[d_user['Indicador'] == 'CONFORMIDADE']
                conf = row_conf.iloc[0]['% Atingimento'] if not row_conf.empty else 0.0
                
                desconto = 0
                if conf < 0.92:
                    row_pont = d_user[d_user['Indicador'] == 'PONTUALIDADE']
                    desconto = row_pont.iloc[0]['Diamantes'] if not row_pont.empty and 'Diamantes' in row_pont.columns else 0
                
                final_dia = total_dia - desconto
                pgto = final_dia * 0.50
                
                lista_pgto.append({
                    "Colaborador": colab_key.title(),
                    "Conformidade": conf,
                    "Total Diamantes": int(total_dia),
                    "Desconto": int(desconto),
                    "A Pagar (R$)": pgto
                })
            
            df_pgto = pd.DataFrame(lista_pgto)
            st.dataframe(df_pgto.style.format({"Conformidade": "{:.1%}", "A Pagar (R$)": "R$ {:.2f}"}), use_container_width=True)

    with tabs[4]:
        st.markdown("### 📋 Dados Brutos")
        if df_dados is not None:
            st.dataframe(df_dados, use_container_width=True)

    with tabs[5]:
        st.markdown("### ⚙️ Administração")
        subtabs = st.tabs(["📤 Upload", "🗑️ Limpeza", "💾 Backup"])
        
        with subtabs[0]:
            data_sugestao = obter_data_hoje()
            nova_data = st.text_input("Mês/Ano Ref:", value=data_sugestao)
            c1, c2 = st.columns(2)
            with c1: st.file_uploader("usuarios.csv", key="u")
            with c2: 
                up_k = st.file_uploader("Métricas (CSVs)", accept_multiple_files=True, key="k")
                if up_k and st.button("Salvar"):
                    faxina_arquivos_temporarios()
                    salvar_arquivos_padronizados(up_k)
                    salvar_config(nova_data)
                    df_novo = carregar_dados_completo()
                    df_users = carregar_usuarios()
                    df_final = filtrar_por_usuarios_cadastrados(df_novo, df_users)
                    if not df_final.empty:
                        atualizar_historico(df_final, nova_data)
                        st.success("Atualizado!")
                        time.sleep(1)
                        st.rerun()
                    else: st.error("Erro: Sem dados após filtro.")

        with subtabs[1]:
            df_h = carregar_historico_completo()
            if df_h is not None:
                for per in df_h['Periodo'].unique():
                    c1, c2 = st.columns([3, 1])
                    c1.write(f"📅 {per}")
                    if c2.button(f"Apagar {per}"):
                        excluir_periodo_historico(per)
                        st.rerun()

        with subtabs[2]:
            if os.path.exists('historico_consolidado.csv'):
                with open('historico_consolidado.csv', 'rb') as f:
                    st.download_button("Baixar Backup", f, "backup.csv", "text/csv")
            if st.button("Resetar Tudo"):
                limpar_base_dados_completa()
                st.rerun()

# --- VISÃO OPERADOR ---
else:
    st.markdown(f"## 🚀 Olá, **{nome_logado.split()[0]}**!")
    st.caption(f"📅 Referência: **{periodo_label}**")
    
    meus_dados = df_dados[df_dados['Colaborador'] == nome_logado].copy()
    
    if not meus_dados.empty:
        # Gamificação
        if 'Diamantes' in meus_dados.columns:
            total_dia = meus_dados['Diamantes'].sum()
            total_max = meus_dados['Max. Diamantes'].sum()
            perc = (total_dia / total_max) if total_max > 0 else 0
            st.markdown("### 💎 Gamificação")
            c1, c2 = st.columns([3, 1])
            c1.progress(perc)
            c2.write(f"**{int(total_dia)} / {int(total_max)}**")
            
            # Calculo Financeiro Individual
            df_conf = meus_dados[meus_dados['Indicador'] == 'CONFORMIDADE']
            conf = df_conf.iloc[0]['% Atingimento'] if not df_conf.empty else 0.0
            
            desc = 0
            obs = ""
            if conf < 0.92:
                df_pont = meus_dados[meus_dados['Indicador'] == 'PONTUALIDADE']
                desc = df_pont.iloc[0]['Diamantes'] if not df_pont.empty else 0
                obs = "(Penalidade: Pontualidade)"
            
            val = (total_dia - desc) * 0.50
            
            st.markdown("#### 💰 Extrato")
            c1, c2, c3 = st.columns(3)
            c1.metric("Diamantes Válidos", int(total_dia - desc), obs)
            c2.metric("Valor Unit.", "R$ 0,50")
            c3.metric("A Receber", f"R$ {val:.2f}")
            st.divider()

        # Cards KPIs
        cols = st.columns(len(meus_dados))
        for i, (_, row) in enumerate(meus_dados.iterrows()):
            val = row['% Atingimento']
            label = formatar_nome_visual(row['Indicador'])
            delta_msg = "Meta 80%"
            color = "normal"
            if val >= 0.90: delta_msg = "💎 Excelência"
            elif val >= 0.80: delta_msg = "✅ Na Meta"
            else: 
                delta_msg = "🔻 Abaixo"
                color = "inverse"
            
            with cols[i]:
                st.metric(label, f"{val:.1%}", delta_msg, delta_color=color)
        
        st.markdown("---")
        # Gráfico Comparativo
        media_equipe = df_dados.groupby('Indicador')['% Atingimento'].mean().reset_index()
        media_equipe.rename(columns={'% Atingimento': 'Média Equipe'}, inplace=True)
        df_comp = pd.merge(meus_dados, media_equipe, on='Indicador')
        df_comp['Indicador'] = df_comp['Indicador'].apply(formatar_nome_visual)
        df_melt = df_comp.melt(id_vars=['Indicador'], value_vars=['% Atingimento', 'Média Equipe'], var_name='Tipo', value_name='Resultado')
        
        fig = px.bar(df_melt, x='Indicador', y='Resultado', color='Tipo', barmode='group',
                     color_discrete_map={'% Atingimento': '#F37021', 'Média Equipe': '#003366'})
        fig.add_hline(y=0.8, line_dash="dash", line_color="green", annotation_text="Meta 80%")
        st.plotly_chart(fig, use_container_width=True)
