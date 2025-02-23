from setuptools import setup, find_packages

setup(
    name="squad_goals",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "dotenv",
        "pydantic",
        "requests",
        "beautifulsoup4",
    ],
)
