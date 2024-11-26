from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from pydantic import BaseModel
import os
import shutil
from logic import vector_embedding, query_documents  # Importing your shared logic

# Initialize FastAPI app
app = FastAPI()

# Directory for storing uploaded files
UPLOAD_DIRECTORY = "./data"
os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)

# Store vectors and contents of uploaded documents
document_vectors = {}  # Dictionary to store vectors by filename
document_contents = {}  # Dictionary to store contents by filename

# Function to handle the embedding process in the background
def process_document(file_path: str, filename: str):
    """
    Background task to process document embedding and store document vectors and content.
    """
    try:
        # Generate vectors and content for the document using vector_embedding function
        new_vectors = vector_embedding(data_dir=UPLOAD_DIRECTORY)  # Process the documents
        document_vectors[filename] = new_vectors

        # Optionally, store the actual document content for later retrieval if needed
        with open(file_path, 'r', encoding='utf-8') as f:
            document_contents[filename] = f.read()

    except Exception as e:
        print(f"Error processing document embedding: {e}")

@app.post("/upload_file")
async def upload_file(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    """
    Endpoint to upload a file (PDF or TXT) and start the embedding process.
    """
    try:
        # Save the uploaded file to the defined directory
        file_path = os.path.join(UPLOAD_DIRECTORY, file.filename)
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        # Start the embedding process in the background (Optional if you want to update vectors after file upload)
        background_tasks.add_task(process_document, file_path, file.filename)

        return {"message": f"File '{file.filename}' uploaded successfully and processing started."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File upload failed: {e}")

class QueryRequest(BaseModel):
    query: str

@app.post("/query_documents")
async def query_documents_endpoint(query_request: QueryRequest):
    """
    Endpoint to query stored documents and retrieve relevant responses.
    """
    try:
        query = query_request.query

        # Check if vectors are available
        if not document_vectors:
            raise HTTPException(status_code=404, detail="No documents available to query.")

        # Use the stored vectors to answer the query
        response = query_documents(query, document_vectors)

        # Log the response from query_documents to debug the format
        print(f"Response from query_documents: {response}")

        # Check if the response contains the expected keys
        if not isinstance(response, dict):
            raise HTTPException(status_code=500, detail="Query response is not in the expected dictionary format.")

        if "answer" not in response or "relevant_docs" not in response:
            raise HTTPException(status_code=500, detail="Invalid response format from query processing.")

        return {
            "query": query,
            "answer": response.get("answer", "No answer found"),
            "relevant_docs": response.get("relevant_docs", []),
            "response_time": response.get("response_time", 0)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during query processing: {e}")

# Root endpoint for the application (optional)
@app.get("/")
def read_root():
    return {"message": "Welcome to the Document Query API!"}
