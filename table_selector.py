import json
from openai import OpenAI
import re
import pandas as pd
import psycopg2

from db_connector import execute_sql_query

client = OpenAI(
    base_url = 'http://localhost:11434/v1',
    api_key='ollama', # required, but unused
)


data1 = []
# Read JSONL file line by line
with open('table_description.jsonl', 'r') as file:
    for line in file:
        # Parse JSON from each line
        data = json.loads(line)
        
        # Access and print the content of each JSON object
        for key, value in data.items():
            # print(f"{key}: {value}")
            data1.append(f"{key}: {value}")
            # Add any additional processing logic as needed
            # print("\n")  # Separate each JSON object with a newline   
# print(data1)
        
query = "give me the list of credit card in USD"
# prompt_str1 = f"Given the data below, return me the python list of table names only, dont give a summary just the names which could hold the potential answer to the query: {query}':\n answer format: ['table 1', 'table 2', ..]\n\n {data1}\n\n"

prompt_str1 = f"{data1} \n\n Query: Given the data above, return me a list of table names that could potentially answer the query given by '{query}'. If one table cannot seem to give a response, you can include more number of tables. "
# prompt_str1 = f"Given the data below, return me the list of table names, which could hold the potential answer to the query: {query}':\n 'NEW DELHI IS THE CAPITAL OF INDIA?'"


# print(prompt_str1)

response = client.chat.completions.create(
    model="mistral",
    messages=[
        {"role": "system", "content": "You are a helpful assistant. Answer with a list of python list."},
        {"role": "user", "content": prompt_str1}
    ]
)

output = response.choices[0].message.content

print("OUTPUT:", output)


# from openai import OpenAI

# client = OpenAI(
#     base_url = 'http://localhost:11434/v1',
#     api_key='ollama', # required, but unused
# )

# response = client.embeddings(model='mxbai-embed-large', prompt='Represent this sentence for searching relevant passages: The sky is blue because of Rayleigh scattering')
# print(response)

# response = client.chat.completions.create(
#   model="mistral",
#   messages=[
#     {"role": "system", "content": "You are a helpful assistant."},
#     {"role": "user", "content": "Who won the world series in 2020?"},
#     {"role": "assistant", "content": "The LA Dodgers won in 2020."},
#     {"role": "user", "content": "Where was it played?"}
#   ]
# )
# print(response.choices[0].message.content)

# from langchain_community.document_loaders import WebBaseLoader
# from langchain_community.document_loaders import PyPDFLoader
# from langchain_community.vectorstores import Chroma
# from langchain_community import embeddings
# from langchain_community.chat_models import ChatOllama
# from langchain_core.runnables import RunnablePassthrough
# from langchain_core.output_parsers import StrOutputParser
# from langchain_core.prompts import ChatPromptTemplate
# from langchain.output_parsers import PydanticOutputParser
# from langchain.text_splitter import CharacterTextSplitter

# model_local = ChatOllama(model="mistral")

# doc_splits= [{"account": "The 'account' table in the 'VyttahMasters' dataset serves as a comprehensive repository for various account details, including IDs, types, contact information, creation/modification timestamps, and status indicators. Additionally, it includes references to related tables for additional context, like country details and compliance information, providing a thorough overview of managed accounts."},
# {"account_category": "The 'account_category' table in the 'VyttahMasters' dataset stores information related to different categories of accounts. It includes columns such as 'code' for the account category code, 'description' for any additional details, 'is_active' to indicate the active status, and 'deleted' to mark if the category has been removed. Additionally, it tracks metadata like creation and last modification timestamps, along with references to the company and user who created or modified the category."}]

# vectorstore = Chroma.from_documents(
#     documents=doc_splits,
#     collection_name="rag-chroma",
#     embedding=embeddings.OllamaEmbeddings(model='nomic-embed-text'),
# )
# retriever = vectorstore.as_retriever()

# print("\n########\nAfter RAG\n")
# after_rag_template = """Just give me the names of the tables in a list format:
# {context}
# Question: {question}
# """
# after_rag_prompt = ChatPromptTemplate.from_template(after_rag_template)
# after_rag_chain = (
#     {"context": retriever, "question": RunnablePassthrough()}
#     | after_rag_prompt
#     | model_local
#     | StrOutputParser()
# )
# print(after_rag_chain.invoke("how many account are available?"))

# import ollama

# embedding = ollama.embeddings(model='nomic-embed-text', prompt = "Represent this sentence for searching relevant passages: how are you?")['embedding']
# print(embedding)