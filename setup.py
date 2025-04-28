#!/usr/bin/env python3
"""
Setup script for the Chatbot Application.
"""

from setuptools import setup, find_packages

setup(
    name="chatbot_app",
    version="1.0.0",
    description="A Flask-based chatbot application with emotion detection",
    author="Admin123",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "flask>=2.2.5",
        "flask-sqlalchemy==3.1.1",
        "flask-migrate==4.0.5",
        "flask-cors==4.0.0",
        "python-dotenv==0.19.0",
        "pytest==8.0.2",
        "gunicorn==21.2.0",
    ],
    entry_points={
        "console_scripts": [
            "chatbot=chatbot_app.__main__:main",
        ],
    },
    python_requires=">=3.6,<=3.13",
)
