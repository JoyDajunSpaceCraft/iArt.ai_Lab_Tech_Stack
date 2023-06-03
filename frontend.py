import streamlit as st
import requests
from transformers import pipeline
import networkx as nx
import matplotlib.pyplot as plt

def send_file(file):
    response = requests.post('http://localhost:5000/upload', files={'file': file})
    return response.json()
from streamlit import session_state as state

# Session state workaround
def get_state(**kwargs):
    if 'get' not in state:
        state.get = State(**kwargs)
    return state.get

class State:
    def __init__(self, **kwargs):
        for key, val in kwargs.items():
            setattr(self, key, val)

def generate_response(user_input, model):
    if model == 'ChatGPT':
        response = f"Bot (ChatGPT): I received your message, '{user_input}'."

    elif model == 'LLama':
        response = f"Bot (LLama): Your message, '{user_input}', has been processed."
    elif model == "Vicuna":
        response = f"Bot (Vicuna): Message received: '{user_input}'."
    else:
        generator = pipeline('text-generation', model='distilgpt2')
        response = generator(user_input, max_length=50)[0]['generated_text']

    return response
# Main Streamlit app
def main():
    if 'chat_log' not in st.session_state:
        # If it's not present, initialize it
        st.session_state['chat_log'] = []
    st.title("Streamlit Chatbot")
    # Add a sidebar
    st.sidebar.header("Settings")
    model = st.sidebar.selectbox("Select the Model", ['ChatGPT', 'LLama', 'Vicuna',"GPT2"])

    user_input = st.text_input("Type your message")

    if st.button("Send"):
        # Update the chat log
        st.session_state.chat_log.append(f"You: {user_input}")

        # Generate a response
        response = f"Bot: I received your message, '{user_input}'."
        response = generate_response(user_input, model)
        st.session_state.chat_log.append(response)

        # Clear the input box after sending the message
        st.session_state.user_input = ""

    # Display chat log
    for message in st.session_state.chat_log:
        st.write(message)
    G = nx.Graph()
    for i, message in enumerate(st.session_state.chat_log):
        if i == 0:
            G.add_node(message)
        else:
            G.add_edge(st.session_state.chat_log[i - 1], message)
    fig, ax = plt.subplots(figsize=(8, 6))  # Add this line
    nx.draw(G, with_labels=True, ax=ax)  # Pass ax to nx.draw()
    st.pyplot(fig)  # Pass fig to st.pyplot()

    uploaded_file = st.file_uploader("Choose a file", type=['csv', 'xlsx'])

    if uploaded_file is not None:
        result = send_file(uploaded_file)
        st.write(f'File saved as {result["filename"]}')


if __name__ == "__main__":
    main()