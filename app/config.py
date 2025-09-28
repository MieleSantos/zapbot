"""
Configurações da aplicação
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configurações da aplicação"""
    
    # Configurações da aplicação
    app_name: str = "ZapBot"
    app_version: str = "1.0.0"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Configurações da Evolution API
    evolution_api_url: str = "http://localhost:8080"
    evolution_api_key: str = "evolution_api_key_123"
    
    # Configurações de segurança
    secret_key: str = "your_secret_key_here_change_in_production"
    
    # Configurações de CORS
    cors_origins: list[str] = ["*"]
    cors_methods: list[str] = ["*"]
    cors_headers: list[str] = ["*"]
    
    # Configurações de logging
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"  # Ignora campos extras do .env


# Instância global das configurações
settings = Settings()
