"""
Modelos Pydantic para validação de dados
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from enum import Enum


class InstanceStatus(str, Enum):
    """Status possíveis de uma instância"""
    CONNECTING = "connecting"
    OPEN = "open"
    CLOSE = "close"


class MessageType(str, Enum):
    """Tipos de mensagem suportados"""
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    DOCUMENT = "document"


class CreateInstanceRequest(BaseModel):
    """Modelo para criação de instância"""
    instance_name: str = Field(..., min_length=3, max_length=50, description="Nome da instância")
    qrcode: bool = Field(True, description="Gerar QR code")
    integration: str = Field("WHATSAPP-BAILEYS", description="Tipo de integração")


class InstanceResponse(BaseModel):
    """Resposta da criação de instância"""
    instance_name: str
    instance_id: str
    status: InstanceStatus
    qrcode_count: int = Field(0, description="Número de QR codes disponíveis")


class QRCodeResponse(BaseModel):
    """Resposta do QR code"""
    count: int = Field(..., description="Número de QR codes disponíveis")
    base64: Optional[str] = Field(None, description="QR code em base64")
    url: Optional[str] = Field(None, description="URL do QR code")


class SendMessageRequest(BaseModel):
    """Modelo para envio de mensagem"""
    number: str = Field(..., description="Número do destinatário (formato: 5511999999999)")
    message: str = Field(..., min_length=1, max_length=4096, description="Texto da mensagem")
    message_type: MessageType = Field(MessageType.TEXT, description="Tipo da mensagem")


class SendMessageResponse(BaseModel):
    """Resposta do envio de mensagem"""
    success: bool
    message_id: Optional[str] = None
    error: Optional[str] = None


class InstanceStatusResponse(BaseModel):
    """Resposta do status da instância"""
    instance_name: str
    state: InstanceStatus
    last_seen: Optional[str] = None


class WebhookData(BaseModel):
    """Dados recebidos via webhook"""
    event: str = Field(..., description="Tipo do evento")
    data: Dict[str, Any] = Field(..., description="Dados do evento")
    instance: str = Field(..., description="Nome da instância")


class HealthResponse(BaseModel):
    """Resposta de health check"""
    status: str = "healthy"
    version: str = "1.0.0"
    evolution_api_status: str = "unknown"
