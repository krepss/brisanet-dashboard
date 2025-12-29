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
    if os.path.exists(ARQUIVO_HIST):
        try:
            df_hist = pd.read_csv(ARQUIVO_HIST)
            df_hist = df_hist[df_hist['Periodo'] != periodo]
            df_final = pd.concat([df_hist, df_save], ignore_index=True)
        except: df_final = df_save
    else: df_final = df_save
    df_final.to_csv(ARQUIVO_HIST, index=False)
    return True

def carregar_historico_completo():
    if os.path.exists('historico_consolidado.csv'):
        try: return pd.read_csv('historico_consolidado.csv')
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
    return valor

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
    # Padroniza colunas para minúsculo para facilitar a busca
    df.columns = [str(c).strip().lower() for c in df.columns]
    
    # 1. Identificar coluna de NOME (Agente, Colaborador, etc)
    col_agente = None
    possiveis_nomes = ['colaborador', 'agente', 'nome', 'employee', 'funcionario', 'operador']
    for c in df.columns:
        if any(p == c or p in c for p in possiveis_nomes):
            col_agente = c
            break
            
    if not col_agente:
        return None, "Coluna de Nome não encontrada"
    
    df.rename(columns={col_agente: 'Colaborador'}, inplace=True)

    # 2. DETECÇÃO DUPLA (CASO ESPECIAL: ADERÊNCIA E CONFORMIDADE JUNTOS)
    col_ad = None
    col_conf = None
    
    # Procura especificamente por colunas de Aderência e Conformidade no mesmo arquivo
    for c in df.columns:
        if 'ader' in c and ('%' in c or 'perc' in c or 'aderencia' in c or 'aderência' in c):
            col_ad = c
        if 'conform' in c and ('%' in c or 'perc' in c or 'conformidade' in c):
            col_conf = c
            
    # Se achou AMBOS no mesmo arquivo, divide em dois dataframes
    if col_ad and col_conf:
        lista_retorno = []
        
        # Cria DataFrame de Aderência
        df_ad = df[['Colaborador', col_ad]].copy()
        df_ad['% Atingimento'] = df_ad[col_ad].apply(processar_porcentagem_br)
        df_ad['Indicador'] = 'ADERENCIA'
        lista_retorno.append(df_ad[['Colaborador', 'Indicador', '% Atingimento']])
        
        # Cria DataFrame de Conformidade
        df_conf = df[['Colaborador', col_conf]].copy()
        df_conf['% Atingimento'] = df_conf[col_conf].apply(processar_porcentagem_br)
        df_conf['Indicador'] = 'CONFORMIDADE'
        lista_retorno.append(df_conf[['Colaborador', 'Indicador', '% Atingimento']])
        
        return pd.concat(lista_retorno), "Arquivo Combinado Detectado (Aderência + Conformidade)"

    # 3. Lógica PADRÃO (1 Arquivo = 1 Indicador)
    col_valor = None
    nome_kpi_limpo = nome_arquivo.split('.')[0].lower()
    
    possiveis_valores = [
        nome_kpi_limpo, 
        'atingimento', 'resultado', 'nota', 'final', 'pontos', 'valor', 'score'
    ]
    
    # Adiciona variações
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
        return None, f"Coluna de Valor não encontrada. Colunas disponíveis: {list(df.columns)}"

    # Padroniza Diamantes
    for c in df.columns:
        if 'diamantes' in c and 'max' not in c: df.rename(columns={c: 'Diamantes'}, inplace=True)
        if 'max' in c and 'diamantes' in c: df.rename(columns={c: 'Max. Diamantes'}, inplace=True)

    df['% Atingimento'] = df['% Atingimento'].apply(processar_porcentagem_br)
    df['Indicador'] = normalizar_nome_indicador(nome_arquivo)
    
    # Limpa colunas extras
    cols_to_keep = ['Colaborador', 'Indicador', '% Atingimento']
    if 'Diamantes' in df.columns: cols_to_keep.append('Diamantes')
    if 'Max. Diamantes' in df.columns: cols_to_keep.append('Max. Diamantes')
    
    return df[cols_to_keep], "OK - Indicador Único"

