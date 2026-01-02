st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;600;800&family=Roboto:wght@300;400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Roboto', sans-serif; }
    
    /* 1. FUNDO GLOBAL */
    .stApp { 
        background: linear-gradient(135deg, #002b55 0%, #004e92 50%, #F37021 100%);
        background-attachment: fixed;
    }
    
    /* 2. TEXTOS GERAIS (Títulos e Parágrafos fora de caixas) -> BRANCO */
    .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6, 
    .stApp p, .stApp li, .stApp div.stMarkdown {
        color: #FFFFFF !important;
    }
    
    /* 3. SIDEBAR (MENU LATERAL) -> TEXTO BRANCO */
    section[data-testid="stSidebar"] {
        background-color: rgba(0, 43, 85, 0.95); /* Fundo escuro */
    }
    /* Força cor branca em todos os elementos de texto da sidebar */
    section[data-testid="stSidebar"] * {
        color: #FFFFFF !important;
    }
    /* Exceção: Texto digitado dentro dos inputs deve ser escuro */
    section[data-testid="stSidebar"] input {
        color: #333333 !important;
    }
    
    /* 4. CARDS DE MÉTRICAS (FUNDO BRANCO -> TEXTO ESCURO) */
    div.stMetric {
        background-color: #FFFFFF !important;
        border: 1px solid #e0e0e0;
        padding: 15px 20px;
        border-radius: 12px;
        border-left: 5px solid #F37021;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    
    /* Rótulo (Label) do Card - ex: "Diamantes Válidos" */
    div.stMetric label, div.stMetric div[data-testid="stMetricLabel"] p {
        color: #555555 !important; 
        font-weight: 600;
    }
    
    /* Valor do Card - ex: "1500" */
    div.stMetric div[data-testid="stMetricValue"] {
        color: #003366 !important;
    }
    
    /* Delta do Card - ex: "Meta Batida" */
    div.stMetric div[data-testid="stMetricDelta"] {
        color: #333333 !important;
    }
    
    /* 5. CARTÃO DE LOGIN */
    [data-testid="stForm"] {
        background-color: rgba(255, 255, 255, 0.95) !important;
        padding: 40px;
        border-radius: 20px;
        box-shadow: 0 15px 35px rgba(0,0,0,0.5);
        border-top: 5px solid #F37021;
    }
    /* Texto dentro do Login -> ESCURO */
    [data-testid="stForm"] h1, [data-testid="stForm"] p {
        color: #003366 !important;
    }
    
    /* 6. ABAS (TABS) */
    /* Texto da aba inativa -> BRANCO */
    button[data-baseweb="tab"] {
        color: rgba(255, 255, 255, 0.7) !important;
    }
    /* Texto da aba ativa -> LARANJA ou BRANCO FORTE */
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #FFFFFF !important;
        background-color: rgba(255, 255, 255, 0.1) !important;
        border-top: 2px solid #F37021 !important;
    }
    
    /* 7. INPUTS E WIDGETS GERAIS */
    .stTextInput label, .stSelectbox label, .stCheckbox label {
        color: #FFFFFF !important; /* Labels dos inputs brancos */
    }
    
    /* 8. DATAFRAME (TABELAS) -> FUNDO BRANCO, TEXTO ESCURO */
    [data-testid="stDataFrame"] {
        background-color: #FFFFFF !important;
        padding: 5px;
        border-radius: 8px;
    }
    [data-testid="stDataFrame"] * {
        color: #333333 !important;
    }

    /* 9. BOTÕES */
    div.stButton > button {
        border-radius: 8px; font-weight: bold; transition: 0.3s;
        background-color: #004e92; color: #FFFFFF !important; border: 1px solid white;
    }
    div.stButton > button:hover {
        background-color: #F37021; border-color: #F37021;
    }
    
    .dev-footer {
        text-align: center; margin-top: 20px; font-size: 0.8em; 
        color: rgba(255,255,255,0.7) !important; font-style: italic;
    }
</style>
""", unsafe_allow_html=True)
