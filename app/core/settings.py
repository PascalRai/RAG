from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    llm_openai_model: str = "gpt-4.1-nano"
    openai_api_key: str = ""
    model_id: str = "text-embedding-3-small"
    
    qdrant_url: str = "http://localhost:6333"
    postgres_uri: str = "postgresql://postgres:postgres@postgres:5432/postgres"

    celery_broker_url: str = "amqp://user:password@localhost:5672//"
    celery_result_backend: str = "rpc://"

    class Config:
        env_file = ".env"

settings = Settings()