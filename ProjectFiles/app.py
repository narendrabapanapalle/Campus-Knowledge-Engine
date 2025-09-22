import streamlit as st
import uuid
import os
import warnings
from langchain_core._api.deprecation import LangChainDeprecationWarning
warnings.filterwarnings("ignore", category=LangChainDeprecationWarning)
from dotenv import load_dotenv

# --- Core LangChain components ---
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import SQLChatMessageHistory

import base64
from pinecone import Pinecone
from PIL import Image

# Import system template and auth components
from system_template import SYSTEM_TEMPLATE
from auth import AuthManager
from database import DatabaseManager

# ---------------- Load Environment Variables ---------------------------
load_dotenv()
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
INDEX_NAME = "langchain-pinecone-demo"

if not PINECONE_API_KEY or not OPENAI_API_KEY:
    st.error("❌ API key not found. Set PINECONE_API_KEY and OPENAI_API_KEY in your .env file")
    st.stop()

# Database and Auth Setup
if "db_manager" not in st.session_state:
    st.session_state.db_manager = DatabaseManager()
if "auth_manager" not in st.session_state:
    st.session_state.auth_manager = AuthManager()

def get_session_history(session_id: str):
    """Get chat history for a session"""
    return SQLChatMessageHistory(
        session_id=session_id,
        table_name="chat_history",
        connection_string="sqlite:///users.db"
    )

# ----------------- Helper function for bot page styling ------------------
def set_bot_background_and_styling():
    """Set background image and custom styling for bot interface"""
    # Try to load background image
    background_style = ""
    if os.path.exists("background.jpg"):
        try:
            with open("background.jpg", "rb") as f:
                img_data = f.read()
            b64_encoded = base64.b64encode(img_data).decode()
            background_style = f"""
                background-image: linear-gradient(rgba(0,0,0,0.6), rgba(0,0,0,0.6)), url(data:image/jpeg;base64,{b64_encoded});
                background-size: cover;
                background-position: center;
                background-repeat: no-repeat;
                background-attachment: fixed;
            """
        except:
            background_style = "background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);"
    else:
        background_style = "background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);"
    
    style = f"""
        <style>
        .stApp {{
            {background_style}
        }}
        [data-testid="stHeader"] {{
            background: rgba(0,0,0,0);
        }}
        [data-testid="stSidebar"] > div:first-child {{
            background: rgba(28, 28,28,0.9);
            backdrop-filter: blur(10px);
        }}
        [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {{
            background-color: rgba(32, 49, 63, 0.8);
            border-radius: 15px;
            border: 1px solid #3c4a56;
            margin-right: 10px;
        }}
        [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {{
            background-color: rgba(32, 49, 63, 0.8);
            border-radius: 15px;
            border: 1px solid #3c4a56;
            margin-left: 10px;
        }}
        [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) [data-testid="stChatMessageContent"] p {{
            color: #FFD700 !important;
        }}
        [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) [data-testid="stChatMessageContent"] p {{
            color: white;
        }}
        [data-testid="stChatInput"] {{
            background-color: rgba(38, 49, 62, 0.9);
            border-top: 1px solid #6a7989;
        }}
        [data-testid="textInputRoot"] input {{
            color: white;
        }}
        .auth-container {{
            background: rgba(28, 28, 28, 0.9);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 2rem;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }}
        .welcome-text {{
            color: white;
            text-align: center;
            margin-bottom: 2rem;
        }}
        </style>
    """
    st.markdown(style, unsafe_allow_html=True)

# ----------------- Lazy Loading Functions -------------------------------------

@st.cache_resource(show_spinner=False)
def get_pinecone_client():
    """Initialize Pinecone client with caching - only when needed"""
    return Pinecone(api_key=PINECONE_API_KEY)

@st.cache_resource(show_spinner=False)
def load_embeddings():
    """Load embeddings with caching and faster model - only when needed"""
    # Use a faster, smaller model for better performance
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True, 'batch_size': 32}
    )

