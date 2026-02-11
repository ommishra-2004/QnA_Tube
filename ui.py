import streamlit as st
import random
import time
from data_fetch import get_video_ids, fetch_transcript
from vector_db import index_parents, index_children, clear_database
from retrival import get_rag_chain

# --- STREAMLIT PAGE CONFIG ---
st.set_page_config(page_title="QTube", page_icon="▶️", layout="wide")


st.markdown("""
    <style>
        .block-container {
            padding-top: 0.5rem;
            padding-bottom: 0rem;
        }
    </style>
""", unsafe_allow_html=True)

# --- SIDEBAR: DATA INDEXING ---
with st.sidebar:
    st.header("⚙️ Indexing Data : ")
    
    default_playlist = "https://www.youtube.com/playlist?list=PL_JbQ74y754Xn5H6wYqU8xY5k5b5b5b5b"
    target_playlist = st.text_input("Target Playlist URL", value=default_playlist)
    
    old_data = st.checkbox("Delete old data?",[True, False], help="If checked, this will delete all previous videos from the database before indexing the new ones.")
    # Indexing Button
    if st.button("Index New Data"):
        if old_data:
            st.write(" Clearing old database entries...")
            clear_database()
            st.write("✅ Database cleared!")

        st.write("Fetching video IDs...") 
        video_ids = get_video_ids(target_playlist)
        
        if not video_ids:
            st.error("Error: No videos found.")
        else:
            progress_bar = st.progress(0)
            total_videos = len(video_ids)
            
            for i, vid_id in enumerate(video_ids):
                st.write(f"Processing {i+1}/{total_videos}: `{vid_id}`")

                transcript_data = fetch_transcript(vid_id)
                if transcript_data:
                    parents_data = index_parents(transcript_data, vid_id)
                    index_children(parents_data, transcript_data, vid_id)
                else:
                    st.warning(f"Skipped {vid_id} (No transcript found or error)")
                
                progress_bar.progress((i + 1) / total_videos)
            
            st.success(f"Successfully indexed {total_videos} videos!")
            
            # Optional: Clear cache so the AI doesn't remember old context
            st.cache_resource.clear()

# --- MAIN CHAT INTERFACE ---
st.markdown("""
    <style>
    .custom-title {
        text-align: center;
        font-size: 3rem;
        font-weight: bold;
        margin-top: 20px;
        margin-bottom: 20px;
    }
            
    .captions {
        text-align: center;
        font-size: 1rem;
        font-weight: bold;
        margin-top: 8px;
        margin-bottom: 20px;
    }
    </style>
    <div class="custom-title">QTube</div>
    <div class="captions">Ask questions/timestamps/summaries based on the content of the videos in provided playlist. </div>
    """, unsafe_allow_html=True)



# 1. Initialize Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []

# 2. Load RAG Chain (Cached to prevent reloading on every interaction)
@st.cache_resource
def load_rag_chain():
    return get_rag_chain()

try:
    rag_chain = load_rag_chain()
except Exception as e:
    st.error(f"Error loading RAG Chain: {e}")
    st.stop()

# 3. Display Chat Messages from History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 4. Handle User Input
if prompt := st.chat_input("Ask about the video content..."):
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate Response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = rag_chain.invoke({"input": prompt})
                st.markdown(response)
                # Add assistant response to history
                st.session_state.messages.append({"role": "assistant", "content": response})
            except Exception as e:
                st.error(f"An error occurred during retrieval: {e}")