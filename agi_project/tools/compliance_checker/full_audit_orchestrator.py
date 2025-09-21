#!/usr/bin/env python3
"""
CHEMIN: tools/compliance_checker/full_audit_orchestrator.py
Rôle Fondamental (Conforme iaGOD.json) :
- Orchestrateur principal audit constitutionnel AGI
- Assemblage de toutes les vérifications
- Coordination audits fichiers et dossiers
- Taille: <200 lignes MAX
"""

import json
from pathlib import Path
from typing import List

from .full_audit_models import FileAuditResult, ComplianceStatus
from .full_audit_core import ConstitutionalAuditor
from .full_audit_analysis import ConstitutionalAnalyzer
from .full_audit_validators import ConstitutionalValidator
from .full_audit_verification import ConstitutionalVerifier


class ConstitutionalOrchestrator(ConstitutionalAuditor):
    """Orchestrateur principal pour audit constitutionnel complet"""
    
    def __init__(self, verbose: bool = False):
        """Initialise l'orchestrateur avec tous les composants"""
        super().__init__(verbose)
        
        # Composants spécialisés
        self.analyzer = ConstitutionalAnalyzer(self.constitution_rules)
        self.validator = ConstitutionalValidator(self.constitution_rules)
        self.verifier = ConstitutionalVerifier(self.constitution_rules)
    
    def audit_file(self, file_path: Path) -> FileAuditResult:
        """Audit complet d'un fichier Python avec toutes les vérifications"""
        # Lecture et parsing (méthode héritée)
        content, lines, tree = self._read_and_parse_file(file_path)
        
        # Si erreur de syntaxe, retourner résultat d'erreur
        if tree is None:
            return self._create_syntax_error_result(file_path, "Erreur de parsing AST")
        
        # Vérification des directives avec composants spécialisés
        directive_results = []
        
        # 1. Analyse de base (architecture, modularité, sécurité)
        directive_results.append(self.analyzer._check_line_limit(file_path, len(lines)))
        directive_results.append(self.analyzer._check_modularity(file_path, tree, content))
        directive_results.append(self.analyzer._check_security(file_path, tree, content))
        
        # 2. Validation (traçabilité, contrats)
        directive_results.append(self.validator._check_traceability(file_path, tree, content))
        directive_results.append(self.validator._check_contracts(file_path, tree))
        
        # 3. Vérification (évolution)
        directive_results.append(self.verifier._check_evolution(file_path, tree, content))
        
        # Calcul des métriques globales
        critical_violations = sum(
            1
            for r in directive_results
            if r.status == ComplianceStatus.VIOLEE and r.severity == "CRITICAL"
        )
        warnings = sum(
            1
            for r in directive_results
            if r.status == ComplianceStatus.VIOLEE and r.severity in ["HIGH", "MEDIUM"]
        )
        conforming = sum(
            1 for r in directive_results if r.status == ComplianceStatus.RESPECTEE
        )
        total_applicable = sum(
            1 for r in directive_results if r.status != ComplianceStatus.NON_APPLICABLE
        )
        global_score = (
            (conforming / total_applicable * 100) if total_applicable > 0 else 0
        )
        
        return FileAuditResult(
            file_path=str(file_path),
            line_count=len(lines),
            size_bytes=len(content.encode("utf-8")),
            directives_results=directive_results,
            global_score=global_score,
            critical_violations=critical_violations,
            warnings=warnings,
        )
    
    def audit_directory(self, target_dir: Path) -> List[FileAuditResult]:
        """Audit récursif d'un répertoire"""
        results = []
        
        if not target_dir.exists() or not target_dir.is_dir():
            raise ValueError(f"Répertoire invalide : {target_dir}")
        
        # Parcourir récursivement les fichiers .py
        for py_file in target_dir.rglob("*.py"):
            if self._validate_file_path(py_file):
                try:
                    result = self.audit_file(py_file)
                    results.append(result)
                    if self.verbose:
                        print(f"✅ Audité: {py_file}")
                except Exception as e:
                    if self.verbose:
                        print(f"❌ Erreur {py_file}: {e}")
        
        return results
    
    def generate_report(self, results: List[FileAuditResult], output_format: str = "console") -> str:
        """Génère un rapport dans le format spécifié"""
        if output_format == "json":
            return self._generate_json_report(results)
        else:
            # Console report sera géré dans full_audit_main.py
            return f"Format {output_format} géré par le module principal"
    
    def _generate_json_report(self, results: List[FileAuditResult]) -> str:
        """Génère un rapport JSON détaillé"""
        total_files = len(results)
        compliant_files = sum(1 for r in results if r.is_compliant())
        total_violations = sum(r.critical_violations + r.warnings for r in results)
        
        report_data = {
            "metadata": {
                "total_files": total_files,
                "compliant_files": compliant_files,
                "compliance_rate": f"{(compliant_files/total_files*100):.1f}%" if total_files > 0 else "0%",
                "total_violations": total_violations,
            },
            "files": [
                {
                    "path": r.file_path,
                    "line_count": r.line_count,
                    "global_score": f"{r.global_score:.1f}%",
                    "critical_violations": r.critical_violations,
                    "warnings": r.warnings,
                    "is_compliant": r.is_compliant(),
                    "directives": [
                        {
                            "id": d.id,
                            "description": d.description,
                            "status": d.status.value,
                            "details": d.details,
                            "severity": d.severity,
                        }
                        for d in r.directives_results
                    ],
                }
                for r in results
            ],
        }
        
        return json.dumps(report_data, indent=2, ensure_ascii=False)
