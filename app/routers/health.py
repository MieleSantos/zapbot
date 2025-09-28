"""
Rotas para health check e status da aplicação
"""
from fastapi import APIRouter
from app.models import HealthResponse
from app.services.evolution_service import evolution_service
from app.config import settings

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/", response_model=HealthResponse)
async def health_check():
    """Verifica o status da aplicação e dependências"""
    evolution_status = "healthy" if await evolution_service.health_check() else "unhealthy"
    
    return HealthResponse(
        status="healthy",
        version=settings.app_version,
        evolution_api_status=evolution_status
    )


@router.get("/evolution")
async def evolution_health_check():
    """Verifica especificamente o status da Evolution API"""
    is_healthy = await evolution_service.health_check()
    
    return {
        "evolution_api": "healthy" if is_healthy else "unhealthy",
        "url": settings.evolution_api_url,
        "status_code": 200 if is_healthy else 500
    }

