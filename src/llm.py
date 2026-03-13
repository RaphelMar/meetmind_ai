from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

def run_agent(transcript: str, role_prompt: str):
    llm = ChatOllama(model= "llama3.2:3b", temperature= 0.1)
    prompt = ChatPromptTemplate.from_messages([
        ("system", role_prompt),
        ("user", "Texto da Reunião: {text}")
    ])

    chain = prompt | llm | StrOutputParser
    return chain.invoke({"text": transcript}).content

