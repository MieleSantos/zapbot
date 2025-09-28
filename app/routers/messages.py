"""
Rotas para envio de mensagens
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any

from app.models import SendMessageRequest, SendMessageResponse
from app.services.evolution_service import evolution_service

router = APIRouter(prefix="/messages", tags=["messages"])


@router.post("/{instance_name}/send", response_model=SendMessageResponse)
async def send_message(instance_name: str, request: SendMessageRequest):
    """Envia uma mensagem de texto"""
    try:
        result = await evolution_service.send_message(
            instance_name=instance_name,
            number=request.number,
            message=request.message
        )
        
        # Verifica se a mensagem foi enviada com sucesso
        # A Evolution API retorna os dados da mensagem diretamente quando sucesso
        if 'key' in result and 'id' in result.get('key', {}):
            # Sucesso - mensagem enviada
            message_id = result['key']['id']
            return SendMessageResponse(
                success=True,
                message_id=message_id
            )
        elif result.get('status') == 'SUCCESS' or result.get('success') == True:
            # Formato alternativo de sucesso
            message_id = None
            if 'response' in result:
                response_data = result['response']
                if isinstance(response_data, dict):
                    message_id = (response_data.get('key', {}).get('id') or 
                                response_data.get('id') or 
                                response_data.get('messageId'))
            
            return SendMessageResponse(
                success=True,
                message_id=message_id
            )
        else:
            # Erro
            error_message = 'Erro desconhecido'
            if 'response' in result:
                response_data = result['response']
                if isinstance(response_data, dict):
                    error_message = response_data.get('message', error_message)
                elif isinstance(response_data, str):
                    error_message = response_data
            elif 'message' in result:
                error_message = result['message']
            
            return SendMessageResponse(
                success=False,
                error=str(error_message)  # Garante que seja string
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao enviar mensagem: {str(e)}")


@router.post("/{instance_name}/send-text")
async def send_text_message(instance_name: str, number: str, message: str):
    """Envia uma mensagem de texto (endpoint simplificado)"""
    try:
        result = await evolution_service.send_message(
            instance_name=instance_name,
            number=number,
            message=message
        )
        
        return {
            "success": result.get('status') == 'SUCCESS',
            "data": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao enviar mensagem: {str(e)}")
