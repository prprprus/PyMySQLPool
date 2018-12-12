## PyMySQLPool

A pymysql-based database connection pool, simple and lightweight.

Table of content

- Features
- Requirements
- Installation
- Example
- Resources
- License

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

### Example

### Resources

### License
