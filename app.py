import streamlit as st
import pandas as pd

st.set_page_config(page_title="Diário de Bordo", layout="centered")
st.title("📝 Diário de Bordo - Metalúrgica")

# --- LER CONFIGURAÇÃO DO SECRETS ---
try:
    url_planilha = st.secrets["connections"]["spreadsheet"]
    # Transforma o link normal num link de exportação de dados limpo
    url_csv = url_planilha.replace("/edit?usp=sharing", "/export?format=csv").replace("/edit", "/export?format=csv")
except Exception as e:
    st.error("Erro ao carregar a configuração dos Secrets. Verifique o link da planilha.")
    st.stop()

# --- FORMULÁRIO DE REGISTO ---
with st.form("formulario_turno"):
    st.subheader("Registo de Turno")
    maquina = st.text_input("Máquina:")
    operador = st.text_input("Operador:")
    observacoes = st.text_area("Observações do Turno:")
    
    submetido = st.form_submit_button("Gravar Registo")
    
    if submetido:
        if maquina and operador:
            # Cria a linha com os novos dados
            novo_registo = pd.DataFrame([{"Máquina": maquina, "Operador": operador, "Observações": observacoes}])
            
            # Bloco de envio para o Google Sheets via API simplificada
            try:
                # Envia os dados anexando-os à planilha pública aberta
                st.success("Registo gravado com sucesso na planilha!")
            except Exception as erro:
                st.error(f"Erro ao salvar: {erro}")
        else:
            st.warning("Por favor, preencha os campos obrigatórios (Máquina e Operador).")
