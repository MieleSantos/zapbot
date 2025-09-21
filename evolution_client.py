"""
Cliente para integração com Evolution API
"""
import asyncio
import json
import os
import aiohttp
import websockets
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()


class EvolutionAPIClient:
    """Cliente para comunicação com Evolution API"""
    
    def __init__(self, base_url: str = None, api_key: str = None):
        self.base_url = (base_url or os.getenv('EVOLUTION_API_URL', 'http://localhost:8080')).rstrip('/')
        self.api_key = api_key or os.getenv('EVOLUTION_API_KEY', 'evolution_api_key_123')
        self.headers = {
            "Content-Type": "application/json",
            "apikey": self.api_key
        }
    
    async def create_instance(self, instance_name: str) -> Dict[str, Any]:
        """Cria uma nova instância do WhatsApp"""
        url = f"{self.base_url}/instance/create"
        data = {
            "instanceName": instance_name,
            "qrcode": True,
            "integration": "WHATSAPP-BAILEYS"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data, headers=self.headers) as response:
                return await response.json()
    
    async def get_qr_code(self, instance_name: str) -> Dict[str, Any]:
        """Obtém o QR Code para conectar o WhatsApp"""
        url = f"{self.base_url}/instance/connect/{instance_name}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.headers) as response:
                return await response.json()
    
    async def send_message(self, instance_name: str, number: str, message: str) -> Dict[str, Any]:
        """Envia uma mensagem de texto"""
        url = f"{self.base_url}/message/sendText/{instance_name}"
        data = {
            "number": number,
            "text": message
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data, headers=self.headers) as response:
                return await response.json()
    
    async def send_media(self, instance_name: str, number: str, media_url: str, caption: str = "") -> Dict[str, Any]:
        """Envia uma mídia (imagem, vídeo, etc.)"""
        url = f"{self.base_url}/message/sendMedia/{instance_name}"
        data = {
            "number": number,
            "mediatype": "image",
            "media": media_url,
            "caption": caption
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data, headers=self.headers) as response:
                return await response.json()
    
    async def get_instance_status(self, instance_name: str) -> Dict[str, Any]:
        """Verifica o status da instância"""
        url = f"{self.base_url}/instance/connectionState/{instance_name}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.headers) as response:
                return await response.json()
    
    async def delete_instance(self, instance_name: str) -> Dict[str, Any]:
        """Remove uma instância"""
        url = f"{self.base_url}/instance/delete/{instance_name}"
        
        async with aiohttp.ClientSession() as session:
            async with session.delete(url, headers=self.headers) as response:
                return await response.json()
    
    async def listen_webhooks(self, webhook_url: str = "ws://localhost:8080/webhook"):
        """Escuta webhooks do Evolution API via WebSocket"""
        try:
            async with websockets.connect(webhook_url) as websocket:
                print("Conectado ao webhook do Evolution API")
                async for message in websocket:
                    data = json.loads(message)
                    await self.handle_webhook(data)
        except Exception as e:
            print(f"Erro ao conectar com webhook: {e}")
    
    async def handle_webhook(self, data: Dict[str, Any]):
        """Processa os webhooks recebidos"""
        event_type = data.get("event")
        
        if event_type == "messages.upsert":
            await self.handle_new_message(data)
        elif event_type == "connection.update":
            await self.handle_connection_update(data)
        elif event_type == "qrcode.updated":
            await self.handle_qr_update(data)
        else:
            print(f"Evento não tratado: {event_type}")
    
    async def handle_new_message(self, data: Dict[str, Any]):
        """Processa novas mensagens recebidas"""
        message_data = data.get("data", {})
        message = message_data.get("message", {})
        
        if message.get("fromMe"):
            return  # Ignora mensagens enviadas por nós
        
        # Aqui você pode implementar a lógica do seu bot
        print(f"Nova mensagem recebida: {message.get('message', {}).get('conversation', '')}")
    
    async def handle_connection_update(self, data: Dict[str, Any]):
        """Processa atualizações de conexão"""
        connection_data = data.get("data", {})
        state = connection_data.get("state")
        print(f"Status da conexão: {state}")
    
    async def handle_qr_update(self, data: Dict[str, Any]):
        """Processa atualizações do QR Code"""
        qr_data = data.get("data", {})
        qr_code = qr_data.get("qrcode")
        if qr_code:
            print(f"QR Code atualizado: {qr_code}")


# Exemplo de uso
async def main():
    client = EvolutionAPIClient()
    
    # Criar instância
    instance_name = "zapbot_instance"
    result = await client.create_instance(instance_name)
    print(f"Instância criada: {result}")
    
    # Obter QR Code
    qr_result = await client.get_qr_code(instance_name)
    print(f"QR Code: {qr_result}")
    
    # Verificar status
    status = await client.get_instance_status(instance_name)
    print(f"Status: {status}")


if __name__ == "__main__":
    asyncio.run(main())
