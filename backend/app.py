from flask import Flask, request, jsonify
import os
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from langchain_huggingface import HuggingFaceEndpoint
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

DB_FAISS_PATH = "vectorstore/db_faiss"

def get_vectorstore():
    embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    db = FAISS.load_local(DB_FAISS_PATH, embedding_model, allow_dangerous_deserialization=True)
    return db

def set_custom_prompt(custom_prompt_template):
    return PromptTemplate(template=custom_prompt_template, input_variables=["context", "question"])

def load_llm(huggingface_repo_id, HF_TOKEN):
    return HuggingFaceEndpoint(
        repo_id=huggingface_repo_id,
        task="text-generation",
        temperature=0.5,
        huggingfacehub_api_token=HF_TOKEN,
        max_new_tokens=512,
    )

@app.route("/api/query", methods=["POST"])
def query():
    try:
        user_query = request.json.get('query')
        HF_TOKEN = os.environ.get("HF_TOKEN")
        huggingface_repo_id = "mistralai/Mistral-7B-Instruct-v0.3"

        custom_prompt_template = """
            Use only the information provided in the context to answer the user's question.
            If the answer is not found within the context, say "I don't know". Do not try to provide an answer outside the context.

            Context: {context}
            Question: {question}

            Start the answer directly. No small talk please.
            Provide a concise and accurate answer. Avoid any generalizations or assumptions.
        """

        vectorstore = get_vectorstore()
        if vectorstore is None:
            return jsonify({"error": "Failed to load the vector store"}), 500

        qa_chain = RetrievalQA.from_chain_type(
            llm=load_llm(huggingface_repo_id=huggingface_repo_id, HF_TOKEN=HF_TOKEN),
            chain_type="stuff",
            retriever=vectorstore.as_retriever(search_kwargs={'k': 3}),
            return_source_documents=True,
            chain_type_kwargs={'prompt': set_custom_prompt(custom_prompt_template)}
        )

        response = qa_chain.invoke({'query': user_query})
        result = response["result"]

        return jsonify({"result": result}), 200

    except Exception as e:
        print("ERROR:", str(e))
        return jsonify({"error": str(e)}), 500

@app.route("/", methods=["GET"])
def home():
    return "✅ MediBot backend is running!"

if __name__ == "__main__":
    app.run(debug=True)
