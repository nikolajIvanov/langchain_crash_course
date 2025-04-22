from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import initialize_agent, AgentType, tool
from langchain_community.tools import DuckDuckGoSearchRun, TavilySearchResults
import os
from datetime import datetime
llm = ChatOpenAI(model="gpt-4o-mini")

# Angepasster Modellname - gemini-2.5.pro-exp-03-25 ist nicht mehr verfügbar
# Verwende stattdessen ein stabiles und verfügbares Modell
llm_google = ChatGoogleGenerativeAI(model="gemini-1.5-pro")

search = TavilySearchResults(api_key=os.getenv("TAVILY_API_KEY"))
search_duckduckgo = DuckDuckGoSearchRun()

@tool
def get_system_time(format: str = "%Y-%m-%d %H:%M:%S"):
    """Gibt das aktuelle Systemdatum und die Uhrzeit in der angegebenen Formatierung zurück."""
    return datetime.now().strftime(format)

agent = initialize_agent(tools=[search, get_system_time], llm=llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True)

agent.invoke({"input": "Wann ist die letzte SpaceX Rakete gestartet und wie viele Tage ist es von heute her?"})

"""
result = llm_google.invoke("Was ist die Hauptstadt von Deutschland?")

print(result.content) 

orbit it solutions
"""
# docker-compose run --rm app langgraph/1_Introduction/react_agent_basic.py 