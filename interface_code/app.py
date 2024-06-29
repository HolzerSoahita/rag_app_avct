import streamlit as st
from advanced_chatbot.services.rag_service import RagService
import os
from pathlib import Path


# Session state variable
if 'file_list' not in st.session_state:
    st.session_state['file_list'] = []

if 'current_index_id' not in st.session_state:
    st.session_state['current_index_id'] = ""


# custom CSS 

st.markdown("""
    <style>            
        .stButton>button {
            border: none;
            background-color : #F0F2F6;
        }
        
        h1 {
            border-bottom: 1px solid #000;
            }
    </style>
    """, unsafe_allow_html=True)

# Sidebar
## Sidebar title
st.sidebar.title("Fichiers")

## Uploaded Button
uploaded_file = st.sidebar.file_uploader("Ajouter votre fichier ici", type=['pdf', 'docx'])
if uploaded_file is not None:

    if not os.path.exists("upload"):
        os.mkdir("upload")

    with open(f"upload/{uploaded_file.name}", "wb") as f:
        f.write(uploaded_file.getbuffer())

    doc_path = Path(f"upload/{uploaded_file.name}")
    index_id, _ = RagService.create_vector_store_index(doc_path)

    st.session_state['file_list'].append((uploaded_file.name,index_id))
    st.session_state['current_index_id'] = index_id

    os.remove(doc_path)


##Files
### Function for deleting files
def delete_file(index_id):
    # Remove the vectore store index
    RagService.delete_vector_store_index(index_id)
    # Remove the corresponding entry from the session state
    st.session_state['file_list'] = [item for item in st.session_state['file_list'] if item[1] != index_id]


### Show all of the uploaded file
for i, (file_name, index_id) in enumerate(st.session_state['file_list']):
    col1, col2 = st.sidebar.columns(2)
    button1 = col1.button(file_name, key=f"button_{i}",use_container_width=True)
    button2 = col2.button('delete', key=f"trash_button_{i}",use_container_width=True,on_click=lambda: delete_file(index_id))


# Chat interface
## st.title("ChatGPT-like clone")
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Chatter ici"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        output_stream, sources = RagService.complete_chat(prompt, [], [st.session_state['current_index_id']])
        response = st.write_stream(output_stream)
    st.session_state.messages.append({"role": "assistant", "content": response})





