from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    PROJECT_NAME: str = "JobBright"
    API_V1_STR: str = "/api/v1"

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://user:password@host:port/db")

    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "a_very_secret_key_that_should_be_changed")
    ALGORITHM: str = "HS256" # Note: Auth0 typically uses RS256, this might be unused or for other purposes
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30 # Example: 30 minutes

    # Auth0
    AUTH0_DOMAIN: str = os.getenv("AUTH0_DOMAIN", "")
    AUTH0_API_AUDIENCE: str = os.getenv("AUTH0_API_AUDIENCE", "")

    # Add other settings as needed (e.g., Stripe keys, external API keys)
    STRIPE_SECRET_KEY: str | None = os.getenv("STRIPE_SECRET_KEY")
    STRIPE_PUBLISHABLE_KEY: str | None = os.getenv("STRIPE_PUBLISHABLE_KEY")
    STRIPE_WEBHOOK_SECRET: str | None = os.getenv("STRIPE_WEBHOOK_SECRET")

    # Celery / Redis
    CELERY_BROKER_URL: str = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
    CELERY_RESULT_BACKEND: str = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

    # Qdrant
    QDRANT_HOST: str = os.getenv("QDRANT_HOST", "localhost")
    QDRANT_PORT: int = int(os.getenv("QDRANT_PORT", 6333))
    QDRANT_API_KEY: str | None = os.getenv("QDRANT_API_KEY") # Added for Qdrant Cloud auth


    # Azure OpenAI
    AZURE_OPENAI_ENDPOINT: str | None = os.getenv("AZURE_OPENAI_ENDPOINT")
    AZURE_OPENAI_API_KEY: str | None = os.getenv("AZURE_OPENAI_API_KEY")
    AZURE_OPENAI_DEPLOYMENT_NAME: str | None = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME") # Your deployment name (e.g., gpt-4-turbo)
    AZURE_OPENAI_API_VERSION: str | None = os.getenv("AZURE_OPENAI_API_VERSION") # e.g., "2023-05-15"

    # Other Model Names
    SPACY_MODEL_NAME: str = os.getenv("SPACY_MODEL_NAME", "en_core_web_sm")
    # OPENAI_MODEL_NAME is deprecated, use AZURE_OPENAI_DEPLOYMENT_NAME

    # Stripe Price ID to Internal Tier Mapping
    # Example: STRIPE_PRICE_ID_TIER_MAP = '{"price_pro_monthly":"pro", "price_pro_annual":"pro", "price_elite_monthly":"elite"}'
    # Use JSON format in the environment variable
    # IMPORTANT: Replace placeholder keys with your actual Stripe Price IDs!
    STRIPE_PRICE_ID_TIER_MAP_JSON: str = os.getenv("STRIPE_PRICE_ID_TIER_MAP_JSON", '{}') 

    # External Services
    SLACK_WEBHOOK_URL: str | None = os.getenv("SLACK_WEBHOOK_URL")


    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()
