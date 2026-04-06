import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import json
import time
import base64
import requests 
from datetime import datetime, timezone, timedelta
import unicodedata
import extra_streamlit_components as stx
import google.generativeai as genai
import time

# --- CONFIGURAÇÃO DE ARQUIVOS E ACESSOS ---
LOGO_FILE = "logo.png"
PASTA_FOTOS = "fotos_perfil" 

# Busca a senha EXCLUSIVAMENTE no cofre seguro. 
# O .get() faz com que, se o cofre não existir, a senha vire 'None' (Nulo).
# Assim, é impossível alguém acertar a senha, trancando o sistema 100%.
SENHA_ADMIN = st.secrets.get("SENHA_GESTOR", None)

USUARIOS_ADMIN = ['gestor', 'admin']

# Garante que a pasta de fotos exista no servidor
if not os.path.exists(PASTA_FOTOS):
    os.makedirs(PASTA_FOTOS)

DICAS_KPI = {
    "ADERENCIA": "Atenção aos horários de login/logoff e pausas. Cumpra a escala rigorosamente.",
    "CONFORMIDADE": "Aqui é o tempo de fila, evite pausas desnecessárias!",
    "INTERACOES": "Seja mais proativo durante o atendimento. Evite silêncio excessivo.",
    "PONTUALIDADE": "Evite atrasos na primeira conexão do dia. Chegue 5 min antes.",
    "CSAT": "Aposte na empatia e na escuta ativa. Confirme a resolução com o cliente.",
    "IR": "Garanta que o serviço voltou a funcionar. Faça testes finais antes de encerrar.",
    "TPC": "Aqui é no pulo do gato, da pra recuperar é só lembrar de tabuluar no momento certo!",
    "TAM": "Assuma o comando da ligação. Seja objetivo e guie o cliente para a solução."
}

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
try:
    st.set_page_config(page_title="Team Sofistas | Analytics", layout="wide", page_icon=LOGO_FILE, initial_sidebar_state="collapsed")
except:
    st.set_page_config(page_title="Team Sofistas | Analytics", layout="wide", page_icon="🦁", initial_sidebar_state="collapsed")

