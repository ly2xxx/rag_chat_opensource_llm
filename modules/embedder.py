import os
import pickle
import tempfile
from langchain.document_loaders.csv_loader import CSVLoader
from langchain.vectorstores import FAISS
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.document_loaders import PyPDFLoader
from langchain.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.embeddings import OllamaEmbeddings
# from InstructorEmbedding import INSTRUCTOR
# from langchain.embeddings import HuggingFaceInstructEmbeddings
import zipfile
import io
import streamlit as st
# from sentence_transformers import SentenceTransformer

class Embedder:

    def __init__(self):
        self.PATH = "embeddings"
        self.MODEL = "mistral"
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

        # Step 2: Iterate through .pkl files and read into a FAISS 'vectors' variable
        vectors = None
        loaded_vectors = None
        for root, dirs, files in os.walk(extracted_dir):
            for file in files:
                if file.endswith('.pkl'):
                    pkl_file_path = os.path.join(root, file)

                    # Load vectors from the pickle file
                    with open(pkl_file_path, 'rb') as f:
                        loaded_vectors = pickle.load(f)
                else:
                    file_path = os.path.join(root, file)

                    # Load vectors from the embedding
                    with open(file_path, 'rb') as f:
                        f.seek(0)
                        loaded_vectors = self.generateEmbeddingsFromFile(f.read(), self.get_file_extension(file))

                # Assuming 'vectors' is a FAISS Index, merge the loaded vectors
                if vectors is None:
                    vectors = loaded_vectors
                else:
                    vectors.merge_from(loaded_vectors)

        # Clean up: Remove the temporary directory and its contents
        if os.path.exists(extracted_dir):
            for file_or_dir in os.listdir(extracted_dir):
                file_or_dir_path = os.path.join(extracted_dir, file_or_dir)
                if os.path.isfile(file_or_dir_path):
                    os.remove(file_or_dir_path)
                elif os.path.isdir(file_or_dir_path):
                    os.rmdir(file_or_dir_path)
        
        os.rmdir(extracted_dir)

        # Now 'vectors' contains all the loaded vectors from the .pkl files
        return vectors
    
    def get_file_extension(self, uploaded_file):
            file_extension =  os.path.splitext(uploaded_file)[1].lower()
            
            return file_extension

    def storeDocEmbeds(self, file, original_filename):
        """
        Stores document embeddings using Langchain and FAISS
        """ 
        
        file_extension = self.get_file_extension(original_filename)

        vectors = None
        if file_extension == ".zip":
            vectors = self.readVectorsFromZip(io.BytesIO(file), original_filename)
        else:
            vectors = self.generateEmbeddingsFromFile(file, file_extension)

        # Save the vectors to a pickle file
        with open(f"{self.PATH}/{self.MODEL}-{original_filename}.pkl", "wb") as f:
            pickle.dump(vectors, f)

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

        os.remove(tmp_file_path)
                
        embeddings = self.initializeEmbeddings()

        vectors = FAISS.from_documents(data, embeddings)
        # Error: 'Document' object has no attribute 'replace'
        # vectors = FAISS.from_texts(data, embeddings)
        return vectors

    def initializeEmbeddings(self):
        # modelPath = "all-MiniLM-L6-v2"
        # embeddings = HuggingFaceEmbeddings(model_name=modelPath)
        # Use embedding function to store them in vector db
        self.MODEL = st.session_state["model"]
        embeddings = OllamaEmbeddings(model=self.MODEL)
        return embeddings


    def getDocEmbeds(self, file, original_filename):
        """
        Retrieves document embeddings
        """
        vector_file_name = f"{self.PATH}/{self.MODEL}-{original_filename}.pkl"

        if not os.path.isfile(vector_file_name):
            self.storeDocEmbeds(file, original_filename)

        # Load the vectors from the pickle file
        with open(vector_file_name, "rb") as f:
            vectors = pickle.load(f)
            st.session_state["vectordb"]=vector_file_name
        
        return vectors
