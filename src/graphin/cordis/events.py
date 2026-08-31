import asyncio
import inspect
from typing import Callable, Dict, List, Any, Optional


class EventBus:
    """Cordis-compatible reactive EventBus supporting sync and async event listeners,

    cancellation hooks, and parallel/bail execution styles.
    """

    def __init__(self):
        self._listeners: Dict[str, List[Callable[..., Any]]] = {}

    def on(self, event: str, listener: Callable[..., Any]) -> Callable[[], None]:
        """Register an event listener.

        Returns a unsubscribe function.
        """
        if event not in self._listeners:
            self._listeners[event] = []
        self._listeners[event].append(listener)

        def unsubscribe():
            self.off(event, listener)

        return unsubscribe

    def off(self, event: str, listener: Callable[..., Any]) -> bool:
        """Remove an event listener."""
        if event in self._listeners and listener in self._listeners[event]:
            self._listeners[event].remove(listener)
            return True
        return False

    def emit(self, event: str, *args: Any, **kwargs: Any) -> List[Any]:
        """Emit an event sequentially.

        Returns all non-None listener results.
        """
        results = []
        listeners = list(self._listeners.get(event, []))
        for listener in listeners:
            res = listener(*args, **kwargs)
            if res is not None:
                results.append(res)
        return results

    async def parallel(self, event: str, *args: Any, **kwargs: Any) -> List[Any]:
        """Emit an event asynchronously across all listeners concurrently."""
        listeners = list(self._listeners.get(event, []))
        tasks = []
        for listener in listeners:
            if inspect.iscoroutinefunction(listener):
                tasks.append(listener(*args, **kwargs))
            else:
                # Wrap synchronous functions in coroutines
                async def wrapper(fn=listener):
                    return fn(*args, **kwargs)
                tasks.append(wrapper())

        if not tasks:
            return []
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return [r for r in results if r is not None and not isinstance(r, Exception)]

    async def bail(self, event: str, *args: Any, **kwargs: Any) -> Optional[Any]:
        """Emit event until first listener returns a non-None value."""
        listeners = list(self._listeners.get(event, []))
        for listener in listeners:
            if inspect.iscoroutinefunction(listener):
                res = await listener(*args, **kwargs)
            else:
                res = listener(*args, **kwargs)
            if res is not None:
                return res
        return None
