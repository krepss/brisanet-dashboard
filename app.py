import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import json
import time
from datetime import datetime
import unicodedata # NOVO: Para corrigir acentos (Bárbara -> BARBARA)

# --- CONFIGURAÇÃO DA LOGO ---
LOGO_FILE = "logo.ico"

# --- SENHA DO GESTOR ---
SENHA_ADMIN = "admin123"
USUARIOS_ADMIN = ['gestor', 'admin']

# --- DICAS AUTOMÁTICAS (SMART COACH) ---
DICAS_KPI = {
    "ADERENCIA": "Cumpra rigorosamente os horários de log in, log out e pausas da sua escala.",
    "CONFORMIDADE": "Aqui se trata do tempo de fila, não estrapole nas pausas e tire pausas desnecessárias.",
    "INTERACOES": "Evite tempos de silêncio (mudo) prolongados. Mantenha o cliente informado enquanto analisa.",
    "PONTUALIDADE": "Programe-se para estar logado e pronto para atender no minuto exato do início de cada pausa.",
    "CSAT": "Demonstre empatia e gentileza. A nota do cliente reflete como ele se sentiu durante o atendimento.",
    "IR": "Garanta que o serviço voltou a funcionar. Faça todos os testes finais e confirme a solução com o cliente antes de encerrar.",
    "TPC": "Otimize a tabulação no tempo certo, aqui é fácil recuperar.",
    "TAM": "Assuma o comando da ligação. Seja objetivo nas perguntas e guie o cliente para a solução de forma ágil."
}

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
try:
    st.set_page_config(page_title="Team Sofistas | Analytics", layout="wide", page_icon=LOGO_FILE)
except:
    st.set_page_config(page_title="Team Sofistas | Analytics", layout="wide", page_icon="🦁")

