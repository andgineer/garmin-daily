import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

with open("requirements.dev.txt") as f:
    tests_requirements = f.read().splitlines()

from src.garmin_dayly import version

setuptools.setup(
    name="garmin-dayly",
    version=version.VERSION,
    author="Andrey Sorokin",
    author_email="andrey@sorokin.engineer",
    description=(
        "Aggregate data from Garmin Connect dayly. "
        "Also contains script to convert goodreads books to markdown files, for example for Obsidian."
    ),
    entry_points={
        "console_scripts": [
            "goodreads_csv_to_markdown=goodreads.goodreads_csv_to_markdown:main",
        ],
    },
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://andgineer.github.io/garmin-dayly/",
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    install_requires=requirements,
    tests_require=tests_requirements,
    python_requires=">=3.7",
    keywords="Garmin Connect Health goodreads book markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
