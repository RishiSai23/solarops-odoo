import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "Project SunFlow API Gateway"
    VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Odoo Connection Configuration
    ODOO_URL: str = os.getenv("ODOO_URL", "http://localhost:8069")
    ODOO_DB: str = os.getenv("ODOO_DB", "sunflow_demo")
    ODOO_USER: str = os.getenv("ODOO_USER", "admin")
    ODOO_PASSWORD: str = os.getenv("ODOO_PASSWORD", "admin")
    
    # When True, if Odoo is offline or unreachable, fall back gracefully to the mock sandbox engine
    SANDBOX_FALLBACK: bool = True

    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings()
