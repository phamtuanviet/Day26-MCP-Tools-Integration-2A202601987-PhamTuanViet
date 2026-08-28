import json
import os
from mcp.server.mcpserver import MCPServer
from starlette.applications import Starlette
from starlette.routing import Mount
from starlette.requests import Request
from starlette.responses import JSONResponse
import uvicorn

DATA_FILE = os.path.join(os.path.dirname(__file__), "data", "orders.json")

def load_orders():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

# Tạo MCPServer (FastMCP trong mcp 2.x)
mcp_app = MCPServer("order-mcp")

@mcp_app.tool()
def get_order(order_id: str) -> dict:
    """Lấy trạng thái đơn hàng (v1)"""
    orders = load_orders()
    for o in orders:
        if o["id"] == order_id:
            return {"status": o["status"]}
    return {"error": "Order not found"}

@mcp_app.tool()
def get_order_v2(order_id: str, include_customer: bool = True) -> dict:
    """Lấy thông tin chi tiết đơn hàng (v2)"""
    orders = load_orders()
    for o in orders:
        if o["id"] == order_id:
            result = {
                "id": o["id"],
                "status": o["status"],
                "updated_at": o["updated_at"]
            }
            if include_customer:
                result["customer"] = o["customer"]
            return result
    return {"error": "Order not found"}

@mcp_app.tool()
def search_orders(status: str) -> list[dict]:
    """Tìm đơn hàng theo trạng thái"""
    orders = load_orders()
    return [o for o in orders if o["status"] == status]

@mcp_app.resource("server://info")
def server_info() -> str:
    """Metadata của server including versioning info"""
    info = {
        "name": "order-mcp",
        "version": "2.0.0",
        "tools": {
            "get_order": {
                "version": "1.0.0",
                "deprecated": False
            },
            "get_order_v2": {
                "version": "2.0.0",
                "deprecated": False
            },
            "search_orders": {
                "version": "1.0.0",
                "deprecated": False
            }
        }
    }
    return json.dumps(info)

# Lấy ASGI app (sse_app tương đương streamable-http cho mcp 2.x client)
asgi_app = mcp_app.sse_app()

# ASGI Middleware cho TokenVerifier
class TokenVerifierMiddleware:
    def __init__(self, app, token: str):
        self.app = app
        self.token = token

    async def __call__(self, scope, receive, send):
        if scope["type"] not in ["http", "websocket"]:
            await self.app(scope, receive, send)
            return

        request = Request(scope, receive)
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            response = JSONResponse({"error": "Unauthorized", "message": "Missing token"}, status_code=401)
            await response(scope, receive, send)
            return
            
        token = auth_header.split(" ")[1]
        if token != self.token:
            response = JSONResponse({"error": "Forbidden", "message": "Invalid token"}, status_code=403)
            await response(scope, receive, send)
            return
            
        await self.app(scope, receive, send)

# Bọc bằng middleware Auth
auth_app = TokenVerifierMiddleware(asgi_app, "my-secret-token")

if __name__ == "__main__":
    print("Starting MCP Server on http://0.0.0.0:18563")
    uvicorn.run(auth_app, host="0.0.0.0", port=18563)
