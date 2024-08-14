from functools import wraps

def cached_property(func):
    """A decorator that caches the result of a method call."""

    class Descriptor:
        def __init__(self, method):
            self.method = method

        def __get__(self, instance, owner):
            if instance is None:
                return self
            result = self.method(instance)
            setattr(instance, self.method.__name__, result)
            return result

    return Descriptor(func)

def singleton(func):
    """A decorator that caches the result of a method call once."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not wrapper.complete:
            wrapper.result = func(*args, **kwargs)
            wrapper.complete = True
        return wrapper.result

    wrapper.complete = False
    wrapper.result = None
    return wrapper
