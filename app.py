import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="Diário de Bordo - Metalúrgica", layout="centered")

st.title("🏭 Diário de Bordo & OEE Metalúrgica")
st.subheader("Central de Produção, Manutenção e Paradas")

# --- CONEXÃO COM O GOOGLE SHEETS ---
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    # Ler os dados existentes para criar o histórico
    dados_existentes = conn.read(ttl=0) # ttl=0 garante que busca o dado mais fresco
except:
    dados_existentes = pd.DataFrame()

# --- ENTRADA DE DADOS (MENU LATERAL) ---
st.sidebar.header("📋 Registro do Turno")
maquina = st.sidebar.selectbox("Selecione a Máquina/Posto", ["BLM", "EMT", "LASER", "ZAPROMAQ", "SOLDA","SERRA"])
operador = st.sidebar.text_input("Nome do Operador")

st.sidebar.divider()

st.sidebar.subheader("⏱️ Tempos")
tempo_total = st.sidebar.number_input("Tempo Total do Turno (Horas)", min_value=1.0, max_value=24.0, value=8.0, step=0.5)
tempo_producao = st.sidebar.number_input("Tempo em Produção (Horas)", min_value=0.0, max_value=24.0, value=5.5, step=0.5)
tempo_manutencao = st.sidebar.number_input("Tempo em Manutenção (Horas)", min_value=0.0, max_value=24.0, value=1.5, step=0.5)

st.sidebar.subheader("🛠️ Motivo da Parada/Manutenção")
motivo = st.sidebar.selectbox("Principal motivo de parada:", [
    "Nenhum (Máquina rodou 100%)", "Manutenção Corretiva (Quebra)", 
    "Manutenção Preventiva", "Setup / Troca de Ferramenta", 
    "Falta de Matéria-Prima", "Ajuste de Processo / Regulagem"
])

st.sidebar.divider()

st.sidebar.subheader("🔢 Produção de Peças")
pecas_boas = st.sidebar.number_input("Peças Boas Aprovadas (Qtd)", min_value=0, value=120, step=1)
pecas_refugo = st.sidebar.number_input("Peças Refugadas/Sucata (Qtd)", min_value=0, value=5, step=1)

# --- CÁLCULOS ---
tempo_ocioso = tempo_total - (tempo_producao + tempo_manutencao)
total_pecas = pecas_boas + pecas_refugo

if tempo_ocioso < 0:
    st.error("🚨 Erro: A soma do tempo de produção e manutenção ultrapassa o tempo total do turno!")
else:
    p_producao = (tempo_producao / tempo_total) * 100
    p_manutencao = (tempo_manutencao / tempo_total) * 100
    p_ocioso = (tempo_ocioso / tempo_total) * 100
    p_qualidade = (pecas_boas / total_pecas * 100) if total_pecas > 0 else 0.0

    # --- INDICADORES ---
    col1, col2, col3 = st.columns(3)
    col1.metric("Disponibilidade", f"{p_producao:.1f}%", f"{tempo_producao}h")
    col2.metric("Qualidade", f"{p_qualidade:.1f}%", f"-{pecas_refugo} refugo(s)", delta_color="inverse")
    col3.metric("Manutenção/Parada", f"{p_manutencao:.1f}%", f"{tempo_manutencao}h", delta_color="off")

    st.divider()

    # --- GRÁFICO ---
    st.write("### 📊 Distribuição do Tempo")
    labels = ['Produção', 'Manutenção', 'Ocioso']
    tamanhos = [p_producao, p_manutencao, p_ocioso]
    cores = ['#2ecc71', '#e74c3c', '#f1c40f']
    explode = (0.05, 0, 0)

    labels_f = [labels[i] for i in range(3) if tamanhos[i] > 0]
    tamanhos_f = [tamanhos[i] for i in range(3) if tamanhos[i] > 0]
    cores_f = [cores[i] for i in range(3) if tamanhos[i] > 0]

    fig, ax = plt.subplots(figsize=(5, 4))
    ax.pie(tamanhos_f, explode=explode[:len(tamanhos_f)], labels=labels_f, autopct='%1.1f%%',
           shadow=False, startangle=140, colors=cores_f, textprops={'fontsize': 10})
    ax.axis('equal')
    st.pyplot(fig)

    st.divider()
    observacoes = st.text_area("📝 Descreva detalhes das paradas ou observações do funcionário:")

    # --- BOTÃO DE SALVAR NA PLANILHA CENTRAL ---
    if st.button("💾 Enviar Registro para a Planilha Central"):
        novos_dados = pd.DataFrame([{
            "Data/Hora": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "Máquina": maquina, "Operador": operador if operador else "Não Informado", 
            "Tempo Total (h)": tempo_total, "Tempo Produção (h)": tempo_producao, 
            "Tempo Manutenção (h)": tempo_manutencao, "Tempo Ocioso (h)": tempo_ocioso, 
            "Motivo da Parada": motivo, "Peças Boas": pecas_boas, "Refugo": pecas_refugo, 
            "Qualidade (%)": round(p_qualidade, 2), "Observações": observacoes
        }])
        
        # Combinar dados antigos com os novos e atualizar o Google Sheets
        df_atualizado = pd.concat([dados_existentes, novos_dados], ignore_index=True)
        conn.update(spreadsheet=st.secrets["connections"]["gsheets"]["spreadsheet"], data=df_atualizado)
        st.success("✅ Enviado com sucesso! Dados consolidados na nuvem.")
        st.rerun()

    # --- VISUALIZAÇÃO DO HISTÓRICO GLOBAL ---
    st.divider()
    st.write("### 📜 Histórico Consolidado de Todos os Aparelhos")
    if not dados_existentes.empty:
        st.dataframe(dados_existentes, use_container_width=True)
    else:
        st.info("Aguardando os primeiros registros dos operadores.")
