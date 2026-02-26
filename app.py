import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import json
import time
import base64
from datetime import datetime
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

def obter_data_hoje(): return datetime.now().strftime("%m/%Y")
def obter_data_atualizacao():
    if os.path.exists('historico_consolidado.csv'): return datetime.fromtimestamp(os.path.getmtime('historico_consolidado.csv')).strftime("%d/%m/%Y às %H:%M")
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
    for f in os.listdir('.'): 
        if f.endswith('.csv'): os.remove(f)
def faxina_arquivos_temporarios():
    protegidos = ['historico_consolidado.csv', 'usuarios.csv', 'config.json', LOGO_FILE, 'feedbacks_gb.csv']
    for f in os.listdir('.'):
        if f.endswith('.csv') and f not in protegidos:
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
    
    cols_order = ['Periodo', 'Colaborador', 'Indicador', '% Atingimento', 'Diamantes', 'Max. Diamantes']
    existing_cols = [c for c in cols_order if c in df_final.columns]
    for c in ['Diamantes', 'Max. Diamantes']:
        if c in existing_cols: df_final[c] = df_final[c].fillna(0.0)
            
    df_final[existing_cols].to_csv(ARQUIVO_HIST, index=False)

def excluir_periodo_historico(periodo_alvo):
    if os.path.exists('historico_consolidado.csv'):
        try:
            df_hist = pd.read_csv('historico_consolidado.csv')
            df_hist['Periodo'] = df_hist['Periodo'].astype(str).str.strip()
            df_novo = df_hist[df_hist['Periodo'] != str(periodo_alvo).strip()]
            df_novo.to_csv('historico_consolidado.csv', index=False)
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

# --- LÓGICA ULTRA-SEGURA DE BUSCA DE COLUNAS (CONFORMIDADE E ADERENCIA) ---
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
    arquivos_ignorar = ['usuarios.csv', 'historico_consolidado.csv', 'config.json', LOGO_FILE, 'feedbacks_gb.csv']
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

def salvar_feedback_gb(dados_fb):
    ARQUIVO_FB = 'feedbacks_gb.csv'
    df_novo = pd.DataFrame([dados_fb])
    if os.path.exists(ARQUIVO_FB):
        try:
            df_hist = pd.read_csv(ARQUIVO_FB)
            df_final = pd.concat([df_hist, df_novo], ignore_index=True)
        except: df_final = df_novo
    else: df_final = df_novo
    df_final.to_csv(ARQUIVO_FB, index=False)

def carregar_feedbacks_gb():
    if os.path.exists('feedbacks_gb.csv'):
        try: return pd.read_csv('feedbacks_gb.csv')
        except: return None
    return None

# --- 4. LOGIN RENOVADO ---
if 'logado' not in st.session_state:
    st.session_state.update({'logado': False, 'usuario_nome': '', 'perfil': '', 'usuario_email': ''})

