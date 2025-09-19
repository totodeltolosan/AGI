import os
import sys
import json
import subprocess
import shutil
import platform
import psutil
import hashlib
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
import logging

from crewai import LLM, Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.tools import BaseTool
from pydantic import BaseModel, Field


# Configuration du logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# ============================================================================
# OUTILS PERSONNALISÉS POUR EVE GENESIS CREW A
# ============================================================================


class FileManagerToolInput(BaseModel):
    """Input schema pour FileManagerTool."""

    action: str = Field(
        ...,
        description="Action à effectuer: create_dir, create_file, copy_file, move_file, delete, read_file, write_file, list_dir",
    )
    path: str = Field(..., description="Chemin du fichier ou dossier")
    content: Optional[str] = Field(
        None, description="Contenu pour les actions write_file"
    )
    destination: Optional[str] = Field(
        None, description="Destination pour copy_file et move_file"
    )


class FileManagerTool(BaseTool):
    name: str = "FileManagerTool"
    description: str = (
        "Outil complet de gestion de fichiers et dossiers pour EVE GENESIS. "
        "Permet de créer, lire, écrire, copier, déplacer et supprimer des fichiers et dossiers. "
        "Supporte également la lecture de métadonnées et la validation de structure de projet."
    )
    args_schema: type[BaseModel] = FileManagerToolInput

    def _run(
        self,
        action: str,
        path: str,
        content: Optional[str] = None,
        destination: Optional[str] = None,
    ) -> str:
        try:
            path_obj = Path(path)

            if action == "create_dir":
                path_obj.mkdir(parents=True, exist_ok=True)
                return f"Dossier créé avec succès: {path}"

            elif action == "create_file":
                path_obj.parent.mkdir(parents=True, exist_ok=True)
                path_obj.touch()
                return f"Fichier créé avec succès: {path}"

            elif action == "write_file":
                if content is None:
                    return "Erreur: contenu requis pour write_file"
                path_obj.parent.mkdir(parents=True, exist_ok=True)
                path_obj.write_text(content, encoding="utf-8")
                return f"Fichier écrit avec succès: {path}"

            elif action == "read_file":
                if not path_obj.exists():
                    return f"Erreur: fichier inexistant: {path}"
                content = path_obj.read_text(encoding="utf-8")
                return f"Contenu de {path}:\n{content}"

            elif action == "copy_file":
                if destination is None:
                    return "Erreur: destination requise pour copy_file"
                dest_obj = Path(destination)
                dest_obj.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(path_obj, dest_obj)
                return f"Fichier copié de {path} vers {destination}"

            elif action == "move_file":
                if destination is None:
                    return "Erreur: destination requise pour move_file"
                dest_obj = Path(destination)
                dest_obj.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(path_obj), str(dest_obj))
                return f"Fichier déplacé de {path} vers {destination}"

            elif action == "delete":
                if path_obj.is_file():
                    path_obj.unlink()
                    return f"Fichier supprimé: {path}"
                elif path_obj.is_dir():
                    shutil.rmtree(path_obj)
                    return f"Dossier supprimé: {path}"
                else:
                    return f"Erreur: chemin inexistant: {path}"

            elif action == "list_dir":
                if not path_obj.is_dir():
                    return f"Erreur: {path} n'est pas un dossier"
                items = []
                for item in path_obj.iterdir():
                    items.append(
                        f"{'[DIR]' if item.is_dir() else '[FILE]'} {item.name}"
                    )
                return f"Contenu de {path}:\n" + "\n".join(items)

            else:
                return f"Action non reconnue: {action}"

        except Exception as e:
            return f"Erreur lors de l'exécution de {action}: {str(e)}"


class SystemMonitorToolInput(BaseModel):
    """Input schema pour SystemMonitorTool."""

    action: str = Field(
        ...,
        description="Action de monitoring: cpu_usage, memory_usage, disk_usage, system_info, process_list, network_info",
    )
    process_name: Optional[str] = Field(
        None, description="Nom du processus pour certaines actions"
    )


