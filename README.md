# RAG Reader Pro

**RAG Reader Pro** is a web-based application that enables users to upload multiple PDF and CSV documents, process the content, and interact with the extracted data via a conversational AI interface. The application combines **FastAPI** for the backend API, **Streamlit** for the frontend interface, and utilizes **HTML/CSS** for UI design and styling.

## GitHub Repository

- [GitHub Link for RAG Reader Pro](https://github.com/Venkatiyyer/Rag-Reader)  

## Setup and Run the Application Locally

Follow these steps to set up and run the RAG Reader Pro app on your local machine:

## 1. Clone the Repository
```bash
git clone https://github.com/Venkatiyyer/Rag-Reader.git
cd rag-reader

### 2. Install Required Dependencies
Make sure you have Python 3.7+ installed. Create and activate a virtual environment, then install the required packages:

python3 -m venv venv
source venv/bin/activate  # For macOS/Linux
venv\Scripts\activate     # For Windows
pip install -r requirements.txt


### 3. Set Up Environment Variables
Ensure you have an .env file with your necessary environment variables, such as API keys or credentials for OpenAI. Example .env:

OPENAI_API_KEY=your_openai_api_key


### 4. Run the Application
Backend (FastAPI Server)
To run the FastAPI backend:

uvicorn logic:app --reload


### Frontend (Streamlit App)
To start the Streamlit frontend:

streamlit run app.py

## Solution Architecture
RAG Reader Pro follows a modular and scalable architecture combining both backend API and frontend UI to facilitate document processing and conversational AI interaction:

### 1. Frontend: Streamlit, HTML, and CSS
Streamlit provides the interactive web interface where users can upload PDF and CSV files and ask questions related to the content of those files.
HTML and CSS are used for additional UI elements and styling, ensuring a smooth user experience.
### 2. Backend: FastAPI
The backend API is built with FastAPI, which handles document processing and manages interactions between the frontend and the AI model.
FastAPI endpoints are used to receive and process uploaded files (PDF and CSV) and return processed results to the frontend.
### 3. Text Extraction & Chunking:
PyPDF2 is used for extracting text from PDF files.
LangChain's CharacterTextSplitter splits the extracted text into chunks to facilitate efficient document search and retrieval.
### 4. Vectorization:
The extracted and chunked text is converted into vector embeddings using OpenAIEmbeddings via LangChain. These embeddings help to efficiently search and retrieve relevant information from the documents.
### 5. Conversational AI:
LangChain's ConversationalRetrievalChain is used to integrate a conversational model for Q&A based on the uploaded documents.
The model, powered by OpenAI (or HuggingFace for embeddings), processes user queries and returns relevant answers based on document content.
ConversationBufferMemory ensures continuous chat history between the user and the model.
### 6. Document Handling:
The application supports PDF and CSV uploads and processes the contents accordingly for Q&A interaction.


## Features
* Upload multiple PDF and CSV documents.
* Ask questions about the uploaded documents.
* Conversational AI provides answers based on the document content.
* Modular design that can be extended to support more file formats.
* FastAPI backend to manage the API endpoints and document processing logic.
* Requirements
* Python 3.10+
* Streamlit for frontend
* FastAPI for backend
* PyPDF2 for PDF extraction
* Pandas for CSV file handling
* LangChain for text processing and conversational AI
* OpenAI API (or HuggingFace API for embeddings)
* Uvicorn for running FastAPI server

## Requirements
* Python 3.7+
* Streamlit for frontend
* FastAPI for backend
* PyPDF2 for PDF extraction
* Pandas for CSV file handling
* LangChain for text processing and conversational AI
* OpenAI API (or HuggingFace API for embeddings)
* Uvicorn for running FastAPI server


###You can install all dependencies with:

pip install -r requirements.txt

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Contributors
Venkat Iyyer - Project Lead



