import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import time
from streamlit_calendar import calendar
from supabase import create_client, Client

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="PowerLog PRO", page_icon="💪", layout="centered")

# --- 2. CONEXÃO SUPABASE ---
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

# --- 3. ESTILO CSS ---
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 12px; height: 3.5em; background-color: #007bff; color: white; font-weight: bold; }
    .ex-card { background: white; padding: 20px; border-radius: 20px; box-shadow: 0px 10px 20px rgba(0,0,0,0.05); text-align: center; margin-bottom: 20px; border: 1px solid #e1e1e1; }
    .big-emoji { font-size: 50px; display: block; }
    .ex-title { font-size: 24px; font-weight: 800; color: #1e1e1e; }
    .time-display { font-size: 28px; font-weight: bold; color: #ff4b4b; background: #fff5f5; padding: 15px; border-radius: 15px; text-align: center; border: 2px solid #ffcccc; margin-bottom: 20px; }
    .metric-box { background: #f0f2f6; padding: 10px; border-radius: 10px; text-align: center; font-weight: bold; min-height: 80px; font-size: 14px; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. LÓGICA DE LOGIN ---
if 'user' not in st.session_state:
    st.session_state.user = None

def pagina_login():
    st.title("⚡ PowerLog PRO - Login")
    aba = st.tabs(["Entrar", "Criar Conta"])
    with aba[0]:
        email = st.text_input("E-mail", key="login_email")
        senha = st.text_input("Senha", type="password", key="login_senha")
        if st.button("Aceder"):
            try:
                res = supabase.auth.sign_in_with_password({"email": email, "password": senha})
                st.session_state.user = res.user
                st.rerun()
            except:
                st.error("E-mail ou senha inválidos.")
    with aba[1]:
        novo_email = st.text_input("E-mail", key="reg_email")
        nova_senha = st.text_input("Senha (mín. 6 caracteres)", type="password", key="reg_senha")
        if st.button("Cadastrar"):
            try:
                supabase.auth.sign_up({"email": novo_email, "password": nova_senha})
                st.success("Conta criada! Verifique seu e-mail.")
            except Exception as e:
                st.error(f"Erro: {e}")

if st.session_state.user is None:
    pagina_login()
    st.stop()

# --- 5. FUNÇÕES DE DADOS ---
user_id = st.session_state.user.id
if 'hora_inicio' not in st.session_state: st.session_state.hora_inicio = None

def buscar_catalogo():
    res = supabase.table("catalogo_exercicios").select("*").order("nome").execute()
    return pd.DataFrame(res.data)

def buscar_meus_treinos():
    res = supabase.table("exercicios").select("*").eq("user_id", user_id).execute()
    return pd.DataFrame(res.data)

def buscar_sessoes():
    res = supabase.table("sessoes").select("*").eq("user_id", user_id).order("id", desc=True).execute()
    return pd.DataFrame(res.data)

def buscar_logs():
    res = supabase.table("logs").select("*").eq("user_id", user_id).execute()
    return pd.DataFrame(res.data)

# --- 6. INTERFACE PRINCIPAL ---
st.sidebar.write(f"👤 {st.session_state.user.email}")
if st.sidebar.button("Sair"):
    supabase.auth.sign_out()
    st.session_state.user = None
    st.rerun()

menu = st.sidebar.selectbox("Navegação", ["🏋️ Treinar Agora", "📊 Histórico", "🆕 Configurar Meus Treinos"])

# --- MENU: CONFIGURAR ---
if menu == "🆕 Configurar Meus Treinos":
    st.subheader("➕ Adicionar ao Plano")
    df_cat = buscar_catalogo()
    with st.form("novo_exercicio"):
        nome_treino = st.text_input("Nome do Treino (Ex: PERNAS, SUPERIOR)").upper().strip()
        novo_ex_manual = st.checkbox("Exercício não está na lista?")
        
        if novo_ex_manual:
            ex_nome = st.text_input("Nome do exercício:")
            ex_emoji = "💪"
        else:
            ex_nome = st.selectbox("Escolha:", df_cat['nome'].tolist() if not df_cat.empty else [])
            ex_emoji = df_cat[df_cat['nome'] == ex_nome].iloc[0]['emoji'] if not df_cat.empty else "💪"

        if st.form_submit_button("Adicionar"):
            if nome_treino and ex_nome:
                supabase.table("exercicios").insert({
                    "user_id": user_id, "treino": nome_treino, "nome": ex_nome, "emoji": ex_emoji
                }).execute()
                st.rerun()

    st.divider()
    meus_ex = buscar_meus_treinos()
    if not meus_ex.empty:
        for i, row in meus_ex.sort_values('treino').iterrows():
            c1, c2, c3 = st.columns([2, 3, 1])
            c1.write(f"**{row['treino']}**")
            c2.write(f"{row['emoji']} {row['nome']}")
            if c3.button("🗑️", key=f"del_{row['id']}"):
                supabase.table("exercicios").delete().eq("id", row['id']).execute()
                st.rerun()

# --- MENU: TREINAR ---
# --- MENU: TREINAR AGORA ---
elif menu == "🏋️ Treinar Agora":
    meus_ex = buscar_meus_treinos()
    df_cat = buscar_catalogo() # Puxamos o catálogo para pegar os GIFs
    
    if meus_ex.empty:
        st.warning("Adicione exercícios no menu Configurar.")
    else:
        treino_sel = st.radio("Treino:", sorted(meus_ex['treino'].unique()), horizontal=True)
        
        # ... (Mantém sua lógica de timer aqui) ...

        st.divider()
        ex_f = meus_ex[meus_ex['treino'] == treino_sel]
        escolhido = st.selectbox("Exercício:", ex_f['nome'])
        
        # AJUSTE DO GIF: Busca o link no catálogo usando o nome do exercício
        link_gif = ""
        if not df_cat.empty:
            match = df_cat[df_cat['nome'] == escolhido]
            if not match.empty:
                link_gif = match.iloc[0].get('gif_url', "")

        # Card do Exercício
        st.markdown(f"<div class='ex-card'><div class='ex-title'>{escolhido}</div></div>", unsafe_allow_html=True)

        # EXIBIÇÃO DO GIF CORRIGIDA
        if link_gif and str(link_gif).strip() != "None":
            col_espaco1, col_gif, col_espaco2 = st.columns([1, 2, 1])
            with col_gif:
                st.image(link_gif, width=300) # Define um tamanho fixo em pixels (ex: 300)
            
        else:
            st.info("💡 Mantenha a postura correta.")

        # Interface de Input
        col_s, col_p, col_r = st.columns([1, 1, 1])
        n_serie_atual = col_s.number_input("Série nº", 1, 10, 1)
        p = col_p.number_input("Peso (kg)", 0.0, 500.0, step=0.5)
        r = col_r.number_input("Reps", 0, 100, 10)
        
        if st.button("✅ Salvar Série"):
            hoje = datetime.now().strftime("%d/%m/%Y %H:%M")
            supabase.table("logs").insert({
                "user_id": user_id, 
                "data": hoje, 
                "exercicio": escolhido, 
                "peso": p, 
                "reps": r, 
                "serie_num": n_serie_atual
            }).execute()
            st.success(f"Série {n_serie_atual} salva!")

# --- MENU: HISTÓRICO ---
elif menu == "📊 Histórico":
    df_l = buscar_logs()
    df_s = buscar_sessoes()
    
    if not df_s.empty:
        df_s['data_dt'] = pd.to_datetime(df_s['data'], errors='coerce')
        # Lógica de métricas resumida para performance
        c1, c2, c3 = st.columns(3)
        c1.markdown(f"<div class='metric-box'>MÊS<br>{df_s[df_s['data_dt'] > (datetime.now() - timedelta(days=30))]['data'].nunique()} treinos</div>", unsafe_allow_html=True)
        c2.markdown(f"<div class='metric-box'>TOTAL<br>{len(df_s)} sessões</div>", unsafe_allow_html=True)
        c3.markdown(f"<div class='metric-box'>LOGS<br>{len(df_l)} séries</div>", unsafe_allow_html=True)

    t1, t2, t3 = st.tabs(["🗓️ Calendário", "📈 Evolução", "📋 Logs"])
    with t1:
        eventos = [{"title": f"💪 {r['treino_tipo']}", "start": r['data']} for _, r in df_s.iterrows()]
        calendar(events=eventos, options={"locale": "pt-br"})
    with t2:
        if not df_l.empty:
            df_l['data_dt'] = pd.to_datetime(df_l['data'], dayfirst=True, errors='coerce')
            ex_sel = st.selectbox("Exercício:", sorted(df_l['exercicio'].unique()))
            df_ev = df_l[df_l['exercicio'] == ex_sel].dropna(subset=['data_dt']).sort_values('data_dt')
            st.line_chart(df_ev.set_index('data_dt')['peso'])
    with t3:
        if not df_l.empty:
            for _, row in df_l.sort_values('id', ascending=False).head(15).iterrows():
                cc1, cc2, cc3 = st.columns([3, 1, 1])
                cc1.write(f"{row['data']} - {row['exercicio']}")
                cc2.write(f"{row['peso']}kg")
                if cc3.button("🗑️", key=f"log_{row['id']}"):
                    supabase.table("logs").delete().eq("id", row['id']).execute()
                    st.rerun()
