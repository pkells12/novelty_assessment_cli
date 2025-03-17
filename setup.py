from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="patent-novelty-analyzer",
    version="0.1.0",
    author="",
    author_email="",
    description="A CLI tool for analyzing patent novelty against existing patents and products",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
    install_requires=[
        "python-dotenv==1.0.0",
        "requests==2.31.0",
        "anthropic==0.7.4",
        "click==8.1.3",
        "rich==13.3.5",
        "pyyaml==6.0.1",
        "tenacity==8.2.2",
        "google-search-results==2.4.2",
    ],
    entry_points={
        "console_scripts": [
            "patent-novelty-analyzer=novelty_assessment_cli.__main__:main",
        ],
    },
) 