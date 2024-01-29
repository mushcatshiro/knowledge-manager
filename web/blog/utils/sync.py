from contextlib import contextmanager
from threading import Lock


class RWLock:
    """RWLock class; this is meant to allow an object to be read from by
    multiple threads, but only written to by a single thread at a time. See:
    https://en.wikipedia.org/wiki/Readers%E2%80%93writer_lock
    Usage:
        from rwlock import RWLock
        my_obj_rwlock = RWLock()
        # When reading from my_obj:
        with my_obj_rwlock.r_locked():
            do_read_only_things_with(my_obj)
        # When writing to my_obj:
        with my_obj_rwlock.w_locked():
            mutate(my_obj)
    """

    def __init__(self):

        self.w_lock = Lock()
        self.num_r_lock: Lock = Lock()
        self.num_r = 0

    def r_acquire(self):
        with self.num_r_lock:
            self.num_r += 1
            if self.num_r == 1:
                with self.w_lock:
                    pass

    def r_release(self):
        assert self.num_r > 0
        with self.num_r_lock:
            self.num_r -= 1
            if self.num_r == 0:
                self.w_lock.release()

    @contextmanager
    def r_locked(self):
        """This method is designed to be used via the `with` statement."""
        try:
            self.r_acquire()
            yield
        finally:
            self.r_release()

    def w_acquire(self):
        with self.w_lock:
            pass

    def w_release(self):
        self.w_lock.release()

    @contextmanager
    def w_locked(self):
        """This method is designed to be used via the `with` statement."""
        try:
            self.w_acquire()
            yield
        finally:
            self.w_release()
