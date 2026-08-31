from __future__ import annotations
import inspect
from typing import Dict, Any, List, Optional, Callable, Type, Union
from graphin.cordis.events import EventBus


class Fiber:
    """Represents an active plugin scope/lifecycle in Cordis.

    Allows clean disposal of listeners, mounted services, and sub-resources.
    """

    def __init__(self, context: Context, name: str = "unnamed_fiber"):
        self.context = context
        self.name = name
        self.disposed = False
        self._dispose_callbacks: List[Callable[[], None]] = []

    def on_dispose(self, callback: Callable[[], None]) -> None:
        """Register a cleanup hook to run when this fiber is disposed."""
        if self.disposed:
            callback()
        else:
            self._dispose_callbacks.append(callback)

    def dispose(self) -> None:
        """Dispose this fiber, triggering all cleanup hooks."""
        if self.disposed:
            return
        self.disposed = True
        for cb in reversed(self._dispose_callbacks):
            try:
                cb()
            except Exception as e:
                pass
        self._dispose_callbacks.clear()
        if self in self.context._fibers:
            self.context._fibers.remove(self)


class Service:
    """Base class for Cordis Services.

    Subclasses must define `service_name`.
    When mounted via `ctx.plugin(MyService)`, `ctx.<service_name>` accesses the service instance.
    """

    service_name: str = "base_service"

    def __init__(self, ctx: Context, name: Optional[str] = None):
        self.ctx = ctx
        if name:
            self.service_name = name
        self.ctx._register_service(self.service_name, self)

    def start(self) -> None:
        """Optional startup lifecycle hook."""
        pass


    def stop(self) -> None:
        """Optional shutdown lifecycle hook."""
        pass


class Context:
    """Root & Scoped Dependency Container microkernel (Cordis Python engine).

    Provides explicit dependency injection, service binding, event bus, and fiber lifecycle management.
    """

    def __init__(self, parent: Optional[Context] = None):
        self.parent = parent
        self.events = EventBus()
        self._services: Dict[str, Service] = {}
        self._fibers: List[Fiber] = []

    def _register_service(self, name: str, service: Service) -> None:
        """Internal helper to register a service on this context."""
        self._services[name] = service
        setattr(self, name, service)

    def get_service(self, name: str) -> Optional[Service]:
        """Retrieve a service by name from this context or parent hierarchy."""
        if name in self._services:
            return self._services[name]
        if self.parent:
            return self.parent.get_service(name)
        return getattr(self, name, None)

    def has_service(self, name: str) -> bool:
        """Check if a service is available."""
        return self.get_service(name) is not None

    def on(self, event: str, listener: Callable[..., Any]) -> Callable[[], None]:
        """Register an event listener tied to the active context."""
        return self.events.on(event, listener)

    def emit(self, event: str, *args: Any, **kwargs: Any) -> List[Any]:
        """Emit an event through this context's event bus."""
        return self.events.emit(event, *args, **kwargs)

    async def parallel(self, event: str, *args: Any, **kwargs: Any) -> List[Any]:
        """Emit an async event concurrently through this context's event bus."""
        return await self.events.parallel(event, *args, **kwargs)

    async def bail(self, event: str, *args: Any, **kwargs: Any) -> Optional[Any]:
        """Emit event until first listener returns non-None."""
        return await self.events.bail(event, *args, **kwargs)

    def plugin(
        self,
        plugin_target: Union[Type[Service], Callable[..., Any]],
        *args: Any,
        **kwargs: Any,
    ) -> Fiber:
        """Mount a plugin (Class or function) onto this context.

        Respects `inject` requirements specified on the plugin.
        Returns a lifecycle Fiber.
        """
        plugin_name = getattr(plugin_target, "__name__", str(plugin_target))
        fiber = Fiber(self, name=plugin_name)
        self._fibers.append(fiber)

        # Check injected service requirements if specified
        required_services = getattr(plugin_target, "inject", [])
        if isinstance(required_services, (list, tuple)):
            for req in required_services:
                if not self.has_service(req):
                    raise RuntimeError(
                        f"Plugin '{plugin_name}' missing required service dependency: '{req}'"
                    )

        if inspect.isclass(plugin_target) and issubclass(plugin_target, Service):
            instance = plugin_target(self, *args, **kwargs)
            instance.start()
            fiber.on_dispose(lambda: instance.stop())
        elif callable(plugin_target):
            res = plugin_target(self, *args, **kwargs)
            if callable(res):
                fiber.on_dispose(res)
            elif hasattr(res, "dispose") and callable(res.dispose):
                fiber.on_dispose(lambda: res.dispose())

        return fiber

    def dispose(self) -> None:
        """Dispose all active fibers and shutdown services."""
        fibers = list(self._fibers)
        for f in fibers:
            f.dispose()
        self._fibers.clear()
        for s in list(self._services.values()):
            try:
                s.stop()
            except Exception:
                pass
        self._services.clear()
