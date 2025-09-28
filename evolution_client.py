"""
Cliente para integração com Evolution API
"""
import asyncio
import json
import os
import base64
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
    
    async def wait_for_qr_code(self, instance_name: str, max_attempts: int = 30, delay: float = 2.0) -> Optional[str]:
        """Aguarda o QR Code ser gerado"""
        print(f"Aguardando QR Code para a instância {instance_name}...")
        
        for attempt in range(max_attempts):
            try:
                qr_result = await self.get_qr_code(instance_name)
                
                # Verifica se há QR code disponível
                if qr_result.get('count', 0) > 0:
                    qr_data = qr_result.get('base64', '')
                    if qr_data:
                        print(f"QR Code gerado com sucesso! (tentativa {attempt + 1})")
                        return qr_data
                
                # Verifica o status da instância
                status = await self.get_instance_status(instance_name)
                instance_state = status.get('instance', {}).get('state', '')
                
                if instance_state == 'open':
                    print("Instância já conectada!")
                    return None
                elif instance_state == 'close':
                    print("Instância fechada. Tentando reconectar...")
                    await self.get_qr_code(instance_name)
                
                print(f"Tentativa {attempt + 1}/{max_attempts} - QR Code ainda não disponível. Aguardando {delay}s...")
                await asyncio.sleep(delay)
                
            except Exception as e:
                print(f"Erro ao obter QR Code (tentativa {attempt + 1}): {e}")
                await asyncio.sleep(delay)
        
        print("Timeout: QR Code não foi gerado dentro do tempo limite")
        return None
    
    def save_qr_code_image(self, qr_data: str, filename: str = "qrcode.png") -> bool:
        """Salva o QR Code como imagem"""
        try:
            # Remove o prefixo data:image/png;base64, se presente
            if qr_data.startswith('data:image'):
                qr_data = qr_data.split(',')[1]
            
            # Decodifica o base64 e salva como imagem
            image_data = base64.b64decode(qr_data)
            with open(filename, 'wb') as f:
                f.write(image_data)
            
            print(f"QR Code salvo como {filename}")
            return True
        except Exception as e:
            print(f"Erro ao salvar QR Code: {e}")
            return False
    
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
    
    # Aguardar e obter QR Code
    qr_code = await client.wait_for_qr_code(instance_name)
    
    if qr_code:
        # Salvar QR Code como imagem
        client.save_qr_code_image(qr_code, "whatsapp_qrcode.png")
        print("\n" + "="*50)
        print("QR CODE GERADO COM SUCESSO!")
        print("="*50)
        print("1. Abra o arquivo 'whatsapp_qrcode.png'")
        print("2. Escaneie o QR Code com seu WhatsApp")
        print("3. Aguarde a conexão ser estabelecida")
        print("="*50)
    else:
        print("Não foi possível gerar o QR Code")
    
    # Verificar status final
    status = await client.get_instance_status(instance_name)
    print(f"Status final: {status}")


if __name__ == "__main__":
    asyncio.run(main())
