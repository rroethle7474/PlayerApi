import os
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec
from transformers import AutoTokenizer, AutoModel
import torch

class PineconeService:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv('PINECONE_API_KEY')
        self.environment = os.getenv('PINECONE_ENVIRONMENT')
        self.index_name = os.getenv('PINECONE_INDEX_NAME')
        print("API Key:", self.api_key)
        print("Environment:", self.environment)
        print("Index:", self.index_name)
        # Initialize Pinecone
        self.pc = Pinecone(api_key=self.api_key)
               # Check if index exists, if not create it
        if self.index_name not in self.pc.list_indexes().names():
            self.pc.create_index(
                name=self.index_name,
                dimension=384,  # Dimension for the all-MiniLM-L6-v2 model
                metric='cosine',
                spec=ServerlessSpec(
                    cloud=os.getenv('PINECONE_CLOUD', 'aws'),
                    region=self.environment
                )
            )
        
        # Get the index
        self.index = self.pc.Index(self.index_name)
        # Load model and tokenizer
        self.model_name = "sentence-transformers/all-MiniLM-L6-v2"
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModel.from_pretrained(self.model_name)

    def create_embedding(self, text):
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=512, padding=True)
        with torch.no_grad():
            outputs = self.model(**inputs)
        embeddings = outputs.last_hidden_state.mean(dim=1).squeeze().tolist()
        return embeddings

    def upsert_vector(self, id, vector, metadata=None):
        self.index.upsert(vectors=[(id, vector, metadata)])

    def query_vectors(self, query_vector, top_k=5):
        return self.index.query(query_vector, top_k=top_k, include_metadata=True)