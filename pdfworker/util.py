#!/usr/bin/env python

# standard library imports
from contextlib import contextmanager
import signal

# third party related imports

# local library imports


class TimeLimitException(Exception): pass


@contextmanager
def time_limit(seconds):
    """Limit function execution time.

    >>> try:
            with time_limit(10):
                long_function_call()
        except TimeoutException:
            print "Timeout"
    >>>

    Args:
        seconds: An integer indicating how long limit the function
            execution time.

    """

    def signal_handler(signum, frame):
        raise TimeLimitException("timeout")

    signal.signal(signal.SIGALRM, signal_handler)
    signal.alarm(seconds)

    try:
        yield
    finally:
        signal.alarm(0)

