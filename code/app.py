from flask import Flask, request, jsonify, render_template, g
import sqlite3
import joblib
import random
from crypto_engine import encrypt_standard, encrypt_hybrid_pqc
from network_sim import simulate_transmission

app = Flask(__name__, template_folder='templates', static_folder='static')
DATABASE = 'research_data.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE, timeout=15.0)
        db.execute('PRAGMA journal_mode=WAL;')
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        db.execute('''CREATE TABLE IF NOT EXISTS uploads
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      username TEXT, filename TEXT, algorithm TEXT,
                      size_kb REAL, latency_ms REAL, packets_lost INTEGER,
                      real_latency_ms REAL, data_type TEXT, 
                      clumsy_lag_ms REAL, clumsy_drop_pct REAL)''')
        db.commit()

init_db() 

try:
    ai_model = joblib.load('research_ai_model.pkl')
except FileNotFoundError:
    print("ERROR: Run train_ai.py first!")
    exit(1)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload_file', methods=['POST'])
def upload_file():
    username = request.form.get('username', 'Guest')
    text_payload = request.form.get('textPayload', '').strip()
    data_type = request.form.get('dataType', 'Manual_Web_Upload')
    clumsy_lag = float(request.form.get('clumsyLag', 0.0))
    clumsy_drop = float(request.form.get('clumsyDrop', 0.0))
    
    if 'file' in request.files and request.files['file'].filename != '':
        uploaded_file = request.files['file']
        file_bytes = uploaded_file.read()
        raw_data = file_bytes.decode('latin1', errors='ignore')
        filename = uploaded_file.filename
    elif text_payload:
        raw_data = text_payload
        filename = "direct_message.txt"
    else:
        return jsonify({"error": "Please provide either a file or a text message."}), 400
    
    # =================================================================
    # THE 65:35 RATIO GATE
    # Exactly 35% of the time, we simulate a network attack.
    # =================================================================
    # Extract the requested algorithm mode
    algo_choice = request.form.get('algoSelect', 'Automatic')
    
    server_load = random.randint(40, 99)

    # =================================================================
    # ROUTING LOGIC: AI vs Manual Override
    # =================================================================
    if algo_choice == 'Automatic':
        is_attack_simulated = random.random() < 0.35 
        if is_attack_simulated:
            features = [[40.0, 7, 10.0, 250.0]] 
            threat_level = random.randint(7, 10)
            reason = "AI detected anomalous flows (PortScan Signature). Routed to PQC."
        else:
            features = [[10.0, 2, 40.0, 500.0]]
            threat_level = random.randint(1, 6)
            reason = "Network flows benign. Routed to AES."
            
        prediction = ai_model.predict(features)[0]
        
        if prediction == 1:
            algo_name = "Hybrid PQC"
            ciphertext = encrypt_hybrid_pqc(raw_data)
        else:
            algo_name = "Standard AES"
            ciphertext = encrypt_standard(raw_data)

    elif algo_choice == 'AES':
        threat_level = random.randint(1, 6)
        reason = "User manually forced Standard AES encryption."
        algo_name = "Standard AES"
        ciphertext = encrypt_standard(raw_data)

    elif algo_choice == 'PQC':
        threat_level = random.randint(7, 10)
        reason = "User manually forced Quantum PQC encryption."
        algo_name = "Hybrid PQC"
        ciphertext = encrypt_hybrid_pqc(raw_data)
        
    else:
        return jsonify({"error": "Invalid algorithm choice."}), 400

    # Calculate Network Impact
    net_stats = simulate_transmission(ciphertext, algo_name)
    # MEMORY CRASH FIX: We truncate the massive string so Flask doesn't crash on return
    display_cipher = ciphertext[:3000] + "\n\n... [MASSIVE PAYLOAD TRUNCATED FOR SERVER MEMORY EFFICIENCY] ..." if len(ciphertext) > 3000 else ciphertext

    db = get_db()
    cursor = db.execute("INSERT INTO uploads (username, filename, algorithm, size_kb, latency_ms, packets_lost, real_latency_ms, data_type, clumsy_lag_ms, clumsy_drop_pct) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
               (username, filename, algo_name, net_stats['file_size_kb'], net_stats['latency_ms'], net_stats['packets_lost'], 0.0, data_type, clumsy_lag, clumsy_drop))
    upload_id = cursor.lastrowid
    db.commit()

    return jsonify({
        "status": "success",
        "algorithm": algo_name,
        "threat_level": threat_level,
        "server_load": server_load,
        "reason": reason,
        "ciphertext": display_cipher, 
        "network_stats": net_stats,
        "upload_id": upload_id 
    })

@app.route('/log_real_time', methods=['POST'])
def log_real_time():
    req_data = request.json
    db = get_db()
    db.execute("UPDATE uploads SET real_latency_ms = ? WHERE id = ?", 
               (req_data['real_time_ms'], req_data['upload_id']))
    db.commit()
    return jsonify({"status": "logged"})

@app.route('/api/stats', methods=['GET'])
def get_stats():
    db = get_db()
    cursor = db.execute("SELECT algorithm, AVG(latency_ms), SUM(packets_lost), AVG(real_latency_ms), COUNT(id) FROM uploads WHERE real_latency_ms > 0 GROUP BY algorithm")
    data = cursor.fetchall()
    return jsonify(data)

if __name__ == '__main__':
    print("🚀 Server open to local network...")
    app.run(host='0.0.0.0', port=5000, debug=False)