# Bài tập MCP Tools Integration - Day 26

Repository này chứa lời giải cho bài tập xây dựng MCP Server cho công việc thực tế, hỗ trợ HTTP SSE Authentication và Versioning.

## Thành phần
- `/01-function-calling`, `/02-mcp-basics`, `/03-production`, `/04-lab`: Các thư mục bài học có sẵn.
- `/my-mcp-server`: Thư mục chứa mã nguồn MCP Server mô phỏng tra cứu thông tin đơn hàng nội bộ. Đã hoàn thiện toàn bộ các tính năng từ Bài 1 (Dễ), Bài 2 (Trung bình) đến Bài 3 (Khó).

## Chi tiết triển khai
Xin xem [my-mcp-server/README.md](my-mcp-server/README.md) để biết thêm chi tiết về:
- Các tools đã phát triển (`get_order`, `get_order_v2`, `search_orders`).
- Cách chạy thử server và gọi tools kèm Token Authentication.
- Resource Versioning (`server://info`).
- Hướng dẫn cấu hình kết nối từ Claude Code.
