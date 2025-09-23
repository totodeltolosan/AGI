#!/usr/bin/env python3
"""
🎼 ORCHESTRATEUR AGI - Niveau 1
Maître de la Constitution qui coordonne les 8 Généraux de Division
Version: 1.0.0
"""

import json
import sys
import os
import hashlib
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import argparse
from dataclasses import dataclass, asdict
from enum import Enum

try:
    import jsonschema
    from rich.console import Console
    from rich.table import Table
    from rich.progress import Progress
    from rich.panel import Panel
    import typer
except ImportError as e:
    print(f"❌ Dépendance manquante: {e}")
    print("💡 Installer avec: pip install jsonschema rich typer")
    sys.exit(1)

console = Console()

class AuditStatus(Enum):
    SUCCESS = "SUCCESS"
    WARNING = "WARNING" 
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"
    TIMEOUT = "TIMEOUT"

class Priority(Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

@dataclass
class ConstitutionValidation:
    valid: bool
    hash: str
    laws_count: int
    version: str
    critical_laws: List[str]
    errors: List[str]
    
@dataclass
class GeneralResult:
    name: str
    status: AuditStatus
    violations: int
    duration: float
    priority: Priority
    errors: List[str]

@dataclass
class GlobalSynthesis:
    audit_status: AuditStatus
    total_violations: int
    critical_violations: int
    generals_results: List[GeneralResult]
    recommendation: str
    execution_time: float

class OrchestrateurAGI:
    """Orchestrateur principal - Maître de la Constitution"""
    
    def __init__(self, audit_id: str):
        self.audit_id = audit_id
        self.start_time = time.time()
        self.constitution_schema = self._load_constitution_schema()
    
    def _load_constitution_schema(self) -> Dict:
        """Charge le schéma JSON strict pour iaGOD.json"""
        return {
            "type": "object",
            "required": ["meta", "laws"],
            "properties": {
                "meta": {
                    "type": "object",
                    "required": ["version", "name", "description"],
                    "properties": {
                        "version": {"type": "string", "pattern": r"^\d+\.\d+\.\d+$"},
                        "name": {"type": "string"},
                        "description": {"type": "string"}
                    }
                },
                "laws": {
                    "type": "object",
                    "required": ["lignes", "securite", "documentation"],
                    "properties": {
                        "lignes": {
                            "type": "object",
                            "required": ["limite", "exclusions"],
                            "properties": {
                                "limite": {"type": "integer", "minimum": 1},
                                "exclusions": {"type": "array", "items": {"type": "string"}}
                            }
                        },
                        "securite": {
                            "type": "object", 
                            "required": ["regles"],
                            "properties": {
                                "regles": {"type": "array", "minItems": 1}
                            }
                        },
                        "documentation": {
                            "type": "object",
                            "required": ["seuils"],
                            "properties": {
                                "seuils": {"type": "object"}
                            }
                        }
                    }
                }
            }
        }
    
    def validate_constitution(self, constitution_file: str, force_audit: bool = False, 
                            constitution_override: bool = False) -> ConstitutionValidation:
        """Validation rigoureuse de la constitution iaGOD.json"""
        
        console.print(f"🏛️ [bold]Validation Constitution: {constitution_file}[/bold]")
        
        if not Path(constitution_file).exists():
            return ConstitutionValidation(False, "", 0, "", [], 
                                        [f"Constitution {constitution_file} introuvable"])
        
        try:
            with open(constitution_file, 'r', encoding='utf-8') as f:
                constitution = json.load(f)
        except json.JSONDecodeError as e:
            return ConstitutionValidation(False, "", 0, "", [], 
                                        [f"Constitution JSON invalide: {e}"])
        
        # Validation schéma strict
        errors = []
        try:
            jsonschema.validate(constitution, self.constitution_schema)
            console.print("✅ [green]Schéma JSON validé[/green]")
        except jsonschema.ValidationError as e:
            error_msg = f"Schéma invalide: {e.message}"
            errors.append(error_msg)
            
            if not constitution_override:
                console.print(f"❌ [red]{error_msg}[/red]")
                return ConstitutionValidation(False, "", 0, "", [], errors)
            else:
                console.print(f"⚠️ [yellow]OVERRIDE: {error_msg}[/yellow]")
        
        # Calcul hash de la constitution
        constitution_str = json.dumps(constitution, sort_keys=True)
        const_hash = hashlib.sha256(constitution_str.encode()).hexdigest()[:16]
        
        # Extraction métadonnées
        version = constitution.get("meta", {}).get("version", "unknown")
        laws_count = len(constitution.get("laws", {}))
        critical_laws = []
        
        # Identification lois critiques
        if "lignes" in constitution.get("laws", {}):
            critical_laws.append("lignes")
        if "securite" in constitution.get("laws", {}):
            critical_laws.append("securite")
            
        # Sauvegarde artefacts
        self._save_constitution_artifacts(constitution, const_hash, version)
        
        is_valid = len(errors) == 0 or constitution_override
        
        console.print(f"🔐 [blue]Hash Constitution: {const_hash}[/blue]")
        console.print(f"📊 [blue]Lois détectées: {laws_count}[/blue]")
        
        return ConstitutionValidation(is_valid, const_hash, laws_count, version, 
                                    critical_laws, errors)
    
    def _save_constitution_artifacts(self, constitution: Dict, hash_val: str, version: str):
        """Sauvegarde les artefacts de constitution validée"""
        
        # Constitution parsée
        with open("constitution-parsed.json", 'w') as f:
            json.dump(constitution, f, indent=2)
        
        # Lois extraites
        laws = constitution.get("laws", {})
        with open("laws-extracted.json", 'w') as f:
            json.dump(laws, f, indent=2)
        
        # Métadonnées
        metadata = {
            "hash": hash_val,
            "version": version,
            "audit_id": self.audit_id,
            "validation_timestamp": datetime.now().isoformat(),
            "laws_count": len(laws)
        }
        with open("constitution-metadata.json", 'w') as f:
            json.dump(metadata, f, indent=2)
        
        # Hash dans fichier séparé
        with open("constitution-hash.txt", 'w') as f:
            f.write(hash_val)
    
    def prepare_mission(self, general: str, law_key: str, constitution_file: str,
                       urgency: str, priority: str, timeout: int, script: str) -> Dict:
        """Prépare l'ordre de mission pour un général"""
        
        console.print(f"🎯 [bold]Préparation mission: {general.upper()}[/bold]")
        
        # Chargement constitution validée
        with open(constitution_file, 'r') as f:
            constitution = json.load(f)
        
        laws = constitution.get("laws", {})
        law_config = laws.get(law_key, {})
        
        if not law_config:
            console.print(f"⚠️ [yellow]Aucune loi trouvée pour {law_key}[/yellow]")
        
        mission_orders = {
            "general_name": general,
            "law_key": law_key,
            "law_config": law_config,
            "urgency": urgency,
            "priority": priority,
            "timeout": timeout,
            "script": script,
            "audit_id": self.audit_id,
            "constitution_version": constitution.get("meta", {}).get("version", "unknown")
        }
        
        # Sauvegarde ordre de mission
        with open(f"mission-{general}.json", 'w') as f:
            json.dump(mission_orders, f, indent=2)
        
        # Output GitHub Actions
        print(f"::set-output name=mission_orders::{json.dumps(mission_orders)}")
        
        return mission_orders
    
    def synthesize_audit(self, artifacts_dir: str, constitution_hash: str, 
                        urgency: str, generals_count: int, timeout_exceeded: bool) -> GlobalSynthesis:
        """Synthèse globale rigoureuse des résultats des 8 généraux"""
        
        console.print("🎯 [bold]SYNTHÈSE GLOBALE AUDIT AGI[/bold]")
        
        generals_results = []
        total_violations = 0
        critical_violations = 0
        
        # Collecte résultats de chaque général
        general_names = ["metreur", "gardien", "archiviste", "greffier", 
                        "archiviste_chef", "cartographe", "chercheur", "auditeur"]
        
        for general in general_names:
            result_file = Path(artifacts_dir) / f"rapport-{general}.json"
            
            if result_file.exists():
                with open(result_file, 'r') as f:
                    result_data = json.load(f)
                
                status = AuditStatus(result_data.get("status", "FAILED"))
                violations = int(result_data.get("violations", 0))
                duration = float(result_data.get("duration", 0))
                priority = Priority(result_data.get("priority", "MEDIUM"))
                errors = result_data.get("errors", [])
                
                total_violations += violations
                if priority in [Priority.CRITICAL, Priority.HIGH]:
                    critical_violations += violations
                    
            else:
                # Général non exécuté ou échec
                status = AuditStatus.FAILED
                violations = 999  # Pénalité forte
                duration = 0
                priority = Priority.CRITICAL
                errors = [f"Rapport {general} manquant"]
                
                total_violations += violations
                critical_violations += violations
            
            generals_results.append(GeneralResult(
                name=general, status=status, violations=violations,
                duration=duration, priority=priority, errors=errors
            ))
        
        # Détermination statut global
        failed_generals = [g for g in generals_results if g.status == AuditStatus.FAILED]
        warning_generals = [g for g in generals_results if g.status == AuditStatus.WARNING]
        
        if len(failed_generals) > 0 or critical_violations > 10:
            audit_status = AuditStatus.FAILED
            recommendation = "BLOCAGE: Violations critiques détectées"
        elif len(warning_generals) > 0 or total_violations > 5:
            audit_status = AuditStatus.WARNING
            recommendation = "ATTENTION: Améliorations requises"
        else:
            audit_status = AuditStatus.SUCCESS
            recommendation = "CONFORMITÉ: Projet validé AGI"
        
        execution_time = time.time() - self.start_time
        
        synthesis = GlobalSynthesis(
            audit_status=audit_status,
            total_violations=total_violations,
            critical_violations=critical_violations,
            generals_results=generals_results,
            recommendation=recommendation,
            execution_time=execution_time
        )
        
        # Sauvegarde synthèse
        self._save_synthesis(synthesis, constitution_hash)
        
        # Outputs GitHub Actions
        print(f"::set-output name=audit_status::{audit_status.value}")
        print(f"::set-output name=total_violations::{total_violations}")
        print(f"::set-output name=critical_violations::{critical_violations}")
        print(f"::set-output name=recommendation::{recommendation}")
        
        return synthesis
    
    def _save_synthesis(self, synthesis: GlobalSynthesis, constitution_hash: str):
        """Sauvegarde la synthèse globale"""
        
        # Rapport JSON complet
        rapport_data = {
            "audit_id": self.audit_id,
            "timestamp": datetime.now().isoformat(),
            "constitution_hash": constitution_hash,
            "synthesis": asdict(synthesis),
            "orchestrator_version": "1.0.0"
        }
        
        with open("rapport-global.json", 'w') as f:
            json.dump(rapport_data, f, indent=2)
        
        # Rapport Markdown
        self._generate_markdown_report(synthesis)
        
        console.print(f"✅ [green]Synthèse sauvegardée: {synthesis.audit_status.value}[/green]")
    
    def _generate_markdown_report(self, synthesis: GlobalSynthesis):
        """Génère le rapport Markdown"""
        
        md_content = f"""# 🎯 Rapport Global Audit AGI
        
**Audit ID:** `{self.audit_id}`  
**Timestamp:** `{datetime.now().isoformat()}`  
**Durée:** `{synthesis.execution_time:.2f}s`

## 📊 Synthèse Globale

- **Statut:** `{synthesis.audit_status.value}`
- **Violations Totales:** `{synthesis.total_violations}`
- **Violations Critiques:** `{synthesis.critical_violations}`
- **Recommandation:** `{synthesis.recommendation}`

## 🎖️ Résultats des 8 Généraux

| Général | Statut | Violations | Durée | Priorité |
|---------|--------|------------|-------|----------|
"""
        
        for general in synthesis.generals_results:
            md_content += f"| {general.name.title()} | {general.status.value} | {general.violations} | {general.duration:.1f}s | {general.priority.value} |\n"
        
        md_content += f"""
## 🏁 Conclusion

{synthesis.recommendation}

---
*Généré par Orchestrateur AGI v1.0.0*
"""
        
        with open("rapport-global.md", 'w') as f:
            f.write(md_content)

def main():
    """Point d'entrée CLI"""
    app = typer.Typer(help="🎼 Orchestrateur AGI - Maître de la Constitution")
    
    @app.command()
    def validate_constitution(
        file: str = typer.Option(..., help="Fichier constitution"),
        audit_id: str = typer.Option(..., help="ID unique audit"),
        force_audit: bool = typer.Option(False, help="Forcer audit"),
        constitution_override: bool = typer.Option(False, help="Override constitution"),
        urgency: str = typer.Option("medium", help="Niveau urgence"),
        github_context: str = typer.Option("", help="Contexte GitHub"),
        verbose: bool = typer.Option(False, help="Mode verbeux")
    ):
        """Valide la constitution iaGOD.json"""
        orchestrator = OrchestrateurAGI(audit_id)
        
        result = orchestrator.validate_constitution(
            file, force_audit, constitution_override
        )
        
        # Outputs GitHub Actions
        print(f"::set-output name=constitution_valid::{str(result.valid).lower()}")
        print(f"::set-output name=constitution_hash::{result.hash}")
        print(f"::set-output name=laws_count::{result.laws_count}")
        print(f"::set-output name=should_proceed::{str(result.valid).lower()}")
        print(f"::set-output name=version::{result.version}")
        print(f"::set-output name=critical_laws::{','.join(result.critical_laws)}")
        
        if not result.valid and not constitution_override:
            console.print("❌ [red]Constitution invalide[/red]")
            for error in result.errors:
                console.print(f"  • {error}")
            sys.exit(1)
    
    @app.command()
    def prepare_mission(
        general: str = typer.Option(..., help="Nom du général"),
        law_key: str = typer.Option(..., help="Clé de loi"),
        constitution_file: str = typer.Option(..., help="Fichier constitution"),
        urgency: str = typer.Option("medium", help="Urgence"),
        priority: str = typer.Option("MEDIUM", help="Priorité"),
        audit_id: str = typer.Option(..., help="ID audit"),
        timeout: int = typer.Option(30, help="Timeout"),
        script: str = typer.Option(..., help="Script handler")
    ):
        """Prépare l'ordre de mission pour un général"""
        orchestrator = OrchestrateurAGI(audit_id)
        orchestrator.prepare_mission(general, law_key, constitution_file, 
                                   urgency, priority, timeout, script)
    
    @app.command()
    def synthesize_audit(
        artifacts_dir: str = typer.Option(..., help="Répertoire artefacts"),
        audit_id: str = typer.Option(..., help="ID audit"),
        constitution_hash: str = typer.Option(..., help="Hash constitution"),
        urgency: str = typer.Option("medium", help="Urgence"),
        generals_count: int = typer.Option(8, help="Nombre généraux"),
        timeout_exceeded: bool = typer.Option(False, help="Timeout dépassé"),
        verbose: bool = typer.Option(False, help="Mode verbeux")
    ):
        """Synthèse globale des résultats"""
        orchestrator = OrchestrateurAGI(audit_id)
        orchestrator.synthesize_audit(artifacts_dir, constitution_hash, 
                                    urgency, generals_count, timeout_exceeded)
    
    app()

if __name__ == "__main__":
    main()
