from sentence_transformers import SentenceTransformer
import qdrant_client
import numpy as np
from typing import List, Dict, Tuple

from ..core.config import settings
from .. import models, schemas # Assuming we might work with models/schemas

# Initialize model and DB client (consider lazy loading or dependency injection)
try:
    model = SentenceTransformer("all-MiniLM-L6-v2")
except Exception as e:
    print(f"Warning: Could not load SentenceTransformer model: {e}")
    model = None

try:
    # Ensure Qdrant client uses config
    qdrant_db = qdrant_client.QdrantClient(
        host=settings.QDRANT_HOST, 
        port=settings.QDRANT_PORT
    )
    # TODO: Add check for collection existence / creation
except Exception as e:
    print(f"Warning: Could not connect to Qdrant: {e}")
    qdrant_db = None

def get_embedding(text: str) -> List[float] | None:
    """Generates embedding for a given text."""
    if not model:
        print("Error: SentenceTransformer model not loaded.")
        return None
    try:
        vector = model.encode(text).tolist() # Convert numpy array to list
        return vector
    except Exception as e:
        print(f"Error generating embedding: {e}")
        return None

def rank_jobs(resume_text: str, jobs: List[Dict]) -> List[Tuple[Dict, float]]:
    """Ranks jobs based on cosine similarity to resume text embedding."""
    if not model:
        print("Error: SentenceTransformer model not loaded. Cannot rank jobs.")
        return [(job, 0.0) for job in jobs] # Return jobs with 0 score
        
    resume_vec = model.encode(resume_text)
    
    # Assume jobs is a list of dicts, each having an 'embedding' key
    # Filter out jobs without valid embeddings
    valid_jobs = [j for j in jobs if j.get('embedding') and isinstance(j['embedding'], list)]
    if not valid_jobs:
        print("Warning: No jobs with valid embeddings found for ranking.")
        return [(job, 0.0) for job in jobs]
        
    job_vecs = np.array([j["embedding"] for j in valid_jobs])
    
    # Calculate cosine similarity
    # Ensure vectors are numpy arrays for calculation
    resume_vec_np = np.array(resume_vec)
    job_vecs_np = np.array(job_vecs)
    
    norm_resume = np.linalg.norm(resume_vec_np)
    norm_jobs = np.linalg.norm(job_vecs_np, axis=1)
    
    # Avoid division by zero if norms are zero
    if norm_resume == 0 or np.any(norm_jobs == 0):
        print("Warning: Zero norm vector encountered during similarity calculation.")
        scores = np.zeros(len(valid_jobs))
    else:
        scores = job_vecs_np @ resume_vec_np / (norm_jobs * norm_resume)
        
    # Combine valid jobs with scores
    ranked_valid_jobs = sorted(zip(valid_jobs, scores), key=lambda x: x[1], reverse=True)
    
    # Include jobs that couldn't be ranked (e.g., missing embedding) at the end with score 0
    unranked_jobs = [(job, 0.0) for job in jobs if job not in valid_jobs]
    
    return ranked_valid_jobs + unranked_jobs

# TODO:
# - Add function to index job embeddings into Qdrant
# - Add function to search Qdrant for similar jobs based on resume embedding 