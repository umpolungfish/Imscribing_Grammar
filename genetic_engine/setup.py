"""genetic_engine — Frobenius-Guided Gene Editing via the Imscribing Grammar.

A proper Python package: genetic code = stratified Frobenius algebra on B4^3.
"""
from setuptools import setup, find_packages

setup(
    name="genetic_engine",
    version="1.0.0",
    description="Frobenius-Guided Gene Editing — genetic code as stratified Frobenius algebra",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Lando \u2297 \u2299perator",
    author_email="operator@imscribing.grammar",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[],
    extras_require={
        "test": ["pytest", "pytest-cov"],
        "dev": ["pytest", "pytest-cov", "black", "mypy"],
    },
    entry_points={
        "console_scripts": [
            "genetic-engine=genetic_engine.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Topic :: Scientific/Engineering :: Mathematics",
    ],
)
