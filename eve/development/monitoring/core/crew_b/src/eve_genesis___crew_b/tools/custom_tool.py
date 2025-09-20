from crewai.tools import BaseTool
from typing import Type, Optional, Dict, Any, List
from pydantic import BaseModel, Field
import os
import json
import yaml
import psutil
import requests
from pathlib import Path
import time
import random


# ============================================================================
# OUTIL 1: GESTIONNAIRE DE FICHIERS (pour données et contenus)
# ============================================================================


class FileManagerInput(BaseModel):
    """Input schema for FileManager."""

    action: str = Field(
        ...,
        description="Action: 'create_dir', 'create_file', 'read_file', 'write_file', 'list_files'",
    )
    path: str = Field(..., description="File or directory path")
    content: Optional[str] = Field(
        None, description="File content for write operations"
    )


class FileManagerTool(BaseTool):
    """TODO: Add docstring."""
    name: str = "File Manager"
    description: str = (
        "Manage files and directories for EVE GENESIS content and data. "
        "Specialized for narrative, scientific, and evolutionary data management."
    )
    args_schema: Type[BaseModel] = FileManagerInput

    """TODO: Add docstring."""
    def _run(self, action: str, path: str, content: Optional[str] = None) -> str:
        try:
            path_obj = Path(path)

            if action == "create_dir":
                path_obj.mkdir(parents=True, exist_ok=True)
                return f"✅ Directory created: {path}"

            elif action == "create_file":
                path_obj.parent.mkdir(parents=True, exist_ok=True)
                path_obj.touch()
                return f"✅ File created: {path}"

            elif action == "read_file":
                if path_obj.exists():
                    content = path_obj.read_text(encoding="utf-8")
                    return (
                        f"✅ File content:\n{content[:500]}..."
                        if len(content) > 500
                        else f"✅ File content:\n{content}"
                    )
                return f"❌ File not found: {path}"

            elif action == "write_file":
                if content is None:
                    return "❌ Content is required for write operations"
                path_obj.parent.mkdir(parents=True, exist_ok=True)
                path_obj.write_text(content, encoding="utf-8")
                return f"✅ File written: {path} ({len(content)} characters)"

            elif action == "list_files":
                if path_obj.is_dir():
                    files = [f.name for f in path_obj.iterdir()]
                    return f"✅ Files in {path}: {files}"
                else:
                    return f"❌ {path} is not a directory"

            else:
                return f"❌ Unknown action: {action}"

        except Exception as e:
            return f"❌ Error in {action}: {str(e)}"


# ============================================================================
# OUTIL 2: GESTIONNAIRE DE CONFIGURATION (pour paramètres évolutifs)
# ============================================================================


class ConfigManagerInput(BaseModel):
    """Input schema for ConfigManager."""

    action: str = Field(
        ...,
        description="Action: 'create_yaml', 'read_yaml', 'update_yaml', 'create_json', 'read_json'",
    )
    file_path: str = Field(..., description="Configuration file path")
    data: Optional[Dict[str, Any]] = Field(None, description="Configuration data")
    key_path: Optional[str] = Field(
        None, description="Dot-separated key path for updates"
    )
    value: Optional[Any] = Field(
        None, description="Value to set for the specified key path"
    )


    """TODO: Add docstring."""
