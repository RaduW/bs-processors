import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="bs-processors",
    version="0.0.1pre03",
    author="RaduW",
    description="html/xml processors for using with BeautifulSoup",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=" https://github.com/RaduW/bs-processors.git",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries"
    ],
    keywords ="BeautifulSoup",
    python_requires=">=3.7",
    license="MIT",
    package_dir={"": "src"},
    packages=setuptools.find_namespace_packages(where="src"),
)
