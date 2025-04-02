from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="tronzap-sdk",
    version="1.0.0",
    author="Tron Energy Market",
    author_email="support@tronzap.com",
    description="Official Python SDK for TronZap.com API. The API lets you buy TRON energy to lower USDT (TRC20) transfer fees.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://tronzap.com",
    project_urls={
        "Bug Tracker": "https://github.com/tron-energy-market/tronzap-sdk-python/issues",
        "Source Code": "https://github.com/tron-energy-market/tronzap-sdk-python",
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.25.0",
    ],
    keywords=[
        "TronZap",
        "Tron",
        "Trx",
        "Tron API",
        "Trx API",
        "TRX energy",
        "TRON energy api",
        "buy trx energy",
        "buy tron energy",
        "trx energy market",
        "tron energy market",
        "USDT",
        "TRC20",
        "TRC-20",
        "cryptocurrency",
        "blockchain",
        "crypto transfers"
    ],
)