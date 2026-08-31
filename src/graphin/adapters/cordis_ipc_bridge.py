import json
import socket
import asyncio
from typing import Dict, Any, Optional
from graphin.cordis.context import Context


class CordisIPCBridge:
    """Inter-Process Communication (IPC) & JSON-RPC bridge for Cordis.

    Enables Grafin orchestrators to exchange events, service calls, and state
    with external `@deepseek-ai/cordis` TS microkernel processes or remote Python nodes over sockets.
    """

    def __init__(self, context: Context, socket_path: str = "/tmp/grafin_cordis.sock"):
        self.context = context
        self.socket_path = socket_path

    def format_request(self, method: str, params: Dict[str, Any], req_id: int = 1) -> str:
        """Format a JSON-RPC 2.0 request message."""
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "id": req_id,
        }
        return json.dumps(payload)

    def parse_response(self, raw_data: str) -> Dict[str, Any]:
        """Parse a JSON-RPC 2.0 response message."""
        try:
            return json.loads(raw_data)
        except json.JSONDecodeError:
            return {"jsonrpc": "2.0", "error": {"code": -32700, "message": "Parse error"}}

    async def send_rpc_call(self, method: str, params: Dict[str, Any], endpoint: Optional[str] = None) -> Dict[str, Any]:
        """Send JSON-RPC call over Unix Domain Socket."""
        target_path = endpoint or self.socket_path
        try:
            reader, writer = await asyncio.open_unix_connection(target_path)
            req_str = self.format_request(method, params) + "\n"
            writer.write(req_str.encode("utf-8"))
            await writer.drain()

            data = await reader.readline()
            writer.close()
            await writer.wait_closed()
            return self.parse_response(data.decode("utf-8"))
        except Exception as e:
            return {"jsonrpc": "2.0", "error": {"code": -32603, "message": f"IPC error: {str(e)}"}}
