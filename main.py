from data_fetch import get_video_ids, fetch_transcript
from vector_db import index_parents, index_children
from retrival import get_rag_chain


# --- A. RUN MODE ---
# Set to True to download data, False to just chat
INDEX_NEW_DATA = True
TARGET_PLAYLIST = "https://www.youtube.com/playlist?list=PLgUwDviBIf0pmWCl2nepwGDO05a0-7EfJ"

if __name__ == "__main__":
    
    # 1. DATA INDEXING 
    if INDEX_NEW_DATA:
        video_ids = get_video_ids(TARGET_PLAYLIST)
        count = 1
        for vid_id in video_ids:
            print(f"--- Processing {count}/{len(video_ids)}: {vid_id} ---")
            transcript_data = fetch_transcript(vid_id)
            
            if transcript_data:
                parents_data = index_parents(transcript_data, vid_id)
                index_children(parents_data, transcript_data, vid_id)
            count += 1
        print("--- All Videos Indexed ---")

    # 2. CHAT INTERFACE
    print("\n--- Starting Chat ---")
    rag_chain = get_rag_chain()
    
    while True:
        query = input("\nAsk (or 'q' to quit): ")
        if query.lower() == 'q': break
        
        print("Thinking...")
        response = rag_chain.invoke({"input": query})
        print(f"\nAI: {response}")