import hashlib
import json
import os
import streamlit as st
import requests
from streamlit_lottie import st_lottie
from streamlit_extras.stylable_container import stylable_container

# --- Set Page Configuration First ---
st.set_page_config(page_title="AI Chatbot", page_icon="🤖", layout="wide")

# --- Helper Functions ---
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def load_users(filepath="users.json"):
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            return json.load(f)
    return {}

def save_users(users, filepath="users.json"):
    with open(filepath, "w") as f:
        json.dump(users, f)

# Helper functions to load and save user questions
def load_user_questions(filepath="user_questions.json"):
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            return json.load(f)
    return {}

def save_user_questions(user_questions, filepath="user_questions.json"):
    with open(filepath, "w") as f:
        json.dump(user_questions, f)

# --- Initialize Persistent Data ---
users_file = "users.json"
users = load_users(users_file)

# --- Initialize Session State ---
if 'users' not in st.session_state:
    st.session_state['users'] = users  # load persistent users into session state
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'username' not in st.session_state:
    st.session_state['username'] = ""
if 'user_questions' not in st.session_state:
    st.session_state['user_questions'] = load_user_questions()

# --- Authentication UI (visible when not logged in) ---
if not st.session_state.get("logged_in"):
    auth_option = st.sidebar.radio("Authentication", ("Login", "Sign Up"))
    
    if auth_option == "Sign Up":
        st.sidebar.subheader("Create New Account")
        new_username = st.sidebar.text_input("Username", key="signup_username")
        new_password = st.sidebar.text_input("Password", type="password", key="signup_password")
        if st.sidebar.button("Sign Up"):
            if new_username and new_password:
                if new_username in st.session_state['users']:
                    st.sidebar.error("Username already exists!")
                else:
                    st.session_state['users'][new_username] = hash_password(new_password)
                    save_users(st.session_state['users'], users_file)
                    st.sidebar.success("Account created successfully! Please log in.")
            else:
                st.sidebar.error("Please provide both username and password.")
    
    if auth_option == "Login":
        st.sidebar.subheader("Login")
        username = st.sidebar.text_input("Username", key="login_username")
        password = st.sidebar.text_input("Password", type="password", key="login_password")
        if st.sidebar.button("Login"):
            stored_users = st.session_state['users']
            if username in stored_users and stored_users[username] == hash_password(password):
                st.session_state['logged_in'] = True
                st.session_state['username'] = username
                # Ensure the user's questions list exists
                if username not in st.session_state['user_questions']:
                    st.session_state['user_questions'][username] = []
                st.sidebar.success(f"Welcome {username}!")
            else:
                st.sidebar.error("Invalid username or password.")

# If the user is logged in, show the chatbot interface
if st.session_state.get("logged_in"):
    # Function to load Lottie animations
    def load_lottie_url(url: str):
        response = requests.get(url)
        if response.status_code != 200:
            return None
        return response.json()

    # Load welcome animation
    lottie_welcome = load_lottie_url("https://assets5.lottiefiles.com/packages/lf20_V9t630.json")

    # Set page configuration (it should be called only once, and at the very beginning)
    # Already handled earlier in the code

    # st.header(":orange[AI Assistant is] :blue[cool] :sunglasses:",divider="orange")

    # Initialize session state for conversation history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Function to send user input to FastAPI backend
    def get_bot_response(user_input):
        try:
            response = requests.post("http://34.233.136.94:8000/chat/", json={"prompt": user_input})
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            return f"Error: {e}"

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"], avatar=message["avatar"]):
            st.markdown(message["content"])

    # User input
    if prompt := st.chat_input("Ask me anything about insurance..."):
        st.session_state.messages.append({"role": "user", "content": prompt, "avatar": "🧑‍💼"})
        with st.chat_message("user", avatar="🧑‍💼"):
            st.markdown(prompt)

        # Get response from FastAPI backend
        response = get_bot_response(prompt)
        st.session_state.messages.append({"role": "assistant", "content": response, "avatar": "🤖"})

        with st.chat_message("assistant", avatar="🤖"):
            st.markdown(response)

        # Save user question to persistent storage (optional)
        if st.session_state['username'] not in st.session_state['user_questions']:
            st.session_state['user_questions'][st.session_state['username']] = []
        st.session_state['user_questions'][st.session_state['username']].append(prompt)
        save_user_questions(st.session_state['user_questions'])
else:
      st.info("Please log in to use the app.")
 
