"""
Serviço para integração com Evolution API
"""
import asyncio
import base64
from typing import Optional, Dict, Any
import aiohttp
from app.config import settings
from app.models import InstanceStatus, QRCodeResponse, InstanceStatusResponse


class EvolutionService:
    """Serviço para comunicação com Evolution API"""
    
    def __init__(self):
        self.base_url = settings.evolution_api_url.rstrip('/')
        self.api_key = settings.evolution_api_key
        self.headers = {
            "Content-Type": "application/json",
            "apikey": self.api_key
        }
    
    async def create_instance(self, instance_name: str, qrcode: bool = True) -> Dict[str, Any]:
        """Cria uma nova instância do WhatsApp"""
        url = f"{self.base_url}/instance/create"
        data = {
            "instanceName": instance_name,
            "qrcode": qrcode,
            "integration": "WHATSAPP-BAILEYS"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data, headers=self.headers) as response:
                return await response.json()
    
    async def get_qr_code(self, instance_name: str) -> QRCodeResponse:
        """Obtém o QR Code para conectar o WhatsApp"""
        url = f"{self.base_url}/instance/connect/{instance_name}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.headers) as response:
                data = await response.json()
                return QRCodeResponse(
                    count=data.get('count', 0),
                    base64=data.get('base64'),
                    url=data.get('url')
                )
    
    async def wait_for_qr_code(self, instance_name: str, max_attempts: int = 30, delay: float = 2.0) -> Optional[str]:
        """Aguarda o QR Code ser gerado"""
        for attempt in range(max_attempts):
            try:
                qr_response = await self.get_qr_code(instance_name)
                
                if qr_response.count > 0 and qr_response.base64:
                    return qr_response.base64
                
                # Verifica o status da instância
                status = await self.get_instance_status(instance_name)
                
                if status.state == InstanceStatus.OPEN:
                    return None  # Já conectado
                elif status.state == InstanceStatus.CLOSE:
                    await self.get_qr_code(instance_name)  # Tenta reconectar
                
                await asyncio.sleep(delay)
                
            except Exception as e:
                print(f"Erro ao obter QR Code (tentativa {attempt + 1}): {e}")
                await asyncio.sleep(delay)
        
        return None
    
    async def get_instance_status(self, instance_name: str) -> InstanceStatusResponse:
        """Verifica o status da instância"""
        url = f"{self.base_url}/instance/connectionState/{instance_name}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.headers) as response:
                data = await response.json()
                instance_data = data.get('instance', {})
                return InstanceStatusResponse(
                    instance_name=instance_data.get('instanceName', instance_name),
                    state=InstanceStatus(instance_data.get('state', 'connecting')),
                    last_seen=instance_data.get('lastSeen')
                )
    
    async def send_message(self, instance_name: str, number: str, message: str) -> Dict[str, Any]:
        """Envia uma mensagem de texto"""
        url = f"{self.base_url}/message/sendText/{instance_name}"
        data = {
            "number": number,
            "text": message
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data, headers=self.headers) as response:
                try:
                    return await response.json()
                except Exception as e:
                    response_text = await response.text()
                    return {
                        "status": "ERROR",
                        "response": {
                            "message": f"Erro na resposta da Evolution API: {response_text}"
                        }
                    }
    
    async def delete_instance(self, instance_name: str) -> Dict[str, Any]:
        """Remove uma instância"""
        url = f"{self.base_url}/instance/delete/{instance_name}"
        
        async with aiohttp.ClientSession() as session:
            async with session.delete(url, headers=self.headers) as response:
                return await response.json()
    
    async def health_check(self) -> bool:
        """Verifica se a Evolution API está funcionando"""
        try:
            url = f"{self.base_url}/manager/fetchInstances"
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers) as response:
                    return response.status == 200
        except Exception:
            return False


# Instância global do serviço
evolution_service = EvolutionService()
