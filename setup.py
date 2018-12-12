import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="PyMySQLPool_zongzhenh",
    version="0.9.1",
    author="Tiger",
    author_email="huangzongzhuan@gmail.com",
    description="Simple connection pool for pymysql",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/zongzhenh/pymysql-pool",
    packages=setuptools.find_packages(exclude=['tests*', ]),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
