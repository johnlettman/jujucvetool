import unittest

from jujucvetool.util import cached_property, singleton, codename_from_manifest


class TestCachedProperty(unittest.TestCase):
    def test_cached_property(self):
        class TestClass:
            def __init__(self, value):
                self._value = value
                self.call_count = 0

            @cached_property
            def value(self):
                self.call_count += 1
                return self._value

        obj = TestClass(42)

        # first access should compute the value
        self.assertEqual(obj.value, 42)
        self.assertEqual(obj.call_count, 1)

        # subsequent accesses should return the cached value without incrementing call_count
        self.assertEqual(obj.value, 42)
        self.assertEqual(obj.call_count, 1)

        # if we modify the cached value directly, the property should return the new value
        obj._value = 99
        self.assertEqual(obj.value, 42)  # Still cached at 42


class TestSingleton(unittest.TestCase):
    def test_singleton(self):
        @singleton
        def example_function(x):
            return x * 2

        # first call should compute the result
        result1 = example_function(10)
        self.assertEqual(result1, 20)

        # subsequent calls should return the cached result, regardless of input
        result2 = example_function(20)
        self.assertEqual(result2, 20)

    def test_singleton_with_different_args(self):
        @singleton
        def example_function(x, y):
            return x + y

        # first call should compute the result
        result1 = example_function(1, 2)
        self.assertEqual(result1, 3)

        # subsequent calls should return the cached result, ignoring new arguments
        result2 = example_function(2, 3)
        self.assertEqual(result2, 3)


class TestCodenameFromManifest(unittest.TestCase):
    def test_codename_from_manifest(self):
        manifest = {
            "update-manager-core": "1:20.04.10"
        }
        codename = codename_from_manifest(manifest)
        self.assertEqual(codename, "focal")

    def test_codename_from_manifest_no_match(self):
        manifest = {
            "update-manager-core": "1:19.04.1"
        }
        with self.assertRaises(Exception) as context:
            codename_from_manifest(manifest)
        self.assertIn("Could not match version to a supported release.", str(context.exception))

    def test_codename_from_manifest_missing_package(self):
        manifest = {
            "some-other-package": "1.0.0"
        }
        with self.assertRaises(Exception) as context:
            codename_from_manifest(manifest)
        self.assertIn("Failed to determine ubuntu release codename", str(context.exception))
