from typing import Tuple, Any, List

from dependency_injector import providers


# Test 1: to check the return type (class)
provider1 = providers.List(
    providers.Factory(object),
    providers.Factory(object),
)
var1: List[Any] = provider1()


# Test 2: to check the .args attributes
provider2 = providers.List(
    providers.Factory(object),
    providers.Factory(object),
)
args2: Tuple[Any] = provider2.args

# Test 3: to check the provided instance interface
provider3 = providers.List(
    providers.Factory(object),
    providers.Factory(object),
)
provided3: List[Any] = provider3.provided()

# Test 4: to check the return type with await
provider4 = providers.List(
    providers.Factory(object),
    providers.Factory(object),
)
async def _async4() -> None:
    var1: List[Any] = await provider4()  # type: ignore
    var2: List[Any] = await provider4.async_()
