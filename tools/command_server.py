#!/usr/bin/env python3
"""
COMMAND SERVER - Serveur Flask pour l'exécution des actions du poste de commandement
Serveur local sécurisé pour l'interface web ↔ système
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import logging
import os
from pathlib import Path
import threading
import time

app = Flask(__name__)
CORS(app)  # Permettre les requêtes du navigateur

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration sécurisée
ALLOWED_SCRIPTS = {
    'launch_session': '/home/toni/Bureau/launch_agi_vscode.sh',
    'run_audit': 'python run_agi_audit.py --target . --output violations.json',
    'refresh_dashboard': 'python tools/dashboard_generator.py',
    'git_status': 'git status --porcelain'
}

@app.route('/execute', methods=['POST'])
def execute_command():
    """Exécute une commande sécurisée."""
    try:
        data = request.get_json()
        command_id = data.get('command_id')
        
        if command_id not in ALLOWED_SCRIPTS:
            return jsonify({'error': 'Commande non autorisée'}), 403
        
        command = ALLOWED_SCRIPTS[command_id]
        logger.info(f"Exécution: {command}")
        
        # Exécution asynchrone pour les commandes longues
        if command_id in ['launch_session', 'run_audit']:
            threading.Thread(target=execute_async, args=(command,)).start()
            return jsonify({'status': 'started', 'message': 'Commande lancée en arrière-plan'})
        else:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
            return jsonify({
                'status': 'completed',
                'returncode': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr
            })
    
    except Exception as e:
        logger.error(f"Erreur exécution: {e}")
        return jsonify({'error': str(e)}), 500

def execute_async(command):
    """Exécute une commande en arrière-plan."""
    try:
        subprocess.run(command, shell=True)
        logger.info(f"Commande terminée: {command}")
    except Exception as e:
        logger.error(f"Erreur commande async: {e}")

@app.route('/status')
def status():
    """Status du serveur."""
    return jsonify({'status': 'operational', 'server': 'AGI Command Server v4.0'})

if __name__ == '__main__':
    print("🚀 Serveur de Commandement AGI démarré")
    print("📡 URL: http://localhost:5000")
    print("⚡ Actions: Prêt pour exécution")
    app.run(host='localhost', port=5000, debug=False)