@st.cache_resource(show_spinner=False)
def get_chat_model():
    """Initialize chat model with caching - only when needed"""
    return ChatOpenAI(
        model="gpt-3.5-turbo-1106", 
        temperature=0.5, 
        api_key=OPENAI_API_KEY,
        max_tokens=1000,  # Limit tokens for faster response
        timeout=30  # Add timeout
    )

@st.cache_resource(show_spinner=False)
def setup_vector_store():
    """Setup vector store with caching - only when needed"""
    embeddings = load_embeddings()
    return PineconeVectorStore.from_existing_index(
        embedding=embeddings, 
        index_name=INDEX_NAME
    )

@st.cache_resource(show_spinner=False)
def setup_rag_chain():
    """Setup complete RAG chain with caching - only when user sends first message"""
    try:
        # Load components silently
        chat = get_chat_model()
        vector_store = setup_vector_store()
        retriever = vector_store.as_retriever(search_kwargs={"k": 3})
        
        # Create contextualize question prompt
        contextualize_q_system_prompt = """Given a chat history and the latest user question \
which might reference context in the chat history, formulate a standalone question \
which can be understood without the chat history. Do NOT answer the question, \
just reformulate it if needed and otherwise return it as is."""
        
        contextualize_q_prompt = ChatPromptTemplate.from_messages([
            ("system", contextualize_q_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ])
        
        # Create history-aware retriever
        history_aware_retriever = create_history_aware_retriever(
            chat, retriever, contextualize_q_prompt
        )
        
        # Modify the system template
        modified_system_template = SYSTEM_TEMPLATE.replace(
            "- Legal Disclaimer",
            "❖ Legal Disclaimer"
        ).replace(
            "{context}",
            "*Context from retrieved documents:*\n{context}"
        )
        
        # Create QA prompt
        qa_prompt = ChatPromptTemplate.from_messages([
            ("system", modified_system_template),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ])
        
        # Create document chain
        question_answer_chain = create_stuff_documents_chain(chat, qa_prompt)
        
        # Create RAG chain
        rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)
        
        return rag_chain
        
    except Exception as e:
        return None

# ----------------- Authentication Functions ---------------------------------
def check_authentication():
    """Check if user is authenticated"""
    return "user_id" in st.session_state and st.session_state.user_id is not None

