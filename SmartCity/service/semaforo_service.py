from flask import Flask, jsonify, request
import random
import time

app = Flask(__name__)

modo_operacao = "normal"

inicio_ciclo = time.time()
ciclo_total = 12

def calcular_estado_semaforo():

    tempo_corrido = (time.time() - inicio_ciclo) % ciclo_total

    if tempo_corrido < 5:
        return "verde"
    elif tempo_corrido < 7:
        return "amarelo"
    else:
        return "vermelho"

@app.route("/estado", methods = ["GET"])
def estado_semaforo():
    if modo_operacao == "normal":
        estado = calcular_estado_semaforo()
    elif modo_operacao == "intermitente":
        estado = "intermitente"
    else:
        estado = "desligado"
    return jsonify({"semaforo": estado})

@app.route("/modo", methods=["POST"])
def mudar_modo():
    global modo_operacao
    dados = request.get_json()

    if not dados or "modo" not in dados:
        return jsonify({"erro": "informe o modo no JSON, ex: {\"modo\": \"intermitente\"}"}), 400
    
    novo_modo = dados["modo"]

    if novo_modo not in ["normal", "intermitente", "falha"]:
        return jsonify({"erro": "Modo inválido. Use normal, intermitente ou falha"}), 400
    
    modo_operacao = novo_modo
    return jsonify({"mensagem":f"Modo alterado para {modo_operacao}"}), 200
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)