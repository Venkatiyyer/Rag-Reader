import streamlit as st
import os
import streamlit.components.v1 as components
from logic import vector_embedding, query_documents  # Import functions from shared_logic.py

# Ensure the directory for saving files exists
data_dir = "./data"
if not os.path.exists(data_dir):
    os.makedirs(data_dir)

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

# CSS for header
header_css = '''
<style>
    .main-header {
        text-align: center;
        font-size: 1rem;
        font-weight: bold;
        color: #e8a507;
        padding: 1rem;
        background: transparent;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.4);
        display: inline-block;
        letter-spacing: 2px;
    }
    .sub-header {
        text-align: right;
        font-size: 1.5rem;
        font-weight: normal;
        color: #870505;
        padding: 1rem;
        background: transparent;
        display: inline-block;
        margin-top: -20px;
        width: 100%;
    }
    @media (max-width: 600px) {
        .main-header { font-size: 2.5rem; }
        .sub-header { font-size: 1.25rem; margin-right: 10%; }
    }
    .question-label {
        font-size: 1.5rem;
        color: #cccccc;
        font-weight: bold;
        margin-top: 2rem;
        display: block;
    }
</style>
'''

question_label = '''
<div class="question-label">Ask a question about your documents:</div>
'''


def main():
    # Page config
    st.set_page_config(page_title="RAGReader Pro", page_icon=":books:")
    st.write(css, unsafe_allow_html=True)

    # Session state
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "vectors" not in st.session_state:
        st.session_state.vectors = None

    # Header
    st.write(header_css, unsafe_allow_html=True)
    st.markdown('<h1 class="main-header">RAGReader Pro</h1>', unsafe_allow_html=True)
    st.markdown('<h2 class="sub-header">Your Document Assistant</h2>', unsafe_allow_html=True)
    st.markdown(question_label, unsafe_allow_html=True)

    # Sidebar: file upload
    with st.sidebar:
        st.subheader("Your documents")
        uploaded_files = st.file_uploader("Upload your PDFs here", accept_multiple_files=True)
        process_button = st.button("Process")

        if uploaded_files and process_button:
            st.subheader("Uploaded Files:")
            for f in uploaded_files:
                st.write(f.name)

            if st.session_state.vectors is None:
                with st.spinner("Processing..."):
                    for f in uploaded_files:
                        path = os.path.join(data_dir, f.name)
                        with open(path, "wb") as fd:
                            fd.write(f.getbuffer())

                    vecs = vector_embedding(data_dir)
                    if isinstance(vecs, dict):
                        st.error(f"Vector build failed: {vecs['message']}")
                    else:
                        st.session_state.vectors = vecs
                        st.success("Files processed successfully!")

    # User input
    user_question = st.text_input("Ask a question about your documents", label_visibility="collapsed")

    if user_question and st.session_state.vectors and not isinstance(st.session_state.vectors, dict):
        st.session_state.chat_history.append(f"You : {user_question}")
        response = query_documents(user_question, st.session_state.vectors)
        if "error" in response:
            st.error(f"⚠️ Retrieval error: {response['error']}")
        elif "no_result" in response:
            st.warning("Ran successfully, but no matching content found.")
        else:
            st.session_state.chat_history.append(response["answer"] )

    # Display chat history
    if st.session_state.chat_history:
        st.subheader("Chat Logs")
        for i, msg in enumerate(st.session_state.chat_history):
            tpl = user_template if i % 2 == 0 else bot_template
            st.markdown(tpl.replace("{{MSG}}", msg), unsafe_allow_html=True)

    # Clear / delete buttons
    if st.button("Clear Chat Logs"):
        st.session_state.chat_history.clear()
        st.success("Chat history cleared!")

    if st.button("Delete Uploaded Files"):
        for fn in os.listdir(data_dir):
            os.remove(os.path.join(data_dir, fn))
        st.session_state.vectors = None
        st.success("Uploaded files deleted!")

if __name__ == '__main__':
    main()
