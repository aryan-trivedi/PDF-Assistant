import fitz  # PyMuPDF
from typing import List
from langchain.text_splitter import RecursiveCharacterTextSplitter

def extract_text_from_pdf(file_path: str) -> str:
    """Extracts text from a PDF file using PyMuPDF."""
    text = ""
    with fitz.open(file_path) as pdf:
        for page in pdf:
            text += page.get_text()
    return text

def split_text_into_chunks(text: str) -> List[str]:
    """Splits raw text into manageable overlapping chunks."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", ".", " ", ""],
    )
    return splitter.split_text(text)

def process_pdf(file_path: str) -> List[str]:
    """Full processing pipeline: extract -> split -> return chunks."""
    raw_text = extract_text_from_pdf(file_path)
    chunks = split_text_into_chunks(raw_text)
    return chunks
