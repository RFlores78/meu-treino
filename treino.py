import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import time
from streamlit_calendar import calendar
from supabase import create_client, Client

# --- 1. CONFIGURAÇÃO DA PÁGINA (DEVE SER A PRIMEIRA LINHA) ---
st.set_page_config(page_title="PowerLog PRO", page_icon="💪", layout="centered")

# --- 2. CONEXÃO SUPABASE ---
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

# --- 3. ESTILO CSS E ÍCONES ---
st.markdown(f"""
    <link rel="apple-touch-icon" sizes="180x180" href="https://raw.githubusercontent.com/RFlores78/meu-treino/main/icon.png">
    <style>
    .stButton>button {{ width: 100%; border-radius: 12px; height: 3.5em; background-color: #007bff; color: white; font-weight: bold; }}
    .ex-card {{ background: white; padding: 20px; border-radius: 20px; box-shadow: 0px 10px 20px rgba(0,0,0,0.05); text-align: center; margin-bottom: 20px; border: 1px solid #e1e1e1; }}
    .big-emoji {{ font-size: 50px; display: block; }}
    .ex-title {{ font-size: 24px; font-weight: 800; color: #1e1e1e; }}
    .time-display {{ font-size: 28px; font-weight: bold; color: #ff4b4b; background: #fff5f5; padding: 15px; border-radius: 15px; text-align: center; border: 2px solid #ffcccc; margin-bottom: 20px; }}
    .metric-box {{ background: #f0f2f6; padding: 10px; border-radius: 10px; text-align: center; font-weight: bold; }}
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

# --- 5. VARIÁVEIS DE SESSÃO E FUNÇÕES ---
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
st.sidebar.write(f"Logado como: {st.session_state.user.email}")
if st.sidebar.button("Sair"):
    supabase.auth.sign_out()
    st.session_state.user = None
    st.rerun()

menu = st.sidebar.selectbox("Navegação", ["🏋️ Treinar Agora", "📊 Histórico", "🆕 Configurar Meus Treinos"])

# --- MENU: CONFIGURAR ---
if menu == "🆕 Configurar Meus Treinos":
    st.subheader("🛠️ Monte sua Grade de Treino")
    df_cat = buscar_catalogo()
    with st.form("form_montagem"):
        nome_treino = st.text_input("Nome do treino (Ex: Treino A)", placeholder="Ex: Superior")
        escolha = st.selectbox("Escolha do catálogo:", df_cat['nome'].tolist() if not df_cat.empty else [])
        if st.form_submit_button("➕ Adicionar"):
            if nome_treino and not df_cat.empty:
                detalhes = df_cat[df_cat['nome'] == escolha].iloc[0]
                supabase.table("exercicios").insert({
                    "user_id": user_id, "treino": nome_treino.upper(), "nome": escolha, "emoji": detalhes['emoji']
                }).execute()
                st.success("Adicionado!")
                st.rerun()

    st.divider()
    st.write("📋 **Sua Configuração Atual:**")
    meus_ex = buscar_meus_treinos()
    
    if not meus_ex.empty:
        for i, row in meus_ex.iterrows():
            col1, col2, col3 = st.columns([1, 3, 1])
            with col1:
                st.write(f"{row['treino']}")
            with col2:
                st.write(f"{row['emoji']} {row['nome']}")
            with col3:
                # Botão de excluir para cada linha
                if st.button("🗑️", key=f"del_{row['id']}"):
                    supabase.table("exercicios").delete().eq("id", row['id']).execute()
                    st.success("Excluído!")
                    st.rerun()
    else:
        st.info("Nenhum exercício configurado.")

# --- MENU: TREINAR ---
elif menu == "🏋️ Treinar Agora":
    meus_ex = buscar_meus_treinos()
    df_s = buscar_sessoes()

    if not df_s.empty:
        ultimo = df_s.iloc[0]
        st.info(f"🔙 Último: {ultimo['treino_tipo']} em {ultimo['data']}")

    if meus_ex.empty:
        st.warning("Configure seus treinos primeiro!")
    else:
        lista_t = sorted(meus_ex['treino'].unique())
        treino_sel = st.radio("Treino de hoje:", lista_t, horizontal=True)

        if st.session_state.hora_inicio:
            seg = int(time.time() - st.session_state.hora_inicio)
            st.markdown(f"<div class='time-display'>⏱️ {seg//60:02d}:{seg%60:02d}</div>", unsafe_allow_html=True)
            if st.button("🏁 ENCERRAR TREINO"):
                tempo_f = f"{seg//60:02d}:{seg%60:02d}"
                supabase.table("sessoes").insert({
                    "user_id": user_id, "data": datetime.now().strftime("%Y-%m-%d"),
                    "duracao": tempo_f, "treino_tipo": treino_sel
                }).execute()
                st.session_state.hora_inicio = None
                st.rerun()
        else:
            if st.button("▶️ INICIAR NOVO TREINO"):
                st.session_state.hora_inicio = time.time()
                st.rerun()

        st.divider()
        ex_f = meus_ex[meus_ex['treino'] == treino_sel]
        escolhido = st.selectbox("Exercício:", ex_f['nome'])
        dados = ex_f[ex_f['nome'] == escolhido].iloc[0]
        
        st.markdown(f"<div class='ex-card'><span class='big-emoji'>{dados['emoji']}</span><div class='ex-title'>{dados['nome']}</div></div>", unsafe_allow_html=True)
        
        n_series = st.number_input("Séries", 1, 10, 4)
        c1, c2 = st.columns(2)
        with c1: p = st.number_input("Peso (kg)", 0.0, 500.0, step=0.5)
        with c2: r = st.number_input("Reps", 0, 100, 10)

        if st.button("✅ Salvar Séries"):
            hoje = datetime.now().strftime("%d/%m/%Y %H:%M")
            for i in range(int(n_series)):
                supabase.table("logs").insert({
                    "user_id": user_id, "data": hoje, "exercicio": escolhido, "peso": p, "reps": r, "serie_num": i+1
                }).execute()
            st.success("Salvo!")

# --- MENU: HISTÓRICO ---
elif menu == "📊 Histórico":
    df_l = buscar_logs()
    df_s = buscar_sessoes()
    
    tab1, tab2 = st.tabs(["🗓️ Calendário", "📈 Evolução"])
    
    with tab1:
        eventos = []
        if not df_s.empty:
            for _, r in df_s.iterrows():
                eventos.append({
                    "title": f"💪 {r['treino_tipo']}", 
                    "start": r['data'], 
                    "backgroundColor": "#007bff"
                })
        calendar(events=eventos, options={"locale": "pt-br"})
        
    with tab2:
        if not df_l.empty:
            ex_sel = st.selectbox("Exercício:", sorted(df_l['exercicio'].unique()))
            df_ev = df_l[df_l['exercicio'] == ex_sel].copy()
            
            # SOLUÇÃO PARA O ERRO: Converte a data de forma flexível
            # O 'errors=coerce' transforma datas inválidas em NaT (Not a Time) para não quebrar o app
            df_ev['data_dt'] = pd.to_datetime(df_ev['data'], dayfirst=True, errors='coerce')
            
            # Remove linhas onde a data falhou na conversão
            df_ev = df_ev.dropna(subset=['data_dt'])
            
            if not df_ev.empty:
                df_plot = df_ev.sort_values('data_dt').set_index('data_dt')
                st.line_chart(df_plot['peso'])
            else:
                st.warning("Formato de data incompatível para gerar o gráfico.")
