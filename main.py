"""
ZapBot - Aplicação FastAPI para integração com WhatsApp via Evolution API
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from app.config import settings
from app.routers import instances, messages, health

# Criação da aplicação FastAPI
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Bot para WhatsApp usando Evolution API",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configuração de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=settings.cors_methods,
    allow_headers=settings.cors_headers,
)

# Inclusão dos routers
app.include_router(health.router)
app.include_router(instances.router)
app.include_router(messages.router)


@app.get("/")
async def root():
    """Rota raiz da aplicação"""
    return {
        "message": f"Bem-vindo ao {settings.app_name}",
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/health"
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Handler global para exceções não tratadas"""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Erro interno do servidor",
            "detail": str(exc) if settings.debug else "Erro interno"
        }
    )


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
