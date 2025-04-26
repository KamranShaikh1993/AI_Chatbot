import os
import json
import time
import numpy as np
import pandas as pd
# from paddleocr import PaddleOCR
import re
import requests
import logging
from sklearn.metrics.pairwise import cosine_similarity

import ollama
import chromadb

from chromadb import PersistentClient


def Insurance_Agent_Rag(prompt):
    # Load the existing persistent collection
    rag_client = PersistentClient(path= r"C:\Users\MY PC\Documents\Kami_AI_RAG\New_Deploy\chroma_store")
    collection = rag_client.get_collection(name="docs")
    
    # Access saved vectors and documents
    all_data = collection.get(include=["documents", "embeddings"])  # 'ids' is included automatically
    
    documents = all_data["documents"]
    embeddings = all_data["embeddings"]
    ids = all_data["ids"]  # No need to request it explicitly
    
    
    input_text = prompt
    
    # generate the embedding
    response = ollama.embed(
        model="mxbai-embed-large",
        input=prompt
    )
    
    # query ChromaDB with correct format
    results = collection.query(
        query_embeddings=response["embeddings"],
        n_results=1,
        include=["embeddings", "documents"]
    )
    
    
    # Extract documents and embeddings
    document_texts = results['documents'][0]           # list of 5 documents
    document_embeddings = results['embeddings'][0]     # list of 5 embeddings
    
    # Convert to NumPy arrays
    query_embedding = np.array(response["embeddings"]).reshape(1, -1)
    document_embeddings = np.array(document_embeddings)
    
    #-------------------------------------------------------------------------------------------
    # Calculate cosine similarities
    cosine_similarities = cosine_similarity(query_embedding, document_embeddings)[0]
    
    # Print similarity scores with documents
    print("🔍 Similar Documents and Their Cosine Scores:\n----------------\n")
    for idx, (score, doc) in enumerate(zip(cosine_similarities, document_texts)):
        print(f"{idx+1}. Score: {score:.4f}")
        # print(f"   Document: {doc[:int(len(doc)/2)]}\n")
    
    # Get the most similar document
    most_similar_idx = np.argmax(cosine_similarities)
    most_relevant_document = document_texts[most_similar_idx]
    
    #-------------------------------------------------------------------------------------------
    
    
    # Generate response using most relevant document
    output = ollama.generate(
        # model="llama2",
        model="llama3.2:latest",
        # model = "deepseek-r1:latest",
        prompt=f"Using this data: {most_relevant_document}. Respond to this prompt: {input_text}"
    )
    
    print("\n🧠 Generated Answer:")
    rag_output = output['response']
    return rag_output

