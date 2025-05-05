# Logging, retry, and utility decorators

import functools
import time

def retry(times: int = 3, delay: float = 1.0):
    """
    Retry decorator to retry a function call on failure.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(times):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt < times - 1:
                        time.sleep(delay)
                    else:
                        raise e
        return wrapper
    return decorator

def log_execution(func):
    """
    Simple logging decorator to track function calls.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print(f"[LOG] Calling {func.__name__}")
        result = func(*args, **kwargs)
        print(f"[LOG] Finished {func.__name__}")
        return result
    return wrapper
