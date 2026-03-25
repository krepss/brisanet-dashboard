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

# --- CONFIGURAÇÃO DA LOGO E ACESSOS ---
LOGO_FILE = "logo.png"
SENHA_ADMIN = "admin123"
USUARIOS_ADMIN = ['gestor', 'admin']

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

# --- 2. CSS COMPACTADO (DESIGN PREMIUM + CARDS) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;600;800&family=Roboto:wght@300;400;700&display=swap');
    html,body{scroll-behavior:smooth!important;font-family:'Roboto',sans-serif;}
    .stApp{background-color:#F4F7F6!important;}
    [data-testid="collapsedControl"],[data-testid="stSidebar"]{display:none!important;}
    .top-banner{background:linear-gradient(135deg,#002b55 0%,#004e92 100%);padding:20px 30px;border-radius:15px;box-shadow:0 8px 20px rgba(0,0,0,0.15);display:flex;justify-content:space-between;align-items:center;margin-bottom:25px;}
    .top-banner h2,.top-banner h4{color:#FFF!important;margin:0!important;padding:0!important;font-family:'Montserrat',sans-serif!important;}
    .top-banner h2{font-weight:800!important;letter-spacing:1px!important;font-size:28px!important;}
    .top-banner h4{font-weight:600!important;font-size:20px!important;}
    .top-banner .sub-text{color:#cce0ff!important;margin:0!important;padding:0!important;font-size:14px!important;font-weight:400!important;}
    button[kind="primary"]{background-color:#e74c3c!important;border:1px solid #c0392b!important;border-radius:8px!important;}
    button[kind="primary"] p{color:#FFF!important;font-weight:bold!important;}
    button[kind="primary"]:hover{background-color:#c0392b!important;border-color:#a93226!important;}
    button[kind="secondary"]{background-color:#003366!important;color:#FFF!important;border-radius:8px!important;font-weight:bold!important;border:none!important;}
    button[kind="secondary"] p{color:#FFF!important;}
    h1,h2,h3,h4,h5,h6{color:#003366!important;font-family:'Montserrat',sans-serif!important;}
    p,li,div{color:#333;}
    div.stMetric,.insight-box,.badge-card{background-color:#FFF!important;box-shadow:0 4px 10px rgba(0,0,0,0.05);border-radius:10px;}
    .card-link{text-decoration:none!important;display:block;}
    .card-excelencia,.card-meta,.card-critico{background-color:#FFF;box-shadow:0 4px 10px rgba(0,0,0,0.05);border-radius:10px;border:1px solid #e0e0e0;padding:10px 15px;cursor:pointer;transition:all .3s ease;}
    .card-excelencia{border-left:5px solid #003366;}
    .card-excelencia:hover{transform:scale(1.03);box-shadow:0 6px 15px rgba(0,51,102,.2);}
    .card-meta{border-left:5px solid #2ecc71;}
    .card-meta:hover{transform:scale(1.03);box-shadow:0 6px 15px rgba(46,204,113,.2);}
    .card-critico{border-left:5px solid #e74c3c;}
    .card-critico:hover{transform:scale(1.03);box-shadow:0 6px 15px rgba(231,76,60,.2);}
    .vacation-card{background-color:#FFF!important;border-left:8px solid #00bcd4!important;padding:30px!important;border-radius:12px!important;text-align:center!important;box-shadow:0 6px 15px rgba(0,0,0,0.08)!important;margin-top:20px!important;}
    .vacation-title{font-family:'Montserrat',sans-serif!important;font-size:1.4em!important;font-weight:600!important;color:#555!important;margin-bottom:10px!important;}
    .vacation-date{font-family:'Roboto',sans-serif!important;font-size:3.5em!important;font-weight:800!important;color:#00838f!important;margin:20px 0!important;text-transform:uppercase!important;}
    .vacation-note{font-size:.9em!important;color:#999!important;font-style:italic!important;}
    [data-testid="stForm"]{background-color:#FFF!important;padding:3rem 2rem!important;border-radius:20px!important;box-shadow:0 15px 35px rgba(0,0,0,0.1)!important;border:none!important;border-top:6px solid #F37021!important;}
    .login-title{font-family:'Montserrat',sans-serif!important;font-weight:800!important;font-size:2.2rem!important;color:#003366!important;text-align:center;margin-bottom:0px;}
    .login-subtitle{font-family:'Roboto',sans-serif!important;font-size:1.1rem!important;color:#666!important;text-align:center;margin-bottom:25px;}
    [data-testid="stForm"] input{background-color:#f8f9fa!important;color:#333!important;border-radius:8px!important;}
    [data-testid="stFileUploader"] button{background-color:#003366!important;color:#FFF!important;border:none!important;}
    [data-testid="stFileUploader"] button:hover{background-color:#F37021!important;}
    div.stMetric{border:1px solid #e0e0e0;border-left:5px solid #F37021;padding:10px 15px!important;}
    div.stMetric label{color:#666!important;font-size:14px!important;}
    div.stMetric div[data-testid="stMetricValue"]{color:#003366!important;font-size:26px!important;font-weight:700;}
    div.stMetric div[data-testid="stMetricDelta"]{font-size:13px!important;}
    .update-badge{background-color:#e3f2fd;color:#0d47a1;padding:5px 10px;border-radius:15px;font-size:.85em;font-weight:bold;border:1px solid #bbdefb;}
    .insight-box{background-color:#fff8e1!important;border-left:5px solid #ffc107!important;padding:15px;margin-bottom:20px;}
    .insight-title{font-weight:bold;color:#d35400;font-size:1.1em;display:flex;align-items:center;gap:8px;}
    .insight-text{font-size:.95em;margin-top:5px;color:#555;}
    .dev-footer{text-align:center;margin-top:40px;font-size:.8em;color:#aaa!important;}
</style>
""", unsafe_allow_html=True)

# --- 3. FUNÇÕES DE BACKEND ---

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
        if (f.endswith('.csv') or f.endswith('.xlsx') or f.endswith('.xls')) and f not in protegidos:
            try: os.remove(f)
            except: pass

# --- LEITOR UNIVERSAL BLINDADO COM MULTI-ENCODING ---
def ler_arquivo_inteligente(arquivo_ou_caminho):
    nome = getattr(arquivo_ou_caminho, 'name', '')
    if isinstance(arquivo_ou_caminho, str): nome = arquivo_ou_caminho
        
    if nome.lower().endswith('.xlsx') or nome.lower().endswith('.xls'):
        try:
            if hasattr(arquivo_ou_caminho, 'seek'): arquivo_ou_caminho.seek(0)
            return pd.read_excel(arquivo_ou_caminho, dtype=str)
        except Exception as e:
            print(f"Erro ao ler Excel: {e}")
            return None
            
    # Array de encodings típicos do Brasil e sistemas internacionais
    encodings = ['utf-8-sig', 'utf-8', 'latin1', 'cp1252', 'ISO-8859-1']
    
    # 1. Super Sniffer Agressivo: Tenta ler o arquivo garantindo que vírgulas em números não quebrem as colunas
    for enc in encodings:
        try:
            if hasattr(arquivo_ou_caminho, 'seek'): arquivo_ou_caminho.seek(0)
            df = pd.read_csv(arquivo_ou_caminho, sep=None, engine='python', encoding=enc, dtype=str)
            if len(df.columns) > 1: 
                return df
        except:
            pass
            
    # 2. Força Bruta de Separadores (caso o Sniffer falhe)
    for sep in [';', ',', '\t', '|']:
        for enc in encodings:
            try:
                if hasattr(arquivo_ou_caminho, 'seek'): arquivo_ou_caminho.seek(0)
                df = pd.read_csv(arquivo_ou_caminho, sep=sep, encoding=enc, dtype=str, on_bad_lines='skip')
                if len(df.columns) > 1: 
                    return df
            except: 
                continue
                
    return None

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

def atualizar_saldos_banco(df_novo, periodo):
    ARQ = 'saldo_banco_horas.csv'
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
    sincronizar_com_github(ARQ, f"Atualizando saldos de banco de horas - {periodo}")

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
    
    # 1. Identifica as colunas cravando no símbolo "%" ou outras palavras chave (blindado para maiusculas/minusculas)
    col_ad = next((c for c in df.columns if 'ader' in c and ('%' in c or 'perc' in c or 'nota' in c or 'resultado' in c)), None)
    if not col_ad: 
        col_ad = next((c for c in df.columns if 'ader' in c and 'duração' not in c and 'programado' not in c and c != 'colaborador'), None)
        
    col_conf = next((c for c in df.columns if 'conform' in c and ('%' in c or 'perc' in c or 'nota' in c or 'resultado' in c)), None)
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
    
    # --- Extração Simples Agressiva ---
    col_valor = None
    nome_indicador = normalizar_nome_indicador(nome_arquivo)
    
    if col_conf and not col_ad:
        col_valor = col_conf
        nome_indicador = 'CONFORMIDADE'
    elif col_ad and not col_conf:
        col_valor = col_ad
        nome_indicador = 'ADERENCIA'
    else:
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
            else: return None, "Nenhuma coluna de nota identificada."
            
    df.rename(columns={col_valor: '% Atingimento'}, inplace=True)
    
    for c in df.columns:
        if 'diamantes' in c and 'max' not in c: df.rename(columns={c: 'Diamantes'}, inplace=True)
        if 'max' in c and 'diamantes' in c: df.rename(columns={c: 'Max. Diamantes'}, inplace=True)
    
    df['% Atingimento'] = df['% Atingimento'].apply(processar_porcentagem_br)
    
    if 'Diamantes' not in df.columns: df['Diamantes'] = 0.0
    if 'Max. Diamantes' not in df.columns: df['Max. Diamantes'] = 0.0
    
    df['Diamantes'] = pd.to_numeric(df['Diamantes'], errors='coerce').fillna(0)
    df['Max. Diamantes'] = pd.to_numeric(df['Max. Diamantes'], errors='coerce').fillna(0)
    
    df['Indicador'] = nome_indicador
    cols_to_keep = ['Colaborador', 'Indicador', '% Atingimento', 'Diamantes', 'Max. Diamantes']
    return df[cols_to_keep], "Extração Simples Agressiva"

def classificar_farol(val):
    if val >= 0.90: return '💎 Excelência' 
    elif val >= 0.80: return '🟢 Meta Batida'
    else: return '🔴 Crítico'

def carregar_dados_completo_debug():
    lista_final = []
    log_debug = []
    arquivos_ignorar = ['usuarios.csv', 'historico_consolidado.csv', 'config.json', LOGO_FILE, 'feedbacks_gb.csv', 'feedbacks_gb_backup.csv', 'historico_operacional.csv', 'historico_voz.csv', 'escalas_banco_horas.csv', 'saldo_banco_horas.csv']
    arquivos = [f for f in os.listdir('.') if (f.endswith('.csv') or f.endswith('.xlsx') or f.endswith('.xls')) and f.lower() not in arquivos_ignorar]
    for arquivo in arquivos:
        try:
            df_bruto = ler_arquivo_inteligente(arquivo)
            if df_bruto is not None:
                df_tratado, msg = tratar_arquivo_especial(df_bruto, arquivo)
                log_debug.append({"Arquivo": arquivo, "Status": "OK" if df_tratado is not None else "Erro", "Detalhe": msg})
                if df_tratado is not None: lista_final.append(df_tratado)
            else: log_debug.append({"Arquivo": arquivo, "Status": "Erro", "Detalhe": "Não conseguiu ler o arquivo / Separador inválido"})
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
    arquivos = [f for f in os.listdir('.') if (f.endswith('.csv') or f.endswith('.xlsx')) and 'usuario' in f.lower()]
    if arquivos:
        df = ler_arquivo_inteligente(arquivos[0])
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
                df = ler_arquivo_inteligente(nome)
                if df is not None: return df
                return pd.read_csv(nome)
            except: continue
    return None

# --- 4. LOGIN RENOVADO ---
if 'logado' not in st.session_state:
    st.session_state.update({'log
