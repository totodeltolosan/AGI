"""
DASHBOARD CORE - Architecture modulaire constitutionnelle AGI
Modules délégués conformes à la directive des 200 lignes maximum.
"""

from .constitutional_collector import ConstitutionalDataCollector
from .git_collector import GitDataCollector
from .template_manager import TemplateManager
from .chart_generator import ChartGenerator
from .dashboard_orchestrator import DashboardOrchestrator

__all__ = [
    'ConstitutionalDataCollector',
    'GitDataCollector', 
    'TemplateManager',
    'ChartGenerator',
    'DashboardOrchestrator'
]

__version__ = "3.0.0"
__author__ = "AGI Constitutional Architecture"
