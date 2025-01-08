from functools import wraps

def exception_handler():
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            res = None
            try:
                res = await func(*args, **kwargs)
            except Exception as e:
                res = str(e)  # 使用 str(e) 而不是 e.message
            finally:
                return res
        return wrapper
    return decorator
