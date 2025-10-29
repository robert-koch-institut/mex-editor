import datetime
import inspect
from collections.abc import Callable
from typing import Any

from reflex.utils import types
from reflex.utils.exceptions import (
    ComputedVarSignatureError,
    VarDependencyError,
)
from reflex.vars.base import AsyncComputedVar, ComputedVar, Var

from mex.editor.locale_service import LocaleService
from mex.editor.state import State

locale_service = LocaleService.get()


def localized_label_var(
    fget: Callable[[State], Any] | None = None,
    label_id: str = "",
    initial_value: Any | types.Unset = types.Unset(),
    cache: bool = True,
    deps: list[str | Var] | None = None,
    auto_deps: bool = True,
    interval: datetime.timedelta | int | None = None,
    backend: bool | None = None,
    **kwargs,
) -> ComputedVar | Callable[[Callable[[State], Any]], ComputedVar]:
    """A ComputedVar decorator with or without kwargs.

    Args:
        fget: The getter function.
        initial_value: The initial value of the computed var.
        cache: Whether to cache the computed value.
        deps: Explicit var dependencies to track.
        auto_deps: Whether var dependencies should be auto-determined.
        interval: Interval at which the computed var should be updated.
        backend: Whether the computed var is a backend var.
        **kwargs: additional attributes to set on the instance

    Returns:
        A ComputedVar instance.

    Raises:
        ValueError: If caching is disabled and an update interval is set.
        VarDependencyError: If user supplies dependencies without caching.
        ComputedVarSignatureError: If the getter function has more than one argument.
    """
    if cache is False and interval is not None:
        raise ValueError("Cannot set update interval without caching.")

    if cache is False and (deps is not None or auto_deps is False):
        raise VarDependencyError("Cannot track dependencies without caching.")

    inner_deps = []
    if deps:
        inner_deps.extend(deps)
    inner_deps.append(State.current_locale)

    if fget is not None:
        print("fget is not None")

        sign = inspect.signature(fget)
        if len(sign.parameters) != 1:
            raise ComputedVarSignatureError(fget.__name__, signature=str(sign))

        if inspect.iscoroutinefunction(fget):
            computed_var_cls: Any = AsyncComputedVar
        else:
            computed_var_cls = ComputedVar
        return computed_var_cls(
            fget,
            initial_value=initial_value,
            cache=cache,
            deps=inner_deps,
            auto_deps=auto_deps,
            interval=interval,
            backend=backend,
            **kwargs,
        )

    def wrapper(fget: Callable[[State], Any]) -> ComputedVar:
        print("CALLING WRAPPER FUNC")

        def lala(state: State) -> str:
            args = fget(state)
            return locale_service.get_text(state.current_locale, label_id).format(args)

        if inspect.iscoroutinefunction(fget):
            computed_var_cls: Any = AsyncComputedVar
        else:
            computed_var_cls = ComputedVar
        return computed_var_cls(
            lala,
            initial_value=initial_value,
            cache=cache,
            deps=inner_deps,
            auto_deps=auto_deps,
            interval=interval,
            backend=backend,
            **kwargs,
        )

    return wrapper