if not st.session_state['logado']:
    c1, c2, c3 = st.columns([1, 1.2, 1]) 
    with c2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        with st.form("form_login"):
            if os.path.exists(LOGO_FILE):
                col_espaco1, col_logo, col_espaco2 = st.columns([1, 0.6, 1])
                with col_logo: st.image(LOGO_FILE, use_column_width=True)
            
            st.markdown('<div class="login-title">Team Sofistas</div>', unsafe_allow_html=True)
            st.markdown('<div class="login-subtitle">Analytics & Performance</div>', unsafe_allow_html=True)
            st.markdown("---")
            email_input = st.text_input("E-mail ou Usuário").strip().lower()
            senha_input = st.text_input("Senha", type="password")
            st.markdown("<br>", unsafe_allow_html=True)
            submit_btn = st.form_submit_button("ACESSAR SISTEMA", use_container_width=True)
            if submit_btn:
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
                        else: st.error("🚫 Usuário não encontrado.")
                    else: st.error("⚠️ Base de usuários não carregada.")
    st.markdown('<div class="dev-footer">Desenvolvido por Klebson Davi</div>', unsafe_allow_html=True)
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
        <h4>Olá, {nome_logado.split()[0]}! 👋</h4>
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
        st.rerun()

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
    tabs = st.tabs(["🚦 Semáforo", "📈 Resumo Executivo", "🏆 Ranking Geral", "⏳ Evolução", "🔍 Indicadores", "💰 Comissões", "📋 Tabela Geral", "🏖️ Férias Equipe", "⚙️ Admin", "⏰ Banco de Horas", "📝 Feedbacks GB"])

    # ------------------ SEMÁFORO ------------------
    with tabs[0]: 
        if df_dados is not None and not df_dados.empty:
            st.markdown(f"### Resumo de Saúde: **{periodo_label}**")
            
            if tem_tam:
                df_media_pessoas = df_dados[df_dados['Indicador'] == 'TAM'][['Colaborador', '% Atingimento']].copy()
            else:
                df_media_pessoas = df_dados.groupby('Colaborador').agg({'Diamantes': 'sum', 'Max. Diamantes': 'sum'}).reset_index()
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

            st.markdown("---")
            st.subheader("💬 Gerador de Feedback Rápido (1:1)")
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
                    </div>""", unsafe_allow_html=True)
            st.markdown("---")
            
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
                media_ad = df_dados[df_dados['Indicador'] == 'ADERENCIA']['% Atingimento'].mean() if 'ADERENCIA' in df_dados['Indicador'].unique() else 0.0
                media_conf = df_dados[df_dados['Indicador'] == 'CONFORMIDADE']['% Atingimento'].mean() if 'CONFORMIDADE' in df_dados['Indicador'].unique() else 0.0
                
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
                                    texto_comparacao = f" Em comparação ao mês anterior ({periodo_anterior}), tivemos um **crescimento de {variacao*100:.1f} p.p.** na performance global da equipe (era {media_anterior_tam:.1%}). 🚀"
                                elif variacao < -0.001:
                                    texto_comparacao = f" Em comparação ao mês anterior ({periodo_anterior}), tivemos uma **queda de {abs(variacao)*100:.1f} p.p.** na performance global da equipe (era {media_anterior_tam:.1%}). 📉"
                                else:
                                    texto_comparacao = f" Em comparação ao mês anterior ({periodo_anterior}), mantivemos a performance global estável (era {media_anterior_tam:.1%}). ⚖️"

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

                texto_resumo = f"""**Resumo Executivo - {periodo_label} | Team Sofistas**

**1. Visão Geral da Operação**
Neste ciclo, a equipe fechou com um Resultado Geral médio de **{media_geral_tam:.1%}**.{texto_comparacao}
Tivemos um total de {total_pessoas} operadores avaliados, distribuídos da seguinte forma:
* 💎 Excelência (>= 90%): {qtd_verde} operadores ({qtd_verde/total_pessoas:.0%})
* 🟢 Meta Batida (80% - 89%): {qtd_amarelo} operadores ({qtd_amarelo/total_pessoas:.0%})
* 🔴 Atenção Prioritária (< 80%): {qtd_vermelho} operadores ({qtd_vermelho/total_pessoas:.0%})

**2. Qualidade e Produtividade**
* **Média de CSAT:** {media_csat:.1%}
* **Média de Aderência:** {media_ad:.1%}
* **Média de Conformidade:** {media_conf:.1%}

**3. Análise de Destaques e Oportunidades**
* 🏆 **Destaque do Mês:** O operador **{nome_top}** entregou o melhor resultado da equipe, atingindo impressionantes **{nota_top:.1%}** de performance global. 
* 🎯 **Atenção Individual:** Por outro lado, **{nome_pior}** obteve o menor resultado do ciclo (**{nota_pior:.1%}**) e precisará de acompanhamento intensivo (PDI) nas próximas semanas.
"""
                if melhor_kpi is not None and pior_kpi is not None:
                    texto_resumo += f"""* 📈 **Ponto Forte da Equipe:** O indicador com melhor desempenho coletivo foi **{formatar_nome_visual(melhor_kpi['Indicador'])}** (Média: {melhor_kpi['% Atingimento']:.1%}).
