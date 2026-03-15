from src.prompts import SystemPrompt
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

import time
from datetime import timedelta

def run_agent(transcript: str, role_prompt: str):
    llm = ChatOllama(model="llama3.2:3b", temperature=0.1, num_ctx=32768, num_gpu= 999)

    # System prompt e chain de execução
    prompt = ChatPromptTemplate.from_messages([
        ("system", role_prompt),
        ("user", "Texto da Reunião: {text}")
    ])
    chain = prompt | llm | StrOutputParser()

    inicio = time.time()

    result = chain.invoke({"text": transcript})

    fim = time.time()
    tempo_decorrido = fim - inicio
    formato_final = str(timedelta(seconds=int(tempo_decorrido)))
    print(f"Tempo de execução Agente: {formato_final}")

    return result

inicio = time.time()

with open("transcricao_bruta.txt", "r") as file:
    conteudo = file.read()

executive_summary = run_agent(transcript=conteudo, role_prompt=SystemPrompt.agent_executive_summary())
meeting_minutes = run_agent(transcript=conteudo, role_prompt=SystemPrompt.agent_ata())
action_plan = run_agent(transcript=conteudo, role_prompt=SystemPrompt.agent_action_plan())



fim = time.time()
tempo_decorrido = fim - inicio
formato_final = str(timedelta(seconds=int(tempo_decorrido)))

print(f"\n\nTempo de execução: {formato_final}\n\n")

print(
    f"""
    # Relatório de Reunião MeetMind AI
    ## Sumário Executivo
    {executive_summary}

    ---

    ## Ata Detalhada
    {meeting_minutes}

    ---

    ## Plano de Ação e Tarefas
    {action_plan}
    """
)