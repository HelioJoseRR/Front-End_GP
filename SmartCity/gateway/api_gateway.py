from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import requests
import logging
import time
import sqlite3
from argon2 import PasswordHasher
import os

app = Flask(__name__)
CORS(app)

DATABASE = 'database.db'

def get_db():
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('../banco/schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

ph = PasswordHasher()
def hash_password(password):
    
    senha_com_pepper = (password + os.getenv('PEPPER')).encode('utf-8')
    return  ph.hash(senha_com_pepper)

def verify_password(stored_hash, provided_password):
    senha_com_pepper = (provided_password + os.getenv('PEPPER')).encode('utf-8')
    try:
        ph.verify(stored_hash, senha_com_pepper)
        return True
    except:
        return False

@app.route('/initdb')
def init_database():
    init_db()
    return "Database iniciado"

@app.route('/add_user', methods=['POST'])
def novo_usuario():
    if request.method == 'POST':
        usuario = request.json.get('usuario')
        senha = request.json.get('senha')
        if not usuario or not senha:
            return jsonify({'erro': 'Usuário e senha são obrigatórios'}), 400
        senha_hash = hash_password(senha)
        try:
            db = get_db()
            cursor = db.cursor()
            cursor.execute("INSERT INTO usuarios (usuario, senha_hash) VALUES (?, ?)", (usuario, senha_hash))
            db.commit()
            return jsonify({'mensagem': 'Usuário criado com sucesso'}), 201
        except sqlite3.Error as e:
            return jsonify({'erro': str(e)}), 500
        finally:
            db.close()

@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        usuario = request.json.get('usuario')
        senha = request.json.get('senha')
        if not usuario or not senha:
            return jsonify({'erro': 'Usuário e senha são obrigatórios'}), 400
        try:
            db = get_db()
            cursor = db.cursor()
            cursor.execute("SELECT senha_hash FROM usuarios WHERE usuario = ?", (usuario, ))
            row = cursor.fetchone()
            if row and verify_password(row['senha_hash'], senha):
                return jsonify({'mensagem': 'Login bem-sucedido'}), 200
            else:
                return jsonify({'erro': 'Usuário ou senha inválidos'}), 401
        except sqlite3.Error as e:
            return jsonify({'erro': str(e)}), 500
        finally:
            db.close()

@app.route('/add_semaforo', methods=['POST'])
def novo_semaforo():
    if request.method == 'POST':
        localizacao = request.json.get('localizacao')
        estado = request.json.get('estado')
        tempo = request.json.get('tempo')
        try:
            db = get_db()
            cursor = db.cursor()
            cursor.execute("INSERT INTO semaforos (localizacao, estado, tempo) VALUES (?, ?, ?)", (localizacao, estado, tempo))
            db.commit()
            return jsonify({'mensagem': 'Semaforo criado com sucesso'}), 201
        except sqlite3.Error as e:
            return jsonify({'erro': str(e)}), 500
        finally:
            db.close()

@app.route('/get_semaforo/<int:id_semaforo>', methods=['GET'])
def busca_semaforo(id_semaforo):
    if request.method == 'GET':
        try:
            db = get_db()
            cursor = db.cursor()
            cursor.execute("SELECT * FROM semaforos WHERE id = ?", (id_semaforo, ))
            dado = cursor.fetchone()
            if dado:
                return jsonify(dict(dado)), 200
            else:
                return jsonify({'erro': 'Semáforo não encontrado'}), 404
        except sqlite3.Error as e:
            return jsonify({'erro': str(e)}), 500
        finally:
            db.close()

@app.route('/semaforos', methods=['GET'])
def get_semaforos():
    if request.method == 'GET':
        try:
            db = get_db()
            cursor = db.cursor()
            cursor.execute("SELECT * FROM semaforos")
            dado = cursor.fetchall()
            return jsonify(dict(dado)), 200
        except sqlite3.Error as e:
            return jsonify({'erro': str(e)}), 500
        finally:
            db.close()

@app.route('/update_semaforo/<int:id_semaforo>', methods=['PUT'])
def update_semaforo(id_semaforo):
    if request.method == 'PUT':
        localizacao = request.json.get('localizacao')
        estado = request.json.get('estado')
        tempo = request.json.get('tempo')
        if not localizacao or not estado or not tempo:
            return jsonify({'erro': 'Todos os campos são obrigatórios'}), 400
        try:
            db = get_db()
            cursor = db.cursor()
            cursor.execute("UPDATE semaforos SET localizacao = ?, estado = ?, tempo = ? WHERE id = ?", (localizacao, estado, tempo, id_semaforo))
            db.commit()
            return jsonify({'mensagem': 'Semáforo atualizado com sucesso'}), 200
        except sqlite3.Error as e:
            return jsonify({'erro': str(e)}), 500
        finally:
            db.close()

@app.route('/add_poste', methods=['POST'])
def novo_poste():
    if request.method == 'POST':
        localizacao = request.json.get('localizacao')
        estado = request.json.get('estado')
        atomatico = request.json.get('atomatico')
        try:
            db = get_db()
            cursor = db.cursor()
            cursor.execute("INSERT INTO postes (localizacao, estado, atomatico) VALUES (?, ?, ?)", (localizacao, estado, atomatico))
            db.commit()
            return jsonify({'mensagem': 'Poste criado com sucesso'}), 201
        except sqlite3.Error as e:
            return jsonify({'erro': str(e)}), 500
        finally:
            db.close()

@app.route('/get_poste/<int:id_poste>', methods=['GET'])
def busca_poste(id_poste):
    if request.method == 'GET':
        try:
            db = get_db()
            cursor = db.cursor()
            cursor.execute("SELECT * FROM postes WHERE id = ?", (id_poste, ))
            dado = cursor.fetchone()
            if dado:
                return jsonify(dict(dado)), 200
            else:
                return jsonify({'erro': 'Poste não encontrado'}), 404
        except sqlite3.Error as e:
            return jsonify({'erro': str(e)}), 500
        finally:
            db.close()

@app.route('/postes', methods=['GET'])
def get_postes():
    if request.method == 'GET':
        try:
            db = get_db()
            cursor = db.cursor()
            cursor.execute("SELECT * FROM postes")
            dado = cursor.fetchall()
            return jsonify(dict(dado)), 200
        except sqlite3.Error as e:
            return jsonify({'erro': str(e)}), 500
        finally:
            db.close()

@app.route('/update_poste/<int:id_poste>', methods=['PUT'])
def update_poste(id_poste):
    if request.method == 'PUT':
        localizacao = request.json.get('localizacao')
        estado = request.json.get('estado')
        atomatico = request.json.get('atomatico')
        if not localizacao or not estado or not atomatico:
            return jsonify({'erro': 'Todos os campos são obrigatórios'}), 400
        try:
            db = get_db()
            cursor = db.cursor()
            cursor.execute("UPDATE postes SET localizacao = ?, estado = ?, atomatico = ? WHERE id = ?", (localizacao, estado, atomatico, id_poste))
            db.commit()
            return jsonify({'mensagem': 'Poste atualizado com sucesso'}), 200
        except sqlite3.Error as e:
            return jsonify({'erro': str(e)}), 500
        finally:
            db.close()


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

SEMAFORO_URL = "http://semaforo:5001/estado"
ILUMINACAO_URL = "http://iluminacao:5002/estado"

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
            elif estado in ["ligado", "desligado"]:
                logging.info(f"{nome} estado forcado: {estado}")
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
        logging.info("Requisição recebida em /api/iluminacao")
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
    if modo not in ["normal", "falha", "manutenção", "ligar", "desligar"]:
        logging.error(f"Modo inválido recebido {modo}")
        return jsonify({"erro": "Modo inválido. Use normal, falha, manutenção, ligar ou desligar"}), 400
    try:
        resposta = requests.post(ILUMINACAO_URL.replace("/estado", "") + "/modo", json=dados)
        logging.info(f"Requisição enviada com sucesso para o serviço de iluminação, resposta: {resposta.json()}")
        return resposta.json(), resposta.status_code
    
    except Exception as e:
        logging.error(f"Erro ao comunicar com o serviço de iluminação: {e}")
        return jsonify({"erro": "Não foi possível alterar o modo de iluminação"}), 500

@app.route("/api/semaforo/modo", methods=["GET"])
def gateway_semaforo_modo():
    try:
        url_modo = SEMAFORO_URL.replace("/estado", "") + "/modo"
        resposta = requests.get(url_modo, timeout=5)
        return jsonify(resposta.json()), resposta.status_code
    except Exception as e:
        logging.error(f"Erro ao obter modo do semáforo: {e}")
        return jsonify({"erro": "Não foi possível obter o modo do semáforo"}), 500

if __name__ == "__main__":
    logging.info("Iniciando API Gateway...")
    app.run(host="0.0.0.0",port=5000, debug=True)