"""
Connexion avec Minetest via API Mod (Directive 42).
Encapsule communication spécifique Minetest.
"""

import socket
import json
import logging

logger = logging.getLogger(__name__)


class ConnexionMinetest:
    """TODO: Add docstring."""
        """TODO: Add docstring."""
    def __init__(self, config_minetest):
        self.host = config_minetest.get("host", "localhost")
        self.port = config_minetest.get("port", 30000)
        self.socket = None
        self.connecte = False

    def etablir_connexion(self):
        """Établit connexion TCP avec Minetest."""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            self.connecte = True
            logger.info(f"Connexion Minetest établie: {self.host}:{self.port}")
            return True
        except Exception as e:
            logger.error(f"Erreur connexion Minetest: {e}")
            return False

    def lire_etat_monde(self):
        """Lit état monde depuis Minetest."""
        if not self.connecte:
            return None

        try:
            self.socket.send(b"GET_STATE\n")
            reponse = self.socket.recv(4096)
            return json.loads(reponse.decode())
        except Exception as e:
            logger.warning(f"Erreur lecture état: {e}")
            return None

    def envoyer_commande(self, commande_json):
        """Envoie commande vers Minetest."""
        if not self.connecte:
            return False

        try:
            data = json.dumps(commande_json).encode() + b"\n"
            self.socket.send(data)
            return True
        except Exception as e:
            logger.warning(f"Erreur envoi commande: {e}")
            return False

    def fermer(self):
        """Ferme connexion proprement."""
        if self.socket:
            try:
                self.socket.close()
            except Exception as e:
                logger.warning(f"Erreur fermeture socket: {e}")
        self.connecte = False
        logger.info("Connexion Minetest fermée")