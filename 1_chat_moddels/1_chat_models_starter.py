from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini")

print(llm.invoke("Was ist die Hauptstadt von Österreich?").content)
