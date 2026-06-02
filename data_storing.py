from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_classic.schema import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
import os


splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,
    chunk_overlap=150,
    separators=["\n\n", "\n", ".", " ", ""]
)


def load_and_chunk(file_path, source_type="unknown"):
    """
    Loads a file and converts it into LangChain Documents (chunks)
    """

    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()

    chunks = splitter.split_text(text)

    docs = []

    for i, chunk in enumerate(chunks):
        docs.append(
            Document(
                page_content=chunk,
                metadata={
                    "source": source_type,
                    "file": os.path.basename(file_path),
                    "chunk_id": i
                }
            )
        )

    return docs


all_docs_knowledge = []
all_docs_persona=[]

knowledge_dirs = {
    "paper": "feynman_data/raw_json",
    "wiki": "feynman_data/wiki",
    "youtube": "feynman_data/youtube_transcripts",
    "book": "feynman_data/books"
}
persona_dirs={
    "wiki": "feynman_data/wiki",
    "youtube": "feynman_data/youtube_transcripts"
}

for source_type, folder in knowledge_dirs.items():
    if not os.path.exists(folder):
        continue

    for file in os.listdir(folder):
        path = os.path.join(folder, file)

        docs = load_and_chunk(path, source_type)
        all_docs_knowledge.extend(docs)

for source_type, folder in persona_dirs.items():
    if not os.path.exists(folder):
        continue

    for file in os.listdir(folder):
        path = os.path.join(folder, file)

        docs = load_and_chunk(path, source_type)
        all_docs_persona.extend(docs)
        
        

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)


vectorstore_persona = FAISS.from_documents(
    documents=all_docs_persona,
    embedding=embeddings
)
vectorstore_knowledge= FAISS.from_documents(
    documents=all_docs_knowledge,
    embedding=embeddings
)
print("Total chunks:", len(all_docs_knowledge))
print(all_docs_knowledge[0])
print("Total chunks:", len(all_docs_persona))
print(all_docs_persona[0])
vectorstore_persona.save_local("feynman_faiss_index_persona")
vectorstore_knowledge.save_local("feynman_faiss_index_knowledge")

