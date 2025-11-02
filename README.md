# 🏙️ SmartCity - Front-End Gateway

Um sistema integrado de **gerenciamento inteligente de cidades** com foco em **semáforos adaptativos** e **iluminação pública otimizada**. Desenvolvido com Flask, Bootstrap 5 e arquitetura em microsserviços usando Docker.

![Status](https://img.shields.io/badge/status-active-brightgreen)
![Python](https://img.shields.io/badge/python-3.9-blue)
![Flask](https://img.shields.io/badge/flask-2.x-orange)
![Docker](https://img.shields.io/badge/docker-ready-blue)
![License](https://img.shields.io/badge/license-MIT-green)

---

## 📋 Índice

- [Visão Geral](#visão-geral)
- [Características](#características)
- [Arquitetura](#arquitetura)
- [Pré-requisitos](#pré-requisitos)
- [Instalação](#instalação)
- [Uso](#uso)
- [API Endpoints](#api-endpoints)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Desenvolvimento](#desenvolvimento)
- [Cálculos de Eficiência](#cálculos-de-eficiência)
- [Contribuindo](#contribuindo)

---

## 🎯 Visão Geral

SmartCity é uma plataforma completa de gerenciamento urbano que permite aos usuários:

- ✅ Gerenciar **regiões** da cidade
- ✅ Otimizar **semáforos adaptativos** com cálculo de eficiência em tempo real
- ✅ Controlar **iluminação pública** com algoritmos de economiz de energia
- ✅ Visualizar **dashboards interativos** com métricas de desempenho
- ✅ Autenticar com segurança usando **Argon2**

---

## ⭐ Características

### 1. **Autenticação e Autorização**
- Login seguro com hash Argon2
- Sessões persistentes
- Pepper adicional para segurança extra
- Controle de acesso por usuário

### 2. **Gerenciamento de Regiões**
- Criar, listar e gerenciar regiões geográficas
- Descrição detalhada de cada região
- Isolamento de dados por usuário

### 3. **Semáforos Adaptativos**
- Cálculo de eficiência baseado em:
  - Estado (vermelho/amarelo/verde)
  - Tempo de ciclo (40-120 segundos)
  - Fluxo de veículos
  - Taxa de ocupação
  - Atraso médio
  - Throughput
  - Comprimento de fila
  - Conformidade com padrões ITE/MUTCD

### 4. **Iluminação Inteligente**
- Modo automático com detecção por infravermelho
- Controle de dimming (ajuste de brilho)
- Cálculo de eficiência considerando:
  - Estado operacional
  - Conformidade com padrões luminotécnicos
  - Luminância e iluminância
  - Eficiência energética
  - Fator de potência
  - Qualidade da luz

### 5. **Dashboard Interativo**
- Interface responsiva com Bootstrap 5
- Tema escuro moderno
- Gráficos em tempo real
- Top 5 semáforos mais/menos eficientes
- Top 5 postes mais/menos eficientes

---

## 🏗️ Arquitetura

### Microsserviços

```
┌─────────────────────────────────────────────────────────┐
│                    CLIENTE (navegador)                   │
│              Bootstrap 5 - Dark Theme                    │
└────────────────────────┬────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
   ┌────▼─────┐     ┌────▼─────┐    ┌────▼──────┐
   │ API       │     │ Gateway   │    │ Frontend  │
   │ Gateway   │     │ Gateway   │    │ Static    │
   │ (5000)    │────│ (5000)    │────│ (assets)  │
   └────┬─────┘     └────┬──────┘    └───────────┘
        │                │
   ┌────┴────┬───────────┴─────┐
   │          │                 │
┌──▼──┐  ┌───▼────┐  ┌────────▼───┐
│MySQL│  │Semáforo│  │Iluminação  │
│DB   │  │Service │  │ Service    │
│3306 │  │(5001)  │  │  (5002)    │
└─────┘  └────────┘  └────────────┘
```

### Stack Tecnológico

| Componente | Tecnologia | Versão |
|-----------|-----------|--------|
| **Backend** | Flask | 2.x |
| **Banco de Dados** | MySQL | 8.0 |
| **Frontend** | Bootstrap | 5.3 |
| **Containerização** | Docker | Latest |
| **Orquestração** | Docker Compose | 3.8 |
| **Python** | Python | 3.9 |
| **Segurança** | Argon2 | Latest |

---

## 📋 Pré-requisitos

### Obrigatório
- Docker 20.10+
- Docker Compose 1.29+
- Git

### Opcional (para desenvolvimento local)
- Python 3.9+
- pip
- MySQL Server 8.0+

---

## 🚀 Instalação

### 1. Clone o Repositório

```bash
git clone https://github.com/seu-usuario/front-end-gp.git
cd front-end-gp
```

### 2. Configure as Variáveis de Ambiente

```bash
# Criar arquivo .env
cat > .env << EOF
DB_HOST=mysql
DB_PORT=3306
DB_NAME=smartcity
DB_USER=smartcity_user
DB_PASSWORD=smartcity_pass
SECRET_KEY=seu-secret-key-aqui
PEPPER=seu-pepper-aqui
EOF
```

### 3. Build e Start do Docker

```bash
# Build das imagens
docker-compose build

# Iniciar os serviços
docker-compose up -d

# Verificar status
docker-compose ps
```

### 4. Acessar a Aplicação

```
Login: http://localhost:5000
Dashboard: http://localhost:5000/dashboard
```

---

## 💻 Uso

### Primeiro Acesso

1. **Criar usuário:**
   ```bash
   curl -X POST http://localhost:5000/add_user \
     -H "Content-Type: application/json" \
     -d '{"usuario": "admin", "senha": "123456"}'
   ```

2. **Fazer login:**
   ```bash
   # Acessar http://localhost:5000
   # Inserir credenciais
   ```

3. **Criar região:**
   - Clicar em "➕ Nova Região"
   - Preencher nome e descrição

4. **Adicionar semáforo:**
   - Selecionar região
   - Abrir aba "🚦 Semáforos"
   - Preencher localização e tempo de ciclo

5. **Adicionar poste:**
   - Selecionar região
   - Abrir aba "💡 Postes"
   - Ativar modo automático se desejado

---

## 📡 API Endpoints

### Autenticação

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/add_user` | Criar novo usuário |
| POST | `/login` | Login do usuário |
| GET | `/logout` | Logout |
| GET | `/api/auth-status` | Status da autenticação |

### Regiões

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/add_regiao` | Criar região |
| GET | `/regioes` | Listar regiões |
| GET | `/regioes/<id>` | Detalhes da região |

### Semáforos

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/add_semaforo` | Criar semáforo |
| GET | `/semaforos` | Listar semáforos |
| GET | `/get_semaforo/<id>` | Detalhes do semáforo |
| PUT | `/update_semaforo/<id>` | Atualizar semáforo |
| DELETE | `/semaforos/<id>` | Deletar semáforo |
| GET | `/semaforos/top5/<id>/<tipo>` | Top 5 (eficientes/ineficientes) |

### Postes

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/add_poste` | Criar poste |
| GET | `/postes` | Listar postes |
| GET | `/get_poste/<id>` | Detalhes do poste |
| PUT | `/update_poste/<id>` | Atualizar poste |
| DELETE | `/postes/<id>` | Deletar poste |
| GET | `/postes/top5/<id>/<tipo>` | Top 5 (eficientes/ineficientes) |

### Gateway de Serviços

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/semaforo` | Estado do semáforo |
| POST | `/api/semaforo/modo` | Alterar modo do semáforo |
| GET | `/api/iluminacao` | Estado da iluminação |
| POST | `/api/iluminacao/modo` | Alterar modo da iluminação |

---

## 📁 Estrutura do Projeto

```
Front-End_GP/
│
├── Dockerfile                          # Imagem Docker
├── docker-compose.yml                  # Orquestração de serviços
│
├── SmartCity/
│   ├── banco/
│   │   └── schema.sql                 # Schema do banco de dados
│   │
│   ├── gateway/
│   │   ├── api_gateway.py             # API Gateway principal
│   │   ├── frontend/
│   │   │   ├── login.html             # Página de login
│   │   │   └── index.html             # Dashboard
│   │   └── static/
│   │       ├── script_simple_new.js   # JavaScript do dashboard
│   │       ├── style_bootstrap.css    # Estilos Bootstrap
│   │       ├── login.js               # Script de login
│   │       └── login.css              # Estilos de login
│   │
│   └── service/
│       ├── semaforo_service.py        # Serviço de semáforo
│       └── iluminacao_service.py      # Serviço de iluminação
│
├── README.md                           # Este arquivo
├── .gitignore                          # Arquivos ignorados
└── .env.example                        # Exemplo de variáveis
```

---

## 🛠️ Desenvolvimento

### Setup Local

```bash
# Criar ambiente virtual
python -m venv venv

# Ativar ambiente
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Instalar dependências
pip install -r requirements.txt

# Rodar localmente
python SmartCity/gateway/api_gateway.py
```

### Estrutura de Branches

```
main (produção)
├── develop (staging)
│   ├── feature/autenticacao
│   ├── feature/semaforos
│   ├── feature/iluminacao
│   └── bugfix/dashboard
```

### Padrão de Commits

```bash
# Features
git commit -m "feat: adicionar suporte a novo tipo de sensor"

# Bugfixes
git commit -m "fix: corrigir cálculo de eficiência"

# Documentação
git commit -m "docs: atualizar README"

# Refatoração
git commit -m "refactor: simplificar lógica de autenticação"
```

---

## 📊 Cálculos de Eficiência

### Semáforo
A eficiência é calculada baseada em:
- **Estado**: vermelho (-8%), amarelo (-3%), verde (0%)
- **Tempo de ciclo**: ideal 60-90s (MUTCD)
- **Taxa de ocupação**: ideal 85% (v/c ratio)
- **Atraso médio**: HCM standard
- **Throughput**: veículos por hora
- **Fila**: limite de 20-30m
- **Pedestres**: demanda de travessia

**Range:** 0-100%

### Poste de Iluminação
A eficiência é calculada baseada em:
- **Estado operacional**: ligado/desligado
- **Conformidade luminotécnica**: padrões NBR/ABNT
- **Luminância**: nível de brilho
- **Eficiência energética**: consumo vs potência
- **Fator de potência**: qualidade da energia
- **Qualidade da luz**: temperatura de cor, IRC
- **Modo automático**: dimming + detecção IR

**Range:** 0-100%

---
