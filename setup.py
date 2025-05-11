"""Setup script for the Bird Camera project."""
from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("requirements.txt", "r") as f:
    requirements = f.read().splitlines()

setup(
    name="bird_cam",
    version="1.0.0",
    author="Bird Camera Project",
    author_email="sendaqmail@gmail.com",
    description="A Raspberry Pi-based camera system for bird photography",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/username/bird_cam",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "bird_cam=src.main:main",
        ],
    },
) 