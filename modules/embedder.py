import os
import shutil
import tempfile
from langchain_community.document_loaders import CSVLoader
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
import zipfile
import io
import streamlit as st
import pandas as pd
from langchain_core.documents import Document

class Embedder:

    def __init__(self):
        self.PATH = "embeddings"
        self.MODEL = st.session_state["model"]
        self.createEmbeddingsDir()

    def createEmbeddingsDir(self):
        """
        Creates a directory to store the embeddings vectors
        """
        if not os.path.exists(self.PATH):
            os.mkdir(self.PATH)

    def readVectorsFromZip(self, file1, extracted_dir):
        os.makedirs(extracted_dir, exist_ok=True)

        # Step 1: Unzip file1 to the temporary directory
        with zipfile.ZipFile(file1, 'r') as zip_ref:
            zip_ref.extractall(extracted_dir)

        embeddings = self.initializeEmbeddings()

        # Step 2: Load every saved FAISS index (a folder containing index.faiss)
        # and merge them into a single 'vectors' store. Stray raw files are
        # embedded on the fly so legacy/manual archives still work.
        vectors = None
        for root, dirs, files in os.walk(extracted_dir):
            loaded_vectors = None
            if "index.faiss" in files:
                loaded_vectors = FAISS.load_local(
                    root, embeddings, allow_dangerous_deserialization=True
                )
                dirs[:] = []  # don't descend into an already-loaded index folder
            else:
                for file in files:
                    file_path = os.path.join(root, file)
                    with open(file_path, 'rb') as f:
                        chunk = self.generateEmbeddingsFromFile(
                            f.read(), self.get_file_extension(file)
                        )
                    loaded_vectors = chunk if loaded_vectors is None else (
                        loaded_vectors.merge_from(chunk) or loaded_vectors
                    )

            if loaded_vectors is None:
                continue
            if vectors is None:
                vectors = loaded_vectors
            else:
                vectors.merge_from(loaded_vectors)

        # Clean up the temporary extraction directory
        shutil.rmtree(extracted_dir, ignore_errors=True)

        return vectors
    
    def get_file_extension(self, uploaded_file):
            file_extension =  os.path.splitext(uploaded_file)[1].lower()
            
            return file_extension

    def index_path(self, original_filename):
        """Folder where the FAISS index for this file/model is persisted."""
        safe_model = self.MODEL.replace(':', '_')
        return f"{self.PATH}/{safe_model}-{original_filename}"

    def storeDocEmbeds(self, file, original_filename):
        """
        Stores document embeddings using Langchain and FAISS
        """

        file_extension = self.get_file_extension(original_filename)

        vectors = None
        if file_extension == ".zip":
            extract_dir = os.path.join(tempfile.gettempdir(), f"unzip-{original_filename}")
            vectors = self.readVectorsFromZip(io.BytesIO(file), extract_dir)
        else:
            vectors = self.generateEmbeddingsFromFile(file, file_extension)

        # Persist the FAISS index natively (writes index.faiss + index.pkl)
        vectors.save_local(self.index_path(original_filename))

    def generateEmbeddingsFromFile(self, file, file_extension):
        with tempfile.NamedTemporaryFile(mode="wb", delete=False) as tmp_file:
            try:
                tmp_file.write(file)
            except Exception as e:
                # print(f"Warning reading file: {e}")
                tmp_file.write(file.encode('utf-8'))
            tmp_file_path = tmp_file.name

        text_splitter = RecursiveCharacterTextSplitter(
                chunk_size = 2000,
                chunk_overlap  = 100,
                length_function = len,
            )

        if file_extension == ".csv":
            loader = CSVLoader(file_path=tmp_file_path, encoding="utf-8",csv_args={
                    'delimiter': ',',})
            data = loader.load()

        elif file_extension == ".pdf":
            loader = PyPDFLoader(file_path=tmp_file_path)  
            data = loader.load_and_split(text_splitter)
            
        elif file_extension == ".txt":
            loader = TextLoader(file_path=tmp_file_path, encoding="utf-8")
            data = loader.load_and_split(text_splitter)

        elif file_extension == ".xlsx":
            # Get all sheet names
            excel_file = pd.ExcelFile(tmp_file_path)
            # all_sheets_data = []
            documents = []
            
            # Read each sheet
            for sheet_name in excel_file.sheet_names:
                df = pd.read_excel(excel_file, sheet_name=sheet_name)
                df = df.astype(str)
                sheet_text = f"Sheet: {sheet_name}\n{df.to_string()}"
                # Create Document object directly
                doc = Document(page_content=sheet_text, metadata={"source": sheet_name})
                documents.append(doc)

            data = documents
            #     all_sheets_data.append(sheet_text)
            
            # # Combine all sheets' data
            # combined_text = "\n\n".join(all_sheets_data)
            
            # # Create documents from the combined text
            # # loader = TextLoader(StringIO(combined_text))
            # text_file = StringIO(combined_text)
            # loader = TextLoader(text_file)
            # data = loader.load()
            
        # os.remove(tmp_file_path)
                
        embeddings = self.initializeEmbeddings()

        vectors = FAISS.from_documents(data, embeddings)
        return vectors

    def initializeEmbeddings(self):
        # Dedicated embedding model (independent of the chat model).
        self.MODEL = st.session_state["model"]
        base_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
        embeddings = OllamaEmbeddings(model="nomic-embed-text", base_url=base_url)
        return embeddings


    def getDocEmbeds(self, file, original_filename):
        """
        Retrieves document embeddings, building and persisting them on first use.
        """
        index_dir = self.index_path(original_filename)

        if not os.path.isdir(index_dir):
            self.storeDocEmbeds(file, original_filename)

        # Load the persisted FAISS index from disk
        embeddings = self.initializeEmbeddings()
        vectors = FAISS.load_local(
            index_dir, embeddings, allow_dangerous_deserialization=True
        )
        st.session_state["vectordb"] = index_dir

        return vectors
