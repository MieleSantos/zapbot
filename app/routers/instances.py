"""
Rotas para gerenciamento de instâncias
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any
import base64

from app.models import (
    CreateInstanceRequest, 
    InstanceResponse, 
    QRCodeResponse, 
    InstanceStatusResponse
)
from app.services.evolution_service import evolution_service

router = APIRouter(prefix="/instances", tags=["instances"])


@router.post("/", response_model=InstanceResponse)
async def create_instance(request: CreateInstanceRequest):
    """Cria uma nova instância do WhatsApp"""
    try:
        result = await evolution_service.create_instance(
            instance_name=request.instance_name,
            qrcode=request.qrcode
        )
        
        if result.get('status') == 403:
            raise HTTPException(status_code=409, detail="Nome da instância já está em uso")
        
        instance_data = result.get('instance', {})
        qrcode_data = result.get('qrcode', {})
        
        return InstanceResponse(
            instance_name=instance_data.get('instanceName'),
            instance_id=instance_data.get('instanceId'),
            status=instance_data.get('status'),
            qrcode_count=qrcode_data.get('count', 0)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao criar instância: {str(e)}")


@router.get("/{instance_name}/qrcode", response_model=QRCodeResponse)
async def get_qr_code(instance_name: str):
    """Obtém o QR Code da instância"""
    try:
        qr_response = await evolution_service.get_qr_code(instance_name)
        return qr_response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter QR Code: {str(e)}")


@router.get("/{instance_name}/qrcode/wait")
async def wait_for_qr_code(instance_name: str):
    """Aguarda o QR Code ser gerado e retorna em base64"""
    try:
        qr_code = await evolution_service.wait_for_qr_code(instance_name)
        
        if qr_code:
            return {
                "success": True,
                "qrcode": qr_code,
                "message": "QR Code gerado com sucesso"
            }
        else:
            return {
                "success": False,
                "message": "QR Code não foi gerado ou instância já conectada"
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao aguardar QR Code: {str(e)}")


@router.get("/{instance_name}/status", response_model=InstanceStatusResponse)
async def get_instance_status(instance_name: str):
    """Obtém o status da instância"""
    try:
        status = await evolution_service.get_instance_status(instance_name)
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter status: {str(e)}")


@router.delete("/{instance_name}")
async def delete_instance(instance_name: str):
    """Remove uma instância"""
    try:
        result = await evolution_service.delete_instance(instance_name)
        return {"success": True, "message": "Instância removida com sucesso", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao remover instância: {str(e)}")


@router.post("/{instance_name}/qrcode/save")
async def save_qr_code_as_image(instance_name: str, background_tasks: BackgroundTasks):
    """Salva o QR Code como imagem"""
    try:
        qr_code = await evolution_service.wait_for_qr_code(instance_name)
        
        if not qr_code:
            raise HTTPException(status_code=404, detail="QR Code não disponível")
        
        # Remove o prefixo data:image/png;base64, se presente
        if qr_code.startswith('data:image'):
            qr_code = qr_code.split(',')[1]
        
        # Decodifica o base64 e salva como imagem
        image_data = base64.b64decode(qr_code)
        filename = f"qrcode_{instance_name}.png"
        
        with open(filename, 'wb') as f:
            f.write(image_data)
        
        return {
            "success": True,
            "filename": filename,
            "message": f"QR Code salvo como {filename}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao salvar QR Code: {str(e)}")