class SystemMonitorTool(BaseTool):
    name: str = "SystemMonitorTool"
    description: str = (
        "Outil de monitoring système complet pour EVE GENESIS. "
        "Permet de surveiller l'utilisation CPU, mémoire, disque, les processus, "
        "et de collecter des informations système détaillées."
    )
    args_schema: type[BaseModel] = SystemMonitorToolInput

    def _run(self, action: str, process_name: Optional[str] = None) -> str:
        try:
            if action == "cpu_usage":
                cpu_percent = psutil.cpu_percent(interval=1)
                cpu_count = psutil.cpu_count()
                cpu_freq = psutil.cpu_freq()
                result = f"CPU Usage: {cpu_percent}%\n"
                result += f"CPU Cores: {cpu_count}\n"
                if cpu_freq:
                    result += f"CPU Frequency: {cpu_freq.current:.2f} MHz"
                return result

            elif action == "memory_usage":
                memory = psutil.virtual_memory()
                swap = psutil.swap_memory()
                result = f"Memory Usage: {memory.percent}%\n"
                result += f"Available Memory: {memory.available / (1024**3):.2f} GB\n"
                result += f"Total Memory: {memory.total / (1024**3):.2f} GB\n"
                result += f"Swap Usage: {swap.percent}%"
                return result

            elif action == "disk_usage":
                disk = psutil.disk_usage("/")
                result = f"Disk Usage: {disk.percent}%\n"
                result += f"Free Space: {disk.free / (1024**3):.2f} GB\n"
                result += f"Total Space: {disk.total / (1024**3):.2f} GB"
                return result

            elif action == "system_info":
                uname = platform.uname()
                boot_time = datetime.fromtimestamp(psutil.boot_time())
                result = f"System: {uname.system}\n"
                result += f"Node Name: {uname.node}\n"
                result += f"Release: {uname.release}\n"
                result += f"Version: {uname.version}\n"
                result += f"Machine: {uname.machine}\n"
                result += f"Processor: {uname.processor}\n"
                result += f"Boot Time: {boot_time}"
                return result

            elif action == "process_list":
                processes = []
                for proc in psutil.process_iter(
                    ["pid", "name", "cpu_percent", "memory_percent"]
                ):
                    try:
                        if (
                            process_name is None
                            or process_name.lower() in proc.info["name"].lower()
                        ):
                            processes.append(
                                f"PID: {proc.info['pid']}, "
                                f"Name: {proc.info['name']}, "
                                f"CPU: {proc.info['cpu_percent']:.2f}%, "
                                f"Memory: {proc.info['memory_percent']:.2f}%"
                            )
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
                return "Processes:\n" + "\n".join(
                    processes[:20]
                )  # Limite à 20 processus

            elif action == "network_info":
                net_io = psutil.net_io_counters()
                result = f"Bytes Sent: {net_io.bytes_sent / (1024**2):.2f} MB\n"
                result += f"Bytes Received: {net_io.bytes_recv / (1024**2):.2f} MB\n"
                result += f"Packets Sent: {net_io.packets_sent}\n"
                result += f"Packets Received: {net_io.packets_recv}"
                return result

            else:
                return f"Action non reconnue: {action}"

        except Exception as e:
            return f"Erreur lors du monitoring système: {str(e)}"


class GitManagerToolInput(BaseModel):
    """Input schema pour GitManagerTool."""

    action: str = Field(
        ...,
        description="Action git: init, add, commit, status, log, branch, clone, pull, push",
    )
    path: Optional[str] = Field(None, description="Chemin du repository")
    message: Optional[str] = Field(None, description="Message de commit")
    branch: Optional[str] = Field(None, description="Nom de la branche")
    url: Optional[str] = Field(None, description="URL pour clone")


class GitManagerTool(BaseTool):
    name: str = "GitManagerTool"
    description: str = (
        "Outil de gestion Git pour EVE GENESIS. "
        "Permet d'initialiser des repositories, faire des commits, gérer les branches, "
        "et effectuer toutes les opérations Git essentielles."
    )
    args_schema: type[BaseModel] = GitManagerToolInput

    def _run(
        self,
        action: str,
        path: Optional[str] = None,
        message: Optional[str] = None,
        branch: Optional[str] = None,
        url: Optional[str] = None,
    ) -> str:
        try:
            working_dir = path or os.getcwd()

            if action == "init":
                result = subprocess.run(
                    ["git", "init"], cwd=working_dir, capture_output=True, text=True
                )
                if result.returncode == 0:
                    return f"Repository Git initialisé dans {working_dir}"
                else:
                    return f"Erreur lors de l'initialisation Git: {result.stderr}"

            elif action == "add":
                result = subprocess.run(
                    ["git", "add", "."], cwd=working_dir, capture_output=True, text=True
                )
                if result.returncode == 0:
                    return "Fichiers ajoutés au staging area"
                else:
                    return f"Erreur lors de l'ajout: {result.stderr}"

            elif action == "commit":
                if not message:
                    return "Erreur: message de commit requis"
                result = subprocess.run(
                    ["git", "commit", "-m", message],
                    cwd=working_dir,
                    capture_output=True,
                    text=True,
                )
                if result.returncode == 0:
                    return f"Commit créé: {message}"
                else:
                    return f"Erreur lors du commit: {result.stderr}"

            elif action == "status":
                result = subprocess.run(
                    ["git", "status", "--porcelain"],
                    cwd=working_dir,
                    capture_output=True,
                    text=True,
                )
                if result.returncode == 0:
                    return f"Status Git:\n{result.stdout}"
                else:
                    return f"Erreur lors du status: {result.stderr}"

            elif action == "log":
                result = subprocess.run(
                    ["git", "log", "--oneline", "-10"],
                    cwd=working_dir,
                    capture_output=True,
                    text=True,
                )
                if result.returncode == 0:
                    return f"Derniers commits:\n{result.stdout}"
                else:
                    return f"Erreur lors du log: {result.stderr}"

            else:
                return f"Action Git non reconnue: {action}"

        except Exception as e:
            return f"Erreur lors de l'opération Git: {str(e)}"


class PackageManagerToolInput(BaseModel):
    """Input schema pour PackageManagerTool."""

    action: str = Field(
        ...,
        description="Action: install, uninstall, list, freeze, create_requirements, check_installed",
    )
    package: Optional[str] = Field(None, description="Nom du package")
    requirements_file: Optional[str] = Field(
        None, description="Chemin vers requirements.txt"
    )


