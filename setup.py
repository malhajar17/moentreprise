"""
Moentreprise - AI-Powered Business Automation Platform
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="moentreprise",
    version="1.0.0",
    author="Mo and the legml.ai team",
    author_email="support@legml.ai",
    description="AI-powered business automation platform with real-time voice interaction",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/moentreprise",
    project_urls={
        "Bug Tracker": "https://github.com/yourusername/moentreprise/issues",
        "Documentation": "https://github.com/yourusername/moentreprise/docs",
        "Source Code": "https://github.com/yourusername/moentreprise",
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Business",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Office/Business :: Financial :: Investment",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Multimedia :: Sound/Audio :: Speech",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "pytest-asyncio>=0.20.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=0.990",
            "sphinx>=5.0.0",
            "sphinx-rtd-theme>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "moentreprise=examples.web_demo:main",
        ],
    },
    include_package_data=True,
    package_data={
        "moentreprise": [
            "resources/*.png",
            "resources/*.jpg",
            "templates/*.html",
            "static/*.css",
            "static/*.js",
        ],
    },
    keywords=[
        "ai",
        "automation",
        "business",
        "openai",
        "realtime",
        "voice",
        "linkedin",
        "marketing",
        "web development",
        "orchestration",
    ],
) 