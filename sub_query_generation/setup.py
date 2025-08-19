"""
Setup script for the sub-query generation package.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

# Read requirements
requirements_path = Path(__file__).parent / "requirements.txt"
if requirements_path.exists():
    with open(requirements_path) as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]
else:
    requirements = ["pyyaml>=6.0", "requests>=2.28.0"]

setup(
    name="sub-query-generation",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Generate multiple sub-queries for improved RAG performance",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/sub-query-generation",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Text Processing :: Linguistic",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pyyaml>=6.0",
        "requests>=2.28.0",
    ],
    extras_require={
        "huggingface": [
            "transformers>=4.30.0",
            "torch>=2.0.0",
            "accelerate>=0.20.0",
            "bitsandbytes>=0.39.0",
        ],
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "sub-query-gen=sub_query_generation.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "sub_query_generation": ["*.yaml", "*.yml"],
    },
)