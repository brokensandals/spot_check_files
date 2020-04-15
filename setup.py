import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="spot_check_files",
    version="0.0.1",
    author="Jacob Williams",
    author_email="jacobaw@gmail.com",
    description="Helps validate the integrity of data backups/exports.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/brokensandals/spot_check_files",
    packages=setuptools.find_packages('src'),
    package_dir={'':'src'},
    entry_points={
        'console_scripts': [
            'spot_check_files = spot_check_files.cli:main'
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: MacOS :: MacOS X",
    ],
    install_requires=[
    ],
    python_requires='>=3.7',
)
