from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from utils.pdf_processing import process_pdf
from langchain_community.vectorstores import FAISS
from langchain.embeddings import SentenceTransformerEmbeddings
import os
import shutil
import uuid
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-pro-latest")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploaded_pdfs"
VECTOR_DIR = "vector_store"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(VECTOR_DIR, exist_ok=True)

@app.post("/upload/")
async def upload_pdf(file: UploadFile = File(...)):
    file_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{file_id}.pdf")
    
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    chunks = process_pdf(file_path)

    embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
    vectorstore = FAISS.from_texts(chunks, embeddings)
    vectorstore.save_local(os.path.join(VECTOR_DIR, file_id))

    return {"message": "PDF processed and vector store saved.", "file_id": file_id}


@app.post("/ask/")
async def ask_question(file_id: str = Form(...), question: str = Form(...)):
    vectorstore_path = os.path.join(VECTOR_DIR, file_id)
    
    if not os.path.exists(vectorstore_path):
        return JSONResponse(status_code=404, content={"error": "Vector store not found for this file_id"})

    embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
    vectorstore = FAISS.load_local(vectorstore_path, embeddings, allow_dangerous_deserialization=True)

    docs = vectorstore.similarity_search(question, k=5)
    context = "\n\n".join([doc.page_content for doc in docs])

    prompt = f"Answer the question based on the following context:\n\n{context}\n\nQuestion: {question}"
    response = model.generate_content(prompt)

    return {"answer": response.text}
