from setuptools import setup
import os

VERSION = "0.1"


def get_long_description():
    with open(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "README.md"),
        encoding="utf8",
    ) as fp:
        return fp.read()


setup(
    name="download-esm",
    description="Download ESM modules from npm and jsdelivr",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    author="Simon Willison",
    url="https://github.com/simonw/download-esm",
    project_urls={
        "Issues": "https://github.com/simonw/download-esm/issues",
        "CI": "https://github.com/simonw/download-esm/actions",
        "Changelog": "https://github.com/simonw/download-esm/releases",
    },
    license="Apache License, Version 2.0",
    version=VERSION,
    packages=["download_esm"],
    entry_points="""
        [console_scripts]
        download-esm=download_esm.cli:cli
    """,
    install_requires=["click", "httpx"],
    extras_require={"test": ["pytest", "pytest-httpx"]},
    python_requires=">=3.7",
)