class PackageManagerTool(BaseTool):
    name: str = "PackageManagerTool"
    description: str = (
        "Outil de gestion des packages Python pour EVE GENESIS. "
        "Permet d'installer, désinstaller, lister les packages, "
        "créer des fichiers requirements.txt et vérifier les dépendances."
    )
    args_schema: type[BaseModel] = PackageManagerToolInput

    def _run(
        self,
        action: str,
        package: Optional[str] = None,
        requirements_file: Optional[str] = None,
    ) -> str:
        try:
            if action == "install":
                if not package:
                    return "Erreur: nom du package requis"
                result = subprocess.run(
                    [sys.executable, "-m", "pip", "install", package],
                    capture_output=True,
                    text=True,
                )
                if result.returncode == 0:
                    return f"Package {package} installé avec succès"
                else:
                    return f"Erreur lors de l'installation: {result.stderr}"

            elif action == "uninstall":
                if not package:
                    return "Erreur: nom du package requis"
                result = subprocess.run(
                    [sys.executable, "-m", "pip", "uninstall", package, "-y"],
                    capture_output=True,
                    text=True,
                )
                if result.returncode == 0:
                    return f"Package {package} désinstallé avec succès"
                else:
                    return f"Erreur lors de la désinstallation: {result.stderr}"

            elif action == "list":
                result = subprocess.run(
                    [sys.executable, "-m", "pip", "list"],
                    capture_output=True,
                    text=True,
                )
                if result.returncode == 0:
                    return f"Packages installés:\n{result.stdout}"
                else:
                    return f"Erreur lors de la liste: {result.stderr}"

            elif action == "freeze":
                result = subprocess.run(
                    [sys.executable, "-m", "pip", "freeze"],
                    capture_output=True,
                    text=True,
                )
                if result.returncode == 0:
                    return f"Requirements actuels:\n{result.stdout}"
                else:
                    return f"Erreur lors du freeze: {result.stderr}"

            elif action == "create_requirements":
                if not requirements_file:
                    requirements_file = "requirements.txt"
                result = subprocess.run(
                    [sys.executable, "-m", "pip", "freeze"],
                    capture_output=True,
                    text=True,
                )
                if result.returncode == 0:
                    Path(requirements_file).write_text(result.stdout, encoding="utf-8")
                    return f"Fichier requirements.txt créé: {requirements_file}"
                else:
                    return f"Erreur lors de la création: {result.stderr}"

            elif action == "check_installed":
                if not package:
                    return "Erreur: nom du package requis"
                result = subprocess.run(
                    [sys.executable, "-m", "pip", "show", package],
                    capture_output=True,
                    text=True,
                )
                if result.returncode == 0:
                    return f"Package {package} est installé:\n{result.stdout}"
                else:
                    return f"Package {package} n'est pas installé"

            else:
                return f"Action non reconnue: {action}"

        except Exception as e:
            return f"Erreur lors de la gestion des packages: {str(e)}"


class ProjectStructureToolInput(BaseModel):
    """Input schema pour ProjectStructureTool."""

    action: str = Field(
        ...,
        description="Action: create_structure, validate_structure, analyze_structure",
    )
    project_path: str = Field(..., description="Chemin du projet")
    structure_type: Optional[str] = Field(
        "standard", description="Type de structure: standard, django, flask, crewai"
    )


class ProjectStructureTool(BaseTool):
    name: str = "ProjectStructureTool"
    description: str = (
        "Outil de gestion de structure de projet pour EVE GENESIS. "
        "Permet de créer des structures de projet standardisées, "
        "valider l'organisation des fichiers et analyser l'architecture."
    )
    args_schema: type[BaseModel] = ProjectStructureToolInput

    def _run(
        self, action: str, project_path: str, structure_type: str = "standard"
    ) -> str:
        try:
            project_dir = Path(project_path)

            if action == "create_structure":
                return self._create_project_structure(project_dir, structure_type)
            elif action == "validate_structure":
                return self._validate_project_structure(project_dir, structure_type)
            elif action == "analyze_structure":
                return self._analyze_project_structure(project_dir)
            else:
                return f"Action non reconnue: {action}"

        except Exception as e:
            return f"Erreur lors de la gestion de structure: {str(e)}"

    def _create_project_structure(self, project_dir: Path, structure_type: str) -> str:
        """Crée une structure de projet standardisée."""
        try:
            # Structure de base pour EVE GENESIS
            if structure_type == "eve_genesis":
                dirs = [
                    "src/eve_core",
                    "src/simulation",
                    "src/ui",
                    "src/ai",
                    "config",
                    "tests/unit",
                    "tests/integration",
                    "docs",
                    "scripts",
                    "data/worlds",
                    "data/creatures",
                    "data/backups",
                    "logs",
                    "resources/sounds",
                    "resources/images",
                    "resources/models",
                ]

                files = {
                    "README.md": "# EVE GENESIS Project\n\nProjet de simulation d'évolution artificielle.\n",
                    ".gitignore": "__pycache__/\n*.pyc\n*.pyo\n*.egg-info/\n.env\nlogs/\ndata/backups/\n",
                    "requirements.txt": "crewai>=0.165.1\npsutil>=5.9.0\npyqt6>=6.0.0\npyvista>=0.43.0\n",
                    "config/settings.yaml": "# Configuration EVE GENESIS\nproject_name: EVE_GENESIS\nversion: 1.0.0\n",
                    "config/models.yaml": "# Configuration des modèles IA\nlocal_models:\n  llama3: 8b\n  phi3: mini\n",
                    ".env.template": "# Variables d'environnement EVE GENESIS\nEVE_DEBUG=False\nEVE_LOG_LEVEL=INFO\n",
                }
            else:
                # Structure standard Python
                dirs = ["src", "tests", "docs", "scripts", "data", "config"]

                files = {
                    "README.md": f"# {project_dir.name}\n\nDescription du projet.\n",
                    ".gitignore": "__pycache__/\n*.pyc\n*.pyo\n*.egg-info/\n.env\n",
                    "requirements.txt": "# Dépendances du projet\n",
                    "setup.py": f"from setuptools import setup, find_packages\n\nsetup(\n    name='{project_dir.name}',\n    version='0.1.0',\n    packages=find_packages(where='src'),\n    package_dir={{'': 'src'}}\n)\n",
                }

            # Création des dossiers
            for dir_path in dirs:
                (project_dir / dir_path).mkdir(parents=True, exist_ok=True)

            # Création des fichiers
            for file_path, content in files.items():
                (project_dir / file_path).write_text(content, encoding="utf-8")

            return f"Structure de projet {structure_type} créée avec succès dans {project_dir}"

        except Exception as e:
            return f"Erreur lors de la création de structure: {str(e)}"

    def _validate_project_structure(
        self, project_dir: Path, structure_type: str
    ) -> str:
        """Valide une structure de projet existante."""
        try:
            if not project_dir.exists():
                return f"Erreur: le dossier {project_dir} n'existe pas"

            missing_items = []

            if structure_type == "eve_genesis":
                required_dirs = [
                    "src/eve_core",
                    "src/simulation",
                    "src/ui",
                    "config",
                    "tests",
                ]
                required_files = [
                    "README.md",
                    "requirements.txt",
                    "config/settings.yaml",
                ]
            else:
                required_dirs = ["src", "tests", "docs"]
                required_files = ["README.md", "requirements.txt"]

            # Vérification des dossiers
            for dir_path in required_dirs:
                if not (project_dir / dir_path).exists():
                    missing_items.append(f"Dossier manquant: {dir_path}")

            # Vérification des fichiers
            for file_path in required_files:
                if not (project_dir / file_path).exists():
                    missing_items.append(f"Fichier manquant: {file_path}")

            if missing_items:
                return f"Structure invalide:\n" + "\n".join(missing_items)
            else:
                return f"Structure de projet {structure_type} valide"

        except Exception as e:
            return f"Erreur lors de la validation: {str(e)}"

    def _analyze_project_structure(self, project_dir: Path) -> str:
        """Analyse la structure d'un projet existant."""
        try:
            if not project_dir.exists():
                return f"Erreur: le dossier {project_dir} n'existe pas"

            analysis = []
            total_files = 0
            total_dirs = 0
            file_types = {}

            for item in project_dir.rglob("*"):
                if item.is_file():
                    total_files += 1
                    suffix = item.suffix or "no_extension"
                    file_types[suffix] = file_types.get(suffix, 0) + 1
                elif item.is_dir():
                    total_dirs += 1

            analysis.append(f"Analyse de {project_dir}:")
            analysis.append(f"Total dossiers: {total_dirs}")
            analysis.append(f"Total fichiers: {total_files}")
            analysis.append("Types de fichiers:")

            for ext, count in sorted(file_types.items()):
                analysis.append(f"  {ext}: {count}")

            return "\n".join(analysis)

        except Exception as e:
            return f"Erreur lors de l'analyse: {str(e)}"


