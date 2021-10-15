"""Dependency injector coroutine providers unit tests."""

import asyncio
import unittest
import warnings

from dependency_injector import (
    providers,
    errors,
)
from pytest import raises

# Runtime import to get asyncutils module
import os
_TOP_DIR = os.path.abspath(
    os.path.sep.join((
        os.path.dirname(__file__),
        "../",
    )),
)
import sys
sys.path.append(_TOP_DIR)

from asyncutils import AsyncTestCase


async def _example(arg1, arg2, arg3, arg4):
    future = asyncio.Future()
    future.set_result(None)
    await future
    return arg1, arg2, arg3, arg4


def run(main):
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(main)


class CoroutineTests(AsyncTestCase):

    def test_init_with_coroutine(self):
        assert isinstance(providers.Coroutine(_example), providers.Coroutine)

    def test_init_with_not_coroutine(self):
        with raises(errors.Error):
            providers.Coroutine(lambda: None)

    def test_init_optional_provides(self):
        provider = providers.Coroutine()
        provider.set_provides(_example)
        assert provider.provides is _example
        assert run(provider(1, 2, 3, 4)) == (1, 2, 3, 4)

    def test_set_provides_returns_self(self):
        provider = providers.Coroutine()
        assert provider.set_provides(_example) is provider

    def test_call_with_positional_args(self):
        provider = providers.Coroutine(_example, 1, 2, 3, 4)
        assert self._run(provider()) == (1, 2, 3, 4)

    def test_call_with_keyword_args(self):
        provider = providers.Coroutine(_example, arg1=1, arg2=2, arg3=3, arg4=4)
        assert self._run(provider()) == (1, 2, 3, 4)

    def test_call_with_positional_and_keyword_args(self):
        provider = providers.Coroutine(_example, 1, 2, arg3=3, arg4=4)
        assert run(provider()) == (1, 2, 3, 4)

    def test_call_with_context_args(self):
        provider = providers.Coroutine(_example, 1, 2)
        assert self._run(provider(3, 4)) == (1, 2, 3, 4)

    def test_call_with_context_kwargs(self):
        provider = providers.Coroutine(_example, arg1=1)
        assert self._run(provider(arg2=2, arg3=3, arg4=4)) == (1, 2, 3, 4)

    def test_call_with_context_args_and_kwargs(self):
        provider = providers.Coroutine(_example, 1)
        assert self._run(provider(2, arg3=3, arg4=4)) == (1, 2, 3, 4)

    def test_fluent_interface(self):
        provider = providers.Coroutine(_example) \
            .add_args(1, 2) \
            .add_kwargs(arg3=3, arg4=4)
        assert self._run(provider()) == (1, 2, 3, 4)

    def test_set_args(self):
        provider = providers.Coroutine(_example) \
            .add_args(1, 2) \
            .set_args(3, 4)
        assert provider.args == (3, 4)

    def test_set_kwargs(self):
        provider = providers.Coroutine(_example) \
            .add_kwargs(init_arg3=3, init_arg4=4) \
            .set_kwargs(init_arg3=4, init_arg4=5)
        assert provider.kwargs == dict(init_arg3=4, init_arg4=5)

    def test_clear_args(self):
        provider = providers.Coroutine(_example) \
            .add_args(1, 2) \
            .clear_args()
        assert provider.args == tuple()

    def test_clear_kwargs(self):
        provider = providers.Coroutine(_example) \
            .add_kwargs(init_arg3=3, init_arg4=4) \
            .clear_kwargs()
        assert provider.kwargs == dict()

    def test_call_overridden(self):
        provider = providers.Coroutine(_example)

        provider.override(providers.Object((4, 3, 2, 1)))
        provider.override(providers.Object((1, 2, 3, 4)))

        assert provider() == (1, 2, 3, 4)

    def test_deepcopy(self):
        provider = providers.Coroutine(_example)

        provider_copy = providers.deepcopy(provider)

        assert provider is not provider_copy
        assert provider.provides is provider_copy.provides
        assert isinstance(provider, providers.Coroutine)

    def test_deepcopy_from_memo(self):
        provider = providers.Coroutine(_example)
        provider_copy_memo = providers.Coroutine(_example)

        provider_copy = providers.deepcopy(
            provider, memo={id(provider): provider_copy_memo})

        assert provider_copy is provider_copy_memo

    def test_deepcopy_args(self):
        provider = providers.Coroutine(_example)
        dependent_provider1 = providers.Callable(list)
        dependent_provider2 = providers.Callable(dict)

        provider.add_args(dependent_provider1, dependent_provider2)

        provider_copy = providers.deepcopy(provider)
        dependent_provider_copy1 = provider_copy.args[0]
        dependent_provider_copy2 = provider_copy.args[1]

        assert provider.args != provider_copy.args

        assert dependent_provider1.provides is dependent_provider_copy1.provides
        assert dependent_provider1 is not dependent_provider_copy1

        assert dependent_provider2.provides is dependent_provider_copy2.provides
        assert dependent_provider2 is not dependent_provider_copy2

    def test_deepcopy_kwargs(self):
        provider = providers.Coroutine(_example)
        dependent_provider1 = providers.Callable(list)
        dependent_provider2 = providers.Callable(dict)

        provider.add_kwargs(a1=dependent_provider1, a2=dependent_provider2)

        provider_copy = providers.deepcopy(provider)
        dependent_provider_copy1 = provider_copy.kwargs["a1"]
        dependent_provider_copy2 = provider_copy.kwargs["a2"]

        assert provider.kwargs != provider_copy.kwargs

        assert dependent_provider1.provides is dependent_provider_copy1.provides
        assert dependent_provider1 is not dependent_provider_copy1

        assert dependent_provider2.provides is dependent_provider_copy2.provides
        assert dependent_provider2 is not dependent_provider_copy2

    def test_deepcopy_overridden(self):
        provider = providers.Coroutine(_example)
        object_provider = providers.Object(object())

        provider.override(object_provider)

        provider_copy = providers.deepcopy(provider)
        object_provider_copy = provider_copy.overridden[0]

        assert provider is not provider_copy
        assert provider.provides is provider_copy.provides
        assert isinstance(provider, providers.Callable)

        assert object_provider is not object_provider_copy
        assert isinstance(object_provider_copy, providers.Object)

    def test_repr(self):
        provider = providers.Coroutine(_example)

        assert repr(provider) == (
            "<dependency_injector.providers."
            "Coroutine({0}) at {1}>".format(repr(_example), hex(id(provider)))
        )


