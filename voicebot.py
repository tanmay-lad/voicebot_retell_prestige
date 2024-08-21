import os
import json
from dotenv import load_dotenv
from retell import Retell
import streamlit as st
import summary

load_dotenv()

client = Retell(
    api_key=os.getenv("RETELL_API_KEY"),
)

def save_transcript(call_id, call_transcript):
    call_transcripts_folder = 'call_transcripts/'
    call_transcript_file = os.path.join(call_transcripts_folder, f"{call_id}.json")

    conversation_history = []

    for line in call_transcript.strip().split('\n'):
        if ': ' in line:  # Check if the delimiter exists
            speaker, content = line.split(': ', 1)
            role = "user" if speaker.strip().lower() == "user" else "assistant"
            conversation_history.append({"role": role, "content": content.strip()})

    # Save the conversation history to a JSON file
    with open(call_transcript_file, "w", encoding='utf-8') as f:
        json.dump(conversation_history, f, indent=4, ensure_ascii=False)


# Set page configuration
st.set_page_config(
    page_title="SubVerseAI",
    page_icon=":telephone_receiver:",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Display fixed header
header = st.container()

with header:
    col1, col2, col3, col4 = header.columns(4)
    with col1:
        phone_number = st.text_input(
            "Enter phone number",
            value = "",
            placeholder="Enter phone number",
            label_visibility="collapsed"
        )
    with col2:
        language = st.selectbox(
            "Select language",
            ("HINDI", "ENGLISH"),
            index=None,
            placeholder="Hindi or English",
            label_visibility="collapsed"
        )
    with col3:
        start_call = st.button("Start Call:telephone_receiver:", use_container_width=True)
    with col4:
        call_details = st.button("Show call summary and transcript", type="primary", use_container_width=True)
    
    header.write("""<div class='fixed-header'></div>""", unsafe_allow_html=True) 

    ### Custom CSS for the sticky header
    st.markdown(
        """
    <style>
        div[data-testid="stVerticalBlock"] div:has(div.fixed-header) {
            position: sticky;
            top: 2.875rem;
            background-color: white;
            z-index: 999;
        }
        .fixed-header {
            border-bottom: 1px solid black;
        }
    </style>
        """,
        unsafe_allow_html=True
    )

if 'call_id' not in st.session_state:
    st.session_state.call_id = '' # Initialize the string

if start_call:
    # Format phone number provided
    phone_number = "+91" + phone_number

    # Select retell key based on language
    language = "ENGLISH" if language is None else language

    # Place call to the number provided
    call = client.call.create(
        from_number=os.getenv("FROM_NUMBER"),
        to_number=phone_number,
        override_agent_id=os.getenv(f"RETELL_AGENT_ID_{language}"),
    )
    # Store call_id to be used later to get call details
    st.session_state.call_id = call.call_id

if call_details:
    # Get call details after call ends
    print(st.session_state.call_id)
    call_id = st.session_state.call_id
    call_details = client.call.retrieve(
        call_id,
    )
    customer_number = call_details.to_number
    disconnection_reason = call_details.disconnection_reason
    call_transcript = call_details.transcript
    # audio_file = call_details.recording_url

    # Save the transcript in txt file
    save_transcript(call_id, call_transcript)

    # summary.call_summary_old(call_id, customer_number, disconnection_reason)
    summary.call_summary(call_id, call_transcript, customer_number, disconnection_reason)