# ============================================================================
# CONFIGURATION CREW A - EVE GENESIS
# ============================================================================


@CrewBase
class EveGenesisCrewALIngenieurAdaptatifSupervisable41AgentsCrew:
    """
    EVE GENESIS Crew A - L'Ingénieur Adaptatif & Supervisable

    Ce crew est responsable de la construction, du packaging et du déploiement
    complet du système EVE GENESIS. Il orchestre 41 agents spécialisés à travers
    6 missions critiques pour créer une application complète et déployable.
    """

    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(self.__class__.__name__)
        self._setup_environment()

    def _setup_environment(self):
        """Configure l'environnement d'exécution du crew."""
        try:
            # Création des dossiers de logs si nécessaire
            log_dir = Path("logs")
            log_dir.mkdir(exist_ok=True)

            # Configuration des variables d'environnement
            os.environ.setdefault("EVE_ENV", "development")
            os.environ.setdefault("EVE_LOG_LEVEL", "INFO")

            self.logger.info("Environnement Crew A configuré avec succès")
        except Exception as e:
            self.logger.error(f"Erreur lors de la configuration: {e}")

    def _get_optimized_llm(self) -> LLM:
        """
        Configuration LLM optimisée pour l'usage local avec Ollama.

        Cette configuration est spécialement adaptée pour les tâches
        de développement et de construction d'EVE GENESIS.
        """
        try:
            return LLM(
                model="llama3:8b",
                base_url="http://localhost:11434",
                temperature=0.7,
                max_tokens=4096,  # Augmenté pour les tâches complexes
                timeout=120,  # Timeout plus généreux
                # Paramètres supplémentaires pour Ollama
                num_predict=4096,
                top_k=40,
                top_p=0.9,
                repeat_penalty=1.1,
            )
        except Exception as e:
            self.logger.error(f"Erreur lors de la configuration LLM: {e}")
            # Configuration de fallback
            return LLM(
                model="llama3:8b",
                base_url="http://localhost:11434",
                temperature=0.7,
                max_tokens=2048,
                timeout=60,
            )

    def _create_agent_with_error_handling(
        self, agent_config_key: str, tools: List[BaseTool] = None
    ) -> Agent:
        """Crée un agent avec gestion d'erreur robuste."""
        try:
            return Agent(
                config=self.agents_config[agent_config_key],
                tools=tools or [],
                reasoning=False,
                inject_date=True,
                llm=self._get_optimized_llm(),
                max_iter=5,  # Limite raisonnable pour éviter les boucles infinies
                max_retry=3,  # Nombre de tentatives en cas d'erreur
                verbose=True,
                allow_delegation=False,  # Évite la complexité inutile
            )
        except Exception as e:
            self.logger.error(
                f"Erreur lors de la création de l'agent {agent_config_key}: {e}"
            )
            raise

    # ========================================================================
    # MISSION 1: FONDATION DU PROJET
    # ========================================================================

    @agent
    def architecte_de_configuration(self) -> Agent:
        """Agent responsable de l'architecture et configuration du projet."""
        return self._create_agent_with_error_handling(
            "architecte_de_configuration",
            [FileManagerTool(), ProjectStructureTool(), SystemMonitorTool()],
        )

    @agent
    def quality_control_engineer(self) -> Agent:
        """Agent responsable du contrôle qualité et de l'assurance qualité."""
        return self._create_agent_with_error_handling(
            "quality_control_engineer",
            [GitManagerTool(), FileManagerTool(), PackageManagerTool()],
        )

    @agent
    def business_continuity_engineer(self) -> Agent:
        """Agent responsable de la continuité d'activité et des sauvegardes."""
        return self._create_agent_with_error_handling(
            "business_continuity_engineer", [FileManagerTool(), SystemMonitorTool()]
        )

    @agent
    def infrastructure_project_manager(self) -> Agent:
        """Agent responsable de la gestion de projet et de l'infrastructure."""
        return self._create_agent_with_error_handling(
            "infrastructure_project_manager",
            [FileManagerTool(), ProjectStructureTool(), SystemMonitorTool()],
        )

    # ========================================================================
    # MISSION 2: DÉVELOPPEMENT AGILE
    # ========================================================================

    @agent
    def agile_mission_master(self) -> Agent:
        """Chef d'orchestre du développement agile."""
        return self._create_agent_with_error_handling(
            "agile_mission_master",
            [FileManagerTool(), GitManagerTool(), SystemMonitorTool()],
        )

    @agent
    def ux_ui_blueprint_guardian(self) -> Agent:
        """Gardien des standards UX/UI et de l'expérience utilisateur."""
        return self._create_agent_with_error_handling(
            "ux_ui_blueprint_guardian", [FileManagerTool(), ProjectStructureTool()]
        )

    @agent
    def real_time_quality_sentinel(self) -> Agent:
        """Sentinelle de qualité en temps réel."""
        return self._create_agent_with_error_handling(
            "real_time_quality_sentinel",
            [FileManagerTool(), SystemMonitorTool(), GitManagerTool()],
        )

    @agent
    def software_developer(self) -> Agent:
        """Développeur principal responsable du code source."""
        return self._create_agent_with_error_handling(
            "software_developer",
            [
                FileManagerTool(),
                GitManagerTool(),
                PackageManagerTool(),
                ProjectStructureTool(),
            ],
        )

    @agent
    def software_architect(self) -> Agent:
        """Architecte logiciel responsable de la structure du code."""
        return self._create_agent_with_error_handling(
            "software_architect",
            [FileManagerTool(), ProjectStructureTool(), SystemMonitorTool()],
        )

    @agent
    def automated_tester(self) -> Agent:
        """Testeur automatisé responsable de la qualité du code."""
        return self._create_agent_with_error_handling(
            "automated_tester",
            [FileManagerTool(), GitManagerTool(), PackageManagerTool()],
        )

    @agent
    def technical_writer(self) -> Agent:
        """Rédacteur technique responsable de la documentation."""
        return self._create_agent_with_error_handling(
            "technical_writer", [FileManagerTool(), ProjectStructureTool()]
        )

    # ========================================================================
    # MISSION 3: PACKAGING ET DISTRIBUTION
    # ========================================================================

    @agent
    def release_engineer(self) -> Agent:
        """Ingénieur de release responsable du packaging."""
        return self._create_agent_with_error_handling(
            "release_engineer",
            [
                FileManagerTool(),
                PackageManagerTool(),
                SystemMonitorTool(),
                GitManagerTool(),
            ],
        )

    @agent
    def ux_designer_for_installation(self) -> Agent:
        """Designer UX spécialisé dans l'expérience d'installation."""
        return self._create_agent_with_error_handling(
            "ux_designer_for_installation", [FileManagerTool(), ProjectStructureTool()]
        )

    @agent
    def release_manager(self) -> Agent:
        """Gestionnaire de release responsable de l'assemblage final."""
        return self._create_agent_with_error_handling(
            "release_manager",
            [
                FileManagerTool(),
                GitManagerTool(),
                PackageManagerTool(),
                SystemMonitorTool(),
            ],
        )

    # ========================================================================
    # MISSION 4: DÉPLOIEMENT INTELLIGENT
    # ========================================================================

    @agent
    def launch_orchestrator(self) -> Agent:
        """Orchestrateur de lancement et d'installation."""
        return self._create_agent_with_error_handling(
            "launch_orchestrator", [SystemMonitorTool(), FileManagerTool()]
        )

    @agent
    def pre_emptive_resource_bundler(self) -> Agent:
        """Responsable du pré-calcul des solutions d'installation."""
        return self._create_agent_with_error_handling(
            "pre_emptive_resource_bundler",
            [SystemMonitorTool(), FileManagerTool(), PackageManagerTool()],
        )

    @agent
    def environment_permissions_surveyor(self) -> Agent:
        """Responsable de l'analyse de l'environnement système."""
        return self._create_agent_with_error_handling(
            "environment_permissions_surveyor", [SystemMonitorTool(), FileManagerTool()]
        )

    @agent
    def user_experience_validator(self) -> Agent:
        """Validateur d'expérience utilisateur."""
        return self._create_agent_with_error_handling(
            "user_experience_validator", [FileManagerTool(), SystemMonitorTool()]
        )

    @agent
    def system_diagnostician(self) -> Agent:
        """Diagnosticien système."""
        return self._create_agent_with_error_handling(
            "system_diagnostician",
            [SystemMonitorTool(), FileManagerTool(), PackageManagerTool()],
        )

    @agent
    def interactive_dialogue_manager(self) -> Agent:
        """Gestionnaire de dialogue interactif."""
        return self._create_agent_with_error_handling(
            "interactive_dialogue_manager", [FileManagerTool()]
        )

    @agent
    def automated_installer(self) -> Agent:
        """Installateur automatisé."""
        return self._create_agent_with_error_handling(
            "automated_installer",
            [SystemMonitorTool(), FileManagerTool(), PackageManagerTool()],
        )

    @agent
    def adaptive_interaction_modulator(self) -> Agent:
        """Modulateur d'interaction adaptative."""
        return self._create_agent_with_error_handling(
            "adaptive_interaction_modulator", [FileManagerTool(), SystemMonitorTool()]
        )

    @agent
    def installation_supervisor(self) -> Agent:
        """Superviseur d'installation."""
        return self._create_agent_with_error_handling(
            "installation_supervisor", [SystemMonitorTool(), FileManagerTool()]
        )

    @agent
    def fault_detector_repairer(self) -> Agent:
        """Détecteur et réparateur de pannes."""
        return self._create_agent_with_error_handling(
            "fault_detector_repairer",
            [SystemMonitorTool(), FileManagerTool(), PackageManagerTool()],
        )

    # ========================================================================
    # MISSION 5: CRÉATION DU MONDE VIRTUEL
    # ========================================================================

    @agent
    def security_guardian(self) -> Agent:
        """Gardien de sécurité système."""
        return self._create_agent_with_error_handling(
            "security_guardian", [SystemMonitorTool(), FileManagerTool()]
        )

    @agent
    def local_api_creator(self) -> Agent:
        """Créateur d'API locale."""
        return self._create_agent_with_error_handling(
            "local_api_creator",
            [FileManagerTool(), SystemMonitorTool(), PackageManagerTool()],
        )

    @agent
    def local_ai_model_manager(self) -> Agent:
        """Gestionnaire de modèles IA locaux."""
        return self._create_agent_with_error_handling(
            "local_ai_model_manager",
            [SystemMonitorTool(), FileManagerTool(), PackageManagerTool()],
        )

    @agent
    def world_architect(self) -> Agent:
        """Architecte du monde virtuel."""
        return self._create_agent_with_error_handling(
            "world_architect", [FileManagerTool(), SystemMonitorTool()]
        )

    @agent
    def digital_geneticist(self) -> Agent:
        """Généticien numérique."""
        return self._create_agent_with_error_handling(
            "digital_geneticist", [FileManagerTool(), SystemMonitorTool()]
        )

    @agent
    def behavioral_ai_specialist(self) -> Agent:
        """Spécialiste IA comportementale."""
        return self._create_agent_with_error_handling(
            "behavioral_ai_specialist", [FileManagerTool(), SystemMonitorTool()]
        )

    # ========================================================================
    # MISSION 6: ÉVEIL D'EVE
    # ========================================================================

    @agent
    def eve_s_awakening_manager(self) -> Agent:
        """Gestionnaire de l'éveil d'EVE."""
        return self._create_agent_with_error_handling(
            "eve_s_awakening_manager", [SystemMonitorTool(), FileManagerTool()]
        )

    @agent
    def ultimate_supervisor_agent(self) -> Agent:
        """Agent superviseur ultime."""
        return self._create_agent_with_error_handling(
            "ultimate_supervisor_agent", [SystemMonitorTool(), FileManagerTool()]
        )

    @agent
    def conversational_assistant(self) -> Agent:
        """Assistant conversationnel."""
        return self._create_agent_with_error_handling(
            "conversational_assistant", [FileManagerTool()]
        )

    @agent
    def emotional_psychological_engine(self) -> Agent:
        """Moteur émotionnel et psychologique."""
        return self._create_agent_with_error_handling(
            "emotional_psychological_engine", [FileManagerTool(), SystemMonitorTool()]
        )

    @agent
    def voice_response_synthesizer(self) -> Agent:
        """Synthétiseur de voix et réponses."""
        return self._create_agent_with_error_handling(
            "voice_response_synthesizer", [FileManagerTool(), SystemMonitorTool()]
        )

    @agent
    def evolving_3d_avatar_creator(self) -> Agent:
        """Créateur d'avatar 3D évolutif."""
        return self._create_agent_with_error_handling(
            "evolving_3d_avatar_creator", [FileManagerTool(), SystemMonitorTool()]
        )

    @agent
    def comparative_intelligence_analyzer(self) -> Agent:
        """Analyseur d'intelligence comparative."""
        return self._create_agent_with_error_handling(
            "comparative_intelligence_analyzer",
            [FileManagerTool(), SystemMonitorTool()],
        )

    @agent
    def human_emotion_recognition_analyst(self) -> Agent:
        """Analyste de reconnaissance émotionnelle humaine."""
        return self._create_agent_with_error_handling(
            "human_emotion_recognition_analyst",
            [FileManagerTool(), SystemMonitorTool()],
        )

    @agent
    def cartographe_de_processus_et_traducteur_structurel(self) -> Agent:
        """Cartographe de processus et traducteur structurel."""
        return self._create_agent_with_error_handling(
            "cartographe_de_processus_et_traducteur_structurel",
            [FileManagerTool(), ProjectStructureTool()],
        )

    # ========================================================================
    # DÉFINITION DES TÂCHES
    # ========================================================================

    @task
    def etablir_les_fondations_du_projet(self) -> Task:
        return Task(config=self.tasks_config["etablir_les_fondations_du_projet"])

    @task
    def construire_le_pipeline_de_controle_qualite(self) -> Task:
        return Task(
            config=self.tasks_config["construire_le_pipeline_de_controle_qualite"]
        )

    @task
    def concevoir_le_systeme_de_sauvegarde(self) -> Task:
        return Task(config=self.tasks_config["concevoir_le_systeme_de_sauvegarde"])

    @task
    def superviser_le_sprint_fondation_et_livrer_le_rapport_de_cloture(self) -> Task:
        return Task(
            config=self.tasks_config[
                "superviser_le_sprint_fondation_et_livrer_le_rapport_de_cloture"
            ]
        )

    @task
    def orchestrer_les_micro_cycles_de_developpement_agile(self) -> Task:
        return Task(
            config=self.tasks_config[
                "orchestrer_les_micro_cycles_de_developpement_agile"
            ]
        )

    @task
    def creer_la_charte_de_design_et_experience(self) -> Task:
        return Task(config=self.tasks_config["creer_la_charte_de_design_et_experience"])

    @task
    def surveiller_la_qualite_en_temps_reel(self) -> Task:
        return Task(config=self.tasks_config["surveiller_la_qualite_en_temps_reel"])

    @task
    def generer_le_code_source_fonctionnel(self) -> Task:
        return Task(config=self.tasks_config["generer_le_code_source_fonctionnel"])

    @task
    def valider_l_architecture_et_la_coherence_du_code(self) -> Task:
        return Task(
            config=self.tasks_config["valider_l_architecture_et_la_coherence_du_code"]
        )

    @task
    def ecrire_et_executer_les_tests_unitaires(self) -> Task:
        return Task(config=self.tasks_config["ecrire_et_executer_les_tests_unitaires"])

    @task
    def creer_la_documentation_technique_complete(self) -> Task:
        return Task(
            config=self.tasks_config["creer_la_documentation_technique_complete"]
        )

    @task
    def creer_le_paquet_d_installation_autonome(self) -> Task:
        return Task(config=self.tasks_config["creer_le_paquet_d_installation_autonome"])

    @task
    def concevoir_l_interface_graphique_de_l_installateur(self) -> Task:
        return Task(
            config=self.tasks_config[
                "concevoir_l_interface_graphique_de_l_installateur"
            ]
        )

    @task
    def assembler_l_archive_finale_et_rediger_les_notes_de_version(self) -> Task:
        return Task(
            config=self.tasks_config[
                "assembler_l_archive_finale_et_rediger_les_notes_de_version"
            ]
        )

    @task
    def orchestrer_le_processus_d_installation_utilisateur(self) -> Task:
        return Task(
            config=self.tasks_config[
                "orchestrer_le_processus_d_installation_utilisateur"
            ]
        )

    @task
    def pre_calculer_les_solutions_d_installation(self) -> Task:
        return Task(
            config=self.tasks_config["pre_calculer_les_solutions_d_installation"]
        )

    @task
    def cartographier_l_environnement_systeme_cible(self) -> Task:
        return Task(
            config=self.tasks_config["cartographier_l_environnement_systeme_cible"]
        )

    @task
    def valider_l_experience_utilisateur(self) -> Task:
        return Task(config=self.tasks_config["valider_l_experience_utilisateur"])

    @task
    def valider_la_compatibilite_materielle_et_logicielle(self) -> Task:
        return Task(
            config=self.tasks_config[
                "valider_la_compatibilite_materielle_et_logicielle"
            ]
        )

    @task
    def gerer_le_dialogue_interactif(self) -> Task:
        return Task(config=self.tasks_config["gerer_le_dialogue_interactif"])

    @task
    def executer_les_taches_d_installation_technique(self) -> Task:
        return Task(
            config=self.tasks_config["executer_les_taches_d_installation_technique"]
        )

    @task
    def definir_le_mode_d_interaction_personnalise(self) -> Task:
        return Task(
            config=self.tasks_config["definir_le_mode_d_interaction_personnalise"]
        )

    @task
    def surveiller_et_valider_l_installation(self) -> Task:
        return Task(config=self.tasks_config["surveiller_et_valider_l_installation"])

    @task
    def etablir_le_perimetre_de_securite_des_ressources(self) -> Task:
        return Task(
            config=self.tasks_config["etablir_le_perimetre_de_securite_des_ressources"]
        )

    @task
    def diagnostiquer_et_reparer_les_erreurs_d_installation(self) -> Task:
        return Task(
            config=self.tasks_config[
                "diagnostiquer_et_reparer_les_erreurs_d_installation"
            ]
        )

    @task
    def demarrer_le_systeme_nerveux_central(self) -> Task:
        return Task(config=self.tasks_config["demarrer_le_systeme_nerveux_central"])

    @task
    def orchestrer_la_sequence_d_eveil_d_eve(self) -> Task:
        return Task(config=self.tasks_config["orchestrer_la_sequence_d_eveil_d_eve"])

    @task
    def charger_les_modeles_d_intelligence_artificielle(self) -> Task:
        return Task(
            config=self.tasks_config["charger_les_modeles_d_intelligence_artificielle"]
        )

    @task
    def generer_le_monde_initial(self) -> Task:
        return Task(config=self.tasks_config["generer_le_monde_initial"])

    @task
    def creer_la_vie_initiale(self) -> Task:
        return Task(config=self.tasks_config["creer_la_vie_initiale"])

    @task
    def attribuer_les_comportements_de_base(self) -> Task:
        return Task(config=self.tasks_config["attribuer_les_comportements_de_base"])

    @task
    def activer_l_interface_de_supervision_principale(self) -> Task:
        return Task(
            config=self.tasks_config["activer_l_interface_de_supervision_principale"]
        )

    @task
    def initialiser_le_module_de_dialogue(self) -> Task:
        return Task(config=self.tasks_config["initialiser_le_module_de_dialogue"])

    @task
    def developper_le_premier_etat_emotionnel(self) -> Task:
        return Task(config=self.tasks_config["developper_le_premier_etat_emotionnel"])

    @task
    def preparer_la_voix_d_eve(self) -> Task:
        return Task(config=self.tasks_config["preparer_la_voix_d_eve"])

    @task
    def afficher_l_avatar_d_eve(self) -> Task:
        return Task(config=self.tasks_config["afficher_l_avatar_d_eve"])

    @task
    def activer_le_tableau_de_bord_cognitif(self) -> Task:
        return Task(config=self.tasks_config["activer_le_tableau_de_bord_cognitif"])

    @task
    def demarrer_l_analyse_emotionnelle_de_l_utilisateur(self) -> Task:
        return Task(
            config=self.tasks_config["demarrer_l_analyse_emotionnelle_de_l_utilisateur"]
        )

    @task
    def generer_le_script_de_lancement_eve(self) -> Task:
        return Task(config=self.tasks_config["generer_le_script_de_lancement_eve"])

    @task
    def generer_la_carte_de_workflow_n8n(self) -> Task:
        return Task(config=self.tasks_config["generer_la_carte_de_workflow_n8n"])

    # ========================================================================
    # CONFIGURATION DU CREW
    # ========================================================================

    @crew
    def crew(self) -> Crew:
        """
        Crée le crew EVE GENESIS Crew A avec configuration optimisée.

        Ce crew orchestre 41 agents à travers 40 tâches séquentielles
        pour construire, tester, packager et déployer l'application EVE GENESIS.
        """
        try:
            return Crew(
                agents=self.agents,
                tasks=self.tasks,
                process=Process.sequential,
                verbose=True,
                memory=False,  # Désactivé pour optimiser les performances avec Ollama
                cache=True,  # Active le cache pour améliorer les performances
                max_rpm=10,  # Limite le taux de requêtes par minute
                embedder=None,  # Pas d'embedder pour simplifier
                full_output=True,  # Active la sortie complète pour le debugging
                step_callback=self._step_callback,  # Callback pour le monitoring
                task_callback=self._task_callback,  # Callback pour les tâches
            )
        except Exception as e:
            self.logger.error(f"Erreur lors de la création du crew: {e}")
            raise

    def _step_callback(self, step):
        """Callback appelé à chaque étape d'exécution."""
        self.logger.info(
            f"Étape exécutée: {step.get('agent', 'Unknown')} - {step.get('tool', 'Unknown')}"
        )

    def _task_callback(self, task):
        """Callback appelé à chaque fin de tâche."""
        self.logger.info(f"Tâche terminée: {task.description[:100]}...")

    def get_crew_status(self) -> Dict[str, Any]:
        """Retourne le statut actuel du crew."""
        return {
            "name": "EVE GENESIS Crew A",
            "agents_count": len(self.agents),
            "tasks_count": len(self.tasks),
            "status": "ready",
            "timestamp": datetime.now().isoformat(),
            "environment": os.environ.get("EVE_ENV", "development"),
            "system_info": {
                "platform": platform.system(),
                "python_version": sys.version.split()[0],
                "memory_usage": f"{psutil.virtual_memory().percent}%",
                "cpu_usage": f"{psutil.cpu_percent()}%",
            },
        }

    def save_execution_report(
        self, result, output_path: str = "logs/crew_a_execution_report.json"
    ):
        """Sauvegarde un rapport d'exécution détaillé."""
        try:
            report = {
                "execution_timestamp": datetime.now().isoformat(),
                "crew_info": self.get_crew_status(),
                "execution_result": str(result),
                "execution_success": bool(result),
                "total_agents": len(self.agents),
                "total_tasks": len(self.tasks),
            }

            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            output_file.write_text(
                json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
            )

            self.logger.info(f"Rapport d'exécution sauvegardé: {output_path}")
            return True
        except Exception as e:
            self.logger.error(f"Erreur lors de la sauvegarde du rapport: {e}")
            return False


