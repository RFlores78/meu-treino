import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
import time
from streamlit_calendar import calendar

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
    .metric-box { background: #f0f2f6; padding: 10px; border-radius: 10px; text-align: center; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

def init_db():
    conn = sqlite3.connect('treino_final_v2.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS exercicios (id INTEGER PRIMARY KEY, treino TEXT, emoji TEXT, nome TEXT, e1 TEXT, e2 TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS logs (id INTEGER PRIMARY KEY, data TEXT, exercicio TEXT, peso REAL, reps INTEGER, serie_num INTEGER)''')
    c.execute('''CREATE TABLE IF NOT EXISTS sessoes (id INTEGER PRIMARY KEY, data TEXT, duracao TEXT, treino_tipo TEXT)''')
    conn.commit()
    conn.close()

init_db()

if 'hora_inicio' not in st.session_state: st.session_state.hora_inicio = None

st.title("⚡ PowerLog PRO")
menu = st.sidebar.selectbox("Navegação", ["🏋️ Treinar Agora", "📊 Histórico", "🆕 Gerenciar Treinos"])

if menu == "🏋️ Treinar Agora":
    conn = sqlite3.connect('treino_final_v2.db')
    lista_treinos = pd.read_sql("SELECT DISTINCT treino FROM exercicios", conn)['treino'].tolist()
    conn.close()
    
    treino_sel = st.radio("Selecione o Treino:", sorted(lista_treinos) if lista_treinos else ["A"], horizontal=True)

    if st.session_state.hora_inicio:
        seg_totais = int(time.time() - st.session_state.hora_inicio)
        tempo_f = f"{seg_totais//60:02d}:{seg_totais%60:02d}"
        st.markdown(f"<div class='time-display'>⏱️ {tempo_f}</div>", unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button("🔄 Atualizar Tempo"): st.rerun()
        with c2:
            if st.button("🏁 ENCERRAR TREINO"):
                conn = sqlite3.connect('treino_final_v2.db')
                conn.cursor().execute("INSERT INTO sessoes (data, duracao, treino_tipo) VALUES (?, ?, ?)", 
                                    (datetime.now().strftime("%Y-%m-%d"), tempo_f, treino_sel))
                conn.commit(); conn.close()
                st.session_state.hora_inicio = None
                st.success("Treino encerrado!")
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
                p1 = st.number_input("Peso (kg)", 0.0, 500.0, step=0.5, key=f"p1_{ex_escolhido}")
                r1 = st.number_input("Repetições", 0, 100, 12, key=f"r1_{ex_escolhido}")
            with col2:
                st.write(f"**{dados['e2']}**")
                p2 = st.number_input("Peso (kg)", 0.0, 500.0, step=0.5, key=f"p2_{ex_escolhido}")
                r2 = st.number_input("Repetições", 0, 100, 12, key=f"r2_{ex_escolhido}")
            
            if st.button(f"✅ Salvar {n_series} Séries"):
                conn = sqlite3.connect('treino_final_v2.db'); c = conn.cursor(); hoje = datetime.now().strftime("%d/%m/%Y %H:%M")
                for i in range(int(n_series)):
                    c.execute("INSERT INTO logs (data, exercicio, peso, reps, serie_num) VALUES (?, ?, ?, ?, ?)", (hoje, dados['e1'], p1, r1, i+1))
                    c.execute("INSERT INTO logs (data, exercicio, peso, reps, serie_num) VALUES (?, ?, ?, ?, ?)", (hoje, dados['e2'], p2, r2, i+1))
                conn.commit(); conn.close(); st.success("Salvo!")
        else:
            c1, c2 = st.columns(2)
            with c1: p = st.number_input("Peso (kg)", 0.0, 500.0, step=0.5, key=f"p_{ex_escolhido}")
            with c2: r = st.number_input("Repetições", 0, 100, 10, key=f"r_{ex_escolhido}")

            if st.button(f"✅ Salvar {n_series} Séries"):
                conn = sqlite3.connect('treino_final_v2.db'); c = conn.cursor(); hoje = datetime.now().strftime("%d/%m/%Y %H:%M")
                for i in range(int(n_series)):
                    c.execute("INSERT INTO logs (data, exercicio, peso, reps, serie_num) VALUES (?, ?, ?, ?, ?)", (hoje, dados['nome'], p, r, i+1))
                conn.commit(); conn.close(); st.success("Salvo!")

elif menu == "🆕 Gerenciar Treinos":
    st.subheader("Adicionar Novo Exercício")
    with st.form("novo_exercicio"):
        t_id = st.text_input("Treino (Ex: E, F)", placeholder="E")
        t_emoji = st.text_input("Emoji", value="💪")
        t_nome = st.text_input("Nome do Exercício/Combo")
        t_e1 = st.text_input("Exercício 1 (Se combo)")
        t_e2 = st.text_input("Exercício 2 (Se combo)")
        if st.form_submit_button("➕ Adicionar"):
            if t_id and t_nome:
                conn = sqlite3.connect('treino_final_v2.db')
                conn.cursor().execute("INSERT INTO exercicios (treino, emoji, nome, e1, e2) VALUES (?, ?, ?, ?, ?)", (t_id.upper(), t_emoji, t_nome, t_e1, t_e2))
                conn.commit(); conn.close()
                st.success("Adicionado!")
            else: st.error("Preencha os campos!")

elif menu == "📊 Histórico":
    conn = sqlite3.connect('treino_final_v2.db')
    df_l = pd.read_sql("SELECT * FROM logs", conn)
    df_s = pd.read_sql("SELECT * FROM sessoes", conn)
    conn.close()

    tab1, tab2, tab3 = st.tabs(["🗓️ Calendário", "📈 Evolução de Carga", "📋 Tabela de Logs"])

    with tab1:
        st.subheader("Dias de Treino")
        eventos = []
        if not df_s.empty:
            for _, row in df_s.iterrows():
                eventos.append({
                    "title": f"💪 {row['treino_tipo']}",
                    "start": row['data'],
                    "display": 'background',
                    "backgroundColor": "#007bff"
                })
        
        # Calendário traduzido para Português
        calendar(
            events=eventos, 
            options={
                "locale": "pt-br",
                "headerToolbar": {"left": "prev,next today", "center": "title", "right": ""},
                "buttonText": {"today": "Hoje"}
            }
        )
        
        st.divider()
        if not df_s.empty:
            df_s['data_dt'] = pd.to_datetime(df_s['data'])
            hoje = datetime.now()
            
            def stats_periodo(df, dias):
                filtro = df[df['data_dt'] > (hoje - timedelta(days=dias))]
                minutos = sum(int(t.split(':')[0]) for t in filtro['duracao'])
                dias_treinados = filtro['data'].nunique()
                return minutos, dias_treinados

            m_sem, d_sem = stats_periodo(df_s, 7)
            m_mes, d_mes = stats_periodo(df_s, 30)
            m_ano, d_ano = stats_periodo(df_s, 365)

            # Exibição com Minutos e Dias conforme solicitado
            c1, c2, c3 = st.columns(3)
            c1.markdown(f"<div class='metric-box'>Semana<br>{m_sem} min<br>{d_sem} dias</div>", unsafe_allow_html=True)
            c2.markdown(f"<div class='metric-box'>Mês<br>{m_mes} min<br>{d_mes} dias</div>", unsafe_allow_html=True)
            c3.markdown(f"<div class='metric-box'>Ano<br>{m_ano} min<br>{d_ano} dias</div>", unsafe_allow_html=True)
            
    with tab2:
        st.subheader("Evolução de Peso")
        if not df_l.empty:
            ex_f = st.selectbox("Selecione o exercício:", sorted(df_l['exercicio'].unique()))
            df_evol = df_l[df_l['exercicio'] == ex_f].copy()
            df_evol['data_dt'] = pd.to_datetime(df_evol['data'], format="%d/%m/%Y %H:%M")
            st.line_chart(df_evol.sort_values('data_dt').set_index('data_dt')['peso'])

    with tab3:
        if not df_l.empty:
            st.subheader("📋 Resumo por Exercício")
            
            # Criando o DataFrame de exibição agrupado
            df_grouped = df_l.copy()
            
            # Agrupamos por Data e Exercício para contar as séries e pegar os valores
            # Usamos 'max' para peso e reps pois você confirmou que são iguais em todas as séries
            df_resumo = df_grouped.groupby(['data', 'exercicio']).agg({
                'serie_num': 'count',
                'peso': 'max',
                'reps': 'max'
            }).reset_index()
            
            # Ordenar pelo mais recente (assumindo formato de data string DD/MM/YYYY HH:MM)
            df_resumo['data_dt'] = pd.to_datetime(df_resumo['data'], format="%d/%m/%Y %H:%M")
            df_resumo = df_resumo.sort_values('data_dt', ascending=False)
            
            # Filtro
            lista_ex = ["Todos"] + sorted(list(df_resumo['exercicio'].unique()))
            filtro = st.selectbox("Filtrar exercício:", lista_ex, key="filtro_resumo")
            
            if filtro != "Todos":
                df_resumo = df_resumo[df_resumo['exercicio'] == filtro]

            st.dataframe(
                df_resumo,
                column_order=("data", "exercicio", "serie_num", "peso", "reps"),
                column_config={
                    "data": st.column_config.TextColumn("📅 Data"),
                    "exercicio": st.column_config.TextColumn("🏋️ Exercício"),
                    "serie_num": st.column_config.NumberColumn("🔢 Séries Totais"),
                    "peso": st.column_config.NumberColumn("⚖️ Carga", format="%.1f kg"),
                    "reps": st.column_config.NumberColumn("🔁 Reps/Série", format="%d reps"),
                },
                hide_index=True,
                use_container_width=True
            )
        else:
            st.info("Ainda não há registros para resumir.")
