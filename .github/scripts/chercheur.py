#!/usr/bin/env python3
"""
Contremaître - Chercheur de patterns
Niveau 3 - Orchestration des recherches dans le code
"""

import json
import argparse
import sys
import os
import re
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description='Chercheur de patterns')
    parser.add_argument('--pattern', required=True)
    parser.add_argument('--extensions', default='py,yml,md')
    parser.add_argument('--repertoire', default='.')
    parser.add_argument('--output', default='recherche_results.json')
    
    args = parser.parse_args()
    
    # Conversion des extensions en liste
    exts = args.extensions.split(',')
    pattern = re.compile(args.pattern, re.IGNORECASE)
    
    results = []
    base_path = Path(args.repertoire)
    
    # Recherche dans les fichiers
    for ext in exts:
        for filepath in base_path.rglob(f'*.{ext}'):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    matches = pattern.findall(content)
                    if matches:
                        results.append({
                            'file': str(filepath),
                            'matches': len(matches),
                            'preview': matches[:3]
                        })
            except Exception as e:
                continue
    
    # Création du rapport
    report = {
        'pattern': args.pattern,
        'extensions': exts,
        'repertoire': args.repertoire,
        'total_files': len(results),
        'results': results[:100]  # Limiter à 100 résultats
    }
    
    # Écriture du résultat
    with open(args.output, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"✅ Recherche terminée : {len(results)} fichiers trouvés")
    return 0

if __name__ == '__main__':
    sys.exit(main())
