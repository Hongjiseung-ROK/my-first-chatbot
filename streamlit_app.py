import streamlit as st
import os
from dotenv import load_dotenv
from openai import AzureOpenAI

# Load environment variables
load_dotenv()

def get_env_var(var_name, default=None):
    if var_name in st.secrets:
        return st.secrets[var_name]
    return os.getenv(var_name, default)

azure_oai_endpoint = get_env_var("AZURE_OAI_ENDPOINT")
azure_oai_key = get_env_var("AZURE_OAI_KEY")
azure_oai_deployment = get_env_var("AZURE_OAI_DEPLOYMENT")
azure_search_endpoint = get_env_var("AZURE_OAI_AISEARCH_URL")
azure_search_key = get_env_var("AZURE_OAI_AISEARCH_KEY")
azure_search_index = get_env_var("AZURE_OAI_AISEARCH_INDEX", "margiestravel")

# Initialize Client
client = AzureOpenAI(
    azure_endpoint=azure_oai_endpoint,
    api_key=azure_oai_key,
    api_version="2024-02-15-preview"
)

st.title("Math Tutor Chatbot : Mathbot 🤖➕➖✖️➗")

# System Prompt
try:
    with open("system.txt", "r", encoding="utf8") as f:
        system_text = f.read().strip()
except FileNotFoundError:
    system_text = "You are a helpful AI assistant."

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("메시지를 입력하세요..."):
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Prepare messages for API call
    # Include system message first
    api_messages = [{"role": "system", "content": system_text}]
    # Add history
    api_messages.extend(st.session_state.messages)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            response = client.chat.completions.create(
                model=azure_oai_deployment,
                messages=api_messages,
                extra_body={
                    "data_sources": [
                        {
                            "type": "azure_search",
                            "parameters": {
                                "endpoint": azure_search_endpoint,
                                "index_name": azure_search_index,
                                "authentication": {
                                    "type": "api_key",
                                    "key": azure_search_key
                                }
                            }
                        }
                    ]
                }
            )
            full_response = response.choices[0].message.content
            message_placeholder.markdown(full_response)
        except Exception as e:
            st.error(f"Error: {e}")

    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": full_response})
