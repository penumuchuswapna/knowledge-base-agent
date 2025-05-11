import streamlit as st
import requests
from streamlit_chat import message

st.set_page_config(page_title="💬 Knowledge Base Agent", page_icon="💬", layout="wide")

# --- Sidebar: Chat History ---
st.sidebar.title("💬 Chat History")
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []
    st.session_state['history_titles'] = []

# Show chat history in sidebar
if st.session_state['history_titles']:
    for i, (title, history) in enumerate(st.session_state['history_titles']):
        if st.sidebar.button(title, key=f"sidebar_{i}"):
            st.session_state['chat_history'] = history
            st.rerun()

# --- Main Chat Area ---
st.markdown("""
    <style>
    .stChatMessage.user {background-color: #23272f; color: #fff; border-radius: 12px 12px 0 12px; margin-bottom: 8px;}
    .stChatMessage.bot {background-color: #1a1d23; color: #fff; border-radius: 12px 12px 12px 0; margin-bottom: 8px;}
    .stTextInput > div > div > input {background: #23272f; color: #fff; border-radius: 8px;}
    .stTextInput > label {font-weight: bold;}
    .block-container {padding-top: 2rem;}
    </style>
""", unsafe_allow_html=True)

st.title("💬 Knowledge Base Agent")

# --- Chat Display (answer above user query, most recent at bottom) ---
def display_chat():
    chat_display = []
    i = 0
    while i < len(st.session_state['chat_history']):
        if st.session_state['chat_history'][i]['role'] == 'user':
            if i+1 < len(st.session_state['chat_history']) and st.session_state['chat_history'][i+1]['role'] == 'bot':
                chat_display.append(st.session_state['chat_history'][i+1])
                chat_display.append(st.session_state['chat_history'][i])
                i += 2
            else:
                chat_display.append(st.session_state['chat_history'][i])
                i += 1
        else:
            chat_display.append(st.session_state['chat_history'][i])
            i += 1
    for idx, chat in enumerate(chat_display):
        if chat['role'] == 'user':
            message(chat['content'], is_user=True, key=f"user_{idx}")
        else:
            message(chat['content'], is_user=False, key=f"bot_{idx}")

display_chat()

# --- Input at the bottom, Enter to send ---
with st.form(key="chat_form", clear_on_submit=True):
    user_input = st.text_input(
        "Your message",
        placeholder="Enter...",
        key="input",
        label_visibility="collapsed"
    )
    submitted = st.form_submit_button("Send")

if submitted and user_input:
    st.session_state['chat_history'].append({"role": "user", "content": user_input})
    st.rerun()

# --- Bot Response Logic ---
if st.session_state['chat_history']:
    # Only process the last user message if it hasn't been answered
    if st.session_state['chat_history'][-1]['role'] == 'user' and (
        len(st.session_state['chat_history']) == 1 or st.session_state['chat_history'][-2]['role'] != 'bot'):
        query = st.session_state['chat_history'][-1]['content']
        # Search across all services
        services = {
            "Google Drive": "search-drive",
            "Jira": "search-jira",
            "GitHub": "search-github",
            "GitLab": "search-gitlab"
        }
        best_result = None
        best_source = None
        context = "No specific context found from search results."
        for service_name, endpoint in services.items():
            try:
                response = requests.get(f"http://localhost:8000/{endpoint}/", params={"query": query})
                if response.status_code == 200:
                    results = response.json().get("results", [])
                    if results:
                        result = results[0]
                        if service_name == "Google Drive":
                            best_result = {
                                "title": result.get("name"),
                                "description": f"File Type: {result.get('mimeType')}",
                                "url": f"https://drive.google.com/file/d/{result.get('id')}/view"
                            }
                            best_source = "Google Drive"
                            context = f"Document: {result.get('name')} ({result.get('mimeType')})"
                        elif service_name == "Jira":
                            best_result = {
                                "title": result.get("key"),
                                "description": result.get("summary"),
                                "url": result.get("url")
                            }
                            best_source = "Jira"
                            context = f"Jira Issue: {result.get('key')} - {result.get('summary')}"
                        elif service_name == "GitHub":
                            best_result = {
                                "title": result.get("full_name"),
                                "description": result.get("description"),
                                "url": result.get("url")
                            }
                            best_source = "GitHub"
                            context = f"GitHub Repository: {result.get('full_name')} - {result.get('description')}"
                        elif service_name == "GitLab":
                            best_result = {
                                "title": result.get("path"),
                                "description": result.get("description"),
                                "url": result.get("url")
                            }
                            best_source = "GitLab"
                            context = f"GitLab Project: {result.get('path')} - {result.get('description')}"
                        break
            except Exception:
                continue
        # Always try to get AI-generated answer
        try:
            ai_response = requests.get(
                "http://localhost:8000/generate-answer/",
                params={"query": query, "context": context}
            )
            if ai_response.status_code == 200:
                ai_answer = ai_response.json().get("answer")
                answer_text = ai_answer
            else:
                answer_text = "Failed to generate AI answer."
        except Exception as e:
            answer_text = f"Error generating AI answer: {e}"
        # Add bot message
        if best_result:
            answer_text += f"\n\n---\n**Source:** [{best_result['title']}]({best_result['url']})\n{best_result['description']}\n*Found in: {best_source}*"
        st.session_state['chat_history'].append({"role": "bot", "content": answer_text})
        # Save to sidebar history (title, chat)
        if answer_text and (not st.session_state['history_titles'] or st.session_state['history_titles'][-1][1] != st.session_state['chat_history']):
            st.session_state['history_titles'].append((query, st.session_state['chat_history'].copy()))
        st.rerun()

# from fastapi import APIRouter
# from pydantic import BaseModel

# router = APIRouter()

# class QueryRequest(BaseModel):
#     query: str

# class QueryResponse(BaseModel):
#     answer: str
#     needs_review: bool = False

# @router.post("/query", response_model=QueryResponse)
# async def handle_query(request: QueryRequest):
#     user_query = request.query
#     print(f"Received query: {user_query}")

#     answer = f"You asked: '{user_query}'. This is a dummy response. Integration logic coming soon!"
#     needs_review = "confidential" in user_query.lower()

#     return QueryResponse(answer=answer, needs_review=needs_review)
