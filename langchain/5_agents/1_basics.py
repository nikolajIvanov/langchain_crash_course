from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain import hub
from langchain.agents import create_react_agent, AgentExecutor, tool
from datetime import datetime


model = ChatOpenAI(model="gpt-4o-mini")


query = "What is the current time?"

prompt_template = hub.pull("hwchase17/react")

@tool
def get_current_time():
    """Get the current time"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

tools = [get_current_time]

agent = create_react_agent(model, tools, prompt_template)

agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

result = agent_executor.invoke({"input": query})


# docker-compose run --rm app langchain/5_agents/1_basics.py 