from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="agi-constitutional-framework",
    version="0.1.0",
    author="AGI Project Team",
    description="Framework de développement AGI avec audit constitutionnel",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/totodeltolosan/AGI",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Quality Assurance",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.11",
    install_requires=[
        "pyyaml>=6.0",
        "click>=8.0.0",
        "rich>=13.0.0",
    ],
    entry_points={
        "console_scripts": [
            "agi-audit=core.compliance.cli:main",
        ],
    },
)
