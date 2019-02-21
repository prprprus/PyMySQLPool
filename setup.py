import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pymysql-pooling",
    version="1.0.0",
    author="prprprus",
    author_email="huangzongzhuan@gmail.com",
    description="pymysql-based database connection pool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/prprprus/PyMySQLPool",
    packages=setuptools.find_packages(),
    install_requires=[
        'PyMySQL',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
