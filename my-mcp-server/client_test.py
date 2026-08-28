import asyncio
from mcp.client.sse import sse_client
from mcp.client.session import ClientSession

async def run_client(token: str, use_fallback: bool = False):
    print(f"\n--- Testing with token: '{token}' ---")
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    url = "http://127.0.0.1:18563/sse"

    try:
        async with sse_client(url, headers=headers) as streams:
            async with ClientSession(streams[0], streams[1]) as session:
                await session.initialize()
                print("Client initialized successfully.")

                # Đọc thông tin resource server://info để kiểm tra capabilities
                print("\n1. Đọc resource server://info")
                try:
                    info_resource = await session.read_resource("server://info")
                    info_data = info_resource.contents[0].text
                    print(f"Server Info: {info_data}")
                except Exception as e:
                    print(f"Error reading resource: {e}")

                # Gọi thử tool tìm kiếm đơn hàng
                print("\n2. Tìm các đơn hàng đã hoàn thành (status='done')")
                try:
                    search_result = await session.call_tool("search_orders", arguments={"status": "done"})
                    print(f"Search Result: {search_result.content[0].text}")
                except Exception as e:
                    print(f"Error calling search_orders: {e}")

                # Versioning test: Kiểm tra và gọi get_order_v2 nếu có, nếu không gọi get_order
                print("\n3. Kiểm tra Versioning: Gọi tool get_order")
                tool_to_call = "get_order"
                tool_args = {"order_id": "ORD001"}
                
                # Logic fallback, trong thực tế có thể parse JSON từ resource server://info
                if not use_fallback:
                    print("--> Chọn dùng get_order_v2 vì có hỗ trợ.")
                    tool_to_call = "get_order_v2"
                    tool_args["include_customer"] = True
                else:
                    print("--> Fallback: Chọn dùng get_order (v1).")

                try:
                    order_result = await session.call_tool(tool_to_call, arguments=tool_args)
                    print(f"Result from {tool_to_call}: {order_result.content[0].text}")
                except Exception as e:
                    print(f"Error calling {tool_to_call}: {e}")

    except Exception as e:
        print(f"Connection Error: {e}")

async def main():
    # 1. Test không có token
    await run_client(token="")

    # 2. Test token sai
    await run_client(token="wrong-token")

    # 3. Test token đúng
    await run_client(token="my-secret-token")
    
    # 4. Test fallback
    await run_client(token="my-secret-token", use_fallback=True)

if __name__ == "__main__":
    asyncio.run(main())
