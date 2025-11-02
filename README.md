# Sistema-Distribuido - Cidade-Inteligente - API-Gateway

## 🚀 Rodando o Projeto

### Via Docker (Recomendado)

#### Pré-requisitos
- Docker
- Docker Compose

#### Passo 1: Construir e iniciar os containers
```bash
docker-compose up --build
```

Isso vai iniciar:
- **MySQL** na porta `3307`
- **Gateway API** na porta `5000`
- **Serviço Semáforo** na porta `5001`
- **Serviço Iluminação** na porta `5002`

#### Passo 2: Verificar se os serviços estão rodando
```bash
docker-compose ps
```

#### Passo 3: Parar os containers
```bash
docker-compose down
```

---

### Rodando Localmente

#### Pré-requisitos
- Python 3.9+
- MySQL Server
- pip

#### Passo 1: Criar ambiente virtual

**Windows (PowerShell)**
```powershell
python -m venv venv
.\venv\Scripts\activate
```

**Linux/MacOS**
```bash
python3 -m venv venv
source venv/bin/activate
```

#### Passo 2: Instalar dependências
```bash
pip install flask flask-cors requests Flask-SQLAlchemy argon2-cffi pymysql cryptography
```

#### Passo 3: Configurar banco de dados
- Certifique-se de que o MySQL está rodando
- Configure as variáveis de ambiente ou edite a conexão nos arquivos de serviço
- Rode o schema: `SmartCity/banco/schema.sql`

#### Passo 4: Executar os serviços em terminais separados

**Terminal 1 - Gateway API**
```bash
set FLASK_APP=SmartCity/gateway/api_gateway.py
set FLASK_ENV=development
flask run --host=0.0.0.0 --port=5000
```

**Terminal 2 - Serviço Semáforo**
```bash
python SmartCity/service/semaforo_service.py
```

**Terminal 3 - Serviço Iluminação**
```bash
python SmartCity/service/iluminacao_service.py
```

---

## 📡 Exemplos de Requisições

### Windows (PowerShell)
```powershell
Invoke-WebRequest -Uri "http://localhost:5000/api/semaforo/modo" -Method POST -ContentType "application/json" -Body '{"modo":"normal"}'
Invoke-WebRequest -Uri "http://localhost:5000/api/iluminacao/modo" -Method POST -ContentType "application/json" -Body '{"modo": "falha"}'
```

### Linux/MacOS (Bash)
```bash
curl -X POST http://localhost:5000/api/semaforo/modo -H "Content-Type: application/json" -d '{"modo":"normal"}'
curl -X POST http://localhost:5000/api/iluminacao/modo -H "Content-Type: application/json" -d '{"modo": "falha"}'
```