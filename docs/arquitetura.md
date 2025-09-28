# Arquitetura do ZapBot

## Diagrama da Arquitetura

```mermaid
graph TB
    %% Cliente/Usuário
    Client[Cliente/Usuário]
    
    %% ZapBot FastAPI Application
    subgraph "ZapBot Application"
        FastAPI[FastAPI Server<br/>Port: 8000]
        
        subgraph "Routers"
            HealthRouter[Health Router<br/>/health]
            InstanceRouter[Instance Router<br/>/instances]
            MessageRouter[Message Router<br/>/messages]
        end
        
        subgraph "Services"
            EvolutionService[Evolution Service<br/>HTTP Client]
        end
        
        subgraph "Models"
            PydanticModels[Pydantic Models<br/>Validation & Serialization]
        end
        
        subgraph "Config"
            Settings[Settings<br/>Environment Variables]
        end
    end
    
    %% Evolution API
    subgraph "Evolution API Container"
        EvolutionAPI[Evolution API<br/>Port: 8080<br/>WhatsApp Integration]
    end
    
    %% Database Layer
    subgraph "Database Layer"
        PostgreSQL[(PostgreSQL<br/>Port: 5432<br/>Instance Data)]
        Redis[(Redis<br/>Port: 6379<br/>Cache & Sessions)]
    end
    
    %% WhatsApp
    WhatsApp[WhatsApp<br/>Mobile/Web]
    
    %% Connections
    Client -->|HTTP Requests| FastAPI
    FastAPI --> HealthRouter
    FastAPI --> InstanceRouter
    FastAPI --> MessageRouter
    
    InstanceRouter --> EvolutionService
    MessageRouter --> EvolutionService
    HealthRouter --> EvolutionService
    
    EvolutionService -->|HTTP API Calls| EvolutionAPI
    EvolutionAPI -->|Store Data| PostgreSQL
    EvolutionAPI -->|Cache Data| Redis
    EvolutionAPI <-->|WebSocket/QR Code| WhatsApp
    
    FastAPI --> Settings
    EvolutionService --> PydanticModels
    
    %% Styling
    classDef clientStyle fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    classDef appStyle fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    classDef serviceStyle fill:#e8f5e8,stroke:#1b5e20,stroke-width:2px
    classDef dbStyle fill:#fff3e0,stroke:#e65100,stroke-width:2px
    classDef whatsappStyle fill:#e0f2f1,stroke:#004d40,stroke-width:2px
    
    class Client clientStyle
    class FastAPI,HealthRouter,InstanceRouter,MessageRouter,EvolutionService,PydanticModels,Settings appStyle
    class EvolutionAPI serviceStyle
    class PostgreSQL,Redis dbStyle
    class WhatsApp whatsappStyle
```

## Componentes da Arquitetura

### 1. ZapBot FastAPI Application
- **FastAPI Server**: Servidor principal da aplicação (porta 8000)
- **Routers**: Módulos organizados por funcionalidade
  - Health Router: Monitoramento e status da aplicação
  - Instance Router: Gerenciamento de instâncias do WhatsApp
  - Message Router: Envio de mensagens
- **Services**: Camada de serviços para integração externa
  - Evolution Service: Cliente HTTP para comunicação com Evolution API
- **Models**: Modelos Pydantic para validação e serialização
- **Config**: Configurações da aplicação via variáveis de ambiente

### 2. Evolution API
- **Container**: Aplicação Evolution API (porta 8080)
- **Funcionalidades**: 
  - Integração com WhatsApp via Baileys
  - Gerenciamento de instâncias
  - Geração de QR Codes
  - Envio e recebimento de mensagens

### 3. Database Layer
- **PostgreSQL**: Banco de dados principal para persistência
  - Dados das instâncias
  - Histórico de mensagens
  - Contatos e chats
- **Redis**: Cache e gerenciamento de sessões
  - Cache de instâncias
  - Sessões temporárias
  - Dados de performance

### 4. Fluxo de Dados
1. Cliente faz requisições HTTP para o ZapBot
2. ZapBot processa via routers específicos
3. Services fazem chamadas para Evolution API
4. Evolution API gerencia conexões WhatsApp
5. Dados são persistidos no PostgreSQL
6. Cache é gerenciado via Redis

## Tecnologias Utilizadas
- **Backend**: FastAPI (Python)
- **WhatsApp Integration**: Evolution API
- **Database**: PostgreSQL
- **Cache**: Redis
- **Containerization**: Docker & Docker Compose
- **Validation**: Pydantic
- **HTTP Client**: aiohttp

