#!/usr/bin/env python3
"""
Setup configuration for the ScreenScraper.fr Python Library
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README file
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

setup(
    name="screenscraper-python",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A clean Python library for accessing retro game art and metadata from ScreenScraper.fr",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/screenscraper-python",
    packages=find_packages(),
    py_modules=["screenscraper"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Games/Entertainment",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.25.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov",
            "black",
            "flake8",
            "mypy",
        ],
        "examples": [
            "pillow",  # For image processing in examples
        ],
    },
    entry_points={
        "console_scripts": [
            "screenscraper-demo=examples:main",
        ],
    },
    keywords="retro gaming screenscraper emulation rom artwork metadata",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/screenscraper-python/issues",
        "Source": "https://github.com/yourusername/screenscraper-python",
        "Documentation": "https://github.com/yourusername/screenscraper-python/blob/main/README.md",
        "ScreenScraper.fr": "https://www.screenscraper.fr/",
    },
)

# Additional files to include in distribution
MANIFEST = """
include README.md
include LICENSE
include requirements.txt
include examples.py
recursive-include examples *.py
recursive-include docs *.md *.rst
"""

# Write MANIFEST.in file
manifest_file = Path(__file__).parent / "MANIFEST.in"
manifest_file.write_text(MANIFEST.strip())

print("Setup configuration created!")
print("\nTo install the package locally for development:")
print("  pip install -e .")
print("\nTo install with development dependencies:")
print("  pip install -e .[dev]")
print("\nTo build distribution packages:")
print("  python setup.py sdist bdist_wheel")
