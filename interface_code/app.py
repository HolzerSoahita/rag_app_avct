import streamlit as st
import streamlit.components.v1 as components
from advanced_chatbot.services.rag_service import RagService
import os
from pathlib import Path


# Session state variable
if 'file_list' not in st.session_state:
    st.session_state['file_list'] = []

if 'current_index_id' not in st.session_state:
    st.session_state['current_index_id'] = ""

if "uploader_key" not in st.session_state:
    st.session_state["uploader_key"] = 1


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

### Modal dialog to show the summary of a book
@st.experimental_dialog("Résumé")
def vote(file_name,summary):
    st.header("Fichier : ")
    st.write(file_name)
    st.header("Contenu : ")
    st.write(summary)
    st.header("Langue : ")
    st.write("Français")

### Show modal
def show_dialog(file_name,summary):
    vote(file_name,summary)

## Uploaded Button
uploaded_file = st.sidebar.file_uploader("Ajouter votre fichier ici", type=['pdf', 'docx'],key=st.session_state["uploader_key"])

if uploaded_file is not None:
    # Creation of the upload folder
    if not os.path.exists("upload"):
        os.mkdir("upload")

    # Saving the uploaded file temporary
    with open(f"upload/{uploaded_file.name}", "wb") as f:
        f.write(uploaded_file.getbuffer())

    # Creation of the vector store index
    doc_path = Path(f"upload/{uploaded_file.name}")
    index_id, _ = RagService.create_vector_store_index(doc_path)

    # Creation of the summary
    language = RagService.detect_document_language(index_id)
    if language.lower() == "fr":
        summary = RagService.summarize_document_index(index_id)
    else :
        summary = RagService.translate_and_summarize_first_page_fr(index_id) 

    # Saving to the user session
    st.session_state['file_list'].append((uploaded_file.name,index_id,summary))
    st.session_state['current_index_id'] = index_id

    # Remove the temporary uploaded file
    os.remove(doc_path)

    # Show the summary of the file
    show_dialog(uploaded_file.name,summary)

    # Clear the content of the st.sidebar.file_uploader
    st.session_state["uploader_key"] += 1
    st.rerun()


##Files
### Function for deleting files
def delete_file(index_id):
    # Remove the vectore store index
    RagService.delete_vector_store_index(index_id)
    # Remove the corresponding entry from the session state
    st.session_state['file_list'] = [item for item in st.session_state['file_list'] if item[1] != index_id]


### Show all of the uploaded file
for i, (file_name, index_id,summary) in enumerate(st.session_state['file_list']):
    col1, col2 = st.sidebar.columns(2)
    button1 = col1.button(file_name, key=f"button_{i}",use_container_width=True,on_click=lambda: show_dialog(file_name,summary))
    button2 = col2.button('🗑️', key=f"trash_button_{i}",use_container_width=True,on_click=lambda: delete_file(index_id))



# Chat interface
## Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

## Display the warning message only if there are no messages in the chat
if not st.session_state.messages:
    st.markdown("""
        <style>
        .center-content {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;  # Adjust this value as needed
        }
        </style>
        <div class="center-content">
            <h2>Attention!, ces textes sont générés par l'IA</h2>
        </div>
        """, unsafe_allow_html=True)
    # st.markdown("<center><h2>Attention!, Ces chats sont générés par l'IA</h2></center>", unsafe_allow_html=True)

## Display the chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

### Modal dialog to say to add file
@st.experimental_dialog("Fichier manquant")
def warning_file():
    st.write("Ajouter un fichier PDF ou docx pour pouvoir commencer à chatter")


### Show modal warning file
def show_dialog_warning_file():
    warning_file()

## Get user input
if prompt := st.chat_input("Chatter ici") :
    if st.session_state['current_index_id'] != "" :
        # Add user message to session state
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate AI response
        with st.chat_message("assistant"):
            output_stream, sources = RagService.complete_chat(prompt, [], [st.session_state['current_index_id']])
            response = st.write_stream(output_stream)

        # Add AI response to session state
        st.session_state.messages.append({"role": "assistant", "content": response})

        # Add a button to display the source
        text = f"Source : {sources[0].text}"
        st.markdown(text)

    else:
        # Test si il y a déjà ajout de document
        show_dialog_warning_file()





