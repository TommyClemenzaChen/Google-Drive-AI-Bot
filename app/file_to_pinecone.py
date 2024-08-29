from pinecone import Pinecone, ServerlessSpec
import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
import logging
from dotenv import load_dotenv

def index_text_files(folder_path):

    try:
        for file_name in os.listdir(folder_path):

            if file_name.endswith(".txt"):
                file_path = os.path.join(folder_path, file_name)
                process_file(file_path)
        logging.info("All files processed")
    except Exception as e:
        logging.error(f"Error processing files: {e}")


def process_file(file_path):
    splitter = RecursiveCharacterTextSplitter(chunk_size = 200, chunk_overlap = 50)
    embed_model = OpenAIEmbeddings()

    # Load the pinecone index
    index = _get_pinecone_client()

    # Read the text file
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()

    # Spliiting + embedding
    chunks = splitter.split_text(text)
    vectors = []
    for i, chunk in enumerate(chunks):
        meta_data = {
            'text': chunk,
        }

        embed_text = embed_model.embed_query(chunk)
        chunk_id = f"{file_path}_{i}"

        vectors.append({"id": chunk_id, "values": embed_text, "metadata": meta_data})
    
    index.upsert(vectors)
    logging.info(f"File {file_path} processed")

def _get_pinecone_client():
    load_dotenv()
    index_name = "google-drive-index"
    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

    pc = Pinecone(api_key = PINECONE_API_KEY)
    # if index_name not in pc.list_indexes():
    #     pc.create_index(name=index_name, 
    #                     dimension=1536,
    #                     metric="cosine",
    #                     spec = ServerlessSpec(cloud="aws", region="us-west-2"),
    #                     )
    return pc.Index(index_name) 

def clear_folder(folder_path):
    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)

        # Check if it is a file and delete it
        if os.path.isfile(file_path):
            os.remove(file_path)
    logging.info(f"Cleared folder {folder_path}")
    

