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