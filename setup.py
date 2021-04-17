from os import path
from setuptools import setup, find_packages

this_directory = path.dirname(__file__)
with open(path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()


setup(
    name="targon",
    packages=find_packages(),
    package_data={"": ["*.sav", "*.json"],},
    version="0.0.1a2",
    install_requires=["pantheon","sortedcontainers"],
    description="Library for Riot API crawlers",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Canisback",
    author_email="canisback@gmail.com",
    url="https://github.com/Canisback/targon",
    keywords=["Riot API", "python", "League of Legends"],
    classifiers=[]
)
