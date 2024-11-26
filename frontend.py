import streamlit as st
import os
from logic import vector_embedding, query_documents  # Import functions from shared_logic.py

# Ensure the directory for saving files exists
data_dir = "./data"
if not os.path.exists(data_dir):
    os.makedirs(data_dir)

# Auto-cleanup of the data directory on app refresh
for filename in os.listdir(data_dir):
    file_path = os.path.join(data_dir, filename)
    if os.path.isfile(file_path):
        os.remove(file_path)

# HTML templates
css = '''
<style>
.chat-message {
    padding: 1.5rem; 
    border-radius: 0.5rem; 
    margin-bottom: 1rem; 
    display: flex
}
.chat-message.user {
    background-color: #2b313e;
    flex-direction: row-reverse; /* Align user message to the right */
}
.chat-message.bot {
    background-color: #475063;
}
.chat-message .avatar {
    width: 20%;
}
.chat-message .avatar img {
    max-width: 78px;
    max-height: 78px;
    border-radius: 50%;
    object-fit: cover;
}
.chat-message .message {
    width: 80%;
    padding: 0 1.5rem;
    color: #fff;
}
</style>
'''

bot_template = '''
<div class="chat-message bot">
    <div class="avatar">
        <img src="https://i.ibb.co/cN0nmSj/Screenshot-2023-05-28-at-02-37-21.png" style="max-height: 78px; max-width: 78px; border-radius: 50%; object-fit: cover;">
    </div>
    <div class="message">{{MSG}}</div>
</div>
'''

user_template = '''
<div class="chat-message user">
    <div class="avatar">
        <img src="">
    </div>    
    <div class="message">
        {{MSG}}  <!-- This will now just render the user's question -->
    </div>
</div>
'''

# CSS 

# Define CSS for header and question label
header_css = '''
<style>
    /* Style for the main header with transparent background */
    .main-header {
        text-align: center;
        font-size: 4rem; /* Large font size for prominence */
        font-weight: bold;
        color: #e8a507;  /* Yellow color for contrast against dark background */
        padding: 1rem;
        background: transparent;  /* Transparent background */
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.4);  /* Slight shadow for visibility */
        display: inline-block;
        letter-spacing: 2px; /* Adds spacing between letters */
    }

    /* Style for the subtitle below the main header */
    .sub-header {
        text-align: right;
        font-size: 1.5rem; /* Font size slightly smaller than the header */
        font-weight: normal;
        color: #870505;  /* Light red text color for contrast */
        padding: 1rem;
        background: transparent;  /* Transparent background */
        display: inline-block;
        margin-top: -20px;  /* Negative margin to bring it closer to the main header */
    }

    /* Adjust font size and alignment for smaller screens */
    @media (max-width: 600px) {
        .main-header {
            font-size: 2.5rem; /* Smaller font size for responsiveness */
        }
        .sub-header {
            font-size: 1.25rem;
            margin-right: 10%; /* Adds a bit of right margin */
        }
    }

    /* Style for the question label */
    .question-label {
        font-size: 1.5rem; /* Slightly larger font for better visibility */
        color: #cccccc; /* Grey color to contrast against a dark background */
        font-weight: bold;
        # margin-bottom: 1rem;
         margin-top: 2rem;
        display: block;
    }
</style>
'''

question_label = '''
<div class="question-label">Ask a question about your documents:</div>
'''



# Frontend code for handling file upload, user input, and chat display
def main():
    # Set page configuration
    st.set_page_config(page_title="RAGReader Pro", page_icon=":books:")

    # Display custom CSS
    st.write(css, unsafe_allow_html=True)

    # Session state for tracking conversation history and vectors
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    if "vectors" not in st.session_state:
        st.session_state.vectors = None

    # Add the CSS to the Streamlit app
    st.write(header_css, unsafe_allow_html=True)
    

# Use the CSS class to style the header
    st.markdown('<h1 class="main-header">RAGReader Pro</h1>', unsafe_allow_html=True)
    st.markdown('<h2 class="sub-header">Your Document Assistant</h2>', unsafe_allow_html=True)
    # Inject the custom CSS into the app
    st.markdown(question_label, unsafe_allow_html=True)
    # Sidebar for file upload
    with st.sidebar:
        st.subheader("Your documents")
        uploaded_files = st.file_uploader("Upload your PDFs here", accept_multiple_files=True)
        process_button = st.button("Process")  # Add process button in sidebar

        if uploaded_files and process_button:
            st.subheader("Uploaded Files:")
            for uploaded_file in uploaded_files:
                st.write(uploaded_file.name)

            # Process the uploaded files once they're uploaded
            if st.session_state.vectors is None:  # Only process files if vectors are not yet created
                with st.spinner("Processing..."):  # Placeholder spinner for processing

                    # Save uploaded PDFs into the data directory
                    for uploaded_file in uploaded_files:
                        with open(os.path.join(data_dir, uploaded_file.name), "wb") as f:
                            f.write(uploaded_file.getbuffer())

                    # Vector embedding after processing files
                    st.session_state.vectors = vector_embedding(data_dir)
                    st.success("Files processed successfully!")

    # User question input
    # Display the custom-styled question label
    
    # st.markdown('<div class="question-label">Ask a question about your documents:</div>', unsafe_allow_html=True)

    user_question = st.text_input("")
    if user_question and st.session_state.vectors:
        # Add user question to the chat history
        st.session_state.chat_history.append(f"  You :{'    '}{user_question}")

        # Query the documents using the provided question
        response = query_documents(user_question, st.session_state.vectors)
        
        # Add bot response to the chat history
        if response and 'answer' in response:  # Check if the 'answer' key is in the response
            st.session_state.chat_history.append(f"{'    '} {response['answer']}")
        else:
            st.session_state.chat_history.append(f"{'    '} Sorry, I couldn't find an answer to your question.")
    # Display the conversation history using templates
    if st.session_state.chat_history:
        st.subheader("Chat Logs")
        for i, message in enumerate(st.session_state.chat_history):
            if i % 2 == 0:  # Even index: user message
                st.markdown(user_template.replace("{{MSG}}", message), unsafe_allow_html=True)
            else:  # Odd index: bot response
                st.markdown(bot_template.replace("{{MSG}}", message), unsafe_allow_html=True)

    # Separate button to clear chat history
    if st.button("Clear Chat Logs"):
        st.session_state.chat_history.clear()
        st.success("Chat history cleared!")

    # Separate button to delete uploaded files
    if st.button("Delete Uploaded Files"):
        # Delete the uploaded files from the data directory
        for filename in os.listdir(data_dir):
            file_path = os.path.join(data_dir, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
        
        # Clear the session state vectors
        st.session_state.vectors = None
        st.success("Uploaded files deleted!")

if __name__ == '__main__':
    main()
