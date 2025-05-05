from flask import Flask, request, jsonify
import os
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from huggingface_hub import InferenceClient
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

DB_FAISS_PATH = "vectorstore/db_faiss"

def get_vectorstore():
    embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    db = FAISS.load_local(DB_FAISS_PATH, embedding_model, allow_dangerous_deserialization=True)
    return db

def generate_response_with_hf(prompt, hf_token, model_name):
    client = InferenceClient(model_name, token=hf_token)
    return client.text_generation(prompt=prompt, max_new_tokens=512, temperature=0.5)

@app.route("/api/query", methods=["POST"])
def query():
    try:
        user_query = request.json.get('query')
        if not user_query:
            return jsonify({"error": "Empty query received."}), 400

        HF_TOKEN = os.environ.get("HF_TOKEN")
        model_name = "mistralai/Mistral-7B-Instruct-v0.3"

        # Prompt template
        custom_prompt_template = """
        Use only the information provided in the context to answer the user's question.
        If the answer is not found within the context, say "I don't know". Do not try to provide an answer outside the context.

        Context: {context}
        Question: {question}

        Start the answer directly. No small talk please.
        Provide a concise and accurate answer. Avoid any generalizations or assumptions.
        """

        vectorstore = get_vectorstore()
        retriever = vectorstore.as_retriever(search_kwargs={'k': 3})
        relevant_docs = retriever.invoke(user_query)

        context = "\n\n".join([doc.page_content for doc in relevant_docs])
        prompt = custom_prompt_template.replace("{context}", context).replace("{question}", user_query)
        result = generate_response_with_hf(prompt, HF_TOKEN, model_name)

        return jsonify({"result": result}), 200

    except Exception as e:
        print("ERROR:", str(e))
        return jsonify({"error": str(e)}), 500

@app.route("/", methods=["GET"])
def home():
    return "✅ MediBot backend is running!"

if __name__ == "__main__":
    app.run(debug=True)
