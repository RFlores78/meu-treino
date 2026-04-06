import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import time

# Configuração da página
st.set_page_config(page_title="PowerLog PRO", page_icon="💪", layout="centered")

# Estilo CSS Premium
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .stButton>button { width: 100%; border-radius: 12px; height: 3.5em; background-color: #007bff; color: white; font-weight: bold; border: none; }
    .ex-card { background: white; padding: 20px; border-radius: 20px; box-shadow: 0px 10px 20px rgba(0,0,0,0.05); text-align: center; margin-bottom: 20px; border: 1px solid #e1e1e1; }
    .big-emoji { font-size: 60px; display: block; margin-bottom: 10px; }
    .ex-title { font-size: 20px; font-weight: 800; color: #1e1e1e; line-height: 1.2; }
    .ex-subtitle { font-size: 14px; color: #666; margin-top: 5px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- BANCO DE DADOS ---
def init_db():
    conn = sqlite3.connect('treino_v5.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS exercicios 
                 (id INTEGER PRIMARY KEY, treino TEXT, emoji TEXT, nome TEXT, meta TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS logs 
                 (id INTEGER PRIMARY KEY, data TEXT, exercicio TEXT, peso REAL, reps INTEGER)''')
    c.execute('''CREATE TABLE IF NOT EXISTS sessoes 
                 (id INTEGER PRIMARY KEY, data TEXT, duracao_min INTEGER, treino_tipo TEXT)''')
    
    c.execute("SELECT count(*) FROM exercicios")
    if c.fetchone()[0] == 0:
        treinos = [
            # TREINO A
            ('A', '🔥', 'Combinado: Supino Inclinado com Halteres + Crucifixo Inclinado com Halteres', '4 x 12 + 4 x 15'),
            ('A', '🔋', 'Combinado: Pulôver com Halteres + Desenvolvimento com Halteres', '3 x 15 + 3 x 15'),
            ('A', '🎯', 'Supino Reto com Halteres', '4 x 8 a 10'),
            ('A', '💀', 'Tríceps Testa com Halteres', '4 x 8 a 10'),
            ('A', '💪', 'Tríceps Francês com Halteres', '4 x 8 a 12'),
            # TREINO B
            ('B', '⏱️', 'Extensora Isométrica', '5 x 20 segundos'),
            ('B', '🦵', 'Extensora', '3 x 15'),
            ('B', '🚀', 'Leg Press c/ Pés Afastados', '4 x 8 a 10'),
            ('B', '🦶', 'Panturrilha no Leg Press', '4 x 15'),
            ('B', '💥', 'Leg Press Horizontal Unilateral', '3 x 8 a 10'),
            ('B', '🎢', 'Cadeira Flexora', '3 x 8 a 10'),
            ('B', '⏱️', 'Flexora Isometria', '4 x 20 segundos'),
            ('B', '🦶', 'Panturrilha no Leg Press (Extra)', '4 x 15'),
            # TREINO C
            ('C', '🛶', 'Combinado: Remada Curvada com Barra Reta + Rosca Alternada com Halteres', '4 x 15 + 4 x 15'),
            ('C', '⚔️', 'Combinado: Remada Unilateral com Halteres + Rosca Direta com Halteres', '3 x 15 + 3 x 15'),
            ('C', '⛓️', 'Remada Fechada com Barra Reta', '4 x 8 a 10'),
            ('C', '🔨', 'Rosca Martelo com Halteres', '4 x 8 a 10'),
            ('C', '🎯', 'Rosca Concentrada', '3 x 8 a 12'),
            # TREINO D
            ('D', '🧬', 'Rosca Direta com Barra Reta 21 (7+7+7)', '3 x 21'),
            ('D', '📉', 'Rosca Direta Banco Inclinado', '3 x 8 a 12'),
            ('D', '🔼', 'Desenvolvimento Sentado com Halteres (Pegada Neutra)', '4 x 8'),
            ('D', '🦅', 'Elevação Lateral com Halteres', '3 x 8 a 12'),
            ('D', '💪', 'Tríceps Francês com Halteres', '3 x 8 a 12'),
            ('D', '🐎', 'Tríceps Coice', '4 x 12')
        ]
        c.executemany("INSERT INTO exercicios (treino, emoji, nome, meta) VALUES (?, ?, ?, ?)", treinos)
    conn.commit()
    conn.close()

init_db()

# --- LÓGICA DE ESTADO ---
if 'hora_inicio' not in st.session_state: st.session_state.hora_inicio = None

# --- INTERFACE ---
st.title("⚡ PowerLog PRO")

menu = st.sidebar.selectbox("Navegação", ["🏋️ Treinar Agora", "📅 Calendário & Stats", "📊 Histórico de Séries"])

if menu == "🏋️ Treinar Agora":
    st.subheader("Bora pra cima! 🚀")
    treino_sel = st.radio("Selecione o Treino:", ["A", "B", "C", "D"], horizontal=True)

    c_cron1, c_cron2 = st.columns([2, 1])
    if st.session_state.hora_inicio is None:
        if c_cron1.button("▶️ Iniciar Treino"):
            st.session_state.hora_inicio = time.time()
            st.rerun()
    else:
        duracao = int((time.time() - st.session_state.hora_inicio) / 60)
        c_cron1.warning(f"⏳ Tempo: {duracao} min")
        if c_cron2.button("🏁 Finalizar"):
            conn = sqlite3.connect('treino_v5.db')
            conn.cursor().execute("INSERT INTO sessoes (data, duracao_min, treino_tipo) VALUES (?, ?, ?)",
                                 (datetime.now().strftime("%Y-%m-%d"), duracao, treino_sel))
            conn.commit()
            conn.close()
            st.session_state.hora_inicio = None
            st.success("Treino Finalizado!")
            st.balloons()
            time.sleep(2)
            st.rerun()

    st.divider()

    conn = sqlite3.connect('treino_v5.db')
    df_ex = pd.read_sql(f"SELECT * FROM exercicios WHERE treino='{treino_sel}'", conn)
    conn.close()

    if not df_ex.empty:
        ex_escolhido = st.selectbox("Selecione o Exercício:", df_ex['nome'])
        dados_ex = df_ex[df_ex['nome'] == ex_escolhido].iloc[0]
        
        # CARD PROFISSIONAL
        st.markdown(f"""
            <div class='ex-card'>
                <span class='big-emoji'>{dados_ex['emoji']}</span>
                <div class='ex-title'>{dados_ex['nome']}</div>
                <div class='ex-subtitle'>Meta: {dados_ex['meta']}</div>
            </div>
            """, unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1: peso = st.number_input("Peso (kg)", min_value=0.0, step=0.5, format="%.1f")
        with c2: reps = st.number_input("Reps Feitas", min_value=0, step=1, value=10) # Valor inicial 10 p/ agilizar
            
        if st.button("✅ Salvar Série"):
            conn = sqlite3.connect('treino_v5.db')
            conn.cursor().execute("INSERT INTO logs (data, exercicio, peso, reps) VALUES (?, ?, ?, ?)",
                                 (datetime.now().strftime("%d/%m/%Y %H:%M"), ex_escolhido, peso, reps))
            conn.commit()
            conn.close()
            st.toast(f"Série Salva: {peso}kg")

elif menu == "📅 Calendário & Stats":
    st.subheader("📅 Desempenho Anual")
    conn = sqlite3.connect('treino_v5.db')
    df_s = pd.read_sql("SELECT * FROM sessoes", conn)
    conn.close()
    if not df_s.empty:
        df_s['data'] = pd.to_datetime(df_s['data'])
        df_ano = df_s[df_s['data'].dt.year == datetime.now().year]
        col_m1, col_m2 = st.columns(2)
        col_m1.metric("Dias Treinados", len(df_ano))
        col_m2.metric("Total Horas", round(df_ano['duracao_min'].sum()/60, 1))
        st.table(df_ano[['data', 'treino_tipo', 'duracao_min']].sort_values('data', ascending=False))

elif menu == "📊 Histórico de Séries":
    st.subheader("📈 Histórico de Cargas")
    conn = sqlite3.connect('treino_v5.db')
    df_l = pd.read_sql("SELECT data, exercicio, peso, reps FROM logs ORDER BY id DESC", conn)
    conn.close()
    st.dataframe(df_l, use_container_width=True)
