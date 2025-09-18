# Sistema-Distribuido - Cidade-Inteligente - API-Gateway
*Windows/poweshell*
- Invoke-WebRequest -Uri "http://localhost:5000/api/semaforo/modo" -Method POST -ContentType "application/json" -Body '{"modo":"normal"}'
- Invoke-WebRequest -Uri "http://localhost:5000/api/iluminacao/modo" -Method POST -ContentType "application/json" -Body '{"modo": "falha"}'

*Linux/bash*
- curl -X POST http://localhost:5000/api/iluminacao/modo -H "Content-Type: application/json" -d '{"modo": "falha"}'

*Windows*
- python -m venv venv
- .\venv\Scripts\activate
- pip install flask
- pip install flask-cors
- pip install requests 

*Linux/MacOs*
- python3 -m venv venv
- source venv/bin/cativante
- pip3 install flask
- pip3 install flask-cors
- pip3 install requests