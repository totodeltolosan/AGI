#!/bin/bash
#
# Installation des alternatives à physics-engine
#

echo "🔧 Installation des dépendances physiques alternatives..."

pip install pymunk>=6.2.0 || echo "⚠️ Pymunk installation échouée"
pip install pygame>=2.1.0 || echo "⚠️ Pygame installation échouée"
pip install Box2D>=2.3.10 || echo "⚠️ Box2D installation échouée"
pip install pybullet>=3.2.4 || echo "⚠️ PyBullet installation échouée"
pip install numpy>=1.21.0 || echo "⚠️ NumPy installation échouée"
pip install scipy>=1.7.0 || echo "⚠️ SciPy installation échouée"

echo "✅ Installation des alternatives physics terminée"
