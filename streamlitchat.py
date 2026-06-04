from datetime import datetime

import streamlit as st
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

# 2. Build the Graph
def get_app():

    llm = ChatOllama(model="llama3",temperature =0.9)
    llm_with_tools  = llm.bind_tools(tools)

    workflow = StateGraph(State)
    workflow.add_node("chatbot", chatbot_node)
    workflow.add_edge(START, "chatbot")
    workflow.add_edge("chatbot", END)
    return workflow.compile()

# 3. Streamlit UI
st.title("LangGraph Chatbot")

# Initialize persistent session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display existing chat history
for msg in st.session_state.messages:
    role = "user" if isinstance(msg, HumanMessage) else "assistant"
    with st.chat_message(role):
        st.markdown(msg.content)

# Handle user input
if prompt := st.chat_input("What is on your mind?"):
    # Add user message to state
    user_msg = HumanMessage(content=prompt)
    st.session_state.messages.append(user_msg)
    
    with st.chat_message("user"):
        st.markdown(prompt)

    # Run LangGraph and display response
    with st.chat_message("assistant"):
        app = get_app()
        # Pass the current history to the graph
        config = {"configurable": {"thread_id": "1"}}
        result = app.invoke({"messages": st.session_state.messages})
        
        # Get the last message from the updated state
        response_msg = result["messages"][-1]
        st.markdown(response_msg.content)
        st.session_state.messages.append(response_msg)

if __name__ == "__main__":
    get_app()