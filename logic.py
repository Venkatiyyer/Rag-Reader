import os
import time
from langchain_groq import ChatGroq
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import create_retrieval_chain
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders.text import TextLoader
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Manually set the API keys
google_api_key = "AIzaSyCxhOGBxS0NuhwIV94wYZ2aqL5nCOPVEkY"
groq_api_key = "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"

# Set the environment variable for Google API key
os.environ["GOOGLE_API_KEY"] = google_api_key

# Initialize the model
llm = ChatGroq(groq_api_key=groq_api_key, model_name="Llama3-8b-8192")

# Define the prompt template for generating responses
prompt = ChatPromptTemplate.from_template(
    """
    Answer the questions based on the provided context only.
    Please provide the most accurate response based on the question.
    <context>
    {context}
    <context>
    Questions: {input}
    """
)

def vector_embedding(data_dir="./data"):
    try:
        # Load .txt files from the data directory
        txt_file_paths = [os.path.join(data_dir, filename) for filename in os.listdir(data_dir) if filename.endswith(".txt")]
        
        # Initialize TextLoader for each text file
        txt_loader = [TextLoader(file_path) for file_path in txt_file_paths]

        # Load .pdf files from the data directory
        pdf_loader = PyPDFDirectoryLoader(data_dir)

        # Load all documents
        txt_docs = []
        for loader in txt_loader:
            txt_docs += loader.load()

        pdf_docs = pdf_loader.load()  # Load PDF files

        # Combine both text and PDF documents into one list
        all_docs = txt_docs + pdf_docs

        # If no documents are found
        if not all_docs:
            return {"message": "No documents found in the specified directory."}

        embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)  # Chunk Creation
        final_documents = text_splitter.split_documents(all_docs[:20])  # splitting
        vectors = FAISS.from_documents(final_documents, embeddings)  # vector OpenAI embeddings

        return vectors

    except Exception as e:
        return {"message": f"Error in vector embedding: {str(e)}"}

def query_documents(query: str, vectors, prompt=prompt):
    try:
        document_chain = create_stuff_documents_chain(llm, prompt)
        retriever = vectors.as_retriever()
        retrieval_chain = create_retrieval_chain(retriever, document_chain)

        # Run the query
        start = time.process_time()
        response = retrieval_chain.invoke({'input': query})
        response_time = time.process_time() - start
        
        # Return the result
        return {
            "query": query,
            "answer": response['answer'],
            "relevant_docs": response['context'],
            "response_time": response_time
        }

    except Exception as e:
        return {"message": f"Error in querying documents: {str(e)}"}
