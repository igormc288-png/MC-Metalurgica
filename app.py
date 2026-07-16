import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import json

st.set_page_config(page_title="Diário de Bordo & OEE Metalúrgica", layout="centered")
st.title("📝 Diário de Bordo & OEE Metalúrgica")
st.subheader("Central de Produção, Manutenção e Paradas")

# --- LEITURA DA PLANILHA (SECRETS) ---
try:
    url_planilha = st.secrets["connections"]["spreadsheet"]
    url_csv = url_planilha.replace("/edit?usp=sharing", "/export?format=csv").split("/edit")[0] + "/export?format=csv"
    dados_teste = pd.read_csv(url_csv, nrows=1)
except Exception as e:
    st.error("Erro ao carregar a planilha. Verifique o link em 'spreadsheet' nos Secrets.")
    st.stop()

# --- FORMULÁRIO COM ATUALIZAÇÃO EM TEMPO REAL ---
with st.form("formulario_turno"):
    st.markdown("### 📋 Dados Gerais do Turno")
    
    col1, col2 = st.columns(2)
    with col1:
        maquina = st.selectbox("Selecione a Máquina/Posto:", ["BLM", "EMT", "ZAPROMAQ", "SOLDA","LASER","SERRA"])
        operador = st.text_input("Nome do Operador:")
    with col2:
        turno = st.selectbox("Turno:", ["1º Turno", "2º Turno", "3º Turno", "Turno Geral"])
        data_registro = st.date_input("Data:", datetime.now())

    st.markdown("---")
    st.markdown("### ⏱️ Controle de Tempos (Horas)")
    
    col3, col4, col5 = st.columns(3)
    with col3:
        tempo_total = st.number_input("Tempo Total do Turno (h):", min_value=0.0, step=0.5, value=8.0)
    with col4:
        tempo_producao = st.number_input("Tempo em Produção (h):", min_value=0.0, step=0.5, value=0.0)
    with col5:
        tempo_manutencao = st.number_input("Tempo em Manutenção (h):", min_value=0.0, step=0.5, value=0.0)

    st.markdown("---")
    st.markdown("### 🛑 Detalhes de Paradas")
    
    col6, col7 = st.columns(2)
    with col6:
        hora_parou = st.text_input("Hora que Parou (ex: 10:30):")
    with col7:
        hora_voltou = st.text_input("Hora que Voltou (ex: 11:15):")
        
    motivo_parada = st.selectbox("Motivo Principal da Parada:", [
        "Nenhum (Máquina rodou 100%)", 
        "Setup / Troca de Ferramenta", 
        "Manutenção Corretiva (Quebra)", 
        "Falta de Matéria-Prima", 
        "Falta de Operador", 
        "Aguardando Programação"
    ])

    st.markdown("---")
    st.markdown("### 📦 Produção e Qualidade")
    
    col8, col9 = st.columns(2)
    with col8:
        pecas_produzidas = st.number_input("Quantidade de Peças Boas:", min_value=0, step=1, value=0)
    with col9:
        pecas_perdidas = st.number_input("Quantidade de Refugo (Peças Perdidas):", min_value=0, step=1, value=0)

    # Cálculo em tempo real da porcentagem
    total_pecas = pecas_produzidas + pecas_perdidas
    porcentagem_qualidade = 100.0 if total_pecas == 0 else round((pecas_produzidas / total_pecas) * 100, 2)
    
    st.metric(label="📊 Porcentagem de Qualidade do Lote", value=f"{porcentagem_qualidade}%")

    st.markdown("---")
    observacoes = st.text_area("Descreva detalhes das paradas ou observações:")
    
    submetido = st.form_submit_button("Enviar Registro para a Planilha Central")
    
    if submetido:
        if operador:
            try:
                # Prepara os dados do JSON para envio seguro via Web App
                payload = {
                    "data": str(data_registro),
                    "turno": turno,
                    "maquina": maquina,
                    "operador": operador,
                    "tempo_total": tempo_total,
                    "tempo_producao": tempo_producao,
                    "tempo_manutencao": tempo_manutencao,
                    "hora_parou": hora_parou,
                    "hora_voltou": hora_voltou,
                    "motivo_parada": motivo_parada,
                    "pecas_boas": pecas_produzidas,
                    "refugo": pecas_perdidas,
                    "qualidade": f"{porcentagem_qualidade}%",
                    "observacoes": observacoes
                }
                
                # Envia diretamente ao Web App do Google Sheets
                web_app_url = st.secrets["connections"]["web_app_url"]
                resposta = requests.post(web_app_url, data=json.dumps(payload))
                
                if resposta.status_code == 200:
                    st.success("✨ Registro enviado com sucesso! Os dados entraram na sua planilha central.")
                    st.balloons()
                else:
                    st.error(f"Erro na comunicação com o Google Apps Script. Código: {resposta.status_code}")
            except Exception as erro:
                st.error(f"Erro ao salvar na planilha: {erro}")
        else:
            st.warning("Por favor, preencha o campo do Operador antes de enviar.")
