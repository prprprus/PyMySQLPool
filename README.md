## PyMySQLPool

A pymysql-based database connection pool, simple and lightweight.

Table of content

- [Features](https://github.com/zongzhenh/PyMySQLPool#features)
- [Requirements](https://github.com/zongzhenh/PyMySQLPool/blob/master/README.md#requirements)
- [Installation](https://github.com/zongzhenh/PyMySQLPool/blob/master/README.md#installation)
- [Example](https://github.com/zongzhenh/PyMySQLPool/blob/master/README.md#example)
- [Resources](https://github.com/zongzhenh/PyMySQLPool/blob/master/README.md#resources)
- [License](https://github.com/zongzhenh/PyMySQLPool/blob/master/README.md#license)

### Features

- Maintain a minimum number of connection pools by default.
- If number of unuse connections less than zero, dynamically add connections to pool until current number of inuse connections equal maximum of pool.
- Release the idle connections in regular until number of unuse connections equal minimum of pool.

### Requirements

- Python -- one of the following:
    - CPython : 2.7 and >= 3.4
    - PyPy : Latest version
- MySQL Server -- one of the following:
    - MySQL >= 5.5
    - MariaDB >= 5.5
- pymysql: >= 0.94

### Installation

Package is uploaded on [PyPI](https://github.com/zongzhenh/PyMySQLPool/blob/master/README.md#pymysqlpool)

You can install with pip

```
$ python3 -m pip install PyMySQLPool
```

### Example



### Resources

### License
