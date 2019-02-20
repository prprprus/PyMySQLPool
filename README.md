# PyMySQLPool

[![build status](https://travis-ci.org/prprprus/PyMySQLPool.svg?branch=master)](hhttps://travis-ci.org/zongzhenh/PyMySQLPool.svg?branch=master) [![codecov](https://codecov.io/gh/zongzhenh/PyMySQLPool/branch/master/graph/badge.svg)](https://codecov.io/gh/zongzhenh/PyMySQLPool) [![pip version](https://img.shields.io/badge/pip-v18.1-blue.svg)](https://img.shields.io/badge/pip-v18.1-blue.svg) [![license](https://img.shields.io/dub/l/vibe-d.svg)](./LICENSE)

PyMySQLPool is a pymysql-based database connection pool, simple and lightweight.

Table of content

- [Features](https://github.com/zongzhenh/PyMySQLPool#features)
- [Requirements](https://github.com/zongzhenh/PyMySQLPool/blob/master/README.md#requirements)
- [Installation](https://github.com/zongzhenh/PyMySQLPool/blob/master/README.md#installation)
- [Example](https://github.com/zongzhenh/PyMySQLPool/blob/master/README.md#example)
- [Parameters](https://github.com/zongzhenh/PyMySQLPool/blob/master/README.md#parameters)
- [Roadmap](https://github.com/zongzhenh/PyMySQLPool/blob/master/README.md#roadmap)
- [Resources](https://github.com/zongzhenh/PyMySQLPool/blob/master/README.md#resources)
- [License](https://github.com/zongzhenh/PyMySQLPool/blob/master/README.md#license)
- [Contributing](https://github.com/zongzhenh/PyMySQLPool/blob/master/README.md#contributing)

## Features

- Maintain a minimum number of connection pools by default.
- If number of unuse connections less than zero, dynamically add connections to pool until current number of inuse connections equal maximum of pool.
- Release the idle connections in regular until number of unuse connections equal minimum of pool.

## Requirements

- Python
    - CPython : >= 3.4
- MySQL Server -- one of the following:
    - MySQL >= 5.5
    - MariaDB >= 5.5
- PyMySQL: >= 0.9.2

## Installation

Package is uploaded on [PyPI](https://pypi.org/project/pymysql-pooling/)

You can install with pip

```
$ pip install pymysql-pooling
```

## Example

Make use of a simple table (Example in [MySQL doc](https://dev.mysql.com/doc/refman/8.0/en/creating-tables.html))

```mysql
mysql> CREATE TABLE pet (name VARCHAR(20), owner VARCHAR(20),
    -> species VARCHAR(20), sex CHAR(1), birth DATE, death DATE);

mysql> INSERT INTO pet
    -> VALUES ("Puffball", "Diane", "hamster", "f", "1999-03-30", NULL);
```

```python
from pymysqlpool.pool import Pool


pool = Pool(host=HOST, port=PORT, user=USER, password=PASSWORD, db=DB)
pool.init()

connection = pool.get_conn()
cur = connection.cursor()
cur.execute('SELECT * FROM `pet` WHERE `name`=%s', args=("Puffball", ))
print(cur.fetchone())

pool.release(connection)
```

This example will print:

```
('Puffball', 'Diane', 'hamster', 'f', datetime.date(1999, 3, 30), None)
```

Support auto-commit mode, as following:

```python
pool = Pool(host=HOST, port=PORT, user=USER, password=PASSWORD, db=DB, autocommit=True)
```

That's all.

## Parameters for the pool initial:

- `host`: Host of MySQL server
- `port`: Port of MySQL server
- `user`: User of MySQL server
- `password`: Password of MySQL server
- `db`: Database of MySQL server
- `charset`: Charset of MySQL server
- `cursorclass`: Class of MySQL Cursor
- `autocommit`: auto commit mode
- `min_size`: Minimum size of connection pool
- `max_size`: Maximum size of connection pool
- `timeout`: Watting time in the multi-thread environment
- `interval`: Statistical cycle time
- `stati_mun`: Statistical frequency
- `multiple`: Regulation standard
- `counter`: Counter
- `accumulation`: Statiscal result

## Roadmap

+ [x] Connection Pool
+ [x] Dynamically Create
+ [x] Dynamically Release
+ [ ] Monitor Web Interface

## Resources

- [PyMySQL Documenation](https://pymysql.readthedocs.io/en/latest/index.html)
- [MySQL Reference Manuals](https://dev.mysql.com/doc/refman/8.0/en/)

## License

PyMySQLPool is released under the MIT License. See LICENSE for more information.

## Contributing

Thank you for your interest in contribution of PyMySQLPool, your help and contribution is very valuable. 

You can submit issue and pull requests, please submit an issue before submitting pull requests.
