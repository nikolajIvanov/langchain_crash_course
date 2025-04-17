from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini")

print(llm.invoke("Was ist die Hauptstadt von Österreich?").content)

# docker-compose run --rm app langchain/1_chat_moddels/1_chat_models_starter.py