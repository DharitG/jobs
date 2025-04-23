import pytest
from unittest.mock import patch, MagicMock
from qdrant_client.http.models import PointStruct, UpdateStatus, ScoredPoint

# Assume services and models are importable
from app.services import matching
from app.models.job import Job
from app.schemas.job import JobCreate # May be needed for mocks
from app.db.session import SessionLocal # Assuming tests might need a DB session mock

# --- Constants & Mock Data ---
MOCK_VECTOR_SIZE = 384 # From matching.py fallback or SentenceTransformer dimension
MOCK_COLLECTION_NAME = "jobs" # From matching.py

# --- Mocks ---

# Mock SentenceTransformer model
mock_sentence_transformer = MagicMock()
mock_sentence_transformer.encode.return_value.tolist.return_value = [0.1] * MOCK_VECTOR_SIZE
mock_sentence_transformer.get_sentence_embedding_dimension.return_value = MOCK_VECTOR_SIZE

# Mock QdrantClient
mock_qdrant_client = MagicMock()

# Mock DB Session (optional, depending on test needs)
mock_db_session = MagicMock(spec=SessionLocal)

# Mock Job object
mock_job = Job(
    id=1,
    title="Test Job",
    company_name="Test Company",
    location="Test Location",
    url="http://test.com/job/1",
    description="Test description",
    embedding=[0.5] * MOCK_VECTOR_SIZE # Sample embedding
    # Add other necessary fields if required by functions being tested
)

# --- Tests ---

@patch('app.services.matching.model', mock_sentence_transformer)
def test_get_embedding_success():
    """Test successful embedding generation."""
    text = "This is a test description."
    embedding = matching.get_embedding(text)
    assert embedding is not None
    assert isinstance(embedding, list)
    assert len(embedding) == MOCK_VECTOR_SIZE
    mock_sentence_transformer.encode.assert_called_once_with(text)

@patch('app.services.matching.model', mock_sentence_transformer)
def test_get_embedding_empty_text():
    """Test embedding generation with empty text."""
    embedding = matching.get_embedding("")
    assert embedding is None
    embedding = matching.get_embedding("   ")
    assert embedding is None
    mock_sentence_transformer.encode.assert_not_called()

@patch('app.services.matching.model', None) # Simulate model loading failure
def test_get_embedding_model_not_loaded():
    """Test embedding generation when the model failed to load."""
    embedding = matching.get_embedding("Some text")
    assert embedding is None

@patch('app.services.matching.qdrant_db', mock_qdrant_client)
def test_index_job_success():
    """Test successful job indexing."""
    mock_qdrant_client.upsert.return_value = MagicMock(status=UpdateStatus.COMPLETED)
    
    result = matching.index_job(job=mock_job, job_embedding=mock_job.embedding)
    
    assert result is True
    mock_qdrant_client.upsert.assert_called_once()
    # Check the structure of the points passed to upsert
    args, kwargs = mock_qdrant_client.upsert.call_args
    assert kwargs.get('collection_name') == MOCK_COLLECTION_NAME
    points_arg = kwargs.get('points')
    assert isinstance(points_arg, list)
    assert len(points_arg) == 1
    assert isinstance(points_arg[0], PointStruct)
    assert points_arg[0].id == mock_job.id
    assert points_arg[0].vector == mock_job.embedding
    assert points_arg[0].payload["title"] == mock_job.title

@patch('app.services.matching.qdrant_db', mock_qdrant_client)
def test_index_job_no_embedding():
    """Test job indexing when no embedding is provided."""
    result = matching.index_job(job=mock_job, job_embedding=None)
    assert result is False
    mock_qdrant_client.upsert.assert_not_called()

@patch('app.services.matching.qdrant_db', None) # Simulate Qdrant connection failure
def test_index_job_qdrant_unavailable():
    """Test job indexing when Qdrant client is unavailable."""
    result = matching.index_job(job=mock_job, job_embedding=mock_job.embedding)
    assert result is False

@patch('app.services.matching.qdrant_db', mock_qdrant_client)
def test_index_job_qdrant_upsert_fails():
    """Test job indexing when Qdrant upsert returns a non-completed status."""
    mock_qdrant_client.upsert.return_value = MagicMock(status=UpdateStatus.ACKNOWLEDGED) # Simulate non-completed
    result = matching.index_job(job=mock_job, job_embedding=mock_job.embedding)
    assert result is False
    mock_qdrant_client.upsert.assert_called_once()

# Mock crud.job.get_jobs_by_ids for search test
mock_get_jobs_by_ids = MagicMock()

@patch('app.services.matching.qdrant_db', mock_qdrant_client)
@patch('app.services.matching.crud.job.get_jobs_by_ids', mock_get_jobs_by_ids)
def test_search_similar_jobs_success():
    """Test successful job search and retrieval."""
    mock_resume_embedding = [0.2] * MOCK_VECTOR_SIZE
    mock_user_id = 123
    
    # Mock Qdrant search result
    mock_qdrant_hits = [
        ScoredPoint(id=1, version=1, score=0.9, payload={}, vector=None),
        ScoredPoint(id=5, version=1, score=0.8, payload={}, vector=None)
    ]
    mock_qdrant_client.search.return_value = mock_qdrant_hits
    
    # Mock DB result
    mock_db_jobs = [
        Job(id=1, title="Job 1", company_name="Comp A"),
        Job(id=5, title="Job 5", company_name="Comp B")
    ]
    mock_get_jobs_by_ids.return_value = mock_db_jobs
    
    results = matching.search_similar_jobs(db=mock_db_session, resume_embedding=mock_resume_embedding, user_id=mock_user_id, limit=5)
    
    assert results == mock_db_jobs
    mock_qdrant_client.search.assert_called_once_with(
        collection_name=MOCK_COLLECTION_NAME,
        query_vector=mock_resume_embedding,
        limit=5
    )
    mock_get_jobs_by_ids.assert_called_once_with(mock_db_session, job_ids=[1, 5])

@patch('app.services.matching.qdrant_db', mock_qdrant_client)
def test_search_similar_jobs_no_qdrant_results():
    """Test job search when Qdrant returns no hits."""
    mock_resume_embedding = [0.2] * MOCK_VECTOR_SIZE
    mock_user_id = 123
    mock_qdrant_client.search.return_value = [] # No hits
    
    results = matching.search_similar_jobs(db=mock_db_session, resume_embedding=mock_resume_embedding, user_id=mock_user_id, limit=5)
    
    assert results == []
    mock_qdrant_client.search.assert_called_once()
    mock_get_jobs_by_ids.assert_not_called() # DB should not be queried if no IDs

@patch('app.services.matching.qdrant_db', None) # Simulate Qdrant connection failure
def test_search_similar_jobs_qdrant_unavailable():
    """Test job search when Qdrant client is unavailable."""
    mock_resume_embedding = [0.2] * MOCK_VECTOR_SIZE
    mock_user_id = 123
    results = matching.search_similar_jobs(db=mock_db_session, resume_embedding=mock_resume_embedding, user_id=mock_user_id, limit=5)
    assert results == []

def test_search_similar_jobs_no_embedding():
    """Test job search when no resume embedding is provided."""
    mock_user_id = 123
    results = matching.search_similar_jobs(db=mock_db_session, resume_embedding=None, user_id=mock_user_id, limit=5)
    assert results == []
    results = matching.search_similar_jobs(db=mock_db_session, resume_embedding=[], user_id=mock_user_id, limit=5)
    assert results == []