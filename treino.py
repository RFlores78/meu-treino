import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import time

# Configuração da página
st.set_page_config(page_title="PowerLog PRO", page_icon="💪", layout="centered")

# Estilo CSS
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 12px; height: 3.5em; background-color: #007bff; color: white; font-weight: bold; }
    .ex-card { background: white; padding: 20px; border-radius: 20px; box-shadow: 0px 10px 20px rgba(0,0,0,0.05); text-align: center; margin-bottom: 20px; border: 1px solid #e1e1e1; }
    .big-emoji { font-size: 50px; display: block; }
    .ex-title { font-size: 22px; font-weight: 800; color: #1e1e1e; }
    .time-display { font-size: 28px; font-weight: bold; color: #ff4b4b; background: #fff5f5; padding: 15px; border-radius: 15px; text-align: center; border: 2px solid #ffcccc; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

def init_db():
    conn = sqlite3.connect('treino_v9.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS exercicios 
                 (id INTEGER PRIMARY KEY, treino TEXT, emoji TEXT, nome TEXT, meta TEXT, e1 TEXT, e2 TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS logs 
                 (id INTEGER PRIMARY KEY, data TEXT, exercicio TEXT, peso REAL, reps INTEGER, serie_num INTEGER)''')
    c.execute('''CREATE TABLE IF NOT EXISTS sessoes 
                 (id INTEGER PRIMARY KEY, data TEXT, duracao_texto TEXT, treino_tipo TEXT)''')
    
    c.execute("SELECT count(*) FROM exercicios")
    if c.fetchone()[0] == 0:
        treinos = [
            # TREINO A
            ('A', '🔥', 'Combo: Supino Inclinado + Crucifixo Inclinado', '4x12 + 4x15', 'Supino Inclinado', 'Crucifixo Inclinado'),
            ('A', '🔋', 'Combo: Pulôver + Desenvolvimento', '3x15 + 3x15', 'Pulôver', 'Desenvolvimento'),
            ('A', '🎯', 'Supino Reto com Halteres', '4 x 8 a 10', '', ''),
            ('A', '💀', 'Tríceps Testa com Halteres', '4 x 8 a 10', '', ''),
            ('A', '💪', 'Tríceps Francês com Halteres', '4 x 8 a 12', '', ''),
            # TREINO B
            ('B', '⏱️', 'Extensora Isométrica', '5 x 20s', '', ''),
            ('B', '🦵', 'Extensora', '3 x 15', '', ''),
            ('B', '🚀', 'Leg Press c/ Pés Afastados', '4 x 8 a 10', '', ''),
            ('B', '🦶', 'Panturrilha no Leg Press', '4 x 15', '', ''),
            ('B', '💥', 'Leg Press Horizontal Unilateral', '3 x 8 a 10', '', ''),
            ('B', '🎢', 'Cadeira Flexora', '3 x 8 a 10', '', ''),
            ('B', '⏱️', 'Flexora Isometria', '4 x 20s', '', ''),
            # TREINO C
            ('C', '🛶', 'Combo: Remada Curvada + Rosca Alternada', '4x15 + 4x15', 'Remada Curvada', 'Rosca Alternada'),
            ('C', '⚔️', 'Combo: Remada Unilateral + Rosca Direta', '3x15 + 3x15', 'Remada Unilateral', 'Rosca Direta'),
            ('C', '⛓️', 'Remada Fechada com Barra Reta', '4 x 8 a 10', '', ''),
            ('C', '🔨', 'Rosca Martelo com Halteres', '4 x 8 a 10', '', ''),
            ('C', '🎯', 'Rosca Concentrada', '3 x 8 a 12', '', ''),
            # TREINO D
            ('D', '🧬', 'Rosca Direta Barra Reta 21', '3 x 21', '', ''),
            ('D', '📉', 'Rosca Direta Banco Inclinado', '3 x 8 a 12', '', ''),
            ('D', '🔼', 'Desenvolvimento Sentado (Neutro)', '4 x 8', '', ''),
            ('D', '🦅', 'Elevação Lateral com Halteres', '3 x 8 a 12', '', ''),
            ('D', '💪', 'Tríceps Francês com Halteres', '3 x 8 a 12', '', ''),
            ('D', '🐎', 'Tríceps Coice', '4 x 12', '', '')
        ]
        c.executemany("INSERT INTO exercicios (treino, emoji, nome, meta, e1, e2) VALUES (?, ?, ?, ?, ?, ?)", treinos)
    conn.commit()
    conn.close()

init_db()

if 'hora_inicio' not in st.session_state: st.session_state.hora_inicio = None

st.title("⚡ PowerLog PRO")
menu = st.sidebar.selectbox("Navegação", ["🏋️ Treinar Agora", "📊 Histórico"])

if menu == "🏋️ Treinar Agora":
    treino_sel = st.radio("Qual o treino de hoje?", ["A", "B", "C", "D"], horizontal=True)

    c1, c2 = st.columns([2,1])
    if st.session_state.hora_inicio is None:
        if c1.button("▶️ Iniciar Treino"): 
            st.session_state.hora_inicio = time.time()
            st.rerun()
    else:
        segundos_totais = int(time.time() - st.session_state.hora_inicio)
        mins, segs = divmod(segundos_totais, 60)
        tempo_f = f"{mins:02d}:{segs:02d}"
        c1.markdown(f"<div class='time-display'>⏱️ {tempo_f}</div>", unsafe_allow_html=True)
        if c2.button("🏁 Finalizar"):
            conn = sqlite3.connect('treino_v9.db')
            conn.cursor().execute("INSERT INTO sessoes (data, duracao_texto, treino_tipo) VALUES (?, ?, ?)", (datetime.now().strftime("%Y-%m-%d"), tempo_f, treino_sel))
            conn.commit(); conn.close()
            st.session_state.hora_inicio = None
            st.success(f"Finalizado em {tempo_f}!"); st.balloons(); time.sleep(1); st.rerun()
        time.sleep(1)
        st.rerun() # Faz o cronômetro atualizar sozinho

    st.divider()

    conn = sqlite3.connect('treino_v9.db')
    df_ex = pd.read_sql(f"SELECT * FROM exercicios WHERE treino='{treino_sel}'", conn)
    conn.close()

    if not df_ex.empty:
        ex_escolhido = st.selectbox("Selecione o Exercício:", df_ex['nome'])
        dados = df_ex[df_ex['nome'] == ex_escolhido].fillna('').iloc[0]
        
        st.markdown(f"<div class='ex-card'><span class='big-emoji'>{dados['emoji']}</span><div class='ex-title'>{dados['nome']}</div><div style='color:gray'>Meta: {dados['meta']}</div></div>", unsafe_allow_html=True)

        if dados['e1'] != '' and dados['e2'] != '':
            n_series = st.number_input("Séries", 1, 10, 4, key=f"s_{dados['nome']}")
            for i in range(int(n_series)):
                st.write(f"**Série {i+1}**")
                col1, col2 = st.columns(2)
                with col1:
                    p1 = st.number_input(f"Peso {dados['e1']} (kg)", 0.0, 500.0, step=0.5, key=f"p1_{i}_{dados['nome']}")
                    r1 = st.number_input(f"Reps {dados['e1']}", 0, 100, 12, key=f"r1_{i}_{dados['nome']}")
                with col2:
                    p2 = st.number_input(f"Peso {dados['e2']} (kg)", 0.0, 500.0, step=0.5, key=f"p2_{i}_{dados['nome']}")
                    r2 = st.number_input(f"Reps {dados['e2']}", 0, 100, 15, key=f"r2_{i}_{dados['nome']}")
            
            if st.button("✅ Salvar Combo"):
                conn = sqlite3.connect('treino_v9.db'); c = conn.cursor(); hoje = datetime.now().strftime("%d/%m/%Y %H:%M")
                for i in range(int(n_series)):
                    # Coleta os dados exatos de cada input do loop
                    c.execute("INSERT INTO logs (data, exercicio, peso, reps, serie_num) VALUES (?, ?, ?, ?, ?)", (hoje, dados['e1'], st.session_state[f"p1_{i}_{dados['nome']}"], st.session_state[f"r1_{i}_{dados['nome']}"], i+1))
                    c.execute("INSERT INTO logs (data, exercicio, peso, reps, serie_num) VALUES (?, ?, ?, ?, ?)", (hoje, dados['e2'], st.session_state[f"p2_{i}_{dados['nome']}"], st.session_state[f"r2_{i}_{dados['nome']}"], i+1))
                conn.commit(); conn.close(); st.toast("Salvo!")
        else:
            n_series = st.number_input("Séries", 1, 10, 4, key=f"s_{dados['nome']}")
            for i in range(int(n_series)):
                c1, c2 = st.columns(2)
                with c1: p = st.number_input(f"Série {i+1}: Peso (kg)", 0.0, 500.0, step=0.5, key=f"p_{i}_{dados['nome']}")
                with c2: r = st.number_input(f"Série {i+1}: Reps", 0, 100, 10, key=f"r_{i}_{dados['nome']}")

            if st.button("✅ Salvar Séries"):
                conn = sqlite3.connect('treino_v9.db'); c = conn.cursor(); hoje = datetime.now().strftime("%d/%m/%Y %H:%M")
                for i in range(int(n_series)):
                    c.execute("INSERT INTO logs (data, exercicio, peso, reps, serie_num) VALUES (?, ?, ?, ?, ?)", (hoje, dados['nome'], st.session_state[f"p_{i}_{dados['nome']}"], st.session_state[f"r_{i}_{dados['nome']}"], i+1))
                conn.commit(); conn.close(); st.toast("Salvo!")

elif menu == "📊 Histórico":
    st.subheader("📈 Histórico")
    conn = sqlite3.connect('treino_v9.db'); df_l = pd.read_sql("SELECT data, exercicio, peso, reps, serie_num FROM logs ORDER BY id DESC", conn); conn.close()
    if not df_l.empty:
        ex_f = st.selectbox("Exercício:", df_l['exercicio'].unique())
        st.dataframe(df_l[df_l['exercicio'] == ex_f], use_container_width=True)