def carregar_dados_completo():
    lista_final = []
    arquivos_ignorar = ['usuarios.csv', 'historico_consolidado.csv', 'config.json']
    arquivos = [f for f in os.listdir('.') if f.endswith('.csv') and f.lower() not in arquivos_ignorar]
    
    for arquivo in arquivos:
        try:
            df_bruto = ler_csv_inteligente(arquivo)
            if df_bruto is not None:
                # Aqui o tratamento pode retornar um DF único (padrão) ou um DF empilhado (se for combinado)
                df_tratado, msg = tratar_arquivo_especial(df_bruto, arquivo)
                if df_tratado is not None:
                    lista_final.append(df_tratado)
        except: pass
        
    if lista_final: 
        # Concatena tudo numa lista só
        df_final = pd.concat(lista_final, ignore_index=True)
        
        # Limpeza de duplicatas
        df_final['Key_Colab'] = df_final['Colaborador'].astype(str).str.strip().str.lower()
        df_final['Key_Ind'] = df_final['Indicador'].astype(str).str.strip().str.lower()
        
        # Se tiver diamantes, mantém o que tem diamantes, senão o último
        if 'Diamantes' in df_final.columns:
             df_final = df_final.sort_values(by='Diamantes', na_position='first')
             
        df_final = df_final.drop_duplicates(subset=['Key_Colab', 'Key_Ind'], keep='last')
        df_final = df_final.drop(columns=['Key_Colab', 'Key_Ind'])
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
                df['nome'] = df['nome'].astype(str).str.strip()
                return df
    return None

