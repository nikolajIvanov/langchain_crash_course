from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini")

print(llm.invoke("Was ist die Hauptstadt von Österreich?").content)

