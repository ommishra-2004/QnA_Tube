import uuid
from qdrant_client import QdrantClient
from qdrant_client.http import models
from langchain_qdrant import QdrantVectorStore
from langchain_experimental.text_splitter import SemanticChunker
from langchain_text_splitters import RecursiveCharacterTextSplitter
from qdrant_client import models
from config import client, embeddings, QDRANT_URL, PARENT_COLLECTION, CHILD_COLLECTION



def clear_database():
    """Deletes the existing collections to reset the database."""
    try:
        client.delete_collection(collection_name=PARENT_COLLECTION)
        client.delete_collection(collection_name=CHILD_COLLECTION)
        print("Database cleared successfully.")
    except Exception as e:
        print(f"Notes: Collections might not exist yet, skipping delete. ({e})")

def index_parents(transcript_data, video_id):
    full_text = " ".join([seg['text'] for seg in transcript_data])
    sementic_splitter = SemanticChunker(
            embeddings = embeddings,
            breakpoint_threshold_type = "percentile"
        )
    parent_docs = sementic_splitter.create_documents([full_text])
    parent_data_list = []
    points_to_upload = []
    current_seg_idx = 0

    for doc in parent_docs:
        pid = str(uuid.uuid4())
        p_start_text = doc.page_content[:15]
        start_time = 0
        for i in range(current_seg_idx, len(transcript_data)):
            if p_start_text in transcript_data[i]['text']:
                start_time = transcript_data[i]['start']
                current_seg_idx = i
                break
        
        payload = {
            "page_content": doc.page_content,
            "video_id": video_id,
            "start": start_time,
            "type": "parent"
        }
        
        points_to_upload.append(models.PointStruct(
            id=pid,
            vector={}, 
            payload=payload
        ))
        
        parent_data_list.append({
            "id": pid,
            "text": doc.page_content,
            "start_index": current_seg_idx 
        })

    if not client.collection_exists(PARENT_COLLECTION):
        client.create_collection(collection_name=PARENT_COLLECTION, vectors_config={})
    
    client.upsert(collection_name=PARENT_COLLECTION, points=points_to_upload)
    return parent_data_list


def index_children(parent_data_list, transcript_data, video_id):
    child_splitter = RecursiveCharacterTextSplitter(chunk_size=400, chunk_overlap=50)
    child_docs_final = []
    
    for parent in parent_data_list:
        child_chunks = child_splitter.create_documents([parent['text']])
        local_seg_idx = parent['start_index']
        
        for child in child_chunks:
            c_start_text = child.page_content[:20]
            c_start_time = 0
            for i in range(local_seg_idx, len(transcript_data)):
                if c_start_text in transcript_data[i]['text']:
                    c_start_time = transcript_data[i]['start']
                    break
            
            child.metadata = {
                "parent_id": parent['id'], 
                "video_id": video_id,
                "start": c_start_time,
                "type": "child"
            }
            child_docs_final.append(child)
            
    QdrantVectorStore.from_documents(
        documents=child_docs_final,
        embedding=embeddings,
        url=QDRANT_URL,
        collection_name=CHILD_COLLECTION,
        force_recreate=False
    )