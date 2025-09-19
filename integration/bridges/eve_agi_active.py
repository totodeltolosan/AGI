#!/usr/bin/env python3
"""
EVE-AGI Bridge Actif - Post-Migration
===================================

Pont opérationnel après migration complète
"""

from .eve_agi_bridge import EVEAGIBridge
from pathlib import Path
import logging

def activate_unified_system():
    """Activer système unifié après migration"""
    logger = logging.getLogger(__name__)
    
    agi_root = Path(__file__).parent.parent.parent
    bridge = EVEAGIBridge(agi_root)
    
    if bridge.initialize_unified_system():
        logger.info("🚀 Système AGI-EVE unifié ACTIF")
        return True
    else:
        logger.error("❌ Échec activation système unifié")
        return False

if __name__ == "__main__":
    activate_unified_system()
