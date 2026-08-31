import pytest
import asyncio
from graphin.cordis.context import Context, Service, Fiber
from graphin.cordis.events import EventBus


class MockService(Service):
    service_name = "mock_service"

    def __init__(self, ctx: Context):
        super().__init__(ctx, name=self.service_name)
        self.started = False
        self.stopped = False

    def start(self):
        self.started = True

    def stop(self):
        self.stopped = True


def test_cordis_service_lifecycle():
    ctx = Context()
    fiber = ctx.plugin(MockService)

    assert ctx.has_service("mock_service")
    mock = ctx.get_service("mock_service")
    assert mock is not None
    assert mock.started is True
    assert mock.stopped is False

    fiber.dispose()
    assert mock.stopped is True


def test_cordis_event_bus():
    ctx = Context()
    logs = []

    def handle_event(msg: str):
        logs.append(msg)
        return f"processed:{msg}"

    unsub = ctx.on("test/event", handle_event)
    res = ctx.emit("test/event", "hello")

    assert logs == ["hello"]
    assert res == ["processed:hello"]

    unsub()
    res2 = ctx.emit("test/event", "again")
    assert res2 == []
    assert logs == ["hello"]


@pytest.mark.asyncio
async def test_cordis_event_bus_async():
    ctx = Context()

    async def async_handler(val: int):
        await asyncio.sleep(0.01)
        return val * 2

    ctx.on("async/test", async_handler)
    res = await ctx.parallel("async/test", 5)
    assert res == [10]

    bail_res = await ctx.bail("async/test", 7)
    assert bail_res == 14


def test_cordis_plugin_injection():
    ctx = Context()

    def dependent_plugin(c: Context):
        pass

    dependent_plugin.inject = ["mock_service"]

    # Fails when service is missing
    with pytest.raises(RuntimeError, match="missing required service dependency"):
        ctx.plugin(dependent_plugin)

    # Succeeds after registering service
    ctx.plugin(MockService)
    fiber = ctx.plugin(dependent_plugin)
    assert fiber is not None
