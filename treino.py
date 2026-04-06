import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import time

# Configuração da página
st.set_page_config(page_title="PowerLog PRO", page_icon="💪", layout="centered")

# Estilo CSS Slim
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
    conn = sqlite3.connect('treino_final_v2.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS exercicios (id INTEGER PRIMARY KEY, treino TEXT, emoji TEXT, nome TEXT, e1 TEXT, e2 TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS logs (id INTEGER PRIMARY KEY, data TEXT, exercicio TEXT, peso REAL, reps INTEGER, serie_num INTEGER)''')
    c.execute('''CREATE TABLE IF NOT EXISTS sessoes (id INTEGER PRIMARY KEY, data TEXT, duracao TEXT, treino_tipo TEXT)''')
    
    c.execute("SELECT count(*) FROM exercicios")
    if c.fetchone()[0] == 0:
        exercicios_completos = [
            ('A', '🔥', 'Supino Inclinado + Crucifixo Inclinado', 'Supino Inclinado (Halter)', 'Crucifixo Inclinado (Halter)'),
            ('A', '🔋', 'Pulôver + Desenvolvimento', 'Pulôver (Halter)', 'Desenvolvimento (Halter)'),
            ('A', '🎯', 'Supino Reto com Halteres', '', ''),
            ('A', '💀', 'Tríceps Testa com Halteres', '', ''),
            ('A', '💪', 'Tríceps Francês com Halteres', '', ''),
            ('B', '⏱️', 'Extensora Isométrica', '', ''),
            ('B', '🦵', 'Extensora', '', ''),
            ('B', '🚀', 'Leg Press Pés Afastados', '', ''),
            ('B', '🦶', 'Panturrilha no Leg Press', '', ''),
            ('B', '💥', 'Leg Press Horizontal Unilateral', '', ''),
            ('B', '🎢', 'Cadeira Flexora', '', ''),
            ('B', '⏱️', 'Flexora Isometria', '', ''),
            ('C', '🛶', 'Remada Curvada + Rosca Alternada', 'Remada Curvada (Barra)', 'Rosca Alternada (Halter)'),
            ('C', '⚔️', 'Remada Unilateral + Rosca Direta', 'Remada Unilateral (Halter)', 'Rosca Direta (Halter)'),
            ('C', '⛓️', 'Remada Fechada com Barra Reta', '', ''),
            ('C', '🔨', 'Rosca Martelo com Halteres', '', ''),
            ('C', '🎯', 'Rosca Concentrada', '', ''),
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
menu = st.sidebar.selectbox("Navegação", ["🏋️ Treinar Agora", "📊 Histórico", "🆕 Gerenciar Treinos"])

if menu == "🏋️ Treinar Agora":
    # Carregar treinos dinamicamente do banco de dados
    conn = sqlite3.connect('treino_final_v2.db')
    lista_treinos = pd.read_sql("SELECT DISTINCT treino FROM exercicios", conn)['treino'].tolist()
    conn.close()
    
    treino_sel = st.radio("Selecione o Treino:", sorted(lista_treinos), horizontal=True)

    if st.session_state.hora_inicio:
        seg_totais = int(time.time() - st.session_state.hora_inicio)
        tempo_f = f"{seg_totais//60:02d}:{seg_totais%60:02d}"
        st.markdown(f"<div class='time-display'>⏱️ {tempo_f}</div>", unsafe_allow_html=True)
        
        # Botão Encerrar que aparece apenas quando o treino está ativo
        if st.button("🏁 ENCERRAR TREINO"):
            conn = sqlite3.connect('treino_final_v2.db')
            conn.cursor().execute("INSERT INTO sessoes (data, duracao, treino_tipo) VALUES (?, ?, ?)", 
                                (datetime.now().strftime("%Y-%m-%d"), tempo_f, treino_sel))
            conn.commit(); conn.close()
            st.session_state.hora_inicio = None
            st.success("Treino guardado!")
            st.rerun()
        time.sleep(1)
        st.rerun()
    else:
        if st.button("▶️ INICIAR TREINO"):
            st.session_state.hora_inicio = time.time()
            st.rerun()

    st.divider()

    conn = sqlite3.connect('treino_final_v2.db')
    df_ex = pd.read_sql(f"SELECT * FROM exercicios WHERE treino='{treino_sel}'", conn)
    conn.close()

    if not df_ex.empty:
        ex_escolhido = st.selectbox("Selecione o Exercício:", df_ex['nome'])
        dados = df_ex[df_ex['nome'] == ex_escolhido].fillna('').iloc[0]
        
        st.markdown(f"<div class='ex-card'><span class='big-emoji'>{dados['emoji']}</span><div class='ex-title'>{dados['nome']}</div></div>", unsafe_allow_html=True)

        n_series = st.number_input("Quantidade de Séries", 1, 10, 4)

        if dados['e1'] != '':
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**{dados['e1']}**")
                p1 = st.number_input("Peso (kg)", 0.0, 500.0, step=0.5, key="p1")
                r1 = st.number_input("Repetições", 0, 100, 12, key="r1")
            with col2:
                st.write(f"**{dados['e2']}**")
                p2 = st.number_input("Peso (kg)", 0.0, 500.0, step=0.5, key="p2")
                r2 = st.number_input("Repetições", 0, 100, 12, key="r2")
            
            if st.button(f"✅ Salvar {n_series} Séries do Combo"):
                conn = sqlite3.connect('treino_final_v2.db'); c = conn.cursor(); hoje = datetime.now().strftime("%d/%m/%Y %H:%M")
                for i in range(int(n_series)):
                    c.execute("INSERT INTO logs (data, exercicio, peso, reps, serie_num) VALUES (?, ?, ?, ?, ?)", (hoje, dados['e1'], p1, r1, i+1))
                    c.execute("INSERT INTO logs (data, exercicio, peso, reps, serie_num) VALUES (?, ?, ?, ?, ?)", (hoje, dados['e2'], p2, r2, i+1))
                conn.commit(); conn.close(); st.success("Séries salvas!")
        else:
            c1, c2 = st.columns(2)
            with c1: p = st.number_input("Peso (kg)", 0.0, 500.0, step=0.5)
            with c2: r = st.number_input("Repetições", 0, 100, 10)

            if st.button(f"✅ Salvar {n_series} Séries"):
                conn = sqlite3.connect('treino_final_v2.db'); c = conn.cursor(); hoje = datetime.now().strftime("%d/%m/%Y %H:%M")
                for i in range(int(n_series)):
                    c.execute("INSERT INTO logs (data, exercicio, peso, reps, serie_num) VALUES (?, ?, ?, ?, ?)", (hoje, dados['nome'], p, r, i+1))
                conn.commit(); conn.close(); st.success("Séries salvas!")

elif menu == "🆕 Gerenciar Treinos":
    st.subheader("Adicionar Novo Exercício")
    with st.form("novo_exercicio"):
        t_id = st.text_input("Identificador do Treino (Ex: E, F, G)", placeholder="E")
        t_emoji = st.text_input("Emoji", value="💪")
        t_nome = st.text_input("Nome do Exercício ou Combo")
        
        st.info("Deixe os campos abaixo vazios se não for um Combo")
        t_e1 = st.text_input("Exercício 1 (Se combo)")
        t_e2 = st.text_input("Exercício 2 (Se combo)")
        
        if st.form_submit_button("➕ Adicionar ao Plano"):
            if t_id and t_nome:
                conn = sqlite3.connect('treino_final_v2.db')
                conn.cursor().execute("INSERT INTO exercicios (treino, emoji, nome, e1, e2) VALUES (?, ?, ?, ?, ?)", 
                                    (t_id.upper(), t_emoji, t_nome, t_e1, t_e2))
                conn.commit(); conn.close()
                st.success(f"Exercício '{t_nome}' adicionado ao Treino {t_id.upper()}!")
            else:
                st.error("Preencha o Identificador e o Nome.")

elif menu == "📊 Histórico":
    st.subheader("📈 Histórico de Cargas")
    conn = sqlite3.connect('treino_final_v2.db')
    df_l = pd.read_sql("SELECT data, exercicio, peso, reps, serie_num FROM logs ORDER BY id DESC", conn)
    conn.close()
    if not df_l.empty:
        filtro = st.selectbox("Filtrar Exercício:", ["Todos"] + list(df_l['exercicio'].unique()))
        if filtro != "Todos": df_l = df_l[df_l['exercicio'] == filtro]
        st.dataframe(df_l, use_container_width=True)
