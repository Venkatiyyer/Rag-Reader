import streamlit as st
import os
from logic import vector_embedding, query_documents

# Ensure the directory for saving files exists
data_dir = "./data"
if not os.path.exists(data_dir):
    os.makedirs(data_dir)

# HTML/CSS templates
css = '''
<style>
.chat-message { padding: 1.5rem; border-radius: 0.5rem; margin-bottom: 1rem; display: flex }
.chat-message.user { background-color: #2b313e; flex-direction: row-reverse; }
.chat-message.bot { background-color: #475063; }
.chat-message .avatar { width: 20%; }
.chat-message .avatar img { max-width: 78px; max-height: 78px; border-radius: 50%; object-fit: cover; }
.chat-message .message { width: 80%; padding: 0 1.5rem; color: #fff; }
</style>
'''
bot_template = '''
<div class="chat-message bot"><div class="avatar"><img src="https://i.ibb.co/cN0nmSj/Screenshot-2023-05-28-at-02-37-21.png"></div><div class="message">{{MSG}}</div></div>
'''
user_template = '''
<div class="chat-message user"><div class="avatar"><img src=""></div><div class="message">{{MSG}}</div></div>
'''
header_css = '''
<style>
.main-header { text-align: center; font-size: 1rem; font-weight: bold; color: #e8a507; padding: 1rem; background: transparent; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.4); display: inline-block; letter-spacing: 2px; }
.sub-header { text-align: right; font-size: 1.5rem; font-weight: normal; color: #870505; padding: 1rem; background: transparent; display: inline-block; margin-top: -20px; width: 100%; }
@media (max-width: 600px) { .main-header { font-size: 2.5rem; } .sub-header { font-size: 1.25rem; margin-right: 10%; } }
.question-label { font-size: 1.5rem; color: #cccccc; font-weight: bold; margin-top: 2rem; display: block; }
</style>
'''
question_label = '<div class="question-label">Ask a question about your documents:</div>'


def main():
    st.set_page_config(page_title="RAGReader Pro", page_icon=":books:")
    st.write(css, unsafe_allow_html=True)

     # Clear uploaded files on app start
    for filename in os.listdir(data_dir):
        file_path = os.path.join(data_dir, filename)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
        except Exception as e:
            st.error(f"Error deleting file {file_path}: {e}")

    # Initialize session state
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "vectors" not in st.session_state:
        st.session_state.vectors = None

    # Header
    st.write(header_css, unsafe_allow_html=True)
    st.markdown('<h1 class="main-header">RAGReader Pro</h1>', unsafe_allow_html=True)
    st.markdown('<h2 class="sub-header">Your Document Assistant</h2>', unsafe_allow_html=True)
    st.markdown(question_label, unsafe_allow_html=True)

    # Sidebar: upload & process
    with st.sidebar:
        st.subheader("Your documents")
        uploaded_files = st.file_uploader("Upload PDFs", type=["pdf"], accept_multiple_files=True)
        if st.button("Process"):
            if not uploaded_files:
                st.warning("Please upload at least one PDF file.")
            else:
                # Save files and build vectors
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

    # # User question input
    # user_question = st.text_input("Ask a question about your documents", label_visibility="collapsed")
    # if user_question:
    #     # Ensure vectors are ready and valid
    #     vecs = st.session_state.vectors
    #     if not vecs:
    #         st.warning("Please process some documents first.")
    #     elif isinstance(vecs, dict):
    #         st.error(f"Previous build error: {vecs['message']}")
    #     else:
    #         st.session_state.chat_history.append(f"You : {user_question}")
    #         response = query_documents(user_question, vecs)
    #         if "error" in response:
    #             st.error(f"⚠️ Retrieval error: {response['error']}")
    #         elif "no_result" in response:
    #             st.warning("Ran successfully, but no matching content found.")
    #         else:
    #             st.session_state.chat_history.append(response["answer"])

    # User question input within a form
    with st.form(key="question_form", clear_on_submit=True):
        user_question = st.text_input(
            "Ask a question about your documents",
            label_visibility="collapsed",
            placeholder="Type your question here..."
        )
        submitted = st.form_submit_button("Enter")
    
    if submitted and user_question:
        # Ensure vectors are ready and valid
        vecs = st.session_state.vectors
        if not vecs:
            st.warning("Please process some documents first.")
        elif isinstance(vecs, dict):
            st.error(f"Previous build error: {vecs['message']}")
        else:
            st.session_state.chat_history.append(f"You : {user_question}")
            response = query_documents(user_question, vecs)
            if "error" in response:
                st.error(f"⚠️ Retrieval error: {response['error']}")
            elif "no_result" in response:
                st.warning("Ran successfully, but no matching content found.")
            else:
                st.session_state.chat_history.append(response["answer"])    

    # Display chat history
    if st.session_state.chat_history:
        st.subheader("Chat Logs")
        for i, msg in enumerate(st.session_state.chat_history):
            tpl = user_template if i % 2 == 0 else bot_template
            st.markdown(tpl.replace("{{MSG}}", msg), unsafe_allow_html=True)

    # Clear/Delete
    if st.button("Clear Chat Logs"):
        st.session_state.chat_history.clear()
        st.success("Chat history cleared!")
    if st.button("Delete Uploaded Files"):
        for fn in os.listdir(data_dir): os.remove(os.path.join(data_dir, fn))
        st.session_state.vectors = None
        st.success("Uploaded files deleted!")

if __name__ == '__main__':
    main()