# --- 2. CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;600;800&family=Roboto:wght@300;400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Roboto', sans-serif; }
    .stApp { background-color: #F4F7F6 !important; }
    
    /* SIDEBAR */
    [data-testid="stSidebar"] {
        background-color: #002b55 !important;
        background-image: linear-gradient(180deg, #002b55 0%, #004e92 100%) !important;
    }
    [data-testid="stSidebar"] * { color: #FFFFFF !important; }
    [data-testid="stSidebar"] input { background-color: #FFFFFF !important; color: #000000 !important; }
    [data-testid="stSidebar"] div[data-baseweb="select"] > div { background-color: #FFFFFF !important; color: #000000 !important; }
    [data-testid="stSidebar"] div[data-baseweb="select"] span { color: #000000 !important; }
    
    h1, h2, h3, h4, h5, h6 { color: #003366 !important; font-family: 'Montserrat', sans-serif !important; }
    p, li, div { color: #333333; }
    
    /* CARDS */
    [data-testid="stForm"], div.stMetric, .vacation-card, .insight-box, .badge-card {
        background-color: #FFFFFF !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
        border-radius: 10px;
    }
    div.stMetric { border: 1px solid #e0e0e0; border-left: 5px solid #F37021; padding: 10px 15px !important; }
    div.stMetric label { color: #666 !important; font-size: 14px !important; }
    div.stMetric div[data-testid="stMetricValue"] { color: #003366 !important; font-size: 26px !important; font-weight: 700; }
    div.stMetric div[data-testid="stMetricDelta"] { font-size: 13px !important; }
    [data-testid="stDataFrame"] { background-color: #FFFFFF; }
    
    div.stButton > button {
        background-color: #003366 !important; color: #FFFFFF !important; border-radius: 8px; font-weight: bold; border: none;
    }
    div.stButton > button p { color: #FFFFFF !important; }
    div.stButton > button:hover { background-color: #F37021 !important; }
    
    button[data-baseweb="tab"] { background-color: transparent !important; color: #666 !important; }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #003366 !important; border-top: 3px solid #F37021 !important; font-weight: bold;
    }
    
    .vacation-card { border-left: 6px solid #00bcd4; padding: 25px; text-align: center; margin-top: 20px; }
    .vacation-title { font-size: 1.3em !important; font-weight: 600; color: #555 !important; }
    .vacation-date { font-size: 2.5em; font-weight: 800; color: #00838f !important; margin: 15px 0; text-transform: uppercase; }
    
    .update-badge {
        background-color: #e3f2fd; color: #0d47a1; padding: 5px 10px; 
        border-radius: 15px; font-size: 0.85em; font-weight: bold; border: 1px solid #bbdefb;
    }
    
    .insight-box {
        background-color: #fff8e1 !important;
        border-left: 5px solid #ffc107 !important;
        padding: 15px;
        margin-bottom: 20px;
    }
    .insight-title { font-weight: bold; color: #d35400; font-size: 1.1em; display: flex; align-items: center; gap: 8px; }
    .insight-text { font-size: 0.95em; margin-top: 5px; color: #555; }

    .dev-footer { text-align: center; margin-top: 30px; font-size: 0.8em; color: #999 !important; }
    .login-title { font-weight: 800; font-size: 2.5em; color: #003366 !important; text-align: center; }
    .login-subtitle { font-size: 1.2em; color: #F37021 !important; text-align: center; margin-bottom: 20px; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

# --- 3. FUNÇÕES DE BACKEND ---

def formatar_nome_visual(nome_cru):
    nome = str(nome_cru).strip().upper()
    if "ADER" in nome: return "Aderência"
    if "CONFORM" in nome: return "Conformidade"
    if "INTERA" in nome: return "Interações"
    if "PONTUAL" in nome: return "Pontualidade"
    if "CSAT" in nome: return "CSAT"
    if "RESOLU" in nome or nome == "IR": return "IR (Resolução)"
    if "TPC" in nome: return "TPC"
    if "TAM" in nome: return "Resultado Geral (TAM)"
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

def obter_data_hoje(): return datetime.now().strftime("%m/%Y")

def obter_data_atualizacao():
    arquivo = 'historico_consolidado.csv'
    if os.path.exists(arquivo):
        timestamp = os.path.getmtime(arquivo)
        return datetime.fromtimestamp(timestamp).strftime("%d/%m/%Y às %H:%M")
    return datetime.now().strftime("%d/%m/%Y")

def salvar_config(data_texto):
    try:
        with open('config.json', 'w') as f: json.dump({'periodo': data_texto}, f)
    except: pass
def ler_config():
    if os.path.exists('config.json'):
        with open('config.json', 'r') as f: return json.load(f).get('periodo', 'Não informado')
    return "Aguardando atualização"
def limpar_base_dados_completa():
    arquivos = [f for f in os.listdir('.') if f.endswith('.csv')]
    for f in arquivos: os.remove(f)
def faxina_arquivos_temporarios():
    arquivos = [f for f in os.listdir('.') if f.endswith('.csv')]
    protegidos = ['historico_consolidado.csv', 'usuarios.csv', 'config.json', LOGO_FILE]
    for f in arquivos:
        if f not in protegidos:
            try: os.remove(f)
            except: pass
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
def excluir_periodo_historico(periodo_alvo):
    ARQUIVO_HIST = 'historico_consolidado.csv'
    if os.path.exists(ARQUIVO_HIST):
        try:
            df_hist = pd.read_csv(ARQUIVO_HIST)
            df_hist['Periodo'] = df_hist['Periodo'].astype(str).str.strip()
            df_novo = df_hist[df_hist['Periodo'] != str(periodo_alvo).strip()]
            df_novo.to_csv(ARQUIVO_HIST, index=False)
            return True
        except: return False
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
    for f in files:
        with open(f.name, "wb") as w: w.write(f.getbuffer())
    return True

# --- CORREÇÃO DE PORCENTAGEM INTELIGENTE ---
def processar_porcentagem_br(valor):
    if pd.isna(valor) or valor == '': return 0.0
    if isinstance(valor, str):
        v = valor.replace('%', '').replace(',', '.').strip()
        try: 
            num = float(v)
            if num > 1.05: return num / 100.0
            return num
        except: return 0.0
    if isinstance(valor, (int, float)):
        if valor > 1.05: return valor / 100.0
        return valor
    return 0.0

def ler_csv_inteligente(arquivo_ou_caminho):
    separadores = [',', ';']
    encodings = ['utf-8-sig', 'latin1', 'cp1252']
    for sep in separadores:
        for enc in encodings:
            try:
                if hasattr(arquivo_ou_caminho, 'seek'): arquivo_ou_caminho.seek(0)
                df = pd.read_csv(arquivo_ou_caminho, sep=sep, encoding=enc, dtype=str)
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
    if 'TAM' in nome: return 'TAM'
    return nome.split('.')[0].upper()

# --- NORMALIZAR NOMES (Correção de Acentos) ---
def normalizar_chave(texto):
    if pd.isna(texto): return ""
    texto = str(texto).strip().upper()
    nfkd = unicodedata.normalize('NFKD', texto)
    texto_sem_acento = u"".join([c for c in nfkd if not unicodedata.combining(c)])
    return " ".join(texto_sem_acento.split())

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
    df['Colaborador'] = df['Colaborador'].apply(normalizar_chave)
    
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
        return pd.concat(lista_retorno), f"Combinado"
    
    col_valor = None
    nome_kpi_limpo = nome_arquivo.split('.')[0].lower()
    prioridades = ['% atingimento', 'atingimento', 'resultado', 'nota final', 'score']
    secundarios = [nome_kpi_limpo, 'nota', 'valor', 'pontos', 'final']
    if 'ader' in nome_kpi_limpo: secundarios.append('aderência')
    if 'conform' in nome_kpi_limpo: secundarios.append('conformidade')
    
    for p in prioridades:
        for c in df.columns:
            if p in c: 
                col_valor = c
                break
        if col_valor: break
    if not col_valor:
        for s in secundarios:
            for c in df.columns:
                if s in c and c != 'colaborador':
                    col_valor = c
                    break
            if col_valor: break
            
    if col_valor: df.rename(columns={col_valor: '% Atingimento'}, inplace=True)
    else: return None, f"Coluna de Valor não encontrada"
    
    for c in df.columns:
        if 'diamantes' in c and 'max' not in c: df.rename(columns={c: 'Diamantes'}, inplace=True)
        if 'max' in c and 'diamantes' in c: df.rename(columns={c: 'Max. Diamantes'}, inplace=True)
    
    df['% Atingimento'] = df['% Atingimento'].apply(processar_porcentagem_br)
    if 'Diamantes' in df.columns: df['Diamantes'] = pd.to_numeric(df['Diamantes'], errors='coerce').fillna(0)
    if 'Max. Diamantes' in df.columns: df['Max. Diamantes'] = pd.to_numeric(df['Max. Diamantes'], errors='coerce').fillna(0)
    df['Indicador'] = normalizar_nome_indicador(nome_arquivo)
    cols_to_keep = ['Colaborador', 'Indicador', '% Atingimento']
    if 'Diamantes' in df.columns: cols_to_keep.append('Diamantes')
    if 'Max. Diamantes' in df.columns: cols_to_keep.append('Max. Diamantes')
    return df[cols_to_keep], "OK"

def classificar_farol(val):
    if val >= 0.90: return '💎 Excelência' 
    elif val >= 0.80: return '🟢 Meta Batida'
    else: return '🔴 Crítico'

def carregar_dados_completo_debug():
    lista_final = []
    log_debug = []
    arquivos_ignorar = ['usuarios.csv', 'historico_consolidado.csv', 'config.json', LOGO_FILE]
    arquivos = [f for f in os.listdir('.') if f.endswith('.csv') and f.lower() not in arquivos_ignorar]
    for arquivo in arquivos:
        try:
            df_bruto = ler_csv_inteligente(arquivo)
            if df_bruto is not None:
                df_tratado, msg = tratar_arquivo_especial(df_bruto, arquivo)
                log_debug.append({"Arquivo": arquivo, "Status": "OK" if df_tratado is not None else "Erro", "Detalhe": msg})
                if df_tratado is not None: lista_final.append(df_tratado)
            else: log_debug.append({"Arquivo": arquivo, "Status": "Erro", "Detalhe": "Não conseguiu ler CSV"})
        except Exception as e: log_debug.append({"Arquivo": arquivo, "Status": "Erro Crítico", "Detalhe": str(e)})
            
    df_final = None
    if lista_final: 
        df_concat = pd.concat(lista_final, ignore_index=True)
        agg_rules = {'% Atingimento': 'mean'}
        if 'Diamantes' in df_concat.columns: agg_rules['Diamantes'] = 'sum'
        if 'Max. Diamantes' in df_concat.columns: agg_rules['Max. Diamantes'] = 'sum'
        df_final = df_concat.groupby(['Colaborador', 'Indicador'], as_index=False).agg(agg_rules)
    return df_final, pd.DataFrame(log_debug)

def carregar_dados_completo():
    df, _ = carregar_dados_completo_debug()
    return df

def carregar_usuarios():
    arquivos = [f for f in os.listdir('.') if f.endswith('.csv') and 'usuario' in f.lower()]
    if arquivos:
        df = ler_csv_inteligente(arquivos[0])
        if df is not None:
            df.columns = df.columns.str.lower()
            col_email = next((c for c in df.columns if 'mail' in c), None)
            col_nome = next((c for c in df.columns if 'colaborador' in c or 'nome' in c), None)
            col_ferias = next((c for c in df.columns if 'ferias' in c or 'férias' in c), None)
            if col_email and col_nome:
                rename_map = {col_email: 'email', col_nome: 'nome'}
                if col_ferias: rename_map[col_ferias] = 'ferias'
                df.rename(columns=rename_map, inplace=True)
                df['email'] = df['email'].astype(str).str.strip().str.lower()
                df['nome'] = df['nome'].apply(normalizar_chave)
                if 'ferias' not in df.columns: df['ferias'] = "Não informado"
                else: df['ferias'] = df['ferias'].astype(str).replace('nan', 'Não informado')
                return df
    return None

def filtrar_por_usuarios_cadastrados(df_dados, df_users):
    if df_dados is None or df_dados.empty: return df_dados
    if df_users is None or df_users.empty: return df_dados
    lista_vip = df_users['nome'].unique()
    df_filtrado = df_dados.copy()
    df_filtrado['TEMP_NOME_UPPER'] = df_filtrado['Colaborador'].apply(normalizar_chave)
    df_filtrado = df_filtrado[df_filtrado['TEMP_NOME_UPPER'].isin(lista_vip)]
    df_filtrado.drop(columns=['TEMP_NOME_UPPER'], inplace=True)
    return df_filtrado

# --- 4. LOGIN RENOVADO ---
if 'logado' not in st.session_state:
    st.session_state.update({'logado': False, 'usuario_nome': '', 'perfil': '', 'usuario_email': ''})

if not st.session_state['logado']:
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        with st.form("form_login"):
            st.markdown('<p class="login-title">Team Sofistas</p>', unsafe_allow_html=True)
            st.markdown('<p class="login-subtitle">Analytics & Performance</p>', unsafe_allow_html=True)
            email_input = st.text_input("E-mail Corporativo ou Usuário Gestor").strip().lower()
            senha_input = st.text_input("Senha (Obrigatório apenas para Gestor)", type="password")
            st.markdown("<br>", unsafe_allow_html=True)
            if st.form_submit_button("ACESSAR"):
                if email_input in USUARIOS_ADMIN and senha_input == SENHA_ADMIN:
                    st.session_state.update({'logado': True, 'usuario_nome': 'Gestor', 'perfil': 'admin', 'usuario_email': 'admin'})
                    st.rerun()
                else:
                    df_users = carregar_usuarios()
                    if df_users is not None:
                        user_row = df_users[df_users['email'] == email_input]
                        if not user_row.empty:
                            nome_upper = user_row.iloc[0]['nome']
                            st.session_state.update({'logado': True, 'usuario_nome': nome_upper, 'perfil': 'user', 'usuario_email': email_input})
                            st.rerun()
                        else: st.error("🚫 E-mail não encontrado.")
                    else: st.error("⚠️ Base de usuários não carregada.")
    st.markdown('<div class="dev-footer">Desenvolvido por Klebson Davi - Supervisor de Suporte Técnico</div>', unsafe_allow_html=True)
    st.stop()

# --- 5. SIDEBAR ---
lista_periodos = listar_periodos_disponiveis()
opcoes_periodo = lista_periodos if lista_periodos else ["Nenhum histórico disponível"]

with st.sidebar:
    if os.path.exists(LOGO_FILE): st.image(LOGO_FILE, use_column_width=True)
    else: st.title("🦁 Team Sofistas")
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
    if df_raw is not None and not df_raw.empty:
        df_dados = filtrar_por_usuarios_cadastrados(df_raw, df_users_cadastrados)
        if df_dados is not None and not df_dados.empty:
            df_dados['Colaborador'] = df_dados['Colaborador'].str.title()
    else: df_dados = None
    
    st.markdown("---")
    nome_logado = st.session_state['usuario_nome'].title() if st.session_state['usuario_nome'] != 'Gestor' else 'Gestor'
    st.markdown(f"### 👤 {nome_logado.split()[0]}")
    if st.button("Sair"):
        st.session_state.update({'logado': False})
        st.rerun()
    st.markdown("---")
    st.caption("Desenvolvido por:\n**Klebson Davi**\nSupervisor de Suporte Técnico")

perfil = st.session_state['perfil']
if df_dados is None and perfil == 'user':
    st.info(f"👋 Olá, **{nome_logado}**! Dados de **{periodo_label}** indisponíveis.")
    st.stop()

# --- GESTOR ---
if perfil == 'admin':
    st.title(f"📊 Visão Gerencial")
    tabs = st.tabs(["🚦 Semáforo", "🏆 Ranking Geral", "⏳ Evolução", "🔍 Indicadores", "💰 Comissões", "📋 Tabela Geral", "🏖️ Férias Equipe", "⚙️ Admin", "📘 Como Alimentar"])
    
    tem_tam = False
    if df_dados is not None: tem_tam = 'TAM' in df_dados['Indicador'].unique()

    with tabs[0]: 
        if df_dados is not None:
            st.markdown(f"### Resumo de Saúde: **{periodo_label}**")
            df_media = df_dados.groupby('Colaborador')['% Atingimento'].mean().reset_index()
            c1, c2, c3 = st.columns(3)
            c1.metric("💎 Excelência", f"{len(df_media[df_media['% Atingimento'] >= 0.90])}")
            c2.metric("🟢 Meta Batida", f"{len(df_media[(df_media['% Atingimento'] >= 0.80) & (df_media['% Atingimento'] < 0.90)])}")
            c3.metric("🔴 Crítico", f"{len(df_media[df_media['% Atingimento'] < 0.80])}")
            st.markdown("---")
            
            # --- NOVO: FEEDBACK ---
            st.subheader("💬 Gerador de Feedback (1:1)")
            colab_feedback = st.selectbox("Selecione:", sorted(df_dados['Colaborador'].unique()), key="sb_feedback")
            if colab_feedback:
                user_kpis = df_dados[df_dados['Colaborador'] == colab_feedback].sort_values(by='% Atingimento', ascending=True)
                if not user_kpis.empty:
                    pior = user_kpis.iloc[0]
                    melhor = user_kpis.iloc[-1]
                    dica = DICAS_KPI.get(pior['Indicador'], "Verifique processos.")
                    st.markdown(f"""
                    <div class="insight-box">
                        <div class="insight-title">⚡ Análise: {colab_feedback}</div>
                        <ul style="margin-top:10px;color:#444">
                            <li><b>Ponto Forte:</b> {formatar_nome_visual(melhor['Indicador'])} ({melhor['% Atingimento']:.1%}) 👏</li>
                            <li><b>Atenção:</b> {formatar_nome_visual(pior['Indicador'])} ({pior['% Atingimento']:.1%}) ⚠️</li>
                            <li><b>Dica:</b> {dica}</li>
                        </ul>
                    </div>""", unsafe_allow_html=True)
            st.markdown("---")
            
            df_dados['Status_Farol'] = df_dados['% Atingimento'].apply(classificar_farol)
            fig_farol = px.bar(df_dados.groupby(['Indicador', 'Status_Farol']).size().reset_index(name='Qtd'), 
                               x='Indicador', y='Qtd', color='Status_Farol', text='Qtd',
                               color_discrete_map={'💎 Excelência': '#003366', '🟢 Meta Batida': '#2ecc71', '🔴 Crítico': '#e74c3c'})
            st.plotly_chart(fig_farol, use_container_width=True)

    with tabs[1]:
        st.markdown(f"### 🏆 Ranking Geral")
        if df_dados is not None:
            if tem_tam: df_rank = df_dados[df_dados['Indicador'] == 'TAM'].copy()
            else: df_rank = df_dados.groupby('Colaborador').agg({'Diamantes':'sum', 'Max. Diamantes':'sum'}).reset_index()
            df_rank['%'] = df_rank.apply(lambda x: x['Diamantes']/x['Max. Diamantes'] if x['Max. Diamantes']>0 else 0, axis=1)
            st.dataframe(df_rank.sort_values(by='%', ascending=False).style.format({'%': '{:.2%}'}), use_container_width=True)

    with tabs[2]:
        st.markdown("### ⏳ Evolução Temporal")
        df_hist = carregar_historico_completo()
        if df_hist is not None and not df_hist.empty:
            df_hist['Colaborador'] = df_hist['Colaborador'].str.title()
            colab_sel = st.selectbox("Selecione o Colaborador:", sorted(df_hist['Colaborador'].unique()))
            df_hist_user = df_hist[df_hist['Colaborador'] == colab_sel].copy()
            if not df_hist_user.empty:
                df_hist_user['Indicador'] = df_hist_user['Indicador'].apply(formatar_nome_visual)
                fig_heat = px.density_heatmap(df_hist_user, x="Periodo", y="Indicador", z="% Atingimento", text_auto=False, title=f"Mapa de Calor: {colab_sel}", color_continuous_scale="RdYlGn", range_color=[0.6, 1.0])
                fig_heat.update_traces(texttemplate="%{z:.1%}", textfont={"size":12})
                fig_heat.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig_heat, use_container_width=True)
            else: st.warning("Sem histórico.")
        else: st.info("Histórico vazio.")

    with tabs[3]:
        if df_dados is not None:
            st.markdown("### 🔬 Detalhe por Indicador")
            df_viz = df_dados.copy()
            df_viz['Indicador'] = df_viz['Indicador'].apply(formatar_nome_visual)
            for kpi in sorted(df_viz['Indicador'].unique()):
                with st.expander(f"📊 Ranking: {kpi}"):
                    df_kpi = df_viz[df_viz['Indicador'] == kpi].sort_values(by='% Atingimento', ascending=True)
                    fig_rank = px.bar(df_kpi, x='% Atingimento', y='Colaborador', orientation='h', text_auto='.1%', color='% Atingimento', color_continuous_scale=['#e74c3c', '#f1c40f', '#2ecc71'])
                    fig_rank.add_vline(x=0.8, line_dash="dash", line_color="black")
                    st.plotly_chart(fig_rank, use_container_width=True)

    with tabs[4]:
        st.markdown(f"### 💰 Relatório de Comissões")
        if df_dados is not None:
            lista_comissoes = []
            df_calc = df_dados.copy()
            df_calc['Colaborador_Key'] = df_calc['Colaborador'].str.upper()
            for colab in df_calc['Colaborador_Key'].unique():
                df_user = df_calc[df_calc['Colaborador_Key'] == colab]
                if tem_tam:
                    row_tam = df_user[df_user['Indicador'] == 'TAM']
                    total_diamantes = row_tam.iloc[0]['Diamantes'] if not row_tam.empty else 0
                else: total_diamantes = df_user['Diamantes'].sum()
                row_conf = df_user[df_user['Indicador'] == 'CONFORMIDADE']
                conf_val = row_conf.iloc[0]['% Atingimento'] if not row_conf.empty else 0.0
                desconto = 0
                if conf_val < 0.92:
                    row_pont = df_user[df_user['Indicador'] == 'PONTUALIDADE']
                    if not row_pont.empty: desconto = row_pont.iloc[0]['Diamantes']
                diamantes_validos = total_diamantes - desconto
                valor_final = diamantes_validos * 0.50
                lista_comissoes.append({"Colaborador": colab.title(), "Conformidade": conf_val, "A Pagar (R$)": valor_final})
            df_comissao = pd.DataFrame(lista_comissoes)
            st.dataframe(df_comissao.style.format({"Conformidade": "{:.2%}", "A Pagar (R$)": "R$ {:.2f}"}), use_container_width=True, height=600)
            csv = df_comissao.to_csv(index=False).encode('utf-8')
            st.download_button("⬇️ Baixar CSV", csv, "comissoes.csv", "text/csv")

    with tabs[5]: 
        if df_dados is not None:
            c1, c2 = st.columns([3, 1])
            with c1: st.markdown(f"### Mapa de Resultados: {periodo_label}")
            with c2: filtro = st.multiselect("🔍 Filtrar:", df_dados['Colaborador'].unique())
            df_show = df_dados if not filtro else df_dados[df_dados['Colaborador'].isin(filtro)]
            df_show_visual = df_show.copy()
            df_show_visual['Indicador'] = df_show_visual['Indicador'].apply(formatar_nome_visual)
            pivot = df_show_visual.pivot_table(index='Colaborador', columns='Indicador', values='% Atingimento').fillna(0.0)
            st.dataframe(pivot.style.background_gradient(cmap='RdYlGn', vmin=0.7, vmax=1.0).format("{:.2%}"), use_container_width=True, height=600)

    with tabs[6]: # Férias
        st.markdown("### 🏖️ Férias da Equipe")
        if df_users_cadastrados is not None:
            df_f = df_users_cadastrados[['nome', 'ferias']].copy()
            df_f['nome'] = df_f['nome'].str.title()
            st.dataframe(df_f, use_container_width=True)

    with tabs[7]: # Admin
        st.markdown("### 📂 Gestão e Diagnóstico")
        st1, st2, st3, st4 = st.tabs(["📤 Upload", "🗑️ Limpeza", "💾 Backup", "🔍 Diagnóstico"])
        with st1:
            data_sugestao = obter_data_hoje()
            nova_data = st.text_input("Mês/Ano de Referência:", value=data_sugestao)
            up_u = st.file_uploader("usuarios.csv", key="u")
            if up_u: 
                with open("usuarios.csv", "wb") as w: w.write(up_u.getbuffer())
                st.success("Usuarios OK!")
            up_k = st.file_uploader("Indicadores (CSVs)", accept_multiple_files=True, key="k")
            if up_k and st.button("Salvar Tudo"):
                faxina_arquivos_temporarios()
                salvar_arquivos_padronizados(up_k)
                salvar_config(nova_data)
                df_debug, log = carregar_dados_completo_debug() 
                if df_debug is not None:
                    atualizar_historico(df_debug, nova_data)
                    st.success("✅ Atualizado com Sucesso!")
                    time.sleep(1)
                    st.rerun()
                else: st.error("Erro ao processar arquivos.")
        with st2:
            st.write("Gerencie o histórico aqui.")
            if st.button("Limpar Histórico Completo"):
                limpar_base_dados_completa()
                st.success("Limpo!")
        with st4:
            if st.button("Rodar Diagnóstico"):
                _, log_df = carregar_dados_completo_debug()
                st.dataframe(log_df)

    with tabs[8]:
        st.info("Instruções de alimentação aqui.")

# --- VISÃO OPERADOR ---
else:
    st.markdown(f"## 🚀 Olá, **{nome_logado.split()[0]}**!")
    data_atualizacao = obter_data_atualizacao()
    st.markdown(f"<div style='margin-bottom: 20px; color: #666;'>📅 Ref: <b>{periodo_label}</b> <span class='update-badge'>🕒 Atualizado: {data_atualizacao}</span></div>", unsafe_allow_html=True)
    
    minhas_ferias = "Não informado"
    if df_users_cadastrados is not None:
        u = df_users_cadastrados[df_users_cadastrados['nome'] == nome_logado.upper()]
        if not u.empty: minhas_ferias = u.iloc[0]['ferias']

    tab_res, tab_fer = st.tabs(["📊 Resultados", "🏖️ Férias"])
    
    with tab_res:
        meus_dados = df_dados[df_dados['Colaborador'] == nome_logado].copy()
        if meus_dados.empty: meus_dados = df_dados[df_dados['Colaborador'].str.contains(nome_logado, case=False, na=False)]
        
        if not meus_dados.empty:
            # --- 1. BADGES E CABEÇALHO ---
            c_rank, c_gamif, c_gauge = st.columns([1, 1.5, 1])
            with c_gamif:
                # Lógica simplificada de medalhas
                badges = []
                if not meus_dados[meus_dados['Indicador'] == 'CONFORMIDADE'].empty:
                    if meus_dados[meus_dados['Indicador'] == 'CONFORMIDADE'].iloc[0]['% Atingimento'] >= 1.0: badges.append("🛡️ Guardião")
                if not meus_dados[meus_dados['Indicador'] == 'CSAT'].empty:
                    if meus_dados[meus_dados['Indicador'] == 'CSAT'].iloc[0]['% Atingimento'] >= 0.95: badges.append("❤️ Amado")
                if badges: st.markdown(f"**Conquistas:** {' '.join(badges)}")
            
            # --- 2. GRÁFICO DE RADAR ---
            media_equipe = df_dados.groupby('Indicador')['% Atingimento'].mean().reset_index()
            df_comp = pd.merge(meus_dados, media_equipe, on='Indicador')
            df_comp['Indicador'] = df_comp['Indicador'].apply(formatar_nome_visual)
            
            categorias = df_comp['Indicador'].tolist()
            valores_user = df_comp['% Atingimento'].tolist()
            valores_media = df_comp['% Atingimento_y'].tolist()
            if categorias:
                categorias.append(categorias[0])
                valores_user.append(valores_user[0])
                valores_media.append(valores_media[0])
                
                fig = go.Figure()
                fig.add_trace(go.Scatterpolar(r=valores_media, theta=categorias, fill='toself', name='Média Equipe', line_color='#cccccc', opacity=0.5))
                fig.add_trace(go.Scatterpolar(r=valores_user, theta=categorias, fill='toself', name='Você', line_color='#F37021'))
                fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 1.1])), showlegend=True, height=300, margin=dict(l=40, r=40, t=20, b=20))
                st.plotly_chart(fig, use_container_width=True)

            st.markdown("---")

            # --- 3. SMART COACH ---
            pior_row = meus_dados.sort_values(by='% Atingimento').iloc[0]
            if pior_row['% Atingimento'] < 0.9:
                dica = DICAS_KPI.get(pior_row['Indicador'], "Fale com seu gestor.")
                st.markdown(f"""<div class="insight-box"><div class="insight-title">💡 Smart Coach: {formatar_nome_visual(pior_row['Indicador'])}</div><div class="insight-text">{dica} (Atual: {pior_row['% Atingimento']:.1%})</div></div>""", unsafe_allow_html=True)

            # --- 4. SIMULADOR ---
            with st.expander("🔮 Simulador de Ganhos"):
                sim_diamantes = st.slider("Se eu fizer X diamantes...", 0, 1000, 500)
                sim_conf = st.checkbox("E mantiver Conformidade > 92%?", value=True)
                ganho = sim_diamantes * 0.50 if sim_conf else (sim_diamantes * 0.50) * 0.8 # Exemplo de penalidade
                st.metric("Eu ganharia:", f"R$ {ganho:.2f}")

            st.markdown("---")

            # --- 5. CARDS ---
            cols = st.columns(len(meus_dados))
            for i, (_, row) in enumerate(meus_dados.iterrows()):
                val = row['% Atingimento']
                label = formatar_nome_visual(row['Indicador'])
                
                # META DINÂMICA
                meta = 0.92 if row['Indicador'] in ['CONFORMIDADE', 'ADERENCIA'] else 0.80
                
                if val >= meta:
                    delta_msg = "✅ Meta Batida"
                    color = "normal"
                else:
                    delta_msg = f"🔻 Meta {meta:.0%}"
                    color = "inverse"
                
                with cols[i]:
                    st.metric(label, f"{val:.2%}", delta_msg, delta_color=color)
            
            # --- 6. HISTÓRICO PESSOAL ---
            st.markdown("---")
            st.markdown("### 📈 Sua Evolução (Últimos Meses)")
            df_hist_full = carregar_historico_completo()
            if df_hist_full is not None:
                # Filtra histórico do usuário logado (normalizando nome)
                hist_user = df_hist_full[df_hist_full['Colaborador'].astype(str).str.upper().apply(normalizar_chave) == normalizar_chave(nome_logado)].copy()
                if not hist_user.empty:
                    hist_user['Indicador'] = hist_user['Indicador'].apply(formatar_nome_visual)
                    fig_hist = px.line(hist_user, x='Periodo', y='% Atingimento', color='Indicador', markers=True)
                    st.plotly_chart(fig_hist, use_container_width=True)
                else:
                    st.info("Sem histórico anterior para exibir gráfico de evolução.")

        else:
            st.warning("Sem dados visualizáveis para seu perfil neste mês.")

    with tab_fer:
        st.markdown(f"<div class='vacation-card'><p class='vacation-title'>Férias Programadas</p><div class='vacation-date'>{minhas_ferias}</div></div>", unsafe_allow_html=True)
