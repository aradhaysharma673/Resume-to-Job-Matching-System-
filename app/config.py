from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "Resume-Job Matcher API"
    version: str = "1.0.0"
    
    # File limits
    max_file_size: int = 5_000_000  # 5MB
    allowed_extensions: list = [".pdf", ".docx", ".txt"]
    
    # Rate limiting
    rate_limit_requests: int = 20
    rate_limit_window: int = 60  # seconds
    
    # Matching thresholds
    excellent_match: float = 0.75
    good_match: float = 0.60
    fair_match: float = 0.40
    
    class Config:
        env_file = ".env"

settings = Settings()
