import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import time

# Configuração da página
st.set_page_config(page_title="PowerLog PRO", page_icon="💪", layout="centered")

# Estilo CSS Profissional
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 10px; font-weight: bold; }
    .metric-card { background: white; padding: 15px; border-radius: 10px; box-shadow: 2px 2px 5px rgba(0,0,0,0.1); text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# --- BANCO DE DADOS ---
def init_db():
    conn = sqlite3.connect('treino_v3.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS exercicios (id INTEGER PRIMARY KEY, treino TEXT, nome TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS logs (id INTEGER PRIMARY KEY, data TEXT, exercicio TEXT, peso REAL, reps INTEGER)''')
    c.execute('''CREATE TABLE IF NOT EXISTS sessoes (id INTEGER PRIMARY KEY, data TEXT, duracao_min INTEGER, treino_tipo TEXT)''')
    
    c.execute("SELECT count(*) FROM exercicios")
    if c.fetchone()[0] == 0:
        treinos = [
            ('A', '🔥 Supino Inclinado + Crucifixo'), ('A', '🔋 Pulôver + Desenv.'), ('A', '🎯 Supino Reto'), ('A', '💀 Tríceps Testa'), ('A', '💪 Tríceps Francês'),
            ('B', '⏱️ Extensora Isomet.'), ('B', '🦵 Extensora'), ('B', '🚀 Leg Press Pés Afast.'), ('B', '🦶 Panturrilha Leg'), ('B', '💥 Leg Unilateral'), ('B', '🎢 Cadeira Flexora'), ('B', '⏱️ Flexora Isomet.'),
            ('C', '🛶 Remada Curvada + Rosca Alt.'), ('C', '⚔️ Remada Unilat. + Rosca Direta'), ('C', '⛓️ Remada Fechada'), ('C', '🔨 Rosca Martelo'), ('C', '🎯 Rosca Concentrada'),
            ('D', '🧬 Rosca Direta 21'), ('D', '📉 Rosca Banco Incl.'), ('D', '🔼 Desenv. Sentado'), ('D', '🦅 Elevação Lateral'), ('D', '💪 Tríceps Francês'), ('D', '🐎 Tríceps Coice')
        ]
        c.executemany("INSERT INTO exercicios (treino, nome) VALUES (?, ?)", treinos)
    conn.commit()
    conn.close()

init_db()

# --- LÓGICA DE ESTADO ---
if 'hora_inicio' not in st.session_state:
    st.session_state.hora_inicio = None

# --- INTERFACE ---
st.title("⚡ PowerLog PRO")

menu = st.sidebar.selectbox("Navegação", ["🏋️ Treinar Agora", "📅 Calendário & Stats", "📊 Histórico de Séries"])

if menu == "🏋️ Treinar Agora":
    st.subheader("Bora pra cima! 🚀")
    
    treino_sel = st.radio("Selecione o Treino:", ["A", "B", "C", "D"], horizontal=True)

    # Controle do Cronômetro
    col_t1, col_t2 = st.columns(2)
    
    if st.session_state.hora_inicio is None:
        if col_t1.button("▶️ Iniciar Treino"):
            st.session_state.hora_inicio = time.time()
            st.rerun()
    else:
        duracao_atual = int((time.time() - st.session_state.hora_inicio) / 60)
        col_t1.warning(f"⏳ Em treino: {duracao_atual} min")
        if col_t2.button("🏁 Finalizar Treino"):
            fim = time.time()
            tempo_total = int((fim - st.session_state.hora_inicio) / 60)
            
            conn = sqlite3.connect('treino_v3.db')
            conn.cursor().execute("INSERT INTO sessoes (data, duracao_min, treino_tipo) VALUES (?, ?, ?)",
                                 (datetime.now().strftime("%Y-%m-%d"), tempo_total, treino_sel))
            conn.commit()
            conn.close()
            
            st.session_state.hora_inicio = None
            st.success(f"Treino finalizado! Duração: {tempo_total} minutos.")
            st.balloons()
            time.sleep(2)
            st.rerun()

    st.divider()

    # Registro de Exercícios
    conn = sqlite3.connect('treino_v3.db')
    df_ex = pd.read_sql(f"SELECT nome FROM exercicios WHERE treino='{treino_sel}'", conn)
    conn.close()

    if not df_ex.empty:
        ex_foco = st.selectbox("Selecione o Exercício:", df_ex['nome'])
        c1, c2 = st.columns(2)
        with c1: peso = st.number_input("Peso (kg)", min_value=0.0, step=0.5)
        with c2: reps = st.number_input("Reps", min_value=0, step=1)
            
        if st.button("✅ Salvar Série"):
            conn = sqlite3.connect('treino_v3.db')
            conn.cursor().execute("INSERT INTO logs (data, exercicio, peso, reps) VALUES (?, ?, ?, ?)",
                                 (datetime.now().strftime("%d/%m/%Y %H:%M"), ex_foco, peso, reps))
            conn.commit()
            conn.close()
            st.toast(f"Salvo: {peso}kg")

elif menu == "📅 Calendário & Stats":
    st.subheader("📅 Seu Desempenho Anual")
    
    conn = sqlite3.connect('treino_v3.db')
    df_sessoes = pd.read_sql("SELECT * FROM sessoes", conn)
    conn.close()
    
    if not df_sessoes.empty:
        df_sessoes['data'] = pd.to_datetime(df_sessoes['data'])
        ano_atual = datetime.now().year
        df_ano = df_sessoes[df_sessoes['data'].dt.year == ano_atual]
        
        # Métricas Compiladas
        m1, m2, m3 = st.columns(3)
        with m1:
            st.markdown(f"<div class='metric-card'><h3>{len(df_ano)}</h3><p>Dias Treinados</p></div>", unsafe_allow_html=True)
        with m2:
            total_horas = round(df_ano['duracao_min'].sum() / 60, 1)
            st.markdown(f"<div class='metric-card'><h3>{total_horas}h</h3><p>Tempo Total</p></div>", unsafe_allow_html=True)
        with m3:
            media = int(df_ano['duracao_min'].mean()) if len(df_ano) > 0 else 0
            st.markdown(f"<div class='metric-card'><h3>{media}m</h3><p>Média/Treino</p></div>", unsafe_allow_html=True)
            
        st.write("### 📅 Dias de Treino")
        # Mostrar calendário simples (Lista de datas)
        df_display = df_ano[['data', 'treino_tipo', 'duracao_min']].copy()
        df_display['data'] = df_display['data'].dt.strftime('%d/%m/%Y')
        st.table(df_display.sort_values('data', ascending=False))
    else:
        st.info("Finalize seu primeiro treino para ver as estatísticas!")

elif menu == "📊 Histórico de Séries":
    st.subheader("📈 Cargas por Exercício")
    conn = sqlite3.connect('treino_v3.db')
    df_logs = pd.read_sql("SELECT * FROM logs ORDER BY id DESC", conn)
    conn.close()
    if not df_logs.empty:
        st.dataframe(df_logs[['data', 'exercicio', 'peso', 'reps']], use_container_width=True)
    else:
        st.write("Nenhuma série registrada.")
