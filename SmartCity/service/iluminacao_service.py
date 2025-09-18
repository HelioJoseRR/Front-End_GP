from flask import Flask, jsonify, request
import random
import time

app = Flask(__name__)

modo_operacao = "normal"

inicio_ciclo = time.time()
ciclo_total = 12

def calcular_estado_iluminacao():

    tempo_corrido = (time.time() - inicio_ciclo) % ciclo_total

    if tempo_corrido < 6:
        return "acesa"
    else:
        return "apagada"

@app.route("/estado", methods = ["GET"])
def estado_iluminacao():

    if modo_operacao == "falha":
        estado = "falha"
    elif modo_operacao == "manutenção":
        estado = "desligado"
    else:
        estado = calcular_estado_iluminacao()
    #time.sleep(random.uniform(0.5,2))    
    return jsonify({"iluminacao": estado})

@app.route("/modo", methods = ["POST"])
def mudar_modo():
    global modo_operacao
    dados = request.get_json()

    if not dados or "modo" not in dados:
        return jsonify({"erro": "informe o modo JSON, ex: {\"modo\" : \"manutenção\"}"}), 400
    
    novo_modo = dados["modo"]

    if novo_modo not in ["normal", "falha", "manutenção"]:
        return jsonify({"erro": "Modo inválido. Use normal, falha ou manutenção"}), 400
    
    modo_operacao = novo_modo
    return jsonify({"mensagem":f"Modo alterado para {modo_operacao}"}), 200

@app.route("/modo", methods = ["GET"])
def obter_modo():
    global modo_operacao
    return jsonify({"modo": modo_operacao})

if __name__ == "__main__":
    app.run(host = "0.0.0.0", port = 5002)