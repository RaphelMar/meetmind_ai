import streamlit as st
import os
from src.core import TranscriberAi

# Configuração da página
st.set_page_config(page_title="MeetMind AI", page_icon="🎙️", layout="wide")

# ==========================================
# Task 13: Layout Streamlit (Sidebar)
# ==========================================
with st.sidebar:
    st.title("🎙️ MeetMind AI")
    st.markdown("---")
    st.write("Faça o upload do arquivo de áudio ou vídeo da sua reunião para gerar automaticamente:")
    st.markdown("""
    - **Sumário Executivo**
    - **Ata Detalhada**
    - **Plano de Ação**
    """)
    st.markdown("---")
    st.info("Formatos suportados: .mp3, .ogg, .wav, .m4a, .mp4")

# ==========================================
# Task 13: Layout Streamlit (Area de Upload)
# ==========================================
st.title("Gerador de Atas e Relatórios")
st.write("Transforme as gravações das suas reuniões em documentos acionáveis.")

# Área de Upload
uploaded_file = st.file_uploader(
    "Arraste ou selecione o arquivo da reunião", 
    type=["mp3", "ogg", "wav", "m4a", "mp4"]
)

if uploaded_file is not None:
    # Botão para iniciar o processamento
    if st.button("Processar Reunião", type="primary"):
        
        # Cria a pasta temporária se não existir (ignorada no seu .gitignore)
        temp_dir = "temp"
        os.makedirs(temp_dir, exist_ok=True)
        
        # Salva o arquivo em disco temporariamente para o TranscriberAi poder ler
        temp_file_path = os.path.join(temp_dir, uploaded_file.name)
        with open(temp_file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
            
        # Feedback visual de carregamento
        with st.spinner("Transcrevendo áudio e gerando os relatórios com IA... Isso pode levar alguns minutos."):
            try:
                # Instancia sua classe do core.py
                meeting_ai = TranscriberAi(file_input=temp_file_path)
                
                # Executa o pipeline (conversão, transcrição e agentes)
                result_markdown = meeting_ai.execute()
                
                st.success("Processamento concluído com sucesso!")
                
                # ==========================================
                # Task 14: Visualização do Markdown final
                # ==========================================
                st.markdown("---")
                st.subheader("Visualização do Relatório")
                # Container para ficar visualmente separado
                with st.container(border=True):
                    st.markdown(result_markdown)
                
                # ==========================================
                # Task 15: Botão de Download (st.download_button)
                # ==========================================
                st.markdown("---")
                st.download_button(
                    label="📥 Baixar Relatório Completo (.md)",
                    data=result_markdown,
                    file_name=f"relatorio_{uploaded_file.name}.md",
                    mime="text/markdown"
                )
                
            except Exception as e:
                st.error(f"Ocorreu um erro durante o processamento: {str(e)}")
                
            finally:
                # Limpeza do arquivo temporário original enviado pelo usuário
                if os.path.exists(temp_file_path):
                    os.remove(temp_file_path)