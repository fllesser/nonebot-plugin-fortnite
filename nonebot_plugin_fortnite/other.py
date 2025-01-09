from functools import wraps

def exception_handler():
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            res = None
            try:
                res = await func(*args, **kwargs)
            except Exception as e:
                e = str(e)
                if "public" in e:
                    res = "战绩未公开"
                elif "exist" in e:
                    res = "用户不存在"
                elif "match" in e:
                    res = "该玩家当前赛季没有进行过任何对局"
                elif "timed out" in e:
                    res = "请求超时, 请稍后再试"
                elif "failed to fetch" in e:
                    res = "拉取账户信息失败, 稍后再试"
                else:
                    res = f"未知错误: {e}"
            finally:
                return res
        return wrapper
    return decorator
