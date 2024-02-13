import streamlit as st
import pandas as pd
import api
from rag import RAG
from PyPDF2 import PdfReader

st.title("Chat with your mixed data")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.system = """write python code for data analysis

query: how many rows are there in data ?
python: df.shape[0]"""
    st.session_state.counter = 2
    st.session_state.data = []
    st.session_state.RAG = False

# system = """write python code for data analysis

# query: how many rows are there in data ?
# python: df.shape[0]"""

def preprocess(prompt):
    print(f"[INFO] >>> reached preprocess")
    system = st.session_state.system
    system += f"""

query: {prompt}
python:"""
    print(f"[INFO] >>> {system} passed to model")
    st.session_state.system = system
    return {"inputs": system,}

def post_process(resp):
    print(f"[INFO] >>> reached post process")
    df = st.session_state.data
    placeholder = {"df":df}
    system = st.session_state.system
    counter = st.session_state.counter
    print(f"[INFO] >>> {resp}")
    temp = resp[0]['generated_text'].split("python:")[counter].split("\n")
    
    try:
        code = temp[0].strip()
        print(f"[INFO] >>> code : {code}")
        exec(f"result = {code}", placeholder)
        exec_result = placeholder["result"]
        next_answer = f""" {temp[0].strip()}"""
    except Exception as e:
        print(f"[ERROR] >>>> {e}")
        exec_result = "Faced an error while executing code"
        code = code
        next_answer = code
    system += next_answer
    counter +=1
    st.session_state.system = system
    st.session_state.counter = counter
    return code, exec_result


file = st.file_uploader("choose a file",type=["csv", "xlsx", "pdf","xls","xlsm","xlsb"])
if file:
    print(f"[infp] >>> {file.name}")
    if file.name.split(".")[-1] == "csv":
        df = pd.read_csv(file)
        st.session_state.data = df
        print(f"[INFO] >>> data frame loaded")

    if file.name.split(".")[-1] == "pdf":
        # documents = [file.read().decode('unicode_escape')]
        # documents = file.getbuffer()
        pdf_reader = PdfReader(file)
        documents = ""
        for page in pdf_reader.pages:
            documents += page.extract_text()
        print(f"[EDA] >>> {documents[:50]}")
        st.session_state.RAG = RAG(documents)

    if file.name.split(".")[-1] in ["xls","xlsx","xlsm","xlsb"]:
        df = pd.read_excel(file)
        st.session_state.data = df
    print(f"[INFO] data frame loaded")

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("What is up?"):
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    print(f"[INFO] >> {prompt} , {len(st.session_state.data)}")

    try:
        if len(st.session_state.data):
            print(f"\n\n\ninfo >>>>> {st.session_state.system}")
            pre_query = preprocess(prompt) 
            resp = api.query(pre_query)
            code, exec_value = post_process(resp)
            # Display assistant response in chat message container
            with st.chat_message("assistant"):
                st.markdown(exec_value)
                st.code(f"{code}")
            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": code})
        elif st.session_state.RAG != None:
            rag = st.session_state.RAG
            result = rag.query(prompt)
            with st.chat_message("assistant"):
                st.markdown(result)
            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": result})

    except Exception as e:
        print(f"[ERROR] >>>> {e}")
        code = "HuggingFace Error"
        exec_value = " Exception Raised"
        with st.chat_message("assistant"):
            st.markdown(exec_value)
            st.code(f"{code}")
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": code})
