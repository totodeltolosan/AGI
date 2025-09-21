# -*- coding: utf-8 -*-
"""
Paramètres de configuration pour le capteur sonore. (v1.1)
"""

# Paramètres audio pour la capture et l'analyse
SAMPLE_RATE = 44100  # Taux d'échantillonnage en Hz (standard pour l'audio de qualité CD)
CHUNK_SIZE = 1024    # Nombre d'échantillons audio par bloc de données
CHANNELS = 1         # Mono

# NOUVEAU : Facteur d'amplification numérique par défaut
AMPLIFICATION_LOGICIELLE = 1.0 # 1.0 = pas de changement. Une valeur de 2.0 doublera le volume capturé.
