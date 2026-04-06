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
    .combo-label { background: #eefbff; color: #007bff; padding: 5px 10px; border-radius: 8px; font-size: 12px; font-weight: bold; margin-bottom: 10px; display: inline-block; }
    </style>
    """, unsafe_allow_html=True)

# --- BANCO DE DADOS ---
def init_db():
    conn = sqlite3.connect('treino_v6.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS exercicios 
                 (id INTEGER PRIMARY KEY, treino TEXT, emoji TEXT, nome TEXT, meta TEXT, e1 TEXT, e2 TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS logs 
                 (id INTEGER PRIMARY KEY, data TEXT, exercicio TEXT, peso REAL, reps INTEGER)''')
    c.execute('''CREATE TABLE IF NOT EXISTS sessoes 
                 (id INTEGER PRIMARY KEY, data TEXT, duracao_min INTEGER, treino_tipo TEXT)''')
    
    c.execute("SELECT count(*) FROM exercicios")
    if c.fetchone()[0] == 0:
        # e1 e e2 são os nomes individuais para exercícios combinados
        treinos = [
            # TREINO A
            ('A', '🔥', 'Combinado: Supino Inclinado + Crucifixo Inclinado', '4x12 + 4x15', 'Supino Inclinado (Halter)', 'Crucifixo Inclinado (Halter)'),
            ('A', '🔋', 'Combinado: Pulôver + Desenvolvimento', '3x15 + 3x15', 'Pulôver (Halter)', 'Desenvolvimento (Halter)'),
            ('A', '🎯', 'Supino Reto com Halteres', '4 x 8 a 10', None, None),
            ('A', '💀', 'Tríceps Testa com Halteres', '4 x 8 a 10', None, None),
            ('A', '💪', 'Tríceps Francês com Halteres', '4 x 8 a 12', None, None),
            # TREINO B
            ('B', '⏱️', 'Extensora Isométrica', '5 x 20 segundos', None, None),
            ('B', '🦵', 'Extensora', '3 x 15', None, None),
            ('B', '🚀', 'Leg Press c/ Pés Afastados', '4 x 8 a 10', None, None),
            ('B', '🦶', 'Panturrilha no Leg Press', '4 x 15', None, None),
            ('B', '💥', 'Leg Press Horizontal Unilateral', '3 x 8 a 10', None, None),
            ('B', '🎢', 'Cadeira Flexora', '3 x 8 a 10', None, None),
            ('B', '⏱️', 'Flexora Isometria', '4 x 20 segundos', None, None),
            # TREINO C
            ('C', '🛶', 'Combinado: Remada Curvada + Rosca Alternada', '4x15 + 4x15', 'Remada Curvada (Barra)', 'Rosca Alternada (Halter)'),
            ('C', '⚔️', 'Combinado: Remada Unilateral + Rosca Direta', '3x15 + 3x15', 'Remada Unilateral (Halter)', 'Rosca Direta (Halter)'),
            ('C', '⛓️', 'Remada Fechada com Barra Reta', '4 x 8 a 10', None, None),
            ('C', '🔨', 'Rosca Martelo com Halteres', '4 x 8 a 10', None, None),
            ('C', '🎯', 'Rosca Concentrada', '3 x 8 a 12', None, None),
            # TREINO D
            ('D', '🧬', 'Rosca Direta com Barra Reta 21', '3 x 21', None, None),
            ('D', '📉', 'Rosca Direta Banco Inclinado', '3 x 8 a 12', None, None),
            ('D', '🔼', 'Desenvolvimento Sentado (Neutro)', '4 x 8', None, None),
            ('D', '🦅', 'Elevação Lateral com Halteres', '3 x 8 a 12', None, None),
            ('D', '💪', 'Tríceps Francês com Halteres', '3 x 8 a 12', None, None),
            ('D', '🐎', 'Tríceps Coice', '4 x 12', None, None)
        ]
        c.executemany("INSERT INTO exercicios (treino, emoji, nome, meta, e1, e2) VALUES (?, ?, ?, ?, ?, ?)", treinos)
    conn.commit()
    conn.close()

init_db()

if 'hora_inicio' not in st.session_state: st.session_state.hora_inicio = None

st.title("⚡ PowerLog PRO")
menu = st.sidebar.selectbox("Navegação", ["🏋️ Treinar Agora", "📅 Calendário & Stats", "📊 Histórico de Séries"])

if menu == "🏋️ Treinar Agora":
    treino_sel = st.radio("Selecione o Treino:", ["A", "B", "C", "D"], horizontal=True)

    # Cronômetro
    c1, c2 = st.columns([2,1])
    if st.session_state.hora_inicio is None:
        if c1.button("▶️ Iniciar Treino"): st.session_state.hora_inicio = time.time(); st.rerun()
    else:
        duracao = int((time.time() - st.session_state.hora_inicio) / 60)
        c1.warning(f"⏳ Tempo: {duracao} min")
        if c2.button("🏁 Finalizar"):
            conn = sqlite3.connect('treino_v6.db'); conn.cursor().execute("INSERT INTO sessoes (data, duracao_min, treino_tipo) VALUES (?, ?, ?)", (datetime.now().strftime("%Y-%m-%d"), duracao, treino_sel)); conn.commit(); conn.close()
            st.session_state.hora_inicio = None; st.success("Finalizado!"); st.balloons(); time.sleep(1); st.rerun()

    st.divider()

    conn = sqlite3.connect('treino_v6.db')
    df_ex = pd.read_sql(f"SELECT * FROM exercicios WHERE treino='{treino_sel}'", conn)
    conn.close()

    if not df_ex.empty:
        ex_escolhido = st.selectbox("Selecione o Exercício:", df_ex['nome'])
        dados = df_ex[df_ex['nome'] == ex_escolhido].iloc[0]
        
        st.markdown(f"<div class='ex-card'><span class='big-emoji'>{dados['emoji']}</span><div class='ex-title'>{dados['nome']}</div><div class='ex-subtitle'>Meta: {dados['meta']}</div></div>", unsafe_allow_html=True)

        # SE FOR COMBINADO, ABRE DOIS CAMPOS
        if dados['e1'] and dados['e2']:
            st.markdown("<span class='combo-label'>SÉRIE COMBINADA</span>", unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**1. {dados['e1']}**")
                p1 = st.number_input(f"Peso (kg) - {dados['e1'][:10]}...", min_value=0.0, step=0.5, key="p1")
                r1 = st.number_input(f"Reps - {dados['e1'][:10]}...", min_value=0, step=1, value=12, key="r1")
            with col2:
                st.write(f"**2. {dados['e2']}**")
                p2 = st.number_input(f"Peso (kg) - {dados['e2'][:10]}...", min_value=0.0, step=0.5, key="p2")
                r2 = st.number_input(f"Reps - {dados['e2'][:10]}...", min_value=0, step=1, value=15, key="r2")
            
            if st.button("✅ Salvar Série Combinada"):
                conn = sqlite3.connect('treino_v6.db')
                c = conn.cursor()
                hoje = datetime.now().strftime("%d/%m/%Y %H:%M")
                c.execute("INSERT INTO logs (data, exercicio, peso, reps) VALUES (?, ?, ?, ?)", (hoje, dados['e1'], p1, r1))
                c.execute("INSERT INTO logs (data, exercicio, peso, reps) VALUES (?, ?, ?, ?)", (hoje, dados['e2'], p2, r2))
                conn.commit(); conn.close()
                st.toast("Ambas as séries salvas!")
        else:
            # EXERCÍCIO SIMPLES
            c1, c2 = st.columns(2)
            with c1: p = st.number_input("Peso (kg)", min_value=0.0, step=0.5)
            with c2: r = st.number_input("Reps Feitas", min_value=0, step=1, value=10)
            if st.button("✅ Salvar Série"):
                conn = sqlite3.connect('treino_v6.db'); conn.cursor().execute("INSERT INTO logs (data, exercicio, peso, reps) VALUES (?, ?, ?, ?)", (datetime.now().strftime("%d/%m/%Y %H:%M"), dados['nome'], p, r)); conn.commit(); conn.close()
                st.toast("Série Salva!")

elif menu == "📅 Calendário & Stats":
    st.subheader("📅 Desempenho Anual")
    conn = sqlite3.connect('treino_v6.db'); df_s = pd.read_sql("SELECT * FROM sessoes", conn); conn.close()
    if not df_s.empty:
        df_s['data'] = pd.to_datetime(df_s['data'])
        col1, col2 = st.columns(2)
        col1.metric("Dias Treinados", len(df_s))
        col2.metric("Total Horas", round(df_s['duracao_min'].sum()/60, 1))
        st.table(df_s[['data', 'treino_tipo', 'duracao_min']].sort_values('data', ascending=False))

elif menu == "📊 Histórico de Séries":
    st.subheader("📈 Histórico por Exercício")
    conn = sqlite3.connect('treino_v6.db'); df_l = pd.read_sql("SELECT data, exercicio, peso, reps FROM logs ORDER BY id DESC", conn); conn.close()
    if not df_l.empty:
        ex_filter = st.multiselect("Filtrar por Exercício:", df_l['exercicio'].unique())
        if ex_filter: df_l = df_l[df_l['exercicio'].isin(ex_filter)]
        st.dataframe(df_l, use_container_width=True)