def filtrar_por_usuarios_cadastrados(df_dados, df_users):
    if df_dados is None or df_dados.empty: return df_dados
    if df_users is None or df_users.empty: return df_dados
    lista_vip = df_users['nome'].astype(str).str.strip().str.lower().unique()
    df_dados['temp_nome'] = df_dados['Colaborador'].astype(str).str.strip().str.lower()
    df_filtrado = df_dados[df_dados['temp_nome'].isin(lista_vip)].copy()
    df_filtrado = df_filtrado.drop(columns=['temp_nome'])
    return df_filtrado

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
                            st.session_state.update({'logado': True, 'usuario_nome': user.iloc[0]['nome'], 'perfil': 'user'})
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
    if df_dados is not None and not df_dados.empty:
        df_dados = df_dados.drop_duplicates(subset=['Colaborador', 'Indicador'], keep='last')

    st.markdown(f"""<div class="date-box">Ref. Exibida:<br>{periodo_label}</div>""", unsafe_allow_html=True)
    st.markdown("---")
    nome = st.session_state['usuario_nome']
    st.markdown(f"### 👤 {nome.split()[0]}")
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
            qtd_verde = len(df_media_pessoas[df_media_pessoas['% Atingimento'] >= 1.0])
            qtd_amarelo = len(df_media_pessoas[(df_media_pessoas['% Atingimento'] >= 0.80) & (df_media_pessoas['% Atingimento'] < 1.0)])
            qtd_vermelho = len(df_media_pessoas[df_media_pessoas['% Atingimento'] < 0.80])
            c1, c2, c3 = st.columns(3)
            c1.metric("🟢 Meta Batida", f"{qtd_verde}", delta=">=100%")
            c2.metric("🟡 Atenção", f"{qtd_amarelo}", delta="80-99%", delta_color="off")
            c3.metric("🔴 Crítico", f"{qtd_vermelho}", delta="<80%", delta_color="inverse")
            st.markdown("---")
            st.subheader("📋 Prioridade de Ação")
            df_atencao = df_media_pessoas[df_media_pessoas['% Atingimento'] < 1.0].sort_values(by='% Atingimento')
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
                        'Status': '🔴 Crítico' if media_pessoa < 0.80 else '🟡 Atenção',
                        'Pior Indicador': f"{nome_kpi_bonito} ({pior_kpi_row['% Atingimento']:.1%})"
                    })
                df_final_atencao = pd.DataFrame(lista_detalhada)
                def colorir_status(val):
                    if 'Crítico' in str(val): return 'color: #e74c3c; font-weight: bold;'
                    if 'Atenção' in str(val): return 'color: #d35400; font-weight: bold;'
                    return ''
                try: st.dataframe(df_final_atencao.style.format({'Média Geral': '{:.1%}'}).map(colorir_status, subset=['Status']), use_container_width=True, height=500)
                except: st.dataframe(df_final_atencao, use_container_width=True, height=500)
            else: st.success("🎉 Todos bateram a meta neste período.")

    with tabs[1]:
        st.markdown("### ⏳ Evolução Temporal")
        df_hist = carregar_historico_completo()
        df_hist = filtrar_por_usuarios_cadastrados(df_hist, df_users_cadastrados)
        if df_hist is not None and not df_hist.empty:
            colab_sel = st.selectbox("Selecione o Colaborador:", sorted(df_hist['Colaborador'].unique()))
            df_hist_user = df_hist[df_hist['Colaborador'] == colab_sel].copy()
            if not df_hist_user.empty:
                df_hist_user['Indicador'] = df_hist_user['Indicador'].apply(formatar_nome_visual)
                df_hist_user['Texto'] = df_hist_user['% Atingimento'].apply(lambda x: f"{x:.1%}")
                fig_heat = px.density_heatmap(df_hist_user, x="Periodo", y="Indicador", z="% Atingimento", 
                                              text_auto=False, title=f"Mapa de Calor: {colab_sel}",
                                              color_continuous_scale="RdYlGn", range_color=[0.7, 1.2])
                fig_heat.update_traces(texttemplate="%{z:.1%}", textfont={"size":12})
                st.plotly_chart(fig_heat, use_container_width=True)
            else: st.warning("Sem histórico para este colaborador.")
        else: st.info("O histórico está vazio.")

    with tabs[2]:
        if df_dados is not None and not df_dados.empty:
            st.markdown("### 🔬 Detalhe por Indicador")
            df_visual = df_dados.copy()
            df_visual['Indicador'] = df_visual['Indicador'].apply(formatar_nome_visual)
            def classificar_farol(val):
                if val >= 1.0: return '🟢 Meta Batida'
                elif val >= 0.80: return '🟡 Atenção'
                else: return '🔴 Crítico'
            df_visual['Status'] = df_visual['% Atingimento'].apply(classificar_farol)
            df_agrupado = df_visual.groupby(['Indicador', 'Status']).size().reset_index(name='Quantidade')
            fig_farol = px.bar(df_agrupado, x='Indicador', y='Quantidade', color='Status', 
                               text='Quantidade', title="Farol de Performance",
                               color_discrete_map={'🟢 Meta Batida': '#2ecc71', '🟡 Atenção': '#f1c40f', '🔴 Crítico': '#e74c3c'})
            st.plotly_chart(fig_farol, use_container_width=True)
            lista_kpis = sorted(df_visual['Indicador'].unique())
            for kpi in lista_kpis:
                with st.expander(f"📊 Ranking: {kpi}", expanded=False):
                    df_kpi = df_visual[df_visual['Indicador'] == kpi].sort_values(by='% Atingimento', ascending=True)
                    fig_rank = px.bar(df_kpi, x='% Atingimento', y='Colaborador', orientation='h',
                                      text_auto='.1%', title=f"Ranking - {kpi}",
                                      color='% Atingimento', color_continuous_scale=['#e74c3c', '#f1c40f', '#2ecc71'])
                    fig_rank.add_vline(x=1.0, line_dash="dash", line_color="black")
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
            try: st.dataframe(pivot.style.background_gradient(cmap='RdYlGn', vmin=0.0, vmax=1.2).format("{:.1%}"), use_container_width=True, height=600)
            except: st.dataframe(pivot.style.format("{:.1%}"), use_container_width=True, height=600)

    with tabs[4]:
        st.markdown("### 📂 Gestão de Arquivos")
        data_sugestao = obter_data_hoje()
        st.markdown("#### 1. Configurar Período")
        nova_data = st.
