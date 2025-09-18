# Sistema-Distribuido - Cidade-Inteligente - API-Gateway

- Invoke-WebRequest -Uri "http://localhost:5000/api/semaforo/modo" -Method POST -ContentType "application/json" -Body '{"modo":"normal"}'
- Invoke-WebRequest -Uri "http://localhost:5000/api/iluminacao/modo" -Method POST -ContentType "application/json" -Body '{"modo": "falha"}'
