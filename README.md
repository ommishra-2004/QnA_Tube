# QnA_Tube: Chat with Your YouTube Playlists 

**QnA_Tube** is a RAG-powered (Retrieval-Augmented Generation) application designed to transform the way we consume educational content on YouTube. Instead of manually scrubbing through hours of footage, you can index an entire playlist and ask specific questions. The AI provides precise answers alongside **timestamped links** that take you directly to the relevant part of the video.

---

## Use Cases
* **Academic Research:** Instantly find explanations within long lecture series of 100+ videos.
* **Coding & Tech:** Quickly locate specific library implementations or bug fixes in tutorial playlists.
* **Content Summarization:** Get a high-level overview of a series of podcasts or interviews.

---

## Key Features
* **Playlist-Wide Context:** Processes and understands information across multiple videos simultaneously.
* **Timestamps:** Don't just get an answer; get the exact minute and second where the topic is discussed (Approximate), Used Parent-Child Chunking strategy for timestamp extraction at the same time keeping context clear and complete to LLM.
* **Dual Interface:** Choose between a lightweight CLI version or a modern(main.py) , interactive web UI(ui.py).
* **Vector-Based Retrieval:** Uses high-dimensional embeddings to find relevant child chunks and share it's parent chunk for giving complete information to LLm.

---

## Tech Stack
* **Orchestration:** [LangChain](https://www.langchain.com/)
* **Vector Database (local):** [Qdrant](https://qdrant.tech/)
* **LLM:** [Google Gemini](https://ai.google.dev/)
* **Frontend:** [Streamlit](https://streamlit.io/)
* **Transcription:** YouTube Transcript API

---

## Project Structure & Implementation

The repository is organized into modular components for scalability and clarity:

* **`ui.py`**: The main entry point for the **Streamlit web interface**. Features a sidebar for playlist input and a chat-style window for querying.
* **`main.py`**: A **CLI-based entry point**. Perfect for developers who want to interact with the system directly through the terminal without a browser.
* **`data_fetch.py`**: Logic for extracting transcripts and metadata (titles, IDs, durations) from YouTube playlists.
* **`vector_db.py`**: Handles the pipeline for text chunking, embedding generation, and storage within the **Qdrant** vector database.
* **`retrival.py`**: The core RAG logic. It performs similarity searches and manages the prompt engineering to ensure answers include accurate citations.
* **`config.py`**: Centralized management for API keys and environment variables.

---

## Installation & Setup

1.  **Clone the Repository:**
    ```bash
    git clone [https://github.com/ommishra-2004/QnA_Tube.git](https://github.com/ommishra-2004/QnA_Tube.git)
    cd QnA_Tube
    ```

2.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure Environment Variables:**
    Create a `.env` file in the root directory and add your credentials:
    ```env
    GOOGLE_API_KEY=your_gemini_api_key
    ```

---

## 📖 How to Run

### 1. Web Interface (Recommended)
For a visual, interactive experience:
```bash
streamlit run ui.py
```

### 2. Terminal 
For a CLI experience:
```bash
python main.py
```

##Contributing
Contributions are welcome! Whether it's adding support for more LLMs or improving the UI, feel free to fork the repo and submit a PR.

###Developed with ❤️ by Om Mishra Student @ Veermata Jijabai Technological Institute (VJTI)
