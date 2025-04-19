from sentence_transformers import SentenceTransformer
import qdrant_client
import numpy as np
from typing import List, Dict, Tuple
import logging # Added
from qdrant_client.http.models import Distance, VectorParams, PointStruct, UpdateStatus # Added

from ..core.config import settings
from .. import models, schemas # Assuming we might work with models/schemas

# Setup logger
logger = logging.getLogger(__name__) # Added

# Initialize model and DB client (consider lazy loading or dependency injection)
try:
    model = SentenceTransformer("all-MiniLM-L6-v2")
    VECTOR_SIZE = model.get_sentence_embedding_dimension() # Added
except Exception as e:
    logger.warning(f"Could not load SentenceTransformer model: {e}") # Updated print to logger
    model = None
    VECTOR_SIZE = 384 # Added fallback

JOB_COLLECTION = "jobs" # Added collection name

try:
    # Ensure Qdrant client uses config, including API key and HTTPS for cloud
    qdrant_db = qdrant_client.QdrantClient(
        host=settings.QDRANT_HOST,
        port=settings.QDRANT_PORT,
        api_key=settings.QDRANT_API_KEY, # Use API Key from settings
        https=(settings.QDRANT_PORT == 443) # Enable HTTPS if using standard HTTPS port
    )
    # Check and create collection if it doesn't exist
    try:
        qdrant_db.get_collection(collection_name=JOB_COLLECTION)
        logger.info(f"Qdrant collection '{JOB_COLLECTION}' already exists.")
    except Exception as e: # Catch specific exception if possible (e.g., collection not found)
        logger.warning(f"Qdrant collection '{JOB_COLLECTION}' not found, attempting to create it. Error: {e}")
        try:
            qdrant_db.create_collection(
                collection_name=JOB_COLLECTION,
                vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE)
            )
            logger.info(f"Successfully created Qdrant collection '{JOB_COLLECTION}'.")
        except Exception as create_e:
            logger.error(f"Failed to create Qdrant collection '{JOB_COLLECTION}': {create_e}")
            qdrant_db = None # Mark client as unusable if collection setup fails

except Exception as e:
    logger.warning(f"Could not connect to Qdrant or setup collection: {e}") # Updated print to logger
    qdrant_db = None

def get_embedding(text: str) -> List[float] | None:
    """Generates embedding for a given text."""
    if not model:
        logger.error("SentenceTransformer model not loaded.") # Use logger
        return None
    try:
        # Ensure text is not empty or just whitespace
        if not text or text.isspace(): # Added check
            logger.warning("Attempted to get embedding for empty text.")
            return None
        vector = model.encode(text).tolist() # Convert numpy array to list
        return vector
    except Exception as e:
        logger.error(f"Error generating embedding: {e}") # Use logger
        return None

# Old rank_jobs function removed, replaced by Qdrant search

def index_job(job: models.Job, job_embedding: List[float]):
    """Indexes a job's embedding and metadata into Qdrant."""
    if not qdrant_db:
        logger.error("Qdrant client not available. Cannot index job.")
        return False
    if not job_embedding:
        logger.warning(f"No embedding provided for job ID {job.id}. Skipping indexing.")
        return False

    try:
        operation_info = qdrant_db.upsert(
            collection_name=JOB_COLLECTION,
            wait=True, # Wait for operation to complete for confirmation
            points=[
                PointStruct(
                    id=job.id,
                    vector=job_embedding,
                    payload={
                        "title": job.title,
                        "company_name": job.company_name,
                        "location": job.location,
                        # Add other filterable/retrievable fields as needed
                        # "posted_date": job.posted_date.isoformat() if job.posted_date else None,
                    }
                )
            ]
        )
        if operation_info.status == UpdateStatus.COMPLETED:
            logger.info(f"Successfully indexed/updated job ID {job.id} in Qdrant.")
            return True
        else:
            logger.warning(f"Qdrant upsert operation for job ID {job.id} finished with status: {operation_info.status}")
            return False
    except Exception as e:
        logger.error(f"Error indexing job ID {job.id} in Qdrant: {e}")
        return False

def search_similar_jobs(resume_embedding: List[float], limit: int = 10) -> List[Tuple[int, float]]:
    """Searches Qdrant for jobs similar to the given resume embedding."""
    if not qdrant_db:
        logger.error("Qdrant client not available. Cannot search for jobs.")
        return []
    if not resume_embedding:
        logger.error("Cannot search for jobs with an empty resume embedding.")
        return []

    try:
        search_result = qdrant_db.search(
            collection_name=JOB_COLLECTION,
            query_vector=resume_embedding,
            limit=limit
            # Add query_filter here if needed, e.g., based on location, keywords in payload
            # query_filter=models.Filter(...)
        )
        # Results are ScoredPoint objects: id, version, score, payload, vector
        ranked_jobs = [(hit.id, hit.score) for hit in search_result]
        logger.info(f"Found {len(ranked_jobs)} similar jobs in Qdrant.")
        return ranked_jobs
    except Exception as e:
        logger.error(f"Error searching for similar jobs in Qdrant: {e}")
        return []
