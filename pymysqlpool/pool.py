import pymysql
from time import time
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
    :param unix_socket: Optionally, you can use a unix socket rather than TCP/IP.
    :param db: Database of MySQL server
    :param charset: Charset of MySQL server
    :param cursorclass: Class of MySQL Cursor
    :param autocommit: auto commit mode
    :param min_size: Minimum size of connection pool
    :param max_size: Maximum size of connection pool
    :param timeout: Watting time in the multi-thread environment
    :param interval: Statistical cycle time
    :param stati_mun: Statistical frequency
    :param multiple: Regulation standard
    :param counter: Counter
    :param accumulation: Statiscal result
    :param ping_check: Verify if the conn is healthy after some amount of seconds (or always, or never).
    """

    def __init__(self,
                 host="localhost",
                 port=3306,
                 user=None,
                 password=None,
                 unix_socket=None,
                 db=None,
                 charset="utf8",
                 cursorclass=pymysql.cursors.DictCursor,
                 autocommit=False,
                 min_size=1,
                 max_size=3,
                 timeout=10.0,
                 interval=600.0,
                 stati_num=3,
                 multiple=4,
                 counter=0,
                 accumulation=0,
                 ping_check: (int, bool) = False,
                 **configs):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.db = db
        self.charset = charset
        self.cursorclass = cursorclass
        self.autocommit = autocommit

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
        self.ping_check = ping_check

        self.unix_socket=unix_socket
        self.configs=configs

    def create_conn(self):
        """Create mysql connection by pymysql and to add unuse_list"""
        c = pymysql.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            db=self.db,
            charset=self.charset,
            cursorclass=self.cursorclass,
            autocommit=self.autocommit,
            unix_socket=self.unix_socket,
            **self.configs
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
            return self.__get_conn()

    def __get_conn(self, retry_count=0):
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

        return self.__get_safe_conn(retry_count)

    def __get_safe_conn(self, retry_count):
        self.current_size += 1
        c = self.unuse_list.pop()
        if self.ping_check:
            now = int(time())
            timeout = now
            if isinstance(self.ping_check, int):
                timeout = timeout - self.ping_check
            if not hasattr(c, '__ping_check_timestamp'):
                c.__ping_check_timestamp = now
            try:
                if c.__ping_check_timestamp < timeout:
                    c.__ping_check_timestamp = now
                    c.ping()
            except:
                self.current_size -= 1
                if retry_count < 10: c = self.__get_conn(retry_count+1)
        if c: self.inuse_list.add(c)
        return c

    def get_pool_size(self):
        """Get current pool size"""
        return self.current_size

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
