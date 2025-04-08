from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="tronzap-sdk",
    version="1.0.2",
    description="Official Python SDK for the Tron Energy API by TronZap.com. Buy Tron energy for cheap USDT transfers on TronZap.com",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Tron Energy Market",
    author_email="support@tronzap.com",
    url="https://tronzap.com",
    project_urls={
        "Homepage": "https://tronzap.com",
        "Documentation": "https://docs.tronzap.com/",
        "Bug Tracker": "https://github.com/tron-energy-market/tronzap-sdk-python/issues",
        "Source Code": "https://github.com/tron-energy-market/tronzap-sdk-python",
        "Buy Tron Energy": "https://tronzap.com",
        "Support": "https://t.me/tronzap_bot"
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3"
    ],
    license="MIT",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3",
    install_requires=[
        "requests>=2.25.0"
    ],
    keywords=[
        "TronZap",
        "Tron",
        "Trx",
        "Tron API",
        "Trx API",
        "TRX energy",
        "Tron energy",
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
