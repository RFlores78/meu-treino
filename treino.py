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
    .ex-title { font-size: 24px; font-weight: 800; color: #1e1e1e; }
    .time-display { font-size: 28px; font-weight: bold; color: #ff4b4b; background: #fff5f5; padding: 15px; border-radius: 15px; text-align: center; border: 2px solid #ffcccc; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

def init_db():
    conn = sqlite3.connect('treino_final_v1.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS exercicios (id INTEGER PRIMARY KEY, treino TEXT, emoji TEXT, nome TEXT, e1 TEXT, e2 TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS logs (id INTEGER PRIMARY KEY, data TEXT, exercicio TEXT, peso REAL, reps INTEGER, serie_num INTEGER)''')
    c.execute('''CREATE TABLE IF NOT EXISTS sessoes (id INTEGER PRIMARY KEY, data TEXT, duracao TEXT, treino_tipo TEXT)''')
    
    c.execute("SELECT count(*) FROM exercicios")
    if c.fetchone()[0] == 0:
        exercicios_completos = [
            # TREINO A
            ('A', '🔥', 'Supino Inclinado + Crucifixo Inclinado', 'Supino Inclinado (Halter)', 'Crucifixo Inclinado (Halter)'),
            ('A', '🔋', 'Pulôver + Desenvolvimento', 'Pulôver (Halter)', 'Desenvolvimento (Halter)'),
            ('A', '🎯', 'Supino Reto com Halteres', '', ''),
            ('A', '💀', 'Tríceps Testa com Halteres', '', ''),
            ('A', '💪', 'Tríceps Francês com Halteres', '', ''),
            # TREINO B
            ('B', '⏱️', 'Extensora Isométrica', '', ''),
            ('B', '🦵', 'Extensora', '', ''),
            ('B', '🚀', 'Leg Press Pés Afastados', '', ''),
            ('B', '🦶', 'Panturrilha no Leg Press', '', ''),
            ('B', '💥', 'Leg Press Horizontal Unilateral', '', ''),
            ('B', '🎢', 'Cadeira Flexora', '', ''),
            ('B', '⏱️', 'Flexora Isometria', '', ''),
            # TREINO C
            ('C', '🛶', 'Remada Curvada + Rosca Alternada', 'Remada Curvada (Barra)', 'Rosca Alternada (Halter)'),
            ('C', '⚔️', 'Remada Unilateral + Rosca Direta', 'Remada Unilateral (Halter)', 'Rosca Direta (Halter)'),
            ('C', '⛓️', 'Remada Fechada com Barra Reta', '', ''),
            ('C', '🔨', 'Rosca Martelo com Halteres', '', ''),
            ('C', '🎯', 'Rosca Concentrada', '', ''),
            # TREINO D
            ('D', '🧬', 'Rosca Direta Barra Reta 21', '', ''),
            ('D', '📉', 'Rosca Direta Banco Inclinado', '', ''),
            ('D', '🔼', 'Desenvolvimento Sentado (Neutro)', '', ''),
            ('D', '🦅', 'Elevação Lateral com Halteres', '', ''),
            ('D', '💪', 'Tríceps Francês com Halteres', '', ''),
            ('D', '🐎', 'Tríceps Coice', '', '')
        ]
        c.executemany("INSERT INTO exercicios (treino, emoji, nome, e1, e2) VALUES (?, ?, ?, ?, ?)", exercicios_completos)
    conn.commit()
    conn.close()

init_db()

if 'hora_inicio' not in st.session_state: st.session_state.hora_inicio = None

st.title("⚡ PowerLog PRO")
menu = st.sidebar.selectbox("Navegação", ["🏋️ Treinar Agora", "📊 Histórico"])

if menu == "🏋️ Treinar Agora":
    treino_sel = st.radio("Selecione o Treino:", ["A", "B", "C", "D"], horizontal=True)

    c1, c2 = st.columns([2,1])
    if st.session_state.hora_inicio is None:
        if c1.button("▶️ Iniciar Treino"): 
            st.session_state.hora_inicio = time.time()
            st.rerun()
    else:
        seg_totais = int(time.time() - st.session_state.hora_inicio)
        mins, segs = divmod(seg_totais, 60)
        tempo_f = f"{mins:02d}:{segs:02d}"
        c1.markdown(f"<div class='time-display'>⏱️ {tempo_f}</div>", unsafe_allow_html=True)
        if c2.button("🏁 Finalizar"):
            conn = sqlite3.connect('treino_final_v1.db')
            conn.cursor().execute("INSERT INTO sessoes (data, duracao, treino_tipo) VALUES (?, ?, ?)", (datetime.now().strftime("%Y-%m-%d"), tempo_f, treino_sel))
            conn.commit(); conn.close()
            st.session_state.hora_inicio = None
            st.success(f"Treino Finalizado!"); st.balloons()
            time.sleep(1); st.rerun()
        time.sleep(1); st.rerun()

    st.divider()

    conn = sqlite3.connect('treino_final_v1.db')
    df_ex = pd.read_sql(f"SELECT * FROM exercicios WHERE treino='{treino_sel}'", conn)
    conn.close()

    if not df_ex.empty:
        ex_escolhido = st.selectbox("Selecione o Exercício:", df_ex['nome'])
        dados = df_ex[df_ex['nome'] == ex_escolhido].fillna('').iloc[0]
        
        st.markdown(f"<div class='ex-card'><span class='big-emoji'>{dados['emoji']}</span><div class='ex-title'>{dados['nome']}</div></div>", unsafe_allow_html=True)

        n_series = st.number_input("Quantidade de Séries", 1, 10, 4, key=f"nser_{dados['nome']}")

        # Se for exercício combinado (Combo)
        if dados['e1'] != '':
            for i in range(int(n_series)):
                st.markdown(f"#### Série {i+1}")
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**{dados['e1']}**")
                    st.number_input("Peso (kg)", 0.0, 500.0, step=0.5, key=f"p1_{i}_{dados['nome']}")
                    st.number_input("Repetições", 0, 100, 12, key=f"r1_{i}_{dados['nome']}")
                with col2:
                    st.write(f"**{dados['e2']}**")
                    st.number_input("Peso (kg)", 0.0, 500.0, step=0.5, key=f"p2_{i}_{dados['nome']}")
                    st.number_input("Repetições", 0, 100, 12, key=f"r2_{i}_{dados['nome']}")
            
            if st.button("✅ Salvar Todas as Séries do Combo"):
                conn = sqlite3.connect('treino_final_v1.db'); c = conn.cursor(); hoje = datetime.now().strftime("%d/%m/%Y %H:%M")
                for i in range(int(n_series)):
                    c.execute("INSERT INTO logs (data, exercicio, peso, reps, serie_num) VALUES (?, ?, ?, ?, ?)", (hoje, dados['e1'], st.session_state[f"p1_{i}_{dados['nome']}"], st.session_state[f"r1_{i}_{dados['nome']}"], i+1))
                    c.execute("INSERT INTO logs (data, exercicio, peso, reps, serie_num) VALUES (?, ?, ?, ?, ?)", (hoje, dados['e2'], st.session_state[f"p2_{i}_{dados['nome']}"], st.session_state[f"r2_{i}_{dados['nome']}"], i+1))
                conn.commit(); conn.close(); st.success("Combo Salvo!")

        # Se for exercício simples
        else:
            for i in range(int(n_series)):
                c1, c2 = st.columns(2)
                with c1: st.number_input(f"Série {i+1}: Peso (kg)", 0.0, 500.0, step=0.5, key=f"ps_{i}_{dados['nome']}")
                with c2: st.number_input(f"Série {i+1}: Repetições", 0, 100, 10, key=f"rs_{i}_{dados['nome']}")

            if st.button("✅ Salvar Todas as Séries"):
                conn = sqlite3.connect('treino_final_v1.db'); c = conn.cursor(); hoje = datetime.now().strftime("%d/%m/%Y %H:%M")
                for i in range(int(n_series)):
                    c.execute("INSERT INTO logs (data, exercicio, peso, reps, serie_num) VALUES (?, ?, ?, ?, ?)", (hoje, dados['nome'], st.session_state[f"ps_{i}_{dados['nome']}"], st.session_state[f"rs_{i}_{dados['nome']}"], i+1))
                conn.commit(); conn.close(); st.success("Séries Salvas!")

elif menu == "📊 Histórico":
    st.subheader("📈 Histórico de Cargas")
    conn = sqlite3.connect('treino_final_v1.db')
    df_l = pd.read_sql("SELECT data, exercicio, peso, reps, serie_num FROM logs ORDER BY id DESC", conn)
    conn.close()
    if not df_l.empty:
        filtro = st.selectbox("Filtrar Exercício:", ["Todos"] + list(df_l['exercicio'].unique()))
        if filtro != "Todos": df_l = df_l[df_l['exercicio'] == filtro]
        st.dataframe(df_l, use_container_width=True)
