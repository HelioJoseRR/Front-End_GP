from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import requests
import logging
import time

app = Flask(__name__)
CORS(app)

logger = logging.getLogger()
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler("gateway.log")
file_handler.setLevel(logging.INFO)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

if not logger.handlers:
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
else:
    logger.handlers.clear()
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

SEMAFORO_URL ="http://127.0.0.1:5001/estado"
ILUMINACAO_URL = "http://127.0.0.1:5002/estado"

SLOW_THRESOLD = 1.0
@app.route("/")
def index():
    return send_from_directory("frontend", "index.html")
def chamar_servico(nome, url):
    try:
        inicio = time.time()
        resposta = requests.get(url, timeout = 5)
        duracao = time.time() - inicio
        dados = resposta.json()

        estado = list(dados.values())[0]

        if nome == "Iluminação":
            if estado in ["falha", "manutenção"]:
                logging.error(f"{nome} em problema {estado}")
            else:
                logging.info(f"{nome} estado normal: {estado}")
        elif nome == "Semáforo":
            if estado in ["intermitente", "desligado"]:
                logging.error(f"{nome} em problema: {estado}")
            else:
                logging.info(f"{nome} estado normal: {estado}")
        
        if duracao > SLOW_THRESOLD:
            logging.warning(f"{nome} demorou {duracao:.2f}s para responder.")
        return dados
    except Exception as e:
        logging.error(f"Erro ao chamar {nome}: {e}")
        raise

@app.route("/api/semaforo", methods = ["GET"])
def gateway_semaforo():
    try:
        logging.info("Requisição recebida em /api/semaforo")
        dados = chamar_servico("Semáforo", SEMAFORO_URL)

        return jsonify({"mensagem": "Resposta do API Gateway - Semáforo", "dados": dados})
    
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route("/api/iluminacao", methods = ["GET"])
def gateway_iluminacao():
    try:
        logging.info("Requisiçõ recebida em /api/iluminacao")
        dados = chamar_servico("Iluminação", ILUMINACAO_URL)

        return jsonify({"mensagem": "Resposta do API Gateway - Iluminação", "dados": dados})
    
    except Exception as e: 
        return jsonify({"erro": str(e)}), 500

@app.route("/api/semaforo/modo", methods = ["POST"])
def comando_semaforo():

    dados = request.get_json()
    logging.info(f"Requisição recebida para alterar modo do semáforo {dados}")

    if not dados:
        logging.error("Nenhum JSON enviado na requisição")
        return jsonify({"erro": "Nenhum JSON enviado"}), 400
    
    if "modo" not in dados:
        logging.error("Chave 'modo' ausente no JSON")
        return jsonify({"erro": "informe o modo no JSON, ex: {\"modo\": \"intermitente\"}"}), 400
    
    modo = dados["modo"]
    if modo not in ["normal", "intermitente", "falha"]:
        logging.error(f"Modo inválido recebido: {modo}")
        return jsonify({"erro": "Modo inválido. Use normal, intermitente ou falha"}), 400
    try:
        resposta = requests.post(SEMAFORO_URL.replace("/estado","") + "/modo", json=dados)
        logging.info(f"Requisição enviada com sucesso para o serviço de semáforo, resposta: {resposta.json()}")
        return resposta.json(), resposta.status_code
    
    except Exception as e:
        logging.error(f"Erro ao comunicar com o serviço de semáforo: {e}")
        return jsonify({"erro": "Não foi possível alterar o modo do semáforo"}), 500

@app.route("/api/iluminacao/modo", methods = ["POST"])
def comando_iluminacao():
    
    dados = request.get_json()
    logging.info(f"Requisição recebida para alterar modo da iluminação {dados}")

    if not dados:
        logging.error("Nenhum JSON enviado na requisição")
        return jsonify({"erro": "Nenhum JSON enviado"}), 400
    
    if "modo" not in dados:
        logging.error("Chave 'modo' ausente no JSON")
        return jsonify({"erro": "informe o modo no JSON, ex: {\"modo\": \"falha\"}"}), 400
    
    modo = dados["modo"]
    if modo not in ["normal", "falha", "manutenção"]:
        logging.error(f"Modo inválido recebido {modo}")
        return jsonify({"erro": "Modo inválido. Use normal, falha ou manutenção"}), 400
    try:
        resposta = requests.post(ILUMINACAO_URL.replace("/estado", "") + "/modo", json=dados)
        logging.info(f"Requisição enviada com sucesso para o serviço de iluminação, resposta: {resposta.json()}")
        return resposta.json(), resposta.status_code
    
    except Exception as e:
        logging.error(f"Erro ao comunicar com o serviço de iluminação: {e}")
        return jsonify({"erro": "Não foi possível alterar o modo de iluminação"}), 500

@app.route("/api/iluminacao/modo", methods=["GET"])
def gateway_iluminacao_modo():
    try:
        url_modo = ILUMINACAO_URL.replace("/estado", "") + "/modo"
        resposta = requests.get(url_modo, timeout=5)
        return jsonify(resposta.json()), resposta.status_code
    except Exception as e:
        logging.error(f"Erro ao obter modo da iluminação: {e}")
        return jsonify({"erro": "Não foi possível obter o modo da iluminação"}), 500

if __name__ == "__main__":
    logging.info("Iniciando API Gateway...")
    app.run(host="0.0.0.0",port=5000, debug=True)