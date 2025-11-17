from setuptools import setup, find_packages

setup(
    name="galex_pipeline",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "astropy",
        "numpy",
        "matplotlib",
        "reproject"
    ],
    description="Automated GALEX cropping + stacking pipeline",
    author="Your Name",
)

