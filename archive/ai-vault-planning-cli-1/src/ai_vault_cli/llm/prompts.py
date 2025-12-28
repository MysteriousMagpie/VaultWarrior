# This file contains predefined prompts for interacting with the AI.

def get_default_prompt():
    return "You are an AI assistant. How can I help you today?"

def get_chat_prompt(user_message):
    return f"User: {user_message}\nAI:"

def get_plan_prompt(thread_summary):
    return f"Based on the following summary, create a detailed plan:\n{thread_summary}"

def get_capture_prompt(capture_text):
    return f"Capture the following note:\n{capture_text}"

def get_ask_prompt(question):
    return f"Answer the following question:\n{question}"