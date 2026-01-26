from typing import Callable, Any, TypeAlias

Executor: TypeAlias = Callable[
    [str, str, float],
    tuple[dict[str, Any], dict[str, Any]]
]