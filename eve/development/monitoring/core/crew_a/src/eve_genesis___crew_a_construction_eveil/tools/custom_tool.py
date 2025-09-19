from crewai.tools import BaseTool
from typing import Type, Optional, Dict, Any
from pydantic import BaseModel, Field
import os
import subprocess
import json
import yaml
import shutil
import hashlib
import psutil
from pathlib import Path
import sys


# ============================================================================
# OUTIL 1: GESTIONNAIRE DE FICHIERS (pour construction projet)
# ============================================================================


class FileManagerInput(BaseModel):
    """Input schema for FileManager."""

    action: str = Field(
        ...,
        description="Action: 'create_dir', 'create_file', 'read_file', 'write_file', 'copy', 'move', 'delete'",
    )
    path: str = Field(..., description="File or directory path")
    content: Optional[str] = Field(
        None, description="File content for write operations"
    )
    destination: Optional[str] = Field(
        None, description="Destination path for copy/move operations"
    )


class FileManagerTool(BaseTool):
    name: str = "File Manager"
    description: str = (
        "Comprehensive file and directory management for EVE GENESIS construction. "
        "Can create directories, create/read/write files, copy, move, and delete files/folders."
    )
    args_schema: Type[BaseModel] = FileManagerInput

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
                return f"✅ Directory created: {path}"

            elif action == "create_file":
                path_obj.parent.mkdir(parents=True, exist_ok=True)
                path_obj.touch()
                return f"✅ File created: {path}"

            elif action == "read_file":
                if path_obj.exists():
                    content = path_obj.read_text(encoding="utf-8")
                    return f"✅ File content:\n{content}"
                return f"❌ File not found: {path}"

            elif action == "write_file":
                if content is None:
                    return "❌ Content is required for write operations"
                path_obj.parent.mkdir(parents=True, exist_ok=True)
                path_obj.write_text(content, encoding="utf-8")
                return f"✅ File written: {path} ({len(content)} characters)"

            elif action == "copy":
                if destination is None:
                    return "❌ Destination is required for copy operations"
                if path_obj.is_file():
                    shutil.copy2(path, destination)
                else:
                    shutil.copytree(path, destination, dirs_exist_ok=True)
                return f"✅ Copied {path} to {destination}"

            elif action == "move":
                if destination is None:
                    return "❌ Destination is required for move operations"
                shutil.move(path, destination)
                return f"✅ Moved {path} to {destination}"

            elif action == "delete":
                if path_obj.is_file():
                    path_obj.unlink()
                elif path_obj.is_dir():
                    shutil.rmtree(path)
                return f"✅ Deleted: {path}"

            else:
                return f"❌ Unknown action: {action}"

        except Exception as e:
            return f"❌ Error in {action}: {str(e)}"


# ============================================================================
# OUTIL 2: EXECUTEUR DE COMMANDES SYSTÈME (pour installation/déploiement)
# ============================================================================


class SystemCommandInput(BaseModel):
    """Input schema for SystemCommand."""

    command: str = Field(..., description="System command to execute")
    working_dir: Optional[str] = Field(
        None, description="Working directory for command execution"
    )
    timeout: int = Field(30, description="Command timeout in seconds")


class SystemCommandTool(BaseTool):
    name: str = "System Command Executor"
    description: str = (
        "Execute system commands safely for EVE GENESIS installation and setup. "
        "Can run shell commands, install packages, configure services."
    )
    args_schema: Type[BaseModel] = SystemCommandInput

    def _run(
        self, command: str, working_dir: Optional[str] = None, timeout: int = 30
    ) -> str:
        try:
            # Sécurité : empêcher les commandes dangereuses
            dangerous_commands = [
                "rm -rf /",
                "format",
                "del *",
                "shutdown",
                "reboot",
                "mkfs",
            ]
            if any(danger in command.lower() for danger in dangerous_commands):
                return f"❌ Command blocked for security: {command}"

            result = subprocess.run(
                command,
                shell=True,
                cwd=working_dir,
                capture_output=True,
                text=True,
                timeout=timeout,
            )

            output = f"✅ Command executed: {command}\n"
            output += f"Return code: {result.returncode}\n"

            if result.stdout:
                output += f"STDOUT:\n{result.stdout}\n"
            if result.stderr:
                output += f"STDERR:\n{result.stderr}\n"

            return output

        except subprocess.TimeoutExpired:
            return f"❌ Command timed out after {timeout}s: {command}"
        except Exception as e:
            return f"❌ Error executing command: {str(e)}"


# ============================================================================
# OUTIL 3: MONITEUR SYSTÈME (pour diagnostic et ressources)
# ============================================================================


class SystemMonitorInput(BaseModel):
    """Input schema for SystemMonitor."""

    action: str = Field(
        ..., description="Action: 'check_resources', 'check_disk', 'check_processes'"
    )
    threshold: Optional[float] = Field(
        None, description="Threshold value for resource monitoring"
    )


