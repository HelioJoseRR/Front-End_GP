from flask import Flask, jsonify, request, send_from_directory, session, redirect, url_for
from flask_cors import CORS
import requests
import logging
import time
import pymysql
from argon2 import PasswordHasher
import os
from functools import wraps
import random

# Timestamp único para cada inicialização do servidor (force recarregar assets)
SERVER_START_TIME = int(time.time())

app = Flask(__name__)
CORS(app)

app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = True
app.config['SESSION_USE_SIGNER'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hora

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
    
    senha_com_pepper = password + os.getenv('PEPPER', '')
    return ph.hash(senha_com_pepper)

def verify_password(stored_hash, provided_password):
    senha_com_pepper = provided_password + os.getenv('PEPPER', '')
    try:
        ph.verify(stored_hash, senha_com_pepper)
        return True
    except Exception:
        return False

def calcular_eficiencia_semaforo(estado, tempo, **kwargs):
    """
    Calcula eficiência do semáforo baseado em métricas reais:
    - Fluxo de veículos (capacidade de passagem)
    - Taxa de ocupação (occupancy rate)
    - Atraso médio (average delay per vehicle)
    - Conformidade com padrões ITE/MUTCD
    - Throughput (veículos/hora)
    - Queue length (comprimento da fila)
    - Requisitos de pedestres
    
    Baseado em: NHTSA, ITE, AASHTO, e estudos de mobilidade urbana
    """
    
    eficiencia = 100.0
    
    # Dados com defaults realistas
    fluxo_veiculos = kwargs.get('fluxo_veiculos', 25)  # veículos/minuto
    taxa_ocupacao = kwargs.get('taxa_ocupacao', 65)     # percentual
    atraso_medio = kwargs.get('atraso_medio', 30)       # segundos
    capacidade_veiculos = kwargs.get('capacidade_veiculos', 30)
    throughput = kwargs.get('throughput', fluxo_veiculos * 60)  # veículos/hora
    queue_length = kwargs.get('queue_length', 5)        # metros
    pedidos_pedestres = kwargs.get('pedidos_pedestres', 0)
    
    # 1. ANÁLISE DE ESTADO ATUAL (15% do total)
    if estado == "vermelho":
        eficiencia -= 8  # Semáforo vermelho reduz passagem
    elif estado == "amarelo":
        eficiencia -= 3  # Amarelo permite transição
    elif estado == "verde":
        eficiencia -= 0  # Verde é ideal
    
    # 2. TEMPO DE CICLO ÓTIMO (20% do total)
    # Ideal: 60-90s (MUTCD), mínimo 40s, máximo 120s
    if tempo < 40:
        eficiencia -= 20  # Muito curto - inadequado
    elif tempo < 50:
        eficiencia -= 15
    elif tempo < 60:
        eficiencia -= 5
    elif 60 <= tempo <= 90:
        eficiencia += 0   # Ótimo
    elif tempo <= 110:
        eficiencia -= 5
    elif tempo <= 120:
        eficiencia -= 15
    else:
        eficiencia -= 20  # Muito longo - inadequado
    
    # 3. TAXA DE OCUPAÇÃO (25% do total)
    # v/c ratio ideal: 0.85-0.95 (capacity)
    if taxa_ocupacao < 50:
        eficiencia -= 10  # Subutilizado
    elif taxa_ocupacao < 70:
        eficiencia -= 5
    elif taxa_ocupacao <= 85:
        eficiencia += 5   # Ótimo
    elif taxa_ocupacao <= 95:
        eficiencia += 0   # Ainda aceitável
    elif taxa_ocupacao <= 105:
        eficiencia -= 10  # Começando a saturar
    else:
        eficiencia -= 25  # Supersaturado
    
    # 4. ATRASO MÉDIO (20% do total)
    # Padrão HCM: 0-10s: Excelente, 10-15s: Bom, 15-25s: Aceitável, >40s: Ruim
    if atraso_medio <= 10:
        eficiencia += 5
    elif atraso_medio <= 15:
        eficiencia += 0
    elif atraso_medio <= 25:
        eficiencia -= 5
    elif atraso_medio <= 40:
        eficiencia -= 15
    else:
        eficiencia -= 25
    
    # 5. THROUGHPUT (15% do total)
    # Máximo esperado: 1.8 veículos/segundo = 6480 veículos/hora por faixa
    max_throughput_esperado = capacidade_veiculos * 60
    if throughput >= max_throughput_esperado * 0.9:
        eficiencia += 10  # Alta eficiência de passagem
    elif throughput >= max_throughput_esperado * 0.7:
        eficiencia += 5
    elif throughput >= max_throughput_esperado * 0.5:
        eficiencia += 0
    elif throughput >= max_throughput_esperado * 0.3:
        eficiencia -= 5
    else:
        eficiencia -= 15  # Muito baixo
    
    # 6. COMPRIMENTO DA FILA (5% do total)
    # Limite máximo aceitável: 20-30 metros
    if queue_length <= 10:
        eficiencia += 3
    elif queue_length <= 20:
        eficiencia += 0
    elif queue_length <= 30:
        eficiencia -= 5
    elif queue_length <= 50:
        eficiencia -= 15
    else:
        eficiencia -= 25
    
    # 7. CONFORMIDADE COM PADRÕES
    conformidade = 100.0
    # Verificar tempos de ciclo compatíveis
    if 60 <= tempo <= 90:
        conformidade += 5
    # Verificar pedestres
    if pedidos_pedestres > 0:
        conformidade -= min(10, pedidos_pedestres * 2)
    
    # Ajuste final de conformidade
    eficiencia += (conformidade - 100) * 0.1
    
    # Garante valor entre 0 e 100
    return max(0, min(100, round(eficiencia, 1)))


def calcular_eficiencia_poste(estado, automatico, **kwargs):
    """
    Calcula eficiência do poste de iluminação baseado em métricas reais:
    Escala revisada para dar melhor diferenciação
    """
    
    eficiencia = 70.0  # Base 70% (não mais 100%)
    
    potencia_nominal = kwargs.get('potencia_nominal', 150)
    consumo_real = kwargs.get('consumo_real', 100)
    luminancia_media = kwargs.get('luminancia_media', 1.5)
    iluminancia_minima = kwargs.get('iluminancia_minima', 5)
    iluminancia_media = kwargs.get('iluminancia_media', 15)
    uniformidade = kwargs.get('uniformidade', 0.4)
    fator_potencia = kwargs.get('fator_potencia', 0.95)
    temperatura_cor = kwargs.get('temperatura_cor', 4000)
    indice_reproducao_cor = kwargs.get('indice_reproducao_cor', 70)
    taxa_ocupacao_via = kwargs.get('taxa_ocupacao_via', 60)
    modo_dimming = kwargs.get('modo_dimming', 1)
    infrared_detection = kwargs.get('infrared_detection', 1)
    
    # 1. ESTADO OPERACIONAL (10% do total)
    if estado == 0:
        eficiencia -= 50  # Desligado = ruim
    elif estado == 1:
        eficiencia += 0   # Ligado = ok
    
    # 2. CONFORMIDADE COM PADRÕES LUMINOTÉCNICOS (25% do total)
    if 10 <= iluminancia_media <= 20 and uniformidade >= 0.35:
        eficiencia += 15  # Perfeito
    elif 8 <= iluminancia_media <= 22 and uniformidade >= 0.30:
        eficiencia += 8
    elif 6 <= iluminancia_media <= 28 and uniformidade >= 0.25:
        eficiencia += 2
    elif iluminancia_media < 5 or iluminancia_media > 30:
        eficiencia -= 20  # Ruim
    else:
        eficiencia -= 10
    
    # 3. LUMINÂNCIA (15% do total)
    if 0.75 <= luminancia_media <= 1.5:
        eficiencia += 12
    elif 0.5 <= luminancia_media <= 2.0:
        eficiencia += 5
    elif luminancia_media < 0.3 or luminancia_media > 2.5:
        eficiencia -= 18  # Muito errado
    else:
        eficiencia -= 8
    
    # 4. EFICIÊNCIA ENERGÉTICA (20% do total)
    percentual_consumo = (consumo_real / potencia_nominal) * 100 if potencia_nominal > 0 else 100
    if percentual_consumo <= 40:
        eficiencia += 20  # Excelente
    elif percentual_consumo <= 60:
        eficiencia += 12
    elif percentual_consumo <= 80:
        eficiencia += 5
    elif percentual_consumo <= 100:
        eficiencia -= 8
    else:
        eficiencia -= 25  # Muito consumo
    
    # 5. FATOR DE POTÊNCIA (10% do total)
    if fator_potencia >= 0.95:
        eficiencia += 10
    elif fator_potencia >= 0.90:
        eficiencia += 5
    elif fator_potencia >= 0.85:
        eficiencia -= 8
    else:
        eficiencia -= 18  # Ruim
    
    # 6. QUALIDADE DA LUZ (10% do total)
    if temperatura_cor in [3000, 4000, 5000] and indice_reproducao_cor >= 70:
        eficiencia += 10
    elif temperatura_cor >= 2700 and indice_reproducao_cor >= 60:
        eficiencia += 4
    else:
        eficiencia -= 12
    
    # 7. MODO AUTOMÁTICO/INTELIGENTE (10% do total)
    if automatico == 1:
        eficiencia += 8
        if modo_dimming == 1:
            eficiencia += 5
        if infrared_detection == 1:
            eficiencia += 5
    else:
        eficiencia -= 5  # Penalidade por não ser automático
    
    # 8. ADEQUAÇÃO À OCUPAÇÃO DA VIA (Adicional: -10 a +5)
    if taxa_ocupacao_via < 30:
        eficiencia -= 10
    elif taxa_ocupacao_via <= 70:
        eficiencia += 3
    elif taxa_ocupacao_via <= 95:
        eficiencia -= 2
    else:
        eficiencia -= 8
    
    return max(0, min(100, round(eficiencia, 1)))

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
        db = None
        try:
            db = get_db()
            cursor = db.cursor()
            cursor.execute("INSERT INTO usuarios (usuario, senha_hash) VALUES (%s, %s)", (usuario, senha_hash))
            db.commit()
            return jsonify({'mensagem': 'Usuário criado com sucesso'}), 201
        except pymysql.Error as e:
            return jsonify({'erro': str(e)}), 500
        finally:
            if db:
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

@app.route('/api/auth-status', methods=['GET'])
def auth_status():
    usuario = session.get('usuario', 'NENHUM')
    print(f"[AUTH-STATUS] Usuário na sessão: {usuario}")
    if 'usuario' in session:
        print(f"[AUTH-STATUS] Autenticado - retornando 200")
        return jsonify({'autenticado': True, 'usuario': session['usuario']}), 200
    print(f"[AUTH-STATUS] NÃO autenticado - retornando 401")
    return jsonify({'autenticado': False}), 401

@app.route('/add_regiao', methods=['POST'])
@login_required
def nova_regiao():
    if request.method == 'POST':
        nome = request.json.get('nome')
        descricao = request.json.get('descricao', '')
        if not nome:
            return jsonify({'erro': 'Nome da região é obrigatório'}), 400
        try:
            db = get_db()
            cursor = db.cursor()
            # Pegar usuario_id da sessão
            usuario = session.get('usuario')
            cursor.execute("SELECT id FROM usuarios WHERE usuario = %s", (usuario,))
            user_result = cursor.fetchone()
            
            if not user_result:
                return jsonify({'erro': 'Usuário não encontrado'}), 404
            
            usuario_id = user_result['id']
            cursor.execute("INSERT INTO regioes (usuario_id, nome, descricao) VALUES (%s, %s, %s)", (usuario_id, nome, descricao))
            db.commit()
            return jsonify({'mensagem': 'Região criada com sucesso'}), 201
        except pymysql.Error as e:
            return jsonify({'erro': str(e)}), 500
        finally:
            if db:
                db.close()

@app.route('/regioes', methods=['GET'])
@login_required
def get_regioes():
    db = None
    print("[REGIOES] Requisição recebida")
    try:
        db = get_db()
        cursor = db.cursor()
        usuario = session.get('usuario')
        
        # Pegar usuario_id
        cursor.execute("SELECT id FROM usuarios WHERE usuario = %s", (usuario,))
        user_result = cursor.fetchone()
        
        if not user_result:
            return jsonify({'erro': 'Usuário não encontrado'}), 404
        
        usuario_id = user_result['id']
        cursor.execute("SELECT id, nome, descricao FROM regioes WHERE usuario_id = %s ORDER BY nome", (usuario_id,))
        dados = cursor.fetchall()
        print(f"[REGIOES] Retornando {len(dados) if dados else 0} regiões para usuário {usuario}")
        return jsonify(dados), 200
    except pymysql.Error as e:
        print(f"[REGIOES] Erro SQL: {str(e)}")
        return jsonify({'erro': str(e)}), 500
    finally:
        if db:
            db.close()

@app.route('/regioes/<int:regiao_id>', methods=['GET'])
@login_required
def get_regiao_details(regiao_id):
    db = None
    try:
        db = get_db()
        cursor = db.cursor()
        usuario = session.get('usuario')
        
        # Pegar usuario_id
        cursor.execute("SELECT id FROM usuarios WHERE usuario = %s", (usuario,))
        user_result = cursor.fetchone()
        
        if not user_result:
            return jsonify({'erro': 'Usuário não encontrado'}), 404
        
        usuario_id = user_result['id']
        cursor.execute("SELECT id, nome, descricao FROM regioes WHERE id = %s AND usuario_id = %s", (regiao_id, usuario_id))
        regiao = cursor.fetchone()
        if not regiao:
            return jsonify({'erro': 'Região não encontrada ou acesso negado'}), 404
        return jsonify(regiao), 200
    except pymysql.Error as e:
        return jsonify({'erro': str(e)}), 500
    finally:
        if db:
            db.close()

@app.route('/add_semaforo', methods=['POST'])
@login_required
def novo_semaforo():
    if request.method == 'POST':
        regiao_id = request.json.get('regiao_id')
        localizacao = request.json.get('localizacao')
        estado = request.json.get('estado')
        tempo = request.json.get('tempo')
        if not regiao_id or not localizacao or not estado or not tempo:
            return jsonify({'erro': 'Todos os campos são obrigatórios'}), 400
        
        # Simular dados reais de tráfego
        fluxo_veiculos = random.randint(15, 40)
        taxa_ocupacao = random.randint(50, 100)
        atraso_medio = random.randint(10, 50)
        throughput = fluxo_veiculos * 60
        queue_length = random.randint(0, 50)
        
        eficiencia = calcular_eficiencia_semaforo(
            estado, tempo,
            fluxo_veiculos=fluxo_veiculos,
            taxa_ocupacao=taxa_ocupacao,
            atraso_medio=atraso_medio,
            throughput=throughput,
            queue_length=queue_length,
            pedidos_pedestres=random.randint(0, 5)
        )
        
        try:
            db = get_db()
            cursor = db.cursor()
            cursor.execute("""INSERT INTO semaforos 
                (regiao_id, localizacao, estado, tempo, eficiencia, fluxo_veiculos, 
                 taxa_ocupacao, atraso_medio, throughput, queue_length) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""", 
                (regiao_id, localizacao, estado, tempo, eficiencia, fluxo_veiculos,
                 taxa_ocupacao, atraso_medio, throughput, queue_length))
            db.commit()
            return jsonify({'mensagem': 'Semaforo criado com sucesso', 'eficiencia': eficiencia}), 201
        except pymysql.Error as e:
            return jsonify({'erro': str(e)}), 500
        finally:
            db.close()

@app.route('/get_semaforo/<int:id_semaforo>', methods=['GET'])
@login_required
def busca_semaforo(id_semaforo):
    if request.method == 'GET':
        db = None
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
            if db:
                db.close()

@app.route('/semaforos', methods=['GET'])
@login_required
def get_semaforos():
    regiao_id = request.args.get('regiao_id', type=int)
    db = None
    try:
        db = get_db()
        cursor = db.cursor()
        usuario = session.get('usuario')
        
        # Verificar se regiao pertence ao usuário
        cursor.execute("SELECT id FROM usuarios WHERE usuario = %s", (usuario,))
        user_result = cursor.fetchone()
        
        if not user_result:
            return jsonify({'erro': 'Usuário não encontrado'}), 404
        
        usuario_id = user_result['id']
        
        if regiao_id:
            # Validar que a regiao pertence ao usuário
            cursor.execute("SELECT id FROM regioes WHERE id = %s AND usuario_id = %s", (regiao_id, usuario_id))
            if not cursor.fetchone():
                return jsonify({'erro': 'Acesso negado'}), 403
            cursor.execute("SELECT * FROM semaforos WHERE regiao_id = %s ORDER BY eficiencia DESC", (regiao_id,))
        else:
            cursor.execute("""SELECT s.* FROM semaforos s 
                           INNER JOIN regioes r ON s.regiao_id = r.id 
                           WHERE r.usuario_id = %s 
                           ORDER BY s.eficiencia DESC""", (usuario_id,))
        dado = cursor.fetchall()
        return jsonify(dado), 200
    except pymysql.Error as e:
        return jsonify({'erro': str(e)}), 500
    finally:
        if db:
            db.close()

@app.route('/semaforos/top5/<int:regiao_id>/<tipo>', methods=['GET'])
@login_required
def get_top5_semaforos(regiao_id, tipo):
    db = None
    try:
        db = get_db()
        cursor = db.cursor()
        if tipo == 'eficientes':
            cursor.execute("SELECT * FROM semaforos WHERE regiao_id = %s ORDER BY eficiencia DESC LIMIT 5", (regiao_id,))
        elif tipo == 'ineficientes':
            cursor.execute("SELECT * FROM semaforos WHERE regiao_id = %s ORDER BY eficiencia ASC LIMIT 5", (regiao_id,))
        else:
            return jsonify({'erro': 'Tipo inválido. Use eficientes ou ineficientes'}), 400
        dados = cursor.fetchall()
        return jsonify(dados), 200
    except pymysql.Error as e:
        return jsonify({'erro': str(e)}), 500
    finally:
        if db:
            db.close()

@app.route('/update_semaforo/<int:id_semaforo>', methods=['PUT'])
@login_required
def update_semaforo(id_semaforo):
    if request.method == 'PUT':
        localizacao = request.json.get('localizacao')
        estado = request.json.get('estado')
        tempo = request.json.get('tempo')
        if not localizacao or not estado or not tempo:
            return jsonify({'erro': 'Campos obrigatórios faltando'}), 400
        try:
            # Simular novos dados de tráfego
            fluxo_veiculos = random.randint(15, 40)
            taxa_ocupacao = random.randint(50, 100)
            atraso_medio = random.randint(10, 50)
            throughput = fluxo_veiculos * 60
            queue_length = random.randint(0, 50)
            
            eficiencia = calcular_eficiencia_semaforo(
                estado, tempo,
                fluxo_veiculos=fluxo_veiculos,
                taxa_ocupacao=taxa_ocupacao,
                atraso_medio=atraso_medio,
                throughput=throughput,
                queue_length=queue_length,
                pedidos_pedestres=random.randint(0, 5)
            )
            
            db = get_db()
            cursor = db.cursor()
            query = """UPDATE semaforos SET localizacao = %s, estado = %s, tempo = %s, eficiencia = %s,
                       fluxo_veiculos = %s, taxa_ocupacao = %s, atraso_medio = %s, throughput = %s,
                       queue_length = %s WHERE id = %s"""
            params = [localizacao, estado, tempo, eficiencia, fluxo_veiculos, taxa_ocupacao, 
                     atraso_medio, throughput, queue_length, id_semaforo]
            cursor.execute(query, params)
            db.commit()
            return jsonify({'mensagem': 'Semáforo atualizado com sucesso', 'eficiencia': eficiencia}), 200
        except pymysql.Error as e:
            return jsonify({'erro': str(e)}), 500
        finally:
            db.close()

@app.route('/semaforos/<int:id_semaforo>', methods=['DELETE'])
@login_required
def deletar_semaforo(id_semaforo):
    if request.method == 'DELETE':
        try:
            db = get_db()
            cursor = db.cursor()
            cursor.execute("DELETE FROM semaforos WHERE id = %s", (id_semaforo,))
            db.commit()
            return jsonify({'mensagem': 'Semáforo deletado com sucesso'}), 200
        except pymysql.Error as e:
            return jsonify({'erro': str(e)}), 500
        finally:
            db.close()

@app.route('/add_poste', methods=['POST'])
@login_required
def novo_poste():
    if request.method == 'POST':
        regiao_id = request.json.get('regiao_id')
        localizacao = request.json.get('localizacao')
        estado = request.json.get('estado')
        automatico = request.json.get('automatico')
        if not regiao_id or not localizacao or estado is None or automatico is None:
            return jsonify({'erro': 'Todos os campos são obrigatórios'}), 400
        
        # Simular dados realistas de iluminação com GRANDE variabilidade
        # para criar diferenciação clara entre postes
        consumo_real = random.uniform(60, 160) if estado == 1 else 0
        # Luminância com variação significativa
        luminancia_media = random.uniform(0.3, 2.5) if estado == 1 else 0
        # Iluminância com variação significativa
        iluminancia_media = random.uniform(5, 30) if estado == 1 else 0
        iluminancia_minima = random.uniform(2, 15) if estado == 1 else 0
        # Uniformidade variável (importante para eficiência)
        uniformidade = random.uniform(0.20, 0.65)
        # Fator de potência variável
        fator_potencia = random.uniform(0.82, 0.99)
        # Temperatura de cor variável
        temperatura_cor = random.choice([2700, 3000, 4000, 5000, 6500])
        # Índice de reprodução de cor variável
        indice_reproducao_cor = random.randint(55, 95)
        # Taxa de ocupação da via variável
        taxa_ocupacao_via = random.randint(20, 100)
        
        eficiencia = calcular_eficiencia_poste(
            estado, automatico,
            potencia_nominal=150,
            consumo_real=consumo_real,
            luminancia_media=luminancia_media,
            iluminancia_minima=iluminancia_minima,
            iluminancia_media=iluminancia_media,
            uniformidade=uniformidade,
            fator_potencia=fator_potencia,
            temperatura_cor=temperatura_cor,
            indice_reproducao_cor=indice_reproducao_cor,
            taxa_ocupacao_via=taxa_ocupacao_via,
            modo_dimming=random.choice([0, 1]) if automatico == 1 else 0,
            infrared_detection=random.choice([0, 1]) if automatico == 1 else 0
        )
        
        try:
            db = get_db()
            cursor = db.cursor()
            cursor.execute("""INSERT INTO postes 
                (regiao_id, localizacao, estado, automatico, eficiencia, consumo_real,
                 luminancia_media, iluminancia_media, iluminancia_minima, uniformidade,
                 fator_potencia, modo_dimming, infrared_detection)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""", 
                (regiao_id, localizacao, estado, automatico, eficiencia, consumo_real,
                 luminancia_media, iluminancia_media, iluminancia_minima, uniformidade,
                 fator_potencia, random.choice([0, 1]) if automatico == 1 else 0, random.choice([0, 1]) if automatico == 1 else 0))
            db.commit()
            return jsonify({'mensagem': 'Poste criado com sucesso', 'eficiencia': eficiencia}), 201
        except pymysql.Error as e:
            return jsonify({'erro': str(e)}), 500
        finally:
            db.close()

@app.route('/get_poste/<int:id_poste>', methods=['GET'])
@login_required
def busca_poste(id_poste):
    if request.method == 'GET':
        db = None
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
            if db:
                db.close()

@app.route('/postes', methods=['GET'])
@login_required
def get_postes():
    regiao_id = request.args.get('regiao_id', type=int)
    db = None
    try:
        db = get_db()
        cursor = db.cursor()
        usuario = session.get('usuario')
        
        # Verificar se regiao pertence ao usuário
        cursor.execute("SELECT id FROM usuarios WHERE usuario = %s", (usuario,))
        user_result = cursor.fetchone()
        
        if not user_result:
            return jsonify({'erro': 'Usuário não encontrado'}), 404
        
        usuario_id = user_result['id']
        
        if regiao_id:
            # Validar que a regiao pertence ao usuário
            cursor.execute("SELECT id FROM regioes WHERE id = %s AND usuario_id = %s", (regiao_id, usuario_id))
            if not cursor.fetchone():
                return jsonify({'erro': 'Acesso negado'}), 403
            cursor.execute("SELECT * FROM postes WHERE regiao_id = %s ORDER BY eficiencia DESC", (regiao_id,))
        else:
            cursor.execute("""SELECT p.* FROM postes p 
                           INNER JOIN regioes r ON p.regiao_id = r.id 
                           WHERE r.usuario_id = %s 
                           ORDER BY p.eficiencia DESC""", (usuario_id,))
        dado = cursor.fetchall()
        return jsonify(dado), 200
    except pymysql.Error as e:
        return jsonify({'erro': str(e)}), 500
    finally:
        if db:
            db.close()

@app.route('/postes/top5/<int:regiao_id>/<tipo>', methods=['GET'])
@login_required
def get_top5_postes(regiao_id, tipo):
    db = None
    try:
        db = get_db()
        cursor = db.cursor()
        if tipo == 'eficientes':
            cursor.execute("SELECT * FROM postes WHERE regiao_id = %s ORDER BY eficiencia DESC LIMIT 5", (regiao_id,))
        elif tipo == 'ineficientes':
            cursor.execute("SELECT * FROM postes WHERE regiao_id = %s ORDER BY eficiencia ASC LIMIT 5", (regiao_id,))
        else:
            return jsonify({'erro': 'Tipo inválido. Use eficientes ou ineficientes'}), 400
        dados = cursor.fetchall()
        return jsonify(dados), 200
    except pymysql.Error as e:
        return jsonify({'erro': str(e)}), 500
    finally:
        if db:
            db.close()

@app.route('/update_poste/<int:id_poste>', methods=['PUT'])
@login_required
def update_poste(id_poste):
    if request.method == 'PUT':
        localizacao = request.json.get('localizacao')
        estado = request.json.get('estado')
        automatico = request.json.get('automatico')
        if localizacao is None or estado is None or automatico is None:
            return jsonify({'erro': 'Campos obrigatórios faltando'}), 400
        try:
            # Simular novos dados de iluminação com GRANDE variabilidade
            consumo_real = random.uniform(60, 160) if estado == 1 else 0
            # Luminância com variação significativa
            luminancia_media = random.uniform(0.3, 2.5) if estado == 1 else 0
            # Iluminância com variação significativa
            iluminancia_media = random.uniform(5, 30) if estado == 1 else 0
            iluminancia_minima = random.uniform(2, 15) if estado == 1 else 0
            # Uniformidade variável (importante para eficiência)
            uniformidade = random.uniform(0.20, 0.65)
            # Fator de potência variável
            fator_potencia = random.uniform(0.82, 0.99)
            # Temperatura de cor variável
            temperatura_cor = random.choice([2700, 3000, 4000, 5000, 6500])
            # Índice de reprodução de cor variável
            indice_reproducao_cor = random.randint(55, 95)
            # Taxa de ocupação da via variável
            taxa_ocupacao_via = random.randint(20, 100)
            
            eficiencia = calcular_eficiencia_poste(
                estado, automatico,
                potencia_nominal=150,
                consumo_real=consumo_real,
                luminancia_media=luminancia_media,
                iluminancia_minima=iluminancia_minima,
                iluminancia_media=iluminancia_media,
                uniformidade=uniformidade,
                fator_potencia=fator_potencia,
                temperatura_cor=temperatura_cor,
                indice_reproducao_cor=indice_reproducao_cor,
                taxa_ocupacao_via=taxa_ocupacao_via,
                modo_dimming=random.choice([0, 1]) if automatico == 1 else 0,
                infrared_detection=random.choice([0, 1]) if automatico == 1 else 0
            )
            
            db = get_db()
            cursor = db.cursor()
            query = """UPDATE postes SET localizacao = %s, estado = %s, automatico = %s, eficiencia = %s,
                       consumo_real = %s, luminancia_media = %s, iluminancia_media = %s,
                       iluminancia_minima = %s, uniformidade = %s, fator_potencia = %s,
                       modo_dimming = %s, infrared_detection = %s WHERE id = %s"""
            params = [localizacao, estado, automatico, eficiencia, consumo_real, luminancia_media,
                     iluminancia_media, iluminancia_minima, uniformidade, fator_potencia,
                     random.choice([0, 1]) if automatico == 1 else 0, random.choice([0, 1]) if automatico == 1 else 0, id_poste]
            cursor.execute(query, params)
            db.commit()
            return jsonify({'mensagem': 'Poste atualizado com sucesso', 'eficiencia': eficiencia}), 200
        except pymysql.Error as e:
            return jsonify({'erro': str(e)}), 500
        finally:
            db.close()

@app.route('/postes/<int:id_poste>', methods=['DELETE'])
@login_required
def deletar_poste(id_poste):
    if request.method == 'DELETE':
        try:
            db = get_db()
            cursor = db.cursor()
            cursor.execute("DELETE FROM postes WHERE id = %s", (id_poste,))
            db.commit()
            return jsonify({'mensagem': 'Poste deletado com sucesso'}), 200
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
SLOW_THRESOLD = 3

@app.route('/')
def index():
    response = send_from_directory('frontend', 'login.html')
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/dashboard')
@login_required
def dashboard():
    response = send_from_directory('frontend', 'index.html')
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/static/<path:filename>')
def static_files(filename):
    response = send_from_directory('static', filename)
    
    # Adicionar timestamp do servidor ao ETag para garantir revalidação a cada restart
    response.headers['ETag'] = f'"{SERVER_START_TIME}"'
    
    # Desabilitar cache para arquivos críticos
    if filename.endswith('.js') or filename.endswith('.css'):
        response.headers['Cache-Control'] = 'no-cache, max-age=0, must-revalidate, no-store'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '-1'
        response.headers['Last-Modified'] = 'Mon, 01 Jan 2000 00:00:00 GMT'
    
    return response

@app.route('/favicon.ico')
def favicon():
    return '', 204

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
    app.run(host="0.0.0.0", port=5000, debug=True)
