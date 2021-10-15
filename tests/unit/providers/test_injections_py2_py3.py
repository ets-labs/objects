"""Dependency injector injections unit tests."""

import unittest

from dependency_injector import providers


class PositionalInjectionTests(unittest.TestCase):

    def test_isinstance(self):
        injection = providers.PositionalInjection(1)
        assert isinstance(injection, providers.Injection)

    def test_get_value_with_not_provider(self):
        injection = providers.PositionalInjection(123)
        assert injection.get_value() == 123

    def test_get_value_with_factory(self):
        injection = providers.PositionalInjection(providers.Factory(object))

        obj1 = injection.get_value()
        obj2 = injection.get_value()

        assert type(obj1) is object
        assert type(obj2) is object
        assert obj1 is not obj2

    def test_get_original_value(self):
        provider = providers.Factory(object)
        injection = providers.PositionalInjection(provider)
        assert injection.get_original_value() is provider

    def test_deepcopy(self):
        provider = providers.Factory(object)
        injection = providers.PositionalInjection(provider)

        injection_copy = providers.deepcopy(injection)

        assert injection_copy is not injection
        assert injection_copy.get_original_value() is not injection.get_original_value()

    def test_deepcopy_memo(self):
        provider = providers.Factory(object)
        injection = providers.PositionalInjection(provider)
        injection_copy_orig = providers.PositionalInjection(provider)

        injection_copy = providers.deepcopy(
            injection, {id(injection): injection_copy_orig})

        assert injection_copy is injection_copy_orig
        assert injection_copy.get_original_value() is injection.get_original_value()


class NamedInjectionTests(unittest.TestCase):

    def test_isinstance(self):
        injection = providers.NamedInjection("name", 1)
        assert isinstance(injection, providers.Injection)

    def test_get_name(self):
        injection = providers.NamedInjection("name", 123)
        assert injection.get_name() == "name"

    def test_get_value_with_not_provider(self):
        injection = providers.NamedInjection("name", 123)
        assert injection.get_value() == 123

    def test_get_value_with_factory(self):
        injection = providers.NamedInjection("name", providers.Factory(object))

        obj1 = injection.get_value()
        obj2 = injection.get_value()

        assert type(obj1) is object
        assert type(obj2) is object
        assert obj1 is not obj2

    def test_get_original_value(self):
        provider = providers.Factory(object)
        injection = providers.NamedInjection("name", provider)
        assert injection.get_original_value() is provider

    def test_deepcopy(self):
        provider = providers.Factory(object)
        injection = providers.NamedInjection("name", provider)

        injection_copy = providers.deepcopy(injection)

        assert injection_copy is not injection
        assert injection_copy.get_original_value() is not injection.get_original_value()

    def test_deepcopy_memo(self):
        provider = providers.Factory(object)
        injection = providers.NamedInjection("name", provider)
        injection_copy_orig = providers.NamedInjection("name", provider)

        injection_copy = providers.deepcopy(
            injection, {id(injection): injection_copy_orig})

        assert injection_copy is injection_copy_orig
        assert injection_copy.get_original_value() is injection.get_original_value()
