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


## Show all of the uploaded file
for i, (file_name, index_id) in enumerate(st.session_state['file_list']):
    col1, col2 = st.sidebar.columns(2)
    button1 = col1.button(file_name, key=f"button_{i}",use_container_width=True)
    button2 = col2.button('delete', key=f"trash_button_{i}",use_container_width=True)






