#!/usr/bin/env python3
"""
CHEMIN: setup.py

Rôle Fondamental (Conforme iaGOD.json) :
- Module de support.
- Ce fichier respecte la constitution AGI.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="agi-eve",
    version="0.1.0",
    author="Votre Nom",
    author_email="votre.email@example.com",
    description="AGI-EVE: Système d'Intelligence Artificielle Générale",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/VOTRE-USERNAME/VOTRE-REPO",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.9",
    install_requires=[
        "numpy>=1.21.0",
        "pandas>=1.3.0",
        "scikit-learn>=1.0.0",
        "torch>=1.12.0",
        "transformers>=4.20.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "mypy>=0.950",
        ],
    },
)
