import pymysql
from threading import Thread, Lock, Condition, Timer


class Error(Exception):
    """Base class for all pool-related exceptions"""
    pass


class TimeoutError(Error):
    """The operation exceeded the given deadline"""
    pass


def resize_pool(interval=600.0, stati_num=3, multiple=4, counter=0,
                accumulation=0, pool=None):
    """Resize connection pool in cycle"""
    assert (pool is not None)
    with pool.lock:
        if counter >= stati_num:
            avg = accumulation / stati_num
            if avg >= multiple:
                num = len(pool.unuse_list) - pool.min_size
                for _ in range(num):
                    c = pool.unuse_list.pop()
                    c.close()
            counter = 0
            accumulation = 0
        else:
            accumulation += (len(pool.unuse_list) + 1) / (len(pool.inuse_list) + 1)
            counter += 1
    t = Timer(interval, resize_pool, args=(interval, stati_num, multiple,
                                           counter, accumulation, pool))
    t.start()


class Pool(object):
    """
    Connection pool for pymysql.

    The initialization parameters are as follows:
    :param host: Host of MySQL server
    :param port: Port of MySQL server
    :param user: User of MySQL server
    :param password: Password of MySQL server
    :param db: Database of MySQL server
    :param charset: Charset of MySQL server
    :param min_size: Minimum size of connection pool
    :param max_size: Maximum size of connection pool
    :param timeout: Watting time in the multi-thread environment
    :param interval: Statistical cycle time
    :param stati_mun: Statistical frequency
    :param multiple: Regulation standard
    :param counter: Counter
    :param accumulation: Statiscal result
    """

    def __init__(self, host='localhost', port=3306, user='root',
                 password=None, db=None, charset='utf8',
                 min_size=1, max_size=1, timeout=10.0,
                 interval=600.0, stati_num=3, multiple=4,
                 counter=0, accumulation=0):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.db = db
        self.charset = charset

        self.min_size = min_size
        self.max_size = max_size
        self.current_size = 0
        self.timeout = timeout

        self.unuse_list = set()
        self.inuse_list = set()
        self.lock = Lock()
        self.cond = Condition(self.lock)

        self.interval = interval
        self.stati_num = stati_num
        self.multiple = multiple
        self.counter = 0
        self.accumulation = 0

    def create_conn(self):
        """Create mysql connection by pymysql and to add unuse_list"""
        c = pymysql.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            db=self.db,
            charset=self.charset
        )
        self.unuse_list.add(c)

    def _start(self):
        """Start thread for resize pool"""
        t = Thread(target=resize_pool, args=(self.interval, self.stati_num,
                                             self.multiple, self.counter,
                                             self.accumulation, self))
        t.start()

    def _init_pool(self):
        """Initial minimum size of pool"""
        assert (self.min_size <= self.max_size)
        for _ in range(self.min_size):
            self.create_conn()

    def init(self):
        self._init_pool()
        self._start()

    def _wait(self):
        """Waiting condition"""
        return len(self.unuse_list) > 0

    def get_conn(self):
        with self.cond:
            # Lack of resources and wait
            if len(self.unuse_list) <= 0 and \
                    self.current_size >= self.max_size:
                # note: TimeoutError mean release operation exception
                # or max_size much less than concurrence
                self.cond.wait_for(self._wait, self.timeout)
                if len(self.unuse_list) <= 0:
                    raise TimeoutError
            # Lack of resources but can created
            if len(self.unuse_list) <= 0 and \
                    self.current_size < self.max_size:
                self.create_conn()

            self.current_size += 1
            c = self.unuse_list.pop()
            self.inuse_list.add(c)
            return c

    def release(self, c):
        """Release connection from inuse_list to unuse_list"""
        with self.cond:
            self.current_size -= 1
            self.inuse_list.remove(c)
            self.unuse_list.add(c)
            self.cond.notify_all()

    def destroy(self):
        """Destroy pool"""
        for _ in range(len(self.unuse_list)):
            c = self.unuse_list.pop()
            c.close()
        for _ in range(len(self.inuse_list)):
            c = self.inuse_list.pop()
            c.close()
