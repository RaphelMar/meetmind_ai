from src.prompts import SystemPrompt
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


INPUT_TRANSCRIPT = "temp/teste.txt"


def run_agent(transcript: str, role_prompt: str, llm_instance):
    """
    Run a single LangChain agent
    Parameters
    ----------
    transcript: str
        The meeting transcript.
    role_prompt: str
        System prompt for the specific agent.
    llm_instance: ChatOllama
        Pre‑instantiated LLM client (singleton).
    """
    # System prompt and chain creation – keep exact pattern
    prompt = ChatPromptTemplate.from_messages([
        ("system", role_prompt),
        ("user", "Texto da Reunião: {text}")
    ])

    chain = prompt | llm_instance | StrOutputParser()

    return chain.invoke({"text": transcript})

def generate_reports(transcript: str):
    """
    Generate executive summary, minutes, and action plan concurrently.
    Returns a tuple (executive_summary, meeting_minutes, action_plan).
    """
    # Instantiate the LLM once (singleton for this run)
    llm = ChatOllama(model="gemma3n:e4b", temperature=0.1, num_ctx=32768, num_gpu=999)

    # Cleaning the raw text of the transcription performed for other agents.
    clean_transcript = run_agent(transcript, SystemPrompt.agent_ata(), llm)

    # Preparing the documents: Executive Summary, Minutes, and Action Plan
    #executive_summary = run_agent(clean_transcript, SystemPrompt.agent_executive_summary(), llm)
    #meeting_minutes = run_agent(clean_transcript, SystemPrompt.agent_ata(), llm)
    #action_plan = run_agent(clean_transcript, SystemPrompt.agent_action_plan(), llm)

    return clean_transcript

if __name__ == "__main__":

    with open(INPUT_TRANSCRIPT, "r") as file:
        transcript = file.read()

    print(generate_reports(transcript))