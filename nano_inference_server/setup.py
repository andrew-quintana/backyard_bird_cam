from setuptools import setup, find_packages

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="nano_inference_server",
    version="0.1.0",
    description="Bird detection inference server for Jetson Nano",
    author="Backyard Bird Cam Team",
    packages=find_packages(),
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'nano-inference=nano_inference_server.main:main',
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    python_requires='>=3.6',
) 