* ⚠️ **Gargalo Coletivo:** O ofensor que mais penalizou a operação de forma geral foi **{formatar_nome_visual(pior_kpi['Indicador'])}** (Média: {pior_kpi['% Atingimento']:.1%}). O operador **{nome_ofensor_kpi}** foi o mais impactado individualmente neste indicador ({nota_ofensor_kpi:.1%}).
"""
                nome_pior_formatado = nome_pior.split(" ")[0] if nome_pior != "Indisponível" else "foco"
                nome_top_formatado = nome_top.split(" ")[0] if nome_top != "Indisponível" else "foco"
                pior_kpi_str = formatar_nome_visual(pior_kpi['Indicador']) if pior_kpi is not None else "gargalos"

                texto_resumo += f"""
**4. Próximos Passos (Plano de Ação Sugerido)**
O foco da liderança para o próximo ciclo será atuar diretamente na base crítica de operadores, com PDI prioritário focado em {nome_pior_formatado}. Além disso, faremos rodadas de ouvidorias e calibração voltadas para **{pior_kpi_str}** com o intuito de recuperar a média da equipe. Paralelamente, manteremos as ações de reconhecimento público exaltando o alto desempenho entregue por {nome_top_formatado} e demais operadores de excelência para engajar o restante do time."""

                st.markdown("💡 **Dica:** O texto abaixo é gerado automaticamente pela Inteligência do sistema cruzando os dados do mês inteiro da sua equipe com os resultados do mês anterior. Você pode copiá-lo para enviar à coordenação ou usar em reuniões gerenciais.")
                st.code(texto_resumo, language="markdown")
            else:
                st.info("Aguardando upload de dados para calcular o resumo executivo.")
        else:
            st.info("Nenhum dado disponível neste período.")

    # ------------------ RANKING ------------------
    with tabs[2]:
        st.markdown(f"### 🏆 Ranking Geral (Consolidado)")
        if df_dados is not None:
            if tem_tam: 
                df_rank = df_dados[df_dados['Indicador'] == 'TAM'].copy()
                df_rank['Resultado'] = df_rank['% Atingimento']
            else: 
                df_rank = df_dados.groupby('Colaborador').agg({'Diamantes':'sum', 'Max. Diamantes':'sum'}).reset_index()
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
        st.markdown("### ⏳ Evolução Temporal")
        df_hist = carregar_historico_completo()
        if df_hist is not None:
            if df_users_cadastrados is not None: df_hist = filtrar_por_usuarios_cadastrados(df_hist, df_users_cadastrados)
            df_hist['Colaborador'] = df_hist['Colaborador'].str.title()
            lista_colabs = sorted(df_hist['Colaborador'].unique())
            if lista_colabs:
                colab_sel = st.selectbox("Selecione o Colaborador:", lista_colabs)
                df_hist_user = df_hist[df_hist['Colaborador'] == colab_sel].copy()
                if not df_hist_user.empty:
                    df_hist_user['Indicador'] = df_hist_user['Indicador'].apply(formatar_nome_visual)
                    fig_heat = px.density_heatmap(df_hist_user, x="Periodo", y="Indicador", z="% Atingimento", text_auto=False, title=f"Mapa de Calor: {colab_sel}", color_continuous_scale="RdYlGn", range_color=[0.6, 1.0])
                    fig_heat.update_traces(texttemplate="%{z:.1%}", textfont={"size":12})
                    st.plotly_chart(fig_heat, use_container_width=True)
                else: st.warning("Sem dados.")
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
                    st.plotly_chart(fig_rank, use_container_width=True)

    # ------------------ COMISSÕES ------------------
    with tabs[5]:
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
    with tabs[6]: 
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
    with tabs[7]:
        st.markdown("### 🏖️ Férias da Equipe")
        if df_users_cadastrados is not None:
            df_f = df_users_cadastrados[['nome', 'ferias']].copy()
            df_f['nome'] = df_f['nome'].str.title()
            st.dataframe(df_f, use_container_width=True)

    # ------------------ ADMIN ------------------
    with tabs[8]:
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
                        salvar_arquivos_padronizados(up_k)
                        salvar_config(nova_data)
                        df_debug, log = carregar_dados_completo_debug() 
                        if df_debug is not None:
                            atualizar_historico(df_debug, nova_data)
                            st.success("✅ Atualizado com Sucesso!")
                            time.sleep(1)
                            st.rerun()
                        else: st.error("Erro ao processar arquivos.")
                    except Exception as e: st.error(f"Erro salvamento: {e}")
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
            if st.button("🔥 Limpar TUDO (Reset Completo)", type="primary"):
                limpar_base_dados_completa()
                st.success("Limpo!")
                time.sleep(1)
                st.rerun()
        with st3:
            st.markdown("#### 💾 Backup de Segurança")
            if os.path.exists('historico_consolidado.csv'):
                with open('historico_consolidado.csv', 'rb') as f: st.download_button("⬇️ Baixar Backup Consolidado", f, "historico_consolidado_backup.csv", "text/csv")
            else: st.warning("Sem histórico para backup.")
            if os.path.exists('feedbacks_gb.csv'):
                with open('feedbacks_gb.csv', 'rb') as f: st.download_button("⬇️ Baixar Banco de Feedbacks", f, "feedbacks_gb_backup.csv", "text/csv")
        with st4:
            if st.button("Rodar Diagnóstico"):
                _, log_df = carregar_dados_completo_debug()
                st.dataframe(log_df)

    # ------------------ BANCO DE HORAS ------------------
    with tabs[9]:
        st.markdown("### ⏰ Análise de Folha de Ponto")
        st.info("Faça o upload do arquivo .xlsx ou .csv.")
        uploaded_ponto = st.file_uploader("Carregar Planilha de Ponto", type=['xlsx', 'csv'])
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
                    else: st.warning("⚠️ Filtro de ativos não aplicado. Carregue o usuarios.csv no Admin.")

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
                else: st.error("Colunas não identificadas.")
            except Exception as e: st.error(f"Erro: {e}")

    # ------------------ FEEDBACKS GB ------------------
    with tabs[10]:
        st.markdown("### 📝 Controle de Feedbacks (GB)")
        st.info("💡 **Objetivo:** Registrar feedback orientado a valor.")
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
                    
                    piores_kpis = df_user_fb[(df_user_fb['Indicador'] != 'TAM') & (df_user_fb['% Atingimento'] < 0.85)]
                    if not piores_kpis.empty:
                        st.markdown("##### 💡 Sugestões de Abordagem (Smart Coach)")
                        for _, row in piores_kpis.iterrows():
                            st.markdown(f"⚠️ **{formatar_nome_visual(row['Indicador'])} ({row['% Atingimento']:.1%}):** {DICAS_KPI.get(row['Indicador'], 'Atenção aos processos.')}")
                    
                    with st.form("form_registro_fb"):
                        motivo_txt = st.text_area("1. Motivo(s):")
                        fb_valor_txt = st.text_area("2. Feedback:")
                        acao_txt = st.text_area("3. Plano de Ação:")
                        if st.form_submit_button("💾 Salvar Registro e Gerar E-mail"):
                            if not motivo_txt or not fb_valor_txt or not acao_txt: st.error("⚠️ Preencha todos os campos.")
                            else:
                                salvar_feedback_gb({"Data_Registro": datetime.now().strftime("%d/%m/%Y %H:%M"), "Periodo_Ref": periodo_label, "Colaborador": colab_fb, "Faixa": faixa_sel.split(" ")[0], "TAM": f"{tam_v:.1%}", "Motivo": motivo_txt, "Acao_GB": acao_txt, "Feedback_Valor": fb_valor_txt})
                                st.success("✅ Feedback registrado!")
                                
                                lista_kpis_email = "\n".join([f"* **{formatar_nome_visual(row['Indicador'])}:** {row['% Atingimento']:.1%}" for _, row in df_user_fb.iterrows()])
                                if tam_v < 0.70: ab = f"O seu Resultado Geral (TAM) fechou em **{tam_v:.1%}**, abaixo da meta. Vamos focar na recuperação!"
                                elif tam_v < 0.80: ab = f"O seu Resultado Geral (TAM) fechou em **{tam_v:.1%}**. Estamos quase lá! Vamos alinhar os ponteiros."
                                elif tam_v < 0.90: ab = f"Parabéns! O seu Resultado Geral (TAM) fechou em **{tam_v:.1%}**, batendo a nossa meta."
                                else: ab = f"Uau! O seu Resultado Geral (TAM) fechou em **{tam_v:.1%}**, resultado de extrema Excelência!"
                                
                                email_template = f"**Assunto:** Feedback Mensal - Resultado Operacional - {periodo_label}\n\nOlá, **{colab_fb}**. Tudo bem?\n\nGostaria de repassar os pontos referentes ao seu desempenho de **{periodo_label}**.\n{ab}\n\nAqui está o detalhamento dos seus indicadores:\n{lista_kpis_email}\n\n**Pontos Mapeados:**\n{motivo_txt}\n\n**Nosso Plano de Ação:**\n{acao_txt}\n\n**Feedback Estratégico:**\n{fb_valor_txt}\n\nConto com seu engajamento para o próximo ciclo!\n\nAtenciosamente,\nSua Liderança."
                                
                                st.markdown("### 📧 E-mail Gerado (Copie e cole):")
                                st.code(email_template, language='markdown')

            else: st.success(f"Nenhum colaborador encontrado na faixa.")
        
        st.markdown("---")
        st.markdown("### 📚 Base Geral de Feedbacks Aplicados")
        df_fbs_hist = carregar_feedbacks_gb()
        if df_fbs_hist is not None and not df_fbs_hist.empty: st.dataframe(df_fbs_hist.iloc[::-1], use_container_width=True, hide_index=True)
        else: st.info("Nenhum feedback registrado no sistema até o momento.")

# ==========================================
# --- 7. VISÃO DO OPERADOR ---
# ==========================================
else:
    st.markdown(f"## 🚀 Olá, **{nome_logado.split()[0]}**!")
    st.markdown(f"<div style='display: flex; align-items: center; margin-bottom: 20px; color: #666;'><span style='margin-right: 15px;'>📅 Referência: <b>{periodo_label}</b></span><span class='update-badge'>🕒 Atualizado em: {obter_data_atualizacao()}</span></div>", unsafe_allow_html=True)
    
    minhas_ferias = "Não informado"
    if df_users_cadastrados is not None:
        try:
            user_info = df_users_cadastrados[df_users_cadastrados['nome'] == nome_logado.upper()]
            if not user_info.empty: minhas_ferias = user_info.iloc[0]['ferias']
        except: pass

    tab_results, tab_ferias, tab_feedbacks = st.tabs(["📊 Meus Resultados", "🏖️ Minhas Férias", "📝 Meus Feedbacks"])

    with tab_results:
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
            
            pior_row = meus_dados.sort_values(by='% Atingimento').iloc[0]
            if pior_row['% Atingimento'] < 0.9:
                dica = DICAS_KPI.get(pior_row['Indicador'], "Fale com seu gestor.")
                st.markdown(f"""<div class="insight-box"><div class="insight-title">💡 Smart Coach: {formatar_nome_visual(pior_row['Indicador'])}</div><div class="insight-text">{dica} (Atual: {pior_row['% Atingimento']:.1%})</div></div>""", unsafe_allow_html=True)

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

            df_hist_full = carregar_historico_completo()
            if df_hist_full is not None:
                hist_user = df_hist_full[df_hist_full['Colaborador'].astype(str).str.upper().apply(normalizar_chave) == normalizar_chave(nome_logado)].copy()
                if not hist_user.empty:
                    hist_user['Indicador'] = hist_user['Indicador'].apply(formatar_nome_visual)
                    st.plotly_chart(px.line(hist_user, x='Periodo', y='% Atingimento', color='Indicador', markers=True), use_container_width=True)

    with tab_ferias:
        st.markdown("### 🗓️ Planejamento de Férias")
        st.markdown(f"<div class='vacation-card'><p class='vacation-title'>Suas próximas férias estão programadas para:</p><div class='vacation-date'>{minhas_ferias}</div><p class='vacation-note'>*Sujeito a alteração.</p></div>", unsafe_allow_html=True)

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

st.markdown("---")
st.markdown('<div class="dev-footer">Desenvolvido por Klebson Davi - Supervisor de Suporte Técnico</div>', unsafe_allow_html=True)
