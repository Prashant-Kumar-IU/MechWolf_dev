from os import path

from setuptools import find_packages, setup

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, "README.md")) as f:
    long_description = f.read()

with open("requirements.txt", "r", encoding="utf-8") as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="mechwolf",
    version="2.0.0",
    description="Enhanced flow chemistry automation platform with improved Flow Setups module",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Prashant-Kumar-IU/MechWolf_dev",
    author="Benjamin Lee, Alex Mijalis, Prashant Kumar, Nicola Pohl",
    author_email="pprashan@iu.edu",
    maintainer="Prashant Kumar",
    maintainer_email="pprashan@iu.edu",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Healthcare Industry",
        "Intended Audience :: Manufacturing",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Chemistry",
        "Topic :: Scientific/Engineering :: Visualization",
    ],
    keywords="flow chemistry, automation, microfluidics, synthetic chemistry, laboratory automation",
    python_requires=">=3.7",
    packages=find_packages(),
    tests_require=["pytest"],
    setup_requires=["pytest-runner"],
    install_requires=requirements,
    extras_require={
        "dev": [
            "black",
            "flake8",
            "isort",
            "mypy",
            "pipdeptree",
            "pipreqs",
            "pre-commit",
            "pytest",
            "zest.releaser",
        ],
        "chemistry": [
            "rdkit>=2020.09.1",
        ],
    },
    include_package_data=True,
    package_data={
        "mechwolf": [
            "**/*.md", 
            "**/*.json", 
            "**/*.html",
            "DataEntry/FlowSetups/docs/*",
            "DataEntry/FlowSetups/README*.md",
        ],
    },
)
