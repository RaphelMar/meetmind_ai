import os
from src.core import TranscriberAi
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

OUTPUT_PATH = Path(os.getenv("OUTPUT_PATH", ""))

def main():
    print("="*50)
    print("🎙️  BEM-VINDO AO MEETMIND AI (Modo Terminal) 🎙️")
    print("="*50)
    
    # Pede ao utilizador o caminho do ficheiro (pode arrastar o ficheiro para o terminal)
    file_path = input("\nArraste o ficheiro de áudio para aqui e prima ENTER:\n> ").strip()
    
    # Remove aspas caso o terminal adicione ao arrastar o ficheiro
    file_path = file_path.strip("'\"")

    if not os.path.exists(file_path):
        print("Erro: Ficheiro não encontrado! Verifique o caminho.")
        return

    print("\nA iniciar o processamento da reunião...")
    
    try:
        # Instancia a classe e executa
        meeting_ai = TranscriberAi(file_input=file_path)
        resultado_markdown = meeting_ai.execute()
        
        # Guarda o resultado num ficheiro
        agora = datetime.now()
        data_formatada = agora.strftime("%Y-%m-%d-%HT%M")
        output_name = OUTPUT_PATH / f"{data_formatada}.md"
        
        with open(output_name, "w", encoding="utf-8") as f:
            f.write(resultado_markdown)
            
        print("\n" + "="*50)
        print(f"SUCESSO! Relatório guardado como: {output_name}")
        print("="*50 + "\n")
        
    except Exception as e:
        print(f"\n❌ Ocorreu um erro durante a execução: {e}")

if __name__ == "__main__":
    main()