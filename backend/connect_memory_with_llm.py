import os 

from langchain_huggingface import HuggingFaceEndpoint
from langchain_core.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

# Setup LLM(Mistral with huggingface)

HF_TOKEN = os.environ.get("HF_TOKEN")
huggingface_repo_id = "mistralai/Mistral-7B-Instruct-v0.3"

def load_llm(huggingface_repo_id):
    llm = HuggingFaceEndpoint(
        repo_id=huggingface_repo_id,
        task="text-generation",
        temperature=0.5,
        huggingfacehub_api_token=HF_TOKEN,
        max_new_tokens=512,
    )
    return llm

# Connect LLm with FAISS and create chain

custom_prompt_template = """
Use only the information provided in the context to answer the user's question.
If the answer is not found within the context, say "I don't know". Do not try to provide an answer outside the context.

Context: {context}
Question: {question}

Start the answer directly. No small talk please.
Provide a concise and accurate answer. Avoid any generalizations or assumptions.
"""

def set_custom_prompt(custom_prompt_template):
    prompt=PromptTemplate(template=custom_prompt_template,
                          input_variables=["context","question"])
    return prompt

# Load database

DB_FAISS_PATH="vectorstore/db_faiss"
embedding_model=HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
db=FAISS.load_local(DB_FAISS_PATH, embedding_model, allow_dangerous_deserialization=True)

# Create QA chain

qa_chain=RetrievalQA.from_chain_type(
    llm=load_llm(huggingface_repo_id),
    chain_type="stuff",
    retriever=db.as_retriever(search_kwargs={'k':3}),
    return_source_documents=True,
    chain_type_kwargs={'prompt':set_custom_prompt(custom_prompt_template)}
)

# Now invoke with a single query

user_query=input("Write Query Here: ")
response=qa_chain.invoke({'query': user_query})
print("RESULT: ", response["result"])
print("SOURCE DOCUMENTS: ", response["source_documents"])