def show_user_profile_sidebar():
    """Show user profile in sidebar"""
    user_id = st.session_state.get("user_id")
    if not user_id:
        return
    
    # Get user's profile picture or use default
    profile_pic = st.session_state.auth_manager.get_user_profile_picture(user_id)
    
    # Welcome message
    if "user_name" in st.session_state:
        st.markdown(f"**Welcome, {st.session_state.user_name}!**")
    
    st.markdown("---")
    
    # Profile picture
    if profile_pic:
        st.image(profile_pic, width=150)
    else:
        # Default profile icon with user's initial
        user_name = st.session_state.get("user_name", "User")
        initial = user_name[0].upper() if user_name else "U"
        
        # Create a circular profile icon using HTML/CSS
        st.markdown(f"""
        <div style="
            width: 150px; 
            height: 150px; 
            border-radius: 50%; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            display: flex; 
            align-items: center; 
            justify-content: center; 
            color: white; 
            font-weight: bold; 
            font-size: 48px;
            margin: 0 auto;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        ">{initial}</div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Simple action buttons - no session management UI
    if st.button("📝 Delete Chat", key="new_chat_btn", use_container_width=True):
        # Clear current chat history but keep same session
        session_id = st.session_state.get("session_id")
        if session_id:
            history = get_session_history(session_id)
            history.clear()
        st.rerun()
    
    st.markdown("---")
    
    # Action buttons
    if st.button("👤 View Profile", key="sidebar_profile_btn", use_container_width=True):
        st.session_state.show_profile = True
        st.rerun()
    
    if st.button("🚪 Logout", key="sidebar_logout_btn", type="secondary", use_container_width=True):
        st.session_state.auth_manager.logout()
        st.rerun()
    
    st.markdown("---")
    
    # Additional info
    st.markdown("### ℹ️ About")
    st.markdown("** Campus Knowledge Engine is your AI-powered campus guide. Ask any question about admissions, courses, faculty, facilities, placements, or student life, and get comprehensive answers tailored to your college.**")

def show_legalbot_interface():
    """Show the main LegalBot interface"""
    st.set_page_config(
        page_title="Campus Knowledge Engine ",
        page_icon="⚖️",
        layout="wide"
    )
    
    set_bot_background_and_styling()
    
    # Sidebar - always visible
    with st.sidebar:
        st.markdown("### 👤 User Profile")
        show_user_profile_sidebar()
    
    # Main interface
    if st.session_state.get("show_profile", False):
        # Show profile page
        col1, col2 = st.columns([1, 4])
        
        with col1:
            if st.button("← Back to LegalBot", type="secondary"):
                st.session_state.show_profile = False
                st.rerun()
        
        with col2:
            st.title("Campus Knowledge Engine- Profile")
        
        st.divider()
        st.session_state.auth_manager.show_profile_page(st.session_state.user_id)
    
    else:
        # Main chat interface
        # Banner Section
        st.markdown("""
            <div style="text-align: center; padding: 2rem 0; color: white;">
                <h1 style="font-size: 3em; margin-bottom: 0;">Campus Knowledge Engine</h1>
                <p style="font-size: 1.2em; opacity: 0.8;">Your College Research Assistant</p>
            </div>
        """, unsafe_allow_html=True)
        
        # Get current session and update access time
        session_id = st.session_state.get("session_id")
        if session_id:
            st.session_state.db_manager.update_session_access_time(st.session_state.user_id, session_id)
            
            # Load and display chat history immediately - no waiting for AI components
            history = get_session_history(session_id)
            
            # Convert LangChain messages to displayable format
            if hasattr(history, 'messages') and history.messages:
                for message in history.messages:
                    role = "user" if message.type == "human" else "assistant"
                    avatar = "🧑‍⚖️" if role == "user" else "🤖"
                    with st.chat_message(role, avatar=avatar):
                        if role == "user":
                            # Use st.write with HTML for better rendering
                            st.write(f'<span style="color: #FFD700;">{message.content}</span>', unsafe_allow_html=True)
                        else:
                            st.markdown(message.content)
            else:
                # Show welcome message for new chats
                with st.chat_message("assistant", avatar="🤖"):
                    st.markdown("Hi, I'm CollegeBot. Ask me any college research question.")
            
            # Handle new user input
            if prompt := st.chat_input("What  question can I help you with?"):
                # Display user message with yellow color using st.write
                with st.chat_message("user", avatar="🧑‍⚖️"):
                    st.write(f'<span style="color: #FFD700;">{prompt}</span>', unsafe_allow_html=True)
                
                # Generate and display assistant response
                with st.chat_message("assistant", avatar="🤖"):
                    with st.spinner("🔍 Searching legal documents and generating response..."):
                        try:
                            # Get RAG chain only when user sends message - truly lazy loading
                            rag_chain = setup_rag_chain()
                            
                            if rag_chain is not None:
                                # Create conversational RAG chain with message history
                                conversational_rag_chain = RunnableWithMessageHistory(
                                    rag_chain,
                                    get_session_history,
                                    input_messages_key="input",
                                    history_messages_key="chat_history",
                                    output_messages_key="answer",
                                )
                                
                                # Get response from RAG chain
                                response = conversational_rag_chain.invoke(
                                    {"input": prompt},
                                    config={
                                        "configurable": {"session_id": session_id}
                                    },
                                )
                                
                                # Extract and display the answer
                                answer = response.get("answer", "Sorry, I couldn't generate a response.")
                                st.markdown(answer)
                            else:
                                st.error("Failed to initialize AI components. Please try again.")
                                
                        except Exception as e:
                            error_message = f"An error occurred: {str(e)}"
                            st.error(error_message)

# ----------------- Main App Logic ---------------------------------
def main():
    """Main application logic"""
    if not check_authentication():
        # Show login page - no pre-loading here
        st.session_state.auth_manager.show_auth_page()
    else:
        # User is authenticated, show bot interface immediately
        show_legalbot_interface()

if __name__ == "__main__":
    main()