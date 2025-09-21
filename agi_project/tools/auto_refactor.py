#!/usr/bin/env python3
"""Auto-Refactor Corrigé pour Detection Violations"""

import argparse
from pathlib import Path
from typing import List
from dataclasses import dataclass

@dataclass
class FileViolation:
    path: Path
    lines: int
    excess: int

class FixedAutoRefactor:
    def __init__(self, max_lines: int = 200, project_root: str = "."):
        self.max_lines = max_lines
        self.project_root = Path(project_root)
        
    def scan_violations(self) -> List[FileViolation]:
        print("🔍 Scan des violations (version corrigée)...")
        violations = []
        
        for py_file in self.project_root.rglob("*.py"):
            # Filtrer seulement les vrais dossiers à ignorer
            if self._should_skip_file(py_file):
                continue
                
            lines = self._count_lines_simple(py_file)
            if lines > self.max_lines:
                excess = lines - self.max_lines
                violations.append(FileViolation(py_file, lines, excess))
                print(f"  📄 {lines} lignes (+{excess}): {py_file}")
        
        return sorted(violations, key=lambda x: x.excess, reverse=True)
    
    def _should_skip_file(self, file_path: Path) -> bool:
        """Version simplifiée - moins de filtres"""
        path_str = str(file_path)
        skip_patterns = [
            "__pycache__", ".git", ".venv", "venv",
            "/backup_", "/.git/"
        ]
        return any(pattern in path_str for pattern in skip_patterns)
    
    def _count_lines_simple(self, file_path: Path) -> int:
        """Comptage simple et fiable"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return len([line for line in f if line.strip()])
        except:
            return 0

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--scan", action="store_true", help="Scanner violations")
    parser.add_argument("--max-lines", type=int, default=200)
    parser.add_argument("--project-root", default=".")
    
    args = parser.parse_args()
    
    refactor = FixedAutoRefactor(args.max_lines, args.project_root)
    violations = refactor.scan_violations()
    
    if violations:
        print(f"\n🚨 {len(violations)} VIOLATIONS DÉTECTÉES:")
        for i, v in enumerate(violations[:10], 1):
            print(f"{i}. {v.lines} lignes (+{v.excess}): {v.path}")
    else:
        print("\n✅ Aucune violation détectée")

if __name__ == "__main__":
    main()
