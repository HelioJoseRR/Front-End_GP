from flask import Flask, jsonify, request, send_from_directory, session, redirect, url_for
from flask_cors import CORS
import requests
import logging
import time
import pymysql
from argon2 import PasswordHasher
import os
from functools import wraps

app = Flask(__name__)
CORS(app)

app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True

def get_db():
    db = pymysql.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=int(os.getenv('DB_PORT', 3306)),
        user=os.getenv('DB_USER', 'smartcity_user'),
        password=os.getenv('DB_PASSWORD', 'smartcity_pass'),
        database=os.getenv('DB_NAME', 'smartcity'),
        cursorclass=pymysql.cursors.DictCursor
    )
    return db

ph = PasswordHasher()
def hash_password(password):
    
    senha_com_pepper = (password + os.getenv('PEPPER', '')).encode('utf-8')
    return  ph.hash(senha_com_pepper)

def verify_password(stored_hash, provided_password):
    senha_com_pepper = (provided_password + os.getenv('PEPPER', '')).encode('utf-8')
    try:
        ph.verify(stored_hash, senha_com_pepper)
        return True
    except Exception:
        return False

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario' not in session:
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

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
            cursor.execute("INSERT INTO usuarios (usuario, senha_hash) VALUES (%s, %s)", (usuario, senha_hash))
            db.commit()
            return jsonify({'mensagem': 'Usuário criado com sucesso'}), 201
        except pymysql.Error as e:
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
            cursor.execute("SELECT senha_hash FROM usuarios WHERE usuario = %s", (usuario, ))
            row = cursor.fetchone()
            if row and verify_password(row['senha_hash'], senha):
                session['usuario'] = usuario
                return jsonify({'mensagem': 'Login bem-sucedido'}), 200
            else:
                return jsonify({'erro': 'Usuário ou senha inválidos'}), 401
        except pymysql.Error as e:
            return jsonify({'erro': str(e)}), 500
        finally:
            db.close()

@app.route('/logout')
def logout():
    session.pop('usuario', None)
    return redirect(url_for('index'))

@app.route('/add_semaforo', methods=['POST'])
@login_required
def novo_semaforo():
    if request.method == 'POST':
        localizacao = request.json.get('localizacao')
        estado = request.json.get('estado')
        tempo = request.json.get('tempo')
        try:
            db = get_db()
            cursor = db.cursor()
            cursor.execute("INSERT INTO semaforos (localizacao, estado, tempo) VALUES (%s, %s, %s)", (localizacao, estado, tempo))
            db.commit()
            return jsonify({'mensagem': 'Semaforo criado com sucesso'}), 201
        except pymysql.Error as e:
            return jsonify({'erro': str(e)}), 500
        finally:
            db.close()

@app.route('/get_semaforo/<int:id_semaforo>', methods=['GET'])
@login_required
def busca_semaforo(id_semaforo):
    if request.method == 'GET':
        try:
            db = get_db()
            cursor = db.cursor()
            cursor.execute("SELECT * FROM semaforos WHERE id = %s", (id_semaforo, ))
            dado = cursor.fetchone()
            if dado:
                return jsonify(dado), 200
            else:
                return jsonify({'erro': 'Semáforo não encontrado'}), 404
        except pymysql.Error as e:
            return jsonify({'erro': str(e)}), 500
        finally:
            db.close()

@app.route('/semaforos', methods=['GET'])
@login_required
def get_semaforos():
    if request.method == 'GET':
        try:
            db = get_db()
            cursor = db.cursor()
            cursor.execute("SELECT * FROM semaforos")
            dado = cursor.fetchall()
            return jsonify(dado), 200
        except pymysql.Error as e:
            return jsonify({'erro': str(e)}), 500
        finally:
            db.close()

@app.route('/update_semaforo/<int:id_semaforo>', methods=['PUT'])
@login_required
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
            cursor.execute("UPDATE semaforos SET localizacao = %s, estado = %s, tempo = %s WHERE id = %s", (localizacao, estado, tempo, id_semaforo))
            db.commit()
            return jsonify({'mensagem': 'Semáforo atualizado com sucesso'}), 200
        except pymysql.Error as e:
            return jsonify({'erro': str(e)}), 500
        finally:
            db.close()

