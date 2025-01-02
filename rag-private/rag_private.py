from embedchain import App
import streamlit as st
import tempfile
import os
from streamlit_chat import message
from io import StringIO

def embedchain_init(db_path):
    return App.from_config(
        config={
      "llm": {
            "provider": "ollama",
            "config": {
                  "model": "llama3.2:latest",
                  "max_tokens": 250,
                  "system_prompt": "Give the anwser more clearly in point from with easy to read",
                  "prompt": "Use the following pieces of context to answer the query at the end.\nIf you don't know the answer, just say that you don't know, don't try to make up an answer.\n$context\n\nQuery: $query\n\nHelpful Answer:",
                  "temperature": 0.5,
                  "stream": True,
                  "base_url": 'http: //localhost:11434',
            }
      },
      "vectordb": {
            "provider": "chroma",
            "config": {
                  "dir": db_path
            }
      },
      "embedder": {
            "provider": "ollama",
            "config": {
                  "model": "llama3.2:latest",
                  "base_url": 'http: //localhost:11434',
                }
            }     
        }
    )


def make_db_path():
    ret = tempfile.mkdtemp(suffix="chroma")
    print(f"Created Chroma DB at {ret}")    
    return ret




# build interface
st.title('Private GPT with OLama')
st.caption('Localy hosted RAG with Lama 3.2')

# vector store storage
db_path = tempfile.mktemp()


print(f'file nme {db_path}')

#Create  a sessin state to store

if 'app' not in st.session_state:
    st.session_state.app = embedchain_init(db_path)
if 'messages' not in st.session_state:
    st.session_state.messages =[]

with st.sidebar:
    st.header("your Contract")
    pdf_file= st.file_uploader("upload file", type='pdf')
    if pdf_file: 
        if st.button('Add to Knowladge'): 
            with st.spinner("Adding PDF to Knowladge..."): 
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as f:
                    f.write(pdf_file.getvalue())
                    st.session_state.app.add(f.name, data_type='pdf_file')
                os.remove(f.name)
            st.success(f'Added {pdf_file.name} to Knoladge!')
        
        
# Chat interface
for i, msg in enumerate(st.session_state.messages):
    message(msg["content"], is_user=msg["role"] == "user", key=str(i))


if prompt := st.chat_input("Ask a question about the PDF"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    message(prompt, is_user=True)

    with st.spinner("Loading..."):
        response = st.session_state.app.chat(prompt)
        st.session_state.messages.append({"role": "assistant", "content": response})
        message(response)

# Clear chat history button
if st.button("Clear Chat History"):
    st.session_state.messages = []