# ============================================================================
# FONCTIONS UTILITAIRES
# ============================================================================


def validate_ollama_connection() -> bool:
    """Valide la connexion à Ollama."""
    try:
        import requests

        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        return response.status_code == 200
    except Exception:
        return False


def setup_crew_environment():
    """Configure l'environnement pour l'exécution du crew."""
    try:
        # Vérification de la connexion Ollama
        if not validate_ollama_connection():
            logger.warning(
                "Ollama n'est pas accessible. Vérifiez que le service est démarré."
            )

        # Création des dossiers nécessaires
        required_dirs = ["logs", "data", "temp", "output"]
        for dir_name in required_dirs:
            Path(dir_name).mkdir(exist_ok=True)

        # Configuration des variables d'environnement
        os.environ.setdefault("PYTHONPATH", str(Path.cwd()))
        os.environ.setdefault("EVE_WORKSPACE", str(Path.cwd()))

        logger.info("Environnement du crew configuré avec succès")
        return True
    except Exception as e:
        logger.error(f"Erreur lors de la configuration de l'environnement: {e}")
        return False


if __name__ == "__main__":
    # Test du crew
    setup_crew_environment()
    crew_instance = EveGenesisCrewALIngenieurAdaptatifSupervisable41AgentsCrew()
    status = crew_instance.get_crew_status()
    print(json.dumps(status, indent=2, ensure_ascii=False))
