from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("req/requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="BOLAFuzz",
    version="1.0.0",
    author="BOLAFuzz Team",
    author_email="contact@bolafuzz.com",
    description="A professional web application security testing tool for detecting BOLA/IDOR vulnerabilities",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/BOLAFuzz/BOLAFuzz",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Security",
        "Topic :: Software Development :: Testing",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "bolafuzz=main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["data/dictionaries/*.txt", "data/models/*.pth", "crawler/bin/*"],
    },
)
