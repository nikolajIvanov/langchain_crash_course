from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

# Beispiel 1: Prompt Template mit einem Human Message

llm = ChatOpenAI(model="gpt-4o-mini")

template = "Gib mir eine kurze Erklärung zu {subject}"

prompt_template = ChatPromptTemplate.from_template(template)

prompt = prompt_template.invoke({"subject": "LLMOps"})

result = llm.invoke(prompt)

print(result.content)

# Beispiel 2: Prompt Template mit System Message und Human Message (Tuples)

messages = [
    ("system", "Du bist ein KI Experte für {topic}."),
    ("human", "Gib mir {number} Informationen über {topic}."),
]

prompt_template = ChatPromptTemplate.from_messages(messages)

prompt = prompt_template.invoke({"topic": "LLMOps", "number": 3})

result = llm.invoke(prompt)

print(result.content)

# docker-compose run --rm app langchain/2_prompt_templates/1_prompt_templates_starter.py