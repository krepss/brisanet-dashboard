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
    "ADERENCIA": "Atenção aos horários de login/logoff e pausas. Cumpra a escala rigorosamente.",
    "CONFORMIDADE": "Revise as pausas e sua programação. A conformidade é seu tempo de fila.",
    "INTERACOES": "Seja mais proativo durante o atendimento. Evite silêncio excessivo.",
    "PONTUALIDADE": "Evite atrasos na primeira conexão do dia e também nas suas pausas. Dica: Chegue minutos antes.",
    "CSAT": "Aposte na empatia e na escuta ativa. Confirme a resolução com o cliente.",
    "IR": "Investigue a causa raiz para evitar retorno. Resolva de vez.",
    "TPC": "Use o roteiro para ser ágil sem perder qualidade no atendimento.",
    "TAM": "Controle o tempo mas priorize a resolução efetiva."
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
    
    /* SIDEBAR AZUL */
    [data-testid="stSidebar"] {
        background-color: #002b55 !important;
        background-image: linear-gradient(180deg, #002b55 0%, #004e92 100%) !important;
    }
    
    /* Texto GERAL da Sidebar -> BRANCO */
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, 
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] label, [data-testid="stSidebar"] span, 
    [data-testid="stSidebar"] div {
        color: #FFFFFF !important;
    }

    /* --- CORREÇÃO DO SELECTBOX (Mês de Referência) --- */
    /* Força o fundo da caixa a ser branco e o texto PRETO */
    [data-testid="stSidebar"] div[data-baseweb="select"] > div {
        background-color: #FFFFFF !important;
        color: #000000 !important;
    }
    /* Força o texto selecionado e as opções a serem pretos */
    [data-testid="stSidebar"] div[data-baseweb="select"] span,
    [data-testid="stSidebar"] div[data-baseweb="select"] div {
        color: #000000 !important;
    }
    /* Ícone da seta em preto */
    [data-testid="stSidebar"] div[data-baseweb="select"] svg {
        fill: #000000 !important;
    }
    /* Menu suspenso (dropdown) */
    ul[data-testid="stSelectboxVirtualDropdown"] li {
        color: #000000 !important;
        background-color: #FFFFFF !important;
    }
    /* ------------------------------------------------ */

    /* Textos Gerais do Corpo */
    h1, h2, h3, h4, h5, h6 { color: #003366 !important; font-family: 'Montserrat', sans-serif !important; }
    p, li, div { color: #333333; }
    
    [data-testid="stForm"], div.stMetric, .vacation-card, .insight-box {
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
    .insight-title { font-weight: bold; color: #d35400; font-size: 1.1em; margin-bottom: 5px; }
    .insight-text { font-size: 0.95em; color: #555; }

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
    if pd.isna(valor) or valor == '':
        return 0.0
    
    if isinstance(valor, str):
        v = valor.replace('%', '').replace(',', '.').strip()
        try: 
            num = float(v)
            # SE O VALOR FOR > 1.05 (ex: 50), DIVIDE POR 100. SE FOR < 1.05 (ex: 0.5), MANTÉM.
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

# --- NOVO: NORMALIZAR NOMES (COM CORREÇÃO DE ACENTOS E ESPAÇOS) ---
def normalizar_chave(texto):
    if pd.isna(texto): return ""
    texto = str(texto).strip().upper()
    # Remove acentos (Bárbara -> BARBARA)
    nfkd = unicodedata.normalize('NFKD', texto)
    texto_sem_acento = u"".join([c for c in nfkd if not unicodedata.combining(c)])
    # Remove espaços duplos
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
    
    # NORMALIZAÇÃO DE NOME AQUI
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

def carregar_dados_completo():
    lista_final = []
    arquivos_ignorar = ['usuarios.csv', 'historico_consolidado.csv', 'config.json', LOGO_FILE]
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
            col_ferias = next((c for c in df.columns if 'ferias' in c or 'férias' in c), None)
            
            if col_email and col_nome:
                rename_map = {col_email: 'email', col_nome: 'nome'}
                if col_ferias: rename_map[col_ferias] = 'ferias'
                df.rename(columns=rename_map, inplace=True)
                df['email'] = df['email'].astype(str).str.strip().str.lower()
                
                # NORMALIZAÇÃO DE NOME AQUI TAMBÉM
                df['nome'] = df['nome'].apply(normalizar_chave)
                
                if 'ferias' not in df.columns: df['ferias'] = "Não informado"
                else: df['ferias'] = df['ferias'].astype(str).replace('nan', 'Não informado')
                return df
    return None

def filtrar_por_usuarios_cadastrados(df_dados, df_users):
    if df_dados is None or df_dados.empty: return df_dados
    if df_users is None or df_users.empty: return df_dados
    lista_vip = df_users['nome'].unique()
    
    # Filtro robusto com normalização
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
    else:
        df_dados = None
    
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
            
            # --- NOVO: GERADOR DE FEEDBACK ---
            st.subheader("💬 Gerador de Feedback (1:1)")
            colab_feedback = st.selectbox("Selecione para análise:", sorted(df_dados['Colaborador'].unique()), key="sb_feedback")
            if colab_feedback:
                user_kpis = df_dados[df_dados['Colaborador'] == colab_feedback].sort_values(by='% Atingimento', ascending=True)
                if not user_kpis.empty:
                    pior = user_kpis.iloc[0]
                    melhor = user_kpis.iloc[-1]
                    dica_geral = DICAS_KPI.get(pior['Indicador'], "Verifique os processos operacionais.")
                    st.markdown(f"""
                    <div class="insight-box">
                        <div class="insight-title">⚡ Análise Rápida: {colab_feedback}</div>
                        <ul style="margin-top:10px; color:#444;">
                            <li><b>Ponto Forte:</b> {formatar_nome_visual(melhor['Indicador'])} ({melhor['% Atingimento']:.1%}) - <i>Elogie!</i> 👏</li>
                            <li><b>Ponto de Atenção:</b> {formatar_nome_visual(pior['Indicador'])} ({pior['% Atingimento']:.1%}) - <i>Foque aqui!</i> ⚠️</li>
                            <li><b>Dica Sugerida:</b> {dica_geral}</li>
                        </ul>
                    </div>
                    """, unsafe_allow_html=True)
            st.markdown("---")

            st.markdown("### 🦁 Performance Global da Equipe")
            remove_pont = st.checkbox("Remover Pontualidade do Cálculo Global", value=False)
            total_dia_team = 0
            total_max_team = 0
            if tem_tam:
                df_tam_team = df_dados[df_dados['Indicador'] == 'TAM']
                total_dia_team = df_tam_team['Diamantes'].sum()
                total_max_team = df_tam_team['Max. Diamantes'].sum()
                if remove_pont:
                    df_pont_team = df_dados[df_dados['Indicador'] == 'PONTUALIDADE']
                    if not df_pont_team.empty:
                        total_dia_team -= df_pont_team['Diamantes'].sum()
                        total_max_team -= df_pont_team['Max. Diamantes'].sum()
            else:
                if remove_pont: df_calc_team = df_dados[df_dados['Indicador'] != 'PONTUALIDADE']
                else: df_calc_team = df_dados
                total_dia_team = df_calc_team['Diamantes'].sum()
                total_max_team = df_calc_team['Max. Diamantes'].sum()
            perc_team = (total_dia_team / total_max_team) if total_max_team > 0 else 0
            fig_team = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = perc_team * 100,
                domain = {'x': [0, 1], 'y': [0, 1]},
                gauge = {
                    'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': 'white'},
                    'bar': {'color': "#003366"},
                    'steps': [{'range': [0, 80], 'color': '#ffcccb'},{'range': [80, 90], 'color': '#fff4cc'},{'range': [90, 100], 'color': '#d9f7be'}],
                    'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': 100}
                }
            ))
            fig_team.update_layout(height=250, margin=dict(l=20, r=20, t=30, b=20))
            st.plotly_chart(fig_team, use_container_width=True)
            
            st.markdown("---")
            st.subheader("📋 Atenção Prioritária")
            df_atencao = df_media_pessoas[df_media_pessoas['% Atingimento'] < 0.80].sort_values(by='% Atingimento')
            if not df_atencao.empty:
                lista_detalhada = []
                for colab in df_atencao['Colaborador']:
                    dados_pessoa = df_dados[df_dados['Colaborador'] == colab]
                    media_pessoa = dados_pessoa['% Atingimento'].mean()
                    pior_kpi_row = dados_pessoa.loc[dados_pessoa['% Atingimento'].idxmin()]
                    nome_kpi_bonito = formatar_nome_visual(pior_kpi_row['Indicador'])
                    lista_detalhada.append({'Colaborador': colab, 'Média Geral': media_pessoa, 'Status': '🔴 Crítico', 'Pior KPI': f"{nome_kpi_bonito} ({pior_kpi_row['% Atingimento']:.2%})"})
                df_final_atencao = pd.DataFrame(lista_detalhada)
                st.dataframe(df_final_atencao.style.format({'Média Geral': '{:.2%}'}), use_container_width=True)
            else: st.success("🎉 Equipe performando bem! Ninguém abaixo de 80%.")

    with tabs[1]:
        st.markdown(f"### 🏆 Ranking Geral (Consolidado)")
        if df_dados is not None and not df_dados.empty:
            if tem_tam: df_rank = df_dados[df_dados['Indicador'] == 'TAM'].copy()
            else:
                 df_rank = df_dados.groupby('Colaborador').agg({'Diamantes': 'sum', 'Max. Diamantes': 'sum'}).reset_index()
                 df_rank['% Atingimento'] = df_rank.apply(lambda row: (row['Diamantes'] / row['Max. Diamantes']) if row['Max. Diamantes'] > 0 else 0, axis=1)
            df_rank = df_rank.sort_values(by='% Atingimento', ascending=False)
            cols_show = ['Colaborador', 'Diamantes', 'Max. Diamantes', '% Atingimento']
            st.dataframe(df_rank[cols_show].style.format({'Diamantes': '{:.0f}', 'Max. Diamantes': '{:.0f}', '% Atingimento': '{:.2%}'}).background_gradient(subset=['% Atingimento'], cmap='RdYlGn'), use_container_width=True, height=600)

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
            else: st.warning("Sem histórico para este colaborador.")
        else: st.info("O histórico está vazio.")

    with tabs[3]:
        if df_dados is not None and not df_dados.empty:
            st.markdown("### 🔬 Detalhe por Indicador")
            df_viz = df_dados.copy()
            df_viz['Indicador'] = df_viz['Indicador'].apply(formatar_nome_visual)
            for kpi in sorted(df_viz['Indicador'].unique()):
                with st.expander(f"📊 Ranking: {kpi}", expanded=False):
                    df_kpi = df_viz[df_viz['Indicador'] == kpi].sort_values(by='% Atingimento', ascending=True)
                    fig_rank = px.bar(df_kpi, x='% Atingimento', y='Colaborador', orientation='h', text_auto='.1%', title=f"Ranking - {kpi}", color='% Atingimento', color_continuous_scale=['#e74c3c', '#f1c40f', '#2ecc71'])
                    fig_rank.add_vline(x=0.8, line_dash="dash", line_color="black", annotation_text="Meta 80%")
                    fig_rank.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                    st.plotly_chart(fig_rank, use_container_width=True)

    with tabs[4]:
        st.markdown(f"### 💰 Relatório de Comissões")
        if df_dados is not None and not df_dados.empty:
            st.info("ℹ️ Regra: R$ 0,50 por Diamante. **Trava:** Conformidade >= 92%.")
            lista_comissoes = []
            df_calc = df_dados.copy()
            df_calc['Colaborador_Key'] = df_calc['Colaborador'].str.upper()
            for colab in df_calc['Colaborador_Key'].unique():
                df_user = df_calc[df_calc['Colaborador_Key'] == colab]
                if tem_tam:
                    row_tam = df_user[df_user['Indicador'] == 'TAM']
                    total_diamantes = row_tam.iloc[0]['Diamantes'] if not row_tam.empty else 0
                else:
                    total_diamantes = df_user['Diamantes'].sum()
                row_conf = df_user[df_user['Indicador'] == 'CONFORMIDADE']
                conf_val = row_conf.iloc[0]['% Atingimento'] if not row_conf.empty else 0.0
                desconto = 0
                obs = "✅ Elegível"
                if conf_val < 0.92:
                    row_pont = df_user[df_user['Indicador'] == 'PONTUALIDADE']
                    if not row_pont.empty:
                        desconto = row_pont.iloc[0]['Diamantes'] if 'Diamantes' in row_pont.columns else 0
                        obs = "⚠️ Penalidade (Pontualidade)"
                    else: obs = "⚠️ Conformidade Baixa"
                diamantes_validos = total_diamantes - desconto
                valor_final = diamantes_validos * 0.50
                lista_comissoes.append({"Colaborador": colab.title(), "Conformidade": conf_val, "Total Diamantes": int(total_diamantes), "Desconto": int(desconto), "Diamantes Líquidos": int(diamantes_validos), "A Pagar (R$)": valor_final, "Status": obs})
            df_comissao = pd.DataFrame(lista_comissoes)
            st.dataframe(df_comissao.style.format({"Conformidade": "{:.2%}", "A Pagar (R$)": "R$ {:.2f}"}).background_gradient(subset=['A Pagar (R$)'], cmap='Greens'), use_container_width=True, height=600)
            csv = df_comissao.to_csv(index=False).encode('utf-8')
            st.download_button("⬇️ Baixar CSV", csv, "comissoes.csv", "text/csv")

    with tabs[5]: 
        if df_dados is not None and not df_dados.empty:
            c1, c2 = st.columns([3, 1])
            with c1: st.markdown(f"### Mapa de Resultados: {periodo_label}")
            with c2: filtro = st.multiselect("🔍 Filtrar:", df_dados['Colaborador'].unique())
            df_show = df_dados if not filtro else df_dados[df_dados['Colaborador'].isin(filtro)]
            df_show_visual = df_show.copy()
            df_show_visual['Indicador'] = df_show_visual['Indicador'].apply(formatar_nome_visual)
            pivot = df_show_visual.pivot_table(index='Colaborador', columns='Indicador', values='% Atingimento')
            pivot = pivot.fillna(0.0)
            try: st.dataframe(pivot.style.background_gradient(cmap='RdYlGn', vmin=0.7, vmax=1.0).format("{:.2%}"), use_container_width=True, height=600)
            except: st.dataframe(pivot.style.format("{:.2%}"), use_container_width=True, height=600)

    with tabs[6]:
        st.markdown("### 🏖️ Cronograma de Férias da Equipe")
        if df_users_cadastrados is not None and not df_users_cadastrados.empty:
            df_ferias_view = df_users_cadastrados[['nome', 'ferias']].copy()
            df_ferias_view.rename(columns={'nome': 'Colaborador', 'ferias': 'Mês Programado'}, inplace=True)
            df_ferias_view['Colaborador'] = df_ferias_view['Colaborador'].str.title()
            search_ferias = st.text_input("🔍 Buscar Colaborador:", placeholder="Digite o nome...")
            if search_ferias:
                df_ferias_view = df_ferias_view[df_ferias_view['Colaborador'].str.contains(search_ferias, case=False)]
            st.dataframe(df_ferias_view, use_container_width=True, hide_index=True)
            csv_ferias = df_ferias_view.to_csv(index=False).encode('utf-8')
            st.download_button("⬇️ Baixar Planilha de Férias", csv_ferias, "ferias_equipe.csv", "text/csv")
        else:
            st.warning("⚠️ Arquivo 'usuarios.csv' não carregado ou sem dados.")

    with tabs[7]:
        st.markdown("### 📂 Gestão de Arquivos")
        subtabs = st.tabs(["📤 Upload & Atualização", "🗑️ Limpeza de Histórico", "💾 Backup"])
        with subtabs[0]:
            data_sugestao = obter_data_hoje()
            st.markdown("#### 1. Configurar Período")
            nova_data = st.text_input("Mês/Ano de Referência:", value=data_sugestao)
            st.markdown("#### 2. Atualizar Arquivos")
            c1, c2 = st.columns(2)
            with c1:
                up_u = st.file_uploader("usuarios.csv", key="u")
                if up_u: 
                    try:
                        with open("usuarios.csv", "wb") as w: w.write(up_u.getbuffer())
                        st.success("Usuarios OK!")
                    except Exception as e: st.error(f"Erro ao salvar usuarios.csv: {e}")
            with c2:
                up_k = st.file_uploader("Indicadores (CSVs, incluindo TAM)", accept_multiple_files=True, key="k")
                if up_k:
                    st.markdown("**🔎 Pré-visualização:**")
                    lista_diag = []
                    for f in up_k:
                        try:
                            df_chk = ler_csv_inteligente(f)
                            if df_chk is not None:
                                df_p, msg = tratar_arquivo_especial(df_chk, f.name)
                                if df_p is not None:
                                    kpis = df_p['Indicador'].unique()
                                    lista_diag.append({"Arquivo": f.name, "Status": "✅ OK", "KPIs": str(kpis)})
                                else: lista_diag.append({"Arquivo": f.name, "Status": "❌ Erro", "Detalhe": msg})
                        except Exception as e: lista_diag.append({"Arquivo": f.name, "Status": "❌ Erro", "Detalhe": str(e)})
                    st.dataframe(pd.DataFrame(lista_diag))
                    if st.button("💾 Salvar e Atualizar Histórico"): 
                        if not nova_data.strip():
                            st.error("⚠️ O campo 'Mês/Ano' não pode estar vazio!")
                            st.stop()
                        try:
                            faxina_arquivos_temporarios()
                            salvos = salvar_arquivos_padronizados(up_k)
                            salvar_config(nova_data)
                            df_novo_ciclo = carregar_dados_completo()
                            if df_novo_ciclo.empty: st.error("⚠️ Erro: Filtro removeu todos os dados.")
                            else:
                                atualizar_historico(df_novo_ciclo, nova_data)
                                st.cache_data.clear()
                                st.balloons()
                                st.success(f"✅ Sucesso! Mês {nova_data} atualizado.")
                                time.sleep(1)
                                st.rerun()
                        except Exception as e: st.error(f"Erro salvamento: {e}")
        with subtabs[1]:
            st.markdown("#### 🗑️ Gerenciar Meses no Sistema")
            df_atual_hist = carregar_historico_completo()
            if df_atual_hist is not None and not df_atual_hist.empty:
                resumo = df_atual_hist.groupby('Periodo').size().reset_index(name='Registros')
                for i, row in resumo.iterrows():
                    c1, c2, c3 = st.columns([2, 1, 1])
                    c1.write(f"📅 **{row['Periodo']}**")
                    c2.write(f"{row['Registros']} linhas")
                    if c3.button(f"Excluir {row['Periodo']}", key=f"del_{i}"):
                        if excluir_periodo_historico(row['Periodo']):
                            st.success(f"Mês {row['Periodo']} excluído!")
                            time.sleep(1)
                            st.rerun()
            else: st.info("Histórico vazio.")
        with subtabs[2]:
            st.markdown("#### 💾 Backup e Reset")
            if os.path.exists('historico_consolidado.csv'):
                with open('historico_consolidado.csv', 'rb') as f:
                    st.download_button("⬇️ Baixar Histórico Consolidado", f, "historico_consolidado.csv", "text/csv")
            st.divider()
            if st.button("🗑️ Resetar Tudo (Apaga Todo o Histórico)"):
                limpar_base_dados_completa()
                if os.path.exists('historico_consolidado.csv'): os.remove('historico_consolidado.csv')
                st.cache_data.clear()
                st.warning("Tudo limpo!")
                time.sleep(2)
                st.rerun()

    with tabs[8]:
        st.markdown("### 📘 Como Alimentar o Sistema")
        st.info("Para garantir que os dados sejam lidos corretamente, siga os padrões abaixo.")
        with st.expander("1. Arquivo de Usuários (Login)"):
            st.markdown("""
            **Nome do Arquivo:** `usuarios.csv` (obrigatório).
            **Colunas:** `Nome`, `Email`, `Férias` (opcional).
            """)
            st.code("Nome,Email,Férias\nJoão Silva,joao@brisanet.com.br,Novembro")
        with st.expander("2. Arquivos de Indicadores (KPIs)"):
            st.markdown("**Nome do Arquivo:** Pode ser qualquer um (ex: `ir.csv`, `csat.csv`).\n**Colunas:** `Colaborador`, `% Atingimento`, `Diamantes`, `Max. Diamantes`.")
            st.code("Colaborador,% Atingimento,Diamantes,Max. Diamantes\nJoão Silva,0.95,95,100")
        with st.expander("3. Arquivo TAM (Opcional)"):
            st.markdown("Se um arquivo tiver **TAM** no nome, ele será usado como o indicador principal de ranking.")
        with st.expander("4. Regras de Gatilho"):
            st.markdown("O cálculo financeiro desconta a pontualidade se a **Conformidade** for < 92%.")

# --- VISÃO OPERADOR ---
else:
    st.markdown(f"## 🚀 Olá, **{nome_logado.split()[0]}**!")
    data_atualizacao = obter_data_atualizacao()
    st.markdown(f"<div style='display: flex; align-items: center; margin-bottom: 20px; color: #666;'><span style='margin-right: 15px;'>📅 Referência: <b>{periodo_label}</b></span><span class='update-badge'>🕒 Atualizado em: {data_atualizacao}</span></div>", unsafe_allow_html=True)
    
    minhas_ferias = "Não informado"
    if df_users_cadastrados is not None:
        try:
            user_info = df_users_cadastrados[df_users_cadastrados['nome'] == nome_logado.upper()]
            if not user_info.empty: minhas_ferias = user_info.iloc[0]['ferias']
        except: pass

    tab_results, tab_ferias = st.tabs(["📊 Meus Resultados", "🏖️ Minhas Férias"])

    with tab_results:
        ranking_msg = "Não classificado"
        if df_dados is not None and not df_dados.empty:
            tem_tam = 'TAM' in df_dados['Indicador'].unique()
            if tem_tam:
                df_rank = df_dados[df_dados['Indicador'] == 'TAM'].copy()
                df_rank = df_rank.sort_values(by='% Atingimento', ascending=False).reset_index(drop=True)
            else:
                df_rank = df_dados.groupby('Colaborador').agg({'Diamantes': 'sum', 'Max. Diamantes': 'sum'}).reset_index()
                df_rank['Score'] = df_rank['Diamantes'] / df_rank['Max. Diamantes']
                df_rank = df_rank.sort_values(by='Score', ascending=False).reset_index(drop=True)
            try:
                posicao = df_rank[df_rank['Colaborador'] == nome_logado].index[0] + 1
                total_colabs = len(df_rank)
                ranking_msg = f"{posicao}º de {total_colabs}"
            except: pass

        meus_dados = df_dados[df_dados['Colaborador'] == nome_logado].copy()
        if meus_dados.empty: meus_dados = df_dados[df_dados['Colaborador'].str.contains(nome_logado, case=False, na=False)].copy()

        if not meus_dados.empty:
            tem_tam = 'TAM' in meus_dados['Indicador'].unique()
            if 'Diamantes' in meus_dados.columns:
                if tem_tam:
                    row_tam = meus_dados[meus_dados['Indicador'] == 'TAM']
                    total_dia_bruto = row_tam.iloc[0]['Diamantes'] if not row_tam.empty else 0
                    total_max = row_tam.iloc[0]['Max. Diamantes'] if not row_tam.empty else 0
                    resultado_global = row_tam.iloc[0]['% Atingimento'] if not row_tam.empty else 0
                else:
                    total_dia_bruto = meus_dados['Diamantes'].sum()
                    total_max = meus_dados['Max. Diamantes'].sum()
                    resultado_global = (total_dia_bruto / total_max) if total_max > 0 else 0
                
                c_rank, c_gamif, c_gauge = st.columns([1, 1.5, 1])
                with c_rank:
                    st.markdown("##### 🏆 Ranking")
                    st.metric("Sua Posição", ranking_msg)
                with c_gamif:
                    st.markdown("##### 💎 Gamificação")
                    st.progress(resultado_global if resultado_global <= 1.0 else 1.0)
                    st.write(f"**{int(total_dia_bruto)} / {int(total_max)}** Diamantes")
                with c_gauge:
                    fig_gauge = go.Figure(go.Indicator(
                        mode = "gauge+number",
                        value = resultado_global * 100,
                        number = {'font': {'size': 24, 'color': '#003366'}}, 
                        gauge = {
                            'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "#003366"},
                            'bar': {'color': "#F37021"},
                            'bgcolor': "white",
                            'steps': [{'range': [0, 100], 'color': '#f4f7f6'}],
                            'threshold': {'line': {'color': "green", 'width': 4}, 'thickness': 0.75, 'value': 100}
                        }))
                    fig_gauge.update_layout(height=140, margin=dict(l=10, r=10, t=30, b=10), paper_bgcolor='rgba(0,0,0,0)', font={'color': '#003366'})
                    st.plotly_chart(fig_gauge, use_container_width=True)
                st.markdown("---")
                
                # --- NOVO: SMART COACH ---
                pior_row = meus_dados.sort_values(by='% Atingimento').iloc[0]
                if pior_row['% Atingimento'] < 0.9:
                    dica = DICAS_KPI.get(pior_row['Indicador'], "Fale com seu gestor.")
                    st.markdown(f"""
                    <div class="insight-box">
                        <div class="insight-title">💡 Smart Coach: {formatar_nome_visual(pior_row['Indicador'])}</div>
                        <div class="insight-text">{dica} (Atual: {pior_row['% Atingimento']:.1%})</div>
                    </div>""", unsafe_allow_html=True)

                df_conf = meus_dados[meus_dados['Indicador'] == 'CONFORMIDADE']
                atingimento_conf = df_conf.iloc[0]['% Atingimento'] if not df_conf.empty else 0.0
                tem_dado_conf = not df_conf.empty
                desconto_diamantes = 0
                motivo_desconto = ""
                GATILHO_FINANCEIRO = 0.92
                if tem_dado_conf and atingimento_conf < GATILHO_FINANCEIRO:
                    df_pont = meus_dados[meus_dados['Indicador'] == 'PONTUALIDADE']
                    if not df_pont.empty:
                        desconto_diamantes = df_pont.iloc[0]['Diamantes']
                        motivo_desconto = f"(Perdeu {desconto_diamantes} de Pontualidade)"
                total_dia_liquido = total_dia_bruto - desconto_diamantes
                valor_final = total_dia_liquido * 0.50
                st.markdown("#### 💰 Extrato Financeiro")
                c1, c2, c3 = st.columns(3)
                c1.metric("Diamantes Válidos", f"{int(total_dia_liquido)}", f"{motivo_desconto}", delta_color="inverse" if desconto_diamantes > 0 else "normal")
                c2.metric("Valor por Diamante", "R$ 0,50")
                if not tem_dado_conf:
                    c3.metric("Valor a Receber", "Aguardando", "Conformidade Indisponível", delta_color="off")
                elif desconto_diamantes > 0:
                    c3.metric("Valor a Receber", f"R$ {valor_final:.2f}", f"Gatilho não atingido (<{GATILHO_FINANCEIRO:.0%})", delta_color="inverse")
                    st.error(f"⚠️ **Gatilho Financeiro não atingido**: Sua conformidade foi **{atingimento_conf:.2%}**. Para receber os diamantes de Pontualidade, é necessário ter >= 92% de Conformidade.")
                else:
                    c3.metric("Valor a Receber", f"R$ {valor_final:.2f}", "Gatilho Atingido! 🤑")
                    if atingimento_conf >= GATILHO_FINANCEIRO:
                        st.success(f"✅ **Gatilho Financeiro Atingido**: Conformidade **{atingimento_conf:.2%}** (>= 92%). Todos os diamantes computados.")
                st.divider()

            cols = st.columns(len(meus_dados))
            for i, (_, row) in enumerate(meus_dados.iterrows()):
                val = row['% Atingimento']
                label = formatar_nome_visual(row['Indicador'])
                
                # --- LÓGICA DE META DINÂMICA (92% para Conformidade/Aderência, 80% Outros) ---
                meta = 0.92 if row['Indicador'] in ['CONFORMIDADE', 'ADERENCIA'] else 0.80
                
                if val >= meta:
                    delta_msg = "✅ Meta Batida"
                    color = "normal"
                else:
                    delta_msg = f"🔻 Meta {meta:.0%}" # Ex: "Meta 92%"
                    color = "inverse"
                
                with cols[i]:
                    st.metric(label, f"{val:.2%}", delta_msg, delta_color=color)

            st.markdown("---")
            media_equipe = df_dados.groupby('Indicador')['% Atingimento'].mean().reset_index()
            media_equipe.rename(columns={'% Atingimento': 'Média Equipe'}, inplace=True)
            df_comp = pd.merge(meus_dados, media_equipe, on='Indicador')
            df_comp['Indicador'] = df_comp['Indicador'].apply(formatar_nome_visual)
            df_melt = df_comp.melt(id_vars=['Indicador'], value_vars=['% Atingimento', 'Média Equipe'], var_name='Tipo', value_name='Resultado')
            fig = px.bar(df_melt, x='Indicador', y='Resultado', color='Tipo', barmode='group', color_discrete_map={'% Atingimento': '#F37021', 'Média Equipe': '#003366'})
            fig.add_hline(y=0.8, line_dash="dash", line_color="green", annotation_text="Meta 80%")
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font={'color': '#333333'}, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.error(f"⚠️ Não encontramos dados de performance para o nome **{nome_logado}**.")
            st.info("Isso acontece quando o nome no login (usuarios.csv) não bate com o nome no arquivo de indicadores.")
            st.write("**Nomes disponíveis no arquivo de indicadores:**")
            st.dataframe(pd.DataFrame(df_dados['Colaborador'].unique(), columns=['Nomes Encontrados']), hide_index=True)

    with tab_ferias:
        st.markdown("### 🗓️ Planejamento de Férias")
        st.markdown("Aqui você confere o mês programado para o seu descanso.")
        st.markdown("<br>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            st.markdown(f"""
            <div class="vacation-card">
                <p class="vacation-title">Suas próximas férias estão programadas para:</p>
                <div class="vacation-date">{minhas_ferias}</div>
                <p class="vacation-note">*Sujeito a alteração conforme necessidade da operação.</p>
            </div>
            """, unsafe_allow_html=True)
