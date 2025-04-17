from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_mistralai import ChatMistralAI

llm_openai = ChatOpenAI(model="gpt-4o-mini")
llm_mistral = ChatMistralAI(model="mistral-large-latest")
llm_anthropic = ChatAnthropic(model="claude-3-5-haiku-20241022")


messages = [
    SystemMessage(content="Du bist ein hilfreicher Reiseführer."),
    HumanMessage(content="Was ist die Hauptstadt von der Türkei?"),
    # AIMessage(content="Die Hauptstadt von der Türkei ist Ankara."),
]

# -- OpenAI --  

restult_openai = llm_openai.invoke(messages)

print(restult_openai.content)

# -- Anthropic --

restult_anthropic = llm_anthropic.invoke(messages)

print(restult_anthropic.content)

# -- Mistral --

restult_mistral = llm_mistral.invoke(messages)

print(restult_mistral.content)

# docker-compose run --rm app langchain/1_chat_moddels/3_chat_models-alternative_models.py