# --- 2. CSS COMPACTADO (CLEAN GLASS PREMIUM) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;800&family=Roboto:wght@300;400;500;700&display=swap');
    
    /* Fundo Gelo Super Suave (Estilo Apple) */
    html, body {scroll-behavior: smooth !important; font-family: 'Roboto', sans-serif;}
    .stApp {background-color: #F5F7FA !important;}
    
    /* Esconde barra lateral */
    [data-testid="collapsedControl"], [data-testid="stSidebar"] {display: none !important;}
    
    /* Textos Gerais */
    h1, h2, h3, h4, h5, h6 {color: #111827 !important; font-family: 'Montserrat', sans-serif !important; letter-spacing: -0.5px;}
    p, li, div {color: #4B5563;}
    
    /* Banner Superior "Vidro Flutuante" */
    .top-banner {
        background: rgba(255, 255, 255, 0.85); 
        backdrop-filter: blur(12px); 
        -webkit-backdrop-filter: blur(12px);
        padding: 20px 30px; 
        border-radius: 24px; 
        border: 1px solid rgba(255, 255, 255, 0.4); 
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.03); 
        display: flex; justify-content: space-between; align-items: center; margin-bottom: 25px;
    }
    .top-banner h2, .top-banner h4 {color: #111827 !important; margin: 0 !important; padding: 0 !important;}
    .top-banner h2 {font-weight: 800 !important; font-size: 28px !important;}
    .top-banner .sub-text {color: #6B7280 !important; margin: 0 !important; padding: 0 !important; font-size: 14px !important; font-weight: 500 !important;}
    
    /* Botões Arredondados (Estilo Nubank/iOS) */
    button[kind="primary"] {background-color: #F37021 !important; border: none !important; border-radius: 30px !important; box-shadow: 0 4px 14px rgba(243, 112, 33, 0.3) !important; transition: all 0.3s ease;}
    button[kind="primary"] p {color: #FFF !important; font-weight: 600 !important;}
    button[kind="primary"]:hover {transform: translateY(-2px); box-shadow: 0 6px 20px rgba(243, 112, 33, 0.4) !important;}
    button[kind="secondary"] {background-color: #FFFFFF !important; border: 1px solid #E5E7EB !important; color: #111827 !important; border-radius: 30px !important; font-weight: 600 !important; box-shadow: 0 2px 5px rgba(0,0,0,0.02) !important;}
    button[kind="secondary"] p {color: #111827 !important;}
    button[kind="secondary"]:hover {border-color: #D1D5DB !important; background-color: #F9FAFB !important;}
    
    /* Cartões Base (Métricas, Formulários) - Sombras esfumaçadas e bordas grandes */
    div.stMetric, .insight-box, .badge-card, [data-testid="stForm"] {
        background-color: #FFFFFF !important; 
        border: none !important; 
        box-shadow: 0 8px 24px rgba(0,0,0,0.04) !important; 
        border-radius: 20px !important;
    }
    
    /* Cards do Semáforo */
    .card-link {text-decoration: none !important; display: block;}
    .card-excelencia, .card-meta, .card-critico {background-color: #FFFFFF; border-radius: 20px; border: 1px solid #F3F4F6; padding: 15px 20px; cursor: pointer; transition: all .3s ease; box-shadow: 0 4px 15px rgba(0,0,0,0.02);}
    .card-excelencia {border-left: 6px solid #10B981;}
    .card-excelencia:hover {transform: translateY(-3px); box-shadow: 0 12px 25px rgba(16, 185, 129, 0.15);}
    .card-meta {border-left: 6px solid #F59E0B;}
    .card-meta:hover {transform: translateY(-3px); box-shadow: 0 12px 25px rgba(245, 158, 11, 0.15);}
    .card-critico {border-left: 6px solid #EF4444;}
    .card-critico:hover {transform: translateY(-3px); box-shadow: 0 12px 25px rgba(239, 68, 68, 0.15);}
    
    /* Ajuste de Texto nos Cards */
    .card-excelencia div:first-child, .card-meta div:first-child, .card-critico div:first-child {color: #6B7280 !important; font-weight: 500;}
    .card-excelencia div:nth-child(2), .card-meta div:nth-child(2), .card-critico div:nth-child(2) {color: #111827 !important;}
    
    /* Login e Formulários */
    [data-testid="stForm"] {padding: 3rem 2rem !important; border-top: none !important;}
    .login-title {color: #111827 !important; text-align: center; margin-bottom: 0px; font-weight: 800;}
    .login-subtitle {color: #6B7280 !important; text-align: center; margin-bottom: 25px;}
    [data-testid="stForm"] input {background-color: #F9FAFB !important; color: #111827 !important; border: 1px solid #E5E7EB !important; border-radius: 12px !important; padding: 12px !important;}
    
    /* Componente Metric Nativo */
    div.stMetric {border-left: 5px solid #F37021; padding: 15px 20px !important;}
    div.stMetric label {color: #6B7280 !important; font-size: 14px !important; font-weight: 500;}
    div.stMetric div[data-testid="stMetricValue"] {color: #111827 !important; font-size: 28px !important; font-weight: 800;}
    
    /* Badges e Insight */
    .update-badge {background-color: #F3F4F6; color: #4B5563; padding: 6px 12px; border-radius: 20px; font-size: .85em; font-weight: 600; border: none;}
    .insight-box {background-color: #FFFBEB !important; border-left: none !important; padding: 20px; margin-bottom: 20px; border-radius: 20px;}
    .insight-title {color: #D97706; font-weight: 700; display: flex; align-items: center; gap: 8px;}
    .insight-text {color: #4B5563;}
    
    /* Tabelas e Abas */
    [data-testid="stDataFrame"] {background-color: transparent !important;}
    .stTabs [data-baseweb="tab-list"] {background-color: transparent; border-bottom: 2px solid #E5E7EB;}
    .stTabs [data-baseweb="tab"] {color: #6B7280; font-weight: 600; padding-top: 15px; padding-bottom: 15px;}
    .stTabs [aria-selected="true"] {color: #F37021 !important; border-bottom-color: #F37021 !important;}
    
    .dev-footer {text-align: center; margin-top: 40px; font-size: .85em; color: #9CA3AF !important; font-weight: 500;}
</style>
""", unsafe_allow_html=True)

# --- 3. FUNÇÕES DE BACKEND ---
def carregar_base_humor():
    """Lê o histórico completo de humor da equipe."""
    ARQUIVO_HUMOR = 'humor_diario.csv'
    if os.path.exists(ARQUIVO_HUMOR):
        try:
            return pd.read_csv(ARQUIVO_HUMOR)
        except:
            return None
    return None

def sincronizar_com_github(nome_arquivo, mensagem="Atualização via Painel Gestor"):
    if "GITHUB_TOKEN" not in st.secrets or "GITHUB_REPO" not in st.secrets:
        return False
    try:
        token = st.secrets["GITHUB_TOKEN"]
        repo = st.secrets["GITHUB_REPO"]
        branch = st.secrets.get("GITHUB_BRANCH", "main")
        
        url = f"https://api.github.com/repos/{repo}/contents/{nome_arquivo}"
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        r = requests.get(url, headers=headers, params={"ref": branch})
        sha = r.json().get("sha") if r.status_code == 200 else None
        
        with open(nome_arquivo, "rb") as f:
            content_b64 = base64.b64encode(f.read()).decode("utf-8")
            
        payload = {
            "message": f"🤖 {mensagem} - Arquivo: {nome_arquivo}",
            "content": content_b64,
            "branch": branch
        }
        if sha: 
            payload["sha"] = sha
            
        requests.put(url, headers=headers, json=payload)
        return True
    except Exception as e:
        print(f"Aviso - Falha ao sincronizar com GitHub: {e}")
        return False

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

def converter_hora_para_float(valor):
    try:
        val_str = str(valor).strip()
        if not val_str or val_str.lower() == 'nan': return 0.0
        sinal = 1
        if val_str.startswith('-'): sinal, val_str = -1, val_str[1:]
        elif val_str.startswith('+'): val_str = val_str[1:]
        parts = val_str.split(':')
        if len(parts) == 2: return sinal * (int(parts[0]) + (int(parts[1]) / 60.0))
        return 0.0
    except: return 0.0

def formatar_saldo_decimal(valor_float):
    try:
        sinal = "+" if valor_float >= 0 else "-"
        valor_abs = abs(valor_float)
        horas = int(valor_abs)
        minutos = int(round((valor_abs - horas) * 60))
        if minutos == 60: horas, minutos = horas + 1, 0
        return f"{sinal}{horas:02d}:{minutos:02d}"
    except: return "00:00"

def tentar_extrair_data_csv(df):
    for col in df.columns:
        if any(x in col.lower() for x in ['data', 'date', 'periodo', 'mês', 'mes', 'competencia', 'ref']):
            try:
                data = pd.to_datetime(df[col], dayfirst=True, errors='coerce').dropna().max()
                if pd.notnull(data): return data.strftime("%m/%Y")
            except: continue
    return None

def obter_data_hoje(): 
    return datetime.now().strftime("%m/%Y")

def obter_data_atualizacao():
    fuso_brasilia = timezone(timedelta(hours=-3))
    if os.path.exists('historico_consolidado.csv'): 
        timestamp_utc = os.path.getmtime('historico_consolidado.csv')
        dt_utc = datetime.fromtimestamp(timestamp_utc, tz=timezone.utc)
        return dt_utc.astimezone(fuso_brasilia).strftime("%d/%m/%Y às %H:%M")
    return datetime.now(fuso_brasilia).strftime("%d/%m/%Y às %H:%M")

def salvar_config(data_texto):
    try:
        with open('config.json', 'w') as f: json.dump({'periodo': data_texto}, f)
        sincronizar_com_github('config.json', "Atualizando configuração global")
    except: pass

def ler_config():
    if os.path.exists('config.json'):
        with open('config.json', 'r') as f: return json.load(f).get('periodo', 'Não informado')
    return "Aguardando atualização"

def limpar_base_dados_completa():
    for f in os.listdir('.'): 
        if f.endswith('.csv'): 
            os.remove(f)
            sincronizar_com_github(f, "Reset de base de dados")

def faxina_arquivos_temporarios():
    protegidos = ['historico_consolidado.csv', 'usuarios.csv', 'config.json', LOGO_FILE, 'feedbacks_gb.csv', 'feedbacks_gb_backup.csv', 'historico_operacional.csv', 'historico_voz.csv', 'escalas_banco_horas.csv', 'saldo_banco_horas.csv']
    for f in os.listdir('.'):
        if f.endswith('.csv') and f not in protegidos:
            try: os.remove(f)
            except: pass

# --- FUNÇÕES DE TMA (CHAT E VOZ) ---
def processar_desempenho_agente(df):
    df.columns = [str(c).strip().lower() for c in df.columns]
    col_nome = next((c for c in df.columns if 'nome' in c and 'agente' in c), None)
    col_vol = next((c for c in df.columns if 'atendidas' in c), None)
    col_tma = next((c for c in df.columns if 'tratamento médio' in c or 'tma' in c), None)

    if col_nome and col_tma:
        df_op = df[[col_nome]].copy()
        df_op.rename(columns={col_nome: 'Colaborador'}, inplace=True)
        df_op['Colaborador'] = df_op['Colaborador'].apply(normalizar_chave)
        
        if col_vol:
            df_op['Atendimentos'] = pd.to_numeric(df[col_vol], errors='coerce').fillna(0)
        else:
            df_op['Atendimentos'] = 0
            
        df_op['TMA_ms'] = pd.to_numeric(df[col_tma], errors='coerce').fillna(0)
        df_op['TMA_seg'] = df_op['TMA_ms'] / 1000.0
        
        def formata_tma(segs):
            if pd.isna(segs) or segs <= 0: return "00:00"
            m = int(segs // 60)
            s = int(segs % 60)
            return f"{m:02d}:{s:02d}"
            
        df_op['TMA_Formatado'] = df_op['TMA_seg'].apply(formata_tma)
        return df_op[['Colaborador', 'Atendimentos', 'TMA_seg', 'TMA_Formatado']]
    return None

def atualizar_historico_operacional(df_novo, periodo):
    ARQ = 'historico_operacional.csv' 
    df_save = df_novo.copy()
    df_save['Periodo'] = str(periodo).strip()
    if os.path.exists(ARQ):
        try:
            df_hist = pd.read_csv(ARQ)
            df_hist['Periodo'] = df_hist['Periodo'].astype(str).str.strip()
            df_hist = df_hist[df_hist['Periodo'] != str(periodo).strip()]
            df_final = pd.concat([df_hist, df_save], ignore_index=True)
        except: df_final = df_save
    else: df_final = df_save
    df_final.to_csv(ARQ, index=False)
    sincronizar_com_github(ARQ, f"Atualizando Produtividade Chat - {periodo}")

def carregar_historico_operacional():
    if os.path.exists('historico_operacional.csv'):
        try: return pd.read_csv('historico_operacional.csv')
        except: return None
    return None

def atualizar_historico_voz(df_novo, periodo):
    ARQ = 'historico_voz.csv' 
    df_save = df_novo.copy()
    df_save['Periodo'] = str(periodo).strip()
    if os.path.exists(ARQ):
        try:
            df_hist = pd.read_csv(ARQ)
            df_hist['Periodo'] = df_hist['Periodo'].astype(str).str.strip()
            df_hist = df_hist[df_hist['Periodo'] != str(periodo).strip()]
            df_final = pd.concat([df_hist, df_save], ignore_index=True)
        except: df_final = df_save
    else: df_final = df_save
    df_final.to_csv(ARQ, index=False)
    sincronizar_com_github(ARQ, f"Atualizando Produtividade Voz - {periodo}")

def carregar_historico_voz():
    if os.path.exists('historico_voz.csv'):
        try: return pd.read_csv('historico_voz.csv')
        except: return None
    return None

# --- FUNÇÕES BANCO DE HORAS E SALDOS ---
def salvar_escala_banco(dados):
    ARQ = 'escalas_banco_horas.csv'
    df_novo = pd.DataFrame([dados])
    if os.path.exists(ARQ):
        try:
            df_hist = pd.read_csv(ARQ)
            df_final = pd.concat([df_hist, df_novo], ignore_index=True)
        except: df_final = df_novo
    else: df_final = df_novo
    df_final.to_csv(ARQ, index=False)
    sincronizar_com_github(ARQ, "Novo agendamento de banco de horas")

def carregar_escalas_banco():
    if os.path.exists('escalas_banco_horas.csv'):
        try: return pd.read_csv('escalas_banco_horas.csv')
        except: return None
    return None

def carregar_saldos_banco():
    if os.path.exists('saldo_banco_horas.csv'):
        try: return pd.read_csv('saldo_banco_horas.csv')
        except: return None
    return None

# --- FUNÇÕES DE KPI (ANTIGAS) ---
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
    
    cols_order = ['Periodo', 'Colaborador', 'Indicador', '% Atingimento', 'Diamantes', 'Max. Diamantes']
    existing_cols = [c for c in cols_order if c in df_final.columns]
    for c in ['Diamantes', 'Max. Diamantes']:
        if c in existing_cols: df_final[c] = df_final[c].fillna(0.0)
            
    df_final[existing_cols].to_csv(ARQUIVO_HIST, index=False)
    sincronizar_com_github(ARQUIVO_HIST, f"Atualizando Indicadores Mensais - {periodo}")

def excluir_periodo_historico(periodo_alvo):
    if os.path.exists('historico_consolidado.csv'):
        try:
            df_hist = pd.read_csv('historico_consolidado.csv')
            df_hist['Periodo'] = df_hist['Periodo'].astype(str).str.strip()
            df_novo = df_hist[df_hist['Periodo'] != str(periodo_alvo).strip()]
            df_novo.to_csv('historico_consolidado.csv', index=False)
            sincronizar_com_github('historico_consolidado.csv', f"Exclusão de mês: {periodo_alvo}")
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

# --- LÊ A PORCENTAGEM (Blindada) ---
def processar_porcentagem_br(valor):
    if pd.isna(valor) or str(valor).strip() == '': return 0.0
    if isinstance(valor, str):
        has_percent = '%' in valor
        v = valor.replace('%', '').replace(',', '.').strip()
        try: 
            num = float(v)
            if has_percent: return num / 100.0
            if num > 1.05: return num / 100.0
            return num
        except: return 0.0
    if isinstance(valor, (int, float)):
        if valor > 1.05: return valor / 100.0
        return float(valor)
    return 0.0

def ler_csv_inteligente(arquivo_ou_caminho):
    for sep in [',', ';']:
        for enc in ['utf-8-sig', 'latin1', 'cp1252']:
            try:
                if hasattr(arquivo_ou_caminho, 'seek'): arquivo_ou_caminho.seek(0)
                df = pd.read_csv(arquivo_ou_caminho, sep=sep, encoding=enc, dtype=str)
                if len(df.columns) > 1: return df
            except: continue
    return None

def normalizar_chave(texto):
    if pd.isna(texto): return ""
    texto = str(texto).strip().upper()
    nfkd = unicodedata.normalize('NFKD', texto)
    return " ".join(u"".join([c for c in nfkd if not unicodedata.combining(c)]).split())

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
    
    # 1. Identifica as colunas cravando no símbolo "%"
    col_ad = next((c for c in df.columns if 'ader' in c and ('%' in c or 'perc' in c)), None)
    if not col_ad: 
        col_ad = next((c for c in df.columns if 'ader' in c and 'duração' not in c and 'programado' not in c and c != 'colaborador'), None)
        
    col_conf = next((c for c in df.columns if 'conform' in c and ('%' in c or 'perc' in c)), None)
    if not col_conf: 
        col_conf = next((c for c in df.columns if 'conform' in c and c != 'colaborador'), None)
    
    if col_ad and col_conf:
        lista_retorno = []
        df_ad = df[['Colaborador', col_ad]].copy()
        df_ad.rename(columns={col_ad: '% Atingimento'}, inplace=True)
        df_ad['% Atingimento'] = df_ad['% Atingimento'].apply(processar_porcentagem_br)
        df_ad['Indicador'] = 'ADERENCIA'
        df_ad['Diamantes'] = 0.0
        df_ad['Max. Diamantes'] = 0.0
        lista_retorno.append(df_ad[['Colaborador', 'Indicador', '% Atingimento', 'Diamantes', 'Max. Diamantes']])
        
        df_conf = df[['Colaborador', col_conf]].copy()
        df_conf.rename(columns={col_conf: '% Atingimento'}, inplace=True)
        df_conf['% Atingimento'] = df_conf['% Atingimento'].apply(processar_porcentagem_br)
        df_conf['Indicador'] = 'CONFORMIDADE'
        df_conf['Diamantes'] = 0.0
        df_conf['Max. Diamantes'] = 0.0
        lista_retorno.append(df_conf[['Colaborador', 'Indicador', '% Atingimento', 'Diamantes', 'Max. Diamantes']])
        
        return pd.concat(lista_retorno, ignore_index=True), "Extração Dupla Segura"
    
    col_valor = None
    nome_kpi_limpo = nome_arquivo.split('.')[0].lower()
    
    prioridades = ['% atingimento', 'atingimento', 'resultado', 'nota final', 'score', 'nota', 'valor']
    for p in prioridades + [nome_kpi_limpo]:
        for c in df.columns:
            if p in c and c != 'colaborador': 
                col_valor = c
                break
        if col_valor: break
        
    if not col_valor:
        cols_restantes = [c for c in df.columns if c != 'colaborador' and 'diamante' not in c]
        if cols_restantes: col_valor = cols_restantes[0]
        else: return None, f"Nenhuma coluna de nota identificada."
            
    df.rename(columns={col_valor: '% Atingimento'}, inplace=True)
    
    for c in df.columns:
        if 'diamantes' in c and 'max' not in c: df.rename(columns={c: 'Diamantes'}, inplace=True)
        if 'max' in c and 'diamantes' in c: df.rename(columns={c: 'Max. Diamantes'}, inplace=True)
    
    df['% Atingimento'] = df['% Atingimento'].apply(processar_porcentagem_br)
    
    if 'Diamantes' not in df.columns: df['Diamantes'] = 0.0
    if 'Max. Diamantes' not in df.columns: df['Max. Diamantes'] = 0.0
    
    df['Diamantes'] = pd.to_numeric(df['Diamantes'], errors='coerce').fillna(0)
    df['Max. Diamantes'] = pd.to_numeric(df['Max. Diamantes'], errors='coerce').fillna(0)
    
    nome_indicador = normalizar_nome_indicador(nome_arquivo)
    if col_conf and 'conform' in col_valor: nome_indicador = 'CONFORMIDADE'
    if col_ad and 'ader' in col_valor: nome_indicador = 'ADERENCIA'
    
    df['Indicador'] = nome_indicador
    cols_to_keep = ['Colaborador', 'Indicador', '% Atingimento', 'Diamantes', 'Max. Diamantes']
    return df[cols_to_keep], "Extração Simples"

def classificar_farol(val):
    if val >= 0.90: return '💎 Excelência' 
    elif val >= 0.80: return '🟢 Meta Batida'
    else: return '🔴 Crítico'

def carregar_dados_completo_debug():
    lista_final = []
    log_debug = []
    arquivos_ignorar = ['usuarios.csv', 'historico_consolidado.csv', 'config.json', LOGO_FILE, 'feedbacks_gb.csv', 'feedbacks_gb_backup.csv', 'historico_operacional.csv', 'historico_voz.csv', 'escalas_banco_horas.csv', 'saldo_banco_horas.csv']
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
            # 1. Padroniza os nomes para minúsculo e tira espaços
            df.columns = df.columns.str.lower().str.strip()
            
            # 2. SEGREDO AQUI: Remove colunas duplicadas acidentais do CSV
            df = df.loc[:, ~df.columns.duplicated()].copy()
            
            col_email = next((c for c in df.columns if 'mail' in c), None)
            col_nome = next((c for c in df.columns if 'colaborador' in c or 'nome' in c), None)
            col_ferias = next((c for c in df.columns if 'ferias' in c or 'férias' in c), None)
            
            if col_email and col_nome:
                rename_map = {col_email: 'email', col_nome: 'nome'}
                if col_ferias: rename_map[col_ferias] = 'ferias'
                
                df.rename(columns=rename_map, inplace=True)
                
                # 3. Garante novamente que não há duplicidade após renomear
                df = df.loc[:, ~df.columns.duplicated()].copy()
                
                # Agora o .str funciona perfeitamente, pois garantimos ser uma coluna única!
                df['email'] = df['email'].astype(str).str.strip().str.lower()
                df['nome'] = df['nome'].apply(normalizar_chave)
                
                if 'ferias' not in df.columns: 
                    df['ferias'] = "Não informado"
                else: 
                    df['ferias'] = df['ferias'].astype(str).replace('nan', 'Não informado')
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

def salvar_feedback_gb(dados_fb):
    ARQUIVO_FB = 'feedbacks_gb.csv'
    df_novo = pd.DataFrame([dados_fb])
    if os.path.exists(ARQUIVO_FB):
        try:
            df_hist = pd.read_csv(ARQUIVO_FB)
            df_final = pd.concat([df_hist, df_novo], ignore_index=True)
        except: df_final = df_novo
    else: 
        if os.path.exists('feedbacks_gb_backup.csv'):
            try:
                df_hist = pd.read_csv('feedbacks_gb_backup.csv')
                df_final = pd.concat([df_hist, df_novo], ignore_index=True)
            except: df_final = df_novo
        else:
            df_final = df_novo
    df_final.to_csv(ARQUIVO_FB, index=False)
    sincronizar_com_github(ARQUIVO_FB, "Novo Feedback GB Registrado")

def carregar_feedbacks_gb():
    nomes_possiveis = ['feedbacks_gb.csv', 'feedbacks_gb_backup.csv']
    for nome in nomes_possiveis:
        if os.path.exists(nome):
            try:
                df = ler_csv_inteligente(nome)
                if df is not None: return df
                return pd.read_csv(nome)
            except: continue
    return None
    
def atualizar_senha(email, nova_senha):
    arquivos = [f for f in os.listdir('.') if f.endswith('.csv') and 'usuario' in f.lower()]
    if arquivos:
        arq = arquivos[0]
        df = pd.read_csv(arq)
        
        # Padroniza as colunas para encontrar o email correto no arquivo original
        cols_lower = df.columns.str.lower()
        col_email = next((c for c, cl in zip(df.columns, cols_lower) if 'mail' in cl), None)
        
        if col_email:
            if 'senha' not in df.columns:
                df['senha'] = ""
            
            # Atualiza a senha no arquivo csv
            mask = df[col_email].astype(str).str.strip().str.lower() == email.strip().lower()
            if mask.any():
                df.loc[mask, 'senha'] = nova_senha
                df.to_csv(arq, index=False)
                sincronizar_com_github(arq, f"Senha atualizada para o usuario: {email}")
                return True
    return False

def salvar_mensagem_mural(dados):
    ARQ = 'mural_parabens.csv'
    df_novo = pd.DataFrame([dados])
    if os.path.exists(ARQ):
        try:
            df_hist = pd.read_csv(ARQ)
            df_final = pd.concat([df_hist, df_novo], ignore_index=True)
        except: df_final = df_novo
    else: df_final = df_novo
    df_final.to_csv(ARQ, index=False)
    sincronizar_com_github(ARQ, "Novo recado no mural de parabens")

def carregar_mensagens_mural():
    if os.path.exists('mural_parabens.csv'):
        try: return pd.read_csv('mural_parabens.csv', dtype=str)
        except: return None
    return None
import re

import re
import glob

# --- NOVAS FUNÇÕES CONSOLIDADAS EM CSV ---

def ler_todas_escalas_wfm():
    """Lê todas as linhas de conteúdo do CSV consolidado."""
    ARQUIVO_CSV = "base_wfm_consolidada.csv"
    if os.path.exists(ARQUIVO_CSV):
        try:
            df = pd.read_csv(ARQUIVO_CSV)
            return df['Conteudo_Linha'].tolist()
        except:
            return []
    return []

def buscar_escala_hoje(nome_operador):
    """Busca a escala do dia atual para o operador logado."""
    try:
        hoje_wfm = datetime.now().strftime("%d/%m/%Y")
        linhas = ler_todas_escalas_wfm()
        
        for linha in linhas:
            if nome_operador.lower() in linha.lower() and hoje_wfm in linha:
                if "dia de folga inteiro" in linha:
                    motivo = linha.split("-")[-1].strip()
                    return {"tipo": "folga", "motivo": motivo}
                else:
                    partes = linha.split(f"{hoje_wfm}, ")
                    if len(partes) > 1:
                        resto = partes[1]
                        turno_eventos = resto.split(": ", 1)
                        turno = turno_eventos[0]
                        eventos_str = turno_eventos[1] if len(turno_eventos) > 1 else ""
                        intervalo_1, refeicao, intervalo_2 = "", "", ""
                        eventos = eventos_str.split(", ")
                        ints = [ev.replace("Intervalo ", "") for ev in eventos if "Intervalo" in ev]
                        refeicao = next((ev.replace("Refeição ", "") for ev in eventos if "Refeição" in ev), "")
                        if len(ints) > 0: intervalo_1 = ints[0]
                        if len(ints) > 1: intervalo_2 = ints[1]
                        return {"tipo": "trabalho", "turno": turno, "intervalo_1": intervalo_1, "refeicao": refeicao, "intervalo_2": intervalo_2}
        return None
    except: return None
        
def salvar_escala_no_csv(conteudo_txt, data_inicio, data_fim):
    ARQUIVO_CSV = "base_wfm_consolidada.csv"
    hoje = datetime.now().strftime("%d/%m/%Y %H:%M")
    # ID único para o período
    id_up = f"{data_inicio.strftime('%Y%m%d')}_{data_fim.strftime('%Y%m%d')}"
    
    linhas = []
    for l in conteudo_txt.split('\n'):
        if "," in l and ":" in l:
            linhas.append({
                "ID_Upload": id_up, 
                "Data_Registro": hoje, 
                "Inicio_Vigencia": data_inicio.strftime("%d/%m/%Y"), 
                "Fim_Vigencia": data_fim.strftime("%d/%m/%Y"), 
                "Conteudo_Linha": l.strip()
            })
    
    df_novo = pd.DataFrame(linhas)
    
    if os.path.exists(ARQUIVO_CSV):
        try:
            df_base = pd.read_csv(ARQUIVO_CSV)
            # Remove duplicatas do mesmo ID antes de concatenar
            df_base = df_base[df_base['ID_Upload'] != id_up]
            df_final = pd.concat([df_base, df_novo], ignore_index=True)
        except:
            df_final = df_novo
    else:
        df_final = df_novo
    
    df_final.to_csv(ARQUIVO_CSV, index=False)
    sincronizar_com_github(ARQUIVO_CSV, f"WFM Update: {id_up}")
    
def gerar_radar_wfm_data(data_alvo):
    """Função que o Gestor usa para o Radar (Linha 1261)."""
    try:
        df_users = carregar_usuarios()
        if df_users is None or df_users.empty: return None
            
        usuarios_ativos = {}
        for _, row in df_users.iterrows():
            nome_norm = str(row['nome']) 
            usuarios_ativos[nome_norm] = {"Colaborador": nome_norm.title(), "Status": "Folga", "Turno": "Ausente"}
            
        linhas = ler_todas_escalas_wfm()
        dias_semana = ['segunda-feira, ', 'terça-feira, ', 'quarta-feira, ', 'quinta-feira, ', 'sexta-feira, ', 'sábado, ', 'domingo, ']
        
        for linha in linhas:
            if data_alvo in linha:
                partes = linha.split(data_alvo)
                nome_cru = partes[0]
                for d in dias_semana: nome_cru = nome_cru.replace(d, "")
                nome_norm_wfm = normalizar_chave(nome_cru.strip())
                
                if nome_norm_wfm in usuarios_ativos:
                    resto = partes[1]
                    status = "Trabalhando"
                    turno = "N/A"
                    if "dia de folga inteiro" in resto.lower():
                        status = "Férias" if "férias" in resto.lower() else "Folga"
                        turno = "Ausente"
                    else:
                        turno_info = resto.split(":")
                        if len(turno_info) > 0:
                            turno = turno_info[0].replace(", ", "").strip()
                            if "treinamento" in resto.lower(): status = "Treinamento"
                            if "questões de saúde" in resto.lower(): status = "Saúde"
                    usuarios_ativos[nome_norm_wfm] = {"Colaborador": nome_norm_wfm.title(), "Status": status, "Turno": turno}
                    
        df = pd.DataFrame(list(usuarios_ativos.values()))
        ordem = {"Trabalhando": 1, "Treinamento": 2, "Saúde": 3, "Férias": 4, "Folga": 5}
        df['Ordem'] = df['Status'].map(ordem).fillna(99)
        return df.sort_values(by=["Ordem", "Colaborador"]).drop(columns=['Ordem'])
    except: return None
def buscar_escala_completa(nome_operador):
    """Gera a tabela completa de escalas para o operador (Linha 2495)."""
    escala = []
    try:
        # Puxa todas as linhas do novo banco de dados CSV
        linhas = ler_todas_escalas_wfm()
        
        for linha in linhas:
            # Verifica se o nome do operador aparece na linha da escala
            if nome_operador.lower() in linha.lower():
                # Busca o padrão de data DD/MM/AAAA
                match_data = re.search(r'\d{2}/\d{2}/\d{4}', linha)
                if match_data:
                    data_str = match_data.group()
                    dia_semana = ""
                    # Tenta capturar o dia da semana (ex: Segunda-Feira) que vem antes da data
                    match_dia = re.search(r'([a-zA-Zá-úÁ-Ú-]+),\s' + data_str, linha)
                    if match_dia:
                        dia_semana = match_dia.group(1).title()
                    
                    if "dia de folga inteiro" in linha.lower():
                        motivo = linha.split("-")[-1].strip()
                        escala.append({"Data": data_str, "Dia": dia_semana, "Turno": "🏖️ Folga", "Detalhes": motivo})
                    else:
                        # Corta a linha para pegar os horários e intervalos
                        partes = linha.split(f"{data_str}, ")
                        if len(partes) > 1:
                            resto = partes[1]
                            turno_eventos = resto.split(": ", 1)
                            turno = turno_eventos[0]
                            detalhes = turno_eventos[1].strip() if len(turno_eventos) > 1 else ""
                            escala.append({"Data": data_str, "Dia": dia_semana, "Turno": turno, "Detalhes": detalhes})
        
        if escala:
            import pandas as pd
            # Converte para DataFrame e remove duplicatas (caso suba o mesmo período 2x)
            df_final = pd.DataFrame(escala).drop_duplicates(subset=['Data'])
            # Ordena pela data para o operador ver em ordem cronológica
            df_final['Data_Convertida'] = pd.to_datetime(df_final['Data'], format='%d/%m/%Y')
            df_final = df_final.sort_values(by='Data_Convertida').drop(columns=['Data_Convertida'])
            return df_final
    except Exception as e:
        pass
    return None

def obter_imagem_perfil(nome_colaborador):
    """Retorna a imagem (Base64) ou None se não encontrar nada."""
    import base64
    nome_seguro = normalizar_chave(nome_colaborador).replace(" ", ".")
    caminho_foto = os.path.join(PASTA_FOTOS, f"{nome_seguro}.png")
    caminho_avatar_txt = caminho_foto.replace(".png", "_avatar.txt")
    
    try:
        # 1. Tenta Foto Real
        if os.path.exists(caminho_foto):
            with open(caminho_foto, "rb") as f:
                return f"data:image/png;base64,{base64.b64encode(f.read()).decode()}"
        
        # 2. Tenta Avatar Escolhido
        elif os.path.exists(caminho_avatar_txt):
            with open(caminho_avatar_txt, "r", encoding="utf-8") as f:
                nome_arq_avatar = f.read().strip()
            caminho_full_avatar = os.path.join("avatares", nome_arq_avatar)
            if os.path.exists(caminho_full_avatar):
                with open(caminho_full_avatar, "rb") as f:
                    return f"data:image/png;base64,{base64.b64encode(f.read()).decode()}"
    except:
        pass
    return None

def registrar_humor_dia(nome_colaborador, humor_escolhido):
    """Salva o humor diário e a hora exata no fuso do Brasil (UTC-3)."""
    from datetime import datetime, timedelta, timezone
    
    # Crava o fuso horário para UTC-3 (Horário de Brasília/Fortaleza)
    fuso_br = timezone(timedelta(hours=-3))
    agora = datetime.now(fuso_br)
    
    hoje_data = agora.strftime("%d/%m/%Y")
    hoje_hora = agora.strftime("%H:%M") 
    
    ARQUIVO_HUMOR = 'humor_diario.csv'
    novo_registro = {
        "Data": hoje_data, 
        "Hora": hoje_hora, 
        "Colaborador": nome_colaborador.title(), 
        "Humor": humor_escolhido
    }
    import pandas as pd
    import os
    df_novo = pd.DataFrame([novo_registro])
    
    if os.path.exists(ARQUIVO_HUMOR):
        try:
            df_base = pd.read_csv(ARQUIVO_HUMOR)
            mask = (df_base['Data'] == hoje_data) & (df_base['Colaborador'].str.upper() == nome_colaborador.upper())
            if mask.any():
                df_base.loc[mask, 'Humor'] = humor_escolhido
                df_base.loc[mask, 'Hora'] = hoje_hora
                df_final = df_base
            else:
                df_final = pd.concat([df_base, df_novo], ignore_index=True)
        except:
            df_final = df_novo
    else:
        df_final = df_novo
        
    df_final.to_csv(ARQUIVO_HUMOR, index=False)
    # Tenta sincronizar com o Github se a função existir
    try:
        sincronizar_com_github(ARQUIVO_HUMOR, f"Humor atualizado: {nome_colaborador}")
    except:
        pass


def carregar_humor_hoje(nome_colaborador):
    """Verifica se o colaborador já registrou o humor hoje (no fuso do Brasil)."""
    from datetime import datetime, timedelta, timezone
    import pandas as pd
    import os
    
    fuso_br = timezone(timedelta(hours=-3))
    hoje = datetime.now(fuso_br).strftime("%d/%m/%Y")
    ARQUIVO_HUMOR = 'humor_diario.csv'
    
    if os.path.exists(ARQUIVO_HUMOR):
        try:
            df_base = pd.read_csv(ARQUIVO_HUMOR)
            mask = (df_base['Data'] == hoje) & (df_base['Colaborador'].str.upper() == nome_colaborador.upper())
            if mask.any():
                return df_base.loc[mask, 'Humor'].values[0]
        except:
            pass
    return None
# ==========================================
# --- 4. LOGIN RENOVADO (SEM DELAY E SEM PISCAR) ---
# ==========================================
import extra_streamlit_components as stx
import streamlit.components.v1 as components

cookie_manager = stx.CookieManager()

if 'logado' not in st.session_state:
    st.session_state.update({'logado': False, 'usuario_nome': '', 'perfil': '', 'usuario_email': ''})

cookie_usuario = cookie_manager.get(cookie="usuario_logado")

# Auto-Login (Lê o cookie sem piscar a tela)
if cookie_usuario and not st.session_state['logado']:
    if cookie_usuario == 'admin' or cookie_usuario == 'gestor':
        st.session_state.update({'logado': True, 'usuario_nome': 'Gestor', 'perfil': 'admin', 'usuario_email': 'admin'})
        st.rerun()
    else:
        df_users = carregar_usuarios()
        if df_users is not None and cookie_usuario in df_users['email'].values:
            user_row = df_users[df_users['email'] == cookie_usuario]
            if not user_row.empty:
                nome_upper = user_row.iloc[0]['nome']
                st.session_state.update({'logado': True, 'usuario_nome': nome_upper, 'perfil': 'user', 'usuario_email': cookie_usuario})
                st.rerun()

# --- GRAVAÇÃO INVISÍVEL DO COOKIE ---
# Se ele logou mas o cookie ainda não foi salvo no navegador, salva agora SILENCIOSAMENTE no fundo
if st.session_state['logado'] and cookie_usuario != st.session_state['usuario_email']:
    components.html(f"""
    <script>
        var date = new Date();
        date.setTime(date.getTime() + (30*24*60*60*1000));
        document.cookie = "usuario_logado={st.session_state['usuario_email']}; expires=" + date.toUTCString() + "; path=/";
    </script>
    """, height=0)

# SÓ MOSTRA A TELA DE LOGIN SE NÃO ESTIVER LOGADO
if not st.session_state['logado']:
    
    # --- 1. CABEÇALHO EXCLUSIVO DA TELA DE LOGIN ---
    logo_html = "<h1 style='text-align: center; font-size: 70px; margin:0;'>🦁</h1>"
    if os.path.exists(LOGO_FILE):
        try:
            with open(LOGO_FILE, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode()
            logo_html = f'<div style="text-align: center;"><img src="data:image/png;base64,{encoded_string}" style="height: 100px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); margin-bottom: 15px;"></div>'
        except: pass
        
    st.markdown(f"""
    <div style="margin-top: 5vh; margin-bottom: 30px;">
        {logo_html}
        <p class="login-title">TEAM SOFISTAS</p>
        <p class="login-subtitle">Acesso Restrito | Analytics & Performance</p>
    </div>
    """, unsafe_allow_html=True)

    # --- 2. CENTRALIZANDO O FORMULÁRIO NA TELA ---
    c_vazio_esq, c_formulario, c_vazio_dir = st.columns([1, 1.5, 1])
    
    with c_formulario:
        tab_login, tab_senha = st.tabs(["🔑 Fazer Login", "📝 Cadastrar Senha"])

        with tab_login:
            with st.form("form_login"):
                st.info("Digite suas credenciais para acessar o painel.")
                email_login = st.text_input("E-mail corporativo").strip().lower()
                senha_login = st.text_input("Senha", type="password")
                submit_login = st.form_submit_button("Entrar", use_container_width=True)
                
                if submit_login:
                    if email_login == 'admin' or email_login == 'gestor':
                        if senha_login == SENHA_ADMIN:
                            st.session_state.update({'logado': True, 'usuario_nome': 'Gestor', 'perfil': 'admin', 'usuario_email': 'admin'})
                            st.rerun() # Troca a tela instantaneamente!
                        else:
                            st.error("❌ Senha do Gestor incorreta.")
                    else:
                        df_users = carregar_usuarios()
                        if df_users is not None and email_login in df_users['email'].values:
                            user_row = df_users[df_users['email'] == email_login]
                            senha_banco = str(user_row.iloc[0].get('senha', '')).strip()

                            if senha_banco == "" or senha_banco == "nan":
                                st.warning("⚠️ Você ainda não cadastrou uma senha. Clique na aba 'Cadastrar Senha'.")
                            elif senha_login == senha_banco:
                                nome_upper = user_row.iloc[0]['nome']
                                st.session_state.update({'logado': True, 'usuario_nome': nome_upper, 'perfil': 'user', 'usuario_email': email_login})
                                st.rerun() # Troca a tela instantaneamente!
                            else:
                                st.error("❌ Senha incorreta.")
                        else:
                            st.error("🚫 E-mail não encontrado na base da operação.")

        with tab_senha:
            if st.session_state.get('senha_criada_sucesso', False):
                st.success("✅ Senha registrada com sucesso!")
                st.info("👉 Por favor, clique na aba **'Fazer Login'** ao lado para acessar o sistema.")
                
                if st.button("Cadastrar outra senha", use_container_width=True):
                    st.session_state['senha_criada_sucesso'] = False
                    st.rerun()
            else:
                with st.form("form_nova_senha"):
                    st.info("Digite seu e-mail corporativo para cadastrar sua senha de acesso.")
                    email_cad = st.text_input("Seu E-mail").strip().lower()
                    nova_senha = st.text_input("Nova Senha", type="password")
                    confirma_senha = st.text_input("Confirme a Nova Senha", type="password")
                    submit_senha = st.form_submit_button("Salvar Minha Senha", use_container_width=True)
                    
                    if submit_senha:
                        if not email_cad or not nova_senha:
                            st.error("⚠️ Preencha todos os campos.")
                        elif nova_senha != confirma_senha:
                            st.error("⚠️ As senhas digitadas não coincidem!")
                        else:
                            df_users = carregar_usuarios()
                            if df_users is not None and email_cad in df_users['email'].values:
                                user_row = df_users[df_users['email'] == email_cad]
                                senha_registrada = str(user_row.iloc[0].get('senha', '')).strip()
                                
                                if senha_registrada != "" and senha_registrada != "nan":
                                    st.error("🔒 Este e-mail já possui uma senha cadastrada. Solicite o reset ao seu Gestor!")
                                else:
                                    if atualizar_senha(email_cad, nova_senha):
                                        st.session_state['senha_criada_sucesso'] = True
                                        st.rerun() 
                                    else:
                                        st.error("❌ Erro ao salvar no banco de dados.")
                            else:
                                st.error("🚫 E-mail não encontrado na base da operação.")

    st.markdown('<div class="dev-footer">Desenvolvido por Klebson Davi - Supervisor de Suporte Técnico</div>', unsafe_allow_html=True)
    st.stop()
# ==========================================
# --- 5. BARRA SUPERIOR E LÓGICA GLOBAL ---
# ==========================================
lista_periodos = listar_periodos_disponiveis()
opcoes_periodo = lista_periodos if lista_periodos else ["Nenhum histórico disponível"]

df_users_cadastrados = carregar_usuarios()
nome_logado = st.session_state['usuario_nome'].title() if st.session_state['usuario_nome'] != 'Gestor' else 'Gestor'

ativos_texto = f"👥 Usuários Ativos: {len(df_users_cadastrados)}" if (st.session_state['perfil'] == 'admin' and df_users_cadastrados is not None) else ""

logo_html = "<h1 style='margin:0; padding:0; font-size:40px;'>🦁</h1>"
if os.path.exists(LOGO_FILE):
    try:
        with open(LOGO_FILE, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode()
        logo_html = f'<img src="data:image/png;base64,{encoded_string}" style="height: 60px; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.2);">'
    except: pass
primeiro_nome = nome_logado.split()[0] if nome_logado and str(nome_logado).strip() else "Usuário"
st.markdown(f"""
<div class="top-banner">
    <div style="display: flex; align-items: center; gap: 20px;">
        {logo_html}
        <div>
            <h2>TEAM SOFISTAS</h2>
            <p class="sub-text">Analytics & Performance</p>
        </div>
    </div>
    <div style="text-align: right;">
        <h4>Olá, {primeiro_nome}! 👋</h4>
        <p class="sub-text" style="font-weight: bold !important;">{ativos_texto}</p>
    </div>
</div>
""", unsafe_allow_html=True)

c_periodo, c_vazio, c_sair = st.columns([3, 6, 1.5])

with c_periodo:
    periodo_selecionado = st.selectbox("📅 Selecione o Mês de Referência:", opcoes_periodo)
    
with c_sair:
    st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
    if st.button("🚪 Sair do Sistema", type="primary", use_container_width=True):
        st.session_state.update({'logado': False})
        # Apaga o cookie via JS e recarrega a página
        components.html("""
        <script>
            document.cookie = "usuario_logado=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
            setTimeout(function() { window.parent.location.reload(); }, 500);
        </script>
        """, height=0)

st.markdown("<hr style='margin-top: 5px; margin-bottom: 20px;'>", unsafe_allow_html=True)

tem_tam = False

if periodo_selecionado == "Nenhum histórico disponível":
    df_raw = None
    periodo_label = "Aguardando Upload"
else:
    df_hist_full = carregar_historico_completo()
    if df_hist_full is not None:
        df_raw = df_hist_full[df_hist_full['Periodo'] == periodo_selecionado].copy()
        if df_raw is not None and not df_raw.empty:
            df_raw = filtrar_por_usuarios_cadastrados(df_raw, df_users_cadastrados)
    else: df_raw = None
    periodo_label = periodo_selecionado

if df_raw is not None and not df_raw.empty:
    df_dados = df_raw.copy()
    df_dados['Colaborador'] = df_dados['Colaborador'].str.title()
    tem_tam = 'TAM' in df_dados['Indicador'].unique()
else: df_dados = None

perfil = st.session_state['perfil']
if df_dados is None and perfil == 'user':
    st.info(f"👋 Olá, **{nome_logado}**! Dados de **{periodo_label}** indisponíveis.")
    st.stop()


# ==========================================
# --- 6. GESTOR ---
# ==========================================
if perfil == 'admin':
    tabs = st.tabs(["🚦 Semáforo", "📈 Resumo Executivo", "🏆 Ranking Geral", "⏳ Evolução", "🔍 Indicadores", "⏱️ Produtividade (Chat & Voz)", "💰 Comissões", "📋 Tabela Geral", "🏖️ Férias Equipe", "⚙️ Admin", "⏰ Banco de Horas", "📝 Feedbacks GB", "🤖 Sofistas AI", "🎉 Celebrações"])    # ------------------ SEMÁFORO ------------------
    with tabs[0]: 
        if df_dados is not None and not df_dados.empty:
            st.markdown(f"### Resumo de Saúde: **{periodo_label}**")
            
            ignorar_pontualidade = st.checkbox("Recalcular Cards sem Pontualidade", value=False)

            if tem_tam:
                df_base = df_dados[df_dados['Indicador'] == 'TAM'][['Colaborador', 'Diamantes', 'Max. Diamantes']].set_index('Colaborador').copy()
                if ignorar_pontualidade:
                    df_pont = df_dados[df_dados['Indicador'] == 'PONTUALIDADE'][['Colaborador', 'Diamantes', 'Max. Diamantes']].set_index('Colaborador').copy()
                    df_base = df_base.subtract(df_pont, fill_value=0)
                df_base['% Atingimento'] = df_base.apply(lambda row: row['Diamantes'] / row['Max. Diamantes'] if row['Max. Diamantes'] > 0 else 0, axis=1)
                df_media_pessoas = df_base.reset_index()
            else:
                if ignorar_pontualidade:
                    df_calc = df_dados[df_dados['Indicador'] != 'PONTUALIDADE']
                else:
                    df_calc = df_dados
                df_media_pessoas = df_calc.groupby('Colaborador').agg({'Diamantes': 'sum', 'Max. Diamantes': 'sum'}).reset_index()
                df_media_pessoas['% Atingimento'] = df_media_pessoas.apply(lambda row: row['Diamantes'] / row['Max. Diamantes'] if row['Max. Diamantes'] > 0 else 0, axis=1)

            qtd_verde = len(df_media_pessoas[df_media_pessoas['% Atingimento'] >= 0.90]) 
            qtd_amarelo = len(df_media_pessoas[(df_media_pessoas['% Atingimento'] >= 0.80) & (df_media_pessoas['% Atingimento'] < 0.90)]) 
            qtd_vermelho = len(df_media_pessoas[df_media_pessoas['% Atingimento'] < 0.80]) 
            
            c1, c2, c3 = st.columns(3)
            
            html_card_excelencia = f"""<a href="#excelencia" class="card-link"><div class="card-excelencia"><div style="color: #666; font-size: 14px;">💎 Excelência <span style="font-size:11px; color:#003366;">(Ver detalhes ⬇)</span></div><div style="color: #003366; font-size: 26px; font-weight: 700; margin-top: -2px;">{qtd_verde}</div><div style="color: #003366; font-size: 13px; font-weight: bold; margin-top: 5px;">↑ &gt;=90%</div></div></a>"""
            c1.markdown(html_card_excelencia, unsafe_allow_html=True)
            html_card_meta = f"""<a href="#meta-batida" class="card-link"><div class="card-meta"><div style="color: #666; font-size: 14px;">🟢 Meta Batida <span style="font-size:11px; color:#2ecc71;">(Ver detalhes ⬇)</span></div><div style="color: #003366; font-size: 26px; font-weight: 700; margin-top: -2px;">{qtd_amarelo}</div><div style="color: #2ecc71; font-size: 13px; font-weight: bold; margin-top: 5px;">~ 80-89%</div></div></a>"""
            c2.markdown(html_card_meta, unsafe_allow_html=True)
            html_card_critico = f"""<a href="#atencao-prioritaria" class="card-link"><div class="card-critico"><div style="color: #666; font-size: 14px;">🔴 Crítico <span style="font-size:11px; color:#e74c3c;">(Ver detalhes ⬇)</span></div><div style="color: #003366; font-size: 26px; font-weight: 700; margin-top: -2px;">{qtd_vermelho}</div><div style="color: #e74c3c; font-size: 13px; font-weight: bold; margin-top: 5px;">↓ &lt;80%</div></div></a>"""
            c3.markdown(html_card_critico, unsafe_allow_html=True)

            
            df_dados_farol = df_dados.copy()
            df_dados_farol['Status_Farol'] = df_dados_farol['% Atingimento'].apply(classificar_farol)
            fig_farol = px.bar(df_dados_farol.groupby(['Indicador', 'Status_Farol']).size().reset_index(name='Qtd'), 
                               x='Indicador', y='Qtd', color='Status_Farol', text='Qtd',
                               color_discrete_map={'💎 Excelência': '#003366', '🟢 Meta Batida': '#2ecc71', '🔴 Crítico': '#e74c3c'})
            st.plotly_chart(fig_farol, use_container_width=True)
            st.markdown("---")

            st.markdown("### 🦁 Performance Global da Equipe")
            remove_pont = st.checkbox("Remover Pontualidade do Cálculo Global", value=False)
            total_dia_team = total_max_team = 0
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
                df_calc_team = df_dados[df_dados['Indicador'] != 'PONTUALIDADE'] if remove_pont else df_dados
                total_dia_team = df_calc_team['Diamantes'].sum()
                total_max_team = df_calc_team['Max. Diamantes'].sum()
            perc_team = (total_dia_team / total_max_team) if total_max_team > 0 else 0
            fig_team = go.Figure(go.Indicator(
                mode = "gauge+number", value = perc_team * 100, domain = {'x': [0, 1], 'y': [0, 1]},
                gauge = {
                    'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': 'white'}, 'bar': {'color': "#003366"},
                    'steps': [{'range': [0, 80], 'color': '#ffcccb'},{'range': [80, 90], 'color': '#fff4cc'},{'range': [90, 100], 'color': '#d9f7be'}],
                    'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': 100}
                }
            ))
            fig_team.update_layout(height=250, margin=dict(l=20, r=20, t=30, b=20))
            st.plotly_chart(fig_team, use_container_width=True)
            st.markdown("---")
            
            st.markdown('<div id="excelencia" style="padding-top: 20px;"></div>', unsafe_allow_html=True)
            st.subheader("💎 Destaques de Excelência (>= 90%)")
            df_exc = df_media_pessoas[df_media_pessoas['% Atingimento'] >= 0.90].sort_values(by='% Atingimento', ascending=False)
            if not df_exc.empty:
                df_exc_show = df_exc[['Colaborador', '% Atingimento']].copy()
                df_exc_show.columns = ['Colaborador', 'Resultado (TAM)']
                st.dataframe(df_exc_show.style.format({'Resultado (TAM)': '{:.2%}'}), use_container_width=True)
            else: st.info("Nenhum colaborador nesta faixa.")

            st.markdown('<div id="meta-batida" style="padding-top: 20px;"></div>', unsafe_allow_html=True)
            st.subheader("🟢 Atingiram a Meta (80% - 89%)")
            df_meta = df_media_pessoas[(df_media_pessoas['% Atingimento'] >= 0.80) & (df_media_pessoas['% Atingimento'] < 0.90)].sort_values(by='% Atingimento', ascending=False)
            if not df_meta.empty:
                df_meta_show = df_meta[['Colaborador', '% Atingimento']].copy()
                df_meta_show.columns = ['Colaborador', 'Resultado (TAM)']
                st.dataframe(df_meta_show.style.format({'Resultado (TAM)': '{:.2%}'}), use_container_width=True)
            else: st.info("Nenhum colaborador nesta faixa.")

            st.markdown('<div id="atencao-prioritaria" style="padding-top: 20px;"></div>', unsafe_allow_html=True)
            st.subheader("📋 Atenção Prioritária (< 80%)")
            df_atencao = df_media_pessoas[df_media_pessoas['% Atingimento'] < 0.80].sort_values(by='% Atingimento')
            if not df_atencao.empty:
                lista_detalhada = []
                for colab in df_atencao['Colaborador']:
                    dados_pessoa = df_dados[df_dados['Colaborador'] == colab]
                    media_pessoa = df_media_pessoas[df_media_pessoas['Colaborador'] == colab].iloc[0]['% Atingimento']
                    df_kpis_only = dados_pessoa[dados_pessoa['Indicador'] != 'TAM'] if tem_tam else dados_pessoa
                    
                    if not df_kpis_only.empty:
                        pior_kpi_row = df_kpis_only.loc[df_kpis_only['% Atingimento'].idxmin()]
                        nome_kpi_bonito = formatar_nome_visual(pior_kpi_row['Indicador'])
                        texto_pior = f"{nome_kpi_bonito} ({pior_kpi_row['% Atingimento']:.2%})"
                    else: texto_pior = "N/A"
                    lista_detalhada.append({'Colaborador': colab, 'Resultado (TAM)': media_pessoa, 'Status': '🔴 Crítico', 'Pior KPI p/ Focar': texto_pior})
                st.dataframe(pd.DataFrame(lista_detalhada).style.format({'Resultado (TAM)': '{:.2%}'}), use_container_width=True)
            else: st.success("🎉 Equipe performando bem! Ninguém abaixo de 80%.")

    # ------------------ RESUMO EXECUTIVO (INTELIGENTE) ------------------
    with tabs[1]:
        st.markdown(f"### 📈 Resumo Executivo: {periodo_label}")
        if df_dados is not None and not df_dados.empty:
            
            if tem_tam: df_media_pessoas = df_dados[df_dados['Indicador'] == 'TAM'][['Colaborador', '% Atingimento']].copy()
            else:
                df_media_pessoas = df_dados.groupby('Colaborador').agg({'Diamantes': 'sum', 'Max. Diamantes': 'sum'}).reset_index()
                df_media_pessoas['% Atingimento'] = df_media_pessoas.apply(lambda row: row['Diamantes'] / row['Max. Diamantes'] if row['Max. Diamantes'] > 0 else 0, axis=1)

            total_pessoas = len(df_media_pessoas)
            
            if total_pessoas > 0:
                media_geral_tam = df_media_pessoas['% Atingimento'].mean()
                qtd_verde = len(df_media_pessoas[df_media_pessoas['% Atingimento'] >= 0.90])
                qtd_amarelo = len(df_media_pessoas[(df_media_pessoas['% Atingimento'] >= 0.80) & (df_media_pessoas['% Atingimento'] < 0.90)])
                qtd_vermelho = len(df_media_pessoas[df_media_pessoas['% Atingimento'] < 0.80])
                
                media_csat = df_dados[df_dados['Indicador'] == 'CSAT']['% Atingimento'].mean() if 'CSAT' in df_dados['Indicador'].unique() else 0.0
                media_ir = df_dados[df_dados['Indicador'] == 'IR']['% Atingimento'].mean() if 'IR' in df_dados['Indicador'].unique() else 0.0
                media_ad = df_dados[df_dados['Indicador'] == 'ADERENCIA']['% Atingimento'].mean() if 'ADERENCIA' in df_dados['Indicador'].unique() else 0.0
                media_conf = df_dados[df_dados['Indicador'] == 'CONFORMIDADE']['% Atingimento'].mean() if 'CONFORMIDADE' in df_dados['Indicador'].unique() else 0.0
                
                # --- AGORA A BUSCA POR PONTO FORTE E GARGALO ANALISA TODOS OS INDICADORES SUBIDOS ---
                df_medias_kpis = df_dados[df_dados['Indicador'] != 'TAM'].groupby('Indicador')['% Atingimento'].mean().reset_index()
                melhor_kpi = df_medias_kpis.loc[df_medias_kpis['% Atingimento'].idxmax()] if not df_medias_kpis.empty else None
                pior_kpi = df_medias_kpis.loc[df_medias_kpis['% Atingimento'].idxmin()] if not df_medias_kpis.empty else None

                # --- COMPARAÇÃO HISTÓRICA DO MÊS ANTERIOR ---
                texto_comparacao = ""
                periodos_ord = listar_periodos_disponiveis()
                if periodo_label in periodos_ord:
                    idx_atual = periodos_ord.index(periodo_label)
                    if idx_atual + 1 < len(periodos_ord):
                        periodo_anterior = periodos_ord[idx_atual + 1]
                        df_hist_full_exec = carregar_historico_completo()
                        if df_hist_full_exec is not None:
                            if df_users_cadastrados is not None:
                                df_hist_full_exec = filtrar_por_usuarios_cadastrados(df_hist_full_exec, df_users_cadastrados)
                            df_ant = df_hist_full_exec[df_hist_full_exec['Periodo'] == periodo_anterior]
                            if not df_ant.empty:
                                if 'TAM' in df_ant['Indicador'].unique():
                                    media_anterior_tam = df_ant[df_ant['Indicador'] == 'TAM']['% Atingimento'].mean()
                                else:
                                    df_ant_calc = df_ant.groupby('Colaborador').agg({'Diamantes': 'sum', 'Max. Diamantes': 'sum'}).reset_index()
                                    df_ant_calc['% Atingimento'] = df_ant_calc.apply(lambda row: row['Diamantes'] / row['Max. Diamantes'] if row['Max. Diamantes'] > 0 else 0, axis=1)
                                    media_anterior_tam = df_ant_calc['% Atingimento'].mean()
                                
                                variacao = media_geral_tam - media_anterior_tam
                                if variacao > 0.001:
                                    texto_comparacao = f" Em comparação ao mês anterior ({periodo_anterior}), tivemos um *crescimento de {variacao*100:.1f} p.p.* na performance da equipe (era {media_anterior_tam:.1%}). 🚀"
                                elif variacao < -0.001:
                                    texto_comparacao = f" Em comparação ao mês anterior ({periodo_anterior}), tivemos uma *queda de {abs(variacao)*100:.1f} p.p.* na performance da equipe (era {media_anterior_tam:.1%}). 📉"
                                else:
                                    texto_comparacao = f" Em comparação ao mês anterior ({periodo_anterior}), mantivemos a performance estável (era {media_anterior_tam:.1%}). ⚖️"

                # Identificação de Operadores Específicos
                try:
                    top_operador = df_media_pessoas.loc[df_media_pessoas['% Atingimento'].idxmax()]
                    nome_top = top_operador['Colaborador'].title()
                    nota_top = top_operador['% Atingimento']
                except:
                    nome_top = "Indisponível"
                    nota_top = 0.0

                try:
                    pior_operador = df_media_pessoas.loc[df_media_pessoas['% Atingimento'].idxmin()]
                    nome_pior = pior_operador['Colaborador'].title()
                    nota_pior = pior_operador['% Atingimento']
                except:
                    nome_pior = "Indisponível"
                    nota_pior = 0.0
                
                nome_ofensor_kpi = "N/A"
                nota_ofensor_kpi = 0.0
                if pior_kpi is not None:
                    df_pior_kpi = df_dados[df_dados['Indicador'] == pior_kpi['Indicador']]
                    if not df_pior_kpi.empty:
                        ofensor_kpi = df_pior_kpi.loc[df_pior_kpi['% Atingimento'].idxmin()]
                        nome_ofensor_kpi = ofensor_kpi['Colaborador'].title()
                        nota_ofensor_kpi = ofensor_kpi['% Atingimento']

                nome_pior_formatado = nome_pior.split(" ")[0] if nome_pior != "Indisponível" else "foco"
                nome_top_formatado = nome_top.split(" ")[0] if nome_top != "Indisponível" else "foco"
                pior_kpi_str = formatar_nome_visual(pior_kpi['Indicador']) if pior_kpi is not None else "gargalos"

                # Geração da String Formatada
                texto_resumo = f"""📊 *RESUMO EXECUTIVO | {periodo_label} - TEAM SOFISTAS* 📊

*1️⃣ VISÃO GERAL DA OPERAÇÃO*
Neste ciclo, a equipe fechou com um Resultado Geral médio de *{media_geral_tam:.1%}*.{texto_comparacao}
Tivemos um total de {total_pessoas} operadores avaliados, distribuídos da seguinte forma:
▪️ 💎 Excelência (>= 90%): {qtd_verde} op. ({qtd_verde/total_pessoas:.0%})
▪️ 🟢 Meta Batida (80% a 89%): {qtd_amarelo} op. ({qtd_amarelo/total_pessoas:.0%})
▪️ 🔴 Atenção Prioritária (< 80%): {qtd_vermelho} op. ({qtd_vermelho/total_pessoas:.0%})

*2️⃣ INDICADORES PRINCIPAIS DA LIDERANÇA*
▪️ CSAT Médio: {media_csat:.1%}
▪️ IR (Resolução) Médio: {media_ir:.1%}
▪️ Aderência Média: {media_ad:.1%}
▪️ Conformidade Média: {media_conf:.1%}

*3️⃣ ANÁLISE GERAL E DESTAQUES*
🏆 *Top Performer:* O operador *{nome_top}* entregou o melhor resultado da equipe, atingindo *{nota_top:.1%}* de performance global. 
🎯 *Foco de Desenvolvimento:* Por outro lado, *{nome_pior}* obteve o menor resultado do ciclo (*{nota_pior:.1%}*) e será priorizado no acompanhamento (PDI).
"""
                if melhor_kpi is not None and pior_kpi is not None:
                    texto_resumo += f"""📈 *Ponto Forte da Equipe:* {formatar_nome_visual(melhor_kpi['Indicador'])} atingiu o melhor desempenho (Média: {melhor_kpi['% Atingimento']:.1%}).
⚠️ *Gargalo Coletivo:* O ofensor geral que mais exigirá atenção de todos os indicadores é {formatar_nome_visual(pior_kpi['Indicador'])} (Média: {pior_kpi['% Atingimento']:.1%}). O operador *{nome_ofensor_kpi}* foi o mais impactado individualmente neste indicador ({nota_ofensor_kpi:.1%}).
"""
                texto_resumo += f"""
*4️⃣ PRÓXIMOS PASSOS*
O foco da liderança para o próximo ciclo será atuar diretamente na base crítica, com PDI prioritário focado em {nome_pior_formatado}, além de rodadas de calibração para alavancar os números de {pior_kpi_str}. Paralelamente, manteremos o reconhecimento de alto desempenho voltado a {nome_top_formatado} e demais Destaques para engajar o restante do time."""

                st.info("💡 **Dica de Ouro:** O texto abaixo foi gerado automaticamente e já está **formatado para o WhatsApp**. Copie e cole na sua janela de conversa com a sua coordenação!")
                st.code(texto_resumo, language="markdown")
                
                # --- NOVO: MURAL DO TIME (GTALK) ---
                st.markdown("---")
                st.markdown("#### 📢 Mural do Time (GTalk/WhatsApp)")
                st.caption("Copie e cole no grupo da equipe para celebrar os resultados!")
                
                # Top 3
                df_rank = df_media_pessoas.sort_values(by='% Atingimento', ascending=False).reset_index(drop=True)
                top1 = df_rank.iloc[0]['Colaborador'] if len(df_rank) > 0 else "N/A"
                top2 = df_rank.iloc[1]['Colaborador'] if len(df_rank) > 1 else "N/A"
                top3 = df_rank.iloc[2]['Colaborador'] if len(df_rank) > 2 else "N/A"

                msg_time = f"""Fala, Time! 🦁🚀

Passando para fechar a régua do mês de *{periodo_label}*!
Queria agradecer o empenho de cada um. Sabemos que a operação é dinâmica, mas o foco de vocês faz toda a diferença.

🏆 *PODIUM DO MÊS - DESTAQUES* 🏆
🥇 *{top1.title()}*
🥈 *{top2.title()}*
🥉 *{top3.title()}*

Parabéns aos destaques! Vocês mandaram muito bem! 👏

Para quem não chegou lá dessa vez: o jogo reinicia agora. Vamos ajustar os ponteiros, focar na qualidade (CSAT/Conformidade) e buscar esse topo no próximo ciclo. Conto com vocês!

O detalhe individual já está atualizado no painel.
Vamos com tudo! 🔥"""
                st.code(msg_time, language="markdown")

            else:
                st.info("Aguardando upload de dados para calcular o resumo executivo.")
        else:
            st.info("Nenhum dado disponível neste período.")
   
    
        # ==========================================================
        # 📡 RADAR WFM INTERATIVO (VISÃO DO GESTOR)
        # ==========================================================
        st.markdown("---")
        
        # Coloca o título e o calendário lado a lado
        c_radar_title, c_radar_date = st.columns([3, 1])
        with c_radar_title:
            st.markdown("### 📡 Radar WFM da Equipe")
        with c_radar_date:
            data_radar_selecionada = st.date_input("Escolha o dia:", format="DD/MM/YYYY")
            
        data_radar_str = data_radar_selecionada.strftime("%d/%m/%Y")
        
        df_radar = gerar_radar_wfm_data(data_radar_str)
        
        if df_radar is not None and not df_radar.empty:
            # Conta a galera de forma automática
            qtd_trabalho = len(df_radar[df_radar['Status'].isin(['Trabalhando', 'Treinamento'])])
            qtd_folga = len(df_radar[df_radar['Status'] == 'Folga'])
            qtd_ausentes = len(df_radar[df_radar['Status'].isin(['Férias', 'Saúde'])])
            
            # Desenha os 3 cartões de resumo
            c_wfm1, c_wfm2, c_wfm3 = st.columns(3)
            c_wfm1.markdown(f"""<div style='background:#FFFFFF; padding:15px; border-radius:12px; border-left:5px solid #2ecc71; box-shadow:0 4px 10px rgba(0,0,0,0.05);'>
            <p style='margin:0; color:#6B7280; font-size:0.9em; font-weight:600;'>💻 Logados / Treinamento</p>
            <h2 style='margin:0; color:#111827;'>{qtd_trabalho}</h2></div>""", unsafe_allow_html=True)
            
            c_wfm2.markdown(f"""<div style='background:#FFFFFF; padding:15px; border-radius:12px; border-left:5px solid #3498db; box-shadow:0 4px 10px rgba(0,0,0,0.05);'>
            <p style='margin:0; color:#6B7280; font-size:0.9em; font-weight:600;'>🏖️ Folgas</p>
            <h2 style='margin:0; color:#111827;'>{qtd_folga}</h2></div>""", unsafe_allow_html=True)
            
            c_wfm3.markdown(f"""<div style='background:#FFFFFF; padding:15px; border-radius:12px; border-left:5px solid #e74c3c; box-shadow:0 4px 10px rgba(0,0,0,0.05);'>
            <p style='margin:0; color:#6B7280; font-size:0.9em; font-weight:600;'>✈️ Férias / Saúde</p>
            <h2 style='margin:0; color:#111827;'>{qtd_ausentes}</h2></div>""", unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Exibe a tabela interativa com o map colorido
            st.dataframe(
                df_radar.style.map(
                    lambda x: 'color: #2ecc71; font-weight:bold;' if x == 'Trabalhando' 
                    else ('color: #e74c3c; font-weight:bold;' if x in ['Férias', 'Saúde'] else 'color: #3498db; font-weight:bold;'), 
                    subset=['Status']
                ), 
                use_container_width=True, 
                hide_index=True
            )
        else:
            st.info(f"Nenhuma escala encontrada para o dia {data_radar_str}. Verifique se a base de usuários está populada e se o arquivo WFM cobre este período.")

        # ==========================================================
        # 🌡️ PAINEL DO GESTOR: TERMÔMETRO DA EQUIPE
        # ==========================================================
        st.markdown("---")
        st.markdown("### 🌡️ Termômetro da Equipe (Clima de Hoje)")
        
        df_humor = carregar_base_humor()
        
        if df_humor is not None and not df_humor.empty:
            hoje_str = datetime.now().strftime("%d/%m/%Y")
            df_hoje = df_humor[df_humor['Data'] == hoje_str]
            
            if not df_hoje.empty:
                # Alerta Inteligente para o Gestor
                alertas = df_hoje[df_hoje['Humor'].isin(["😡 Estressado", "😫 Cansado"])]
                if not alertas.empty:
                    st.warning(f"⚠️ **Atenção Líder:** {len(alertas)} colaborador(es) reportaram estar sob estresse ou cansaço hoje. Considere uma abordagem mais acolhedora.")
                else:
                    st.success("✅ Excelente! Ninguém reportou estresse extremo ou cansaço até o momento.")
                
                c_grafico, c_lista = st.columns([1, 2])
                
                with c_grafico:
                    st.markdown("##### 📊 Resumo do Dia")
                    # Conta quantos de cada humor
                    contagem_humor = df_hoje['Humor'].value_counts().reset_index()
                    contagem_humor.columns = ['Humor', 'Operadores']
                    st.dataframe(contagem_humor, use_container_width=True, hide_index=True)
                    
                with c_lista:
                    st.markdown("##### 👥 Quem é Quem")
                    
                    # Traz o nome, humor e HORA, ordenando pelos estressados primeiro
                    ordem_peso = {"😡 Estressado": 1, "😫 Cansado": 2, "😐 Normal": 3, "🙂 Bem": 4, "🤩 Incrível": 5}
                    df_hoje_sorted = df_hoje.copy()
                    df_hoje_sorted['Peso'] = df_hoje_sorted['Humor'].map(ordem_peso)
                    
                    # Ordena pela gravidade do humor e depois pela hora do registro
                    if 'Hora' in df_hoje_sorted.columns:
                        df_hoje_sorted = df_hoje_sorted.sort_values(by=['Peso', 'Hora'], ascending=[True, False])
                        df_hoje_sorted = df_hoje_sorted[['Hora', 'Colaborador', 'Humor']] # Define a ordem visual das colunas
                    else:
                        df_hoje_sorted = df_hoje_sorted.sort_values(by='Peso').drop(columns=['Peso', 'Data'])
                    
                    st.dataframe(df_hoje_sorted, use_container_width=True, hide_index=True)
        # --- 🧠 GERADOR DE INSIGHTS FCAR (IA) ---
        st.markdown("---")
        st.markdown("### 🧠 Análise Estratégica da Operação (Modelo FCAR)")
        st.write("Gere relatórios automatizados no formato Fato, Causa, Ação e Resultado para colar no sistema oficial da empresa.")
        
        contexto_fcar = st.text_area("O que você observou na operação neste período?", placeholder="Ex: A equipe teve muitas falhas de login no sistema X, o que aumentou nosso Tempo Médio de Atendimento...")
        
        if st.button("🚀 Gerar Insight FCAR da Equipe", use_container_width=True):
            if contexto_fcar.strip() == "":
                st.warning("⚠️ Escreva um breve contexto acima para a IA poder analisar!")
            else:
                with st.spinner("Processando dados e gerando análise executiva..."):
                    try:
                        # Prompt blindado para gerar o modelo FCAR com perfeição corporativa
                        prompt_fcar = f"""
                        Atue como um Coordenador de Operações de Suporte Técnico de Alta Performance.
                        A partir da minha observação abaixo, estruture um relatório gerencial utilizando ESTRITAMENTE a metodologia FCAR (Fato, Causa, Ação, Resultado).
                        
                        Minha observação do cenário atual: "{contexto_fcar}"
                        
                        Regras de Ouro:
                        - Use linguagem corporativa, analítica e objetiva.
                        - O 'Fato' deve ser baseado no que eu disse, sem invenções.
                        - A 'Causa' deve ser uma hipótese técnica e lógica.
                        - A 'Ação' deve conter de 2 a 3 passos táticos para a gestão executar.
                        - O 'Resultado' deve prever o impacto ou a meta de recuperação.
                        
                        Retorne APENAS a estrutura abaixo pronta para copiar e colar:
                        
                        **F (Fato):** [Seu texto]
                        
                        **C (Causa):** [Seu texto]
                        
                        **A (Ação):** - [Ação 1]
                        - [Ação 2]
                        
                        **R (Resultado Esperado):** [Seu texto]
                        """
                        
                        # Chama a IA (usando o mesmo modelo já configurado no seu sistema)
                        import google.generativeai as genai
                        
                        # Faz o sistema varrer a sua API e pegar o primeiro modelo de texto válido
                        nome_modelo_valido = None
                        for m in genai.list_models():
                            if 'generateContent' in m.supported_generation_methods:
                                nome_modelo_valido = m.name
                                break
                        
                        if nome_modelo_valido:
                            modelo_ia = genai.GenerativeModel(nome_modelo_valido)
                            resposta_fcar = modelo_ia.generate_content(prompt_fcar)
                        else:
                            st.error("Nenhum modelo de texto encontrado na sua chave de API.")
                        
                        # Caixinha Clean Glass para exibir o resultado com estilo
                        st.markdown("<div style='background-color: #FFFFFF; padding: 25px; border-radius: 20px; border-left: 6px solid #F37021; box-shadow: 0 8px 24px rgba(0,0,0,0.04); margin-top: 15px;'>", unsafe_allow_html=True)
                        st.markdown(resposta_fcar.text)
                        st.markdown("</div>", unsafe_allow_html=True)
                        
                    except Exception as e:
                        st.error(f"Erro ao conectar com a IA: {e}")
    # ------------------ RANKING ------------------
    with tabs[2]:
        st.markdown(f"### 🏆 Ranking Geral (Consolidado)")
        recalcular_ranking = st.checkbox("Visualizar Ranking sem Pontualidade", value=False)
        if df_dados is not None:
            if tem_tam: 
                df_rank = df_dados[df_dados['Indicador'] == 'TAM'][['Colaborador', 'Diamantes', 'Max. Diamantes']].set_index('Colaborador').copy()
                if recalcular_ranking:
                    df_pont = df_dados[df_dados['Indicador'] == 'PONTUALIDADE'][['Colaborador', 'Diamantes', 'Max. Diamantes']].set_index('Colaborador').copy()
                    df_rank = df_rank.subtract(df_pont, fill_value=0)
                df_rank['Resultado'] = df_rank.apply(lambda row: row['Diamantes'] / row['Max. Diamantes'] if row['Max. Diamantes'] > 0 else 0, axis=1)
                df_rank = df_rank.reset_index()
            else: 
                if recalcular_ranking:
                    df_calc = df_dados[df_dados['Indicador'] != 'PONTUALIDADE']
                else:
                    df_calc = df_dados
                df_rank = df_calc.groupby('Colaborador').agg({'Diamantes':'sum', 'Max. Diamantes':'sum'}).reset_index()
                df_rank['Resultado'] = df_rank.apply(lambda x: x['Diamantes']/x['Max. Diamantes'] if x['Max. Diamantes']>0 else 0, axis=1)
            
            df_rank = df_rank.sort_values(by='Resultado', ascending=False).reset_index(drop=True)
            
            medalhas = []
            for i in range(len(df_rank)):
                if i == 0: medalhas.append("🥇 1º Lugar")
                elif i == 1: medalhas.append("🥈 2º Lugar")
                elif i == 2: medalhas.append("🥉 3º Lugar")
                else: medalhas.append(f"🏅 {i+1}º Lugar")
            df_rank.insert(0, 'Posição', medalhas)
            
            cols_show = ['Posição', 'Colaborador', 'Resultado']
            format_dict = {'Resultado': lambda x: f"{x:.2%}" if pd.notnull(x) else "-"}
            
            if 'Diamantes' in df_rank.columns:
                df_rank.rename(columns={'Diamantes': '💎 Diamantes Válidos', 'Max. Diamantes': '🏆 Máx. Diamantes'}, inplace=True)
                cols_show.insert(2, '💎 Diamantes Válidos')
                cols_show.insert(3, '🏆 Máx. Diamantes')
                format_dict['💎 Diamantes Válidos'] = '{:.0f}'
                format_dict['🏆 Máx. Diamantes'] = '{:.0f}'
                
            st.dataframe(df_rank[cols_show].style.format(format_dict).background_gradient(subset=['Resultado'], cmap='RdYlGn'), use_container_width=True, hide_index=True, height=600)

    # ------------------ EVOLUÇÃO TEMPORAL ------------------
    with tabs[3]:
        st.markdown("### ⏳ Evolução Temporal (Qualidade)")
        df_hist = carregar_historico_completo()
        
        df_op_hist = carregar_historico_operacional()
        df_voz_hist = carregar_historico_voz()
        
        if df_hist is not None:
            if df_users_cadastrados is not None: df_hist = filtrar_por_usuarios_cadastrados(df_hist, df_users_cadastrados)
            df_hist['Colaborador'] = df_hist['Colaborador'].str.title()
            lista_colabs = sorted(df_hist['Colaborador'].unique())
            if lista_colabs:
                colab_sel = st.selectbox("Selecione o Colaborador para análise histórica:", lista_colabs)
                
                df_hist_user = df_hist[df_hist['Colaborador'] == colab_sel].copy()
                if not df_hist_user.empty:
                    df_hist_user['Indicador'] = df_hist_user['Indicador'].apply(formatar_nome_visual)
                    fig_heat = px.density_heatmap(df_hist_user, x="Periodo", y="Indicador", z="% Atingimento", text_auto=False, title=f"Mapa de Calor de Qualidade: {colab_sel}", color_continuous_scale="RdYlGn", range_color=[0.6, 1.0])
                    fig_heat.update_traces(texttemplate="%{z:.1%}", textfont={"size":12})
                    st.plotly_chart(fig_heat, use_container_width=True)
                else: st.warning("Sem dados de qualidade.")
                
                st.markdown("---")
                st.markdown("### 📈 Evolução Histórica de Produtividade (TMA)")
                c_line1, c_line2 = st.columns(2)
                
                if df_op_hist is not None:
                    df_op_user_hist = df_op_hist[df_op_hist['Colaborador'].apply(normalizar_chave) == normalizar_chave(colab_sel)].copy()
                    if not df_op_user_hist.empty:
                        df_op_user_hist['Data_Ord'] = pd.to_datetime(df_op_user_hist['Periodo'], format='%m/%Y', errors='coerce')
                        df_op_user_hist = df_op_user_hist.sort_values(by='Data_Ord')
                        
                        with c_line1:
                            fig_line_chat = px.line(df_op_user_hist, x='Periodo', y='TMA_seg', title='Evolução TMA Chat', markers=True, text='TMA_Formatado')
                            fig_line_chat.add_hline(y=1200, line_dash="dash", line_color="red", annotation_text="Meta (20m)")
                            fig_line_chat.update_traces(textposition="top center")
                            fig_line_chat.update_yaxes(visible=False)
                            st.plotly_chart(fig_line_chat, use_container_width=True)
                
                if df_voz_hist is not None:
                    df_voz_user_hist = df_voz_hist[df_voz_hist['Colaborador'].apply(normalizar_chave) == normalizar_chave(colab_sel)].copy()
                    if not df_voz_user_hist.empty:
                        df_voz_user_hist['Data_Ord'] = pd.to_datetime(df_voz_user_hist['Periodo'], format='%m/%Y', errors='coerce')
                        df_voz_user_hist = df_voz_user_hist.sort_values(by='Data_Ord')
                        
                        with c_line2:
                            fig_line_voz = px.line(df_voz_user_hist, x='Periodo', y='TMA_seg', title='Evolução TMA Voz', markers=True, text='TMA_Formatado', color_discrete_sequence=['#8e44ad'])
                            fig_line_voz.add_hline(y=420, line_dash="dash", line_color="red", annotation_text="Meta (7m)")
                            fig_line_voz.update_traces(textposition="top center")
                            fig_line_voz.update_yaxes(visible=False)
                            st.plotly_chart(fig_line_voz, use_container_width=True)

            else: st.warning("Histórico vazio após filtro.")
        else: st.info("Histórico vazio.")

    # ------------------ INDICADORES ------------------
    with tabs[4]:
        if df_dados is not None:
            st.markdown("### 🔬 Detalhe por Indicador")
            df_viz = df_dados.copy()
            df_viz['Indicador'] = df_viz['Indicador'].apply(formatar_nome_visual)
            for kpi in sorted(df_viz['Indicador'].unique()):
                with st.expander(f"📊 Ranking: {kpi}"):
                    df_kpi = df_viz[df_viz['Indicador'] == kpi].sort_values(by='% Atingimento', ascending=True)
                    fig_rank = px.bar(df_kpi, x='% Atingimento', y='Colaborador', orientation='h', text_auto='.1%', color='% Atingimento', color_continuous_scale=['#e74c3c', '#f1c40f', '#2ecc71'])
                    fig_rank.add_vline(x=0.8, line_dash="dash", line_color="black")
                    st.plotly_chart(fig_rank, use_container_width=True, key=f"chart_rank_{kpi}")
                    
    # ------------------ PRODUTIVIDADE (CHAT E VOZ) ------------------
    with tabs[5]:
        st.markdown("### ⏱️ Produtividade Operacional")
        
        tb_chat, tb_voz = st.tabs(["💬 Canal Chat", "📞 Canal Voz"])
        
        # --- TAB CHAT ---
        with tb_chat:
            df_op_hist = carregar_historico_operacional()
            if df_op_hist is not None:
                df_op_atual = df_op_hist[df_op_hist['Periodo'] == periodo_label].copy()
                if not df_op_atual.empty:
                    if df_users_cadastrados is not None:
                        lista_vip = df_users_cadastrados['nome'].unique()
                        df_op_atual = df_op_atual[df_op_atual['Colaborador'].apply(normalizar_chave).isin(lista_vip)]
                    
                    df_op_atual['Colaborador'] = df_op_atual['Colaborador'].str.title()
                    
                    c1, c2 = st.columns(2)
                    with c1:
                        df_vol = df_op_atual.sort_values('Atendimentos', ascending=True)
                        fig_vol = px.bar(df_vol, x='Atendimentos', y='Colaborador', orientation='h', 
                                         title='💬 Volume de Chats Atendidos', text='Atendimentos',
                                         color='Atendimentos', color_continuous_scale='Blues')
                        fig_vol.update_traces(textposition='outside', textfont_size=12)
                        fig_vol.update_layout(coloraxis_showscale=False, margin=dict(l=10, r=50, t=40, b=20))
                        fig_vol.update_xaxes(visible=False)
                        fig_vol.update_yaxes(title="")
                        st.plotly_chart(fig_vol, use_container_width=True)
                    with c2:
                        df_tma = df_op_atual.sort_values('TMA_seg', ascending=False)
                        fig_tma = px.bar(df_tma, x='TMA_seg', y='Colaborador', orientation='h', 
                                         title='⏱️ Tempo Médio de Atendimento (TMA Chat)', text='TMA_Formatado',
                                         color='TMA_seg', color_continuous_scale=['#2ecc71', '#f1c40f', '#e74c3c'])
                        fig_tma.add_vline(x=1200, line_dash="dash", line_color="red", annotation_text="Meta (20m)", annotation_position="top right")
                        fig_tma.update_traces(textposition='outside', textfont_size=12)
                        fig_tma.update_layout(coloraxis_showscale=False, margin=dict(l=10, r=50, t=40, b=20))
                        fig_tma.update_xaxes(visible=False)
                        fig_tma.update_yaxes(title="")
                        st.plotly_chart(fig_tma, use_container_width=True)
                        
                    st.markdown("#### 📋 Tabela de Produtividade (Chat)")
                    st.dataframe(df_op_atual[['Colaborador', 'Atendimentos', 'TMA_Formatado']].rename(columns={'Atendimentos': 'Chats Atendidos', 'TMA_Formatado': 'TMA Chat (mm:ss)'}), use_container_width=True, hide_index=True)
                else:
                    st.info("Nenhum dado de produtividade de Chat para este período. Faça o upload na aba Admin.")
            else:
                st.info("Nenhum histórico de produtividade de Chat encontrado. Faça o upload na aba Admin.")
                
        # --- TAB VOZ ---
        with tb_voz:
            df_voz_hist = carregar_historico_voz()
            if df_voz_hist is not None:
                df_voz_atual = df_voz_hist[df_voz_hist['Periodo'] == periodo_label].copy()
                if not df_voz_atual.empty:
                    if df_users_cadastrados is not None:
                        lista_vip = df_users_cadastrados['nome'].unique()
                        df_voz_atual = df_voz_atual[df_voz_atual['Colaborador'].apply(normalizar_chave).isin(lista_vip)]
                    
                    df_voz_atual['Colaborador'] = df_voz_atual['Colaborador'].str.title()
                    
                    c3, c4 = st.columns(2)
                    with c3:
                        df_vol_v = df_voz_atual.sort_values('Atendimentos', ascending=True)
                        fig_vol_v = px.bar(df_vol_v, x='Atendimentos', y='Colaborador', orientation='h', 
                                         title='📞 Volume de Ligações Atendidas', text='Atendimentos',
                                         color='Atendimentos', color_continuous_scale='Purples')
                        fig_vol_v.update_traces(textposition='outside', textfont_size=12)
                        fig_vol_v.update_layout(coloraxis_showscale=False, margin=dict(l=10, r=50, t=40, b=20))
                        fig_vol_v.update_xaxes(visible=False)
                        fig_vol_v.update_yaxes(title="")
                        st.plotly_chart(fig_vol_v, use_container_width=True)
                    with c4:
                        df_tma_v = df_voz_atual.sort_values('TMA_seg', ascending=False)
                        fig_tma_v = px.bar(df_tma_v, x='TMA_seg', y='Colaborador', orientation='h', 
                                         title='⏱️ Tempo Médio de Atendimento (TMA Voz)', text='TMA_Formatado',
                                         color='TMA_seg', color_continuous_scale=['#2ecc71', '#f1c40f', '#e74c3c'])
                        fig_tma_v.add_vline(x=420, line_dash="dash", line_color="red", annotation_text="Meta (7m)", annotation_position="top right")
                        fig_tma_v.update_traces(textposition='outside', textfont_size=12)
                        fig_tma_v.update_layout(coloraxis_showscale=False, margin=dict(l=10, r=50, t=40, b=20))
                        fig_tma_v.update_xaxes(visible=False)
                        fig_tma_v.update_yaxes(title="")
                        st.plotly_chart(fig_tma_v, use_container_width=True)
                        
                    st.markdown("#### 📋 Tabela de Produtividade (Voz)")
                    st.dataframe(df_voz_atual[['Colaborador', 'Atendimentos', 'TMA_Formatado']].rename(columns={'Atendimentos': 'Ligações Atendidas', 'TMA_Formatado': 'TMA Voz (mm:ss)'}), use_container_width=True, hide_index=True)
                else:
                    st.info("Nenhum dado de produtividade de Voz para este período. Faça o upload na aba Admin.")
            else:
                st.info("Nenhum histórico de produtividade de Voz encontrado. Faça o upload na aba Admin.")

    # ------------------ COMISSÕES ------------------
    with tabs[6]:
        st.markdown(f"### 💰 Relatório de Comissões")
        if df_dados is not None:
            st.info("ℹ️ Regra: R$ 0,50 por Diamante. **Trava:** Conformidade >= 92%.")
            lista_comissoes = []
            df_calc = df_dados.copy()
            df_calc['Colaborador_Key'] = df_calc['Colaborador'].str.upper()
            
            for colab in df_calc['Colaborador_Key'].unique():
                df_user = df_calc[df_calc['Colaborador_Key'] == colab]
                
                total_diamantes = df_user[df_user['Indicador'] == 'TAM'].iloc[0]['Diamantes'] if tem_tam and not df_user[df_user['Indicador'] == 'TAM'].empty else df_user['Diamantes'].sum()
                
                row_conf = df_user[df_user['Indicador'] == 'CONFORMIDADE']
                tem_conf = not row_conf.empty
                conf_val = row_conf.iloc[0]['% Atingimento'] if tem_conf else None
                
                desconto = 0
                obs = "✅ Elegível"
                
                if not tem_conf:
                    obs = "⚠️ Aguardando Conformidade"
                elif conf_val is not None and round(conf_val, 4) < 0.92:
                    row_pont = df_user[df_user['Indicador'] == 'PONTUALIDADE']
                    if not row_pont.empty:
                        desconto = row_pont.iloc[0]['Diamantes'] if 'Diamantes' in row_pont.columns else 0
                        obs = "⚠️ Penalidade (Pontualidade)"
                    else: obs = "⚠️ Conformidade Baixa"
                
                diamantes_validos = total_diamantes - desconto
                valor_final = diamantes_validos * 0.50
                
                lista_comissoes.append({
                    "Colaborador": colab.title(),
                    "Conformidade": conf_val,
                    "Total Diamantes": int(total_diamantes),
                    "Desconto": int(desconto),
                    "Diamantes Líquidos": int(diamantes_validos),
                    "A Pagar (R$)": valor_final,
                    "Status": obs
                })
            
            df_comissao = pd.DataFrame(lista_comissoes)
            df_comissao['Conformidade'] = df_comissao['Conformidade'].apply(lambda x: f"{x:.2%}" if pd.notnull(x) else "Aguardando")
            
            st.dataframe(
                df_comissao.style.format({"A Pagar (R$)": "R$ {:.2f}"}).background_gradient(subset=['A Pagar (R$)'], cmap='Greens'), 
                use_container_width=True, 
                height=600
            )
            st.download_button("⬇️ Baixar CSV", df_comissao.to_csv(index=False).encode('utf-8'), "comissoes.csv", "text/csv")

    # ------------------ MAPA DE RESULTADOS ------------------
    with tabs[7]: 
        if df_dados is not None:
            c1, c2 = st.columns([3, 1])
            with c1: st.markdown(f"### Mapa de Resultados: {periodo_label}")
            with c2: filtro = st.multiselect("🔍 Filtrar:", df_dados['Colaborador'].unique())
            df_show = df_dados if not filtro else df_dados[df_dados['Colaborador'].isin(filtro)]
            df_show_visual = df_show.copy()
            df_show_visual['Indicador'] = df_show_visual['Indicador'].apply(formatar_nome_visual)
            pivot = df_show_visual.pivot_table(index='Colaborador', columns='Indicador', values='% Atingimento').fillna(0.0)
            st.dataframe(pivot.style.background_gradient(cmap='RdYlGn', vmin=0.7, vmax=1.0).format("{:.2%}"), use_container_width=True, height=600)

    # ------------------ FÉRIAS ------------------
    with tabs[8]:
        st.markdown("### 🏖️ Férias da Equipe")
        if df_users_cadastrados is not None:
            mapa_meses = {
                '01': 'Janeiro', '02': 'Fevereiro', '03': 'Março', '04': 'Abril',
                '05': 'Maio', '06': 'Junho', '07': 'Julho', '08': 'Agosto',
                '09': 'Setembro', '10': 'Outubro', '11': 'Novembro', '12': 'Dezembro'
            }
            
            try:
                mes_num = periodo_selecionado.split('/')[0]
                nome_mes = mapa_meses.get(mes_num, "")
            except:
                mes_num = ""
                nome_mes = ""

            df_f = df_users_cadastrados[['nome', 'ferias']].copy()
            df_f['nome'] = df_f['nome'].str.title()
            
            def esta_de_ferias(texto_ferias, mes_num, nome_mes):
                t = str(texto_ferias).lower()
                termos = []
                if nome_mes: 
                    termos.append(nome_mes.lower())
                    try: termos.append(unicodedata.normalize('NFKD', nome_mes).encode('ASCII', 'ignore').decode('utf-8').lower())
                    except: pass
                if mes_num:
                    termos.append(f"/{mes_num}")
                    termos.append(f"/{mes_num}/")
                    termos.append(f"-{mes_num}-")
                
                for termo in termos:
                    if termo in t: return True
                return False

            if nome_mes:
                df_ferias_mes = df_f[df_f['ferias'].apply(lambda x: esta_de_ferias(x, mes_num, nome_mes))]
                if not df_ferias_mes.empty:
                    st.success(f"🌴 **Ausentes em {nome_mes}: {len(df_ferias_mes)} colaboradores**")
                    st.dataframe(df_ferias_mes, use_container_width=True)
                    st.markdown("---")
                else:
                    st.info(f"ℹ️ Nenhum colaborador identificado com férias marcadas para **{nome_mes}**.")
            
            st.markdown("**📋 Lista Completa**")
            st.dataframe(df_f, use_container_width=True)

    # ------------------ ADMIN ------------------
    with tabs[9]:
        st.markdown("### 📂 Gestão e Diagnóstico")
        
        # --- ADICIONAMOS A ABA DE GERENCIAR EQUIPE AQUI ---
        st_eq, st1, st2, st3, st4 = st.tabs(["👥 Gerenciar Equipe", "📤 Upload", "🗑️ Limpeza", "💾 Backup", "🔍 Diagnóstico"])
        
        with st_eq:
            st.markdown("#### 👥 Gestão de Usuários e Senhas")
            st.info("Adicione, edite ou remova operadores. Para resetar a senha de alguém, basta apagar o conteúdo da coluna 'senha' na linha do operador e salvar (assim ele poderá criar uma nova senha na tela inicial).")
            
            arquivo_usuarios = "usuarios.csv"
            if os.path.exists(arquivo_usuarios):
                df_gerenciar = pd.read_csv(arquivo_usuarios)
                # Garante que as colunas padrão existam para não dar erro
                for col in ['nome', 'email', 'ferias', 'senha', 'nascimento', 'admissao']:
                    if col not in df_gerenciar.columns:
                        df_gerenciar[col] = ""
                        
                # Mostra o editor de dados mágico
                df_users_editado = st.data_editor(df_gerenciar, num_rows="dynamic", use_container_width=True, key="editor_usuarios")
                
                if st.button("💾 Salvar Alterações da Equipe", type="primary"):
                    df_users_editado.to_csv(arquivo_usuarios, index=False)
                    sincronizar_com_github(arquivo_usuarios, "Gestor atualizou a base de usuários e senhas")
                    st.success("✅ Equipe atualizada com sucesso!")
                    time.sleep(1.5)
                    st.rerun()
            else:
                st.warning("⚠️ A base de usuários ainda não existe. Faça o upload na aba 'Upload'.")

        with st1:
            
            data_sugestao = obter_data_hoje()
            nova_data = st.text_input("Mês/Ano de Referência:", value=data_sugestao)
            
            up_u = st.file_uploader("Atualizar usuarios.csv (Mantém senhas antigas)", key="u")
            if up_u: 
                # --- NOVA REGRA DE UPLOAD PARA NÃO APAGAR AS SENHAS ---
                df_novo_u = pd.read_csv(up_u)
                if os.path.exists("usuarios.csv"):
                    df_antigo_u = pd.read_csv("usuarios.csv")
                    # Se o gestor subir um csv novo, o sistema mescla e salva as senhas já cadastradas
                    if 'senha' in df_antigo_u.columns and 'email' in df_antigo_u.columns and 'email' in df_novo_u.columns:
                        dicionario_senhas = dict(zip(df_antigo_u['email'].astype(str).str.lower().str.strip(), df_antigo_u['senha']))
                        df_novo_u['senha'] = df_novo_u['email'].astype(str).str.lower().str.strip().map(dicionario_senhas).fillna("")
                
                df_novo_u.to_csv("usuarios.csv", index=False)
                sincronizar_com_github("usuarios.csv", "Atualizando base de usuários mantendo senhas")
                st.success("✅ Usuários atualizados sem perder as senhas já criadas!")
            
            st.markdown("---")
            st.markdown("#### 💎 Arquivos de Indicadores (Qualidade, Aderência, etc)")
            up_k = st.file_uploader("Indicadores (CSVs)", accept_multiple_files=True, key="k")
            
            c_up1, c_up2 = st.columns(2)
            with c_up1:
                st.markdown("#### 💬 Arquivo Chat (Opcional)")
                up_op = st.file_uploader("Relatório (Volume / TMA Chat)", type=['csv'], key="up_op")
            with c_up2:
                st.markdown("#### 📞 Arquivo Voz (Opcional)")
                up_voz = st.file_uploader("Relatório (Volume / TMA Voz)", type=['csv'], key="up_voz")

            if st.button("💾 Salvar e Atualizar Histórico", type="primary"): 
                if not nova_data.strip():
                    st.error("⚠️ O campo 'Mês/Ano' não pode estar vazio!")
                    st.stop()
                
                sucesso = False

                try:
                    if up_k:
                        faxina_arquivos_temporarios()
                        salvar_arquivos_padronizados(up_k)
                        salvar_config(nova_data)
                        df_debug, log = carregar_dados_completo_debug() 
                        if df_debug is not None:
                            atualizar_historico(df_debug, nova_data)
                            sucesso = True
                            st.success("✅ Histórico de Diamantes atualizado com sucesso!")
                        else: st.error("❌ Erro ao processar arquivos de indicadores.")
                    
                    if up_op:
                        df_op_raw = ler_csv_inteligente(up_op)
                        if df_op_raw is not None:
                            df_op_tratado = processar_desempenho_agente(df_op_raw)
                            if df_op_tratado is not None:
                                atualizar_historico_operacional(df_op_tratado, nova_data)
                                sucesso = True
                                st.success("✅ Dados de Produtividade (Chat) atualizados!")
                            else: st.error("❌ Erro ao ler colunas de TMA Chat.")
                            
                    if up_voz:
                        df_voz_raw = ler_csv_inteligente(up_voz)
                        if df_voz_raw is not None:
                            df_voz_tratado = processar_desempenho_agente(df_voz_raw)
                            if df_voz_tratado is not None:
                                atualizar_historico_voz(df_voz_tratado, nova_data)
                                sucesso = True
                                st.success("✅ Dados de Produtividade (Voz) atualizados!")
                            else: st.error("❌ Erro ao ler colunas de TMA Voz.")
                    
                    if sucesso:
                        time.sleep(1.5)
                        st.rerun()

                except Exception as e: st.error(f"Erro salvamento: {e}")

            if up_k:
                st.markdown("**🔎 Pré-visualização KPIs:**")
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
            # ==========================================================
            # 📅 CENTRAL DE ESCALAS WFM (DENTRO DA ABA UPLOAD)
            # ==========================================================
            st.markdown("---")
            st.markdown("### 📅 Central de Escalas WFM")
            
            # Criamos abas internas para não bagunçar a tela de upload de indicadores
            tab_up_wfm, tab_gerenciar_wfm = st.tabs(["📤 Subir Nova Escala", "🗑️ Gerenciar Histórico WFM"])
            
            with tab_up_wfm:
                st.info("O arquivo será processado e guardado na base de dados única de escalas.")
                c_data1, c_data2 = st.columns(2)
                d_ini = c_data1.date_input("Início do Período", key="wfm_ini_new")
                d_fim = c_data2.date_input("Fim do Período", key="wfm_fim_new")
                
                arquivo_wfm = st.file_uploader("Arquivo de turnos (.txt)", type=["txt"], key="file_wfm_new")
                
                if arquivo_wfm and st.button("🚀 Consolidar Escala", type="primary"):
                    conteudo = arquivo_wfm.getvalue().decode("utf-8")
                    salvar_escala_no_csv(conteudo, d_ini, d_fim)
                    st.success(f"✅ Escala de {d_ini} a {d_fim} integrada!")
                    time.sleep(1)
                    st.rerun()

            with tab_gerenciar_wfm:
                if os.path.exists("base_wfm_consolidada.csv"):
                    df_wfm = pd.read_csv("base_wfm_consolidada.csv")
                    colunas_necessarias = ['ID_Upload', 'Inicio_Vigencia', 'Fim_Vigencia']
                    
                    if all(col in df_wfm.columns for col in colunas_necessarias):
                        resumo_wfm = df_wfm.groupby(colunas_necessarias).size().reset_index(name='Linhas')
                        st.write("#### Períodos ativos no sistema:")
                        for i, row in resumo_wfm.iterrows():
                            c_txt, c_btn = st.columns([3, 1])
                            c_txt.info(f"📅 **{row['Inicio_Vigencia']}** até **{row['Fim_Vigencia']}**")
                            if c_btn.button("Excluir", key=f"del_wfm_aba_{i}"):
                                df_wfm = df_wfm[df_wfm['ID_Upload'] != row['ID_Upload']]
                                df_wfm.to_csv("base_wfm_consolidada.csv", index=False)
                                sincronizar_com_github("base_wfm_consolidada.csv", "Remoção WFM via Admin")
                                st.rerun()
                    else:
                        st.error("Arquivo WFM corrompido. Recomenda-se resetar.")
                else:
                    st.info("Nenhuma escala WFM consolidada ainda.")
            
        with st2:
            st.markdown("#### 🗑️ Gerenciar Meses")
            df_atual_hist = carregar_historico_completo()
            if df_atual_hist is not None:
                resumo = df_atual_hist.groupby('Periodo').size().reset_index(name='Registros')
                for i, row in resumo.iterrows():
                    c1, c2, c3 = st.columns([2, 1, 1])
                    c1.write(f"📅 **{row['Periodo']}**")
                    c2.write(f"{row['Registros']} linhas")
                    if c3.button(f"Excluir {row['Periodo']}", key=f"del_{i}"):
                        excluir_periodo_historico(row['Periodo'])
                        st.rerun()
            st.divider()
            st.markdown("#### 🧹 Reset de Agendamentos (Banco de Horas)")
            if st.button("Limpar Histórico de Agendamentos de Horas"):
                if os.path.exists("escalas_banco_horas.csv"):
                    os.remove("escalas_banco_horas.csv")
                    sincronizar_com_github("escalas_banco_horas.csv", "Limpando agendamentos antigos")
                    st.success("Histórico limpo!")
                    time.sleep(1)
                    st.rerun()
            st.divider()
            if st.button("🔥 Limpar TUDO (Reset Completo do Sistema)", type="primary"):
                limpar_base_dados_completa()
                st.success("Limpo!")
                time.sleep(1)
                st.rerun()
        with st3:
            st.markdown("#### 💾 Backup de Segurança")
            if os.path.exists('historico_consolidado.csv'):
                with open('historico_consolidado.csv', 'rb') as f: st.download_button("⬇️ Baixar Backup Consolidado", f, "historico_consolidado_backup.csv", "text/csv")
            else: st.warning("Sem histórico para backup.")
            if os.path.exists('historico_operacional.csv'):
                with open('historico_operacional.csv', 'rb') as f: st.download_button("⬇️ Baixar Backup TMA Chat", f, "historico_operacional_backup.csv", "text/csv")
            if os.path.exists('historico_voz.csv'):
                with open('historico_voz.csv', 'rb') as f: st.download_button("⬇️ Baixar Backup TMA Voz", f, "historico_voz_backup.csv", "text/csv")
            if os.path.exists('feedbacks_gb.csv'):
                with open('feedbacks_gb.csv', 'rb') as f: st.download_button("⬇️ Baixar Banco de Feedbacks", f, "feedbacks_gb_backup.csv", "text/csv")
            if os.path.exists('escalas_banco_horas.csv'):
                with open('escalas_banco_horas.csv', 'rb') as f: st.download_button("⬇️ Baixar Agendamentos (Banco de Horas)", f, "escalas_banco_horas.csv", "text/csv")
            if os.path.exists('saldo_banco_horas.csv'):
                with open('saldo_banco_horas.csv', 'rb') as f: st.download_button("⬇️ Baixar Saldos (Banco de Horas)", f, "saldo_banco_horas.csv", "text/csv")
        with st4:
            if st.button("Rodar Diagnóstico"):
                _, log_df = carregar_dados_completo_debug()
                st.dataframe(log_df)
        
        
    # ------------------ BANCO DE HORAS ------------------
    with tabs[10]:
        st.markdown("### ⏰ Banco de Horas e Agendamentos")
        
        # Formulário de Agendamento Novo
        st.markdown("#### 📅 Agendar Retirada / Pagamento de Horas")
        with st.form("form_banco_horas"):
            colab_list = sorted(df_users_cadastrados['nome'].str.title().unique()) if df_users_cadastrados is not None else ["Nenhum usuário cadastrado"]
            c_f1, c_f2 = st.columns(2)
            sel_colab = c_f1.selectbox("Colaborador:", colab_list)
            unidade_gerencial = c_f2.text_input("Unidade Gerencial:", value="MU_SUPORTE_VAREJO")
            
            tipo_agendamento = st.radio("Tipo de Solicitação:", ["Pagamento (Horas Negativas - Trabalhar a mais)", "Retirada (Horas Positivas - Folga/Sair cedo)"])
            
            c_d1, c_d2 = st.columns(2)
            data_ini = c_d1.date_input("Data de Início")
            data_fim = c_d2.date_input("Data de Fim")
            
            c_h1, c_h2, c_h3 = st.columns(3)
            qtd_horas = c_h1.text_input("Quantidade (HH:MM)", placeholder="Ex: 02:00")
            hora_ini = c_h2.time_input("Horário Inicial")
            hora_fim = c_h3.time_input("Horário Final")
            
            submit_agendamento = st.form_submit_button("Salvar e Gerar Solicitação 🚀")
            
            if submit_agendamento:
                if not qtd_horas:
                    st.error("Por favor, preencha a Quantidade de Horas.")
                else:
                    tipo_curto = "Pagamento" if "Pagamento" in tipo_agendamento else "Retirada"
                    texto_gerado = f"UNIDADE GERENCIAL | DATA DE INICIO E FIM | COLABORADOR | TIPO (Retirada/Pagamento) | QUANTIDADE (HH:MM) | HORÁRIO INICIAL | HORÁRIO FINAL\n"
                    texto_gerado += f"{unidade_gerencial} | {data_ini.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')} | {str(sel_colab).upper()} | {tipo_curto} | {qtd_horas} | {hora_ini.strftime('%H:%M')} | {hora_fim.strftime('%H:%M')}"
                    
                    dados_salvar = {
                        "Periodo_Registro": datetime.now().strftime("%d/%m/%Y %H:%M"),
                        "Unidade": unidade_gerencial,
                        "Colaborador": sel_colab,
                        "Data_Inicio": data_ini.strftime('%d/%m/%Y'),
                        "Data_Fim": data_fim.strftime('%d/%m/%Y'),
                        "Tipo": tipo_curto,
                        "Quantidade": qtd_horas,
                        "Horario_Inicial": hora_ini.strftime('%H:%M'),
                        "Horario_Final": hora_fim.strftime('%H:%M')
                    }
                    salvar_escala_banco(dados_salvar)
                    
                    st.success("✅ Agendamento salvo com sucesso!")
                    st.info("Copie o texto abaixo e envie para o setor de WFM/RH:")
                    st.code(texto_gerado, language="text")

        st.markdown("---")
        # Visualização do Histórico e Upload Antigo
        st_t1, st_t2 = st.tabs(["📋 Histórico de Agendamentos", "📊 Análise de Saldo (Upload)"])
        
        with st_t1:
            df_agendamentos = carregar_escalas_banco()
            if df_agendamentos is not None and not df_agendamentos.empty:
                st.info("💡 **Dica:** Você pode dar dois cliques em qualquer célula para **EDITAR** o agendamento, ou selecionar uma linha e apertar a tecla **'Delete'** do teclado para **EXCLUIR**.")
                
                # O Data Editor mágico do Streamlit
                df_editado = st.data_editor(df_agendamentos, num_rows="dynamic", use_container_width=True, key="editor_agendamentos")
                
                if st.button("💾 Salvar Alterações na Tabela", type="primary"):
                    df_editado.to_csv('escalas_banco_horas.csv', index=False)
                    sincronizar_com_github('escalas_banco_horas.csv', "Atualização/Exclusão de Agendamento de Horas")
                    st.success("✅ Alterações salvas com sucesso! (A tabela do operador já foi atualizada).")
                    time.sleep(1.5)
                    st.rerun()
            else:
                st.info("Nenhum agendamento registrado até o momento.")

        with st_t2:
            st.info("Faça o upload do arquivo .xlsx ou .csv contendo os saldos atuais da equipe.")
            uploaded_ponto = st.file_uploader("Carregar Planilha de Ponto (Saldos)", type=['xlsx', 'csv'])
            if uploaded_ponto is not None:
                try:
                    if uploaded_ponto.name.endswith('.xlsx'): df_ponto = pd.read_excel(uploaded_ponto, skiprows=4)
                    else: df_ponto = pd.read_csv(uploaded_ponto, skiprows=4)
                    col_nome = next((c for c in df_ponto.columns if "Nome" in str(c)), None)
                    col_saldo = next((c for c in df_ponto.columns if "Total Banco" in str(c) or "Saldo Atual" in str(c)), None)
                    
                    if col_nome and col_saldo:
                        df_ponto = df_ponto[[col_nome, col_saldo]].dropna()
                        df_ponto.rename(columns={col_nome: 'Colaborador', col_saldo: 'Saldo String'}, inplace=True)
                        
                        if df_users_cadastrados is not None:
                            df_ponto['TEMP_NOME_NORM'] = df_ponto['Colaborador'].apply(normalizar_chave)
                            lista_ativos = df_users_cadastrados['nome'].unique()
                            df_ponto = df_ponto[df_ponto['TEMP_NOME_NORM'].isin(lista_ativos)]
                            df_ponto.drop(columns=['TEMP_NOME_NORM'], inplace=True)

                        df_ponto['Saldo (h)'] = df_ponto['Saldo String'].apply(converter_hora_para_float)
                        df_ponto['Status'] = df_ponto['Saldo (h)'].apply(lambda x: '🔴 Crítico (Negativo)' if x < 0 else '🟢 Positivo')
                        total_neg = df_ponto[df_ponto['Saldo (h)'] < 0]['Saldo (h)'].sum()
                        total_pos = df_ponto[df_ponto['Saldo (h)'] > 0]['Saldo (h)'].sum()
                        qtd_neg = len(df_ponto[df_ponto['Saldo (h)'] < 0])
                        
                        m1, m2, m3 = st.columns(3)
                        m1.metric("🔴 Pessoas Negativas", f"{qtd_neg}")
                        m2.metric("📉 Total Horas Devidas", formatar_saldo_decimal(total_neg))
                        m3.metric("📈 Total Horas Crédito", formatar_saldo_decimal(total_pos))
                        
                        st.markdown("---")
                        fig_ponto = px.bar(df_ponto.sort_values(by='Saldo (h)'), x='Saldo (h)', y='Colaborador', orientation='h', color='Status', color_discrete_map={'🔴 Crítico (Negativo)': '#e74c3c', '🟢 Positivo': '#2ecc71'}, text='Saldo String')
                        st.plotly_chart(fig_ponto, use_container_width=True)
                        st.dataframe(df_ponto.style.background_gradient(subset=['Saldo (h)'], cmap='RdYlGn'), use_container_width=True)
                        
                        # --- BOTÃO NOVO PARA SALVAR PARA A EQUIPE ---
                        st.markdown("---")
                        if st.button("💾 Publicar Saldos para a Equipe", type="primary"):
                            df_ponto[['Colaborador', 'Saldo String', 'Saldo (h)', 'Status']].to_csv('saldo_banco_horas.csv', index=False)
                            sincronizar_com_github('saldo_banco_horas.csv', "Atualizando saldos do banco de horas da equipe")
                            st.success("✅ Saldos publicados com sucesso! A equipe já pode visualizar seus saldos individuais na aba 'Meu Banco de Horas'.")
                            
                    else: st.error("Colunas não identificadas.")
                except Exception as e: st.error(f"Erro: {e}")

    # ------------------ FEEDBACKS GB ------------------
    # ------------------ FEEDBACKS GB (COM IA INTEGRADA) ------------------
    with tabs[11]:
        st.markdown("### 📝 Controle de Feedbacks (GB)")
        
        arquivo_padrao = os.path.exists('feedbacks_gb.csv')
        arquivo_backup = os.path.exists('feedbacks_gb_backup.csv')
        status_msg = "❌ Nenhum banco de dados encontrado."
        if arquivo_padrao: status_msg = "✅ Banco de Dados Principal (feedbacks_gb.csv) encontrado."
        elif arquivo_backup: status_msg = "⚠️ Usando Backup (feedbacks_gb_backup.csv)."
        
        st.caption(f"Status do Sistema: {status_msg}")
        st.info("💡 **Objetivo:** Registrar feedback orientado a valor, agora com ajuda da Inteligência Artificial!")
        
        if df_dados is not None and tem_tam:
            df_tam = df_dados[df_dados['Indicador'] == 'TAM'].copy()
            faixa_sel = st.selectbox("🎯 Selecione a Faixa de Desempenho (Baseado no TAM):", ["🔴 Abaixo de 70% (Crítico)", "🟠 Entre 70% e 80% (Atenção)", "🟡 Entre 80% e 90% (Meta Batida)", "🟢 Acima de 90% (Excelência)"])
            
            if "Abaixo de 70%" in faixa_sel: df_filtrado = df_tam[df_tam['% Atingimento'] < 0.70]
            elif "Entre 70% e 80%" in faixa_sel: df_filtrado = df_tam[(df_tam['% Atingimento'] >= 0.70) & (df_tam['% Atingimento'] < 0.80)]
            elif "Entre 80% e 90%" in faixa_sel: df_filtrado = df_tam[(df_tam['% Atingimento'] >= 0.80) & (df_tam['% Atingimento'] < 0.90)]
            else: df_filtrado = df_tam[df_tam['% Atingimento'] >= 0.90]
            
            if not df_filtrado.empty:
                st.write(f"Encontramos **{len(df_filtrado)}** colaborador(es) nesta faixa.")
                colab_fb = st.selectbox("Selecione o Colaborador:", sorted(df_filtrado['Colaborador'].unique()), key="sel_colab_fb")
                
                if colab_fb:
                    df_user_fb = df_dados[df_dados['Colaborador'] == colab_fb].sort_values(by='% Atingimento', ascending=False)
                    tam_v = df_user_fb[df_user_fb['Indicador'] == 'TAM'].iloc[0]['% Atingimento'] if not df_user_fb[df_user_fb['Indicador'] == 'TAM'].empty else 0.0
                    st.markdown(f"#### 📊 Raio-X Completo: {colab_fb}")
                    
                    cols_per_row = 4
                    for i in range(0, len(df_user_fb), cols_per_row):
                        cols = st.columns(cols_per_row)
                        for j in range(cols_per_row):
                            if i + j < len(df_user_fb):
                                row = df_user_fb.iloc[i + j]
                                val = row['% Atingimento']
                                ind_nome = formatar_nome_visual(row['Indicador'])
                                meta = 0.92 if row['Indicador'] in ['CONFORMIDADE', 'ADERENCIA'] else 0.80
                                status_msg = "✅ Meta" if round(val, 4) >= meta else "🔻 Abaixo"
                                color = "normal" if round(val, 4) >= meta else "inverse"
                                cols[j].metric(ind_nome, f"{val:.1%}", status_msg, delta_color=color)
                    
                    st.markdown("---")
                    
                    # --- NOVO: GERADOR DE FEEDBACK COM IA ---
                    st.markdown("#### 🤖 1. Gerador Inteligente de Feedback (Sofistas AI)")
                    st.write("Deixe a inteligência artificial cruzar os dados operacionais e criar um feedback humanizado, saindo do modelo engessado!")
                    
                    contexto_gestor = st.text_input("Alguma observação extra para a IA incluir? (Opcional):", placeholder="Ex: Elogie a empatia nas ligações, ou cobre mais agilidade no chat...")
                    
                    if st.button("✨ Gerar Feedback Completo com IA", type="primary", use_container_width=True):
                        if "GEMINI_API_KEY" in st.secrets:
                            with st.spinner("Sofistas AI está analisando os indicadores e escrevendo o feedback..."):
                                try:
                                    import google.generativeai as genai
                                    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                                    model = genai.GenerativeModel('gemini-2.5-flash')
                                    
                                    # Pega os números exatos do operador
                                    dados_kpi_str = df_user_fb[['Indicador', '% Atingimento']].to_csv(index=False)
                                    
                                    prompt_ia = f"""
                                    Aja como se você fosse EU, o Supervisor de Suporte Técnico (experiente, muito empático, humano e focado no desenvolvimento da equipe).
                                    Sua tarefa é estruturar o feedback para o MEU operador, {colab_fb}, em PRIMEIRA PESSOA (como se eu estivesse conversando diretamente com ele).
                                    
                                    Aqui estão os indicadores de performance dele neste mês:
                                    {dados_kpi_str}
                                    O Resultado Geral (TAM) dele fechou em {tam_v:.1%}.
                                    
                                    Meu contexto/observação extra sobre ele para você incluir de forma natural no texto: {contexto_gestor}
                                    
                                    Escreva um texto extremamente humanizado e encorajador. Fuja do tom robótico ou punitivo. 
                                    Gere a resposta com a seguinte estrutura EXATA:
                                    
                                    ### 🌟 Seus Pontos Fortes (Reconhecimento)
                                    (Fale diretamente com ele. Comece valorizando o esforço dele, citando os indicadores em que ele foi bem ou superou a meta. Faça-o se sentir importante e essencial para o nosso time.)
                                    
                                    ### 🎯 Onde Vamos Focar (Ponto de Atenção)
                                    (Aponte o indicador mais crítico ou o gargalo principal de forma construtiva e amigável. Use abordagens como "Notei que podemos ajustar...", "Onde a gente pode virar o jogo juntos é...")
                                    
                                    ### 🚀 Nosso Plano de Ação
                                    (Forneça 2 a 3 dicas super práticas, rápidas e aplicáveis no dia a dia do suporte técnico para ele melhorar esse ponto de atenção. Mostre que eu, como supervisor, estou lado a lado com ele para ajudar.)
                                    
                                    ### 📧 Resumo Oficial para Envio (E-mail / WhatsApp)
                                    (Escreva uma mensagem pronta, formatada de forma limpa e amigável, para eu simplesmente copiar e enviar para ele. 
                                    Esta mensagem deve agir como um "Resumo do nosso 1:1", contendo:
                                    1. Agradecimento pelo empenho no mês.
                                    2. Destaque rápido do que ele fez de melhor.
                                    3. Qual será o nosso foco de melhoria combinado.
                                    4. Fechamento motivacional me colocando à disposição.
                                    Assine como "Sua Liderança".)
                                    """
                                    
                                    resposta_fb = model.generate_content(prompt_ia)
                                    # Salva na memória para não sumir se a tela recarregar
                                    st.session_state[f'fb_gerado_{colab_fb}'] = resposta_fb.text
                                except Exception as e:
                                    st.error(f"Erro ao conectar com a IA: {e}")
                        else:
                            st.warning("⚠️ Você precisa configurar a chave GEMINI_API_KEY no painel de Segredos (Secrets) do Streamlit.")
                            
                    # Mostra a resposta gerada de forma elegante
                    if st.session_state.get(f'fb_gerado_{colab_fb}'):
                        st.markdown("<div style='background-color: #f8f9fa; padding: 25px; border-radius: 10px; border-left: 5px solid #003366; box-shadow: 0 4px 10px rgba(0,0,0,0.05);'>", unsafe_allow_html=True)
                        st.markdown(st.session_state[f'fb_gerado_{colab_fb}'])
                        st.markdown("</div><br>", unsafe_allow_html=True)
                        st.info("👆 Copie os trechos acima que você mais gostou e cole nas caixas abaixo para registrar oficialmente no sistema.")

                    # --- FORMULÁRIO DE REGISTRO ---
                    st.markdown("#### 💾 2. Registrar Feedback no Sistema")
                    with st.form("form_registro_fb"):
                        motivo_txt = st.text_area("1. Motivo(s) / Diagnóstico:")
                        fb_valor_txt = st.text_area("2. Feedback Estratégico:")
                        acao_txt = st.text_area("3. Plano de Ação:")
                        
                        if st.form_submit_button("Salvar Registro Oficial"):
                            if not motivo_txt or not fb_valor_txt or not acao_txt: 
                                st.error("⚠️ Preencha os três campos para registrar.")
                            else:
                                salvar_feedback_gb({"Data_Registro": datetime.now().strftime("%d/%m/%Y %H:%M"), "Periodo_Ref": periodo_label, "Colaborador": colab_fb, "Faixa": faixa_sel.split(" ")[0], "TAM": f"{tam_v:.1%}", "Motivo": motivo_txt, "Acao_GB": acao_txt, "Feedback_Valor": fb_valor_txt})
                                st.success("✅ Feedback registrado e salvo na base com sucesso!")
                                import time
                                time.sleep(1.5)
                                st.rerun()

            else: st.success(f"Nenhum colaborador encontrado na faixa.")
        
        st.markdown("---")
        st.markdown("### 📚 Base Geral de Feedbacks Aplicados")
        df_fbs_hist = carregar_feedbacks_gb()
        if df_fbs_hist is not None and not df_fbs_hist.empty: 
            st.dataframe(df_fbs_hist.iloc[::-1], use_container_width=True, hide_index=True)
        else: 
            st.info("Nenhum feedback registrado no sistema até o momento.")

# ------------------ SOFISTAS AI (GEMINI) ------------------
    with tabs[12]:
        st.markdown("### 🤖 Sofistas AI - Assistente Operacional")
        st.info("Faça perguntas sobre os resultados da equipe ou peça para eu redigir um feedback baseado nos números!")

        if "GEMINI_API_KEY" in st.secrets:
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            model = genai.GenerativeModel('gemini-2.5-flash')

            if "mensagens_ia" not in st.session_state:
                st.session_state.mensagens_ia = []

            # 1. A MÁGICA: Criamos uma caixa com scroll (tamanho fixo) para as mensagens
            caixa_chat_gestor = st.container(height=450)

            # 2. Desenhamos o histórico SEMPRE dentro da caixa
            with caixa_chat_gestor:
                for msg in st.session_state.mensagens_ia:
                    with st.chat_message(msg["role"]):
                        st.markdown(msg["content"])

            # 3. O input fica FORA da caixa, garantindo que as respostas fiquem EM CIMA dele
            if prompt := st.chat_input("Ex: Escreva um feedback elogiando o top performer de CSAT"):
                
                st.session_state.mensagens_ia.append({"role": "user", "content": prompt})

                # 4. Forçamos a pergunta e a resposta a aparecerem DENTRO da caixa
                with caixa_chat_gestor:
                    with st.chat_message("user"):
                        st.markdown(prompt)

                    contexto_dados = ""
                    if df_dados is not None and not df_dados.empty:
                        contexto_dados = f"\n\n[DADOS ATUAIS DA EQUIPE]:\n{df_dados.to_csv(index=False)}"

                    with st.chat_message("assistant"):
                        with st.spinner("Analisando a operação..."):
                            try:
                                prompt_completo = f"Você é um assistente de gestão de call center chamado Sofistas AI. Use os dados a seguir para responder a pergunta. Seja direto e profissional.\n{contexto_dados}\n\nPergunta do Gestor: {prompt}"
                                response = model.generate_content(prompt_completo)
                                st.markdown(response.text)
                                st.session_state.mensagens_ia.append({"role": "assistant", "content": response.text})
                            except Exception as e:
                                st.error(f"Erro de conexão com o Gemini: {e}")
        else:
            st.warning("⚠️ Chave da API do Gemini (GEMINI_API_KEY) não encontrada nas configurações secretas do Streamlit.")
# ------------------ MURAL DE CELEBRAÇÕES (GESTOR) ------------------
    with tabs[13]:
        st.markdown("### 🎉 Mural de Celebrações")
        st.info("Acompanhe os aniversariantes do mês e quem está completando mais um ciclo de casa com a gente! 🎈")
        
        meses_pt = {1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril', 5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto', 9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'}
        hoje = datetime.now()
        mes_atual = hoje.month
        
        lista_niver, lista_firma = [], []
        
        if df_users_cadastrados is not None:
            for _, row in df_users_cadastrados.iterrows():
                nome_colab = str(row.get('nome', '')).title()
                
                # 🎂 Aniversário
                nasc_str = str(row.get('nascimento', '')).strip()
                if nasc_str and nasc_str != 'nan':
                    try:
                        dia_n, mes_n = int(nasc_str.split('/')[0]), int(nasc_str.split('/')[1])
                        if mes_n == mes_atual:
                            lista_niver.append({'dia': dia_n, 'nome': nome_colab, 'data': f"{dia_n:02d}/{mes_n:02d}"})
                    except: pass
                    
                # 💼 Tempo de Casa
                adm_str = str(row.get('admissao', '')).strip()
                if adm_str and adm_str != 'nan':
                    try:
                        data_adm = datetime.strptime(adm_str, "%d/%m/%Y")
                        if data_adm.month == mes_atual:
                            anos_casa = hoje.year - data_adm.year
                            if anos_casa > 0:
                                lista_firma.append({'dia': data_adm.day, 'nome': nome_colab, 'anos': anos_casa, 'data': f"{data_adm.day:02d}/{data_adm.month:02d}"})
                    except: pass

        lista_niver = sorted(lista_niver, key=lambda x: x['dia'])
        lista_firma = sorted(lista_firma, key=lambda x: x['dia'])
        
        st.markdown(f"<h4 style='text-align: center; color: #003366; margin-top: 20px;'>Celebrações de {meses_pt[mes_atual]}</h4>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        
        with c1:
            st.markdown("##### 🎂 Aniversários de Vida")
            if lista_niver:
                for item in lista_niver:
                    is_today = "🎈 HOJE!" if item['dia'] == hoje.day else ""
                    st.markdown(f"<div style='padding:12px; background-color:#FFF; border-left:5px solid #F37021; margin-bottom:10px; border-radius:8px; box-shadow:0 2px 8px rgba(0,0,0,0.05); display:flex; justify-content:space-between;'><span><b>{item['data']}</b> - {item['nome']}</span><span style='color:#e74c3c; font-weight:bold;'>{is_today}</span></div>", unsafe_allow_html=True)
            else: st.write("Nenhum aniversariante neste mês.")
                
        with c2:
            st.markdown("##### 💼 Tempo de Casa")
            if lista_firma:
                for item in lista_firma:
                    anos_texto = f"{item['anos']} ano" if item['anos'] == 1 else f"{item['anos']} anos"
                    st.markdown(f"<div style='padding:12px; background-color:#FFF; border-left:5px solid #003366; margin-bottom:10px; border-radius:8px; box-shadow:0 2px 8px rgba(0,0,0,0.05); display:flex; justify-content:space-between;'><span><b>{item['data']}</b> - {item['nome']}</span><span style='background-color:#e0f7fa; padding:2px 10px; border-radius:12px; font-size:0.85em; color:#006064; font-weight:bold;'>{anos_texto}</span></div>", unsafe_allow_html=True)
            else: st.write("Ninguém completando tempo de casa neste mês.")   
                
# --- 💌 MURAL DE RECADINHOS (VERSÃO GESTOR) ---
        st.markdown("---")
        st.markdown("### 💌 Mural de Recadinhos")
        st.info("Como Gestor, também podes deixar mensagens para os teus colaboradores e acompanhar o que a equipa está a escrever!")

        aniversariantes_nomes = [item['nome'] for item in lista_niver]
        
        if aniversariantes_nomes:
            # Formulário para o Gestor enviar recados
            with st.form("form_recado_gestor"):
                c_quem, c_vazio = st.columns([1, 2])
                para_quem = c_quem.selectbox("Enviar parabéns para:", aniversariantes_nomes)
                mensagem = st.text_area("Mensagem do Gestor:", placeholder="Ex: Parabéns pelo teu dia e pelo excelente trabalho! 🚀")
                
                if st.form_submit_button("Publicar no Mural 🎈"):
                    if mensagem.strip():
                        salvar_mensagem_mural({
                            "Data": datetime.now().strftime("%d/%m/%Y %H:%M"),
                            "De": "Gestor 🦁", # Identifica que foi a liderança que enviou
                            "Para": para_quem,
                            "Mensagem": mensagem
                        })
                        st.success("✅ Recado do Gestor publicado!")
                        import time
                        time.sleep(1.2)
                        st.rerun()
        
        # --- EXIBIÇÃO DOS RECADOS NO PAINEL DO GESTOR ---
        df_mural = carregar_mensagens_mural()
        if df_mural is not None and not df_mural.empty:
            st.markdown("#### 📬 Todas as Mensagens do Mês")
            
            # Filtra mensagens para os aniversariantes atuais
            recados_mes = df_mural[df_mural['Para'].isin(aniversariantes_nomes)]
            
            if not recados_mes.empty:
                for _, row in recados_mes.iloc[::-1].iterrows():
                    # Estilo diferenciado se a mensagem veio do Gestor
                    is_gestor = "Gestor" in str(row['De'])
                    cor_borda = "#e74c3c" if is_gestor else "#003366"
                    
                    st.markdown(f"""
                    <div style='background-color:#FFF; padding:15px; border-radius:10px; border-left: 5px solid {cor_borda}; margin-bottom:15px; box-shadow: 0 4px 10px rgba(0,0,0,0.05);'>
                        <p style='margin:0; color:#555; font-size:0.9em;'>
                            De: <b>{row['De']}</b> ➔ Para: <b>{row['Para']}</b>
                            <span style='float:right; font-size:0.8em; color:#999;'>{row['Data']}</span>
                        </p>
                        <p style='margin-top:10px; margin-bottom:0; font-size:1.05em; color:#333; font-style: italic;'>"{row['Mensagem']}"</p>
                    </div>
                    """, unsafe_allow_html=True)
# ==========================================
# --- 7. VISÃO DO OPERADOR ---
# ==========================================
else:
    # --- NOVO CABEÇALHO ALINHADO (FOTO E BOAS-VINDAS) ---
    nome_seguro_user = normalizar_chave(nome_logado).replace(" ", ".")
    caminho_foto_user = os.path.join(PASTA_FOTOS, f"{nome_seguro_user}.png")

    col_foto_perfil, col_texto_perfil = st.columns([1, 6])
    
    # ==========================================
    # 📸 POPUP DE EDIÇÃO DE PERFIL
    # ==========================================
    @st.dialog("📸 Personalizar Perfil")
    def exibir_popup_perfil():
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("##### 📤 Subir Foto")
            upload_foto = st.file_uploader("PNG ou JPG:", type=['png', 'jpg', 'jpeg'], key="up_foto_popup")
            if upload_foto and st.button("Salvar Foto", type="primary", use_container_width=True):
                with open(caminho_foto_user, "wb") as f:
                    f.write(upload_foto.getbuffer())
                sincronizar_com_github(caminho_foto_user, f"Foto: {nome_logado}")
                st.rerun()

        with col2:
            st.markdown("##### 🎭 Avatar")
            pasta_avatares = "avatares"
            if os.path.exists(pasta_avatares):
                arquivos_disp = [f for f in os.listdir(pasta_avatares) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
                if arquivos_disp:
                    formatar_nome = lambda x: x.split('.')[0].replace('_', ' ').title()
                    mapa_avatares = {formatar_nome(f): f for f in arquivos_disp}
                    selecao_nome = st.selectbox("Estilos:", list(mapa_avatares.keys()), label_visibility="collapsed")
                    nome_arq = mapa_avatares[selecao_nome]
                    
                    st.image(os.path.join(pasta_avatares, nome_arq), width=60)
                    
                    if st.button("Definir Avatar", type="primary", use_container_width=True):
                        caminho_avatar_txt = caminho_foto_user.replace(".png", "_avatar.txt")
                        with open(caminho_avatar_txt, "w", encoding="utf-8") as f:
                            f.write(nome_arq)
                        if os.path.exists(caminho_foto_user):
                            os.remove(caminho_foto_user)
                        st.rerun()
            else:
                st.warning("Sem avatares na pasta.")
                
        st.divider()
        if st.button("🗑️ Remover Imagem Atual", use_container_width=True):
            if os.path.exists(caminho_foto_user): os.remove(caminho_foto_user)
            caminho_av = caminho_foto_user.replace(".png", "_avatar.txt")
            if os.path.exists(caminho_av): os.remove(caminho_av)
            st.rerun()

    # ==========================================
    # 🖼️ EXIBIÇÃO DA FOTO NA TELA PRINCIPAL
    # ==========================================
    with col_foto_perfil:
        caminho_avatar_txt = caminho_foto_user.replace(".png", "_avatar.txt")
        
        # 1. Prioridade: Foto Real
        if os.path.exists(caminho_foto_user):
            with open(caminho_foto_user, "rb") as f:
                img_base64 = base64.b64encode(f.read()).decode()
            st.markdown(f'<img src="data:image/png;base64,{img_base64}" style="border-radius: 50%; width: 90px; height: 90px; object-fit: cover; border: 3px solid #F37021; box-shadow: 0 4px 10px rgba(0,0,0,0.1); display: block; margin: 0 auto;">', unsafe_allow_html=True)
            
        # 2. Prioridade: Avatar
        elif os.path.exists(caminho_avatar_txt):
            with open(caminho_avatar_txt, "r", encoding="utf-8") as f:
                nome_arq_avatar = f.read().strip()
            caminho_full_avatar = os.path.join("avatares", nome_arq_avatar)
            
            if os.path.exists(caminho_full_avatar):
                with open(caminho_full_avatar, "rb") as f:
                    avatar_base64 = base64.b64encode(f.read()).decode()
                st.markdown(f'<img src="data:image/png;base64,{avatar_base64}" style="border-radius: 50%; width: 90px; height: 90px; object-fit: cover; border: 3px solid #003366; box-shadow: 0 4px 10px rgba(0,0,0,0.1); display: block; margin: 0 auto;">', unsafe_allow_html=True)
            else:
                st.markdown("<h1 style='font-size: 70px; text-align: center; margin:0;'>👤</h1>", unsafe_allow_html=True)
                
        # 3. Padrão: Ícone Vazio
        else:
            st.markdown("<h1 style='font-size: 70px; text-align: center; margin:0;'>👤</h1>", unsafe_allow_html=True)
        
        # BOTÃO DISCRETO PARA ABRIR O POPUP
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("✏️ Editar", use_container_width=True):
            exibir_popup_perfil()

    with col_texto_perfil:
        # 1. Cria a variável blindada ANTES de jogar na tela
        primeiro_nome = nome_logado.split()[0] if nome_logado and str(nome_logado).strip() else "Equipe"
        
        # --- ⏳ CÁLCULO DE TEMPO DE EMPRESA ---
        tempo_empresa_str = ""
        if df_users_cadastrados is not None:
            try:
                user_info = df_users_cadastrados[df_users_cadastrados['nome'] == nome_logado.upper()]
                if not user_info.empty and 'admissao' in user_info.columns:
                    data_adm_str = str(user_info.iloc[0]['admissao']).strip()
                    
                    if data_adm_str and data_adm_str != "nan":
                        # Tenta converter a data que o gestor digitou (DD/MM/YYYY)
                        data_adm = datetime.strptime(data_adm_str, "%d/%m/%Y")
                        hoje = datetime.now()
                        
                        # Faz a matemática de anos e meses
                        anos = hoje.year - data_adm.year
                        meses = hoje.month - data_adm.month
                        if hoje.day < data_adm.day:
                            meses -= 1
                        if meses < 0:
                            anos -= 1
                            meses += 12
                            
                        # Ajusta plural e singular para ficar gramaticalmente perfeito
                        str_anos = f"{anos} ano" if anos == 1 else f"{anos} anos"
                        str_meses = f"{meses} mês" if meses == 1 else f"{meses} meses"
                        
                        # Monta o textinho da medalha
                        if anos > 0 and meses > 0:
                            texto_tempo = f"{str_anos} e {str_meses}"
                        elif anos > 0:
                            texto_tempo = f"{str_anos}"
                        elif meses > 0:
                            texto_tempo = f"{str_meses}"
                        else:
                            texto_tempo = "Menos de 1 mês 🌱"
                            
                        # Cria a medalha com o novo texto completo
                        tempo_empresa_str = f"<span class='update-badge' style='background-color:#fff3e0; color:#e65100; margin-left:10px; border-color: #ffb74d;'>⏳ Tempo de Casa: <b>{texto_tempo}</b></span>"
            except Exception as e:
                pass # Se a data estiver em branco ou no formato errado, simplesmente não mostra a medalha

        # 2. Usa a variável segura no Markdown e injeta a medalha de tempo de casa
        st.markdown(f"## 🚀 Olá, **{primeiro_nome}**!")
        st.markdown(f"<div style='display: flex; align-items: center; margin-top:-15px; color: #666; font-size:0.9em;'><span style='margin-right: 15px;'>📅 Referência: <b>{periodo_label}</b></span><span class='update-badge' style='background-color:#e0f7fa; color:#006064;'>🕒 Atualizado em: {obter_data_atualizacao()}</span>{tempo_empresa_str}</div>", unsafe_allow_html=True)
                 
        # ==========================================================
        # 🏛️ REFLEXÃO DIÁRIA (POPUP FILOSÓFICO DE 2 ETAPAS)
        # ==========================================================
        
        # 1. Variável Mestra (Decide se a janela deve abrir/ficar aberta)
        if 'mostrar_popup_humor' not in st.session_state:
            humor_banco = carregar_humor_hoje(nome_logado)
            if humor_banco is None:
                st.session_state['mostrar_popup_humor'] = True # Abre sozinho se não votou
            else:
                st.session_state['mostrar_popup_humor'] = False # Fica fechado

        # 2. A "Cara" e as Etapas do Popup
        @st.dialog("Reflexão Diária 🏛️")
        def exibir_popup_humor():
            # Memória para saber se estamos na tela 1 (votar) ou 2 (ler)
            if f'etapa_popup_{nome_logado}' not in st.session_state:
                st.session_state[f'etapa_popup_{nome_logado}'] = 1

            # --- ETAPA 1: ESCOLHA DO HUMOR ---
            if st.session_state[f'etapa_popup_{nome_logado}'] == 1:
                st.markdown(f"<p style='text-align: center; color: #4B5563; margin-bottom: 20px;'>Como você está se sentindo hoje, {primeiro_nome}?</p>", unsafe_allow_html=True)
                
                opcoes_humor = ["🤩 Incrível ", "🙂 Bem ", "😐 Normal ", "😫 Cansado ", "😡 Estressado "]
                humor_banco = carregar_humor_hoje(nome_logado)
                idx_padrao = opcoes_humor.index(humor_banco) if humor_banco in opcoes_humor else 0
                
                escolha_humor = st.radio("Selecione:", opcoes_humor, index=idx_padrao, horizontal=False, label_visibility="collapsed")
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                # AQUI ESTAVA O ERRO! Sem st.rerun() neste botão, a janela NÃO fecha.
                if st.button("Salvar e Refletir", type="primary", use_container_width=True):
                    registrar_humor_dia(nome_logado, escolha_humor)
                    
                    mensagem_final = f"O universo muda constantemente; nossa vida é o que nossos pensamentos fazem dela. Um excelente turno, {primeiro_nome}."
                    
                    if "GEMINI_API_KEY" in st.secrets:
                        with st.spinner("Buscando sabedoria para o seu dia... 🏛️"):
                            try:
                                import google.generativeai as genai
                                genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                                model = genai.GenerativeModel('gemini-2.5-flash')
                                prompt_humor = f"""
                                Você é um sábio filósofo antigo (estilo Sêneca ou Marco Aurélio), acolhedor e profundo. 
                                O operador de suporte técnico {primeiro_nome} acabou de registrar que seu humor hoje é '{escolha_humor}'. 
                                Escreva uma reflexão profundamente FILOSÓFICA e madura (máximo 3 frases curtas) para ele ler agora. 
                                Se ele estiver estressado/cansado, traga sabedoria sobre controle, resiliência e a transitoriedade das dificuldades. 
                                Se ele estiver bem/incrível, traga uma reflexão sobre manter a virtude, foco e humildade. 
                                Não use aspas no início e no fim.
                                """
                                resposta = model.generate_content(prompt_humor)
                                if resposta and resposta.text:
                                    mensagem_final = resposta.text.replace('"', '').strip()
                            except:
                                pass
                    
                    # Salva a mensagem e manda a tela ir para a Etapa 2
                    st.session_state[f'msg_humor_ia_{nome_logado}'] = mensagem_final
                    st.session_state[f'etapa_popup_{nome_logado}'] = 2
                    st.rerun() # <--- ISSO RECARREGA APENAS O POPUP AGORA, MOSTRANDO A ETAPA 2

            # --- ETAPA 2: A MENSAGEM FILOSÓFICA ---
            elif st.session_state[f'etapa_popup_{nome_logado}'] == 2:
                st.markdown(f"""
                <div style='background-color: #f8fafc; border-left: 4px solid #64748b; padding: 25px; border-radius: 8px; margin-bottom: 25px; box-shadow: 0 4px 6px rgba(0,0,0,0.05);'>
                    <p style='margin: 0; color: #334155; font-size: 1.1em; font-style: italic; line-height: 1.6; text-align: center;'>"{st.session_state[f'msg_humor_ia_{nome_logado}']}"</p>
                </div>
                """, unsafe_allow_html=True)
                
                # AQUI SIM, o st.rerun() serve para FECHAR o popup definitivamente
                if st.button("Ir para o meu painel 🚀", type="primary", use_container_width=True):
                    st.session_state['mostrar_popup_humor'] = False # Desativa o popup
                    st.rerun()

        # 3. Disparador do Popup
        if st.session_state.get('mostrar_popup_humor', False):
            exibir_popup_humor()
            
        # ==========================================================
        # 4. Exibição Dinâmica do Humor no Painel
        # ==========================================================
        humor_atual = carregar_humor_hoje(nome_logado)
        
        if humor_atual:
            # Divide no mesmo padrão do WFM: 75% texto, 25% botão
            c_humor_txt, c_humor_btn = st.columns([3, 1])
            
            with c_humor_txt:
                st.markdown(f"""
                <div style='background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 0 15px; display: flex; align-items: center; height: 41px; box-shadow: 0 1px 2px rgba(0,0,0,0.02);'>
                    <span style='color: #64748b; font-size: 0.9em; margin-right: 5px;'>Você disse que hoje se sente:</span>
                    <span style='color: #0f172a; font-size: 1em; font-weight: 700;'>{humor_atual}</span>
                </div>
                """, unsafe_allow_html=True)
                
            with c_humor_btn:
                if st.button("🔄 Mudou?", use_container_width=True):
                    st.session_state['mostrar_popup_humor'] = True
                    st.session_state[f'etapa_popup_{nome_logado}'] = 1
                    st.rerun()
        else:
            # Caso ele ainda não tenha votado (ou fechou o popup sem querer)
            if st.button("🌡️ Registrar meu Humor"):
                st.session_state['mostrar_popup_humor'] = True
                st.session_state[f'etapa_popup_{nome_logado}'] = 1
                st.rerun()
    # --- 🕒 CARTÃO DE PAUSAS DO WFM ---
        # ==========================================================
        # 🕒 ESCALA E PAUSAS (WFM) - MODO COMPACTO COM POPUP
        # ==========================================================
        escala_hoje = buscar_escala_hoje(nome_logado)
        
        # 1. Definindo a Janela do Popup
        @st.dialog("🕒 Minha Escala e Pausas", width="large")
        def exibir_popup_wfm():
            st.markdown("#### ☕ Suas Pausas de Hoje")
            if escala_hoje:
                if escala_hoje.get("tipo") == "trabalho":
                    cp1, cp2, cp3 = st.columns(3)
                    with cp1:
                        st.info(f"**Pausa 1:**\n\n{escala_hoje.get('intervalo_1', '--')}")
                    with cp2:
                        st.warning(f"**Refeição:**\n\n{escala_hoje.get('refeicao', '--')}")
                    with cp3:
                        st.info(f"**Pausa 2:**\n\n{escala_hoje.get('intervalo_2', '--')}")
                else:
                    st.success(f"🏖️ Hoje é seu dia de descanso! Motivo: {escala_hoje.get('motivo', 'Folga')}")
            else:
                st.info("Nenhuma escala encontrada para você no dia de hoje.")
                
            st.divider()
            
            st.markdown("#### 📅 Escala Completa do Mês")
            df_escala_mes = buscar_escala_completa(nome_logado)
            if df_escala_mes is not None and not df_escala_mes.empty:
                st.dataframe(df_escala_mes, use_container_width=True, hide_index=True)
            else:
                st.warning("Nenhum histórico de escala mensal encontrado.")

        # ==========================================================
        # 2. Exibição Ultra-Compacta na Tela Principal (TUDO NA MESMA LINHA)
        # ==========================================================
        if escala_hoje and escala_hoje.get("tipo") == "trabalho":
            turno_txt = escala_hoje.get('turno', '--')
            icone_status = "💼 Ativo"
            cor_status = "#3b82f6" # Azul
        elif escala_hoje and escala_hoje.get("tipo") == "folga":
            turno_txt = "Folga"
            icone_status = "🏖️ Descanso"
            cor_status = "#10b981" # Verde
        else:
            turno_txt = "Sem dados"
            icone_status = "❓ N/A"
            cor_status = "#64748b" # Cinza

        # Divide a tela: 75% para o mini-card do turno, 25% para o botão
        c_turno, c_botao = st.columns([3, 1])
        
        with c_turno:
            # Ajuste fino: height em exatos 41px (tamanho do botão) e sem margin-top
            st.markdown(f"""
            <div style='background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 0 15px; display: flex; justify-content: space-between; align-items: center; height: 41px; box-shadow: 0 1px 2px rgba(0,0,0,0.02);'>
                <div style='display: flex; align-items: center; gap: 8px;'>
                    <span style='font-size: 1.1em; margin-top: -2px;'>🕒</span>
                    <span style='color: #64748b; font-size: 0.85em; font-weight: 600;'>MEU TURNO:</span>
                    <span style='color: #0f172a; font-size: 0.95em; font-weight: 800;'>{turno_txt}</span>
                </div>
                <div>
                    <span style='color: {cor_status}; font-size: 0.75em; font-weight: 700; background-color: {cor_status}15; padding: 3px 8px; border-radius: 10px;'>{icone_status}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        with c_botao:
            # Removido o código de espaço invisível. Agora o botão nasce colado no topo da coluna.
            if st.button("☕ Ver Pausas", use_container_width=True):
                exibir_popup_wfm()
    # --- 🎂 VERIFICAÇÃO DE ANIVERSÁRIO ---
    if df_users_cadastrados is not None:
        try:
            # Puxa o dado da linha do usuário logado
            user_info = df_users_cadastrados[df_users_cadastrados['nome'] == nome_logado.upper()]
            if not user_info.empty and 'nascimento' in user_info.columns:
                data_nasc = str(user_info.iloc[0]['nascimento']).strip()
                
                # Pega o dia e mês de hoje no formato DD/MM
                hoje_str = datetime.now().strftime("%d/%m")
                
                # Se os primeiros 5 caracteres (DD/MM) baterem, é festa!
                # Usamos st.session_state para os balões subirem só 1 vez por login e não irritar o operador
                if data_nasc[:5] == hoje_str:
                    st.success(f"🎉 **Feliz Aniversário, {primeiro_nome}!** Toda a equipe Sofistas te deseja um dia incrível e repleto de conquistas! 🎂🎈")
                    if not st.session_state.get('baloes_vistos', False):
                        st.balloons()
                        st.session_state['baloes_vistos'] = True
        except: pass        

    # --- CRIAÇÃO DAS ABAS ---
    tab_results, tab_time, tab_ferias, tab_feedbacks, tab_banco, tab_ia, tab_celebracoes = st.tabs(["📊 Meus Resultados", "🦁 Visão do Time", "🏖️ Minhas Férias", "📝 Meus Feedbacks", "⏰ Meu Banco de Horas", "🤖 Assistente IA", "🎉 Celebrações"])
    # ---------------------------------------------------------
    # ABA 1: MEUS RESULTADOS
    # ---------------------------------------------------------
    with tab_results:
        
        # CÁLCULO DE RANKING
        ranking_msg = "Não classificado"
        if df_dados is not None and not df_dados.empty:
            if tem_tam: df_rank = df_dados[df_dados['Indicador'] == 'TAM'].copy().sort_values(by='% Atingimento', ascending=False).reset_index(drop=True)
            else:
                df_rank = df_dados.groupby('Colaborador').agg({'Diamantes': 'sum', 'Max. Diamantes': 'sum'}).reset_index()
                df_rank['Score'] = df_rank['Diamantes'] / df_rank['Max. Diamantes']
                df_rank = df_rank.sort_values(by='Score', ascending=False).reset_index(drop=True)
            try: ranking_msg = f"{df_rank[df_rank['Colaborador'] == nome_logado].index[0] + 1}º de {len(df_rank)}"
            except: pass

        meus_dados = df_dados[df_dados['Colaborador'] == nome_logado].copy() if df_dados is not None else pd.DataFrame()
        if meus_dados.empty and df_dados is not None: meus_dados = df_dados[df_dados['Colaborador'].str.contains(nome_logado, case=False, na=False)].copy()

        if not meus_dados.empty:
            total_dia_bruto = meus_dados[meus_dados['Indicador'] == 'TAM'].iloc[0]['Diamantes'] if tem_tam and not meus_dados[meus_dados['Indicador'] == 'TAM'].empty else meus_dados['Diamantes'].sum()
            total_max = meus_dados[meus_dados['Indicador'] == 'TAM'].iloc[0]['Max. Diamantes'] if tem_tam and not meus_dados[meus_dados['Indicador'] == 'TAM'].empty else meus_dados['Max. Diamantes'].sum()
            resultado_global = meus_dados[meus_dados['Indicador'] == 'TAM'].iloc[0]['% Atingimento'] if tem_tam and not meus_dados[meus_dados['Indicador'] == 'TAM'].empty else ((total_dia_bruto / total_max) if total_max > 0 else 0)
            
            c_rank, c_gamif, c_gauge = st.columns([1, 1.5, 1])
            with c_rank:
                st.markdown("##### 🏆 Ranking")
                st.metric("Sua Posição", ranking_msg)
            with c_gamif:
                st.markdown("##### 💎 Gamificação")
                st.progress(resultado_global if resultado_global <= 1.0 else 1.0)
                badges = []
                if not meus_dados[meus_dados['Indicador'] == 'CONFORMIDADE'].empty:
                    if round(meus_dados[meus_dados['Indicador'] == 'CONFORMIDADE'].iloc[0]['% Atingimento'], 4) >= 1.0: badges.append("🛡️ Guardião")
                if not meus_dados[meus_dados['Indicador'] == 'CSAT'].empty:
                    if round(meus_dados[meus_dados['Indicador'] == 'CSAT'].iloc[0]['% Atingimento'], 4) >= 0.95: badges.append("❤️ Amado")
                if not meus_dados[meus_dados['Indicador'] == 'ADERENCIA'].empty:
                    if round(meus_dados[meus_dados['Indicador'] == 'ADERENCIA'].iloc[0]['% Atingimento'], 4) >= 0.98: badges.append("⏰ Relógio Suíço")
                if not meus_dados[meus_dados['Indicador'] == 'IR'].empty:
                    if round(meus_dados[meus_dados['Indicador'] == 'IR'].iloc[0]['% Atingimento'], 4) >= 0.90: badges.append("🧩 Sherlock")
                if not meus_dados[meus_dados['Indicador'] == 'PONTUALIDADE'].empty:
                    if round(meus_dados[meus_dados['Indicador'] == 'PONTUALIDADE'].iloc[0]['% Atingimento'], 4) >= 1.0: badges.append("🎯 No Alvo")
                if not meus_dados[meus_dados['Indicador'] == 'TPC'].empty:
                    if round(meus_dados[meus_dados['Indicador'] == 'TPC'].iloc[0]['% Atingimento'], 4) >= 1.0: badges.append("⚡ The Flash")
                if not meus_dados[meus_dados['Indicador'] == 'INTERACOES'].empty:
                    if round(meus_dados[meus_dados['Indicador'] == 'INTERACOES'].iloc[0]['% Atingimento'], 4) >= 1.0: badges.append("🤖 Ciborgue")
                st.write(f"**{int(total_dia_bruto)} / {int(total_max)}** Diamantes")
                if badges: st.success(f"Conquistas: {' '.join(badges)}")
                with st.expander("ℹ️ Legenda das Conquistas"):
                    st.markdown("* 🛡️ **Guardião:** 100% Conformidade\n* ❤️ **Amado:** CSAT > 95%\n* ⏰ **Relógio Suíço:** Aderência > 98%\n* 🧩 **Sherlock:** Resolução > 90%\n* 🎯 **No Alvo:** Pontualidade 100%\n* ⚡ **The Flash:** TPC na Meta\n* 🤖 **Ciborgue:** Interações na Meta")

            with c_gauge:
                fg = go.Figure(go.Indicator(mode="gauge+number", value=resultado_global*100, number={'font':{'size':24,'color':'#003366'}}, gauge={'axis':{'range':[None,100],'tickwidth':1,'tickcolor':"#003366"},'bar':{'color':"#F37021"},'bgcolor':"white",'steps':[{'range':[0,100],'color':'#f4f7f6'}],'threshold':{'line':{'color':"green",'width':4},'thickness':0.75,'value':100}}))
                fg.update_layout(height=140, margin=dict(l=10,r=10,t=30,b=10), paper_bgcolor='rgba(0,0,0,0)', font={'color':'#003366'})
                st.plotly_chart(fg, use_container_width=True)
            
            st.markdown("---")
            
            # SMART COACH (MENTOR IA)
            st.markdown("### 🤖 Seu Mentor IA (Smart Coach)")
            st.info("Deixe a Inteligência Artificial analisar seus números atuais e te dar dicas exclusivas de como aumentar sua comissão!")

            if "GEMINI_API_KEY" in st.secrets:
                if st.button("✨ Gerar meu Plano de Ação com IA", type="primary", use_container_width=True):
                    with st.spinner("O Sofistas AI está analisando seus resultados detalhadamente..."):
                        try:
                            dados_op_str = meus_dados[['Indicador', '% Atingimento', 'Diamantes']].to_csv(index=False)
                            prompt_op = f"""
                            Você é um mentor motivacional e especialista em atendimento ao cliente chamado Sofistas AI. 
                            O nome do operador é {nome_logado.split()[0]}.
                            Aqui estão os resultados dele neste mês atual:
                            {dados_op_str}
                            
                            Sua tarefa:
                            1. Comece com um cumprimento super animado chamando-o pelo nome.
                            2. Elogie os pontos fortes (onde ele bateu a meta ou chegou perto).
                            3. Identifique o maior gargalo (o indicador com a nota mais baixa).
                            4. Dê 2 dicas práticas, curtas e diretas de como ele pode melhorar esse indicador específico no dia a dia do call center.
                            5. Encerre com uma frase de incentivo focada em como ele pode ganhar mais comissões/diamantes no próximo ciclo.
                            Use formatação bonita com Markdown (negrito, listas) e use emojis. Seja extremamente amigável, direto e focado em dinheiro/resultados.
                            """
                            import google.generativeai as genai
                            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                            model = genai.GenerativeModel('gemini-2.5-flash')
                            resposta = model.generate_content(prompt_op)
                            
                            st.markdown("""<div style="background-color: #f8f9fa; border-left: 6px solid #F37021; padding: 25px; border-radius: 10px; margin-top: 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.05);">""", unsafe_allow_html=True)
                            st.markdown(resposta.text)
                            st.markdown("</div><br>", unsafe_allow_html=True)
                        except Exception as e:
                            st.error(f"Putz, a IA tropeçou nos cabos: {e}")
            else:
                st.caption("A chave da IA ainda não foi configurada pelo Gestor no sistema.")

            st.markdown("---")

            # EXTRATO FINANCEIRO
            df_conf = meus_dados[meus_dados['Indicador'] == 'CONFORMIDADE']
            atingimento_conf = df_conf.iloc[0]['% Atingimento'] if not df_conf.empty else 0.0
            tem_dado_conf = not df_conf.empty
            desconto_diamantes = 0
            motivo_desconto = ""
            GATILHO_FINANCEIRO = 0.92
            
            if tem_dado_conf and round(atingimento_conf, 4) < GATILHO_FINANCEIRO:
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
                if round(atingimento_conf, 4) >= GATILHO_FINANCEIRO:
                    st.success(f"✅ **Gatilho Financeiro Atingido**: Conformidade **{atingimento_conf:.2%}** (>= 92%). Todos os diamantes computados.")
            st.divider()

            cols = st.columns(len(meus_dados))
            for i, (_, row) in enumerate(meus_dados.iterrows()):
                val = row['% Atingimento']
                label = formatar_nome_visual(row['Indicador'])
                meta = 0.92 if row['Indicador'] in ['CONFORMIDADE', 'ADERENCIA'] else 0.80
                with cols[i]: st.metric(label, f"{val:.2%}", "✅ Meta Batida" if round(val, 4) >= meta else f"🔻 Meta {meta:.0%}", delta_color="normal" if round(val, 4) >= meta else "inverse")
            st.markdown("---")
            
            # PRODUTIVIDADE OPERADOR
            st.markdown("#### ⏱️ Sua Produtividade")
            df_op_hist = carregar_historico_operacional()
            df_voz_hist = carregar_historico_voz()
            
            c_p1, c_p2, c_p3, c_p4 = st.columns(4)
            
            if df_op_hist is not None:
                df_op_user = df_op_hist[(df_op_hist['Periodo'] == periodo_label) & (df_op_hist['Colaborador'].apply(normalizar_chave) == normalizar_chave(nome_logado))]
                if not df_op_user.empty:
                    vol_chat = int(df_op_user.iloc[0]['Atendimentos'])
                    tma_chat_seg = df_op_user.iloc[0]['TMA_seg']
                    tma_chat_fmt = df_op_user.iloc[0]['TMA_Formatado']
                    
                    media_chat_dia = vol_chat / 22.0
                    delta_vol_c = f"~{media_chat_dia:.0f} por dia (base 22d)"
                    delta_tma_c = "- Dentro da Meta (20m)" if tma_chat_seg <= 1200 else "+ Acima da Meta (20m)"
                        
                    c_p1.metric("💬 Chats Atendidos", vol_chat, delta_vol_c, delta_color="off")
                    c_p2.metric("⏱️ TMA Chat", tma_chat_fmt, delta_tma_c, delta_color="inverse")
                else:
                    c_p1.metric("💬 Chats", "-")
                    c_p2.metric("⏱️ TMA Chat", "-")
            else:
                c_p1.metric("💬 Chats", "-")
                c_p2.metric("⏱️ TMA Chat", "-")

            if df_voz_hist is not None:
                df_voz_user = df_voz_hist[(df_voz_hist['Periodo'] == periodo_label) & (df_voz_hist['Colaborador'].apply(normalizar_chave) == normalizar_chave(nome_logado))]
                if not df_voz_user.empty:
                    vol_voz = int(df_voz_user.iloc[0]['Atendimentos'])
                    tma_voz_seg = df_voz_user.iloc[0]['TMA_seg']
                    tma_voz_fmt = df_voz_user.iloc[0]['TMA_Formatado']
                    
                    media_voz_dia = vol_voz / 22.0
                    delta_vol_v = f"~{media_voz_dia:.0f} por dia (base 22d)"
                    delta_tma_v = "- Dentro da Meta (7m)" if tma_voz_seg <= 420 else "+ Acima da Meta (7m)"
                        
                    c_p3.metric("📞 Ligações Atendidas", vol_voz, delta_vol_v, delta_color="off")
                    c_p4.metric("⏱️ TMA Voz", tma_voz_fmt, delta_tma_v, delta_color="inverse")
                else:
                    c_p3.metric("📞 Ligações", "-")
                    c_p4.metric("⏱️ TMA Voz", "-")
            else:
                c_p3.metric("📞 Ligações", "-")
                c_p4.metric("⏱️ TMA Voz", "-")

            st.markdown("---")
            
            # RAIO X RADAR CHART
            media_equipe = df_dados.groupby('Indicador')['% Atingimento'].mean().reset_index()
            media_equipe.rename(columns={'% Atingimento': 'Média Equipe'}, inplace=True)
            if not media_equipe.empty:
                df_comp = pd.merge(meus_dados, media_equipe, on='Indicador')
                if not df_comp.empty:
                    df_comp['Indicador'] = df_comp['Indicador'].apply(formatar_nome_visual)
                    categorias = df_comp['Indicador'].tolist()
                    valores_user = df_comp['% Atingimento'].tolist()
                    valores_media = df_comp['Média Equipe'].tolist()
                    if categorias:
                        categorias.append(categorias[0])
                        valores_user.append(valores_user[0])
                        valores_media.append(valores_media[0])
                        fig = go.Figure()
                        fig.add_trace(go.Scatterpolar(r=valores_media, theta=categorias, fill='toself', name='Média Equipe', line_color='#cccccc', opacity=0.5))
                        fig.add_trace(go.Scatterpolar(r=valores_user, theta=categorias, fill='toself', name='Você', line_color='#F37021'))
                        fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 1.1])), showlegend=True, height=350, margin=dict(l=40, r=40, t=20, b=20), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                        st.markdown("##### 🕸️ Raio-X de Competências")
                        st.plotly_chart(fig, use_container_width=True)
            st.markdown("---")
            
            # EVOLUÇÃO HISTÓRICA
            st.markdown("### ⏳ Sua Evolução Histórica")
            df_hist_full = carregar_historico_completo()
            if df_hist_full is not None:
                hist_user = df_hist_full[df_hist_full['Colaborador'].astype(str).str.upper().apply(normalizar_chave) == normalizar_chave(nome_logado)].copy()
                if not hist_user.empty:
                    hist_user['Indicador'] = hist_user['Indicador'].apply(formatar_nome_visual)
                    st.plotly_chart(px.line(hist_user, x='Periodo', y='% Atingimento', color='Indicador', markers=True, title="Evolução de Qualidade"), use_container_width=True)

            c_lin1, c_lin2 = st.columns(2)
            if df_op_hist is not None:
                df_op_user_hist = df_op_hist[df_op_hist['Colaborador'].apply(normalizar_chave) == normalizar_chave(nome_logado)].copy()
                if not df_op_user_hist.empty:
                    df_op_user_hist['Data_Ord'] = pd.to_datetime(df_op_user_hist['Periodo'], format='%m/%Y', errors='coerce')
                    df_op_user_hist = df_op_user_hist.sort_values(by='Data_Ord')
                    with c_lin1:
                        fig_line_chat = px.line(df_op_user_hist, x='Periodo', y='TMA_seg', title='Sua Evolução TMA Chat', markers=True, text='TMA_Formatado')
                        fig_line_chat.add_hline(y=1200, line_dash="dash", line_color="red", annotation_text="Meta (20m)")
                        fig_line_chat.update_traces(textposition="top center")
                        fig_line_chat.update_yaxes(visible=False)
                        st.plotly_chart(fig_line_chat, use_container_width=True)

            if df_voz_hist is not None:
                df_voz_user_hist = df_voz_hist[df_voz_hist['Colaborador'].apply(normalizar_chave) == normalizar_chave(nome_logado)].copy()
                if not df_voz_user_hist.empty:
                    df_voz_user_hist['Data_Ord'] = pd.to_datetime(df_voz_user_hist['Periodo'], format='%m/%Y', errors='coerce')
                    df_voz_user_hist = df_voz_user_hist.sort_values(by='Data_Ord')
                    with c_lin2:
                        fig_line_voz = px.line(df_voz_user_hist, x='Periodo', y='TMA_seg', title='Sua Evolução TMA Voz', markers=True, text='TMA_Formatado', color_discrete_sequence=['#8e44ad'])
                        fig_line_voz.add_hline(y=420, line_dash="dash", line_color="red", annotation_text="Meta (7m)")
                        fig_line_voz.update_traces(textposition="top center")
                        fig_line_voz.update_yaxes(visible=False)
                        st.plotly_chart(fig_line_voz, use_container_width=True)

# ---------------------------------------------------------
    # ABA 2: VISÃO DO TIME (PÓDIO FOCADO NO % COM NOME COMPLETO)
    # ---------------------------------------------------------
    with tab_time:
        st.markdown("### 🦁 Visão Geral do Time")
        st.info("Aqui você acompanha como estamos indo como equipe. Lembre-se: quando o time ganha, todos ganham!")

        if df_dados is not None:
            ignorar_pont_op = st.checkbox("Recalcular Visão Global sem Pontualidade", key="chk_pont_op", value=False)
            
            if tem_tam:
                df_base = df_dados[df_dados['Indicador'] == 'TAM'][['Colaborador', 'Diamantes', 'Max. Diamantes']].set_index('Colaborador').copy()
                if ignorar_pont_op:
                    df_pont = df_dados[df_dados['Indicador'] == 'PONTUALIDADE'][['Colaborador', 'Diamantes', 'Max. Diamantes']].set_index('Colaborador').copy()
                    df_base = df_base.subtract(df_pont, fill_value=0)
                df_base['% Atingimento'] = df_base.apply(lambda row: row['Diamantes'] / row['Max. Diamantes'] if row['Max. Diamantes'] > 0 else 0, axis=1)
                df_media_team = df_base.reset_index()
            else:
                if ignorar_pont_op:
                    df_calc = df_dados[df_dados['Indicador'] != 'PONTUALIDADE']
                else:
                    df_calc = df_dados
                df_media_team = df_calc.groupby('Colaborador').agg({'Diamantes': 'sum', 'Max. Diamantes': 'sum'}).reset_index()
                df_media_team['% Atingimento'] = df_media_team.apply(lambda row: row['Diamantes'] / row['Max. Diamantes'] if row['Max. Diamantes'] > 0 else 0, axis=1)

            total_dia_team = df_media_team['Diamantes'].sum()
            total_max_team = df_media_team['Max. Diamantes'].sum()
            perc_team = (total_dia_team / total_max_team) if total_max_team > 0 else 0
            
            user_share_row = df_media_team[df_media_team['Colaborador'] == nome_logado]
            msg_share = "Dados insuficientes"
            if not user_share_row.empty and total_dia_team > 0:
                user_dia = user_share_row.iloc[0]['Diamantes']
                share = (user_dia / total_dia_team)
                msg_share = f"Você representa **{share:.1%}** do resultado da equipe."

            # PÓDIO TOP 3
            st.markdown("---")
            st.markdown("### 🏆 Pódio Team Sofistas - Top 3")
            
            if not df_media_team.empty:
                # CORREÇÃO AQUI: Ordenando matematicamente pelo % de Atingimento, e não mais por Diamantes
                df_podio = df_media_team[~df_media_team['Colaborador'].str.startswith('⚠️')].sort_values(by='% Atingimento', ascending=False).head(3).reset_index(drop=True)
                
                if len(df_podio) >= 1:
                    col1, col2, col3 = st.columns(3)
                    ordem_colunas = [col2, col1, col3] 
                    posicoes_legenda = ["🥇 1º LUGAR", "🥈 2º LUGAR", "🥉 3º LUGAR"]
                    cores_borda = ["#d4af37", "#a9a9a9", "#cd7f32"] 

                    for i, col in enumerate(ordem_colunas):
                        if i < len(df_podio):
                            op_data = df_podio.iloc[i]
                            op_nome = op_data['Colaborador']
                            op_perc = op_data['% Atingimento']
                            
                            # 1. CHAMA A FUNÇÃO QUE JÁ SABE SE É FOTO OU AVATAR
                            img_perfil = obter_imagem_perfil(op_nome)

                            with col:
                                st.markdown(f"<h4 style='text-align: center; color: #003366;'>{posicoes_legenda[i]}</h4>", unsafe_allow_html=True)
                                
                                st.markdown(f"""
                                    <div style="background-color: #FFF; border: 4px solid {cores_borda[i]}; padding: 15px; border-radius: 12px; text-align: center; box-shadow: 0 4px 10px rgba(0,0,0,0.1); margin-bottom: 20px;">
                                """, unsafe_allow_html=True)
                                
                                # 2. AQUI ESTAVA O ERRO: AGORA USAMOS A VARIÁVEL img_perfil
                                if img_perfil:
                                    st.markdown(f"""
                                        <img src="{img_perfil}" style="border-radius: 50%; width: 100px; height: 100px; object-fit: cover; border: 4px solid {cores_borda[i]}; box-shadow: 0 4px 8px rgba(0,0,0,0.1); display: block; margin: 0 auto 10px auto;">
                                    """, unsafe_allow_html=True)
                                else:
                                    # Se não tiver foto nem avatar, mostra o ícone cinza
                                    st.markdown("<h1 style='font-size: 60px; text-align: center; margin:0;'>👤</h1>", unsafe_allow_html=True)
                                    
                                st.markdown(f"""
                                    <p style="font-size: 1.1em; font-weight: bold; color: #333; margin: 5px 0; text-align: center;">{op_nome.title()}</p>
                                    <p style="font-size: 1.8em; font-weight: 800; color: {cores_borda[i]}; margin: 5px 0; text-align: center;">{op_perc:.2%}</p>
                                    </div>
                                """, unsafe_allow_html=True)
                                
            st.markdown("---")

            # Display Global
            c1, c2 = st.columns(2)
            c1.markdown(f"#### 🦁 Média Global da Equipe: **{perc_team:.1%}**")
            c2.success(msg_share)
            
            fig_team = go.Figure(go.Indicator(
                mode = "gauge+number", value = perc_team * 100, domain = {'x': [0, 1], 'y': [0, 1]},
                gauge = {
                    'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': 'white'}, 'bar': {'color': "#003366"},
                    'steps': [{'range': [0, 80], 'color': '#ffcccb'},{'range': [80, 90], 'color': '#fff4cc'},{'range': [90, 100], 'color': '#d9f7be'}],
                    'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': 100}
                }
            ))
            fig_team.update_layout(height=250, margin=dict(l=20, r=20, t=30, b=20))
            st.plotly_chart(fig_team, use_container_width=True)

    # ---------------------------------------------------------
    # ABA 3: FÉRIAS
    # ---------------------------------------------------------
    with tab_ferias:
        minhas_ferias = "Não informado"
        
        # 1. Puxa a base oficial de usuários já carregada pelo sistema
        if df_users_cadastrados is not None and not df_users_cadastrados.empty:
            # Procura a linha exata do operador logado
            nome_busca = normalizar_chave(nome_logado)
            user_info = df_users_cadastrados[df_users_cadastrados['nome'] == nome_busca]
            
            if not user_info.empty and 'ferias' in user_info.columns:
                valor_ferias = str(user_info.iloc[0]['ferias']).strip()
                
                # Se o campo não estiver vazio na sua planilha de admin
                if valor_ferias.lower() not in ['nan', 'none', '', 'nat']:
                    minhas_ferias = valor_ferias
                else:
                    minhas_ferias = "Data a definir"

        # 2. Desenha o Card Premium (Clean Glass)
        st.markdown(f"""
        <div style='background-color: #FFFFFF; padding: 30px; border-radius: 20px; border-top: 6px solid #003366; box-shadow: 0 8px 24px rgba(0,0,0,0.04); text-align: center; margin-top: 20px;'>
            <h1 style='font-size: 50px; margin-bottom: 10px;'>🏖️</h1>
            <p style='color: #6B7280; font-size: 1.1em; font-weight: 600; margin-bottom: 5px;'>Suas próximas férias estão programadas para:</p>
            <div style='color: #111827; font-size: 2em; font-weight: 800; margin-bottom: 15px;'>{minhas_ferias}</div>
            <p style='color: #9CA3AF; font-size: 0.85em;'>*Baseado no seu cadastro oficial. Consulte sempre a Liderança para alinhar os detalhes.</p>
        </div>
        """, unsafe_allow_html=True)
    # ---------------------------------------------------------
    # ABA 4: FEEDBACKS
    # ---------------------------------------------------------
    with tab_feedbacks:
        st.markdown("### 📝 Histórico de Feedbacks")
        df_fbs = carregar_feedbacks_gb()
        if df_fbs is not None and not df_fbs.empty:
            df_fbs['Colaborador_Norm'] = df_fbs['Colaborador'].apply(normalizar_chave)
            meus_fbs = df_fbs[df_fbs['Colaborador_Norm'] == normalizar_chave(nome_logado)].copy()
            if not meus_fbs.empty:
                for _, row in meus_fbs.iloc[::-1].iterrows():
                    with st.expander(f"📅 {row['Periodo_Ref']} | 🎯 Resultado TAM: {row['TAM']} {row.get('Faixa', '')}"):
                        st.markdown(f"**🎯 Motivos:**\n> {row['Motivo']}\n\n**🚀 Plano de Ação:**\n> {row['Acao_GB']}\n\n**💡 Feedback:**\n> {row['Feedback_Valor']}")
            else: st.info("Você ainda não possui registros de feedback no sistema.")
        else: st.info("Nenhum feedback registrado no sistema até o momento.")

    # ---------------------------------------------------------
    # ABA 5: BANCO DE HORAS
    # ---------------------------------------------------------
    with tab_banco:
        st.markdown("### ⏰ Meu Banco de Horas")
        df_saldos = carregar_saldos_banco()
        if df_saldos is not None and not df_saldos.empty:
            df_saldos['Colaborador_Norm'] = df_saldos['Colaborador'].apply(normalizar_chave)
            meu_saldo_row = df_saldos[df_saldos['Colaborador_Norm'] == normalizar_chave(nome_logado)]
            
            if not meu_saldo_row.empty:
                saldo_str = meu_saldo_row.iloc[0]['Saldo String']
                saldo_h = meu_saldo_row.iloc[0]['Saldo (h)']
                
                if saldo_h < 0:
                    cor_delta = "inverse"
                    st_delta = "Devendo Horas"
                else:
                    cor_delta = "normal"
                    st_delta = "Horas Positivas"
                    
                st.markdown("#### ⚖️ Seu Saldo Atual")
                c_s1, c_s2 = st.columns([1, 3])
                c_s1.metric("Saldo de Horas", saldo_str, st_delta, delta_color=cor_delta)
                
                if saldo_h < 0:
                    c_s2.error(f"⚠️ **Atenção!** Você está com **{saldo_str}** negativas. Fique de olho na aba de Agendamentos para alinhar o pagamento com a gestão.")
                else:
                    c_s2.success(f"🎉 **Parabéns!** Você tem **{saldo_str}** positivas. Caso deseje, alinhe com seu gestor para retirar essas horas (folga ou sair mais cedo).")
                st.markdown("---")

        st.markdown("#### 📅 Seus Agendamentos")
        df_banco = carregar_escalas_banco()
        if df_banco is not None and not df_banco.empty:
            df_banco['Colaborador_Norm'] = df_banco['Colaborador'].apply(normalizar_chave)
            meus_agendamentos = df_banco[df_banco['Colaborador_Norm'] == normalizar_chave(nome_logado)].copy()
            
            if not meus_agendamentos.empty:
                st.info("Abaixo estão as suas solicitações de folgas/retiradas ou dias de pagamento de horas já alinhadas com a coordenação.")
                for _, row in meus_agendamentos.iloc[::-1].iterrows():
                    cor_borda = "#2ecc71" if "Retirada" in row['Tipo'] else "#e74c3c"
                    icone = "🏖️" if "Retirada" in row['Tipo'] else "💼"
                    st.markdown(f"""
                    <div style="border-left: 5px solid {cor_borda}; padding: 15px; background-color: #FFF; border-radius: 8px; box-shadow: 0 4px 10px rgba(0,0,0,0.05); margin-bottom: 15px;">
                        <h4 style="margin-top: 0; color: #003366;">{icone} {row['Tipo'].upper()}</h4>
                        <p style="margin: 5px 0;"><b>Data:</b> {row['Data_Inicio']} até {row['Data_Fim']}</p>
                        <p style="margin: 5px 0;"><b>Horário:</b> {row['Horario_Inicial']} às {row['Horario_Final']}</p>
                        <p style="margin: 5px 0; color: #666;"><b>Total de Horas:</b> {row['Quantidade']}</p>
                        <p style="margin: 5px 0; font-size: 12px; color: #999;">Registrado em: {row.get('Periodo_Registro', 'N/A')}</p>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.success("Você não possui agendamentos futuros no momento.")
        else:
            st.success("Você não possui agendamentos futuros no momento.")

    # ---------------------------------------------------------
    # ABA 6: ASSISTENTE TÉCNICO IA
    # ---------------------------------------------------------
    with tab_ia:
        st.markdown("### 🤖 Sofistas AI - Seu Assistente Técnico")
        st.info("Tire dúvidas sobre internet, Wi-Fi, roteadores, fibra óptica, ou até mesmo pergunte sobre seus indicadores e diamantes deste mês!")

        if "GEMINI_API_KEY" in st.secrets:
            import google.generativeai as genai
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            model = genai.GenerativeModel('gemini-2.5-flash')

            if "mensagens_ia_op" not in st.session_state:
                st.session_state.mensagens_ia_op = []

            for msg in st.session_state.mensagens_ia_op:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

            if prompt := st.chat_input("Ex: O que causa lentidão no Wi-Fi 2.4GHz? ou Como foi meu CSAT?"):
                with st.chat_message("user"):
                    st.markdown(prompt)
                st.session_state.mensagens_ia_op.append({"role": "user", "content": prompt})

                contexto_op = ""
                if not meus_dados.empty:
                    contexto_op = f"\n[DADOS DO OPERADOR {nome_logado.upper()} NESTE MÊS]:\n{meus_dados[['Indicador', '% Atingimento', 'Diamantes']].to_csv(index=False)}"

                instrucao_sistema = f"""
                Você é o Sofistas AI, um assistente virtual criado para ajudar os operadores de suporte técnico de um provedor de internet (ISP).
                Seu objetivo principal é ajudar o operador a resolver dúvidas técnicas do dia a dia (redes, Wi-Fi, fibra, roteadores, lentidão, etc) de forma didática, clara e direta ao ponto, para que ele possa atender bem o cliente na linha.
                Você também tem acesso aos resultados de performance dele no mês: {contexto_op}.
                Se ele perguntar sobre os indicadores dele, responda de forma amigável e motivadora.
                """

                with st.chat_message("assistant"):
                    with st.spinner("Sofistas AI digitando..."):
                        try:
                            resposta = model.generate_content(f"{instrucao_sistema}\n\nPergunta do Operador: {prompt}")
                            st.markdown(resposta.text)
                            st.session_state.mensagens_ia_op.append({"role": "assistant", "content": resposta.text})
                        except Exception as e:
                            st.error(f"Erro ao conectar com a IA: {e}")
        else:
            st.warning("⚠️ O Gestor ainda não configurou a chave da Inteligência Artificial no sistema.")
# ---------------------------------------------------------
    # ABA 7: MURAL DE CELEBRAÇÕES (OPERADOR)
    # ---------------------------------------------------------
    with tab_celebracoes:
        st.markdown("### 🎉 Mural de Celebrações")
        st.info("Fique de olho nos aniversariantes do mês e mande os parabéns para a equipe! 🎈")
        
        meses_pt = {1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril', 5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto', 9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'}
        hoje = datetime.now()
        mes_atual = hoje.month
        
        lista_niver, lista_firma = [], []
        
        if df_users_cadastrados is not None:
            for _, row in df_users_cadastrados.iterrows():
                nome_colab = str(row.get('nome', '')).title()
                
                # 🎂 Aniversário
                nasc_str = str(row.get('nascimento', '')).strip()
                if nasc_str and nasc_str != 'nan':
                    try:
                        dia_n, mes_n = int(nasc_str.split('/')[0]), int(nasc_str.split('/')[1])
                        if mes_n == mes_atual:
                            lista_niver.append({'dia': dia_n, 'nome': nome_colab, 'data': f"{dia_n:02d}/{mes_n:02d}"})
                    except: pass
                    
                # 💼 Tempo de Casa
                adm_str = str(row.get('admissao', '')).strip()
                if adm_str and adm_str != 'nan':
                    try:
                        data_adm = datetime.strptime(adm_str, "%d/%m/%Y")
                        if data_adm.month == mes_atual:
                            anos_casa = hoje.year - data_adm.year
                            if anos_casa > 0:
                                lista_firma.append({'dia': data_adm.day, 'nome': nome_colab, 'anos': anos_casa, 'data': f"{data_adm.day:02d}/{data_adm.month:02d}"})
                    except: pass

        lista_niver = sorted(lista_niver, key=lambda x: x['dia'])
        lista_firma = sorted(lista_firma, key=lambda x: x['dia'])
        
        st.markdown(f"<h4 style='text-align: center; color: #003366; margin-top: 20px;'>Celebrações de {meses_pt[mes_atual]}</h4>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        
        with c1:
            st.markdown("##### 🎂 Aniversários de Vida")
            if lista_niver:
                for item in lista_niver:
                    is_today = "🎈 HOJE!" if item['dia'] == hoje.day else ""
                    st.markdown(f"<div style='padding:12px; background-color:#FFF; border-left:5px solid #F37021; margin-bottom:10px; border-radius:8px; box-shadow:0 2px 8px rgba(0,0,0,0.05); display:flex; justify-content:space-between;'><span><b>{item['data']}</b> - {item['nome']}</span><span style='color:#e74c3c; font-weight:bold;'>{is_today}</span></div>", unsafe_allow_html=True)
            else: st.write("Nenhum aniversariante neste mês.")
                
        with c2:
            st.markdown("##### 💼 Tempo de Casa")
            if lista_firma:
                for item in lista_firma:
                    anos_texto = f"{item['anos']} ano" if item['anos'] == 1 else f"{item['anos']} anos"
                    st.markdown(f"<div style='padding:12px; background-color:#FFF; border-left:5px solid #003366; margin-bottom:10px; border-radius:8px; box-shadow:0 2px 8px rgba(0,0,0,0.05); display:flex; justify-content:space-between;'><span><b>{item['data']}</b> - {item['nome']}</span><span style='background-color:#e0f7fa; padding:2px 10px; border-radius:12px; font-size:0.85em; color:#006064; font-weight:bold;'>{anos_texto}</span></div>", unsafe_allow_html=True)
            else: st.write("Ninguém completando tempo de casa neste mês.")

# --- 💌 MURAL DE RECADINHOS ---
        st.markdown("---")
        st.markdown("### 💌 Mural de Recadinhos")
        st.write("Deixe uma mensagem de carinho para os aniversariantes deste mês!")

        aniversariantes_nomes = [item['nome'] for item in lista_niver]
        
        if aniversariantes_nomes:
            # Formulário para enviar o recado
            with st.form("form_recado"):
                c_quem, c_vazio = st.columns([1, 2])
                para_quem = c_quem.selectbox("Para quem é o recado?", aniversariantes_nomes)
                mensagem = st.text_area("Escreva sua mensagem (ela ficará visível para toda a equipe):", placeholder="Ex: Parabéns, guerreiro! Muito sucesso e saúde! 🎉")
                
                if st.form_submit_button("Enviar Recado 🎈"):
                    if mensagem.strip():
                        salvar_mensagem_mural({
                            "Data": datetime.now().strftime("%d/%m/%Y %H:%M"),
                            "De": primeiro_nome.title(),
                            "Para": para_quem,
                            "Mensagem": mensagem
                        })
                        st.success("✅ Recado enviado com sucesso!")
                        import time
                        time.sleep(1.5)
                        st.rerun()
                    else:
                        st.error("⚠️ Escreva algo antes de enviar!")
        else:
            st.info("Nenhum aniversariante neste mês para deixar recado.")

        # --- EXIBIÇÃO DOS RECADOS ---
        df_mural = carregar_mensagens_mural()
        if df_mural is not None and not df_mural.empty:
            st.markdown("#### 📬 Recados Recentes")
            
            # Filtramos só os recados para os aniversariantes do mês atual
            recados_mes = df_mural[df_mural['Para'].isin(aniversariantes_nomes)]
            
            if not recados_mes.empty:
                for _, row in recados_mes.iloc[::-1].iterrows():
                    # Se o recado for para o usuário logado, damos um destaque dourado!
                    eh_pra_mim = row['Para'].upper() == nome_logado.upper()
                    cor_fundo = "#fff8e1" if eh_pra_mim else "#FFF"
                    cor_borda = "#ffc107" if eh_pra_mim else "#003366"
                    tag_especial = "<span style='background-color:#ffc107; color:#555; padding:2px 8px; border-radius:10px; font-size:0.8em; font-weight:bold; margin-left:10px;'>É PRA VOCÊ! 🎉</span>" if eh_pra_mim else ""
                    
                    st.markdown(f"""
                    <div style='background-color:{cor_fundo}; padding:15px; border-radius:10px; border-left: 5px solid {cor_borda}; margin-bottom:15px; box-shadow: 0 4px 10px rgba(0,0,0,0.05);'>
                        <p style='margin:0; color:#555; font-size:0.9em;'>
                            De: <b>{row['De']}</b> ➔ Para: <b style="color: {cor_borda};">{row['Para']}</b> {tag_especial}
                            <span style='float:right; font-size:0.8em; color:#999;'>{row['Data']}</span>
                        </p>
                        <p style='margin-top:10px; margin-bottom:0; font-size:1.05em; color:#333; font-style: italic;'>"{row['Mensagem']}"</p>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.write("Ainda não há recados neste mês. Seja o primeiro a escrever!")
# ==========================================
# RODAPÉ DO SISTEMA
# ==========================================
st.markdown("---")
st.markdown('<div class="dev-footer">Desenvolvido por Klebson Davi - Supervisor de Suporte Técnico</div>', unsafe_allow_html=True)
