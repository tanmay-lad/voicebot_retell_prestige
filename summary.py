import asyncio
from dotenv import load_dotenv
import os
import json
import streamlit as st

import llm

from groq import AsyncGroq

load_dotenv()

def get_system_prompt():
    system_prompts_folder = 'system_prompts_summary/'
    # system_prompts_file = os.path.join(system_prompts_folder, "prestige.txt")
    system_prompts_file = os.path.join(system_prompts_folder, "ujjivan.txt")
    
    conversation_history = []
    
    with open(system_prompts_file, 'r', encoding='utf-8') as f:
        content = f.read()

        if content.strip(): # Check if the content is not empty after removing leading/trailing whitespace
            conversation_history.append({"role": "system", "content": content.strip()})
    
    return conversation_history

def show_call_transcript(transcript_file):
  try:
      with open(transcript_file, 'r', encoding='utf-8') as f:
          conversation_history = json.load(f)

      for message in conversation_history:
          role = message["role"]
          content = message["content"]
          if role == "user":
              st.chat_message("user").markdown(content)
          elif role == "assistant":
              st.chat_message("assistant").markdown(content)
  except FileNotFoundError:
      st.error(f"File not found: {transcript_file}")

def call_summary(call_id, call_transcript, customer_number, disconnection_reason):
    col1, col2  = st.columns(2)
    

    # Display call summary in the right column
    with col1:
        # Get system prompt and conversation history from files
        system_prompt = get_system_prompt()
        
        # Call LLM function and display output
        client = AsyncGroq(api_key = os.getenv('GROQ_API_KEY'))

        st.write("**Call Summary:**\n")
        st.write(f"* **Contact Number:** {customer_number}")
        st.write(f"* **Disconnection reason:** {disconnection_reason}")

        query = f"Following is the transcript of the call between agent and customer \n {call_transcript}. \n There could be ASR and speaker recognition errors, especially for numbers and proper nouns. Write a conversation summary with bullet points, in less than 40 words."
        
        response = asyncio.run(llm.call_summary(client, query, system_prompt))

        # Save the output in txt file
        call_summary_folder = 'call_summary/'
        call_summary_file = os.path.join(call_summary_folder, f"{call_id}.txt")

        with open(call_summary_file, 'w', encoding='utf-8') as f:
            f.write("**Call Summary:**\n")
            f.write(f"* **Contact Number:** {customer_number}\n")
            f.write(f"* **Disconnection reason:** {disconnection_reason}\n")
            f.write(response)

    # Display transcript in the left column
    with col2:
        call_transcripts_folder = 'call_transcripts/'
        call_transcript_file = os.path.join(call_transcripts_folder, f"{call_id}.json")

        st.write("**Call Transcript:**\n")

        # Display each message
        show_call_transcript(call_transcript_file)