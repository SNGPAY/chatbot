import streamlit as st
from datetime import datetime
from streamlit_option_menu import option_menu
from typing import Annotated, TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_community.chat_models import ChatOllama
from langchain_core.tools import tool

from langchain_core.messages import HumanMessage, AIMessage


# 1. Define LangGraph State and Logic
class State(TypedDict):
    # Annotated with add_messages so new messages append to history
    messages: Annotated[list, add_messages]

def chatbot_node(state: State):

    predefined_intents = [
        "purchase", 
        "sale"
    ]

    prompt = f"""
    You are an AI assistant. Classify the user's input into exactly one of the following intents:
    {', '.join(predefined_intents)}
    
    User input: "{state["messages"]}"
    Output ONLY the intent name.
    """

    print("Prompt sent to LLM:", datetime.now())  # Debugging statement
    llm = ChatOllama(model="llama3",temperature =0.0)
    llm_with_tools  = llm.bind_tools(tools)
    response = llm_with_tools.invoke(prompt)

    print("LLM response:", datetime.now())  # Debugging statement

    chain = AIMessage(content=(response.content.strip().upper()))

    if chain == "PURCHASE":
        response = AIMessage(content="You want to make a purchase. Here are some options: ...")
    else:        response = AIMessage(content="You want to make a sale. Here are some options: ...")

    return {"messages": [response]}

@tool
def get_weather(city: str):
    """Use this tool to check the current weather in a specific city."""
    return f"The weather in {city} is sunny and 75°F."

@tool
def search_web(query: str):
    """Use this tool for general questions about news, events, or facts."""
    return f"Search result for '{query}': LangGraph is a framework for building stateful agents."

tools = [get_weather, search_web]

def identification_node(llm_with_tools):

    response = llm.invoke("Identify yourself");

    return response

def get_app():

    llm = ChatOllama(model="llama3",temperature =0.9)
    #llm_with_tools  = llm.bind_tools(tools)

    workflow = StateGraph(State)
    workflow.add_node("chatbot", chatbot_node)
    workflow.add_edge(START, "chatbot")
    workflow.add_edge("chatbot", END)
    return workflow.compile()


st.set_page_config(
    page_title="AI Workspace",
    page_icon="🤖",
    layout="wide"
)

# ---------------------------
# Session State
# ---------------------------

if "page" not in st.session_state:
    st.session_state.page = "Explore Apps"

if "selected_app" not in st.session_state:
    st.session_state.selected_app = None

if "messages" not in st.session_state:
    st.session_state.messages = {}

# ---------------------------
# Sample Apps
# ---------------------------

APPS = [
    {
        "name": "Payment Assistant",
        "category": "Payment",
        "image": "image/payment_image.png",
        "description": "Receive Tenant Payment, Payout"
    },
    {
        "name": "Maintenance Assistant",
        "category": "Maintenance",
        "image": "image/maintenance_image.png",
        "description": "Raise maintenance request, track status"
    },
    {
        "name": "Finance Assistant",
        "category": "Finance",
        "image": "image/finance_image.png",
        "description": "Financial insights and KPI reporting."
    },
    {
        "name": "Collaboration Assistant",
        "category": "Collaboration",
        "image": "image/collaboration_image.png",
        "description": "House committee and tenant communication assistant."
    },
    {
        "name": "Legal Assistant",
        "category": "Legal",
        "image": "https://picsum.photos/500/300?5",
        "description": "Contract review and legal document support."
    },
    {
        "name": "Data Analyst",
        "category": "Analytics",
        "image": "https://picsum.photos/500/300?6",
        "description": "Business intelligence and dashboard assistant."
    }
]

# ---------------------------
# Styling
# ---------------------------

st.markdown("""
<style>

.main {
    background:#343541;
}

.card {
    background:#202123;
    border-radius:15px;
    padding:15px;
    border:1px solid #444654;
    margin-bottom:15px;
}

.card:hover{
    border:1px solid #10A37F;
}

.app-title{
    font-size:20px;
    font-weight:600;
    color:white;
}

.app-category{
    color:#10A37F;
    font-size:12px;
}

.app-desc{
    color:#d1d5db;
    font-size:14px;
}

</style>
""", unsafe_allow_html=True)

# ---------------------------
# Sidebar
# ---------------------------

with st.sidebar:

    st.title("Smart Home AI Assistant")

    selected = option_menu(
        "",
        ["New Chat", "Explore Apps", "My Apps"],
        icons=["chat", "grid", "robot"],
        default_index=1
    )

    st.divider()

    st.subheader("Recent Chats")

    for app_name in st.session_state.messages.keys():

        if st.button(
            app_name,
            use_container_width=True
        ):
            st.session_state.selected_app = app_name
            st.session_state.page = "chat"

# ---------------------------
# New Chat
# ---------------------------

if selected == "New Chat":

    st.title("Welcome")

    st.markdown("""
    ## What can I help with?

    Choose an App from the sidebar.
    """)

# ---------------------------
# Explore Apps
# ---------------------------

elif selected == "Explore Apps":

    st.title("Explore Apps")

    search = st.text_input(
        "",
        placeholder="Search apps..."
    )

    filtered = [
        a for a in APPS
        if search.lower() in a["name"].lower()
    ]

    cols = st.columns(3)

    for i, app in enumerate(filtered):

        with cols[i % 3]:

            st.markdown(f"### {app['name']}")    
            st.caption(app["category"])
            st.write(app["description"])
            st.image(
                app["image"],
                use_container_width=True
            )
     
            if st.button(
                "Open",
                key=app["name"]
            ):
                st.session_state.selected_app = app["name"]

                if app["name"] not in st.session_state.messages:
                    st.session_state.messages[app["name"]] = []

                st.rerun()

# ---------------------------
# Chat Screen
# ---------------------------

if st.session_state.selected_app:

    st.divider()

    st.title(
        f"💬 {st.session_state.selected_app}"
    )

    history = st.session_state.messages[
        st.session_state.selected_app
    ]

    for msg in history:

        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    prompt = st.chat_input(
        f"Message {st.session_state.selected_app}"
    )

    if prompt:

        history.append({
            "role": "user",
            "content": prompt
        })

        # Replace with your LLM call
        app = get_app()
        # Pass the current history to the graph
        config = {"configurable": {"thread_id": "1"}}
        result = app.invoke({"messages": st.session_state.messages})
        
        # Get the last message from the updated state
        response = result["messages"][-1]
        #f"{st.session_state.selected_app} received: {prompt}"

        history.append({
            "role": "assistant",
            "content": response
        })

        st.rerun()