class DelegatedCoroutineTests(unittest.TestCase):

    def test_inheritance(self):
        assert isinstance(providers.DelegatedCoroutine(_example),
                              providers.Coroutine)

    def test_is_provider(self):
        assert providers.is_provider(providers.DelegatedCoroutine(_example)) is True

    def test_is_delegated_provider(self):
        provider = providers.DelegatedCoroutine(_example)
        assert providers.is_delegated(provider) is True

    def test_repr(self):
        provider = providers.DelegatedCoroutine(_example)

        assert repr(provider) == (
            "<dependency_injector.providers."
            "DelegatedCoroutine({0}) at {1}>".format(repr(_example), hex(id(provider)))
        )


class AbstractCoroutineTests(AsyncTestCase):

    def test_inheritance(self):
        assert isinstance(providers.AbstractCoroutine(_example),
                              providers.Coroutine)

    def test_call_overridden_by_coroutine(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")

            @asyncio.coroutine
            def _abstract_example():
                raise RuntimeError("Should not be raised")

        provider = providers.AbstractCoroutine(_abstract_example)
        provider.override(providers.Coroutine(_example))

        assert self._run(provider(1, 2, 3, 4)) == (1, 2, 3, 4)

    def test_call_overridden_by_delegated_coroutine(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")

            @asyncio.coroutine
            def _abstract_example():
                raise RuntimeError("Should not be raised")

        provider = providers.AbstractCoroutine(_abstract_example)
        provider.override(providers.DelegatedCoroutine(_example))

        assert self._run(provider(1, 2, 3, 4)) == (1, 2, 3, 4)

    def test_call_not_overridden(self):
        provider = providers.AbstractCoroutine(_example)

        with raises(errors.Error):
            provider(1, 2, 3, 4)

    def test_override_by_not_coroutine(self):
        provider = providers.AbstractCoroutine(_example)

        with raises(errors.Error):
            provider.override(providers.Factory(object))

    def test_provide_not_implemented(self):
        provider = providers.AbstractCoroutine(_example)

        with raises(NotImplementedError):
            provider._provide((1, 2, 3, 4), dict())

    def test_repr(self):
        provider = providers.AbstractCoroutine(_example)

        assert repr(provider) == (
            "<dependency_injector.providers."
            "AbstractCoroutine({0}) at {1}>".format(repr(_example), hex(id(provider)))
        )


class CoroutineDelegateTests(unittest.TestCase):

    def setUp(self):
        self.delegated = providers.Coroutine(_example)
        self.delegate = providers.CoroutineDelegate(self.delegated)

    def test_is_delegate(self):
        assert isinstance(self.delegate, providers.Delegate)

    def test_init_with_not_callable(self):
        with raises(errors.Error):
            providers.CoroutineDelegate(providers.Object(object()))
