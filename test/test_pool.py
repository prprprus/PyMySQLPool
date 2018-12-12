import unittest
from unittest.mock import patch
from pymysqlpool import pool
from threading import Thread


class MockMySQLConnection(object):

    def __init__(self, host='localhost', port=3306, user='root',
                 password='None', db='None', charset='utf8'):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.db = db
        self.charset = charset

    def close(self):
        return 'Mock pymysql close method.'


# mock method of pool
def mock_create_conn(self):
    c = MockMySQLConnection()
    self.unuse_list.add(c)


def mock__init_pool(self):
    assert (self.min_size <= self.max_size)
    for _ in range(self.min_size):
        mock_create_conn(self)


def mock__start(self):
    pass


# test case
class TestPool(unittest.TestCase):

    def setUp(self):
        self.concurrence = 1000
        # unequal pre
        self.p = pool.Pool(min_size=10, max_size=90, timeout=10.0)

    def tearDown(self):
        pass

    @patch.object(pool.Pool, 'create_conn', new=mock_create_conn)
    def test_create_conn(self):
        assert (mock_create_conn == pool.Pool.create_conn)
        self.p.create_conn()
        assert (len(self.p.unuse_list) == 1)
        assert (filter(lambda x: isinstance(x, MockMySQLConnection), self.p.unuse_list))

    @patch.object(pool.Pool, 'create_conn', new=mock_create_conn)
    @patch.object(pool.Pool, '_init_pool', new=mock__init_pool)
    @patch.object(pool.Pool, '_start', new=mock__start)
    def test_init(self):
        self.p.init()
        assert (len(self.p.unuse_list) == self.p.min_size)

    @patch.object(pool.Pool, 'create_conn', new=mock_create_conn)
    @patch.object(pool.Pool, '_init_pool', new=mock__init_pool)
    @patch.object(pool.Pool, '_start', new=mock__start)
    def test_get_conn(self):
        self.p.init()
        c = self.p.get_conn()
        assert (isinstance(c, MockMySQLConnection))
        assert (len(self.p.unuse_list) == self.p.min_size - 1)
        assert (len(self.p.inuse_list) == 1)
        assert (filter(lambda x: isinstance(x, MockMySQLConnection), self.p.unuse_list))
        assert (filter(lambda x: isinstance(x, MockMySQLConnection), self.p.inuse_list))

    @patch.object(pool.Pool, 'create_conn', new=mock_create_conn)
    @patch.object(pool.Pool, '_init_pool', new=mock__init_pool)
    @patch.object(pool.Pool, '_start', new=mock__start)
    def test_release(self):
        self.p.init()
        c = self.p.get_conn()
        self.p.release(c)
        assert (len(self.p.unuse_list) == self.p.min_size)
        assert (len(self.p.inuse_list) == 0)

    @patch.object(pool.Pool, 'create_conn', new=mock_create_conn)
    @patch.object(pool.Pool, '_init_pool', new=mock__init_pool)
    @patch.object(pool.Pool, '_start', new=mock__start)
    def test_destroy(self):
        self.p.init()
        self.p.inuse_list.add(MockMySQLConnection())
        self.p.destroy()
        assert (len(self.p.unuse_list) == 0)
        assert (len(self.p.inuse_list) == 0)

    @patch.object(pool.Pool, 'create_conn', new=mock_create_conn)
    @patch.object(pool.Pool, '_init_pool', new=mock__init_pool)
    @patch.object(pool.Pool, '_start', new=mock__start)
    def pure_get_and_release(self):
        c = self.p.get_conn()
        self.p.release(c)

    @patch.object(pool.Pool, 'create_conn', new=mock_create_conn)
    @patch.object(pool.Pool, '_init_pool', new=mock__init_pool)
    @patch.object(pool.Pool, '_start', new=mock__start)
    def test_get_conn_by_concurrence(self):
        self.p.init()
        for i in range(self.concurrence):
            t = Thread(target=self.pure_get_and_release)
            t.start()
        assert (len(self.p.unuse_list) == self.p.min_size)
        assert (len(self.p.inuse_list) == 0)
        assert (filter(lambda x: isinstance(x, MockMySQLConnection), self.p.unuse_list))


if __name__ == '__main__':
    unittest.main(verbosity=2)
