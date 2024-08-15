import re
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


def codename_from_manifest(installed_pkgs):
    """Updated codename function to support newer Ubuntu releases."""
    try:
        ubuntu_releases = {
            r"1:0.196(.\d+)+": "trusty",
            r"1:16.04(.\d+)+": "xenial",
            r"1:18.04(.\d+)+": "bionic",
            r"1:20.04(.\d+)+": "focal",
            r"1:20.10(.\d+)+": "groovy",
            r"1:21.04(.\d+)+": "hirsute",
            r"1:21.10(.\d+)+": "impish",
            r"1:22.04(.\d+)+": "jammy",
            r"1:22.10(.\d+)+": "kinetic",
            r"1:23.04(.\d+)+": "lunar",
        }

        update_manager_core_ver = installed_pkgs.get("update-manager-core", "")

        for pattern, codename in ubuntu_releases.items():
            if re.match(pattern, update_manager_core_ver):
                return codename

        raise Exception("Could not match version to a supported release.")
    except Exception as e:
        raise Exception(
            "Failed to determine ubuntu release codename from the provided "
            "manifest file: %s" % e
        )
