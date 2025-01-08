from functools import wraps

def exception_handler():
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            res = None
            try:
                res = func(*args, **kwargs)
            except Exception as e:
                res = e.message
            finally:
                return res
        return wrapper
    return decorator

