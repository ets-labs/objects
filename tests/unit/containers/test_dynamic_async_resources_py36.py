"""Dependency injector dynamic container unit tests for async resources."""
import asyncio

# Runtime import to get asyncutils module
import os
_TOP_DIR = os.path.abspath(
    os.path.sep.join((
        os.path.dirname(__file__),
        '../',
    )),
)
import sys
sys.path.append(_TOP_DIR)

from asyncutils import AsyncTestCase

from dependency_injector import (
    containers,
    providers,
)


class AsyncResourcesTest(AsyncTestCase):

    def test_init_and_shutdown_ordering(self):
        """Test init and shutdown resources.

        Methods .init_resources() and .shutdown_resources() should respect resources dependencies.
        Initialization should first initialize resources without dependencies and then provide
        these resources to other resources. Resources shutdown should follow the same rule: first
        shutdown resources without initialized dependencies and then continue correspondingly
        until all resources are shutdown.
        """
        initialized_resources = []
        shutdown_resources = []

        async def _resource(name, delay, **_):
            await asyncio.sleep(delay)
            initialized_resources.append(name)

            yield name

            await asyncio.sleep(delay)
            shutdown_resources.append(name)

        class Container(containers.DeclarativeContainer):
            resource1 = providers.Resource(
                _resource,
                name='r1',
                delay=0.03,
            )
            resource2 = providers.Resource(
                _resource,
                name='r2',
                delay=0.02,
                r1=resource1,
            )
            resource3 = providers.Resource(
                _resource,
                name='r3',
                delay=0.01,
                r2=resource2,
            )

        container = Container()

        self._run(container.init_resources())
        self.assertEqual(initialized_resources, ['r1', 'r2', 'r3'])
        self.assertEqual(shutdown_resources, [])

        self._run(container.shutdown_resources())
        self.assertEqual(initialized_resources, ['r1', 'r2', 'r3'])
        self.assertEqual(shutdown_resources, ['r1', 'r2', 'r3'])

        self._run(container.init_resources())
        self.assertEqual(initialized_resources, ['r1', 'r2', 'r3', 'r1', 'r2', 'r3'])
        self.assertEqual(shutdown_resources, ['r1', 'r2', 'r3'])

        self._run(container.shutdown_resources())
        self.assertEqual(initialized_resources, ['r1', 'r2', 'r3', 'r1', 'r2', 'r3'])
        self.assertEqual(shutdown_resources, ['r1', 'r2', 'r3', 'r1', 'r2', 'r3'])
