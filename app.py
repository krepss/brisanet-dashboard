import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import json
import time
from datetime import datetime

# --- 1. CONFIGURAÇÃO ---
st.set_page_config(page_title="Brisanet Analytics", layout="wide", page_icon="📶")

# --- 2. CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Roboto', sans-serif; }
    .stApp { background-color: #f4f7f6; }
    div.stMetric {
        background-color: white; border: 1px solid #e0e0e0; padding: 15px 20px;
        border-radius: 12px; border-left: 5px solid #F37021;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05); transition: transform 0.2s;
    }
    div.stMetric:hover { transform: translateY(-5px); box-shadow: 0 8px 15px rgba(0,0,0,0.1); }
    div.stButton > button {
        background: linear-gradient(90deg, #F37021 0%, #d35400 100%); color: white; border: none;
        padding: 0.5rem 1rem; border-radius: 8px; font-weight: bold; transition: 0.3s;
    }
    div.stButton > button:hover { transform: scale(1.02); box-shadow: 0 4px 12px rgba(243, 112, 33, 0.4); }
    h1, h2, h3 { color: #003366 !important; }
    .login-container {
        background: white; padding: 40px; border-radius: 15px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.08); text-align: center; border-top: 6px solid #003366;
    }
    .date-box {
        background-color: #e3f2fd; color: #003366; padding: 10px; 
        border-radius: 8px; text-align: center; font-size: 0.9em; font-weight: bold;
        margin-bottom: 20px; border: 1px solid #bbdefb;
    }
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

def limpar_base_dados():
    arquivos = [f for f in os.listdir('.') if f.endswith('.csv')]
    for f in arquivos:
        os.remove(f)

# --- HISTÓRICO ---
def atualizar_historico(df_atual, periodo):
    ARQUIVO_HIST = 'historico_consolidado.csv'
    df_save = df_atual.copy()
    df_save['Periodo'] = periodo
    
    # Garante padronização antes de salvar
    df_save['Colaborador'] = df_save['Colaborador'].astype(str).str.strip().str.upper()
    
    if os.path.exists(ARQUIVO_HIST):
        try:
            df_hist = pd.read_csv(ARQUIVO_HIST)
            # Remove dados antigos deste mesmo período
            df_hist = df_hist[df_hist['Periodo'] != periodo]
            df_final = pd.concat([df_hist, df_save], ignore_index=True)
        except: df_final = df_save
    else: df_final = df_save
    
    df_final.to_csv(ARQUIVO_HIST, index=False)
    return True

def carregar_historico_completo():
    if os.path.exists('historico_consolidado.csv'):
        try: 
            df = pd.read_csv('historico_consolidado.csv')
            # Padroniza leitura
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
    
    # 1. Identificar coluna de NOME
    col_agente = None
    possiveis_nomes = ['colaborador', 'agente', 'nome', 'employee', 'funcionario', 'operador']
    for c in df.columns:
        if any(p == c or p in c for p in possiveis_nomes):
            col_agente = c
            break
            
    if not col_agente: return None, "Coluna de Nome não encontrada"
    
    df.rename(columns={col_agente: 'Colaborador'}, inplace=True)
    
    # --- PADRONIZAÇÃO DE NOME FORÇADA ---
    # Converte tudo para maiúsculo e remove espaços para evitar duplicatas (João vs JOAO)
    df['Colaborador'] = df['Colaborador'].astype(str).str.strip().str.upper()

    # 2. Lógica Especial: Arquivo Combinado (Aderência & Conformidade)
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
        
        return pd.concat(lista_retorno), "Arquivo Combinado Detectado"

    # 3. Lógica Padrão (Arquivo Único)
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
            
    if col_valor: 
        df.rename(columns={col_valor: '% Atingimento'}, inplace=True)
    else: 
        return None, f"Coluna de Valor não encontrada ({possiveis_valores})"

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
        
        # --- AGREGADOR DE DUPLICATAS (SOMA E MÉDIA) ---
        # Se um colaborador aparecer 2x no mesmo indicador, tira a média da nota e soma os diamantes
        agg_rules = {'% Atingimento': 'mean'}
        if 'Diamantes' in df_concat.columns: agg_rules['Diamantes'] = 'sum'
        if 'Max. Diamantes' in df_concat.columns: agg_rules['Max. Diamantes'] = 'sum' # Assume que se apareceu 2x, o potencial dobrou
        
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
                # Padroniza nome dos usuários também para bater o match
                df['nome'] = df['nome'].astype(str).str.strip().str.upper()
                return df
    return None

def filtrar_por_usuarios_cadastrados(df_dados, df_users):
    if df_dados is None or df_dados.empty: return df_dados
    if df_users is None or df_users.empty: return df_dados
    
    lista_vip = df_users['nome'].unique() # Já está upper
    # df_dados['Colaborador'] já está upper e tratado
    
    df_filtrado = df_dados[df_dados['Colaborador'].isin(lista_vip)].copy()
    return df_filtrado

# --- CLASSIFICAÇÃO ---
def classificar_farol(val):
    if val >= 0.90: return '💎 Excelência' # >= 90%
    elif val >= 0.80: return '🟢 Meta Batida' # 80% a 90%
    else: return '🔴 Crítico' # < 80%

# --- 4. LOGIN ---
if 'logado' not in st.session_state:
    st.session_state.update({'logado': False, 'usuario_nome': '', 'perfil': ''})

if not st.session_state['logado']:
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown(f"""
        <div class="login-container">
            <h1 style="color: #F37021; font-size: 3em; margin: 0;">📶</h1>
            <h3 style="color: #003366; margin: 10px 0;">Portal de Resultados</h3>
            <p style="color: #777; font-size: 0.9em;">Acompanhamento de Performance Individual</p>
        </div>
        """, unsafe_allow_html=True)
        with st.form("form_login"):
            email = st.text_input("Email Corporativo").strip().lower()
            senha = st.text_input("Senha (Apenas Gestores)", type="password")
            if st.form_submit_button("ENTRAR", use_container_width=True):
                if email in ['gestor', 'admin'] and senha == 'admin':
                    st.session_state.update({'logado': True, 'usuario_nome': 'Gestor', 'perfil': 'admin'})
                    st.rerun()
                else:
                    df_users = carregar_usuarios()
                    if df_users is not None:
                        user = df_users[df_users['email'] == email]
                        if not user.empty:
                            # Guarda o nome em Title Case para ficar bonito
                            nome_upper = user.iloc[0]['nome']
                            st.session_state.update({'logado': True, 'usuario_nome': nome_upper, 'perfil': 'user'})
                            st.rerun()
                        else: st.error("Email não encontrado.")
                    else: st.error("⚠️ Sistema em manutenção.")
    st.stop()

# --- 5. DASHBOARD ---
lista_periodos = listar_periodos_disponiveis()
opcoes_periodo = lista_periodos if lista_periodos else ["Nenhum histórico disponível"]

with st.sidebar:
    st.title("📶 BRISANET")
    st.caption("Performance Analytics")
    periodo_selecionado = st.selectbox("📅 Visualizar Mês:", opcoes_periodo)
    
    if periodo_selecionado == "Nenhum histórico disponível":
        df_raw = None
        periodo_label = "Aguardando Upload"
        st.warning("⚠️ Histórico vazio ou não encontrado.")
    else:
        df_hist_full = carregar_historico_completo()
        if df_hist_full is not None:
            df_raw = df_hist_full[df_hist_full['Periodo'] == periodo_selecionado].copy()
        else: df_raw = None
        periodo_label = periodo_selecionado
    
    df_users_cadastrados = carregar_usuarios()
    df_dados = filtrar_por_usuarios_cadastrados(df_raw, df_users_cadastrados)
    
    # Converte nomes para Title Case na visualização final
    if df_dados is not None and not df_dados.empty:
        df_dados['Colaborador'] = df_dados['Colaborador'].str.title()

    st.markdown(f"""<div class="date-box">Ref. Exibida:<br>{periodo_label}</div>""", unsafe_allow_html=True)
    st.markdown("---")
    
    # Exibe nome do usuário logado bonito
    nome_logado = st.session_state['usuario_nome'].title() if st.session_state['usuario_nome'] != 'Gestor' else 'Gestor'
    
    st.markdown(f"### 👤 {nome_logado.split()[0]}")
    if st.button("Sair / Logout"):
        st.session_state.update({'logado': False})
        st.rerun()

perfil = st.session_state['perfil']

if df_dados is None and perfil == 'user':
    st.info("👋 Olá! Os dados deste mês ainda não estão disponíveis. O gestor precisa fazer o upload.")
    st.stop()

# --- GESTOR ---
if perfil == 'admin':
    st.title(f"📊 Visão Gerencial")
    tabs = st.tabs(["🚦 Painel de Semáforo", "⏳ Evolução (Heatmap)", "🔍 Detalhe por Indicador", "📋 Tabela Geral", "⚙️ Admin / Upload"])
    
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
            st.subheader("📋 Prioridade de Ação")
            df_atencao = df_media_pessoas[df_media_pessoas['% Atingimento'] < 0.80].sort_values(by='% Atingimento')
            
            if not df_atencao.empty:
                lista_detalhada = []
                for colab in df_atencao['Colaborador']:
                    dados_pessoa = df_dados[df_dados['Colaborador'] == colab]
                    media_pessoa = dados_pessoa['% Atingimento'].mean()
                    pior_kpi_row = dados_pessoa.loc[dados_pessoa['% Atingimento'].idxmin()]
                    nome_kpi_bonito = formatar_nome_visual(pior_kpi_row['Indicador'])
                    lista_detalhada.append({
                        'Colaborador': colab,
                        'Média Geral': media_pessoa,
                        'Status': '🔴 Crítico',
                        'Pior Indicador': f"{nome_kpi_bonito} ({pior_kpi_row['% Atingimento']:.1%})"
                    })
                df_final_atencao = pd.DataFrame(lista_detalhada)
                try: st.dataframe(df_final_atencao.style.format({'Média Geral': '{:.1%}'}), use_container_width=True, height=500)
                except: st.dataframe(df_final_atencao, use_container_width=True, height=500)
            else: st.success("🎉 Ninguém na zona crítica (<80%) neste período.")

    with tabs[1]:
        st.markdown("### ⏳ Evolução Temporal")
        df_hist = carregar_historico_completo()
        df_hist = filtrar_por_usuarios_cadastrados(df_hist, df_users_cadastrados)
        
        if df_hist is not None and not df_hist.empty:
            df_hist['Colaborador'] = df_hist['Colaborador'].str.title() # Visual Bonito
            colab_sel = st.selectbox("Selecione o Colaborador:", sorted(df_hist['Colaborador'].unique()))
            df_hist_user = df_hist[df_hist['Colaborador'] == colab_sel].copy()
            if not df_hist_user.empty:
                df_hist_user['Indicador'] = df_hist_user['Indicador'].apply(formatar_nome_visual)
                df_hist_user['Texto'] = df_hist_user['% Atingimento'].apply(lambda x: f"{x:.1%}")
                fig_heat = px.density_heatmap(df_hist_user, x="Periodo", y="Indicador", z="% Atingimento", 
                                              text_auto=False, title=f"Mapa de Calor: {colab_sel}",
                                              color_continuous_scale="RdYlGn", range_color=[0.6, 1.0])
                fig_heat.update_traces(texttemplate="%{z:.1%}", textfont={"size":12})
                st.plotly_chart(fig_heat, use_container_width=True)
            else: st.warning("Sem histórico para este colaborador.")
        else: st.info("O histórico está vazio.")

    with tabs[2]:
        if df_dados is not None and not df_dados.empty:
            st.markdown("### 🔬 Detalhe por Indicador")
            df_visual = df_dados.copy()
            df_visual['Indicador'] = df_visual['Indicador'].apply(formatar_nome_visual)
            df_visual['Status'] = df_visual['% Atingimento'].apply(classificar_farol)
            
            df_agrupado = df_visual.groupby(['Indicador', 'Status']).size().reset_index(name='Quantidade')
            fig_farol = px.bar(df_agrupado, x='Indicador', y='Quantidade', color='Status', 
                               text='Quantidade', title="Farol de Performance",
                               color_discrete_map={'💎 Excelência': '#3498db', '🟢 Meta Batida': '#2ecc71', '🔴 Crítico': '#e74c3c'})
            st.plotly_chart(fig_farol, use_container_width=True)
            
            lista_kpis = sorted(df_visual['Indicador'].unique())
            for kpi in lista_kpis:
                with st.expander(f"📊 Ranking: {kpi}", expanded=False):
                    df_kpi = df_visual[df_visual['Indicador'] == kpi].sort_values(by='% Atingimento', ascending=True)
                    fig_rank = px.bar(df_kpi, x='% Atingimento', y='Colaborador', orientation='h',
                                      text_auto='.1%', title=f"Ranking - {kpi}",
                                      color='% Atingimento', color_continuous_scale=['#e74c3c', '#f1c40f', '#2ecc71'])
                    fig_rank.add_vline(x=0.8, line_dash="dash", line_color="black", annotation_text="Meta 80%")
                    st.plotly_chart(fig_rank, use_container_width=True)

    with tabs[3]: 
        if df_dados is not None and not df_dados.empty:
            c1, c2 = st.columns([3, 1])
            with c1: st.markdown(f"### Mapa de Resultados: {periodo_label}")
            with c2: filtro = st.multiselect("🔍 Filtrar:", df_dados['Colaborador'].unique())
            df_show = df_dados if not filtro else df_dados[df_dados['Colaborador'].isin(filtro)]
            df_show_visual = df_show.copy()
            df_show_visual['Indicador'] = df_show_visual['Indicador'].apply(formatar_nome_visual)
            pivot = df_show_visual.pivot_table(index='Colaborador', columns='Indicador', values='% Atingimento')
            try: st.dataframe(pivot.style.background_gradient(cmap='RdYlGn', vmin=0.7, vmax=1.0).format("{:.1%}"), use_container_width=True, height=600)
            except: st.dataframe(pivot.style.format("{:.1%}"), use_container_width=True, height=600)

    with tabs[4]:
        st.markdown("### 📂 Gestão de Arquivos")
        data_sugestao = obter_data_hoje()
        st.markdown("#### 1. Configurar Período")
        nova_data = st.text_input("Mês/Ano de Referência:", value=data_sugestao)
        
        st.markdown("#### 2. Atualizar Arquivos (Upload Inteligente)")
        c1, c2 = st.columns(2)
        with c1:
            up_u = st.file_uploader("usuarios.csv", key="u")
            if up_u: 
                try:
                    with open("usuarios.csv", "wb") as w: w.write(up_u.getbuffer())
                    st.success("Usuarios OK!")
                except Exception as e: st.error(f"Erro ao salvar usuarios.csv: {e}")
        with c2:
            up_k = st.file_uploader("Indicadores (CSVs)", accept_multiple_files=True, key="k")
            
            # DIAGNÓSTICO
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
                    try:
                        salvos = salvar_arquivos_padronizados(up_k)
                        salvar_config(nova_data)
                        df_novo_ciclo = carregar_dados_completo()
                        df_users_fresh = carregar_usuarios()
                        df_filtrado = filtrar_por_usuarios_cadastrados(df_novo_ciclo, df_users_fresh)
                        if df_filtrado.empty and not df_novo_ciclo.empty:
                            st.error("⚠️ NENHUM dado foi salvo! O filtro de usuários removeu todos os nomes. Verifique o 'usuarios.csv'.")
                        else:
                            atualizar_historico(df_filtrado, nova_data)
                            st.cache_data.clear()
                            st.balloons()
                            st.success(f"✅ Sucesso! Dados salvos em **{nova_data}**.")
                            time.sleep(1)
                            st.rerun()
                    except Exception as e: st.error(f"Erro salvamento: {e}")
        
        st.markdown("---")
        st.markdown("### 3. Restaurar/Baixar")
        if os.path.exists('historico_consolidado.csv'):
            with open('historico_consolidado.csv', 'rb') as f:
                st.download_button("⬇️ Baixar Histórico Consolidado", f, "historico_consolidado.csv", "text/csv")
        
        if st.button("🗑️ Resetar Tudo"):
            limpar_base_dados()
            if os.path.exists('historico_consolidado.csv'): os.remove('historico_consolidado.csv')
            st.cache_data.clear()
            st.warning("Tudo limpo!")
            time.sleep(2)
            st.rerun()

# --- COLABORADOR ---
else:
    # Ajusta o nome para Title Case na exibição
    nome_visual_user = nome_logado
    st.markdown(f"## 🚀 Olá, **{nome_visual_user.split()[0]}**!")
    st.caption(f"📅 Dados referentes a: **{periodo_label}**")
    
    # O df_dados já foi convertido para Title Case no bloco do Dashboard
    # Mas precisamos garantir o match com o nome logado (que também está Title Case)
    meus_dados = df_dados[df_dados['Colaborador'] == nome_visual_user].copy()
    
    if not meus_dados.empty:
        if 'Diamantes' in meus_dados.columns and 'Max. Diamantes' in meus_dados.columns:
            total_dia_bruto = meus_dados['Diamantes'].sum()
            total_max = meus_dados['Max. Diamantes'].sum()
            perc_dia = (total_dia_bruto / total_max) if total_max > 0 else 0
            
            st.markdown("### 💎 Gamificação")
            col_bar, col_num = st.columns([3, 1])
            with col_bar: st.progress(perc_dia)
            with col_num: st.write(f"**{total_dia_bruto} / {total_max}** Diamantes")
            
            df_conf = meus_dados[meus_dados['Indicador'] == 'CONFORMIDADE']
            atingimento_conf = df_conf.iloc[0]['% Atingimento'] if not df_conf.empty else 0.0
            tem_dado_conf = not df_conf.empty
            
            desconto_diamantes = 0
            motivo_desconto = ""
            
            # REGRA FINANCEIRA: GATILHO EM 92%
            GATILHO_FINANCEIRO = 0.92
            
            if tem_dado_conf and atingimento_conf < GATILHO_FINANCEIRO:
                df_pont = meus_dados[meus_dados['Indicador'] == 'PONTUALIDADE']
                if not df_pont.empty:
                    desconto_diamantes = df_pont.iloc[0]['Diamantes']
                    motivo_desconto = f"(Descontados {desconto_diamantes} de Pontualidade)"
            
            total_dia_liquido = total_dia_bruto - desconto_diamantes
            valor_final = total_dia_liquido * 0.50
            
            st.markdown("#### 💰 Extrato Financeiro")
            c1, c2, c3 = st.columns(3)
            c1.metric("Diamantes Válidos", f"{total_dia_liquido}", f"{motivo_desconto}", delta_color="inverse" if desconto_diamantes > 0 else "normal")
            c2.metric("Valor por Diamante", "R$ 0,50")
            
            if not tem_dado_conf:
                c3.metric("Valor a Receber", "Aguardando", "Conformidade Indisponível", delta_color="off")
            elif desconto_diamantes > 0:
                c3.metric("Valor a Receber", f"R$ {valor_final:.2f}", f"Gatilho não atingido (<{GATILHO_FINANCEIRO:.0%})", delta_color="inverse")
                st.error(f"⚠️ **Gatilho Financeiro não atingido**: Sua conformidade foi **{atingimento_conf:.1%}**. Para receber os diamantes de Pontualidade, é necessário ter >= 92% de Conformidade.")
            else:
                c3.metric("Valor a Receber", f"R$ {valor_final:.2f}", "Gatilho Atingido! 🤑")
                if atingimento_conf >= GATILHO_FINANCEIRO:
                    st.success(f"✅ **Gatilho Financeiro Atingido**: Conformidade **{atingimento_conf:.1%}** (>= 92%). Todos os diamantes computados.")
            st.markdown("---")

        cols = st.columns(len(meus_dados))
        for i, row in enumerate(meus_dados.iterrows()):
            r = row[1]
            val = r['% Atingimento']
            nome_visual = formatar_nome_visual(r['Indicador'])
            
            # --- NOVA LÓGICA DE CORES DOS CARDS ---
            delta_msg = "Meta 80%"
            delta_cor = "normal"
            if val >= 0.90: 
                delta_msg = "💎 Excelência!"
            elif val >= 0.80:
                delta_msg = "✅ Meta Batida"
            else:
                delta_cor = "inverse"
                delta_msg = "🔻 Abaixo da Meta"

            with cols[i]:
                st.metric(label=nome_visual, value=f"{val:.1%}", delta=delta_msg, delta_color=delta_cor)
        st.markdown("---")
        
        # Gráficos
        media_equipe = df_dados.groupby('Indicador')['% Atingimento'].mean().reset_index()
        media_equipe.rename(columns={'% Atingimento': 'Média Equipe'}, inplace=True)
        df_comp = pd.merge(meus_dados, media_equipe, on='Indicador')
        df_comp['Indicador'] = df_comp['Indicador'].apply(formatar_nome_visual)
        df_melt = df_comp.melt(id_vars=['Indicador'], value_vars=['% Atingimento', 'Média Equipe'], var_name='Tipo', value_name='Resultado')
        
        fig_comp = px.bar(df_melt, x='Indicador', y='Resultado', color='Tipo', barmode='group',
                          text_auto='.1%', title="Minha Performance vs Média Geral",
                          color_discrete_map={'% Atingimento': '#F37021', 'Média Equipe': '#bdc3c7'})
        fig_comp.add_hline(y=0.8, line_dash="dash", line_color="green", annotation_text="Meta 80%")
        st.plotly_chart(fig_comp, use_container_width=True)
    else: st.error("Usuário sem dados vinculados.")