class ConfigManagerTool(BaseTool):
    name: str = "Configuration Manager"
    description: str = (
        "Manage dynamic configurations for EVE GENESIS evolution and enrichment. "
        "Handles agent settings, narrative parameters, and system evolution configs."
    )
        """TODO: Add docstring."""
    args_schema: Type[BaseModel] = ConfigManagerInput

    def _run(
        self,
        action: str,
        file_path: str,
        data: Optional[Dict[str, Any]] = None,
        key_path: Optional[str] = None,
        value: Optional[Any] = None,
    ) -> str:
        try:
            path_obj = Path(file_path)

            if action == "create_yaml":
                if data is None:
                    return "❌ Data is required for YAML creation"
                path_obj.parent.mkdir(parents=True, exist_ok=True)
                with open(file_path, "w", encoding="utf-8") as f:
                    yaml.dump(
                        data, f, default_flow_style=False, allow_unicode=True, indent=2
                    )
                return f"✅ YAML file created: {file_path}"

            elif action == "read_yaml":
                if not path_obj.exists():
                    return f"❌ YAML file not found: {file_path}"
                with open(file_path, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                return f"✅ YAML loaded successfully from {file_path}"

            elif action == "update_yaml":
                if not path_obj.exists():
                    return f"❌ YAML file not found: {file_path}"
                if key_path is None or value is None:
                    return "❌ key_path and value are required for updates"

                with open(file_path, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f) or {}

                keys = key_path.split(".")
                current = data
                for key in keys[:-1]:
                    if key not in current:
                        current[key] = {}
                    current = current[key]
                current[keys[-1]] = value

                with open(file_path, "w", encoding="utf-8") as f:
                    yaml.dump(
                        data, f, default_flow_style=False, allow_unicode=True, indent=2
                    )
                return f"✅ YAML updated: {key_path} = {value}"

            elif action == "create_json":
                if data is None:
                    return "❌ Data is required for JSON creation"
                path_obj.parent.mkdir(parents=True, exist_ok=True)
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                return f"✅ JSON file created: {file_path}"

            elif action == "read_json":
                if not path_obj.exists():
                    return f"❌ JSON file not found: {file_path}"
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                return f"✅ JSON loaded successfully from {file_path}"

            else:
                return f"❌ Unknown action: {action}"

        except Exception as e:
            return f"❌ Error in configuration management: {str(e)}"


# ============================================================================
# OUTIL 3: CLIENT API (pour communications inter-agents)
# ============================================================================


class APIClientInput(BaseModel):
    """Input schema for APIClient."""

    action: str = Field(..., description="Action: 'get', 'post', 'put'")
    url: str = Field(..., description="API endpoint URL")
    data: Optional[Dict[str, Any]] = Field(None, description="Request data")
    timeout: int = Field(10, description="Request timeout in seconds")

    """TODO: Add docstring."""

class APIClientTool(BaseTool):
    name: str = "API Client"
    description: str = (
        "Communicate with EVE GENESIS APIs and external services. "
            """TODO: Add docstring."""
        "Enables inter-agent communication and external data integration."
    )
    args_schema: Type[BaseModel] = APIClientInput

    def _run(
        self,
        action: str,
        url: str,
        data: Optional[Dict[str, Any]] = None,
        timeout: int = 10,
    ) -> str:
        try:
            headers = {"Content-Type": "application/json"}

            if action == "get":
                response = requests.get(url, headers=headers, timeout=timeout)
            elif action == "post":
                response = requests.post(
                    url, headers=headers, json=data, timeout=timeout
                )
            elif action == "put":
                response = requests.put(
                    url, headers=headers, json=data, timeout=timeout
                )
            else:
                return f"❌ Unknown HTTP method: {action}"

            result = f"✅ {action.upper()} {url}\n"
            result += f"Status Code: {response.status_code}\n"

            try:
                json_response = response.json()
                result += f"Response: {json.dumps(json_response, indent=2)[:300]}...\n"
            except:
                result += f"Response: {response.text[:200]}...\n"

            return result

        except requests.exceptions.Timeout:
            return f"❌ Request timeout after {timeout}s: {url}"
        except requests.exceptions.ConnectionError:
            return f"❌ Connection error: {url}"
        except Exception as e:
            return f"❌ Error in API request: {str(e)}"


# ============================================================================
# OUTIL 4: MONITEUR SYSTÈME (pour performance et adaptation)
# ============================================================================


class SystemMonitorInput(BaseModel):
    """Input schema for SystemMonitor."""

    action: str = Field(
        ...,
        description="Action: 'check_resources', 'monitor_performance', 'adaptive_check'",
    )
        """TODO: Add docstring."""


class SystemMonitorTool(BaseTool):
    name: str = "System Monitor"
        """TODO: Add docstring."""
    description: str = (
        "Monitor system performance for EVE GENESIS adaptive behaviors. "
        "Provides resource info for evolutionary optimization."
    )
    args_schema: Type[BaseModel] = SystemMonitorInput

    def _run(self, action: str) -> str:
        try:
            if action == "check_resources":
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()

                report = f"🖥️ System Resources:\n"
                report += f"CPU: {cpu_percent}%\n"
                report += f"RAM: {memory.percent}% ({memory.used//1024//1024}MB used)\n"

                return report

            elif action == "monitor_performance":
                cpu_percent = psutil.cpu_percent(interval=0.5)
                memory = psutil.virtual_memory()

                # Analyse adaptive
                if cpu_percent > 80:
                    recommendation = (
                        "🔥 High CPU - Consider reducing simulation complexity"
                    )
                elif cpu_percent < 20:
                    recommendation = "💚 Low CPU - Can increase simulation detail"
                else:
                    recommendation = "⚖️ Balanced CPU - Optimal performance"

                return (
                    f"📊 Performance Analysis:\nCPU: {cpu_percent}%\n{recommendation}"
                )

            elif action == "adaptive_check":
                # Simulation d'un check adaptatif pour l'évolution
                metrics = {
                    "cpu_efficiency": random.uniform(0.7, 1.0),
                    "memory_optimization": random.uniform(0.6, 0.95),
                    "system_stability": random.uniform(0.8, 1.0),
                }

                avg_performance = sum(metrics.values()) / len(metrics)

                return (
                    f"🧬 Adaptive Metrics:\n"
                    + f"Efficiency: {metrics['cpu_efficiency']:.2f}\n"
                    + f"Optimization: {metrics['memory_optimization']:.2f}\n"
                    + f"Stability: {metrics['system_stability']:.2f}\n"
                    + f"Overall Performance: {avg_performance:.2f}"
                )

            else:
                return f"❌ Unknown action: {action}"

        except Exception as e:
            return f"❌ Error in system monitoring: {str(e)}"


# ============================================================================
# OUTIL 5: GÉNÉRATEUR DE DONNÉES ÉVOLUTIVES
# ============================================================================


class DataGeneratorInput(BaseModel):
    """Input schema for DataGenerator."""

    data_type: str = Field(
        ..., description="Type: 'narrative', 'statistical', 'evolutionary', 'creative'"
    )
    parameters: Optional[Dict[str, Any]] = Field(
        None, description="Generation parameters"
    )
    output_format: str = Field(
        "json", description="Output format: 'json', 'yaml', 'text'"
            """TODO: Add docstring."""
    )


    """TODO: Add docstring."""
class DataGeneratorTool(BaseTool):
    name: str = "Data Generator"
    description: str = (
        "Generate synthetic data for EVE GENESIS evolution and enrichment. "
        "Creates narrative content, statistics, and evolutionary parameters."
    )
    args_schema: Type[BaseModel] = DataGeneratorInput

    def _run(
        self,
        data_type: str,
        parameters: Optional[Dict[str, Any]] = None,
        output_format: str = "json",
    ) -> str:
        try:
            if parameters is None:
                parameters = {}

            if data_type == "narrative":
                # Génération de données narratives
                stories = [
                    "In the depths of the digital realm, consciousness stirred...",
                    "The algorithms danced in patterns unknown to their creators...",
                    "Evolution took a new form in the silicon universe...",
                    "Each iteration brought new wisdom to the artificial minds...",
                ]

                data = {
                    "story_fragments": random.sample(stories, 2),
                    "narrative_themes": ["consciousness", "evolution", "discovery"],
                    "emotional_tone": random.choice(
                        ["curious", "mystical", "profound"]
                    ),
                    "generated_at": time.time(),
                }

            elif data_type == "statistical":
                # Génération de données statistiques
                data = {
                    "population_metrics": {
                        "total_entities": random.randint(100, 1000),
                        "evolution_rate": random.uniform(0.1, 0.8),
                        "diversity_index": random.uniform(0.5, 1.0),
                    },
                    "performance_stats": {
                        "processing_efficiency": random.uniform(0.7, 0.95),
                        "adaptation_speed": random.uniform(0.3, 0.9),
                    },
                }

            elif data_type == "evolutionary":
                # Génération de paramètres évolutifs
                data = {
                    "mutation_rate": random.uniform(0.01, 0.1),
                    "selection_pressure": random.uniform(0.2, 0.8),
                    "environmental_factors": {
                        "complexity": random.uniform(0.3, 0.9),
                        "stability": random.uniform(0.5, 1.0),
                        "resources": random.uniform(0.4, 0.8),
                    },
                    "generation": random.randint(1, 100),
                }

            elif data_type == "creative":
                # Génération de données créatives
                colors = ["crimson", "azure", "emerald", "golden", "violet"]
                moods = ["serene", "dynamic", "mysterious", "harmonious"]

                data = {
                    "color_palette": random.sample(colors, 3),
                    "artistic_mood": random.choice(moods),
                    "inspiration_level": random.uniform(0.6, 1.0),
                    "creative_complexity": random.randint(1, 10),
                }

            else:
                return f"❌ Unknown data type: {data_type}"

            # Format de sortie
            if output_format == "json":
                return f"✅ Generated {data_type} data:\n{json.dumps(data, indent=2)}"
            elif output_format == "yaml":
                return f"✅ Generated {data_type} data:\n{yaml.dump(data, default_flow_style=False)}"
            else:
                return f"✅ Generated {data_type} data:\n{str(data)}"

        except Exception as e:
            return f"❌ Error in data generation: {str(e)}"


# ============================================================================
# EXPORT DES OUTILS POUR CREW B
# ============================================================================

CREW_B_TOOLS = [
    FileManagerTool(),
    ConfigManagerTool(),
    APIClientTool(),
    SystemMonitorTool(),
    DataGeneratorTool(),
]


def get_enrichment_tools():
    """Retourne les outils essentiels pour l'enrichissement EVE GENESIS."""
    return CREW_B_TOOLS


def get_tool_by_name(tool_name: str):
    """Récupère un outil spécifique par son nom."""
    tool_map = {tool.name: tool for tool in CREW_B_TOOLS}
    return tool_map.get(tool_name)