# ZapBot API - Documentação

## Visão Geral

ZapBot é uma aplicação FastAPI que fornece uma interface para integração com WhatsApp através da Evolution API. A aplicação segue as melhores práticas de desenvolvimento com FastAPI.

## Estrutura do Projeto

```
zapbot/
├── app/
│   ├── __init__.py
│   ├── config.py          # Configurações da aplicação
│   ├── models.py          # Modelos Pydantic
│   ├── routers/           # Rotas da API
│   │   ├── __init__.py
│   │   ├── health.py      # Health checks
│   │   ├── instances.py   # Gerenciamento de instâncias
│   │   └── messages.py    # Envio de mensagens
│   └── services/          # Serviços de negócio
│       ├── __init__.py
│       └── evolution_service.py
├── app.py                 # Aplicação principal
├── evolution_client.py    # Cliente Python (legado)
├── docker-compose.yml     # Configuração Docker
└── pyproject.toml         # Dependências
```

## Instalação e Execução

### 1. Instalar dependências
```bash
poetry install
```

### 2. Configurar variáveis de ambiente
Copie o arquivo `env.example` para `.env` e configure as variáveis necessárias.

### 3. Iniciar os containers Docker
```bash
docker-compose up -d
```

### 4. Executar a aplicação
```bash
poetry run python app.py
```

A aplicação estará disponível em: http://localhost:8000

## Endpoints da API

### Health Check
- `GET /health/` - Status geral da aplicação
- `GET /health/evolution` - Status da Evolution API

### Instâncias
- `POST /instances/` - Criar nova instância
- `GET /instances/{instance_name}/qrcode` - Obter QR code
- `GET /instances/{instance_name}/qrcode/wait` - Aguardar QR code
- `GET /instances/{instance_name}/status` - Status da instância
- `DELETE /instances/{instance_name}` - Remover instância
- `POST /instances/{instance_name}/qrcode/save` - Salvar QR code como imagem

### Mensagens
- `POST /messages/{instance_name}/send` - Enviar mensagem
- `POST /messages/{instance_name}/send-text` - Enviar mensagem (simplificado)

## Documentação Interativa

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Exemplo de Uso

### 1. Criar uma instância
```bash
curl -X POST "http://localhost:8000/instances/" \
  -H "Content-Type: application/json" \
  -d '{
    "instance_name": "minha_instancia",
    "qrcode": true,
    "integration": "WHATSAPP-BAILEYS"
  }'
```

### 2. Obter QR code
```bash
curl -X GET "http://localhost:8000/instances/minha_instancia/qrcode/wait"
```

### 3. Enviar mensagem
```bash
curl -X POST "http://localhost:8000/messages/minha_instancia/send" \
  -H "Content-Type: application/json" \
  -d '{
    "number": "5511999999999",
    "message": "Olá! Esta é uma mensagem do ZapBot",
    "message_type": "text"
  }'
```

## Características

- ✅ **FastAPI** com documentação automática
- ✅ **Pydantic** para validação de dados
- ✅ **Async/Await** para operações assíncronas
- ✅ **CORS** configurado
- ✅ **Error Handling** global
- ✅ **Health Checks** para monitoramento
- ✅ **Estrutura modular** e escalável
- ✅ **Type Hints** em todo o código
- ✅ **Logging** configurável

## Próximos Passos

- [ ] Implementar autenticação JWT
- [ ] Adicionar webhooks para receber mensagens
- [ ] Implementar cache Redis
- [ ] Adicionar testes unitários
- [ ] Configurar CI/CD
- [ ] Adicionar métricas e monitoramento
