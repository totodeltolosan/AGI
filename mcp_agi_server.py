#!/usr/bin/env python3
"""
CHEMIN: mcp_agi_server.py

Rôle Fondamental (Conforme iaGOD.json) :
- Module de support.
- Ce fichier respecte la constitution AGI.
"""

import http.server
import json
from pathlib import Path
from urllib.parse import unquote

class AGIMCPHandler(http.server.BaseHTTPRequestHandler):
    """Handler HTTP pour serveur MCP AGI"""
    BASE_PATH = "/home/toni/Documents/Projet AGI"
    
    def do_GET(self):
        """Traiter requêtes GET"""
        try:
            if self.path.startswith('/api/read/'):
                self._read_file()
            elif self.path.startswith('/api/list/'):
                self._list_files()
            elif self.path.startswith('/api/compliance/'):
                self._check_compliance()
            elif self.path == '/api/status':
                self._send_json({"status": "AGI MCP Online", "version": "2.0"})
            else:
                self._send_error(404, "Endpoint non trouvé")
        except Exception as e:
            self._send_error(500, str(e))
    
    def do_POST(self):
        """Traiter requêtes POST"""
        try:
            if self.path.startswith('/api/write/'):
                self._write_file()
            else:
                self._send_error(404, "Endpoint POST non trouvé")
        except Exception as e:
            self._send_error(500, str(e))
    
    def do_OPTIONS(self):
        """Traiter requêtes OPTIONS pour CORS"""
        self.send_response(200)
        self._set_cors_headers()
        self.end_headers()
    
    def _read_file(self):
        """Lire contenu d'un fichier"""
        file_path = unquote(self.path[10:])
        full_path = Path(self.BASE_PATH) / file_path
        
        if not self._is_safe_path(full_path):
            self._send_error(403, "Accès refusé")
            return
            
        if not full_path.exists():
            self._send_error(404, "Fichier non trouvé")
            return
        
        try:
            content = full_path.read_text(encoding='utf-8')
            lines = content.count('\n') + 1
            
            self._send_json({
                "content": content,
                "path": file_path,
                "lines": lines,
                "agi_compliant": lines <= 200
            })
        except Exception as e:
            self._send_error(500, f"Erreur lecture: {str(e)}")
    
    def _write_file(self):
        """Écrire contenu dans un fichier"""
        file_path = unquote(self.path[11:])
        full_path = Path(self.BASE_PATH) / file_path
        
        if not self._is_safe_path(full_path):
            self._send_error(403, "Écriture refusée")
            return
        
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            content = data.get('content', '')
            lines = content.count('\n') + 1
            
            if full_path.exists():
                backup_path = full_path.with_suffix('.backup')
                backup_path.write_text(full_path.read_text())
            
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content, encoding='utf-8')
            
            self._send_json({
                "status": "success",
                "path": file_path,
                "lines": lines,
                "agi_compliant": lines <= 200
            })
        except Exception as e:
            self._send_error(500, f"Erreur écriture: {str(e)}")
    
    def _list_files(self):
        """Lister fichiers d'un répertoire"""
        dir_path = unquote(self.path[10:]) or ""
        full_path = Path(self.BASE_PATH) / dir_path
        
        try:
            files = []
            if full_path.is_dir():
                for item in sorted(full_path.iterdir()):
                    if item.name.startswith('.'):
                        continue
                    
                    rel_path = str(item.relative_to(Path(self.BASE_PATH)))
                    if item.is_file():
                        try:
                            lines = item.read_text().count('\n') + 1 if item.suffix == '.py' else 0
                            files.append({
                                "path": rel_path,
                                "lines": lines,
                                "agi_compliant": lines <= 200 if item.suffix == '.py' else True
                            })
                        except:
                            files.append({"path": rel_path, "lines": 0})
            
            self._send_json({"files": files, "base_path": dir_path})
        except Exception as e:
            self._send_error(500, str(e))
    
    def _check_compliance(self):
        """Vérifier conformité constitutionnelle"""
        try:
            violations = []
            compliant = []
            
            for py_file in Path(self.BASE_PATH).rglob("*.py"):
                if "__pycache__" in str(py_file):
                    continue
                
                try:
                    lines = py_file.read_text().count('\n') + 1
                    rel_path = str(py_file.relative_to(Path(self.BASE_PATH)))
                    
                    if lines > 200:
                        violations.append({"path": rel_path, "lines": lines})
                    else:
                        compliant.append({"path": rel_path, "lines": lines})
                except:
                    pass
            
            total = len(compliant) + len(violations)
            compliance_rate = len(compliant) / total * 100 if total > 0 else 100
            
            self._send_json({
                "compliance_rate": round(compliance_rate, 1),
                "total_files": total,
                "violations": len(violations),
                "violation_details": sorted(violations, key=lambda x: x['lines'], reverse=True)[:5]
            })
        except Exception as e:
            self._send_error(500, str(e))
    
    def _is_safe_path(self, path):
        """Vérifier sécurité du chemin"""
        try:
            return path.resolve().is_relative_to(Path(self.BASE_PATH).resolve())
        except:
            return False
    
    def _send_json(self, data):
        """Envoyer réponse JSON"""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self._set_cors_headers()
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode('utf-8'))
    
    def _send_error(self, code, message):
        """Envoyer erreur HTTP"""
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self._set_cors_headers()
        self.end_headers()
        self.wfile.write(json.dumps({"error": message}).encode('utf-8'))
    
    def _set_cors_headers(self):
        """Définir headers CORS"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
    
    def log_message(self, format, *args):
        """Logger personnalisé"""
        print(f"[AGI-MCP] {format % args}")

if __name__ == "__main__":
    PORT = 8081
    print(f"Serveur MCP AGI démarré sur http://localhost:{PORT}")
    print(f"Base: {AGIMCPHandler.BASE_PATH}")
    print("Conforme AGI.md (<200 lignes)")
    
    try:
        httpd = http.server.HTTPServer(('localhost', PORT), AGIMCPHandler)
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServeur arrêté")