class SystemMonitorTool(BaseTool):
    name: str = "System Monitor"
    description: str = (
        "Monitor system resources (CPU, RAM, disk) for EVE GENESIS optimization and diagnostics."
    )
    args_schema: Type[BaseModel] = SystemMonitorInput

    def _run(self, action: str, threshold: Optional[float] = None) -> str:
        try:
            if action == "check_resources":
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage("/")

                report = f"🖥️ System Resources Report:\n"
                report += f"CPU Usage: {cpu_percent}%\n"
                report += f"RAM Usage: {memory.percent}% ({memory.used//1024//1024}MB / {memory.total//1024//1024}MB)\n"
                report += f"Disk Usage: {disk.percent}% ({disk.free//1024//1024//1024}GB free)\n"

                if threshold:
                    alerts = []
                    if cpu_percent > threshold:
                        alerts.append(f"⚠️ High CPU usage: {cpu_percent}%")
                    if memory.percent > threshold:
                        alerts.append(f"⚠️ High RAM usage: {memory.percent}%")
                    if disk.percent > threshold:
                        alerts.append(f"⚠️ High disk usage: {disk.percent}%")

                    if alerts:
                        report += "\n" + "\n".join(alerts)

                return report

            elif action == "check_disk":
                disk = psutil.disk_usage("/")
                return f"💾 Disk Usage: {disk.percent}% ({disk.free//1024//1024//1024}GB free)"

            elif action == "check_processes":
                processes = []
                for proc in psutil.process_iter(["pid", "name", "cpu_percent"]):
                    try:
                        if proc.info["cpu_percent"] > 5:
                            processes.append(proc.info)
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass

                processes.sort(key=lambda x: x["cpu_percent"], reverse=True)
                report = "📊 Top CPU Processes:\n"
                for proc in processes[:5]:
                    report += f"PID {proc['pid']}: {proc['name']} - {proc['cpu_percent']:.1f}%\n"

                return report

            else:
                return f"❌ Unknown action: {action}"

        except Exception as e:
            return f"❌ Error in system monitoring: {str(e)}"


# ============================================================================
# OUTIL 4: GESTIONNAIRE DE CONFIGURATION (pour YAML/JSON)
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


class ConfigManagerTool(BaseTool):
    name: str = "Configuration Manager"
    description: str = (
        "Manage YAML and JSON configuration files for EVE GENESIS. "
        "Can create, read, and update complex configuration structures."
    )
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
                    if not isinstance(current, dict):
                        current = {}
                    if key not in current:
                        current[key] = {}
                    current = current[key]
                    if current is None:
                        current = {}
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
# OUTIL 5: VALIDATEUR DE CODE (pour tests et qualité)
# ============================================================================


class CodeValidatorInput(BaseModel):
    """Input schema for CodeValidator."""

    action: str = Field(
        ...,
        description="Action: 'validate_python', 'check_syntax', 'calculate_checksum'",
    )
    file_path: Optional[str] = Field(None, description="File path for validation")
    code_content: Optional[str] = Field(
        None, description="Python code content to validate"
    )


class CodeValidatorTool(BaseTool):
    name: str = "Code Validator"
    description: str = (
        "Validate Python code, check syntax, and calculate checksums for EVE GENESIS."
    )
    args_schema: Type[BaseModel] = CodeValidatorInput

    def _run(
        self,
        action: str,
        file_path: Optional[str] = None,
        code_content: Optional[str] = None,
    ) -> str:
        try:
            if action == "validate_python":
                if file_path:
                    with open(file_path, "r", encoding="utf-8") as f:
                        code_content = f.read()

                if not code_content:
                    return "❌ No code content provided"

                try:
                    compile(code_content, "<string>", "exec")
                    return f"✅ Python code is syntactically valid"
                except SyntaxError as e:
                    return f"❌ Syntax error: {e}"

            elif action == "check_syntax":
                if not file_path:
                    return "❌ File path is required for syntax check"

                result = subprocess.run(
                    [sys.executable, "-m", "py_compile", file_path],
                    capture_output=True,
                    text=True,
                )

                if result.returncode == 0:
                    return f"✅ Syntax check passed: {file_path}"
                else:
                    return f"❌ Syntax errors in {file_path}:\n{result.stderr}"

            elif action == "calculate_checksum":
                if not file_path:
                    return "❌ File path is required for checksum calculation"

                with open(file_path, "rb") as f:
                    content = f.read()
                    md5_hash = hashlib.md5(content).hexdigest()
                    sha256_hash = hashlib.sha256(content).hexdigest()

                return f"✅ Checksums for {file_path}:\nMD5: {md5_hash}\nSHA256: {sha256_hash}"

            else:
                return f"❌ Unknown action: {action}"

        except Exception as e:
            return f"❌ Error in code validation: {str(e)}"


# ============================================================================
# EXPORT DES OUTILS POUR CREW A
# ============================================================================

CREW_A_TOOLS = [
    FileManagerTool(),
    SystemCommandTool(),
    SystemMonitorTool(),
    ConfigManagerTool(),
    CodeValidatorTool(),
]


def get_construction_tools():
    """Retourne les outils essentiels pour la construction EVE GENESIS."""
    return CREW_A_TOOLS


def get_tool_by_name(tool_name: str):
    """Récupère un outil spécifique par son nom."""
    tool_map = {tool.name: tool for tool in CREW_A_TOOLS}
    return tool_map.get(tool_name)
