from operator import itemgetter
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from langchain_qdrant import QdrantVectorStore
from langchain_google_genai import ChatGoogleGenerativeAI
from config import client, embeddings, PARENT_COLLECTION, CHILD_COLLECTION



# The Crazyyy Part yaha main hybrid chunk retrival karna hai

def retrieve_semantic_context(query_str):
    # just inititalized child vector store
    child_store = QdrantVectorStore(
        client=client,
        collection_name=CHILD_COLLECTION,
        embedding=embeddings
    )
    
    # 1. Search Children in child vector store
    child_results = child_store.similarity_search(query_str, k=5)
    if not child_results: return []

    # 2. Parent id aur sabse pehle child for that parent ka map banayenge, (kyuki retrival mai 1st child will have highest similarity score!!)
    parent_child_map = {}
    for child in child_results:
        p_id = child.metadata['parent_id']
        if p_id not in parent_child_map:
            parent_child_map[p_id] = child

    parent_ids = list(parent_child_map.keys())
    
    # 3. Just parent id's ke basis pai usske points retrive kr rhe hain from vector db (no vector search here)
    parent_points = client.retrieve(collection_name=PARENT_COLLECTION, ids=parent_ids)
    parent_data_list = {point.id: point.payload for point in parent_points}
    

    # 4. Merging jaha context parent ka aur time child ka 
    final_docs = []
    for p_id in parent_ids:
        parent_payload = parent_data_list.get(p_id)
        child_doc = parent_child_map[p_id]
        
        if parent_payload:
            final_docs.append(Document(
                page_content=parent_payload['page_content'], 
                metadata={
                    "video_id": child_doc.metadata['video_id'],
                    "start": child_doc.metadata['start'],
                }
            ))
            
    return final_docs


def format_docs_toon(docs):
    formatted_string = f"transcript_segments[{len(docs)}]{{serial_number | video_id | time | content}}:\n"
    for i, doc in enumerate(docs):
        vid_id = doc.metadata.get('video_id', 'UNKNOWN')
        start = doc.metadata.get('start', 0)
        content = doc.page_content.replace('\n', ' ').replace('|', '-')
        formatted_string += f"{i+1} | {vid_id} | {int(start)} seconds | {content} \n"
    return formatted_string

def get_rag_chain():
    prompt_template = """
    You are an expert Q&A system for a YouTube playlist. 
    Use the provided 'transcript_segments' (in TOON format) to answer.

    CRITICAL INSTRUCTIONS:
    1. Identify the 'serial_number' of the most relevant segment.
    2. Answer fully based on the 'content'.
    3. You MUST cite the source using a Markdown link format: [Source](https://www.youtube.com/watch?v=VIDEO_ID&t=START_SECONDS).

    Format:
    [Answer Text] ([Source](https://www.youtube.com/watch?v={{video_id}}&t={{start_seconds}}))

    Question: {input}
    Context:
    {context}
    """
    prompt = ChatPromptTemplate.from_template(prompt_template)
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.3)

    return (
        {
            "context": itemgetter("input") | RunnableLambda(retrieve_semantic_context) | format_docs_toon,
            "input": itemgetter("input")
        }
        | prompt
        | llm
        | StrOutputParser()
    )