@app.route('/add_poste', methods=['POST'])
@login_required
def novo_poste():
    if request.method == 'POST':
        localizacao = request.json.get('localizacao')
        estado = request.json.get('estado')
        atomatico = request.json.get('atomatico')
        try:
            db = get_db()
            cursor = db.cursor()
            cursor.execute("INSERT INTO postes (localizacao, estado, atomatico) VALUES (%s, %s, %s)", (localizacao, estado, atomatico))
            db.commit()
            return jsonify({'mensagem': 'Poste criado com sucesso'}), 201
        except pymysql.Error as e:
            return jsonify({'erro': str(e)}), 500
        finally:
            db.close()

@app.route('/get_poste/<int:id_poste>', methods=['GET'])
@login_required
def busca_poste(id_poste):
    if request.method == 'GET':
        try:
            db = get_db()
            cursor = db.cursor()
            cursor.execute("SELECT * FROM postes WHERE id = %s", (id_poste, ))
            dado = cursor.fetchone()
            if dado:
                return jsonify(dado), 200
            else:
                return jsonify({'erro': 'Poste não encontrado'}), 404
        except pymysql.Error as e:
            return jsonify({'erro': str(e)}), 500
        finally:
            db.close()

@app.route('/postes', methods=['GET'])
@login_required
def get_postes():
    if request.method == 'GET':
        try:
            db = get_db()
            cursor = db.cursor()
            cursor.execute("SELECT * FROM postes")
            dado = cursor.fetchall()
            return jsonify(dado), 200
        except pymysql.Error as e:
            return jsonify({'erro': str(e)}), 500
        finally:
            db.close()

@app.route('/update_poste/<int:id_poste>', methods=['PUT'])
@login_required
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
            cursor.execute("UPDATE postes SET localizacao = %s, estado = %s, atomatico = %s WHERE id = %s", (localizacao, estado, atomatico, id_poste))
            db.commit()
            return jsonify({'mensagem': 'Poste atualizado com sucesso'}), 200
        except pymysql.Error as e:
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
    if 'usuario' in session:
        return redirect(url_for('dashboard'))
    return send_from_directory("frontend", "login.html")

@app.route("/dashboard")
@login_required
def dashboard():
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
                logger.error(f"{nome} em problema {estado}")
            elif estado in ["ligado", "desligado"]:
                logger.info(f"{nome} estado forcado: {estado}")
            else:
                logger.info(f"{nome} estado normal: {estado}")
        elif nome == "Semáforo":
            if estado in ["intermitente", "desligado"]:
                logger.error(f"{nome} em problema: {estado}")
            else:
                logger.info(f"{nome} estado normal: {estado}")
        
        if duracao > SLOW_THRESOLD:
            logging.warning(f"{nome} demorou {duracao:.2f}s para responder.")
        return dados
    except Exception as e:
        logging.error(f"Erro ao chamar {nome}: {e}")
        raise

@app.route("/api/semaforo", methods = ["GET"])
@login_required
def gateway_semaforo():
    try:
        logging.info("Requisição recebida em /api/semaforo")
        dados = chamar_servico("Semáforo", SEMAFORO_URL)

        return jsonify({"mensagem": "Resposta do API Gateway - Semáforo", "dados": dados})
    
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route("/api/iluminacao", methods = ["GET"])
@login_required
def gateway_iluminacao():
    try:
        logging.info("Requisição recebida em /api/iluminacao")
        dados = chamar_servico("Iluminação", ILUMINACAO_URL)

        return jsonify({"mensagem": "Resposta do API Gateway - Iluminação", "dados": dados})
    
    except Exception as e: 
        return jsonify({"erro": str(e)}), 500

@app.route("/api/semaforo/modo", methods = ["POST"])
@login_required
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
@login_required
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
@login_required
def gateway_semaforo_modo():
    try:
        url_modo = SEMAFORO_URL.replace("/estado", "") + "/modo"
        resposta = requests.get(url_modo, timeout=5)
        return jsonify(resposta.json()), resposta.status_code
    except Exception as e:
        logging.error(f"Erro ao obter modo do semáforo: {e}")
        return jsonify({"erro": "Não foi possível obter o modo do semáforo"}), 500

@app.route("/api/iluminacao/modo", methods=["GET"])
@login_required
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
