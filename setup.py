from setuptools import setup, find_packages

setup(
    name="agi-eve",
    version="1.0.0",
    author="Toni",
    description="Écosystème AGI-EVE unifié",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.11",
    install_requires=[
        "numpy",
        "pandas", 
        "scipy",
        "matplotlib",
        "tkinter",
        "PyQt6"
    ],
)
